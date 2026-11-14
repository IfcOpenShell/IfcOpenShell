#!/usr/bin/env python3
"""Check (and optionally fix) copyright notice year ranges against git history.

Copyright headers in this repo look like:

    # Copyright (C) 2021 Thomas Krijnen <thomas@aecgeeks.com>

but the year is rarely kept up to date, and the format used for a range
varies ("2020-2021", "2020, 2021", ...). This script derives the year range
a file was actually touched in (first commit year to last commit year, via
`git log --follow`) and compares it against the year(s) in the file's
copyright line(s).

Usage:
    # Report mismatches for an explicit list of files (never repo-wide by default):
    python .github/scripts/check_copyright.py path/to/file.py path/to/other.py

    # Report mismatches for a glob:
    python .github/scripts/check_copyright.py "src/ifcopenshell-python/ifcopenshell/*.py"

    # Rewrite the year(s) in place to match git history:
    python .github/scripts/check_copyright.py --fix path/to/file.py

Files with no copyright header, no git history, or more than one copyright
line (multiple listed authors) are reported but never modified: this script
only ever touches the year portion of an unambiguous, single-author header.
"""

from __future__ import annotations

import argparse
import glob
import re
import subprocess
import sys
from pathlib import Path

# Matches e.g. "# Copyright (C) 2021 Name <email>" or "// Copyright (c) 2020-2021 Name".
COPYRIGHT_RE = re.compile(
    r"^(?P<prefix>\s*[#/]{1,2}\s*Copyright\s*\(C\)\s*)" r"(?P<years>\d{4}(?:\s*[-,]\s*\d{4})?)" r"(?P<suffix>.*)$",
    re.IGNORECASE,
)


def git_year_range(path: Path, repo_root: Path) -> tuple[int, int] | None:
    """Return (first_year, last_year) the file was committed, or None if it has no git history."""
    result = subprocess.run(
        ["git", "log", "--follow", "--format=%ad", "--date=format:%Y", "--", str(path)],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )
    years = sorted({int(year) for year in result.stdout.split()})
    if not years:
        return None
    return years[0], years[-1]


def format_years(first: int, last: int) -> str:
    return str(first) if first == last else f"{first}-{last}"


def parse_years(years_text: str) -> tuple[int, int]:
    """Parse a header's year text ("2021", "2020-2021", "2020, 2021") into (first, last)."""
    parts = [int(p) for p in re.split(r"\s*[-,]\s*", years_text.strip())]
    return min(parts), max(parts)


class Report:
    def __init__(self, path: Path, status: str, detail: str, line_index: int | None = None):
        self.path = path
        self.status = status  # ok | mismatch | no-header | no-history | multi-author
        self.detail = detail
        self.line_index = line_index


def check_file(path: Path, repo_root: Path) -> Report:
    try:
        text = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError) as e:
        return Report(path, "error", str(e))

    lines = text.splitlines(keepends=True)
    matches = [(i, COPYRIGHT_RE.match(line)) for i, line in enumerate(lines)]
    matches = [(i, m) for i, m in matches if m]

    if not matches:
        return Report(path, "no-header", "no 'Copyright (C) YYYY' line found")

    git_range = git_year_range(path, repo_root)
    if git_range is None:
        return Report(path, "no-history", "file has no git history (not committed?)")

    if len(matches) > 1:
        return Report(
            path,
            "multi-author",
            f"{len(matches)} copyright lines (multiple listed authors), skipping: "
            "per-author year ranges need a design decision, see issue #4467",
        )

    line_index, match = matches[0]
    header_range = parse_years(match.group("years"))
    expected = format_years(*git_range)

    if header_range == git_range:
        return Report(path, "ok", f"{expected} matches git history", line_index)

    return Report(
        path,
        "mismatch",
        f"header says '{match.group('years').strip()}', git history says '{expected}'",
        line_index,
    )


def fix_file(path: Path, report: Report, repo_root: Path) -> None:
    assert report.status == "mismatch" and report.line_index is not None
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)
    match = COPYRIGHT_RE.match(lines[report.line_index])
    assert match is not None

    git_range = git_year_range(path, repo_root)
    assert git_range is not None
    expected = format_years(*git_range)

    lines[report.line_index] = match.group("prefix") + expected + match.group("suffix") + "\n"
    path.write_text("".join(lines), encoding="utf-8")


def resolve_paths(patterns: list[str]) -> list[Path]:
    paths: list[Path] = []
    for pattern in patterns:
        matched = glob.glob(pattern, recursive=True)
        if not matched and Path(pattern).is_file():
            matched = [pattern]
        for m in matched:
            p = Path(m)
            if p.is_file():
                paths.append(p)
    return paths


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("paths", nargs="+", help="explicit files and/or globs to check (never repo-wide implicitly)")
    parser.add_argument("--fix", action="store_true", help="rewrite mismatched headers in place")
    parser.add_argument("--repo-root", default=".", help="path to the git repository root (default: cwd)")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    files = resolve_paths(args.paths)
    if not files:
        print("No files matched.", file=sys.stderr)
        return 2

    mismatches = 0
    for path in sorted(files):
        report = check_file(path, repo_root)
        if report.status == "ok":
            continue
        if report.status == "mismatch":
            mismatches += 1
            if args.fix:
                fix_file(path, report, repo_root)
                print(f"FIXED     {path}: {report.detail}")
            else:
                print(f"MISMATCH  {path}: {report.detail}")
        elif report.status == "no-header":
            print(f"NO HEADER {path}: {report.detail}")
        elif report.status == "no-history":
            print(f"NO GIT    {path}: {report.detail}")
        elif report.status == "multi-author":
            print(f"SKIP      {path}: {report.detail}")
        else:
            print(f"ERROR     {path}: {report.detail}")

    if not args.fix and mismatches:
        print(f"\n{mismatches} file(s) with copyright year mismatches.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
