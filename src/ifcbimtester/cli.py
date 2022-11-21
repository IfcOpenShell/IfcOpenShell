#!/usr/bin/env python3

# BIMTester - OpenBIM Auditing Tool
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of BIMTester.
#
# BIMTester is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# BIMTester is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with BIMTester.  If not, see <http://www.gnu.org/licenses/>.


import os
import argparse
import bimtester.clean
import bimtester.reports
import bimtester.run

parser = argparse.ArgumentParser(description="Runs unit tests for BIM data")
parser.add_argument("-a", "--action", type=str, help="Action to perform, from run/purge", default="run")
parser.add_argument("--advanced-arguments", type=str, help="Specify arguments to Behave", default="")
parser.add_argument("-c", "--console", action="store_true", help="Show results in the console")
parser.add_argument("-f", "--feature", type=str, help="Specify a feature file to test", required=True)
parser.add_argument("-i", "--ifc", type=str, help="Specify an IFC file to test", required=True)
parser.add_argument("-p", "--path", type=str, help="Define a path for use in test steps that use relative paths")
parser.add_argument("-r", "--report", type=str, help="Specify an output file for a HTML report")
parser.add_argument("--steps", type=str, help="Specify a custom step definition Python file or directory")
parser.add_argument("--schema-file", type=str, help="Path to a custom IFC schema, used with --schema-name")
parser.add_argument("--schema-name", type=str, help="The name of a custom IFC schema, used with --schema-file")
parser.add_argument("--lang", type=str, help="Specify a language e.g. en/de/fr/it", default="")

args = vars(parser.parse_args())

if args["action"] == "run":
    report_json = bimtester.run.TestRunner(args["ifc"], args["schema_file"]).run(args)
    if args["report"]:
        bimtester.reports.ReportGenerator().generate(report_json, args["report"])
elif args["action"] == "purge":
    bimtester.clean.TestPurger().purge()
