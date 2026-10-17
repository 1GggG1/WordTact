"""Materialize neutral inputs for evidence-boundary agent trials, without answer keys."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


FIXTURE = Path(__file__).parent / "fixtures/evidence_boundary/inputs.json"


def materialize(output: Path, context: str) -> dict[str, str]:
    if context not in {"brief", "expanded"}:
        raise ValueError("context must be brief or expanded")
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    output.mkdir(parents=True, exist_ok=False)
    files = {
        "audit-request.txt": data["audit_request"] + "\n",
        "writing-request.txt": data["writing_request"] + "\n",
    }
    for case in data["audit_cases"]:
        prefix = f"audits/{case['id']}"
        files[f"{prefix}/prose.md"] = case["prose"]
        files[f"{prefix}/context.md"] = (
            "# 本篇叙事约定\n\n" + case["contract"]
            + "\n\n# 项目资料\n\n" + case[f"{context}_context"] + "\n"
        )
    for case in data["writing_cases"]:
        files[f"writers/{case['id']}/brief.md"] = case["brief"] + "\n"
    hashes = {}
    for relative, text in files.items():
        path = output / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        content = text.encode("utf-8")
        path.write_bytes(content)
        hashes[relative] = hashlib.sha256(content).hexdigest()
    (output / "input-hashes.json").write_text(
        json.dumps(hashes, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return hashes


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--context", required=True, choices=("brief", "expanded"))
    args = parser.parse_args()
    result = materialize(args.output, args.context)
    print(f"Materialized {len(result)} input files in {args.output}")
