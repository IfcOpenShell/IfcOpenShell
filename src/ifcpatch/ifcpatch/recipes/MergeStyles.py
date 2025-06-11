# IfcPatch - IFC patching utiliy
# Copyright (C) 2023 Dion Moult <dion@thinkmoult.com>
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

import ifcopenshell
import ifcopenshell.guid
import ifcopenshell.util.element


class Patcher:
    def __init__(self, file, logger):
        """Merge identical styles together

        Some software may create an obscene number of styles instead of reusing
        them properly. This patch merges all IfcPresentationStyle,
        IfcSurfaceStyleShading, and IfcColourRgb if they are identical.

        Example:

        .. code:: python

            ifcpatch.execute({"file": model, "recipe": "MergeStyles", "arguments": []})
        """
        self.file = file
        self.logger = logger

    def patch(self):
        for ifc_class in ("IfcColourRgb", "IfcSurfaceStyleShading", "IfcPresentationStyle"):
            uniques = {}
            i = 0
            for element in self.file.by_type(ifc_class):
                data = "-".join([str(a) for a in element])
                if unique := uniques.get(data, None):
                    ifcopenshell.util.element.replace_element(element, unique)
                    self.file.remove(element)
                    i += 1
                else:
                    uniques[data] = element
            print(f"Replaced {i} {ifc_class}")
