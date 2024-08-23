# IfcPatch - IFC patching utiliy
# Copyright (C) 2023 Dion Moult <dion@thinkmoult.com>,  Massimo Fabbro <maxfb87@yahoo.it>
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

""" This script regenerates all drawing paths in case they have been created in a different operating system.

It is useful when an annotation drawing has been created on windows and you want to recreate the
drawig in linux.
In this case, bonsai would tell you that can't load "stylesheet" or "markers" or "symbols" or "patterns" folder.
If this happens, this script comes in rescue!
Basically, as the path is stored in a string, the script replaces the existing sep char with the right one.
It works on the active ifc file (if exists).

"""

import bonsai.tool as tool
import ifcopenshell
import sys


import os
from sys import platform

file = tool.Ifc.get()
if not file:
    print("No ifc file")
    sys.exit()

annotations = file.by_type("IfcAnnotation")
count = 0

for annotation in annotations:
    if annotation.ObjectType == "DRAWING":
        psets = ifcopenshell.util.element.get_psets(annotation)
        pset = psets["EPset_Drawing"]
        pset_ifc = file.by_id(pset["id"])
        wrong_sep = ""
        if platform == "linux" or platform == "linux2" or platform == "darwin":
            wrong_sep = "\\"
        if platform == "win32":
            wrong_sep = "/"
        ifcopenshell.api.run(
            "pset.edit_pset",
            file,
            pset=pset_ifc,
            properties={
                "Stylesheet": pset["Stylesheet"].replace(wrong_sep, os.path.sep),
                "Markers": pset["Markers"].replace(wrong_sep, os.path.sep),
                "Symbols": pset["Symbols"].replace(wrong_sep, os.path.sep),
                "Patterns": pset["Patterns"].replace(wrong_sep, os.path.sep),
            },
        )
        count += 1

print(f"DONE! Checked {count} drawings")
