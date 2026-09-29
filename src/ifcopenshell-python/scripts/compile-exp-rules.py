#!/usr/bin/env python3
"""Download and compile ifcopenshell.express rules for all available schemas.

Missing schemas that are known to be available on GitHub are downloaded first.

Usage:
    python compile-exp-rules.py            # print this message
    python compile-exp-rules.py --check    # download schemas and report which are present
    python compile-exp-rules.py --compile  # implies --check, then compile rules for them
"""

import argparse
import subprocess
import sys
import urllib.request
from pathlib import Path
from typing import NamedTuple

EXPRESS_DIR = Path(__file__).parent.parent / "ifcopenshell" / "express"

GITHUB_RAW_URL = (
    "https://raw.githubusercontent.com/buildingSMART/IFC4.x-development/refs/heads/ifc4.3-main/reference_schemas"
)

# buildingSMART's website blocks automated/scripted downloads, so these have to be fetched manually.
BUILDINGSMART_SCHEMAS_URL = "https://technical.buildingsmart.org/standards/ifc/ifc-schema-specifications/"


class ExpFile(NamedTuple):
    name: str
    available_on_github: bool
    required: bool


SCHEMA_TO_EXP_FILENAME = {
    # Main schemas.
    "IFC2X3": ExpFile("IFC2X3_TC1", True, True),
    "IFC4": ExpFile("IFC4_ADD2_TC1", True, True),
    # IFC4X3_ADD2 is available from https://technical.buildingsmart.org/standards/ifc/ifc-schema-specifications/
    "IFC4X3_ADD2": ExpFile("IFC4X3_ADD2", False, True),
    # Withdrawn schemas.
    "IFC4X1": ExpFile("IFC4x1", True, True),
    "IFC4X2": ExpFile("IFC4x2", True, True),
    # Retired schemas.
    "IFC4X3_RC1": ExpFile("IFC4x3_RC1", True, True),
    "IFC4X3_RC2": ExpFile("IFC4x3_RC2", True, True),
    "IFC4X3_RC3": ExpFile("IFC4x3_RC3", True, True),
    "IFC4X3_RC4": ExpFile("IFC4x3_RC4", True, True),
    ## Couldn't find them anywhere, so I guess their .py will be missing updates.
    "IFC4X3": ExpFile("IFC4X3", False, False),
    "IFC4X3_ADD1": ExpFile("IFC4X3_ADD1", False, False),
    "IFC4X3_TC1": ExpFile("IFC4X3_TC1", False, False),
}


def download_schema(exp_filename: str, exp_path: Path) -> None:
    url = f"{GITHUB_RAW_URL}/{exp_filename}.exp"
    print(f"Downloading '{url}'...")
    with urllib.request.urlopen(url) as response:
        exp_path.write_bytes(response.read())


def resolve_exp_paths() -> dict[str, Path]:
    exp_paths: dict[str, Path] = {}
    for schema_name, exp_file in SCHEMA_TO_EXP_FILENAME.items():
        exp_path = EXPRESS_DIR / f"{exp_file.name}.exp"
        if not exp_path.exists():
            if not exp_file.available_on_github:
                if exp_file.required:
                    raise FileNotFoundError(
                        f"{schema_name}: '{exp_path}' not found and not available on GitHub. "
                        f"Download it from {BUILDINGSMART_SCHEMAS_URL} and save it to '{EXPRESS_DIR}'."
                    )
                print(f"Skipping {schema_name}: '{exp_path}' not found and not available on GitHub.")
                continue
            download_schema(exp_file.name, exp_path)
        print(f"{schema_name}: present ({exp_path})")
        exp_paths[schema_name] = exp_path
    return exp_paths


def compile_schema(schema_name: str, exp_path: Path) -> None:
    print(f"Compiling rules for {schema_name} from '{exp_path.name}'...")
    subprocess.run(
        [sys.executable, "-m", "rule_compiler", str(exp_path)],
        cwd=EXPRESS_DIR,
        check=True,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true", help="download schemas and report which are present")
    parser.add_argument("--compile", action="store_true", help="implies --check, then compile rules for them")
    args = parser.parse_args()

    if not args.check and not args.compile:
        print(__doc__)
        return

    exp_paths = resolve_exp_paths()

    if args.compile:
        for schema_name, exp_path in exp_paths.items():
            compile_schema(schema_name, exp_path)


if __name__ == "__main__":
    main()
