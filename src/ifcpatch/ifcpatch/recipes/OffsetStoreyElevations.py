# IfcPatch - IFC patching utiliy
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
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

import typing


class Patcher:
    def __init__(self, src, file, logger, z: typing.Union[str, float] = "0"):
        """Offset building storeys by a particular Z value

        All objects placed relative to the storeys will also be shifted.

        :param z: The Z value in project length units to offset storeys by.
        :type z: typing.Union[str, float]

        Example:

        .. code:: python

            # Shift all storeys up by 42 units
            ifcpatch.execute({"input": "input.ifc", "file": model, "recipe": "OffsetStoreyElevations", "arguments": [42]})
        """
        self.src = src
        self.file = file
        self.logger = logger
        self.z = float(z)

    def patch(self):
        project = self.file.by_type("IfcProject")[0]
        storeys = self.find_decomposed_ifc_class(project, "IfcBuildingStorey")
        for storey in storeys:
            co = storey.ObjectPlacement.RelativePlacement.Location.Coordinates
            storey.ObjectPlacement.RelativePlacement.Location.Coordinates = (co[0], co[1], co[2] + float(self.z))
            co = storey.ObjectPlacement.RelativePlacement.Location.Coordinates
            # NOTE  If the geometric data is provided (ObjectPlacement is
            # specified), the Elevation value shall either not be included, or
            # be equal to the local placement Z value.
            storey.Elevation = co[2]

    def find_decomposed_ifc_class(self, element, ifc_class):
        results = []
        rel_aggregates = element.IsDecomposedBy
        if not rel_aggregates:
            return results
        for rel_aggregate in rel_aggregates:
            for part in rel_aggregate.RelatedObjects:
                if part.is_a(ifc_class):
                    results.append(part)
                results.extend(self.find_decomposed_ifc_class(part, ifc_class))
        return results
