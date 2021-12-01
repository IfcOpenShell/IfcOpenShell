#!/usr/bin/env python3

# IfcClash - IFC-based clash detection.
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of IfcClash.
#
# IfcClash is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcClash is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcClash.  If not, see <http://www.gnu.org/licenses/>.

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
