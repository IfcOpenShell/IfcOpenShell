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
import ifcopenshell.util.element
import ifcpatch
import logging
from typing import Union


class Patcher(ifcpatch.BasePatcher):
    def __init__(self, file: ifcopenshell.file, logger: Union[logging.Logger, None] = None):
        """Merge identical styles together

        Some software may create an obscene number of styles instead of reusing
        them properly. This patch merges all IfcPresentationStyle,
        IfcSurfaceStyleShading, and IfcColourRgb if they are identical.

        Example:

        .. code:: python

            ifcpatch.execute({"file": model, "recipe": "MergeStyles", "arguments": []})
        """
        super().__init__(file, logger)

    def patch(self):
        for ifc_class in ("IfcColourRgb", "IfcSurfaceStyleShading", "IfcPresentationStyle"):
            uniques = {}
            i = 0
            for element in self.file.by_type(ifc_class):
                ifc_class = element.is_a()
                key = "-".join([str(a) for a in element])
                if unique := uniques.get(ifc_class, {}).get(key, None):
                    ifcopenshell.util.element.replace_element(element, unique)
                    self.file.remove(element)
                    i += 1
                else:
                    uniques.setdefault(ifc_class, {})[key] = element
            print(f"Replaced {i} {ifc_class}")
