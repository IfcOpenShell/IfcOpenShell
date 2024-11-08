#!/usr/bin/env python3

# IfcTester - IDS based model auditing
# Copyright (C) 2022 Dion Moult <dion@thinkmoult.com>
#
# This file is part of IfcTester.
#
# IfcTester is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcTester is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcTester.  If not, see <http://www.gnu.org/licenses/>.

import time
import argparse
import ifcopenshell
from . import ids
from . import reporter
from pathlib import Path

parser = argparse.ArgumentParser(description="Uses an IDS to audit an IFC")
parser.add_argument("ids", type=str, help="Path to an IDS")
parser.add_argument("ifc", type=str, help="Path to an IFC", nargs="?")
parser.add_argument("-r", "--reporter", type=str, help="The reporting method to view audit results", default="Console")
parser.add_argument("--no-color", help="Disable colour output (supported by Console reporting)", action="store_true")
parser.add_argument("--excel-safe", help="Make sure exported ODS is safely exported for Excel", action="store_true")
parser.add_argument("-o", "--output", help="Output file (supported for all types of reporting except Console)")
args = parser.parse_args()

ids_path = Path(args.ids)
if ids_path.suffix.lower() != ".ids":
    raise Exception(f"Provided file is not an .ids file: '{ids_path}'.")

ifc_patch = Path(args.ifc)
if ifc_patch.suffix.lower() != ".ifc":
    raise Exception(f"Provided file is not an .ifc file: '{ifc_patch}'.")

specs = ids.open(str(ids_path))
if args.ifc:
    start = time.time()
    ifc = ifcopenshell.open(ifc_patch)
    assert isinstance(ifc, ifcopenshell.file)
    print("Finished loading:", time.time() - start)
    start = time.time()
    specs.validate(ifc)
    print("Finished validating:", time.time() - start)

if args.reporter == "Console":
    engine = reporter.Console(specs, use_colour=not args.no_color)
elif args.reporter == "Txt":
    engine = reporter.Txt(specs)
elif args.reporter == "Json":
    engine = reporter.Json(specs)
elif args.reporter == "Html":
    engine = reporter.Html(specs)
elif args.reporter == "Ods":
    engine = reporter.Ods(specs, excel_safe=args.excel_safe)
elif args.reporter == "OdsSummary":
    engine = reporter.OdsSummary(specs, excel_safe=args.excel_safe)
elif args.reporter == "Bcf":
    engine = reporter.Bcf(specs)

engine.report()

if args.output:
    engine.to_file(args.output)
else:
    print(engine.to_string())
