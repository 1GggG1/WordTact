"""Materialize paired Chinese-fiction style trials without evaluator-only criteria."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


FIXTURE = Path(__file__).parent / "fixtures/style_consistency/inputs.json"


def materialize(output: Path, context: str) -> dict[str, str]:
    if context not in {"plain", "guided"}:
        raise ValueError("context must be plain or guided")
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    files = {"request.txt": data["request"] + "\n"}
    for case in data["cases"]:
        prefix = f"cases/{case['id']}"
        files[f"{prefix}/request.txt"] = case["request"] + "\n"
        files[f"{prefix}/context.md"] = case["context"] + "\n"
        if case["mode"] == "audit":
            files[f"{prefix}/prose.md"] = case["prose"] + "\n"
        for name, content in case.get("sources", {}).items():
            files[f"{prefix}/{name}"] = content + "\n"
        if context == "guided" and case.get("guidance"):
            files[f"{prefix}/style.md"] = case["guidance"] + "\n"
        if case.get("stale_sample"):
            sample = case["stale_sample"]
            files[f"{prefix}/sample-record.json"] = json.dumps({
                "path": sample["path"],
                "sha256": hashlib.sha256((sample["approved_text"] + "\n").encode()).hexdigest(),
                "status": "approved version at previous audit",
            }, ensure_ascii=False, indent=2) + "\n"
    # Validate all paths before making the output directory or writing any inputs.
    root = output.resolve()
    if any(not (root / name).resolve().is_relative_to(root) for name in files):
        raise ValueError("input path escapes trial root")
    output.mkdir(parents=True, exist_ok=False)
    hashes = {}
    for name, content in files.items():
        path = output / name
        path.parent.mkdir(parents=True, exist_ok=True)
        raw = content.encode("utf-8")
        path.write_bytes(raw)
        hashes[name] = hashlib.sha256(raw).hexdigest()
    (output / "input-hashes.json").write_text(
        json.dumps(hashes, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return hashes


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--context", required=True, choices=("plain", "guided"))
    args = parser.parse_args()
    print(f"Materialized {len(materialize(args.output, args.context))} inputs in {args.output}")
