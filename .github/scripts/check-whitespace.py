# /// script
# dependencies = [
#   "pytest",
# ]
# ///

"""Check (and by default fix) whitespace issues in tracked source files:
- stray CR, e.g. 'hello\\rworld' -> 'helloworld'
- line ending mismatch, e.g. 'hello\\r\\n' -> 'hello\\n' (or vice versa)
- missing newline at end of file
- extra newline(s) at end of file
- trailing whitespace at end of line
"""

import argparse
import io
import os
import re
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path
from typing import BinaryIO, Literal, cast

import pytest


class C:
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    RESET = "\033[0m"


CR = b"\r"
CRLF = b"\r\n"
LF = b"\n"

LineSeparator = Literal[b"\r\n", b"\n"]
SYSTEM_LINE_SEPARATOR = cast(LineSeparator, os.linesep.encode())


class Checker:
    def __init__(self, newline: LineSeparator = SYSTEM_LINE_SEPARATOR) -> None:
        self.newline = newline
        self.issues = 0

    def report(self, label: str, issue: str) -> None:
        self.issues += 1
        print(f"{label}: {C.RED}{issue}{C.RESET}")

    def check_stray_cr(self, filepath: Path, check: bool) -> None:
        with filepath.open("r+b") as f:
            self._check_stray_cr(f, str(filepath), check)

    def _check_stray_cr(self, f: BinaryIO, label: str, check: bool) -> None:
        # a CR is "stray" if it isn't immediately followed by a LF, i.e. not part of a CRLF pair
        # CRLF/CR mismatch will be reported separately.
        stray_cr = re.compile(rb"\r(?!\n)")

        content = f.read()
        matches = list(stray_cr.finditer(content))
        if not matches:
            return

        line_numbers = dict.fromkeys(content.count(b"\n", 0, m.start()) + 1 for m in matches)
        for line_number in line_numbers:
            self.report(f"{label}:{line_number}", "stray carriage return")
        if check:
            return

        f.seek(0)
        f.write(stray_cr.sub(b"", content))
        f.truncate()

    def check_line_endings_mismatch(self, filepath: Path, check: bool) -> None:
        with filepath.open("r+b") as f:
            self._check_line_endings_mismatch(f, str(filepath), check)

    def _check_line_endings_mismatch(self, f: BinaryIO, label: str, check: bool) -> None:
        NEWLINE = self.newline

        def get_line_ending(line: bytes) -> LineSeparator | None:
            if line.endswith(CRLF):
                return CRLF
            if line.endswith(LF):
                return LF
            # last line with no trailing newline at all; check_eof_newline handles that
            return None

        changed = False
        fixed_lines = []
        for line_number, line in enumerate(f, start=1):
            found = get_line_ending(line)
            if found in (NEWLINE, None):
                fixed_lines.append(line)
                continue

            self.report(f"{label}:{line_number}", f"line ending mismatch (expected {NEWLINE!r}, found {found!r})")
            changed = True
            content = line[: -len(found)]
            fixed_lines.append(content + NEWLINE)

        if changed and not check:
            f.seek(0)
            f.write(b"".join(fixed_lines))
            f.truncate()

    def check_eof_newline(self, filepath: Path, check: bool) -> None:
        with filepath.open("r+b") as f:
            self._check_eof_newline(f, str(filepath), check)

    def _check_eof_newline(self, f: BinaryIO, label: str, check: bool) -> None:
        NEWLINE = self.newline
        NEWLINE_SIZE = len(NEWLINE)

        size = f.seek(0, os.SEEK_END)
        if size == 0:
            return

        trailing_newlines = 0
        while True:
            pos = f.seek((-trailing_newlines - 1) * NEWLINE_SIZE, os.SEEK_END)
            if f.read(NEWLINE_SIZE) != NEWLINE:
                break
            trailing_newlines += 1
            if pos == 0:
                break

        if trailing_newlines == 0:
            self.report(label, "missing newline at end of file")
            if check:
                return
            f.seek(0, os.SEEK_END)
            f.write(NEWLINE)
        elif trailing_newlines > 1:
            self.report(label, f"{trailing_newlines} trailing newlines at end of file")
            if check:
                return
            f.truncate(size - (trailing_newlines - 1) * NEWLINE_SIZE)

    def check_trailing_whitespaces(self, filepath: Path, check: bool) -> None:
        with filepath.open("r+b") as f:
            self._check_trailing_whitespaces(f, str(filepath), check)

    def _check_trailing_whitespaces(self, f: BinaryIO, label: str, check: bool) -> None:
        NEWLINE = self.newline
        NEWLINE_SIZE = len(NEWLINE)

        changed = False
        fixed_lines = []
        for line_number, line in enumerate(f, start=1):
            has_newline = line.endswith(NEWLINE)
            content = line[:-NEWLINE_SIZE] if has_newline else line
            stripped = content.rstrip()
            if stripped != content:
                self.report(f"{label}:{line_number}", "trailing whitespace")
                changed = True
            fixed_lines.append(stripped + (NEWLINE if has_newline else b""))

        if changed and not check:
            f.seek(0)
            f.write(b"".join(fixed_lines))
            f.truncate()


CheckMethod = Callable[[Checker, BinaryIO, str, bool], None]


class TestChecker:
    def _assert_check(
        self,
        method: CheckMethod,
        content: bytes,
        expected_issues: int,
        fixed: bytes,
        check: bool,
        line_ending: LineSeparator,
        *,
        transform: bool = True,
    ) -> None:
        checker = Checker(line_ending)
        if line_ending == CRLF and transform:
            content = content.replace(LF, CRLF)
            fixed = fixed.replace(LF, CRLF)
        buffer = io.BytesIO(content)
        method(checker, buffer, "test", check)
        assert buffer.getvalue() == (content if check else fixed)
        assert checker.issues == expected_issues

    @pytest.mark.parametrize(
        ("content", "expected_issues", "fixed"),
        (
            # OK
            (b"", 0, b""),
            (b"hello\n", 0, b"hello\n"),
            (b"line1\r\nline2\n", 0, b"line1\r\nline2\n"),
            # ERR
            (b"hello\rworld\n", 1, b"helloworld\n"),
            (b"a\rb\rc\n", 1, b"abc\n"),
            (b"hello\r", 1, b"hello"),
        ),
    )
    @pytest.mark.parametrize("check", [False, True])
    def test_check_stray_cr(self, content: bytes, expected_issues: int, fixed: bytes, check: bool) -> None:
        # Don't parametrize by line endings, since in this case it doesn't matter.
        self._assert_check(Checker._check_stray_cr, content, expected_issues, fixed, check, LF)

    @pytest.mark.parametrize(
        ("content", "expected_issues", "fixed", "line_ending"),
        (
            # OK
            (b"", 0, b"", LF),
            (b"hello\n", 0, b"hello\n", LF),
            (b"hello\r\n", 0, b"hello\r\n", CRLF),
            # ERR
            (b"hello\r\n", 1, b"hello\n", LF),
            (b"a\nb\r\nc\n", 1, b"a\nb\nc\n", LF),
            (b"a\r\nb\r\n", 2, b"a\nb\n", LF),
            (b"hello\n", 1, b"hello\r\n", CRLF),
            (b"a\r\nb\nc\r\n", 1, b"a\r\nb\r\nc\r\n", CRLF),
        ),
    )
    @pytest.mark.parametrize("check", [False, True])
    def test_check_line_endings_mismatch(
        self, content: bytes, expected_issues: int, fixed: bytes, line_ending: LineSeparator, check: bool
    ) -> None:
        self._assert_check(
            Checker._check_line_endings_mismatch, content, expected_issues, fixed, check, line_ending, transform=False
        )

    @pytest.mark.parametrize(
        ("content", "expected_issues", "fixed"),
        (
            # OK
            (b"", 0, b""),
            (b"hello\n", 0, b"hello\n"),
            # ERR
            (b"hello", 1, b"hello\n"),
            (b"hello\n\n\n", 1, b"hello\n"),
            (b"\n\n\n", 1, b"\n"),
        ),
    )
    @pytest.mark.parametrize("check", [False, True])
    @pytest.mark.parametrize("line_ending", [LF, CRLF])
    def test_check_eof_newline(
        self, content: bytes, expected_issues: int, fixed: bytes, check: bool, line_ending: LineSeparator
    ) -> None:
        self._assert_check(Checker._check_eof_newline, content, expected_issues, fixed, check, line_ending)

    @pytest.mark.parametrize(
        ("content", "expected_issues", "fixed"),
        (
            # OK
            (b"", 0, b""),
            (b"hello\n", 0, b"hello\n"),
            (b"hello", 0, b"hello"),
            # ERR
            (b" ", 1, b""),
            (b"hello ", 1, b"hello"),
        ),
    )
    @pytest.mark.parametrize("check", [False, True])
    @pytest.mark.parametrize("line_ending", [LF, CRLF])
    def test_check_trailing_whitespaces(
        self, content: bytes, expected_issues: int, fixed: bytes, check: bool, line_ending: LineSeparator
    ) -> None:
        self._assert_check(Checker._check_trailing_whitespaces, content, expected_issues, fixed, check, line_ending)

    @staticmethod
    def run_tests(extra_args: list[str] | None = None) -> None:
        pytest.main([__file__, *(extra_args or [])])


def existing_path(value: str) -> Path:
    path = Path(value)
    if not path.exists():
        raise argparse.ArgumentTypeError(f"path not found: {value}")
    return path


# Python files are covered by `black`.
PATTERNS = (
    "*.cpp",
    "*.h",
    "*.i",
)

REPO_ROOT = Path(subprocess.check_output(["git", "rev-parse", "--show-toplevel"], text=True).strip())

# Generated files; formatted by the express codegen, not by this script.
IGNORED_DIRS = (REPO_ROOT / "src/ifcparse/schemas",)


def get_tracked_files(root: Path | None = None) -> list[Path]:
    output = subprocess.check_output(
        ["git", "ls-files", "--others", "--cached", "--exclude-standard", *PATTERNS],
        cwd=root,
        text=True,
    )
    base = root if root is not None else Path()
    filepaths = []
    for line in output.splitlines():
        filepath = base / line
        if not any(filepath.resolve().is_relative_to(d) for d in IGNORED_DIRS):
            filepaths.append(filepath)
    return filepaths


def main() -> int:
    # anything after "--" is forwarded to pytest, e.g. `--test -- --capture=no`
    argv = sys.argv[1:]
    if "--" in argv:
        split = argv.index("--")
        argv, extra_args = argv[:split], argv[split + 1 :]
    else:
        extra_args = []

    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=__doc__,
    )
    parser.add_argument("paths", type=existing_path, nargs="*", help="files or directories to check")
    parser.add_argument(
        "--check",
        action="store_true",
        help="only check for whitespace issues without applying fixes",
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="run self-tests",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="print each checked path",
    )
    args = parser.parse_args(argv)

    if args.test:
        TestChecker.run_tests(extra_args)
        return 0

    if args.paths:
        filepaths: list[Path] = []
        for path in args.paths:
            filepaths.extend(get_tracked_files(path) if path.is_dir() else [path])
    else:
        filepaths = get_tracked_files()

    # dict.fromkeys() dedupes while preserving order, unlike set().
    filepaths = list(dict.fromkeys(filepaths))

    checker = Checker()
    for filepath in filepaths:
        if args.verbose:
            print(f"checking {filepath}")
        checker.check_stray_cr(filepath, args.check)
        checker.check_line_endings_mismatch(filepath, args.check)
        checker.check_eof_newline(filepath, args.check)
        checker.check_trailing_whitespaces(filepath, args.check)
    print(f"{len(filepaths)} file(s) checked.")
    if not checker.issues:
        color = C.GREEN
    elif args.check:
        color = C.RED
    else:
        color = C.YELLOW
    outcome = "found" if args.check else "found and fixed"
    print(f"{color}{checker.issues} issue(s) {outcome}.{C.RESET}")

    return 1 if args.check and checker.issues else 0


if __name__ == "__main__":
    sys.exit(main())
