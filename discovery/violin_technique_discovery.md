# Violin Technique Discovery Pipeline — Handoff

## What you're doing

Discover, bottom-up and blind, what practicing violinists and teachers publicly describe as the "killer" technical challenges of specific pieces. The output is a **draft taxonomy of violin techniques** extracted purely from evidence — not from any prior list.

A **killer technique** is one that, if the player lacks it, they *literally cannot play the piece* (or fail catastrophically). Not "sounds worse without it." Not "adds polish." Not "musical interpretation." A physical/technical gate.

## Non-goals — do not do these

- Do **not** build the repertoire graph itself. This is only the taxonomy-discovery pass that precedes it.
- Do **not** classify pieces by difficulty level.
- Do **not** let any pre-existing taxonomy shape extraction, canonicalization, or grouping. Blindness is the design. (See "Existing lists" below for what you *can* do with them.)
- Do **not** filter or normalize claims to fit a hypothesis. Keep author's original words at extraction time.
- Do **not** touch piano.

## Existing technique lists — reference only, do not overfit

Standard pedagogical references do maintain their own technique taxonomies. Feel free to **note them in `run_log.md`** as a resource for the human reviewer — but do not use them to shape any prompt, category, or label in the pipeline outputs. The whole exercise is worthless if we retrofit the corpus onto Galamian's chapter headings.

Known references worth noting if you encounter them (non-exhaustive):
- **Simon Fischer** — *Basics* and *The Violin Lesson* (~300 exercises grouped by skill; probably the most granular modern taxonomy).
- **Ivan Galamian** — *Principles of Violin Playing and Teaching*.
- **Carl Flesch** — *The Art of Violin Playing* and *Scale System*.
- **Yehudi Menuhin** — *Violin: Six Lessons with Yehudi Menuhin*.
- **Leopold Auer** — *Violin Playing as I Teach It*.
- **Yost** — *Studies in the Art of Violin Playing*.
- **RCM / ABRSM / Trinity** syllabi — some grades tag technique requirements.

Rules of engagement:
- If you happen upon one of these while scraping, log the URL + one-sentence note in `run_log.md` under a "References noted" heading. Do not extract claims from these into `claims.jsonl` — they'd contaminate the corpus with authoritative jargon.
- Do NOT paste their category names into any prompt.
- Do NOT compare the discovered taxonomy against them yourself. That's a human step downstream.

## Deliverables (write to `discovery/output/`)

1. `corpus.json` — the piece list you actually collected sources for, with per-piece source URLs.
2. `sources/{piece_id}/{source_index}.md` — cached scraped text per source (so this is auditable and re-runnable).
3. `claims.jsonl` — one line per atomic claim.
4. `claims_sorted.csv` — the same claims sorted alphabetically by `verbatim_phrase`, for human browsing.
5. `run_log.md` — brief log of what you scraped, what failed, what you skipped and why.

**Stop after producing (1)–(5) and post a summary. Do not proceed to any grouping / taxonomy step without explicit go-ahead** — a human will look at `claims_sorted.csv` first and decide whether the follow-up automation described in Phase 3 is worth running.

If given the green light, additionally produce:

6. `canonical.jsonl` — one line per claim, adding a short LLM-generated canonical label (see Phase 3).
7. `groups.md` — canonical labels grouped, each showing member claims with source links.
8. `taxonomy_draft.md` — a proposed taxonomy synthesized from the groups, with full source attribution on every entry.

## Phase 1 — Corpus assembly

### Piece selection

Target **~100 movements** spanning early intermediate to virtuoso, with deliberate diversity of era and style. Below is the seed list. Use it verbatim; if any piece yields <2 usable sources, drop it and log why.

**Early / intermediate (Suzuki bk 4–7 range)**
- Vivaldi Concerto in A minor RV 356 — mvt I
- Bach Concerto in A minor BWV 1041 — mvt I, mvt III
- Bach Concerto in E major BWV 1042 — mvt I
- Bach Double Concerto BWV 1043 — mvt I (violin I)
- Handel Sonata in D major HWV 371 — mvt IV
- de Bériot Scène de Ballet
- Viotti Concerto no. 22 in A minor — mvt I
- Kreisler Praeludium & Allegro
- Kreisler Liebesleid
- Kreisler Recitativo & Scherzo-Caprice
- Massenet Méditation from Thaïs
- Wieniawski Légende

**Mozart / Haydn**
- Mozart Violin Concerto no. 3 K.216 — mvt I, mvt III
- Mozart Violin Concerto no. 4 K.218 — mvt I
- Mozart Violin Concerto no. 5 K.219 — mvt I
- Haydn Concerto in C major Hob. VIIa:1 — mvt I

**DeLay Group 1 (Romantic entry-level concertos)**
- Bruch Violin Concerto no. 1 in G minor — mvt I, mvt II, mvt III
- Mendelssohn Violin Concerto in E minor — mvt I, mvt III
- Lalo Symphonie espagnole — mvt I, mvt IV, mvt V
- Vieuxtemps Concerto no. 5 in A minor — mvt I
- Wieniawski Concerto no. 2 in D minor — mvt I
- Saint-Saëns Concerto no. 3 in B minor — mvt I
- Saint-Saëns Havanaise
- Saint-Saëns Introduction & Rondo Capriccioso

**DeLay Group 2+ (top-tier Romantic concertos)**
- Sibelius Concerto in D minor — mvt I, mvt III
- Tchaikovsky Concerto in D major — mvt I, mvt III
- Brahms Concerto in D major — mvt I, mvt III
- Beethoven Concerto in D major — mvt I

**Solo Bach**
- Bach Chaconne (Partita 2 in D minor BWV 1004)
- Bach Fugue from Sonata 1 in G minor BWV 1001
- Bach Fugue from Sonata 3 in C major BWV 1005
- Bach Preludio from Partita 3 in E major BWV 1006
- Bach Presto from Sonata 1 BWV 1001
- Bach Adagio from Sonata 1 BWV 1001

**Ysaÿe solo sonatas**
- Sonata no. 1 (Szigeti) — mvt I
- Sonata no. 2 (Thibaud) — mvt I "Obsession"
- Sonata no. 3 "Ballade"
- Sonata no. 4 (Kreisler) — mvt I
- Sonata no. 6

**Virtuoso showpieces**
- Wieniawski Polonaise brillante no. 1 in D major
- Wieniawski Scherzo-Tarantelle op. 16
- Paganini Caprice no. 1
- Paganini Caprice no. 4
- Paganini Caprice no. 5
- Paganini Caprice no. 13
- Paganini Caprice no. 17
- Paganini Caprice no. 24
- Paganini Moto Perpetuo
- Ernst Erlkönig transcription
- Ernst Variations on "The Last Rose of Summer"
- Sarasate Zigeunerweisen
- Sarasate Carmen Fantasy
- Sarasate Introduction & Tarantella

**Sonatas & concert works**
- Franck Sonata in A major — mvt I, mvt IV
- Brahms Sonata no. 3 in D minor — mvt I
- Debussy Sonata — mvt I
- Ravel Tzigane
- Ravel Sonata no. 2 — mvt II (Blues)
- Prokofiev Sonata no. 1 in F minor — mvt I
- Prokofiev Concerto no. 2 in G minor — mvt I
- Bartók Sonata no. 2 — mvt I
- R. Strauss Sonata in E-flat — mvt I
- Grieg Sonata no. 3 in C minor — mvt I

**20th–21st century**
- Bartók Concerto no. 2 — mvt I
- Berg Violin Concerto
- Shostakovich Concerto no. 1 — mvt III (Passacaglia), mvt IV (Burlesque)
- Stravinsky Concerto in D — mvt I
- Schoenberg Violin Concerto — mvt I
- Ligeti Concerto — mvt V
- Adès Concerto "Concentric Paths"
- Penderecki Concerto no. 2 "Metamorphosen"

That's ~90 movements. Add ~10 more you find during scraping if they surface strong sources (e.g. Zimbalist, Enescu, Elgar concerto). Skip if you can't find ≥2 sources.

### Sources to search

For **each** piece, try to get sources from multiple of these:

1. **Reddit r/violin** — search `"piece name" hard` or `"piece name" prerequisite`. Sort by top comments.
2. **Violinist.com forums** — search their site.
3. **The Strad archives** (thestrad.com) — masterclass columns often exist for canonical pieces.
4. **Tonebase Violin blog** (tonebase.co/blog and lesson descriptions).
5. **Kurt Sassmannshaus / Violinmasterclass.com** — has per-piece pages for a lot of repertoire.
6. **YouTube masterclass auto-captions** — search `"piece name" masterclass` — Perlman, Hilary Hahn, Zukerman, Julia Fischer, Kavakos, Vengerov, Midori. Pull captions via `yt-dlp --write-auto-sub`.
7. **DMA / doctoral dissertations** — ProQuest search by piece title. Many are free at institutional repos. High signal per document.
8. **Violinist.com blog posts / interviews** with performers about specific pieces.
9. **Violinschool.com**, **Colourful Keys** (mostly piano but occasional violin).
10. **Wikipedia** performance/reception sections (rarely useful but occasionally cite a specific technical demand).

### Query patterns (rotate through these — different phrasings surface different claims)

- `"[piece]" why is it hard`
- `"[piece]" hardest part`
- `"[piece]" prerequisite`
- `"[piece]" before you can play`
- `"[piece]" technical challenge`
- `"[piece]" cannot play without`
- `"[piece]" difficulty`
- `"[piece]" masterclass` (mainly YouTube)
- `"[piece]" technique required`

Also run these **orthogonal general queries** once (not per-piece) to surface cross-piece consensus:

- `hardest techniques on violin`
- `what separates good violinists from great`
- `what teachers wish students had learned before advanced repertoire`
- `most difficult violin techniques`
- `things violinists cannot fake`

Save these general-query results in `sources/_general/`.

### Storage

Per piece, save each raw scraped source as `sources/{piece_id}/{n}_{short_slug}.md` with a header:

```markdown
---
piece_id: bruch_g_minor_mvt1
source_type: reddit | violinist_com | strad | tonebase | youtube_captions | dissertation | sassmannshaus | blog | other
source_url: https://...
scraped_at: 2026-08-16
---

<full text or transcript>
```

Use `piece_id` as a stable slug (e.g. `mendelssohn_e_minor_mvt3`, `paganini_caprice_24`, `bach_chaconne`, `ysaye_sonata2_mvt1`).

## Phase 2 — Atomic claim extraction

For each source file, run the extraction prompt below via the Anthropic API (Claude Haiku 4.5, batch API) — see the `claude-api` skill for setup.

### Blinding rules

- The extraction prompt does **not** contain any predefined technique vocabulary.
- If you find yourself typing "categories like spiccato, sautillé, thirds..." into a prompt — stop. That's confirmation bias entering the pipeline.
- Reject vague claims. If the source only says "this is really hard" without naming a specific physical technique or demand, skip it.

### Extraction prompt

Use this verbatim as the user message; `{piece_id}`, `{source_url}`, `{text}` are substituted:

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

### Batching

Use the Anthropic batch API. Sources longer than ~30K tokens: chunk by paragraph before submitting. Expect ~1–2 minutes wall time per batch; batch API costs ~50% of streaming.

### Pipeline the phases — do not serialize

Extraction is per-source, so start extracting the moment a piece's sources are on disk — don't wait for the whole corpus to finish scraping. Practical shape:

- Scraper walks the piece list. As each piece's sources land, drop them in a queue.
- A separate worker pulls from the queue and submits batch-API extraction jobs.
- Batch results append to `claims.jsonl` as they return.

For the POC (12 pieces) this doesn't matter much. For the full corpus (~265 pieces × ~10 sources) serializing scrape→extract wastes hours; pipelining brings the wall time down to whichever phase is slower (scraping, usually).

### Post-processing

Concatenate all extractions into `claims.jsonl`, one JSON object per line. Assign each claim a stable `claim_id` (hash of `piece_id + verbatim_phrase + source_url`). Deduplicate exact `verbatim_phrase` collisions within a single source (but keep across sources — those are corroboration).

Expected volume: ~1500–4000 claims total from ~100 pieces × 5–15 sources each.

### Human check-in gate

**After Phase 2, stop.** Post a summary and wait for go-ahead before running Phase 3.

The summary should include:
- Piece / source / claim counts
- 20 randomly sampled claims (for spot-checking extraction quality)
- The 30 most common `verbatim_phrase` strings (exact-string counts)
- Anything surprising you noticed

Why this gate exists: the raw claim list may already be browsable enough that Phase 3 automation is unnecessary. If ~200 distinct canonical techniques cover the corpus, a human can taxonomize by reading `claims_sorted.csv` directly. Only run Phase 3 if a human confirms the volume/messiness warrants it.

**Do not run Phase 3 automatically.** Wait for explicit approval.

## Phase 3 — LLM canonicalization and grouping *(only if approved)*

Do **not** use embeddings + clustering. General-purpose embeddings collapse exactly the fine-grained distinctions we care about (thirds vs sixths vs octaves; spiccato vs sautillé vs ricochet; natural vs artificial harmonics). We want an LLM that actually knows those distinctions to do the canonicalization.

### Step 3a — Canonicalize each claim

For each claim in `claims.jsonl`, prompt Claude Haiku 4.5 (batch API) to produce a short canonical label. **Blinding still applies: the prompt shows no reference taxonomy.**

```
You are reading one claim about a specific technical challenge on the
violin, in the author's own words.

Task: produce a short canonical label (2–6 words) that names the SPECIFIC
skill or demand being described. Preserve fine-grained distinctions — if
the author says "thirds," do not generalize to "double stops." If the
author says "sautillé," do not generalize to "off-string bowing." Use the
author's terminology if it is already specific; otherwise the most
neutral, physically descriptive short phrase.

Do NOT consult any predefined taxonomy. Do NOT invent standardized
category names. Do NOT collapse distinct techniques into umbrella terms.

Claim: {verbatim_phrase}
Quote (for context): {quote}

Output JSON:
{ "canonical_label": "..." }
```

Append `canonical_label` to each claim, write to `canonical.jsonl`.

### Step 3b — Group by canonical label

Group claims by exact canonical label match, then run one lightweight LLM merge pass over the label list only (not the underlying claims): given the sorted list of unique labels, propose merges of near-synonyms (`"LH pizzicato"` + `"left hand pizzicato"` + `"plucking with the left hand"` → one group), but **preserve any label that names a distinct technique**. Ask the LLM to err on splitting: when in doubt, keep them separate.

Prompt for the merge pass:

```
Below is an alphabetized list of short labels naming violin techniques.
Some are exact synonyms of each other and should be merged. Others are
distinct techniques and MUST be kept separate — err heavily toward
splitting.

Rules:
- MERGE only when two labels clearly name the same physical skill in
  different words (e.g. "LH pizzicato" and "left-hand pizz").
- DO NOT merge across granularity levels. "Thirds" and "sixths" are
  different techniques. "Spiccato" and "sautillé" are different
  techniques. "Natural harmonics" and "artificial harmonics" are
  different techniques. Keep them separate.
- If unsure, do NOT merge.

Labels:
{sorted_unique_labels}

Output JSON:
{
  "merges": [
    { "canonical": "...", "aliases": ["...", "..."] }
  ]
}
```

Apply the merges to produce final grouping.

### Step 3c — Write `groups.md`

For each group, list the canonical label, the number of claims, the number of distinct pieces mentioning it, and the exemplar claims (up to 20) with clickable source URLs. Sort groups by number of distinct pieces (descending) — a technique that's mentioned across many pieces is more foundational than one that appears in one virtuoso showpiece.

Structure:

```markdown
### <canonical label> (34 claims across 18 pieces)

Aliases: "<alias 1>", "<alias 2>"

**Claims:**
- "<verbatim quote>" — {piece_id} ({source_type}, [link]({source_url}))
- ...
```

### Step 3d — Propose `taxonomy_draft.md`

Final synthesis pass with Claude Sonnet, shown *only* the canonical label list + per-label piece counts (NOT the underlying claims — those would leak external terminology into structural thinking). Ask Sonnet to propose a natural grouping of the labels into higher-level categories, but keep every canonical label as a leaf. **Do not collapse leaves.**

Prompt:

```
Below is a list of specific violin techniques that emerged from analyzing
public discussion of ~100 pieces. Each label appears with the number of
distinct pieces where it was mentioned as a gate-keeping technical
challenge.

Task: propose a natural higher-level grouping (2–6 groups) that a
practicing violinist would find useful. Every individual label must
appear as a LEAF under exactly one group — do not merge or drop leaves.
Groups are for navigation only.

Do not invent standardized category names from any pedagogical
reference; describe each group in plain physical terms.

Labels (with counts):
{labels_with_counts}

Output as markdown.
```

Save the result as `taxonomy_draft.md`, prefixed with corpus stats and a link back to `groups.md` for source-level detail.

## Cost budget

Rough estimates. Stop and check in if you're going to exceed 3× these.

**Phases 1–2 (always run):**

| Item | Estimate |
|---|---|
| Scraping (no LLM cost, just runtime) | 4–8 hours |
| Extraction (Haiku 4.5, batch API, ~2M input tokens) | $3–10 |
| **Subtotal** | **~$3–10** |

**Phase 3 (only if approved after check-in):**

| Item | Estimate |
|---|---|
| Canonicalization (Haiku, batch, ~3K claims) | ~$1 |
| Label merge pass (Sonnet, single call) | <$1 |
| Taxonomy synthesis (Sonnet, single call) | <$1 |
| **Subtotal** | **~$2** |

## Guardrails / gotchas

- **YouTube captions are noisy.** Auto-generated captions often mis-hear technical terms ("spiccato" → "speak auto"). Include them anyway — surrounding phrasing usually disambiguates during extraction — but note the noise.
- **Reddit threads have upvote signal.** Bias toward top-voted comments, but include disagreement — a debate about whether X is hard is useful signal.
- **Piece disambiguation.** "Mozart 3" / "K.216" / "Third Concerto" all mean the same piece. Normalize aggressively during scraping (use canonical `piece_id`).
- **Movement granularity.** If a source discusses a whole concerto without distinguishing movements, tag the extracted claims with the whole work; do not guess which movement. Track a separate `piece_id_precision: work | movement` field if needed.
- **Fake sources.** Some SEO blogs are LLM-generated slop. If a page reads like a Wikipedia paraphrase with no specific technical claims, drop it.
- **Do not filter claims to fit a hypothesis.** If practitioners keep bringing up something you didn't expect (e.g. "bow distribution planning," "counting in mixed meter," "endurance"), let it through. Those are the discoveries.
- **Fail loud.** If scraping breaks for a source type, log which and skip that source type rather than silently reducing the corpus.

## Success criteria

**End of Phase 2 (mandatory stop):**
- ≥80 pieces made it into `claims.jsonl` with ≥3 claims each.
- `claims_sorted.csv` is human-browsable.
- No claim references a technique-taxonomy source (RCM, ABRSM, textbooks). Every claim is grounded in a corpus quote with a real source URL.

**End of Phase 3 (only if approved):**
- Every canonical label preserves fine-grained distinctions (thirds ≠ sixths; spiccato ≠ sautillé; natural harmonics ≠ artificial harmonics; perfect octaves ≠ fingered octaves). If you see these collapsed anywhere in `groups.md`, Phase 3 has failed — fix it before proceeding.
- Every entry in `groups.md` and `taxonomy_draft.md` has clickable source URLs — no aggregation without attribution.
- No label or category name is imported from a standard pedagogical reference.

## When you're done

**After Phase 2**, post a summary and stop:
- Number of pieces, sources, claims.
- 20 randomly sampled claims (spot-check).
- Top 30 exact-string `verbatim_phrase` counts.
- 3–5 things that surprised you during extraction (candidate discoveries).
- 3–5 sources or pieces that gave low-quality signal (candidates to drop).
- Cost actually spent so far.

Wait for explicit approval before running Phase 3.

**After Phase 3 (if approved)**, post:
- Number of canonical labels and groups.
- 3–5 labels that felt like real discoveries.
- 3–5 places where the merge pass felt suspect (candidates for a human to review).
- Total cost spent.

Do not attempt to compare against any prior technique list. That's the next step and belongs to a human reviewer.
