#!/usr/bin/env python3
"""Preview or refresh project-configured active/archive relationship blocks."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from tagging_common import (
    ConfigError,
    Context,
    add_common_arguments,
    diagnostic_proposal,
    dump_markdown,
    iter_files,
    load_context,
    print_summary,
    read_markdown,
    relative,
    semantic_tags,
    version_family,
    write_if_apply,
)


BLOCK_START = "<!-- AUTO-ARCHIVE-LINKS:START -->"
BLOCK_END = "<!-- AUTO-ARCHIVE-LINKS:END -->"


@dataclass
class Note:
    path: Path
    frontmatter: dict[str, Any]
    body: str
    tags: dict[str, list[str]]

    @property
    def title(self) -> str:
        return str(self.frontmatter.get("title") or self.path.stem)

    @property
    def family(self) -> str:
        return str(self.frontmatter.get("version_family") or version_family(self.path)).casefold()

    @property
    def chapters(self) -> set[str]:
        value = self.frontmatter.get("chapters") or []
        if isinstance(value, str):
            value = [value]
        return {str(item) for item in value}

    @property
    def doc_type(self) -> str:
        return str(self.frontmatter.get("doc_type") or "")


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    add_common_arguments(result)
    return result


def load_notes(context: Context, fields: tuple[str, ...]) -> list[Note]:
    notes: list[Note] = []
    for path in iter_files(context, fields, {".md"}):
        frontmatter, body = read_markdown(path)
        notes.append(Note(path, frontmatter, body, semantic_tags(frontmatter)))
    return notes


def wiki_link(note: Note, context: Context, label: str | None = None) -> str:
    target = relative(note.path, context.root)
    if target.endswith(".md"):
        target = target[:-3]
    return f"[[{target}|{label or note.title}]]"


def similarity(left: Note, right: Note) -> int:
    score = 0
    if left.family and left.family == right.family:
        score += 8
    elif left.family and right.family and (left.family in right.family or right.family in left.family):
        score += 4
    if left.chapters and right.chapters and left.chapters & right.chapters:
        score += 6
    if left.doc_type and left.doc_type == right.doc_type:
        score += 2
    overlap = 0
    for category in left.tags:
        overlap += len(set(left.tags[category]) & set(right.tags[category]))
    score += min(overlap, 5)
    return score


def title_for(note: Note, context: Context) -> str:
    archive = context.config.get("archive") or {}
    overrides = archive.get("title_overrides") or {}
    if not isinstance(overrides, dict):
        raise ConfigError("archive.title_overrides must be a mapping")
    return str(overrides.get(relative(note.path, context.root)) or note.title)


def preferred_rank(note: Note, context: Context) -> int:
    archive = context.config.get("archive") or {}
    preferred = archive.get("preferred_paths") or []
    if not isinstance(preferred, list) or not all(isinstance(item, str) for item in preferred):
        raise ConfigError("archive.preferred_paths must be a list")
    rel = relative(note.path, context.root)
    try:
        return len(preferred) - preferred.index(rel)
    except ValueError:
        return 0


def best_matches(note: Note, candidates: list[Note], context: Context, limit: int = 5) -> list[Note]:
    ranked = [
        (similarity(note, candidate), preferred_rank(candidate, context), relative(candidate.path, context.root), candidate)
        for candidate in candidates
        if candidate.path != note.path
    ]
    ranked = [item for item in ranked if item[0] >= 7]
    ranked.sort(key=lambda item: (-item[0], -item[1], item[2]))
    return [item[3] for item in ranked[:limit]]


def strip_block(body: str) -> str:
    pattern = re.compile(
        r"\n*## (?:Archive relationships|Current relationships)\n"
        + re.escape(BLOCK_START)
        + r"\n.*?\n"
        + re.escape(BLOCK_END)
        + r"\n*",
        re.DOTALL,
    )
    return pattern.sub("\n\n", body).rstrip()


def attach_block(body: str, heading: str, lines: list[str]) -> str:
    clean = strip_block(body)
    if not lines:
        return f"{clean}\n" if clean else ""
    block = "\n".join([f"## {heading}", BLOCK_START, *lines, BLOCK_END])
    return f"{clean}\n\n{block}\n" if clean else f"{block}\n"


def archive_tags(existing: Any, note: Note) -> list[str]:
    values = [existing] if isinstance(existing, str) else list(existing or [])
    preserved = [item for item in values if isinstance(item, str) and not item.startswith("archive")]
    status = str(note.frontmatter.get("status") or "reference").casefold().replace(" ", "-")
    return list(dict.fromkeys([*preserved, "archive", f"archive/{status}"]))


def planned_write(context: Context, note: Note, content: str, changes: list[dict[str, Any]]) -> None:
    old = note.path.read_text(encoding="utf-8", errors="ignore")
    if old == content:
        return
    changes.append({"action": "update", "path": relative(note.path, context.root)})
    write_if_apply(context, note.path, content)


def run(context: Context) -> None:
    active = load_notes(context, ("active_dirs", "skill_dirs"))
    archived = load_notes(context, ("archive_dirs",))
    changes: list[dict[str, Any]] = []
    weak_candidates: list[dict[str, Any]] = []

    for note in active:
        matches = best_matches(note, archived, context)
        lines = [f"- {wiki_link(item, context, title_for(item, context))}" for item in matches]
        body = attach_block(note.body, "Archive relationships", lines)
        planned_write(context, note, dump_markdown(note.frontmatter, body), changes)

    for note in archived:
        current = best_matches(note, active, context)
        family = [
            item
            for item in archived
            if item.path != note.path and item.family and item.family == note.family
        ][:4]
        lines = [f"- Current: {wiki_link(item, context, title_for(item, context))}" for item in current]
        lines.extend(f"- Same family: {wiki_link(item, context, title_for(item, context))}" for item in family)
        body = attach_block(note.body, "Current relationships", list(dict.fromkeys(lines)))
        frontmatter = dict(note.frontmatter)
        frontmatter["tags"] = archive_tags(frontmatter.get("tags"), note)
        planned_write(context, note, dump_markdown(frontmatter, body), changes)

        if not current:
            scored = sorted(
                ((similarity(note, item), relative(item.path, context.root)) for item in active),
                reverse=True,
            )[:3]
            if scored and scored[0][0] > 0:
                weak_candidates.append(
                    {"archive": relative(note.path, context.root), "candidates": scored}
                )

    print_summary(
        "refresh-archive-graph",
        context,
        changes,
        active_notes=len(active),
        archive_notes=len(archived),
        weak_candidates=weak_candidates,
    )


def main() -> int:
    args = parser().parse_args()
    try:
        context, config_path = load_context(args)
        if context is None:
            root = Path(args.project_root).expanduser().resolve()
            if args.apply:
                raise ConfigError(f"refusing apply without confirmed config: {config_path}")
            print(f"project_root={root}")
            print(f"config_missing={config_path}")
            print("configuration_proposal:")
            print(diagnostic_proposal(root), end="")
            return 0
        run(context)
        return 0
    except (ConfigError, OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
