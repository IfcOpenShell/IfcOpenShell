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

import os
from sys import platform

class Patcher:
    def __init__(self, src, file, logger):
        """ Regenerate all drawings path in case they have been created in a different operating system.

        It is useful when an annotation drawing has been created on windows and you want to recreate the
        drawig in linux.
        In this case, blenderbim would tell you that can't load "stylesheet" or "markers" or "symbols" or "patterns" folder.
        If this happens, this recipie comes in rescue!
        Basically, as the path is stored in a string, the recipie replace the existing sep char with the right one.
        It doesn't need to specify the ifc output file or any arguments.
        If ifc ouput file is specified, it saves the patched file in the new file.

        Example:

        .. code:: python

            ifcpatch.execute({"input": model, "recipe": "ReplaceDrawingPath"})
        """
        self.src = src
        self.file = file
        self.logger = logger

    def patch(self):
        import blenderbim.tool as tool
        import ifcopenshell

        annotations = self.file.by_type('IfcAnnotation')

        for annotation in annotations:
            if annotation.ObjectType == 'DRAWING':
                psets = ifcopenshell.util.element.get_psets(annotation)
                pset = psets['EPset_Drawing']
                pset_ifc = self.file.by_id(pset['id'])
                wrong_sep = ""
                if platform == 'linux' or platform == 'linux2' or platform == 'darwin':
                    wrong_sep = "\\"
                if platform == 'win32':
                    wrong_sep = "/"
                ifcopenshell.api.run("pset.edit_pset", self.file, pset = pset_ifc, properties = {
                    'Stylesheet' : pset['Stylesheet'].replace(wrong_sep, os.path.sep),
                    'Markers' : pset['Markers'].replace(wrong_sep, os.path.sep),
                    'Symbols' : pset['Symbols'].replace(wrong_sep, os.path.sep),
                    'Patterns' : pset['Patterns'].replace(wrong_sep, os.path.sep),
                })

