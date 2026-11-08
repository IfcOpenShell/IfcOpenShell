# /// script
# dependencies = [
#   "packaging",
#   "semver",
# ]
# ///

"""Validate the `VERSION` file (or set it with `--bump`) and print the version forms derived from it.

Main source of truth for `VERSION` format, as it's checked in CI.

Two derived formats we do need to support:
- Python PEP 440 - used by all our Python packages
- SemVer - used by Blender

Notably, Python supporst `0.8.5.post1`, while semver rejects it.

Similar derived versions are used in `vars.mk` and in cmake.
"""

import argparse
import re
import sys
from datetime import date
from pathlib import Path
from typing import NamedTuple

import semver
from packaging.version import InvalidVersion, Version

VERSION_FILE = Path(__file__).parents[2] / "VERSION"

# Shape supported by VERSION.
# TODO: do we really need `alpha` suffix support here or it's appended everywhere automatically?
RE_VERSION = re.compile(r"^\d+\.\d+\.\d+((alpha|post)\d+)?$")


class Versions(NamedTuple):
    version: str
    version_base: str
    version_python: str
    version_semver: str
    version_daily: str
    version_semver_daily: str

    @classmethod
    def derive(cls, version: str) -> "Versions":
        base = re.sub(r"[A-Za-z]+\d+$", "", version)
        version_date = date.today().strftime("%y%m%d")
        return cls(
            version=version,
            version_base=base,
            version_python=version.replace("alpha", "a"),
            version_semver=re.sub(r"([A-Za-z]+)(\d+)$", r"-\1\2", version),
            version_daily=f"{base}a{version_date}",
            version_semver_daily=f"{base}-alpha{version_date}",
        )


def validate(version: str) -> list[str]:
    if not RE_VERSION.match(version):
        return [
            f"'{version}' should be 'X.Y.Z' with an optional 'alpha<N>' or 'post<N>' suffix without separator, "
            "e.g. '0.9.0', '0.9.0alpha0', '0.9.0post1'."
        ]

    errors: list[str] = []
    versions = Versions.derive(version)
    for field in ("version_python", "version_daily"):
        value = getattr(versions, field)
        try:
            Version(value)
        except InvalidVersion:
            errors.append(f"{field.upper()} '{value}' is not a valid PEP 440 version.")
    for field in ("version_semver", "version_semver_daily"):
        value = getattr(versions, field)
        if not semver.Version.is_valid(value):
            errors.append(f"{field.upper()} '{value}' is not a valid SemVer version (required by Blender).")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--bump", metavar="VERSION", help="Validate VERSION and write it to the `VERSION` file.")
    args = parser.parse_args()

    version = args.bump if args.bump is not None else VERSION_FILE.read_text().strip()
    errors = validate(version)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    versions = Versions.derive(version)
    for name, value in versions._asdict().items():
        print(f"{name.upper():<20} {value}")
    print(f"{'Python (normalized)':<20} {Version(versions.version_python)}")

    if args.bump is not None:
        VERSION_FILE.write_text(f"{version}\n")
        print(f"Updated '{VERSION_FILE.name}'.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
