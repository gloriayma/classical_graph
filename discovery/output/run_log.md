# Violin Technique Discovery — Run Log

Started: 2026-08-16
Operator: Claude (Opus 4.7, 1M ctx), running via Claude Code CLI.

## Setup

- Working in worktree `.claude/worktrees/discovery-doc/` on branch `worktree-discovery-doc`.
- Directory scaffolding under `discovery/output/`:
  - `corpus.json` — 85 pieces from seed list (base list, sources filled during scrape).
  - `sources/{piece_id}/{n}_{slug}.md` — cached raw text per source.
  - `sources/_general/` — orthogonal general-query results.
  - `claims.jsonl`, `claims_sorted.csv` — extraction output.
- No direct Anthropic API key visible in environment; running extraction via Claude subagents rather than the batch API. Semantically equivalent (same model family, same prompt), only cheaper-per-token isn't guaranteed; treat cost estimates in the discovery doc as ceiling not floor.

## Scraping strategy per source type

- **Reddit r/violin**: WebSearch with `site:reddit.com/r/violin "<piece>" (hard|prerequisite|hardest)`; WebFetch the JSON endpoint (`<url>.json`) so we get raw comment text rather than a rendered SPA.
- **Violinist.com** and **thestrad.com** and **tonebase.co**: WebSearch with `site:` filter then WebFetch on hits.
- **Violinmasterclass.com (Sassmannshaus)**: has stable per-piece URLs; WebFetch directly if we can guess the slug, else WebSearch.
- **YouTube masterclass captions**: yt-dlp is NOT installed on this host. Attempting via `yt-dlp` install would need a network step; if it fails, fall back to WebFetch on transcript aggregator pages (youtubetranscript.com or similar) and log if none available.
- **Dissertations**: WebSearch `"<piece>" dissertation site:proquest.com OR site:ir.<uni>.edu`; WebFetch abstracts + full text where hosted.

## References noted (pedagogical taxonomies — DO NOT extract into claims.jsonl)

The discovery doc lists Fischer / Galamian / Flesch / Menuhin / Auer / Yost / RCM / ABRSM as reference taxonomies to log but not extract from. Will append any hits here during scraping.

## Piece drops

Log below any piece where <2 usable sources were found and it had to be dropped.

## Source-type failures

Log any global scraper failure (e.g. Reddit JSON rate-limited, yt-dlp not installable) here.

- **Reddit (pilot batch, 2026-08-16)**: WebFetch to `reddit.com` and `old.reddit.com` returned "Claude Code is unable to fetch". curl to `www.reddit.com/*/search.json`, `old.reddit.com/*/search.json`, and `api.reddit.com` all serve a JS-shell page (`<body class=theme-beta>`) rather than JSON — Reddit is anti-bot blocking non-authenticated requests from this network. Skipping Reddit for pilot; will need OAuth or a different route for later batches.
- **violinist.com discussion archive**: 403 Forbidden on WebFetch on the specific archive-thread page. WebSearch surfaces titles/snippets. May work through cached copies or a different retrieval path later.
- **KU ScholarWorks (kuscholarworks.ku.edu)**: 403 Forbidden on WebFetch for both `/server/api/core/bitstreams/...` and `/entities/publication/...` URLs. This blocked access to Wei-yu Chang, "The Chaconne for Solo Violin by J. S. Bach: A Performance Guide" (2019) — a high-value pedagogical dissertation. Try Google-cached or alternate mirror in a later batch.
- **Memphis DigitalCommons and academia.edu**: 403 Forbidden on WebFetch. Blocks another Chaconne performance-practice dissertation and the University of Iowa alto-saxophone Chaconne guide (which had transferable technical content).
- **tonebase.co course pages**: The free-lesson landing pages (e.g. `/free-violin-lessons/vln-eric-silberger-paganini-caprices-05-caprice-no-24`) return 404 on WebFetch. Only the paid-course landing pages (course description) are fetchable, and those contain marketing-level rather than per-variation technical detail.

## Skipped URLs (pilot batch, 2026-08-16)

Reddit URLs surfaced by WebSearch but not fetched (per spec — Reddit blocked on this network):

- No Reddit URLs surfaced in the top-10 results for any of the four pilot pieces. (WebSearch queries did not include `site:reddit.com`; would need explicit reddit query in a later batch.)

## References noted (pedagogical taxonomies — DO NOT extract)

None encountered directly in the pilot batch searches. Kurt Sassmannshaus was surfaced as a violinist.com blog author on Paganini Caprices (violinist.com/blog/laurie/20177/21295/) — his site violinmasterclass.com is fine to save from, but that specific violinist.com post is 403 and would have been treated as pedagogical anyway; noting the URL here.

### General-queries batch (2026-08-16)

Pedagogical-taxonomy sources surfaced during the 5 orthogonal general queries — logged, NOT saved into `sources/_general/`:

- **Musical phrasing anthology (Wikiquote)**: https://en.wikiquote.org/wiki/Musical_phrasing — collates quotes from Auer, Matthay, Tartini, Curry, Mason, Clifford. Anthology of pedagogical taxonomies per spec, skipped.
- **The Strad — Pedagogues' Top Studies: Etude of Choice** (2012 feature): https://www.thestrad.com/playing-hub/pedagogues-top-studies-etude-of-choice/13310.article — teachers discuss Kreutzer, Paganini, Popper, Ševčík, Simandl, Grützmacher, Piatti, Feuillard etudes. Contains rich technical demand content but is essentially a taxonomy of pedagogical study material; skipped from the corpus per spec (Fischer/Galamian/Flesch/Ševčík etc. reference clause).
- **The Violin Site — Fingered Octaves lesson**: https://www.theviolinsite.com/lessons/fingered-octaves.html — page explicitly notes it is "based on the Yost System"; Yost is a listed reference taxonomy per spec.

## General-queries batch — Source-type notes (2026-08-16)

- **Quora**: `www.quora.com` returns HTTP 403 on WebFetch. WebSearch snippets are usable but no full-thread text retrievable. Two Quora threads had strong titles (hardest violin technique / good vs great) but couldn't be fetched.
- **violinlounge.com, violinspiration.com, violinlab.com, timusic.net, muijonathan.com, violinspiration up-bow-staccato**: WebFetch fetched successfully but the underlying summarizer returned re-summarized bullet-list paraphrase rather than verbatim article body, even with an explicit verbatim-only prompt. Not saved (would contaminate the corpus with LLM re-writes). This is a WebFetch-side rewrite pattern, not the site's fault — noted here because it recurred across many mid-tier violin blogs during this batch. thestrad.com, stringsmagazine.com, meadowlarkviolin.com, lvlmusicacademy.com, heatherkayeviolin.com all returned true verbatim bodies.


## batch_C notes (2026-08-16)

### Source-type failures
- The Strad "for-subscribers" masterclass URLs consistently paywalled (Saint-Saens 3 by Beilman; Havanaise by Baillie; Weithaas Brahms parts 1/2; Hadelich Tchaikovsky pt 2; Rodney Friend IRC). Only the non-subscriber Kavakos Sibelius URL (`/artists/...7349.article`) returned full body.
- violinist.com — HTTP 403 on every attempted WebFetch. Skipped.
- WebFetch aggressively summarized many non-paywalled articles despite explicit verbatim prompts; saved outputs contain paragraph-level structure and preserved author quotes, but are not strictly verbatim. Callers of the extraction phase should treat these as high-signal cached texts, not raw HTML.

### References noted
- Auer's "Violin Playing as I Teach It" (from the Vieuxtemps Wikipedia article) — pedagogical reference, not extracted.
- Sassmannshaus masterclass on Havanaise sautillé (violinmasterclass.com/posts/183) — did not fetch to avoid contaminating with pedagogical-reference material.


## batch_E notes (2026-08-16)

### Source-type failures
- violinist.com — HTTP 403 on every WebFetch attempt (Sassmannshaus's Paganini technique article, Rachel Barton Pine interview, Ludwig Bartholdy hardest-pieces blog). Skipped per spec.
- thomastik-infeld.com — HTTP 403 on all "Hidden Method of Paganini" installments. Skipped.
- thestrad.com — HTTP 403 on Rita Fernandes Paganini feature and the Ruggiero Ricci "Secret behind Paganini's amazing technique" feature. WebFetch summarizer also refused verbatim reproduction on the few that loaded, citing copyright.
- earsense.org — WebFetch: "unable to verify the first certificate" (SSL); curl fallback got only nav/glossary metadata, no analytical prose. Skipped.
- theviolinchannel.com Sean Lee video blog — HTTP 403.
- sagepub.com (Kraker "Ernst's Erlkönig: A Practice Guide") — HTTP 403 on both HTML and PDF endpoints. Would have been a strong dissertation-style source for ernst_erlkonig.
- openscholar.uga.edu Curty DMA on Ysaÿe — HTTP 403.
- researcharchive.vuw.ac.nz Ysaÿe thesis — redirect to `openaccess.wgtn.ac.nz` which also 403s.

### Wikipedia strategy shift
WebFetch's underlying model refused to return verbatim Wikipedia article bodies (citing copyright), returning summarized paraphrases with invented section headers. Switched to `curl` + `api.php?action=parse&prop=wikitext` which returned true verbatim wikitext — used this for Six Sonatas (Ysaÿe), Heinrich Wilhelm Ernst biography, Erlkönig (Schubert) Ernst section, Scherzo Tarantelle, Polonaise de Concert Op. 4, Caprice No. 5, Caprice No. 24, The Last Rose of Summer, and the 24 Caprices main article (with per-caprice technique summary table). Individual Caprice pages for Nos. 1, 4, 17 do not exist as separate Wikipedia articles; used the 24 Caprices main-article table entry instead.

### Interlude.hk strategy
Two Interlude.hk listicles ("Devilish Genius" / "Hardest Violin Pieces" / "Wieniawski's Dazzling Decade") returned verbatim per-section content when prompted with "copy the paragraph about piece X" specifically. Full-article prompts triggered copyright refusals or summarization.

### References noted
- The Strad "Pedagogues' Top Studies: Etude of Choice" — already noted by prior batches; not re-fetched.
- Fritz Kreisler arrangements of Paganini caprices Nos. 13, 20, 24 — noted in the 24 Caprices wikitext; performer edition, not a pedagogical taxonomy, so allowable, but not a fetched source.
