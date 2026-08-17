# Phase 2 — Extraction prompt (blinded)

**Applied to every source file individually. No predefined technique vocabulary is shown to the extractor.**

## Prompt (verbatim from discovery doc, §Phase 2)

```
You are reading text about a specific violin piece. Extract every specific
technical challenge the author mentions.

Rules:
1. Use the AUTHOR'S OWN WORDS for the challenge — do not paraphrase into
   standard terminology.
2. Only extract when the author names a SPECIFIC physical or technical
   demand (a bow stroke, a left-hand skill, a coordination, a passage
   type). Reject vague claims like "this piece is really hard" or
   "you need to be advanced."
3. Only extract claims that a competent player would *fail* on without
   the skill — a physical gate, not a matter of polish, musicality,
   or interpretation. If unsure, err on skipping.
4. Include a verbatim quote (30–200 chars) that grounds the claim.
5. Output ONLY valid JSON. No prose. One object per claim.

Piece: {piece_id}
Source URL: {source_url}

Text:
---
{text}
---

Output format — a JSON array of objects, each shaped:
{
  "piece_id": "{piece_id}",
  "verbatim_phrase": "<author's own words for the challenge, ≤100 chars>",
  "quote": "<30–200 char verbatim quote from the text>",
  "source_url": "{source_url}"
}

If no qualifying claims exist in the text, output: []
```

## Runner design (since we don't have direct batch-API access)

Since the Anthropic batch API isn't accessible from this environment, the extractor pass is executed via a `general-purpose` subagent per batch of source files. The subagent:

1. Iterates over its assigned source files.
2. For each file, reads front-matter (piece_id, source_url) + body.
3. Runs the verbatim prompt above **in-context** (i.e. the subagent itself produces the JSON — its own model call IS the extraction).
4. Appends results to a batch output file `discovery/output/_extraction/{batch_id}.jsonl` — one JSON object per line, each object being one claim.
5. Skips (outputs nothing) when the prompt yields `[]`.

**Blinding:** the subagent's prompt shows only the extraction prompt above, and the source text. It does NOT show any technique vocabulary list, does NOT reveal Fischer/Galamian/RCM/etc. terminology. The extractor may of course know violin technique names from pretraining, but rule 1 (use author's words) counteracts that.

## Post-processing

After all extraction subagents finish, a small Python script:

- Concatenates all `_extraction/*.jsonl` into `claims.jsonl`.
- Assigns each claim a stable `claim_id` = SHA1(piece_id + verbatim_phrase + source_url)[:12].
- Deduplicates exact `verbatim_phrase` collisions **within the same source_url** (keeps across sources — those are corroboration).
- Writes `claims_sorted.csv` sorted alphabetically by `verbatim_phrase`, columns:
  `claim_id, piece_id, verbatim_phrase, quote, source_url`.
