#!/usr/bin/env python3
"""Install WordTact and its independent conversation skill from this local bundle."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import tempfile
from datetime import datetime, timezone
from uuid import uuid4


ROOT = Path(__file__).resolve().parent
SKILLS = ("wordtact", "conversational-register")
IGNORED = {
    "__pycache__", ".DS_Store", ".AppleDouble", ".LSOverride", "__MACOSX",
    ".Spotlight-V100", ".Trashes", ".fseventsd", ".TemporaryItems",
    ".DocumentRevisions-V100", ".VolumeIcon.icns",
    ".com.apple.timemachine.donotpresent",
}


def files(root: Path) -> dict[str, bytes]:
    """Read a skill tree without internal links, caches or macOS metadata."""
    result = {}
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        if (any(part in IGNORED or part.startswith("._") for part in relative.parts)
                or path.suffix.lower() in {".pyc", ".pyo", ".pyd", ".plist"}):
            continue
        if path.is_symlink():
            raise ValueError(f"unexpected link inside skill: {path}")
        if path.is_file():
            result[relative.as_posix()] = path.read_bytes()
    return result


def conversation_body(content: bytes) -> bytes:
    text = content.decode("utf-8")
    metadata = re.match(r"\A---\n(.*?)\n---(?:\n|$)", text, re.DOTALL)
    if metadata is None or not re.search(r"(?m)^name: conversational-register$", metadata.group(1)):
        raise ValueError("conversation payload must contain conversational-register frontmatter")
    return text[metadata.end():].lstrip().encode("utf-8")


def payloads(root: Path = ROOT) -> dict[str, dict[str, bytes]]:
    editing = files(root / "wordtact")
    conversation = files(root / "conversational-register")
    if "SKILL.md" not in conversation or "LICENSE" not in conversation:
        raise ValueError("conversational-register SKILL.md and LICENSE must be included")
    body = conversation_body(conversation["SKILL.md"])
    if editing.get("references/conversation.md") != body:
        raise ValueError("WordTact conversation fallback is stale; run the general builder with --sync-conversation")
    if "SKILL.md" not in editing or "LICENSE" not in editing:
        raise ValueError("WordTact SKILL.md and LICENSE must be included")
    metadata = re.match(r"\A---\n(.*?)\n---(?:\n|$)", editing["SKILL.md"].decode("utf-8"), re.DOTALL)
    if metadata is None or not re.search(r"(?m)^name: wordtact$", metadata.group(1)):
        raise ValueError("WordTact entrypoint has the wrong skill name")
    return {
        "wordtact": editing,
        "conversational-register": conversation,
    }


def fingerprint(contents: dict[str, bytes]) -> dict[str, str]:
    return {name: hashlib.sha256(data).hexdigest() for name, data in contents.items()}


def install(destination: Path, selected=SKILLS, *, replace=False, dry_run=False,
            backup_dir: Path | None = None, root: Path = ROOT) -> dict:
    destination = destination.expanduser().resolve()
    root = root.resolve()
    selected = tuple(dict.fromkeys(selected))
    if not selected or any(name not in SKILLS for name in selected):
        raise ValueError("select wordtact, conversational-register, or both")
    sources = payloads(root)
    plans = []
    for name in selected:
        target = destination / name
        if root in target.parents or target == root or target in root.parents:
            raise ValueError(f"installation would overlap its source: {target}")
        before = files(target) if target.is_dir() else None
        if before == sources[name]:
            action = "unchanged"
        elif target.is_symlink():
            raise ValueError(f"different existing symlink: {target}; install into its real skill location instead")
        elif target.exists() and not target.is_dir():
            raise ValueError(f"skill target is not a directory: {target}")
        elif target.exists():
            if not replace:
                raise ValueError(f"different existing skill: {target}; use --replace to back it up and update it")
            action = "replace"
        else:
            action = "create"
        plans.append({"name": name, "path": str(target), "action": action,
                      "before": fingerprint(before) if before is not None else None,
                      "after": fingerprint(sources[name])})
    report = {"destination": str(destination), "dry_run": dry_run, "skills": plans, "backup": None}
    if dry_run or all(plan["action"] == "unchanged" for plan in plans):
        return report

    backup_root = (backup_dir or Path.home() / ".local/state/wordtact/backups").expanduser().resolve()
    if any(plan["action"] == "replace" for plan in plans):
        if backup_root == destination or destination in backup_root.parents or backup_root == root or root in backup_root.parents:
            raise ValueError("backups must be outside the source and destination skill trees")
        backup = backup_root / (datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid4().hex[:8])
        backup.mkdir(parents=True)
        for plan in plans:
            if plan["action"] == "replace":
                shutil.copytree(Path(plan["path"]), backup / plan["name"])
                if fingerprint(files(backup / plan["name"])) != plan["before"]:
                    raise ValueError(f"target changed while backing up: {plan['path']}")
        (backup / "installation.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        report["backup"] = str(backup)

    destination.mkdir(parents=True, exist_ok=True)
    moved = []
    written = []
    with tempfile.TemporaryDirectory(prefix=".wordtact-install-", dir=destination.parent) as temporary:
        stage = Path(temporary)
        for plan in plans:
            if plan["action"] == "unchanged":
                continue
            new = stage / "new" / plan["name"]
            for relative, data in sources[plan["name"]].items():
                path = new / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(data)
        try:
            for plan in plans:
                if plan["action"] == "unchanged":
                    continue
                target = Path(plan["path"])
                current = fingerprint(files(target)) if target.is_dir() else None
                if target.is_symlink() or current != plan["before"] or (target.exists() and not target.is_dir()):
                    raise ValueError(f"target changed during installation: {target}")
                if target.exists():
                    old = stage / "old" / plan["name"]
                    old.parent.mkdir(parents=True, exist_ok=True)
                    os.replace(target, old)
                    moved.append((target, old))
                os.replace(stage / "new" / plan["name"], target)
                written.append((target, plan["after"]))
                if fingerprint(files(target)) != plan["after"]:
                    raise OSError(f"installed content mismatch: {target}")
        except BaseException:
            # Restore only our own output; do not overwrite an unrelated concurrent edit.
            for target, expected in reversed(written):
                if not target.is_symlink() and target.is_dir() and fingerprint(files(target)) == expected:
                    shutil.rmtree(target)
            for target, old in reversed(moved):
                if not target.exists() and not target.is_symlink():
                    os.replace(old, target)
            raise
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dest", type=Path, required=True, help="the selected client's skill directory")
    parser.add_argument("--only", choices=SKILLS, help="install only one skill; default installs both")
    parser.add_argument("--dry-run", action="store_true", help="show the plan without filesystem changes")
    parser.add_argument("--replace", action="store_true", help="back up and update different existing regular directories")
    parser.add_argument("--backup-dir", type=Path, help="backup parent, outside skill trees")
    args = parser.parse_args()
    try:
        result = install(args.dest, (args.only,) if args.only else SKILLS,
                         replace=args.replace, dry_run=args.dry_run, backup_dir=args.backup_dir)
    except (OSError, ValueError) as error:
        parser.exit(1, f"Installation stopped: {error}\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
