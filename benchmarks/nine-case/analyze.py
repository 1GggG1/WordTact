#!/usr/bin/env python3
"""Recompute diagnostic summaries from the public, anonymized evaluation evidence."""
from __future__ import annotations

import argparse
import json
import statistics
from collections import Counter, defaultdict
from pathlib import Path

DIMENSIONS = ("naturalness", "voice", "craft", "economy")
FIDELITY_ORDER = {"pass": 0, "minor": 1, "major": 2}


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def analyze(records: list[dict], judgments: list[dict], mapping: dict, pairs: dict) -> dict:
    """Do not combine dimensions into an overall score or count repeats as new cases."""
    ratings = {}
    bad_quotes = []
    for evaluation in judgments:
        payload = evaluation["input"]
        candidates = {c["id"]: c for c in payload["candidates"]}
        task_text = "\n".join(payload["task"][k] for k in ("request", "context", "source"))
        for row in evaluation["judgment"]["candidates"]:
            ratings[evaluation["case_id"], evaluation["order"], row["id"]] = row
            for issue in row["issues"]:
                valid_candidate = issue["candidate_quote"] in candidates[row["id"]]["text"]
                valid_source = bool(issue["source_quote"]) and issue["source_quote"] in task_text
                if not valid_candidate or not valid_source:
                    bad_quotes.append({"case_id": evaluation["case_id"], "order": evaluation["order"],
                                       "candidate_id": row["id"], "issue": issue,
                                       "candidate_quote_found": valid_candidate,
                                       "source_quote_found": valid_source})
    groups = defaultdict(list)
    sample_ratings = []
    for record in records:
        cid = record["case_id"]
        candidate_id = mapping[cid]["keys"][record["key"]]
        ordered = [ratings[cid, order, candidate_id] for order in ("forward", "reverse")]
        row = {"key": record["key"], "case_id": cid, "model": record["model"],
               "method": record["method"], "candidate_id": candidate_id,
               **{d: statistics.mean(v[d] for v in ordered) for d in DIMENSIONS},
               "fidelity_by_order": [v["fidelity"] for v in ordered],
               "worst_fidelity": max((v["fidelity"] for v in ordered), key=FIDELITY_ORDER.get),
               "both_fidelity_pass": all(v["fidelity"] == "pass" for v in ordered),
               "hard_failures": record["checks"]["hard_failures"]}
        sample_ratings.append(row)
        # Keep drafting apart from revision so Humanizer is never compared on fewer cases.
        scope = "fiction_draft" if cid == "F01" else "fiction_edit" if cid.startswith("F") else "general"
        groups[record["model"] + "|" + scope + "|" + record["method"]].append((row, record))
    summaries = {}
    for key, members in groups.items():
        rows, raw = zip(*members)
        summaries[key] = {
            "generations": len(rows), "distinct_cases": len({r["case_id"] for r in rows}),
            "mean_quality": {d: round(statistics.mean(r[d] for r in rows), 3) for d in DIMENSIONS},
            "both_fidelity_pass": sum(r["both_fidelity_pass"] for r in rows),
            "worst_fidelity_counts": dict(Counter(r["worst_fidelity"] for r in rows)),
            "fidelity_order_disagreements": sum(r["fidelity_by_order"][0] != r["fidelity_by_order"][1] for r in rows),
            "hard_failure_generations": sum(bool(r["hard_failures"]) for r in rows),
            "median_wall_seconds": round(statistics.median(r["elapsed_seconds"] for r in raw), 3),
            "min_wall_seconds": min(r["elapsed_seconds"] for r in raw),
            "max_wall_seconds": max(r["elapsed_seconds"] for r in raw),
            "tokens": {k: sum(r.get("usage", {}).get(k, 0) for r in raw)
                       for k in ("input_tokens", "cached_input_tokens", "output_tokens", "reasoning_output_tokens")},
        }
    per_case = {}
    for pair in pairs.values():
        key = "|".join((pair["model"], pair["case_id"], pair["control"]))
        counts = per_case.setdefault(key, {f: {"win": 0, "tie": 0, "loss": 0, "order_disagreements": 0}
                                           for f in ("language_quality", "usable_overall")})
        for field in counts:
            counts[field][pair[field]] += 1
            counts[field]["order_disagreements"] += (
                pair["orders"]["forward"][field] != pair["orders"]["reverse"][field])
    return {"groups": summaries, "sample_ratings": sample_ratings,
            "per_case_pairs": per_case, "quote_audit_flags": bad_quotes,
            "notes": ["Quality dimensions are not combined into a composite score.",
                      "Worst fidelity is a conservative union of two model judgments, not verified ground truth.",
                      "An unfound quote is an audit flag, not an automatic reversal of the judgment.",
                      "Wall time includes tools and host overhead and is not pure model latency."]}


def quote_preview(text: str) -> str:
    """Keep Markdown hard breaks and fenced content in readable blockquote previews."""
    lines = []
    fence = None
    for line in text.splitlines():
        marker = next((m for m in ("```", "~~~") if line.lstrip().startswith(m)), None)
        if marker and fence is None:
            fence = marker
        elif marker == fence:
            fence = None
        if not fence and not marker:
            if not line.strip():
                line = ""
            elif line.endswith("  "):
                line = line.rstrip() + "\\"
        lines.append("> " + line if line else ">")
    return "\n".join(lines)


def write_case_reports(destination: Path, records: list[dict], judgments: list[dict], metrics: dict) -> None:
    """Readable previews always use repetition 1, never a score-selected candidate."""
    target = destination / "cases"
    target.mkdir(parents=True, exist_ok=True)
    tasks = {j["case_id"]: j["input"]["task"] for j in judgments}
    grades = {r["key"]: r for r in metrics["sample_ratings"]}
    names = {"bare": "无本次任务 skill", "humanizer": "Humanizer", "project": "项目 skill"}
    for cid, task in sorted(tasks.items()):
        lines = [f"# {cid} · {task['title']}", "",
                 "固定展示第一轮，未经人工修订或按分数挑选。完整三轮见同目录上层的 `generations.json`。", "",
                 "## 任务", "", task["request"], "", "## 上下文", "", task["context"], ""]
        if task["source"]:
            lines.extend(["## 原文", "", quote_preview(task["source"]), ""])
        lines.extend(["## 三轮成对比较", "", "项目 skill 相对对照；数字依次为胜／平／负，顺序分歧已计为平局。", "",
                      "| 模型 | 对照 | 语言质量 | 综合可用性 |", "|---|---|---|---|"])
        for key, counts in sorted(metrics["per_case_pairs"].items()):
            model, case, control = key.split("|")
            if case != cid:
                continue
            values = ["/".join(str(counts[f][k]) for k in ("win", "tie", "loss"))
                      for f in ("language_quality", "usable_overall")]
            lines.append(f"| {model} | {names.get(control, control)} | {values[0]} | {values[1]} |")
        lines.append("")
        preview = [r for r in records if r["case_id"] == cid and r["repeat"] == 1]
        for r in sorted(preview, key=lambda x: (x["model"], ("bare", "humanizer", "project").index(x["method"]))):
            score = grades[r["key"]]
            numbers = " / ".join(str(score[d]) for d in DIMENSIONS)
            lines.extend([f"## {r['model']} · {names[r['method']]}", "",
                          f"Astra 两次评分均值（自然度／声音／组织／信息密度）：{numbers}；",
                          f"保真判断（两次）：{' / '.join(score['fidelity_by_order'])}。", "",
                          quote_preview(r["text"]), ""])
        (target / (cid + ".md")).write_text("\n".join(lines), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("results", type=Path)
    args = parser.parse_args()
    root = args.results
    records, judgments = read(root / "generations.json"), read(root / "judgments.json")
    result = analyze(records, judgments, read(root / "label-key.json"), read(root / "pairs.json"))
    (root / "metrics.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_case_reports(root, records, judgments, result)
    print(json.dumps(result["groups"], ensure_ascii=False, indent=2))
    print("Quote audit flags:", len(result["quote_audit_flags"]))


if __name__ == "__main__":
    main()
