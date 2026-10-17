#!/usr/bin/env python3
"""Build the novel source archive with a deterministic file list."""

from __future__ import annotations

import argparse
import hashlib
import os
import re
import stat
import tempfile
import zipfile
from datetime import date, datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PREFIX = "novel-superpower"
ARCHIVE_NAME_RE = re.compile(r"^novel-superpower-full-(\d{8})\.zip$")
EXCLUDED_NAMES = {
    "agent-progress.md",
    "feature-list.json",
}
EXCLUDED_PARTS = {".git", "__pycache__"}
MACOS_NAMES = {
    ".DS_Store", ".AppleDouble", ".LSOverride", "__MACOSX", ".Spotlight-V100",
    ".Trashes", ".fseventsd", ".TemporaryItems", ".DocumentRevisions-V100",
    ".VolumeIcon.icns", ".com.apple.timemachine.donotpresent",
}


def is_macos_artifact(path: Path) -> bool:
    return path.suffix.lower() == ".plist" or any(
        part in MACOS_NAMES or part.startswith("._") for part in path.parts
    )


def validate_release_date(value: str) -> str:
    if not re.fullmatch(r"\d{8}", value):
        raise argparse.ArgumentTypeError("release date must use YYYYMMDD")
    try:
        datetime.strptime(value, "%Y%m%d")
    except ValueError as exc:
        raise argparse.ArgumentTypeError("release date must be a valid YYYYMMDD date") from exc
    return value


def archive_for_date(release_date: str, root: Path = ROOT) -> Path:
    return root / f"novel-superpower-full-{validate_release_date(release_date)}.zip"


def source_archives(root: Path = ROOT) -> list[Path]:
    return sorted(
        path
        for path in root.glob("novel-superpower-full-*.zip")
        if path.is_file() and ARCHIVE_NAME_RE.fullmatch(path.name)
    )


def source_files(root: Path = ROOT) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*"):
        relative = path.relative_to(root)
        if is_macos_artifact(relative):
            continue
        if any(part in EXCLUDED_PARTS for part in relative.parts):
            continue
        if len(relative.parts) == 1 and ARCHIVE_NAME_RE.fullmatch(path.name):
            continue
        if path.name in EXCLUDED_NAMES or path.suffix in {".pyc", ".pyo", ".pyd"}:
            continue
        if path.is_symlink():
            raise ValueError(f"refusing to package symlink: {relative}")
        if path.is_file():
            files.append(path)
    return sorted(files, key=lambda item: item.relative_to(root).as_posix())


def build(archive: Path, root: Path = ROOT) -> tuple[int, str]:
    root = root.resolve()
    archive = archive.resolve()
    if root in archive.parents and not (
        archive.parent == root and ARCHIVE_NAME_RE.fullmatch(archive.name)
    ):
        raise ValueError(
            "output inside the source tree must be a root dated release archive; "
            "use --output outside the repository to prevent archive self-inclusion"
        )
    files = source_files(root)
    archive.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix="novel-superpower.", suffix=".zip", dir=archive.parent
    )
    os.close(descriptor)
    temporary = Path(temporary_name)
    try:
        with zipfile.ZipFile(
            temporary,
            mode="w",
            compression=zipfile.ZIP_DEFLATED,
            compresslevel=9,
        ) as package:
            for path in files:
                relative = path.relative_to(root).as_posix()
                info = zipfile.ZipInfo(f"{PREFIX}/{relative}", date_time=(1980, 1, 1, 0, 0, 0))
                mode = stat.S_IMODE(path.stat().st_mode)
                info.external_attr = (stat.S_IFREG | mode) << 16
                info.compress_type = zipfile.ZIP_DEFLATED
                info.create_system = 3
                package.writestr(info, path.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
        os.replace(temporary, archive)
    finally:
        if temporary.exists():
            temporary.unlink()

    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    return len(files), digest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--date",
        dest="release_date",
        default=date.today().strftime("%Y%m%d"),
        type=validate_release_date,
        help="release date in YYYYMMDD form (default: today)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="explicit archive path; use a path outside the repository (does not remove old releases)",
    )
    parser.add_argument(
        "--replace-existing",
        action="store_true",
        help="remove other dated release archives after the new archive is built successfully",
    )
    args = parser.parse_args()

    if args.output is not None and args.replace_existing:
        parser.error("--output cannot be combined with --replace-existing; explicit output preserves old releases")
    archive = args.output.resolve() if args.output is not None else archive_for_date(args.release_date)
    try:
        count, digest = build(archive)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    removed: list[str] = []
    if args.replace_existing:
        for existing in source_archives():
            if existing != archive:
                existing.unlink()
                removed.append(existing.name)

    print(f"Built {archive}: {count} files, sha256={digest}")
    if removed:
        print(f"Removed superseded archives: {', '.join(removed)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
