#!/usr/bin/env python3
"""
Reddit scraper via the official OAuth API.

Why this exists: reddit.com anonymous endpoints (WebFetch, curl to .json,
old.reddit, api.reddit) all return 403 from this network. Every free
mirror (redlib, pullpush, archive.org CDX) is now behind Anubis PoW or
explicit anti-agent rate-limits. The one path Reddit actively supports
is their OAuth API — free tier, 60 req/min, one-time app registration.

Setup — a one-time thing the human has to do:

  1. Go to https://www.reddit.com/prefs/apps
  2. Click "create app". Choose "script" type (simplest — no redirect flow).
  3. Any name and description. Redirect URI: http://localhost:8080 (unused).
  4. After creating, you get:
       - client_id   : the string right under the app name
       - client_secret : the "secret" field
  5. Write both into ~/.config/violin-discovery/reddit.json :
       { "client_id": "...", "client_secret": "...",
         "username": "<your reddit username>",
         "password": "<your reddit password>" }
     (username/password are needed for the "password" grant on script apps.
      If you'd rather not, use the OAUTH_INSTALLED_APP path below.)

Alternative — "installed app" grant (no username/password, but you must
create the app as an "installed app" instead of a script):
       { "client_id": "...", "installed_app": true }

Usage:

  python3 reddit_scraper.py search "bach chaconne" --subreddit violin --limit 5
  python3 reddit_scraper.py thread <post_id>
  python3 reddit_scraper.py bulk_scrape ../output/corpus.json

Bulk scrape reads corpus.json, does one search per piece (2–3 query
patterns), pulls the top-voted threads (with comments), and writes the
results as normal source files under
discovery/output/sources/{piece_id}/reddit_*.md.

Respects Reddit's rate limit — 60 req/min — with a sleep between calls.
"""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import re
import sys
import time
from typing import Any

try:
    import urllib.request
    import urllib.parse
except ImportError:
    sys.exit("stdlib urllib missing?")


UA = "violin-technique-discovery/0.1 (research; contact via project repo)"
CRED_PATH = pathlib.Path.home() / ".config" / "violin-discovery" / "reddit.json"
TOKEN_URL = "https://www.reddit.com/api/v1/access_token"
API_BASE = "https://oauth.reddit.com"

# 60 req/min → conservative 1.2s sleep between calls
RATE_SLEEP_S = 1.2

# Repo-relative paths (this script lives in discovery/scripts/)
SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
OUTPUT_DIR = SCRIPT_DIR.parent / "output"
SOURCES_DIR = OUTPUT_DIR / "sources"


# ---------- auth ----------

def load_creds() -> dict:
    if not CRED_PATH.exists():
        sys.exit(f"Missing {CRED_PATH}. See docstring at top of this file for setup.")
    return json.loads(CRED_PATH.read_text())


def get_token(creds: dict) -> str:
    """Return a bearer token. Handles both 'script' (password) and 'installed_app' flows."""
    client_id = creds["client_id"]
    client_secret = creds.get("client_secret", "")
    if creds.get("installed_app"):
        data = {
            "grant_type": "https://oauth.reddit.com/grants/installed_client",
            "device_id": creds.get("device_id", "DO_NOT_TRACK_THIS_DEVICE"),
        }
    else:
        data = {
            "grant_type": "password",
            "username": creds["username"],
            "password": creds["password"],
        }

    body = urllib.parse.urlencode(data).encode()
    req = urllib.request.Request(TOKEN_URL, data=body, method="POST")
    req.add_header("User-Agent", UA)
    # basic auth
    import base64
    creds_str = f"{client_id}:{client_secret}"
    b64 = base64.b64encode(creds_str.encode()).decode()
    req.add_header("Authorization", f"Basic {b64}")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")

    with urllib.request.urlopen(req, timeout=15) as resp:
        payload = json.loads(resp.read().decode())
    if "access_token" not in payload:
        sys.exit(f"Reddit did not return a token: {payload}")
    return payload["access_token"]


# ---------- api calls ----------

def api_get(path: str, token: str, params: dict | None = None) -> Any:
    q = f"?{urllib.parse.urlencode(params)}" if params else ""
    req = urllib.request.Request(f"{API_BASE}{path}{q}")
    req.add_header("User-Agent", UA)
    req.add_header("Authorization", f"Bearer {token}")
    time.sleep(RATE_SLEEP_S)
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode())


def search(token: str, query: str, subreddit: str = "violin", limit: int = 10, sort: str = "top", t: str = "all") -> list[dict]:
    """Return a list of submission dicts."""
    data = api_get(
        f"/r/{subreddit}/search",
        token,
        {"q": query, "restrict_sr": "on", "limit": limit, "sort": sort, "t": t},
    )
    return [child["data"] for child in data.get("data", {}).get("children", [])]


def thread(token: str, post_id: str, subreddit: str = "violin", comment_sort: str = "top", limit: int = 500) -> tuple[dict, list[dict]]:
    """Return (submission, flat_list_of_comment_dicts) for a thread."""
    listing = api_get(
        f"/r/{subreddit}/comments/{post_id}",
        token,
        {"sort": comment_sort, "limit": limit, "depth": 8},
    )
    if not isinstance(listing, list) or len(listing) < 2:
        return {}, []
    submission = listing[0]["data"]["children"][0]["data"]
    comments = []

    def walk(node):
        if not node or not isinstance(node, dict):
            return
        kind = node.get("kind")
        d = node.get("data", {})
        if kind == "t1":
            comments.append(d)
            replies = d.get("replies")
            if isinstance(replies, dict):
                for child in replies.get("data", {}).get("children", []):
                    walk(child)

    for child in listing[1]["data"]["children"]:
        walk(child)
    return submission, comments


# ---------- corpus helpers ----------

def piece_query_variants(piece: dict) -> list[str]:
    """A few phrasings per piece — rotate to hit different Reddit conversations."""
    composer = piece["composer"].replace("Bériot", "Beriot").replace("Ysaÿe", "Ysaye").replace("Bartók", "Bartok")
    title = piece["title"]
    movement = piece.get("movement") or ""
    base = f"{composer} {title}"
    if movement:
        base_mvt = f"{composer} {title} {movement}"
    else:
        base_mvt = base
    # 3 quick queries, in decreasing specificity
    return [
        f'"{base_mvt}" hardest',
        f"{base} technique",
        f'"{title}" prerequisite',
    ]


def next_index(piece_dir: pathlib.Path) -> str:
    existing = sorted(piece_dir.glob("*.md"))
    n = 1
    if existing:
        # last index like "01_foo.md" → 2
        m = re.match(r"^(\d+)_", existing[-1].name)
        if m:
            n = int(m.group(1)) + 1
    return f"{n:02d}"


def write_reddit_source(piece_id: str, url: str, title: str, body_text: str) -> pathlib.Path:
    piece_dir = SOURCES_DIR / piece_id
    piece_dir.mkdir(parents=True, exist_ok=True)
    idx = next_index(piece_dir)
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower())[:40].strip("-") or "thread"
    out = piece_dir / f"{idx}_reddit-{slug}.md"
    front = (
        f"---\n"
        f"piece_id: {piece_id}\n"
        f"source_type: reddit\n"
        f"source_url: {url}\n"
        f"scraped_at: {time.strftime('%Y-%m-%d')}\n"
        f"title: {json.dumps(title)}\n"
        f"---\n\n"
    )
    out.write_text(front + body_text)
    return out


def scrape_piece(token: str, piece: dict, per_piece_limit: int = 3) -> list[pathlib.Path]:
    """Search Reddit for a piece and cache the top threads with comments."""
    written: list[pathlib.Path] = []
    seen_ids: set[str] = set()

    for query in piece_query_variants(piece):
        try:
            subs = search(token, query, subreddit="violin", limit=6, sort="top")
        except urllib.error.HTTPError as e:
            print(f"  search '{query}' failed: {e}", file=sys.stderr)
            continue

        for sub in subs:
            if len(written) >= per_piece_limit:
                return written
            post_id = sub.get("id")
            if not post_id or post_id in seen_ids:
                continue
            seen_ids.add(post_id)
            title = sub.get("title", "")
            selftext = sub.get("selftext", "") or ""
            permalink = "https://www.reddit.com" + sub.get("permalink", "")
            num_comments = sub.get("num_comments", 0)
            score = sub.get("score", 0)

            # Skip threads with no comments AND no selftext — no signal
            if num_comments == 0 and len(selftext) < 100:
                continue

            try:
                _, comments = thread(token, post_id)
            except urllib.error.HTTPError as e:
                print(f"  thread {post_id} failed: {e}", file=sys.stderr)
                continue

            # Format thread body: post + top comments (only those with score >= 2, up to 40)
            parts = []
            parts.append(f"**Thread: {title}** — score {score}, {num_comments} comments")
            if selftext.strip():
                parts.append("**OP:**")
                parts.append(selftext.strip())
            kept_comments = [c for c in comments if c.get("score", 0) >= 2]
            kept_comments = kept_comments[:40]
            if kept_comments:
                parts.append("\n**Comments (top-voted, verbatim):**")
                for c in kept_comments:
                    author = c.get("author", "[deleted]")
                    body = (c.get("body") or "").strip()
                    if not body or body in ("[removed]", "[deleted]"):
                        continue
                    cscore = c.get("score", 0)
                    parts.append(f"\n— {author} (score {cscore}):\n{body}")

            body_text = "\n\n".join(parts)
            out = write_reddit_source(piece["piece_id"], permalink, title, body_text)
            written.append(out)
            print(f"  wrote {out.name}")

    return written


# ---------- cli ----------

def cmd_search(args):
    token = get_token(load_creds())
    subs = search(token, args.query, subreddit=args.subreddit, limit=args.limit, sort=args.sort)
    for sub in subs:
        print(f"[{sub.get('score', 0):>5}] {sub.get('num_comments', 0):>3}c  {sub.get('title')} — https://www.reddit.com{sub.get('permalink','')}")


def cmd_thread(args):
    token = get_token(load_creds())
    submission, comments = thread(token, args.post_id, subreddit=args.subreddit)
    print(f"# {submission.get('title')}")
    print(f"(score {submission.get('score')}, {submission.get('num_comments')} comments)")
    print(submission.get("selftext", "").strip())
    for c in comments[:30]:
        body = (c.get("body") or "").strip()
        if not body or body in ("[removed]", "[deleted]"):
            continue
        print(f"\n— {c.get('author','?')} ({c.get('score',0)}):")
        print(body)


def cmd_bulk_scrape(args):
    corpus = json.loads(pathlib.Path(args.corpus).read_text())
    only = set(args.only.split(",")) if args.only else None
    token = get_token(load_creds())
    for i, piece in enumerate(corpus["pieces"]):
        pid = piece["piece_id"]
        if only and pid not in only:
            continue
        print(f"[{i+1}/{len(corpus['pieces'])}] {pid}")
        try:
            scrape_piece(token, piece, per_piece_limit=args.per_piece_limit)
        except Exception as e:
            print(f"  ERROR on {pid}: {e}", file=sys.stderr)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_search = sub.add_parser("search")
    p_search.add_argument("query")
    p_search.add_argument("--subreddit", default="violin")
    p_search.add_argument("--limit", type=int, default=10)
    p_search.add_argument("--sort", default="top")
    p_search.set_defaults(func=cmd_search)

    p_thread = sub.add_parser("thread")
    p_thread.add_argument("post_id")
    p_thread.add_argument("--subreddit", default="violin")
    p_thread.set_defaults(func=cmd_thread)

    p_bulk = sub.add_parser("bulk_scrape")
    p_bulk.add_argument("corpus", help="path to corpus.json")
    p_bulk.add_argument("--per-piece-limit", type=int, default=3, help="max threads to save per piece")
    p_bulk.add_argument("--only", help="comma-separated piece_ids to limit to (for testing)")
    p_bulk.set_defaults(func=cmd_bulk_scrape)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
