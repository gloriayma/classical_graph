# Extraction subagent prompt template — Phase 2

You are extractor `{BATCH_ID}`. Your job: apply the verbatim extraction prompt below to each source file in your manifest, and append one JSON claim per line to your output JSONL.

**Blinding is critical.** Do NOT enrich, rename, or normalize claims. Do NOT map author words to standard technique names (Fischer/Galamian/RCM/etc.). Preserve fine-grained distinctions (thirds ≠ sixths; spiccato ≠ sautillé).

## Working directory

`/Users/gloria/dev/classical/.claude/worktrees/discovery-doc/`

## Your manifest

Read the file list from `discovery/output/_extraction/_manifests/{BATCH_ID}.txt` (one relative path per line).

## Output

Write to `discovery/output/_extraction/{BATCH_ID}.jsonl`. One JSON object per line, no wrapper array. If a source file yields zero qualifying claims, write nothing for it.

## Per-file procedure

1. **Read** the source file. Extract `piece_id` and `source_url` from the YAML front-matter. The body follows the second `---`.
2. **Apply** the extraction prompt below to the body text, producing a JSON array of claims.
3. **Append** each claim object as a line in your output JSONL. Fields per claim:
   - `piece_id` — from front-matter
   - `source_url` — from front-matter
   - `verbatim_phrase` — the author's own words for the technical demand (≤100 chars)
   - `quote` — a 30–200 char verbatim excerpt from the source that grounds the claim

Do **not** add a `source_path` field or any other field beyond the four above. Do **not** deduplicate within your batch — the post-processor handles that.

## The extraction prompt (apply to each source body verbatim)

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

## Special handling for `_general` files

Files under `sources/_general/` describe violin technique in general, not any specific piece. For these:
- Keep `piece_id: _general` in the JSON.
- Still apply the same rules (extract only *specific* technical demands, not vague hardship claims).
- These claims will float as "corpus-wide" observations rather than piece-specific ones; the human reviewer will decide how to use them.

## Stop condition

Process every file in your manifest. Give a compact summary at the end: files processed, files yielding zero claims, total claim lines emitted, any files that were unreadable / malformed.

Do NOT edit any file outside `discovery/output/_extraction/`.
