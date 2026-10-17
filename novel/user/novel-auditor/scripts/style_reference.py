#!/usr/bin/env python3
"""Collect reproducible language evidence and compare frozen reference distributions.

Reports describe usage; neither a successful command nor a statistical deviation
accepts prose or authorizes a rewrite. See ../references/style-reference.md.
"""
from __future__ import annotations

import argparse
import copy
import importlib.util
import math
from pathlib import Path
import sys


# Resolve the sibling in both source and flat installations, independent of cwd
# and of unrelated modules named language_scan already present in sys.modules.
_spec = importlib.util.spec_from_file_location(
    "_style_language_scan", Path(__file__).resolve().with_name("language_scan.py"))
language = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(language)
ValidationError = language.ValidationError
require = language.require
fingerprint = language.fingerprint

ENGINE = "style-reference-v1"
MEASUREMENT = {"denominator": "nonwhite_characters", "normalization": "none",
               "overlap": "merge_connected", "window_algorithm": "nonwhite-v1"}
ROLES = {"fit", "calibration", "holdout", "target"}


def nonempty(value, label):
    require(isinstance(value, str) and bool(value.strip()), label + " must be nonempty text")


def integer(value, label, minimum=1):
    require(type(value) is int and value >= minimum, label + " must be an integer >= " + str(minimum))


def exact_keys(value, required, optional=(), label="object"):
    require(isinstance(value, dict), label + " must be an object")
    require(set(required) <= set(value) <= set(required) | set(optional), label + " has missing or unknown keys")


def seal(value, key):
    result = copy.deepcopy(value)
    result[key] = fingerprint(result)
    return result


def check_seal(value, kind, key):
    require(isinstance(value, dict) and value.get("schema_version") == 1
            and value.get("kind") == kind and value.get("engine") == ENGINE,
            "incompatible " + kind + " schema or engine")
    body = {k: v for k, v in value.items() if k != key}
    require(value.get(key) == fingerprint(body), "modified " + kind + "; regenerate artifact")


def validate_features(spec):
    exact_keys(spec, {"schema_version", "measurement", "features"}, label="feature spec")
    require(spec["schema_version"] == 1, "feature schema_version must be 1")
    measure = spec["measurement"]
    exact_keys(measure, set(MEASUREMENT) | {"window_chars"}, label="measurement")
    require(all(measure[k] == v for k, v in MEASUREMENT.items()), "unsupported measurement contract")
    if measure["window_chars"] is not None:
        integer(measure["window_chars"], "window_chars")
    require(isinstance(spec["features"], list) and spec["features"], "features must be nonempty")
    categories = []
    for item in spec["features"]:
        exact_keys(item, {"id", "definition", "forms", "count_basis"},
                   {"label", "legacy_category_id"}, "feature")
        require(item["count_basis"] in {"surface", "semantic"}, "invalid count_basis")
        for name in ("label", "legacy_category_id"):
            if name in item:
                nonempty(item[name], name)
        require(isinstance(item["forms"], list), "forms must be a list")
        for form in item["forms"]:
            exact_keys(form, {"kind", "value"}, label="feature form")
        categories.append({k: item[k] for k in ("id", "definition", "forms")})
    language.validate_profile({"schema_version": 1, "profile_id": "reference-features", "revision": 1,
                               "scope": "measurement only", "calibration_sources": ["feature spec"],
                               "categories": categories})
    return spec


def load_corpus(root, manifest):
    exact_keys(manifest, {"schema_version", "language", "text_type", "units"},
               {"profile_id", "revision", "scope"}, "manifest")
    for name in ("language", "text_type"):
        nonempty(manifest[name], name)
    units = language.load_units(root, manifest)
    hashes, partitions, origins = set(), {}, []
    for unit, item in zip(units, manifest["units"]):
        exact_keys(item, {"unit_id", "path", "complete_chapter", "source_group", "partition_group",
                          "register", "role"}, {"extraction"}, "manifest unit")
        for key in ("source_group", "partition_group", "register"):
            nonempty(item[key], key)
        require(item["role"] in ROLES, "invalid corpus role")
        require(unit["source_sha256"] not in hashes, "duplicate source content; count one representation")
        hashes.add(unit["source_sha256"])
        partition = (item["source_group"], item["partition_group"])
        require(partition not in partitions or partitions[partition] == item["role"],
                "partition_group crosses dataset roles")
        partitions[partition] = item["role"]
        unit.update({key: item[key] for key in ("source_group", "partition_group", "register", "role")})
        if "extraction" in item:
            origin = item["extraction"]
            exact_keys(origin, {"path", "source_sha256", "start", "end"}, label="extraction")
            data = language.safe_path(root, origin["path"]).read_bytes()
            original = data.decode("utf-8")
            require(language.digest(data) == origin["source_sha256"], "stale extraction source")
            integer(origin["start"], "extraction start", 0)
            integer(origin["end"], "extraction end")
            require(origin["start"] < origin["end"] <= len(original), "invalid extraction span")
            require(original[origin["start"]:origin["end"]] == unit["text"], "extracted text differs from source span")
            unit["extraction"] = copy.deepcopy(origin)
            provenance = (origin["source_sha256"], origin["start"], origin["end"])
        else:
            provenance = (unit["source_sha256"], 0, len(unit["text"]))
        for old_hash, start, end in origins:
            require(old_hash != provenance[0] or max(start, provenance[1]) >= min(end, provenance[2]),
                    "overlapping original source ranges")
        origins.append(provenance)
        unit["origin"] = {"sha256": provenance[0], "start": provenance[1], "end": provenance[2]}
    return units


def windows(text, size):
    if size is None:
        return []
    positions = [i for i, char in enumerate(text) if not char.isspace()]
    result = []
    for offset in range(0, len(positions), size):
        start = positions[offset] if offset else 0
        end = positions[offset + size] if offset + size < len(positions) else len(text)
        count = min(size, len(positions) - offset)
        result.append({"start": start, "end": end, "nonwhite_characters": count,
                       "partial": count != size})
    return result


def collect(root, manifest, spec):
    validate_features(spec)
    units = load_corpus(root, manifest)
    feature_hash = fingerprint(spec)
    occurrences, raw_matches, rows = [], [], []
    for unit in units:
        uid = unit["unit_id"]
        unit["windows"] = windows(unit["text"], spec["measurement"]["window_chars"])
        for feature in spec["features"]:
            hits, raw = language.find_occurrences(unit, feature)
            for hit in hits:
                hit["feature_id"] = hit.pop("category_id")
                hit["id"] = "style-hit-" + fingerprint([ENGINE, feature_hash, hit["id"]])[:24]
            occurrences.extend(hits)
            raw_matches.append({"unit_id": uid, "feature_id": feature["id"], "matches": raw})
            ranges = [{"start": 0, "end": len(unit["text"]), "nonwhite_characters": unit["nonwhite_characters"],
                       "partial": False, "scope_kind": "unit", "window_index": None}]
            ranges += [dict(window, scope_kind="window", window_index=index)
                       for index, window in enumerate(unit["windows"])]
            for span in ranges:
                selected = [h["id"] for h in hits if span["start"] <= h["start"] < span["end"]]
                row = {"unit_id": uid, "feature_id": feature["id"], **span,
                       "surface_count": len(selected), "occurrence_ids": selected}
                row["row_id"] = "style-row-" + fingerprint([feature_hash, unit["source_sha256"], row])[:24]
                rows.append(row)
    result = seal({"schema_version": 1, "kind": "style_evidence", "engine": ENGINE,
                   "manifest": manifest, "feature_spec": spec, "feature_sha256": feature_hash,
                   "units": [{k: v for k, v in u.items() if k != "text"} for u in units],
                   "raw_matches": raw_matches, "occurrences": occurrences, "statistics": rows}, "evidence_id")
    # The template is derived on demand, so its evidence_id has no cyclic hash.
    return result


def verify_evidence(root, evidence):
    check_seal(evidence, "style_evidence", "evidence_id")
    fresh = collect(root, evidence["manifest"], evidence["feature_spec"])
    require(fresh == evidence, "stale or modified evidence; collect again")


def annotation_template(evidence):
    semantic = {f["id"] for f in evidence["feature_spec"]["features"] if f["count_basis"] == "semantic"}
    return {"schema_version": 1, "evidence_id": evidence["evidence_id"],
            "feature_sha256": evidence["feature_sha256"], "reviewer": "",
            "classifications": [{"id": h["id"], "applies": None, "reason": ""}
                                for h in evidence["occurrences"] if h["feature_id"] in semantic]}


def classified_rows(evidence, annotations=None):
    features = {f["id"]: f for f in evidence["feature_spec"]["features"]}
    semantic_hits = {h["id"] for h in evidence["occurrences"] if features[h["feature_id"]]["count_basis"] == "semantic"}
    labels = {}
    if annotations is not None:
        exact_keys(annotations, {"schema_version", "evidence_id", "feature_sha256", "reviewer", "classifications"},
                   label="annotations")
        require(annotations["schema_version"] == 1 and annotations["evidence_id"] == evidence["evidence_id"]
                and annotations["feature_sha256"] == evidence["feature_sha256"], "stale annotations")
        require(isinstance(annotations["classifications"], list), "classifications must be a list")
        require(isinstance(annotations["reviewer"], str), "reviewer must be text")
        for item in annotations["classifications"]:
            exact_keys(item, {"id", "applies", "reason"}, label="classification")
            require(item["id"] in semantic_hits and item["id"] not in labels, "unknown or duplicate classification")
            require(item["applies"] is None or type(item["applies"]) is bool, "applies must be boolean or null")
            require(isinstance(item["reason"], str), "classification reason must be text")
            if item["applies"] is not None:
                nonempty(item["reason"], "classification reason")
                nonempty(annotations["reviewer"], "reviewer and version")
            labels[item["id"]] = item
    rows = []
    for original in evidence["statistics"]:
        row = copy.deepcopy(original)
        semantic = features[row["feature_id"]]["count_basis"] == "semantic"
        unresolved = [i for i in row["occurrence_ids"] if labels.get(i, {}).get("applies") is None] if semantic else []
        counted = [i for i in row["occurrence_ids"] if labels.get(i, {}).get("applies") is True] if semantic else row["occurrence_ids"]
        row.update(count_basis="semantic" if semantic else "surface", unresolved_ids=unresolved,
                   confirmed_count=len(counted), counted_ids=counted, count=None if unresolved else len(counted))
        row["per_10000"] = None if unresolved else 10000 * row["count"] / row["nonwhite_characters"]
        rows.append(row)
    return rows


def quantile(values, probability):
    """Linear interpolation at (n - 1) * probability, including zero rows."""
    if not values:
        return None
    ordered = sorted(values)
    position = (len(ordered) - 1) * probability
    lower, upper = math.floor(position), math.ceil(position)
    return ordered[lower] + (ordered[upper] - ordered[lower]) * (position - lower)


def summary(rows, units):
    totals = [r for r in rows if r["scope_kind"] == "unit"]
    full = [r for r in rows if r["scope_kind"] == "window" and not r["partial"]]
    partial = [r for r in rows if r["scope_kind"] == "window" and r["partial"]]
    complete = all(r["count"] is not None for r in totals)
    denominator = sum(r["nonwhite_characters"] for r in totals)
    count = sum(r["confirmed_count"] for r in totals) if complete else None
    rates = [r["per_10000"] for r in full] if complete else []
    hit_units = {r["unit_id"] for r in totals if r["confirmed_count"] > 0}
    return {"complete": complete, "unit_count": len(totals),
            "partition_count": len({(u["source_group"], u["partition_group"]) for u in units}),
            "nonwhite_characters": denominator, "surface_count": sum(r["surface_count"] for r in totals),
            "confirmed_count": sum(r["confirmed_count"] for r in totals), "count": count,
            "per_10000": 10000 * count / denominator if complete and denominator else None,
            "feature_partition_count": len({(u["source_group"], u["partition_group"]) for u in units if u["unit_id"] in hit_units}),
            "unresolved_ids": [i for r in totals for i in r["unresolved_ids"]],
            "full_window_count": len(full), "partial_window_count": len(partial),
            "window_rates": rates,
            "window_presence": sum(r["count"] > 0 for r in full) / len(full) if complete and full else None,
            "quantiles": {str(q): quantile(rates, q) for q in (0.1, 0.5, 0.9)},
            "quantile_algorithm": "linear-v1"}


def grouped_summaries(evidence, rows, role):
    units = [u for u in evidence["units"] if u["role"] == role]
    result = []
    for group, register in sorted({(u["source_group"], u["register"]) for u in units}):
        selected = [u for u in units if (u["source_group"], u["register"]) == (group, register)]
        ids = {u["unit_id"] for u in selected}
        for feature in evidence["feature_spec"]["features"]:
            matching = [r for r in rows if r["unit_id"] in ids and r["feature_id"] == feature["id"]]
            result.append({"source_group": group, "register": register, "feature_id": feature["id"],
                           "statistics": summary(matching, selected)})
    return result


POLICY_PARAMETERS = {"min_partitions", "min_windows", "min_feature_count", "min_feature_partitions",
                     "upper_quantile", "min_extra_count"}


def validate_policy(policy, evidence, annotations):
    exact_keys(policy, {"schema_version", "feature_sha256", "parameters", "calibration"}, label="policy")
    require(policy["schema_version"] == 1 and policy["feature_sha256"] == evidence["feature_sha256"], "incompatible policy")
    require(evidence["feature_spec"]["measurement"]["window_chars"] is not None, "policy needs fixed windows")
    params = policy["parameters"]
    exact_keys(params, POLICY_PARAMETERS, label="policy parameters")
    for key in POLICY_PARAMETERS - {"upper_quantile", "min_extra_count"}:
        integer(params[key], key)
    require(params["min_partitions"] >= 2 and params["min_windows"] >= 2,
            "calibration requires at least two partitions and windows; this is not a literary limit")
    for key in ("upper_quantile", "min_extra_count"):
        require(type(params[key]) in (int, float) and math.isfinite(params[key]), key + " must be finite")
    require(0.5 < params["upper_quantile"] <= 1 and params["min_extra_count"] > 0, "invalid upper tail or practical difference")
    record = policy["calibration"]
    exact_keys(record, {"evidence_id", "annotations_sha256", "parameter_sha256", "unit_ids", "assessment"}, label="calibration")
    require(record["evidence_id"] == evidence["evidence_id"]
            and record["annotations_sha256"] == fingerprint(annotations)
            and record["parameter_sha256"] == fingerprint(params), "stale calibration record")
    units = [u for u in evidence["units"] if u["role"] == "calibration"]
    require(isinstance(record["unit_ids"], list) and len(record["unit_ids"]) == len(set(record["unit_ids"]))
            and set(record["unit_ids"]) == {u["unit_id"] for u in units}, "calibration units must match evidence")
    require(len({(u["source_group"], u["partition_group"]) for u in units}) >= 2, "independent calibration partitions required")
    nonempty(record["assessment"], "calibration assessment")


def eligibility(stats, policy, calibration=None):
    reasons = []
    if not stats["complete"]:
        reasons.append("incomplete_reference_classification")
    if not stats["full_window_count"]:
        reasons.append("no_full_reference_windows")
    if stats["count"] == 0:
        reasons.append("feature_not_observed_in_reference")
    if policy is None:
        reasons.append("descriptive_profile")
    else:
        params = policy["parameters"]
        for field, minimum in (("partition_count", "min_partitions"), ("full_window_count", "min_windows"),
                               ("feature_partition_count", "min_feature_partitions")):
            if stats[field] < params[minimum]:
                reasons.append("insufficient_" + field)
        if stats["count"] is None or stats["count"] < params["min_feature_count"]:
            reasons.append("insufficient_feature_count")
        if calibration is not None and (not calibration["complete"] or calibration["partition_count"] < 2
                                        or not calibration["full_window_count"]):
            reasons.append("insufficient_calibration_coverage")
    return reasons


def window_difference(row, stats, params=None):
    rates = stats["window_rates"]
    rate = row["per_10000"]
    if row["partial"] or rate is None or not rates:
        return {"comparable": False, "candidate": False}
    median = quantile(rates, 0.5)
    result = {"comparable": True, "candidate": False,
              "empirical_percentile": (sum(x < rate for x in rates) + 0.5 * sum(x == rate for x in rates)) / len(rates),
              "delta_from_median": rate - median}
    if params is not None:
        threshold = quantile(rates, params["upper_quantile"])
        extra = row["count"] - threshold * row["nonwhite_characters"] / 10000
        result.update(reference_upper_rate=threshold, extra_count=extra,
                      candidate=rate > threshold and extra >= params["min_extra_count"])
    return result


def build(root, evidence, annotations=None, policy=None):
    verify_evidence(root, evidence)
    manifest = evidence["manifest"]
    for field in ("profile_id", "scope"):
        nonempty(manifest.get(field), field)
    integer(manifest.get("revision"), "reference revision")
    require(all(u["role"] in {"fit", "calibration"} for u in evidence["units"]),
            "build accepts fit/calibration only; holdout and target stay separate")
    require(any(u["role"] == "fit" for u in evidence["units"]), "fit units required")
    rows = classified_rows(evidence, annotations)
    groups = grouped_summaries(evidence, rows, "fit")
    calibration = grouped_summaries(evidence, rows, "calibration")
    if policy is not None:
        validate_policy(policy, evidence, annotations)
    calibration_by_key = {(g["source_group"], g["register"], g["feature_id"]): g["statistics"] for g in calibration}
    for group in groups:
        key = (group["source_group"], group["register"], group["feature_id"])
        cal = calibration_by_key.get(key, {"complete": False, "partition_count": 0, "full_window_count": 0})
        group["advisory_limits"] = eligibility(group["statistics"], policy, cal)
    cal_results = []
    if policy is not None:
        by_uid = {u["unit_id"]: u for u in evidence["units"]}
        group_map = {(g["source_group"], g["register"], g["feature_id"]): g for g in groups}
        for row in rows:
            unit = by_uid[row["unit_id"]]
            if unit["role"] != "calibration" or row["scope_kind"] != "window":
                continue
            key = (unit["source_group"], unit["register"], row["feature_id"])
            group = group_map.get(key)
            limits = group["advisory_limits"] if group else ["no_matching_fit_group"]
            params = policy["parameters"] if not limits else None
            difference = window_difference(row, group["statistics"], params) if group else {"comparable": False, "candidate": False}
            cal_results.append({"row_id": row["row_id"], "unit_id": row["unit_id"],
                                "feature_id": row["feature_id"], "source_group": unit["source_group"],
                                "advisory_limits": limits, **difference})
    return seal({"schema_version": 1, "kind": "style_reference", "engine": ENGINE,
                 "profile_id": manifest["profile_id"], "revision": manifest["revision"], "scope": manifest["scope"],
                 "language": manifest["language"], "text_type": manifest["text_type"],
                 "feature_spec": evidence["feature_spec"], "feature_sha256": evidence["feature_sha256"],
                 "evidence_id": evidence["evidence_id"], "annotations_sha256": fingerprint(annotations),
                 "source_units": evidence["units"], "state": "calibrated" if policy is not None else "descriptive",
                 "groups": groups, "calibration_statistics": calibration, "calibration_results": cal_results,
                 "policy": policy,
                 "limits": ["Frozen corpus snapshot; hashes bind records, not annotation truth or literary quality.",
                            "Calibration assessment is a recorded editorial judgment, not a proof of improved prose."]}, "reference_id")


def check_independence(target, reference):
    for unit in target:
        for source in reference:
            require(unit["source_sha256"] != source["source_sha256"], "target duplicates reference/calibration text")
            require((unit["source_group"], unit["partition_group"]) != (source["source_group"], source["partition_group"]),
                    "target shares reference/calibration partition")
            a, b = unit["origin"], source["origin"]
            require(a["sha256"] != b["sha256"] or max(a["start"], b["start"]) >= min(a["end"], b["end"]),
                    "target overlaps reference/calibration extraction")


def compare(root, evidence, reference, annotations=None, reference_group=None, max_results=None):
    verify_evidence(root, evidence)
    check_seal(reference, "style_reference", "reference_id")
    require(reference["feature_sha256"] == evidence["feature_sha256"]
            and reference["feature_spec"] == evidence["feature_spec"], "incompatible features or measurement; collect again")
    require(reference["language"] == evidence["manifest"]["language"]
            and reference["text_type"] == evidence["manifest"]["text_type"], "incompatible language or text_type")
    require(all(u["role"] in {"target", "holdout"} for u in evidence["units"]), "compare requires target or holdout units")
    check_independence(evidence["units"], reference["source_units"])
    available = sorted({g["source_group"] for g in reference["groups"]})
    if reference_group is None:
        require(len(available) == 1, "multiple reference groups; select --reference-group explicitly")
        reference_group = available[0]
    require(reference_group in available, "unknown reference group")
    if max_results is not None:
        integer(max_results, "max_results")
    reference_map = {(g["register"], g["feature_id"]): g for g in reference["groups"] if g["source_group"] == reference_group}
    rows = classified_rows(evidence, annotations)
    comparisons, candidates = [], []
    for unit in evidence["units"]:
        for feature in evidence["feature_spec"]["features"]:
            matching = [r for r in rows if r["unit_id"] == unit["unit_id"] and r["feature_id"] == feature["id"]]
            target = summary(matching, [unit])
            group = reference_map.get((unit["register"], feature["id"]))
            reasons = list(group["advisory_limits"]) if group else ["register_mismatch"]
            if not target["complete"]:
                reasons.append("incomplete_target_classification")
            if not target["full_window_count"]:
                reasons.append("no_full_target_windows")
            params = reference["policy"]["parameters"] if reference["policy"] is not None and not reasons else None
            differences = []
            for row in matching:
                if row["scope_kind"] != "window":
                    continue
                difference = window_difference(row, group["statistics"], params) if group else {"comparable": False, "candidate": False}
                details = {**row, **difference}
                differences.append(details)
                if difference["candidate"]:
                    candidates.append({"row_id": row["row_id"], "unit_id": unit["unit_id"],
                                       "feature_id": feature["id"], "start": row["start"], "end": row["end"],
                                       "occurrence_ids": row["counted_ids"], "count": row["count"],
                                       "reference_upper_rate": difference["reference_upper_rate"],
                                       "extra_count": difference["extra_count"], "decision": "context_review"})
            comparisons.append({"unit_id": unit["unit_id"], "feature_id": feature["id"], "count_basis": feature["count_basis"],
                                "register": unit["register"], "reference_group": reference_group,
                                "advisory_limits": reasons, "target": target,
                                "reference": group["statistics"] if group else None, "windows": differences})
    candidates.sort(key=lambda r: (-r["extra_count"], r["unit_id"], r["start"], r["feature_id"]))
    count = len(candidates)
    return seal({"schema_version": 1, "kind": "style_comparison", "engine": ENGINE,
                 "evidence_id": evidence["evidence_id"], "reference_id": reference["reference_id"],
                 "feature_sha256": evidence["feature_sha256"], "annotations_sha256": fingerprint(annotations),
                 "source_units": evidence["units"], "reference_group": reference_group,
                 "measurement_status": "complete" if all(c["target"]["complete"] for c in comparisons) else "partial",
                 "comparisons": comparisons, "occurrences": evidence["occurrences"],
                 "review_candidates": candidates[:max_results] if max_results else candidates,
                 "candidate_total": count, "truncated": max_results is not None and count > max_results,
                 "limits": ["Advisory language evidence only; no prose acceptance or automatic rewriting.",
                            "Lower frequency does not request filling a quota. Reference snapshot is not revalidated against its original files."]}, "comparison_id")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("collect", "build", "compare"):
        cmd = commands.add_parser(name)
        cmd.add_argument("--source-root", required=True)
        cmd.add_argument("--output", help="new JSON artifact; parent must exist")
        if name == "collect":
            cmd.add_argument("--manifest", required=True)
            cmd.add_argument("--features", required=True)
            cmd.add_argument("--template-output", help="optional new annotation-template JSON artifact")
        else:
            cmd.add_argument("--evidence", required=True)
            cmd.add_argument("--annotations")
        if name == "build":
            cmd.add_argument("--policy")
        if name == "compare":
            cmd.add_argument("--reference", required=True)
            cmd.add_argument("--reference-group")
            cmd.add_argument("--max-results", type=int)
    args = parser.parse_args(argv)
    try:
        read = language.read_json
        if args.command == "collect":
            result = collect(args.source_root, read(args.manifest), read(args.features))
            destinations = [Path(p).resolve() for p in (args.output, args.template_output) if p]
            require(len(destinations) == len(set(destinations)), "output and template-output must differ")
            require(all(not p.exists() for p in destinations), "output already exists; choose new artifact paths")
        else:
            evidence = read(args.evidence)
            annotations = read(args.annotations) if args.annotations else None
            if args.command == "build":
                result = build(args.source_root, evidence, annotations, read(args.policy) if args.policy else None)
            else:
                result = compare(args.source_root, evidence, read(args.reference), annotations,
                                 args.reference_group, args.max_results)
        language.output_json(result, args.output)
        if args.command == "collect" and args.template_output:
            language.output_json(annotation_template(result), args.template_output)
        return 0
    except (ValidationError, OSError, ValueError, KeyError, TypeError) as exc:
        print("style reference error: " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
