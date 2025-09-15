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
import ifcopenshell.api
import ifcopenshell.api.geometry
import ifcopenshell.util
import ifcopenshell.util.element
import ifcopenshell.util.placement
import numpy as np


class Patcher:
    def __init__(self, file: ifcopenshell.file, logger: logging.Logger, ifc_class: str = "", only_xy: bool = True):
        """Resets the location of non-geometric spatial elements to 0,0,0

        Often, non-geometric spatial elements are located at arbitrary
        locations relative to the model. Because they are non-geometric but
        still contain placements, many users do not realise that their
        coordinates are actually ver far away and can cause precision issues if
        "fit all in view" is used.

        This patch lets you selectively reset the location of spatial elements
        (sites, buildings, storeys) back to 0,0,0. This is typically done after
        other coordinate operation patches. Alternatively, consider using the
        SetFalseOrigin patch which can do this operation built-in.

        :param ifc_class: The class of spatial element to reset coordinates
            for. Leave blank if you want to reset everything.
        :param only_xy: If True, only the X and Y coordinates will be affected.

        Example:

        .. code:: python

            # All IfcSites will shift back to 0,0,0.
            ifcpatch.execute({"file": model, "recipe": "ResetSpatialElementLocations", "arguments": ["IfcSite"]})
        """
        self.file = file
        self.logger = logger
        self.ifc_class = ifc_class
        self.only_xy = only_xy

    def patch(self) -> None:
        project = self.file.by_type("IfcProject")[0]
        queue = [project]
        while queue:
            element = queue.pop()
            if not self.ifc_class or element.is_a(self.ifc_class):
                self.patch_placement_to_origin(element)
            if parts := ifcopenshell.util.element.get_parts(element):
                queue.extend(parts)

    def patch_placement_to_origin(self, element: ifcopenshell.entity_instance) -> None:
        if not getattr(element, "ObjectPlacement", None) or getattr(element, "Representation", None):
            return
        if self.only_xy:
            m = ifcopenshell.util.placement.get_local_placement(element.ObjectPlacement)
            m[0][3] = 0.0
            m[1][3] = 0.0
            ifcopenshell.api.geometry.edit_object_placement(self.file, product=element, matrix=m, is_si=False)
            return
        ifcopenshell.api.geometry.edit_object_placement(self.file, product=element, matrix=np.eye(4), is_si=False)
