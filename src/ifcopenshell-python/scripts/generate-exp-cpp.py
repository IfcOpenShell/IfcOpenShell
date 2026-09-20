#!/usr/bin/env python3
# /// script
# ///
"""Generate C++ ifcparse schema sources from EXPRESS (.exp) definitions
and copy them into src/ifcparse/schemas.

Usage:
    python generate-exp-cpp.py
"""

import itertools
import shlex
import subprocess
import sys
from pathlib import Path
from typing import NamedTuple


class Schema(NamedTuple):
    exp: str
    schema_name: str


LICENSE_HEADER = """\
/********************************************************************************
 *                                                                              *
 * This file is part of IfcOpenShell.                                           *
 *                                                                              *
 * IfcOpenShell is free software: you can redistribute it and/or modify         *
 * it under the terms of the Lesser GNU General Public License as published by  *
 * the Free Software Foundation, either version 3.0 of the License, or          *
 * (at your option) any later version.                                          *
 *                                                                              *
 * IfcOpenShell is distributed in the hope that it will be useful,              *
 * but WITHOUT ANY WARRANTY; without even the implied warranty of               *
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the                 *
 * Lesser GNU General Public License for more details.                          *
 *                                                                              *
 * You should have received a copy of the Lesser GNU General Public License     *
 * along with this program. If not, see <http://www.gnu.org/licenses/>.         *
 *                                                                              *
 ********************************************************************************/

/********************************************************************************
 *                                                                              *
{exp_line}
 * but instead modify the python script that has been used to generate this.    *
 *                                                                              *
 ********************************************************************************/
"""

BOX_WIDTH = 81


def generated_header(exp: str) -> str:
    text = f" * This file has been generated from {exp}. Do not make modifications"
    exp_line = text + " " * (BOX_WIDTH - len(text) - 1) + "*"
    return LICENSE_HEADER.format(exp_line=exp_line)


class C:
    RED = "\033[31m"
    GREEN = "\033[32m"
    RESET = "\033[0m"


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = Path(subprocess.check_output(["git", "rev-parse", "--show-toplevel"], cwd=SCRIPT_DIR, text=True).strip())
EXPRESS_DIR = REPO_ROOT / "src" / "ifcopenshell-python" / "ifcopenshell" / "express"
SCHEMAS_DIR = REPO_ROOT / "src" / "ifcparse" / "schemas"


def run(*cmd: str) -> None:
    print("$", shlex.join(cmd))
    subprocess.check_call(cmd, cwd=EXPRESS_DIR)


def write_generated_file(out: str, exp: str, *ins: str) -> None:
    out_path = SCHEMAS_DIR / out
    with out_path.open("w") as f_out:
        f_out.write(generated_header(exp))
        for fn in ins:
            f_out.write((EXPRESS_DIR / fn).read_text())
    print(f"{C.GREEN}wrote {out_path}{C.RESET}")


def cleanup() -> None:
    for fn in itertools.chain(EXPRESS_DIR.glob("*.cpp"), EXPRESS_DIR.glob("*.h")):
        fn.unlink()


def run_express_parser(exp: str) -> None:
    run(
        sys.executable,
        "express_parser.py",
        exp,
        "header",
        "implementation",
        "schema_class",
        "definitions",
    )


def generate_schema(schema: Schema) -> None:
    if not (EXPRESS_DIR / schema.exp).exists():
        print(f"{C.RED}skipping {schema.exp}, not found{C.RESET}")
        return

    run_express_parser(schema.exp)

    name = schema.schema_name
    write_generated_file(f"{name}.cpp", schema.exp, f"{name}.cpp")
    write_generated_file(f"{name}.h", schema.exp, f"{name}.h")
    write_generated_file(f"{name}-schema.cpp", schema.exp, f"{name}-schema.cpp")
    write_generated_file(f"{name}-definitions.h", schema.exp, f"{name}-definitions.h")

    cleanup()


SCHEMAS = [
    Schema("IFC2X3_TC1.exp", "Ifc2x3"),
    Schema("IFC4_ADD2_TC1.exp", "Ifc4"),
    Schema("IFC4x1.exp", "Ifc4x1"),
    Schema("IFC4x2.exp", "Ifc4x2"),
    Schema("IFC4x3_RC1.exp", "Ifc4x3_rc1"),
    Schema("IFC4x3_RC2.exp", "Ifc4x3_rc2"),
    Schema("IFC4x3_RC3.exp", "Ifc4x3_rc3"),
    Schema("IFC4x3_RC4.exp", "Ifc4x3_rc4"),
    Schema("IFC4X3.exp", "Ifc4x3"),
    Schema("IFC4X3_TC1.exp", "Ifc4x3_tc1"),
    Schema("IFC4X3_ADD1.exp", "Ifc4x3_add1"),
    Schema("IFC4X3_ADD2.exp", "Ifc4x3_add2"),
]


def main() -> None:
    for schema in SCHEMAS:
        generate_schema(schema)

    run_express_parser("header_schema.exp")

    write_generated_file("Header_section_schema.cpp", "header_schema.exp", "Header_section_schema.cpp")
    write_generated_file("Header_section_schema.h", "header_schema.exp", "Header_section_schema.h")
    write_generated_file("Header_section_schema-schema.cpp", "header_schema.exp", "Header_section_schema-schema.cpp")

    cleanup()


if __name__ == "__main__":
    main()
