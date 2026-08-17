# Violin Technique Discovery Pipeline — Handoff

## What you're doing

Discover, bottom-up and blind, what practicing violinists and teachers publicly describe as the "killer" technical challenges of specific pieces. The output is a **draft taxonomy of violin techniques** extracted purely from evidence — not from any prior list.

A **killer technique** is one that, if the player lacks it, they *literally cannot play the piece* (or fail catastrophically). Not "sounds worse without it." Not "adds polish." Not "musical interpretation." A physical/technical gate.

## Non-goals — do not do these

- Do **not** build the repertoire graph itself. This is only the taxonomy-discovery pass that precedes it.
- Do **not** classify pieces by difficulty level.
- Do **not** consult any pre-existing taxonomy of violin techniques (RCM's, ABRSM's, textbook categorizations, or any prior list from this project). The whole point is bottom-up discovery. Blindness is the design.
- Do **not** filter or normalize claims to fit a hypothesis. Keep author's original words at extraction time; normalization only happens after clustering.
- Do **not** touch piano.

## Deliverables (write to `discovery/output/`)

1. `corpus.json` — the piece list you actually collected sources for, with per-piece source URLs.
2. `sources/{piece_id}/{source_index}.md` — cached scraped text per source (so this is auditable and re-runnable).
3. `claims.jsonl` — one line per atomic claim.
4. `embeddings.parquet` — claim embeddings, keyed to claim IDs.
5. `clusters.json` — cluster assignments, exemplars per cluster, and LLM-labeled cluster names.
6. `taxonomy_draft.md` — human-readable summary: one section per cluster, exemplar quotes, size, and the label. This is what a human will actually read.
7. `run_log.md` — brief log of what you scraped, what failed, what you skipped and why.

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

### Post-processing

Concatenate all extractions into `claims.jsonl`, one JSON object per line. Assign each claim a stable `claim_id` (hash of `piece_id + verbatim_phrase + source_url`). Deduplicate exact `verbatim_phrase` collisions within a single source (but keep across sources — those are corroboration).

Expected volume: ~1500–4000 claims total from ~100 pieces × 5–15 sources each.

## Phase 3 — Cluster and label

### Embedding

Embed the `verbatim_phrase` field (not the quote — the quote has piece-specific noise). Recommended models, in order of preference:

1. **Voyage `voyage-3-lite`** — cheap, good for short technical phrases.
2. **OpenAI `text-embedding-3-small`** — fine, well-documented.
3. **`sentence-transformers/all-MiniLM-L6-v2`** — free, local, adequate for this scale.

Save to `embeddings.parquet` with columns `claim_id, embedding, verbatim_phrase, piece_id`.

### Clustering

Use **HDBSCAN** (Python `hdbscan` package). Parameters to try:

- `min_cluster_size=5` (a cluster of 5+ distinct claims is meaningful)
- `min_samples=3`
- `metric='euclidean'` on L2-normalized embeddings (equivalent to cosine)

Alternative if HDBSCAN gives too much noise (label = -1): try Agglomerative with distance threshold ~0.35 on normalized cosine distance.

**Do not force a target `k`.** The whole point is to let natural structure emerge.

Save `clusters.json`:

```json
{
  "clusters": [
    {
      "cluster_id": 0,
      "size": 47,
      "n_distinct_pieces": 22,
      "exemplars": [
        {"claim_id": "...", "verbatim_phrase": "...", "quote": "...", "piece_id": "...", "source_url": "..."}
      ],
      "all_claim_ids": ["..."]
    }
  ],
  "noise": ["<claim_ids of unclustered claims>"]
}
```

Exemplars: top ~20 by centrality (nearest to the cluster centroid).

### Cluster labeling

For each cluster, ask Claude Sonnet to write a short label. **The prompt shows only that cluster's exemplars — no other clusters, no prior taxonomy, no reference list.**

```
Below are ~20 examples of things violinists said about specific technical
challenges in specific pieces. All examples come from ONE cluster — they
were grouped together because they seem to describe the same underlying
skill or demand.

Your task: write a short label (2–6 words) that names this skill in the
most neutral, descriptive terms possible. Do NOT invent jargon; use plain
descriptive English. Also write a 1-sentence description of what
distinguishes this skill.

If the examples do NOT actually cohere — if they seem to describe
different things — say so explicitly.

Examples:
{exemplars}

Output JSON:
{
  "label": "...",
  "description": "...",
  "coherent": true | false,
  "notes": "<optional, any observations>"
}
```

### Final human-readable output

Write `taxonomy_draft.md` structured as:

```markdown
# Violin Technique Taxonomy — Discovery Draft

Generated: <date>
Pieces analyzed: <n>
Sources: <n>
Total claims extracted: <n>
Clusters found: <n>
Noise / unclustered: <n>

## Clusters (ordered by size)

### Cluster 0 — <label> (size: 47, across 22 pieces)

<description>

**Exemplar quotes:**
- "<verbatim quote>" — {piece_id} ({source_type}, [link]({source_url}))

**Pieces mentioned:** bruch_g_minor_mvt1, mendelssohn_e_minor_mvt3, ...
```

The doc must let a reader **click any exemplar's source URL** and read the original — full attribution, no aggregation.

## Cost budget

Rough estimates. Stop and check in if you're going to exceed 3× these.

| Item | Estimate |
|---|---|
| Scraping (no LLM cost, just runtime) | 4–8 hours |
| Extraction (Haiku 4.5, batch API, ~2M input tokens) | $3–10 |
| Embeddings (~3K claims × ~30 tokens, Voyage or OpenAI) | <$1 |
| Cluster labeling (Sonnet, ~50 clusters × ~3K tokens) | ~$1 |
| **Total** | **~$5–15** |

## Guardrails / gotchas

- **YouTube captions are noisy.** Auto-generated captions often mis-hear technical terms ("spiccato" → "speak auto"). Include them anyway — surrounding phrasing usually disambiguates during extraction — but note the noise.
- **Reddit threads have upvote signal.** Bias toward top-voted comments, but include disagreement — a debate about whether X is hard is useful signal.
- **Piece disambiguation.** "Mozart 3" / "K.216" / "Third Concerto" all mean the same piece. Normalize aggressively during scraping (use canonical `piece_id`).
- **Movement granularity.** If a source discusses a whole concerto without distinguishing movements, tag the extracted claims with the whole work; do not guess which movement. Track a separate `piece_id_precision: work | movement` field if needed.
- **Fake sources.** Some SEO blogs are LLM-generated slop. If a page reads like a Wikipedia paraphrase with no specific technical claims, drop it.
- **Do not filter claims to fit a hypothesis.** If practitioners keep bringing up something you didn't expect (e.g. "bow distribution planning," "counting in mixed meter," "endurance"), let it through. Those are the discoveries.
- **Fail loud.** If scraping breaks for a source type, log which and skip that source type rather than silently reducing the corpus.

## Success criteria

- ≥80 pieces made it into `claims.jsonl` with ≥3 claims each.
- ≥30 distinct clusters emerge (loose lower bound; adjust if HDBSCAN gives fewer legitimate clusters).
- `taxonomy_draft.md` is readable end-to-end and every claim links back to a real source URL.
- No cluster label references a technique-taxonomy source (RCM, ABRSM, textbooks, previous notes). All labels come from what the corpus actually said.

## When you're done

Post a short summary as the final message:
- Number of pieces, sources, claims, clusters, noise fraction.
- 3–5 clusters that surprised you (that felt like real discoveries).
- 3–5 clusters that felt noisy / incoherent (candidates to inspect further).
- Cost actually spent.

Do not attempt to compare against any prior technique list. That's the next step and belongs to a human reviewer.
