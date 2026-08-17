#!/usr/bin/env python3
"""
Post-process Phase 2 extractor output:
  discovery/output/_extraction/ext_*.jsonl
    → discovery/output/claims.jsonl
    → discovery/output/claims_sorted.csv

- Assigns stable claim_id = SHA1(piece_id + verbatim_phrase + source_url)[:12]
- Deduplicates exact (piece_id, verbatim_phrase, source_url) collisions within a
  single source (cross-source repetition is kept — that's corroboration).
- Sorts CSV alphabetically by verbatim_phrase (case-insensitive).
"""

import csv
import glob
import hashlib
import json
import os
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "output")
EXT_DIR = os.path.join(OUT_DIR, "_extraction")


def claim_id(piece_id: str, verbatim: str, source_url: str) -> str:
    h = hashlib.sha1(f"{piece_id}|{verbatim}|{source_url}".encode("utf-8")).hexdigest()
    return h[:12]


def main():
    seen: set[tuple[str, str, str]] = set()
    out_claims: list[dict] = []
    parse_errors = 0
    schema_errors = 0
    total_lines = 0

    for path in sorted(glob.glob(os.path.join(EXT_DIR, "ext_*.jsonl"))):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                total_lines += 1
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    parse_errors += 1
                    continue
                pid = obj.get("piece_id")
                verb = obj.get("verbatim_phrase")
                url = obj.get("source_url", "")
                quote = obj.get("quote", "")
                if not (pid and verb):
                    schema_errors += 1
                    continue
                key = (pid, verb.strip().lower(), url)
                if key in seen:
                    continue
                seen.add(key)
                out_claims.append({
                    "claim_id": claim_id(pid, verb, url),
                    "piece_id": pid,
                    "verbatim_phrase": verb,
                    "quote": quote,
                    "source_url": url,
                })

    # Write claims.jsonl
    claims_path = os.path.join(OUT_DIR, "claims.jsonl")
    with open(claims_path, "w") as f:
        for c in out_claims:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")

    # Write claims_sorted.csv (alphabetical by verbatim_phrase, case-insensitive)
    csv_path = os.path.join(OUT_DIR, "claims_sorted.csv")
    sorted_claims = sorted(out_claims, key=lambda c: c["verbatim_phrase"].lower())
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["claim_id", "piece_id", "verbatim_phrase", "quote", "source_url"],
        )
        writer.writeheader()
        for c in sorted_claims:
            writer.writerow(c)

    # Stats
    piece_counter = Counter(c["piece_id"] for c in out_claims)
    src_counter = Counter(c["source_url"] for c in out_claims)
    verb_counter = Counter(c["verbatim_phrase"].strip() for c in out_claims)

    print(f"Total raw lines:     {total_lines}")
    print(f"Parse errors:        {parse_errors}")
    print(f"Schema errors:       {schema_errors}")
    print(f"Unique claims:       {len(out_claims)}")
    print(f"Distinct pieces:     {len(piece_counter)}")
    print(f"Distinct sources:    {len(src_counter)}")
    print(f"Distinct verbatims:  {len(verb_counter)}")
    print()
    print("Top-30 exact-string verbatim_phrase counts:")
    for phrase, n in verb_counter.most_common(30):
        print(f"  {n:3d}  {phrase}")
    print()
    print("Pieces with <3 claims (may need drop):")
    thin = [(p, n) for p, n in piece_counter.items() if n < 3]
    for p, n in sorted(thin, key=lambda x: x[1]):
        print(f"  {n}  {p}")


if __name__ == "__main__":
    main()
