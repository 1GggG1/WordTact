#!/usr/bin/env python3
"""Build the general release containing WordTact, its installer and conversation skill."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import stat
import tempfile
import zipfile


ROOT = Path(__file__).resolve().parents[1]
PREFIX = "wordtact-general"


def load_installer(root: Path):
    installer = root / "install.py"
    spec = importlib.util.spec_from_file_location("wordtact_installer", installer)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sync_conversation(root: Path = ROOT) -> None:
    module = load_installer(root)
    content = (root / "conversational-register/SKILL.md").read_bytes()
    (root / "wordtact/references/conversation.md").write_bytes(module.conversation_body(content))


def release_files(root: Path = ROOT) -> dict[str, bytes]:
    module = load_installer(root)
    result = {f"{name}/{relative}": data
              for name, content in module.payloads(root).items()
              for relative, data in content.items()}
    result["install.py"] = (root / "install.py").read_bytes()
    result["INSTALL.md"] = (root / "INSTALL.md").read_bytes()
    manifest = {relative: hashlib.sha256(data).hexdigest() for relative, data in sorted(result.items())}
    result["manifest.json"] = (json.dumps(manifest, indent=2) + "\n").encode("utf-8")
    return result


def build(output: Path, root: Path = ROOT) -> dict:
    output = output.expanduser().resolve()
    if output == root.resolve() or root.resolve() in output.parents:
        raise ValueError("write the release outside general/ to keep generated files out of source")
    contents = release_files(root)
    output.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=".wordtact-release-", suffix=".zip", dir=output.parent)
    os.close(fd)
    try:
        with zipfile.ZipFile(temporary, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for relative, data in sorted(contents.items()):
                info = zipfile.ZipInfo(f"{PREFIX}/{relative}", (1980, 1, 1, 0, 0, 0))
                info.create_system = 3
                info.external_attr = (stat.S_IFREG | 0o644) << 16
                info.compress_type = zipfile.ZIP_DEFLATED
                archive.writestr(info, data)
        os.replace(temporary, output)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    return {"path": str(output), "files": len(contents), "sha256": hashlib.sha256(output.read_bytes()).hexdigest()}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--sync-conversation", action="store_true", help="refresh WordTact's fallback from the canonical conversation skill before building")
    args = parser.parse_args()
    try:
        if args.sync_conversation:
            sync_conversation()
        print(json.dumps(build(args.output), indent=2))
    except (OSError, ValueError) as error:
        parser.exit(1, f"Build stopped: {error}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
