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


class Patcher:
    def __init__(self, src, file, logger):
        """Convert nesting relationships to aggregate relationships

        Some software like Revit won't load nested children elements because
        they (incorrectly) don't consider it to be part of the spatial tree.
        For example, 12D software will use nesting.

        This patch converts all nest relationships into aggregate
        relationships.

        See bug: https://github.com/Autodesk/revit-ifc/issues/706

        Example:

        .. code:: python

            ifcpatch.execute({"input": "input.ifc", "file": model, "recipe": "ConvertNestToAggregate", "arguments": []})
        """
        self.src = src
        self.file = file
        self.logger = logger

    def patch(self):
        for rel in self.file.by_type("IfcRelNests"):
            new = self.file.createIfcRelAggregates(
                ifcopenshell.guid.new(),
                rel.OwnerHistory,
                rel.Name,
                rel.Description,
                rel.RelatingObject,
                rel.RelatedObjects,
            )
            self.file.remove(rel)
