#!/usr/bin/env python3

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
parser.add_argument("-i", "--ifc", type=str, help="Specify a ifc file", required=True)
parser.add_argument("-p", "--path", type=str, help="Define a path for use in tests")
parser.add_argument("-r", "--report", type=str, help="Specify an output file for a HTML report")
parser.add_argument("--schema", type=str, help="Specify an output file for a HTML report")
parser.add_argument("--lang", type=str, help="Specify a language", default="")

args = vars(parser.parse_args())

if args["action"] == "run":
    report_json = bimtester.run.TestRunner(args["ifc"], schema=args["schema"] or None).run(args)
    if args["report"]:
        bimtester.reports.ReportGenerator().generate(report_json, args["report"])
elif args["action"] == "purge":
    bimtester.clean.TestPurger().purge()
