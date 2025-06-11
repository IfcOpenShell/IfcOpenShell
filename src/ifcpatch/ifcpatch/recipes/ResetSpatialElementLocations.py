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

import ifcopenshell
import logging


class Patcher:
    def __init__(self, file: ifcopenshell.file, logger: logging.Logger, ifc_class: str = "IfcSite"):
        """Resets the location of a spatial element to 0,0,0

        Another more specialised patch to fix incorrect coordinate usage is to
        reset the location of spatial elements (sites, buildings, storeys) back
        to 0,0,0.

        :param ifc_class: The class of spatial element to reset coordinates for.

        Example:

        .. code:: python

            # All IfcSites will shift back to 0,0,0.
            ifcpatch.execute({"input": "input.ifc", "file": model, "recipe": "ResetSpatialElementLocations", "arguments": ["IfcSite"]})
        """
        self.file = file
        self.logger = logger
        self.ifc_class = ifc_class

    def patch(self) -> None:
        project = self.file.by_type("IfcProject")[0]
        spatial_elements = self.find_decomposed_ifc_class(project, self.ifc_class)
        for spatial_element in spatial_elements:
            self.patch_placement_to_origin(spatial_element)

    def find_decomposed_ifc_class(
        self, element: ifcopenshell.entity_instance, ifc_class: str
    ) -> list[ifcopenshell.entity_instance]:
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

    def patch_placement_to_origin(self, element: ifcopenshell.entity_instance) -> None:
        element.ObjectPlacement.RelativePlacement.Location.Coordinates = (0.0, 0.0, 0.0)
        if element.ObjectPlacement.RelativePlacement.Axis:
            element.ObjectPlacement.RelativePlacement.Axis.DirectionRatios = (0.0, 0.0, 1.0)
        if element.ObjectPlacement.RelativePlacement.RefDirection:
            element.ObjectPlacement.RelativePlacement.RefDirection.DirectionRatios = (1.0, 0.0, 0.0)
