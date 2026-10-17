#!/usr/bin/env python3
"""Deterministic evidence for an LLM language review; never a semantic classifier.

All offsets are zero-based Unicode character offsets, with exclusive ends. Source
hashes cover the original UTF-8 bytes, including line endings. See language-tools.md.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
from pathlib import Path


class ValidationError(ValueError):
    """An input cannot support the claimed review."""


def require(condition, message):
    if not condition:
        raise ValidationError(message)


def digest(data):
    if isinstance(data, str):
        data = data.encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def fingerprint(value):
    return digest(canonical(value))


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def nonwhite(text):
    return sum(not char.isspace() for char in text)


def safe_path(root, relative):
    require(isinstance(relative, str) and bool(relative), "path must be a nonempty relative path")
    name = Path(relative)
    require(not name.is_absolute() and ".." not in name.parts, "path must remain within project root")
    root = Path(root).resolve()
    path = (root / name).resolve()
    require(path != root and root in path.parents, "path escapes project root")
    require(path.is_file(), "source file not found: " + relative)
    return path


def load_units(root, manifest):
    require(isinstance(manifest, dict) and manifest.get("schema_version") == 1, "manifest schema_version must be 1")
    require(isinstance(manifest.get("units"), list) and manifest["units"], "manifest units must be nonempty")
    seen_ids, seen_paths, units = set(), set(), []
    for item in manifest["units"]:
        require(isinstance(item, dict), "unit must be an object")
        require("reading" not in item and "canonical" not in item,
                "language scans require one published reading file per unit; sliced mapping manifests are not supported")
        uid = item.get("unit_id")
        require(isinstance(uid, str) and uid.strip() and uid not in seen_ids, "unit_id must be unique and nonempty")
        require(type(item.get("complete_chapter")) is bool, "complete_chapter must be explicit boolean")
        path = safe_path(root, item.get("path"))
        require(path not in seen_paths, "a source file cannot be counted twice; use one reading representation")
        seen_ids.add(uid)
        seen_paths.add(path)
        data = path.read_bytes()
        text = data.decode("utf-8")
        require(bool(text.strip()), "empty reading unit: " + uid)
        units.append({"unit_id": uid, "path": item["path"], "complete_chapter": item["complete_chapter"],
                      "source_sha256": digest(data), "text": text, "nonwhite_characters": nonwhite(text)})
    return units


DEFAULT_TERMS = (
    "与此同时 值得注意的是 毫无疑问 不言而喻 某种意义上 在这一刻 就在此时 事实上 显而易见 毋庸置疑 "
    "不禁 心中涌起 一股莫名的 内心深处 五味杂陈 百感交集 心头一震 眼中闪过一丝 嘴角微微上扬 嘴角勾起一抹 "
    "深邃 璀璨 凝重 肃穆 淡然 从容 不由自主 浑然不觉 恍若隔世 宛如 "
    "这一切 而这 或许 也许，这就是 在这个世界上 命运的齿轮开始转动"
).split()


def default_profile():
    categories = [{"id": "term-" + str(index + 1), "label": term,
                   "definition": "LLM determines the contextual use; frequency is a review trigger.",
                   "forms": [{"kind": "literal", "value": term}], "thresholds": {"chapter_at_least": 2}}
                  for index, term in enumerate(DEFAULT_TERMS)]
    categories += [
        {"id": "contrast", "label": "不是 X，是 Y", "definition": "Confirm the contrast construction in context.",
         "forms": [{"kind": "regex", "value": r"不是[^。！？\n]{1,80}?(?:而是|(?<!不)是)"}],
         "thresholds": {"chapter_more_than": 3}},
        {"id": "dash", "label": "破折号", "definition": "Confirm a narrative dash rather than protected syntax.",
         "forms": [{"kind": "literal", "value": "——"}], "thresholds": {"chapter_more_than": 15}},
    ]
    return {"schema_version": 1, "profile_id": "generic-language-review", "revision": 1,
            "scope": "Chinese prose; inherited initial review triggers, not universal literary limits",
            "calibration_sources": ["Shared language rules; project calibration must record its own evidence"],
            "categories": categories}


THRESHOLDS = {"chapter_at_least", "chapter_more_than", "per_10000_more_than", "paragraph_at_least"}


def validate_profile(profile):
    require(isinstance(profile, dict) and profile.get("schema_version") == 1, "profile schema_version must be 1")
    require(isinstance(profile.get("profile_id"), str) and profile["profile_id"].strip(), "profile_id required")
    require(type(profile.get("revision")) is int and profile["revision"] > 0, "positive profile revision required")
    require(isinstance(profile.get("scope"), str) and profile["scope"].strip(), "profile scope required")
    require(isinstance(profile.get("calibration_sources"), list) and profile["calibration_sources"], "calibration sources required")
    require(isinstance(profile.get("categories"), list) and profile["categories"], "categories must be nonempty")
    seen = set()
    for category in profile["categories"]:
        require(isinstance(category, dict), "category must be an object")
        cid = category.get("id")
        require(isinstance(cid, str) and cid.strip() and cid not in seen, "unique category id required")
        seen.add(cid)
        require(isinstance(category.get("definition"), str) and category["definition"].strip(), "category definition required")
        require(isinstance(category.get("forms"), list) and category["forms"], "category forms required")
        for form in category["forms"]:
            require(isinstance(form, dict) and form.get("kind") in {"literal", "regex"}, "form kind must be literal or regex")
            require(isinstance(form.get("value"), str) and form["value"], "nonempty form required")
            if form["kind"] == "regex":
                try:
                    expression = re.compile(form["value"])
                except re.error as exc:
                    raise ValidationError("invalid profile regex: " + str(exc)) from exc
                require(expression.search("") is None, "regex must not match empty text")
        thresholds = category.get("thresholds", {})
        require(isinstance(thresholds, dict) and set(thresholds) <= THRESHOLDS, "unknown threshold")
        for key, value in thresholds.items():
            require(type(value) in {int, float} and math.isfinite(value) and value > 0, "threshold must be positive and finite")
            if key != "per_10000_more_than":
                require(type(value) is int, "count threshold must be integer")
    return profile


def paragraphs(text):
    """A paragraph is a nonblank block; adjacent single newlines stay together."""
    result, start = [], 0
    for match in re.finditer(r"(?:\r?\n)[ \t]*(?:\r?\n)+", text):
        if text[start:match.start()].strip():
            result.append((start, match.start()))
        start = match.end()
    if text[start:].strip():
        result.append((start, len(text)))
    return result


def context(text, start, end):
    return {"before": text[max(0, start - 60):start], "after": text[end:end + 60]}


def occurrence(unit, category, start, end, forms):
    text = unit["text"]
    return {"id": "hit-" + fingerprint([unit["unit_id"], unit["source_sha256"], category, start, end])[:24],
            "unit_id": unit["unit_id"], "path": unit["path"], "source_sha256": unit["source_sha256"],
            "category_id": category, "start": start, "end": end, "text": text[start:end],
            "line": text.count("\n", 0, start) + 1, "forms": forms, **context(text, start, end)}


def find_occurrences(unit, category):
    text, spans = unit["text"], []
    for index, form in enumerate(category["forms"]):
        if form["kind"] == "literal":
            offset = 0
            while True:
                offset = text.find(form["value"], offset)
                if offset < 0:
                    break
                spans.append((offset, offset + len(form["value"]), index))
                offset += 1
        else:
            for match in re.finditer(form["value"], text):
                require(match.end() > match.start(), "regex produced empty match")
                spans.append((match.start(), match.end(), index))
    # Connected overlapping spans describe one contextual occurrence. Adjacent
    # nonoverlapping spans remain two occurrences. Keep all raw matches as evidence.
    groups = []
    for start, end, form_index in sorted(spans):
        if groups and start < groups[-1][1]:
            groups[-1][1] = max(end, groups[-1][1])
            groups[-1][2].add(form_index)
        else:
            groups.append([start, end, {form_index}])
    hits = [occurrence(unit, category["id"], start, end, sorted(forms)) for start, end, forms in groups]
    raw = [{"start": start, "end": end, "form_index": index} for start, end, index in sorted(spans)]
    return hits, raw


def automatic_protection(text):
    """Protect recognizable technical syntax only from punctuation diagnostics."""
    spans = []
    expressions = [
        (r"(?ms)^([ \t]*)(`{3,}|~{3,})[^\n]*\n.*?^[ \t]*\2[ \t]*(?:\n|$)", "fenced code"),
        (r"`+[^`\n]+`+", "inline code"),
        (r"https?://[^\s<>\"“”‘’（）()，。；：？！、]+", "URL"),
        (r"(?<![A-Za-z0-9_])[vV]?\d+(?:\.\d+)+(?![A-Za-z0-9_])", "decimal or version"),
        (r"(?<![A-Za-z0-9_])[A-Za-z][A-Za-z0-9]*(?:[-/][A-Za-z0-9]+)+(?![A-Za-z0-9_])", "technical identifier"),
    ]
    for pattern, reason in expressions:
        for match in re.finditer(pattern, text):
            spans.append({"start": match.start(), "end": match.end(), "reason": reason, "automatic": True})
    # Whole-line JSON is unambiguous enough to protect after actual JSON parsing.
    start = 0
    for line in text.splitlines(keepends=True):
        stripped = line.strip()
        if stripped.startswith(("{", "[")):
            try:
                parsed = json.loads(stripped)
            except (json.JSONDecodeError, ValueError):
                pass
            else:
                if isinstance(parsed, (dict, list)):
                    spans.append({"start": start, "end": start + len(line), "reason": "JSON line", "automatic": True})
        start += len(line)
    return sorted(spans, key=lambda span: (span["start"], span["end"]))


def explicit_protection(units, protected):
    if protected is None:
        return {}
    require(isinstance(protected, dict) and protected.get("schema_version") == 1, "protected schema_version must be 1")
    require(isinstance(protected.get("units"), list), "protected units required")
    by_id, result = {unit["unit_id"]: unit for unit in units}, {}
    for entry in protected["units"]:
        require(isinstance(entry, dict), "protected unit must be an object")
        uid = entry.get("unit_id")
        require(uid in by_id and uid not in result, "unknown or duplicate protected unit")
        unit = by_id[uid]
        require(entry.get("source_sha256") == unit["source_sha256"], "stale protected source hash")
        require(isinstance(entry.get("spans"), list), "protected spans required")
        result[uid] = []
        for span in entry["spans"]:
            require(isinstance(span, dict), "protected span must be an object")
            start, end = span.get("start"), span.get("end")
            require(type(start) is int and type(end) is int and 0 <= start < end <= len(unit["text"]), "invalid protected span")
            require(isinstance(span.get("reason"), str) and span["reason"].strip(), "protected span needs a specific reason")
            require(span.get("text") == unit["text"][start:end], "protected span text mismatch")
            require(unit["text"][:start].strip() or unit["text"][end:].strip(), "whole-unit punctuation exemption is not allowed")
            result[uid].append({"start": start, "end": end, "reason": span["reason"], "automatic": False})
        covered = bytearray(len(unit["text"]))
        for span in result[uid]:
            covered[span["start"]:span["end"]] = b"\1" * (span["end"] - span["start"])
        require(any(not covered[index] and not char.isspace() for index, char in enumerate(unit["text"])),
                "combined whole-unit punctuation exemption is not allowed")
    return result


def punctuation(unit, extra):
    text = unit["text"]
    protected = automatic_protection(text) + extra
    mask = bytearray(len(text))
    for span in protected:
        mask[span["start"]:span["end"]] = b"\1" * (span["end"] - span["start"])
    issues = []

    def add(start, end, code, message, structural=False):
        issues.append({"id": "punct-" + fingerprint([unit["unit_id"], unit["source_sha256"], start, end, code])[:24],
                       "unit_id": unit["unit_id"], "start": start, "end": end, "text": text[start:end],
                       "code": code, "message": message, "structural_review": structural,
                       **context(text, start, end)})

    # Mask only the protected characters, not a whole punctuation run that
    # happens to touch them. Otherwise one protected '-' hides adjacent '--'.
    # Spaces retain original offsets and split runs at real protection borders.
    visible = "".join(" " if mask[index] else char for index, char in enumerate(text))
    for match in re.finditer(r"[—–－-]+|[…\.]+", visible):
        value = match.group()
        if value[0] in "—–－-" and value != "——":
            add(match.start(), match.end(), "dash_form", "Use exactly two U+2014 characters: ——")
        elif value[0] in "…." and value != "……":
            add(match.start(), match.end(), "ellipsis_form", "Use …… for ellipsis and 。 for Chinese sentence ending")
    for index, char in enumerate(text):
        if mask[index]:
            continue
        if char in '「」『』"\'':
            add(index, index + 1, "quote_form", "Chinese outer quotes use “”; inner quotes use ‘’")
        elif char in ",;:!?()":
            add(index, index + 1, "ascii_punctuation", "Use the corresponding fullwidth Chinese punctuation")

    opening, closing, stack = "“‘（《〈", "”’）》〉", []
    pairs = dict(zip(closing, opening))
    for index, char in enumerate(text):
        if mask[index]:
            continue
        if char in opening:
            quotes = [entry for entry in stack if entry[0] in "“‘"]
            if char == "‘" and (not quotes or quotes[-1][0] != "“"):
                add(index, index + 1, "quote_nesting", "Inner quote requires an outer quote", True)
            if char == "“" and quotes:
                # This can be a conventional opening repeated at a new paragraph.
                add(index, index + 1, "quote_nesting", "Check nested or repeated paragraph opening against the full quotation", True)
            if char == "〈" and not any(entry[0] == "《" for entry in stack):
                add(index, index + 1, "title_nesting", "Nested title mark requires an outer title", True)
            stack.append((char, index))
        elif char in closing:
            if not stack or stack[-1][0] != pairs[char]:
                add(index, index + 1, "pair_order", "Unmatched or out-of-order closing punctuation", True)
            else:
                opened, start = stack.pop()
                if opened in "“‘" and re.search(r"\n\s*\n", text[start:index]):
                    add(start, index + 1, "cross_paragraph_quote", "Review the complete multi-paragraph quotation structure", True)
    for char, index in stack:
        add(index, index + 1, "unclosed_pair", "Review apparently unclosed punctuation in its complete context", True)
    issues.sort(key=lambda item: (item["start"], item["code"]))
    return {"unit_id": unit["unit_id"], "protected_spans": protected, "issues": issues,
            "requires_llm_structure_review": True}


def make_statistics(units, profile, hits):
    rows = []
    for index, unit in enumerate(units):
        uid = unit["unit_id"]
        ranges = [("unit", uid, [unit], None)]
        for number, (start, end) in enumerate(paragraphs(unit["text"]), 1):
            ranges.append(("paragraph", [uid, number], [unit], (start, end)))
        window = units[max(0, index - 2):index + 1]
        ranges.append(("rolling3", [item["unit_id"] for item in window], window, None))
        for kind, scope, selected, span in ranges:
            selected_ids = {item["unit_id"] for item in selected}
            denominator = nonwhite(unit["text"][span[0]:span[1]]) if span else sum(item["nonwhite_characters"] for item in selected)
            complete = kind == "unit" and unit["complete_chapter"]
            for category in profile["categories"]:
                matching = [hit for hit in hits if hit["category_id"] == category["id"] and hit["unit_id"] in selected_ids
                            and (span is None or span[0] <= hit["start"] < span[1])]
                count = len(matching)
                # Keep explicit zero chapter totals, but do not bury the review
                # in thousands of empty paragraph/window rows.
                if count == 0 and kind != "unit":
                    continue
                rate = 10000 * count / denominator if denominator else 0
                thresholds, triggers = category.get("thresholds", {}), []
                if complete:
                    if "chapter_at_least" in thresholds and count >= thresholds["chapter_at_least"]:
                        triggers.append("chapter_at_least")
                    if "chapter_more_than" in thresholds and count > thresholds["chapter_more_than"]:
                        triggers.append("chapter_more_than")
                if kind in {"unit", "rolling3"} and "per_10000_more_than" in thresholds and rate > thresholds["per_10000_more_than"]:
                    triggers.append("per_10000_more_than")
                if kind == "paragraph" and "paragraph_at_least" in thresholds and count >= thresholds["paragraph_at_least"]:
                    triggers.append("paragraph_at_least")
                rows.append({"id": "density-" + fingerprint([kind, scope, category["id"]])[:24], "scope_kind": kind,
                             "scope": scope, "category_id": category["id"], "count": count,
                             "nonwhite_characters": denominator, "per_10000": round(rate, 6),
                             "complete_chapter": complete, "occurrence_ids": [hit["id"] for hit in matching], "triggers": triggers})
    return rows


def scan(root, manifest, profile=None, protected=None):
    profile = validate_profile(default_profile() if profile is None else profile)
    units = load_units(root, manifest)
    explicit = explicit_protection(units, protected)
    hits, raw_counts, punctuation_reports = [], [], []
    for unit in units:
        for category in profile["categories"]:
            found, raw = find_occurrences(unit, category)
            hits.extend(found)
            raw_counts.append({"unit_id": unit["unit_id"], "category_id": category["id"],
                               "raw_form_matches": len(raw), "deduplicated_occurrences": len(found), "raw_matches": raw})
        punctuation_reports.append(punctuation(unit, explicit.get(unit["unit_id"], [])))
    rows = make_statistics(units, profile, hits)
    report = {"schema_version": 1, "kind": "language_scan", "status": "NEEDS_VERIFICATION",
              "manifest": manifest, "profile": profile, "profile_sha256": fingerprint(profile),
              "protected_sha256": fingerprint(protected),
              "units": [{key: value for key, value in unit.items() if key != "text"} for unit in units],
              "raw_counts": raw_counts, "occurrences": hits, "statistics": rows, "punctuation": punctuation_reports,
              "limits": ["No word-sense or quality inference; LLM classification and aggregate review required.",
                         "Rates describe supplied text; chapter thresholds are not applied to fragments.",
                         "Punctuation protection does not remove text from frequency denominators or matches."]}
    report["scan_id"] = fingerprint(report)
    report["review_template"] = {
        "schema_version": 1, "scan_id": report["scan_id"], "profile_sha256": report["profile_sha256"],
        "classifications": [{"id": hit["id"], "applies": None, "reason": "", "action": "unresolved"} for hit in hits],
        "unit_reviews": [{"unit_id": unit["unit_id"], "density_reviewed": False, "punctuation_reviewed": False,
                          "reason": "", "new_patterns": []} for unit in units],
        "density_reviews": [{"id": row["id"], "decision": "unresolved", "reason": "", "occurrence_ids": row["occurrence_ids"]}
                            for row in rows if row["triggers"]],
        "punctuation_reviews": [{"id": issue["id"], "decision": "unresolved", "reason": ""}
                                for result in punctuation_reports for issue in result["issues"]],
    }
    return report


def keyed(items, field, expected, label, complete=True):
    require(isinstance(items, list), label + " must be a list")
    result = {}
    for item in items:
        require(isinstance(item, dict), label + " item must be an object")
        key = item.get(field)
        require(key in expected and key not in result, label + " has unknown or duplicate id")
        result[key] = item
    if complete:
        require(set(result) == set(expected), label + " is incomplete")
    return result


def recount(root, old_scan, decisions, profile=None, protected=None):
    require(isinstance(old_scan, dict) and old_scan.get("kind") == "language_scan", "expected language_scan report")
    fresh = scan(root, old_scan.get("manifest"), profile, protected)
    require(old_scan == fresh, "stale or modified scan: source, profile, protection or report changed; scan again")
    require(isinstance(decisions, dict) and decisions.get("schema_version") == 1, "decisions schema_version must be 1")
    require(decisions.get("scan_id") == fresh["scan_id"], "decisions refer to a different scan")
    require(decisions.get("profile_sha256") == fresh["profile_sha256"], "decisions profile hash mismatch")
    by_id = {hit["id"]: hit for hit in fresh["occurrences"]}
    labels = keyed(decisions.get("classifications"), "id", by_id, "classifications")
    semantic, unresolved = [], []
    for key, label in labels.items():
        require(type(label.get("applies")) is bool, "classification applies must be boolean")
        require(isinstance(label.get("reason"), str) and label["reason"].strip(), "classification reason required")
        action = label.get("action")
        if label["applies"]:
            require(action in {"retain", "revise", "unresolved"}, "applicable use needs retain/revise/unresolved action")
            semantic.append(by_id[key])
            if action != "retain":
                unresolved.append({"kind": "occurrence", "id": key, "reason": action})
        else:
            require(action == "not_applicable", "excluded sense must use not_applicable action")
    units = load_units(root, fresh["manifest"])
    require([{key: value for key, value in unit.items() if key != "text"} for unit in units] == fresh["units"],
            "source changed during recount; scan again")
    rows = make_statistics(units, fresh["profile"], semantic)
    reviews = keyed(decisions.get("unit_reviews"), "unit_id", {unit["unit_id"] for unit in units}, "unit_reviews")
    for uid, review in reviews.items():
        require(type(review.get("density_reviewed")) is bool and type(review.get("punctuation_reviewed")) is bool,
                "unit review flags must be boolean")
        require(isinstance(review.get("new_patterns"), list), "new_patterns must be a list")
        require(isinstance(review.get("reason"), str), "unit review reason must be text")
        if not review["density_reviewed"] or not review["punctuation_reviewed"] or not review["reason"].strip() or review["new_patterns"]:
            unresolved.append({"kind": "unit_review", "id": uid,
                               "reason": "review incomplete or new patterns need addition to a calibrated profile and rescan"})
    row_ids = {row["id"] for row in fresh["statistics"]} | {row["id"] for row in rows}
    densities = keyed(decisions.get("density_reviews"), "id", row_ids, "density_reviews", complete=False)
    outcomes = []
    for row in rows:
        if not row["triggers"]:
            continue
        review = densities.get(row["id"], {})
        # Template rows may shrink after semantic filtering, but retention must
        # name exactly the remaining applicable occurrences, not an entire class.
        covered = review.get("occurrence_ids", [])
        retained = (review.get("decision") == "retain" and isinstance(review.get("reason"), str)
                    and bool(review["reason"].strip()) and isinstance(covered, list)
                    and len(covered) == len(set(covered)) and set(covered) == set(row["occurrence_ids"]))
        outcome = {"id": row["id"], "outcome": "有据保留" if retained else "未解决",
                   "reason": review.get("reason", "missing density review")}
        outcomes.append(outcome)
        if not retained:
            unresolved.append({"kind": "density", **outcome})
    issue_by_id = {issue["id"]: issue for item in fresh["punctuation"] for issue in item["issues"]}
    punctuation_reviews = keyed(decisions.get("punctuation_reviews"), "id", issue_by_id, "punctuation_reviews")
    for key, issue in issue_by_id.items():
        review = punctuation_reviews[key]
        if not (issue["structural_review"] and review.get("decision") == "valid_structure"
                and isinstance(review.get("reason"), str) and review["reason"].strip()):
            unresolved.append({"kind": "punctuation", "id": key, "reason": "fix glyph errors or supply an exact protected span; validate structures in context"})
    return {"schema_version": 1, "kind": "language_recount", "scan_id": fresh["scan_id"],
            "profile_sha256": fresh["profile_sha256"], "status": "NEEDS_VERIFICATION" if unresolved else "PASS",
            "frequency_outcome": "未解决" if any(item["kind"] in {"occurrence", "unit_review", "density"} for item in unresolved)
                                 else ("有据保留" if outcomes else "达标"),
            "raw_counts": fresh["raw_counts"], "semantic_statistics": rows, "density_outcomes": outcomes,
            "unresolved": unresolved, "units": fresh["units"],
            "limits": ["PASS covers this language review only; semantic regression, reader review and project acceptance remain separate.",
                       "LLM judgments are recorded assertions, not mechanically proven word senses or literary quality."]}


def output_json(result, output=None):
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if output:
        target = Path(output)
        # Review artifacts must not silently overwrite any existing input file.
        with target.open("x", encoding="utf-8") as stream:
            stream.write(rendered)
    else:
        print(rendered, end="")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("scan", "recount"):
        command = commands.add_parser(name)
        command.add_argument("--project-root", required=True)
        command.add_argument("--profile", help="explicit calibrated profile; omitted uses generic defaults")
        command.add_argument("--protected", help="hash-bound punctuation exception spans")
        command.add_argument("--output", help="new JSON artifact; existing files are never overwritten")
        if name == "scan":
            command.add_argument("--manifest", required=True)
        else:
            command.add_argument("--scan", required=True)
            command.add_argument("--classifications", required=True)
    args = parser.parse_args(argv)
    try:
        profile = read_json(args.profile) if args.profile else None
        protected = read_json(args.protected) if args.protected else None
        if args.command == "scan":
            result = scan(args.project_root, read_json(args.manifest), profile, protected)
        else:
            result = recount(args.project_root, read_json(args.scan), read_json(args.classifications), profile, protected)
        output_json(result, args.output)
        return 3 if args.command == "recount" and result["status"] != "PASS" else 0
    except (ValidationError, OSError, ValueError, KeyError, TypeError) as exc:
        print("language review error: " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
