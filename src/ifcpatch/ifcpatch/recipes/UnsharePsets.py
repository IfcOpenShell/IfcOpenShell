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

import ifcopenshell
import ifcopenshell.api.pset
import ifcopenshell.guid
import ifcopenshell.util.element
import ifcopenshell.util.selector
from logging import Logger


class Patcher:
    def __init__(self, src: str, file: ifcopenshell.file, logger: Logger, query: str = ""):
        """Create independent copies for shared psets in IFC file.

        In IFC it's possible that same property set is shared by multiple elements,
        so editing it's properties will automatically change their values for all those elements.

        Sometimes it's intended but sometimes it's not and it's just the way some other
        software exports IFC (e.g. there is a known case when Tekla exports shared psets for all the occurrences).
        While it is more optimized way to store data, it may lead to unexpected results when editing properties.

        This recipe creates independent copies of all shared psets (may be limited by the query)
        and assigns them to the elements, so they can be edited without affecting any other elements.

        :param query: A query to select the subset of IFC elements, optional.
            If not provided, patch will be applied to all shared property sets in the model.

        Example:

        .. code:: python

            # Unshare all psets in the IFC file.
            ifcpatch.execute({"input": "input.ifc", "file": model, "recipe": "UnsharePsets"})

            # Unshare psets on all IfcWalls.
            ifcpatch.execute({"input": "input.ifc", "file": model, "recipe": "UnsharePsets", "arguments": ["IfcWall"]})
        """
        self.src = src
        self.file = file
        self.logger = logger
        self.query = query

    def patch(self):
        filtered_elements: set[ifcopenshell.entity_instance] = set()
        if self.query:
            filtered_elements = ifcopenshell.util.selector.filter_elements(self.file, self.query)

        all_psets = self.file.by_type("IfcPropertySetDefinition")
        psets: dict[ifcopenshell.entity_instance, set[ifcopenshell.entity_instance]] = {}
        for pset in all_psets:
            elements = ifcopenshell.util.element.get_elements_by_pset(pset)
            # Skip non shared psets.
            if len(elements) < 2:
                continue
            # Skip non selected elements.
            if self.query:
                if not any(e in filtered_elements for e in elements):
                    continue
                elements = elements.intersection(filtered_elements)
            psets[pset] = elements

        new_psets = []
        for pset, elements in psets.items():
            # Let the first element to keep the original property set.
            elements = list(elements)
            new_psets.extend(ifcopenshell.api.pset.unshare_pset(self.file, elements, pset))

        print(f"{len(new_psets)} new psets were created.")
