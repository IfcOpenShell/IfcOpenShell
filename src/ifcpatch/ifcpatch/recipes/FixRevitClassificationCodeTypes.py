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


class Patcher:
    def __init__(self, src, file, logger):
        """Reassigns occurrence classifications to types

        Revit has a bug (see https://github.com/Autodesk/revit-ifc/issues/691)
        where it assigns classification codes to occurrences instead of types.
        Almost always, this is not what you want. This patch reassigns all
        classifications to their respective types.

        Example:

        .. code:: python

            ifcpatch.execute({"input": "input.ifc", "file": model, "recipe": "FixRevitClassificationCodeTypes"})
        """
        self.src = src
        self.file = file
        self.logger = logger

    def patch(self):
        for rel in self.file.by_type("IfcRelAssociatesClassification"):
            related_types = set()
            for related_object in rel.RelatedObjects:
                relating_type = ifcopenshell.util.element.get_type(related_object)
                if relating_type:
                    related_types.add(relating_type)
                else:
                    related_types.add(related_object)
            rel.RelatedObjects = list(related_types)
