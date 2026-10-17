#!/usr/bin/env python3
"""Find normalized literal repetitions with original-source coordinates.

This is a retrieval aid, not a claim of redundant narrative function. Normalization
retains Unicode letters and digits, preserving an offset map for every character.
"""
from __future__ import annotations

import argparse
import sys
from collections import defaultdict

from language_scan import (ValidationError, context, fingerprint, load_units,
                           output_json, read_json, require)


def normalize(text):
    positions = [index for index, char in enumerate(text) if char.isalpha() or char.isdigit()]
    return "".join(text[index] for index in positions), positions


def anchor(unit, positions, start, end):
    original_start, original_end = positions[start], positions[end - 1] + 1
    return {"unit_id": unit["unit_id"], "path": unit["path"], "source_sha256": unit["source_sha256"],
            "start": original_start, "end": original_end, "text": unit["text"][original_start:original_end],
            "line": unit["text"].count("\n", 0, original_start) + 1,
            **context(unit["text"], original_start, original_end)}


def scan_repeats(root, manifest, min_length=10, max_results=200, watch=None):
    require(type(min_length) is int and min_length > 0, "min_length must be a positive integer")
    require(type(max_results) is int and max_results > 0, "max_results must be a positive integer")
    watch = [] if watch is None else watch
    require(isinstance(watch, list) and all(isinstance(term, str) and term for term in watch), "watch terms must be nonempty strings")
    units = load_units(root, manifest)
    normalized = [normalize(unit["text"]) for unit in units]
    seeds = defaultdict(list)
    for unit_index, (text, _) in enumerate(normalized):
        for position in range(max(0, len(text) - min_length + 1)):
            seeds[text[position:position + min_length]].append((unit_index, position))
    results, seen, truncated, covered = [], set(), False, defaultdict(list)
    # One representative is compared with each other occurrence of a seed. This
    # retrieves each location without materializing quadratically many pairs.
    # Already-covered seed positions cannot produce a new maximal pair.
    for seed, locations in seeds.items():
        if len(locations) < 2:
            continue
        left_index, left_start = locations[0]
        left_text = normalized[left_index][0]
        for right_index, right_start in locations[1:]:
            diagonal = (left_index, right_index, right_start - left_start)
            if any(start <= left_start and left_start + min_length <= end for start, end in covered[diagonal]):
                continue
            right_text = normalized[right_index][0]
            a, b, length = left_start, right_start, min_length
            while a > 0 and b > 0 and left_text[a - 1] == right_text[b - 1]:
                a -= 1
                b -= 1
                length += 1
            while a + length < len(left_text) and b + length < len(right_text) and left_text[a + length] == right_text[b + length]:
                length += 1
            key = (left_index, a, right_index, b, length)
            covered[diagonal].append((a, a + length))
            if key in seen:
                continue
            seen.add(key)
            if len(results) >= max_results:
                truncated = True
                break
            results.append({"id": "repeat-" + fingerprint(key)[:24], "normalized_text": left_text[a:a + length],
                            "normalized_length": length,
                            "left": anchor(units[left_index], normalized[left_index][1], a, a + length),
                            "right": anchor(units[right_index], normalized[right_index][1], b, b + length),
                            "same_unit_overlaps": left_index == right_index and a + length > b})
        if truncated:
            break
    watched = []
    for term in dict.fromkeys(watch):
        locations = []
        for unit in units:
            position = 0
            while True:
                position = unit["text"].find(term, position)
                if position < 0:
                    break
                end = position + len(term)
                locations.append({"unit_id": unit["unit_id"], "path": unit["path"], "source_sha256": unit["source_sha256"],
                                  "start": position, "end": end, "text": term, **context(unit["text"], position, end)})
                position += 1
        watched.append({"term": term, "count": len(locations), "locations": locations})
    return {"schema_version": 1, "kind": "repeat_scan", "status": "NEEDS_VERIFICATION",
            "manifest": manifest, "min_length": min_length, "max_results": max_results,
            "truncated": truncated, "matches": results, "watch_terms": watched,
            "units": [{key: value for key, value in unit.items() if key != "text"} for unit in units],
            "limits": ["Only Unicode letters and digits are compared; case is preserved.",
                       "Each seed is paired with its first location, not every possible pair; output may overlap.",
                       "No entity filtering or synonym matching; LLM judges narrative function and whether repetition is useful.",
                       "No matches does not establish absence of semantic repetition; truncated output is incomplete."]}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--min-length", type=int, default=10)
    parser.add_argument("--max-results", type=int, default=200)
    parser.add_argument("--watch", action="append", default=[])
    parser.add_argument("--output", help="new JSON artifact; an existing file is never overwritten")
    args = parser.parse_args(argv)
    try:
        result = scan_repeats(args.project_root, read_json(args.manifest), args.min_length, args.max_results, args.watch)
        output_json(result, args.output)
        return 0
    except (ValidationError, OSError, ValueError, KeyError, TypeError) as exc:
        print("repeat scan error: " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
