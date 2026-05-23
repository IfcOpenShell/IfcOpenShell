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
import glob
import os
import sys

import ifcopenshell

import ifcpatch


def main():
    parser = argparse.ArgumentParser(description="Patches IFC files to fix badly formatted data")
    parser.add_argument("-i", "--input", type=str, required=True, help="The IFC file or glob pattern (e.g. *.ifc) to patch")
    parser.add_argument("-o", "--output", type=str, help="The output file or directory")
    parser.add_argument("-r", "--recipe", type=str, required=True, help="Name of the recipe to use when patching")
    parser.add_argument("-l", "--log", type=str, help="Specify a log file", default="ifcpatch.log")
    parser.add_argument("-a", "--arguments", nargs="+", help="Specify custom arguments to the patch recipe")
    args = vars(parser.parse_args())

    inputs = glob.glob(args["input"])
    if not inputs:
        print(f"Error: No files found matching pattern: {args['input']}")
        sys.exit(1)

    if len(inputs) > 1:
        print(f"# Batch processing {len(inputs)} files ...")

    output_is_dir = args["output"] and (os.path.isdir(args["output"]) or not os.path.splitext(args["output"])[1])

    for input_file in inputs:
        print(f"# Processing {input_file} ...")
        
        current_args = args.copy()
        try:
            current_args["file"] = ifcopenshell.open(input_file)
            current_args["input"] = input_file
        except Exception as e:
            print(f"Error loading {input_file}: {e}")
            continue

        try:
            output = ifcpatch.execute(current_args)
        except Exception as e:
            print(f"Error patching {input_file}: {e}")
            continue

        if not args["output"]:
            current_output = input_file
        elif output_is_dir:
            if not os.path.exists(args["output"]):
                os.makedirs(args["output"], exist_ok=True)
            current_output = os.path.join(args["output"], os.path.basename(input_file))
        else:
            current_output = args["output"]

        print(f"# Writing {current_output} ...")
        ifcpatch.write(output, current_output)

    print("# All tasks are complete :-)")


if __name__ == "__main__":
    main()
