#!/usr/bin/env python3

# IfcPatch - IFC patching utiliy
# Copyright (C) 2020, 2021, 2022 Dion Moult <dion@thinkmoult.com>
#
# This file is part of IfcPatch.
#
# IfcPatch is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcPatch is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcPatch.  If not, see <http://www.gnu.org/licenses/>.

import argparse
import ifcpatch
import ifcopenshell

parser = argparse.ArgumentParser(description="Patches IFC files to fix badly formatted data")
parser.add_argument("-i", "--input", type=str, required=True, help="The IFC file to patch")
parser.add_argument("-o", "--output", type=str, help="The output file to save the patched IFC")
parser.add_argument("-r", "--recipe", type=str, required=True, help="Name of the recipe to use when patching")
parser.add_argument("-l", "--log", type=str, help="Specify a log file", default="ifcpatch.log")
parser.add_argument("-a", "--arguments", nargs="+", help="Specify custom arguments to the patch recipe")
args = vars(parser.parse_args())

print("# Loading IFC file ...")
args["file"] = ifcopenshell.open(args["input"])

print("# Patching ...")
output = ifcpatch.execute(args)

print("# Writing patched file ...")
if not args["output"]:
    args["output"] = args["input"]
ifcpatch.write(output, args["output"])

print("# All tasks are complete :-)")
