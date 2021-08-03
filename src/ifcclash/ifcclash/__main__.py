#!/usr/bin/env python3
import sys
import json
import logging
import argparse
from .ifcclash import Clasher, ClashSettings

parser = argparse.ArgumentParser(description="Clashes geometry between two IFC files")
parser.add_argument("input", type=str, help="A JSON dataset describing a series of clashsets")
parser.add_argument(
    "-o", "--output", type=str, help="The JSON diff file to output. Defaults to output.json", default="output.json"
)
args = parser.parse_args()

settings = ClashSettings()
settings.output = args.output
settings.logger = logging.getLogger("Clash")
settings.logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
settings.logger.addHandler(handler)
ifc_clasher = Clasher(settings)
with open(args.input, "r") as clash_sets_file:
    ifc_clasher.clash_sets = json.loads(clash_sets_file.read())
ifc_clasher.clash()
ifc_clasher.export()
