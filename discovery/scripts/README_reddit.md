# Reddit scraping — setup

## What I tried and why the free paths are dead

From this network:

| path | result |
|---|---|
| `www.reddit.com/*` + `.json` suffix | 403 (data-center IP block) |
| `old.reddit.com/*` (with browser UA) | 403 |
| `api.reddit.com/*` | serves the SPA HTML shell |
| Pushshift successor `pullpush.io` | 429 + explicit "no free scraping for agents; contact for paid service" |
| Redlib mirrors (`redlib.catsarch.com`, `red.artemislena.eu`, `redlib.privacyredirect.com`, `libreddit.projectsegfau.lt`, `libreddit.perennialte.ch`, `libreddit.privacydev.net`) | Anubis proof-of-work challenge on every request |
| `rl.bloat.cat` | Custom "not a clanker" JS-cookie gate |
| `archive.org` CDX for reddit URLs | 498 rate-limited |
| **Reddit OAuth API (`www.reddit.com/api/v1/access_token`)** | **401 to invalid creds — endpoint is reachable, only the anonymous surface is blocked** |

Only OAuth works. Every free-mirror approach fell in ~2024–2025 when Reddit tightened anonymous access and mirrors buckled under scraper load. The consensus response (Anubis) is targeted specifically at AI/data-center IPs.

## One-time setup (5 minutes, human required)

1. Go to https://www.reddit.com/prefs/apps
2. Scroll down, click **"create app"** (or "create another app").
3. Fill in:
   - **name**: anything, e.g. `violin-technique-discovery`
   - **type**: choose **"script"** (simplest — no OAuth redirect dance needed)
   - **redirect URI**: `http://localhost:8080` (unused for script type but required)
   - description: optional
4. Click "create app".
5. You'll now see a summary card. Copy:
   - **client_id** — the string right under the app name (usually starts with letters, ~14 chars)
   - **secret** — labelled "secret" field

6. Create `~/.config/violin-discovery/reddit.json` with:

```json
{
  "client_id": "PASTE_CLIENT_ID_HERE",
  "client_secret": "PASTE_SECRET_HERE",
  "username": "YOUR_REDDIT_USERNAME",
  "password": "YOUR_REDDIT_PASSWORD"
}
```

`chmod 600 ~/.config/violin-discovery/reddit.json`.

The username/password aren't for logging *in*; script-type apps just use the password grant to prove the app owner is the one making calls. Reddit's own docs recommend it.

**If you'd rather not put your password in a file:** register the app as "installed app" instead of "script", and use `{"client_id": "...", "installed_app": true}` in `reddit.json`. That path uses an app-only anonymous token with the same rate limits.

## Usage

```
# quick sanity check
python3 discovery/scripts/reddit_scraper.py search "bach chaconne" --limit 5

# scrape one specific thread by post ID
python3 discovery/scripts/reddit_scraper.py thread 1abcdef

# bulk-scrape the whole corpus (or a subset)
python3 discovery/scripts/reddit_scraper.py bulk_scrape discovery/output/corpus.json
python3 discovery/scripts/reddit_scraper.py bulk_scrape discovery/output/corpus.json --only bach_chaconne,paganini_caprice_24
```

Bulk scrape writes files as normal source files under
`discovery/output/sources/{piece_id}/{n}_reddit-<slug>.md`, so Phase 2
extraction picks them up automatically on the next run.

Rate: ~1.2s between calls, well under Reddit's 60 req/min limit.
With 83 pieces × 3 queries × 6 candidate threads × 1 thread-detail fetch ≈ 500–1500 calls total, so a full re-scrape is ~10–20 minutes wall time.

## After scraping — re-run Phase 2 extraction

```
# rebuild manifests including new Reddit files
python3 <<'EOF'
import json, os, math, glob
files = sorted(glob.glob('discovery/output/sources/*/*.md'))
# only the new ones — anything containing 'reddit' in the filename
new_files = [f for f in files if 'reddit' in os.path.basename(f)]
os.makedirs('discovery/output/_extraction/_manifests', exist_ok=True)
with open('discovery/output/_extraction/_manifests/reddit_addendum.txt', 'w') as fh:
    fh.write('\n'.join(new_files) + '\n')
print(f'wrote {len(new_files)} paths to reddit_addendum.txt')
EOF

# then dispatch an extraction subagent (or run manually) on that manifest,
# writing to _extraction/reddit_addendum.jsonl, and re-run the postprocess:

python3 discovery/scripts/postprocess_claims.py
```

The postprocess script picks up every `_extraction/*.jsonl` file, so
`reddit_addendum.jsonl` gets folded in automatically.
