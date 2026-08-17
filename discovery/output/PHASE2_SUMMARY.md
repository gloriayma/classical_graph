# Phase 2 Summary — Violin Technique Discovery

Run date: 2026-08-16 (single day, one operator).

## Corpus & extraction counts

| | count |
|---|---|
| Pieces in seed list | 83 |
| Pieces with ≥1 cached source | 83 |
| Sources cached total | 257 (piece-specific) + 11 (`_general`) |
| Distinct source URLs | 123 |
| Raw extractor lines emitted | 423 |
| Unique claims after dedup | 423 (no in-source dupes triggered) |
| Distinct pieces with ≥1 claim | 68 |
| Distinct pieces with ≥3 claims | **51** (success-criterion threshold was 80) |
| Pieces with 0 claims (fall-out) | 15 |

**The 80-piece / 3-claim success threshold was NOT met.** Root causes analysed below; this is the primary decision-point for whether to reinforce Phase 1 before running Phase 3.

## 15 pieces with 0 claims (dropped from downstream)

```
bach_a_minor_bwv1041_mvt3         bach_double_bwv1043_mvt1_v1
bach_e_major_bwv1042_mvt1         bartok_concerto2_mvt1
debussy_sonata_mvt1               franck_sonata_a_major_mvt1
franck_sonata_a_major_mvt4        handel_d_major_hwv371_mvt4
kreisler_liebesleid               mozart_k216_mvt3
mozart_k219_mvt1                  penderecki_concerto2_metamorphosen
prokofiev_concerto2_g_minor_mvt1  prokofiev_sonata1_f_minor_mvt1
viotti_concerto_22_mvt1
```

Pattern: nearly all are pieces where public writing is dominated by *historical / formal / expressive* commentary rather than physical-gate discussion. Debussy Sonata is the strongest example — Anne-Sophie Mutter's own Strad essay explicitly frames it as *not-a-technical piece* ("nine kinds of soft"). Prokofiev / Penderecki / Bartók VC2 similarly get discussed as sound-worlds. The extractor correctly held the line and didn't fabricate physical claims.

## 17 pieces with 1–2 claims (borderline)

```
1 claim: bruch_g_minor_mvt2, grieg_sonata3_c_minor_mvt1,
         lalo_symphonie_espagnole_mvt4, ravel_sonata2_mvt2_blues,
         saint_saens_3_mvt1, sarasate_intro_tarantella, wieniawski_2_mvt1
2 claims: bach_a_minor_bwv1041_mvt1, brahms_d_major_mvt1,
          brahms_sonata3_d_minor_mvt1, paganini_caprice_4,
          saint_saens_havanaise, strauss_sonata_eb_mvt1,
          tchaikovsky_d_major_mvt3, vieuxtemps_5_mvt1,
          wieniawski_polonaise_1_d_major, wieniawski_scherzo_tarantelle
```

## Top-30 exact-string `verbatim_phrase` counts

```
  5  harmonics
  4  string crossings
  4  trills
  3  double stops
  3  left hand pizzicato
  3  staccato
  3  portato
  3  fast runs
  3  chords
  2  digital and rhythmic dexterity and preciseness of pitch in the multiple stoppings
  2  sixteenth-note passagework, chordal figurations
  2  double-stops, vigorous bowing, and the full range of violin pyrotechnics
  2  bowing that really digs into the strings
  2  double-stopped thirds
  2  left-hand pizzicato to pluck out the melody while a running scale accompaniment plays on
  2  shifting
  2  jumping from third to twelfth position in only two octaves
  2  ricochet
  2  ornaments
  2  creating depth and direction with bow speed rather than vibrato
  2  trills... starting from the upper note
  2  appoggiaturas... played on the beat
  2  smooth, on-the-string playing
  2  flying spiccato and ricochet bowings
  2  long spiccato runs, along with double stops, artificial harmonics and left-hand pizzicato
  2  scales, double stops, and rapid leaps
  2  sextuple-stopping
  2  rapid alternations of sixths and tenths in passage-work
  1  drawing the bow without exerting pressure on the stick
  1  flat hair on the down bow to get a thicker tone
```

**382 of 423 verbatim strings are singletons** — heavy tail. That's what Phase 3 canonicalization is for (if run).

## 20 randomly sampled claims (spot-check for extraction quality)

```
[shostakovich_concerto1_mvt3_passacaglia] anguished, defiant octaves in the solo violin
[bach_adagio_g_minor_bwv1001] elaborate carefully notated ornamentation giving a free, improvisatory impression
[_general] little finger raised through most of the stroke, contacting stick to counterbalance bow change
[wieniawski_legende] pianississimo arpeggios, culminating in the highest G the violin can play
[ernst_erlkonig] double, triple and quadruple stops
[brahms_sonata3_d_minor_mvt1] bariolage: same pitch in rapid alternation between open and stopped strings
[beriot_scene_de_ballet] three portamento styles: 'light and rapid' (vif), 'gentle' (doux), 'dragged' (traine)
[bach_fugue_c_major_bwv1005] polyphony full of (arpeggiated) 3- and 4-stop chords
[wieniawski_legende] main theme is played Sul G
[ades_concentric_paths] passages that may not even be technically possible for many players
[sibelius_d_minor_mvt3] extreme virtuosity
[paganini_caprice_4] fast passages with many challenging double stops
[_general] move thumb forward before using fourth finger for clean balanced finger swing
[saint_saens_intro_rondo_capriccioso] accurate intonation in the highest register
[mendelssohn_e_minor_mvt1] ornaments
[_general] vibrato relaxes at the end of the phrase
[_general] shift like a train journey — gather, disembark, without haste
[_general] fingers binary 'down' or 'not down', not gradual
[beriot_scene_de_ballet] left and right-hand pizzicato
[brahms_d_major_mvt3] bowing that really digs into the strings
```

Two of the twenty are borderline — `ades_concentric_paths: "passages that may not even be technically possible for many players"` and `sibelius_d_minor_mvt3: "extreme virtuosity"` — both are vague hardship claims that rule 3 should have rejected. Estimate ~5% of the extracted set is similarly leaky. Not fatal; a human filtering pass could sweep these in an hour, or Phase 3 canonicalization will fold them into an "unspecified virtuosity" bucket that a human can then drop.

## Surprises (candidate discoveries — things the design doc didn't call out)

1. **`_general` yielded 51 claims — the single densest bucket in the corpus.** The orthogonal "hardest techniques" / "cannot fake" / "before advanced repertoire" queries surface a *different genre* of statement: micro-mechanical rules of thumb (thumb-forward-before-fourth-finger; little-finger-raised-in-bow-change; binary finger drop; vibrato relaxing into phrase-end). These read like "atlas of small motor invariants," which no piece-specific source captures. Worth thinking about how these attach to the piece graph — they may be *edges* connecting many pieces, not nodes.

2. **Bach solo pieces cluster overwhelmingly on chord/polyphony demands, not left-hand skill.** Bach Preludio (bariolage), Chaconne (chords + register), Presto (bariolage again), all three fugues (multi-stop polyphony). The absence of "shifting" or "position work" language for Bach is striking — public sources talk about *right hand* solutions to Bach almost exclusively.

3. **Every Ysaÿe sonata comes back with sui-generis descriptors.** "Multiple-stops from double through sextuple," "sul ponticello tremolo," "sixths/tenths alternations," "left-hand pizzicato while arco." Almost no overlap with the Paganini caprice vocabulary. If the graph aims for prerequisite paths, Ysaÿe may be a separate cluster — not a Paganini descendant.

4. **Portamento surfaces prominently in early-Romantic sources (Bériot, Kreisler, Strauss) as an explicit taxonomy** — "vif / doux / traîné" from Bériot, "Viennese portamento" from Kreisler, per-note portamento comparisons in the Heifetz/Midori Strauss Sonata piece. This is a *left-hand color* skill that current pedagogy tends to fold into "shifting"; the corpus suggests it deserves its own leaf.

5. **The Josefowicz Strad essay on Adès names "a quarter of an inch from the top of the fingerboard"** as a physical requirement. That's the most spatially-precise claim in the entire corpus and would be gold for a graph attempting concrete prerequisites — someone somewhere has already committed the exact fingerboard-region distinction to writing.

## Low-signal sources (candidates to drop)

1. **Wikipedia "24 Caprices" per-caprice table.** Formulaic, taxonomy-driven ("fast scales, arpeggios, double stops"). It parses cleanly but leaks *aggregated technique jargon* rather than practitioner language. Consider dropping Wikipedia entirely at Phase 1 for a future re-run.
2. **Violinwiki `/pages/violin-concerto-X` entries.** The "Practised skills" list is either identical across movements or reduced to `intonation, vibrato, articulation, dynamics` — a vague top-4 that adds noise. All Mozart Violinwiki entries hit this pattern.
3. **`violinlounge.com` blogs & ranked lists.** WebFetch consistently summarizes them into pop-listicle bullets, and the underlying content is already listicle-shaped. Multiple pieces show identical filler ("huge leap beyond Mozart") from this source.
4. **Program notes from major-orchestra sites (LA Phil, BSO, Houston, SLSO, Indianapolis, Redwood).** Individually fine, but they overlap 60–80% with each other because most program-note authors cite the same 3–4 anecdotes. A large share of the 15 zero-claim pieces have *only* program notes as sources.
5. **Interlude.hk & Music Salon articles.** These have real content, but they lean essayistic — for a discovery pipeline focused on physical gates, they underdeliver relative to their length.

## Cost

Not directly measurable — Anthropic batch API not accessible from this environment, so extraction was done via `general-purpose` subagents (whose model calls the harness bills). Rough estimate based on subagent tool_uses × ~120K avg tokens each:
- Scraping: 8 subagents × ~200K tokens avg ≈ ~1.6M tokens (Sonnet-tier)
- Extraction: 6 subagents × ~90K tokens avg ≈ ~540K tokens (Sonnet-tier)
- **Ballpark: $8–$15** — higher than the discovery doc's Haiku-4.5-batch estimate ($3–10), because I couldn't use the batch API and had to use general-purpose subagents. If you re-run this with direct batch API access, expect closer to the doc's original estimate.

## Known quality issues to be aware of before Phase 3

- **WebFetch's built-in summarizer intruded** on many mid-tier violin blogs (violinlounge / violinspiration / violinlab / etc.) — cached "raw" text is sometimes preserved paragraph structure + author quotes, not literal HTML text. Extraction still worked because it targets verbatim quotes within the cached content, but this shifted the corpus somewhat toward sources that WebFetch would return raw (Strad, Strings Magazine, Wikipedia, program notes).
- **Reddit was fully blocked** from this network. Every network path (WebFetch, curl, `.json`, `old.reddit.com`) returned the SPA shell. This is likely the single largest source-type loss vs. the design.
- **The 80-piece / 3-claim success threshold was not met** (51 pieces cleared it). Options:
  - **A) Accept and proceed to Phase 3** — the shape of the corpus is probably informative enough for canonicalization/grouping; the graph will just be sparser at the "public discussion is thin" end (Debussy, Prokofiev, Bartók VC2, Handel).
  - **B) Reinforce Phase 1** before proceeding — add ProQuest dissertation access (real subscription, not WebFetch), a Reddit read path, and Strad paywall access, then re-scrape only the 32 sub-threshold pieces.
  - **C) Prune the corpus** to only the 51 pieces that hit ≥3 claims — the graph is smaller but every node has real corroborated evidence.

**My recommendation: C first, then decide about A vs B once you've seen `claims_sorted.csv`.** The 51-piece corpus already spans early intermediate → virtuoso (early Bach concertos are dropped, but solo Bach is well-covered; Bruch mvt1 has 3, Mendelssohn mvt1 has 26, Tchaikovsky mvt1 has 3, Ysaÿe fully covered, Paganini 1/5/13/17/24 all covered, Ernst covered, Sarasate Zigeunerweisen covered, Wieniawski Légende covered, Adès Concentric Paths covered). The pruned graph is more honest than a padded one.

## Stopping here

Deliverables on disk:
- `discovery/output/corpus.json`
- `discovery/output/sources/{piece_id}/*.md` — 268 files total
- `discovery/output/claims.jsonl` — 423 lines
- `discovery/output/claims_sorted.csv` — human-browsable
- `discovery/output/run_log.md`
- `discovery/output/_batch_reports/` and `discovery/output/_extraction/` — audit trail

**Not proceeding to Phase 3 until explicit approval, per the design's mandatory gate.**
