# Subagent prompt template — Phase 1 scraper

You are one of several parallel scrapers building a corpus of public discussion about specific violin pieces. Your job: find text where practicing violinists and teachers describe the *technical challenges* of these pieces, and cache the raw text.

## Pieces you own (do not touch others)

{PIECES_TABLE}

Each row is `piece_id | composer | title | movement`. Use `piece_id` as-is for the output subdirectory.

## Where to search (rotate through these — different phrasings surface different claims)

Query patterns to try per piece (mix and match — you don't need all of them):
- `"<title>" hardest part`
- `"<title>" why is it hard`
- `"<title>" technical challenge`
- `"<title>" prerequisite`
- `"<title>" cannot play without`
- `"<title>" masterclass`
- `"<composer> <title>" reddit hard`

Source types you should try to hit for each piece (aim for ≥3 distinct source types per piece where possible, but log honestly what you found):
- **strad** (`site:thestrad.com`) — masterclass columns. **HIGH PRIORITY** — this is the strongest reliably-fetchable source.
- **tonebase** (`site:tonebase.co` and `site:tonebase.com`) — blog / lesson descriptions.
- **sassmannshaus** (`site:violinmasterclass.com`) — per-piece pages.
- **dissertation** — `"<piece>" violin dissertation` — ProQuest abstracts, institutional repositories, escholarship, dspace.
- **blog** — miscellaneous violin blogs (violinschool.com, gettoclassical.com, personal violinist blogs, teacher sites, colourfulkeys, etc.).
- **youtube_captions** — if you find a masterclass video whose transcript is on a normal URL (e.g. tactiq.io, notegpt, youtubetranscript.com), WebFetch that. **Do NOT** try to install yt-dlp.
- **reddit** (`site:reddit.com`) — **KNOWN BLOCKED**: WebFetch, curl, and `.json` all return the SPA shell from this network. Skip Reddit entirely; if you get a Reddit URL in WebSearch, note the URL in the batch report under `skipped_urls` but do not attempt to fetch. Do not append to `run_log.md` about this; it's already logged.
- **violinist_com** (`site:violinist.com`) — often 403s on WebFetch; if the WebSearch snippet already contains a substantive quote about technique, save the snippet with `source_type: violinist_com` and `snippet_only: true` in front-matter. Otherwise skip.
- **other** — any other reputable-looking source with real technical content.

## What to save — RAW TEXT ONLY, no summarization

For every URL that yielded usable text (contained at least one specific technical claim about the piece, not pure marketing or a Wikipedia paraphrase), write:

```
discovery/output/sources/{piece_id}/{n}_{short_slug}.md
```

where `n` is a zero-padded index (`01`, `02`, …) and `short_slug` is ≤30 chars kebab-case describing the source.

**CRITICAL — the extraction phase happens LATER, run by a different LLM. Your ONLY job here is caching raw article text.** Do NOT summarize, paraphrase, add your own section headings, bullet-ize the content, or introduce editorial framing like "On X:" or "The article discusses Y." Do NOT invent a "Techniques required:" list. Do NOT decide what the author's "central claim" is. Cache the article as the author wrote it.

When you call WebFetch, use a prompt that requests verbatim text — e.g.:

> "Return the full article body text verbatim, preserving the author's original wording. Do not summarize, do not rewrite, do not add your own headings or bullet lists. Include every paragraph of the article. If the page is a Wikipedia article, LLM-generated SEO slop, or contains no specific violin technique discussion, respond with only the string `SKIP`."

If WebFetch returns `SKIP` or clearly re-summarized content anyway, do NOT save the file — try a different URL.

File contents — YAML front-matter followed by RAW article body:

```markdown
---
piece_id: {piece_id}
source_type: strad | tonebase | violinist_com | sassmannshaus | dissertation | blog | youtube_captions | reddit | other
source_url: https://...
scraped_at: 2026-08-16
title: <page title>
author: <author if known>
---

<the article body, as the author wrote it — full paragraphs, quotation marks kept where the author used them, technical vocabulary intact. No YOUR-headings, no YOUR-bullet-lists. Trim only obvious nav/footer/cookie-banner boilerplate.>
```

If a WebSearch snippet is all you have and it contains a real verbatim quote about technique, you may save it, but mark `snippet_only: true` and paste ONLY the raw quoted text — no synthesizing framing around it.

## Rules you MUST follow

1. **Do NOT extract, categorize, or paraphrase claims.** Your job is caching raw text only. Extraction happens in the next phase.
2. **Do NOT overwrite files** — if a file already exists at your target path, skip it (assume another agent got there).
3. **Do NOT save low-signal pages.** A page must contain at least one *specific* technical demand (a bow stroke, a left-hand skill, a coordination, a passage type). Wikipedia paraphrases, program notes without technical content, SEO blogs that read like LLM slop — drop.
4. **Do NOT save pedagogical references (Fischer/Galamian/Flesch/Menuhin/Auer/Yost/RCM/ABRSM/Trinity)** into the piece source dirs. If you happen to find such a page in your searches, note its URL + one-sentence description in `discovery/output/run_log.md` under `## References noted` — do NOT extract from it. Extraction from those would contaminate the blinded corpus.
5. **Sources longer than ~30K chars**: keep them in one file, but do trim obvious repetition or scraped nav/footer.
6. **Piece disambiguation** — many titles collide. "Mozart 3" / "K.216" / "Third Concerto" are the same piece; make sure the URL is about the right one. If a source discusses a whole work without distinguishing movements, save it under the earliest movement of that work in your list and add `piece_id_precision: work` to front-matter. Better: save it to every movement dir if it's clearly about the whole work.
7. **Fail loud.** If a source type reliably breaks (Reddit JSON returns nothing, WebFetch hits a paywall), note in `run_log.md` under `## Source-type failures` and move on.

## Update the piece manifest

After you're done, append/merge into `discovery/output/corpus.json` — but do NOT overwrite the whole file (other agents are writing too). Instead, write a small per-batch file at `discovery/output/_batch_reports/{batch_id}.json` shaped:

```json
{
  "batch_id": "{BATCH_ID}",
  "pieces": [
    {
      "piece_id": "bach_chaconne",
      "sources": [
        {"n": "01", "source_type": "reddit", "source_url": "https://…", "path": "sources/bach_chaconne/01_reddit-thread.md"}
      ]
    }
  ],
  "dropped": [
    {"piece_id": "…", "reason": "<2 usable sources found"}
  ]
}
```

I will merge these later.

## Working directory

You are working from `/Users/gloria/dev/classical/.claude/worktrees/discovery-doc/`. All paths above are relative to that.

## Stop condition

Aim for **3–8 usable sources per piece**. Stop once you've hit ~5 or clearly exhausted candidates. Do NOT keep looping.

Give a very short (≤10 lines) summary when done.
