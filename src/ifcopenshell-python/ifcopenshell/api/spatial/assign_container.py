# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of IfcOpenShell.
#
# IfcOpenShell is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcOpenShell is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcOpenShell.  If not, see <http://www.gnu.org/licenses/>.

import ifcopenshell
import ifcopenshell.api
import ifcopenshell.util.placement


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {
            "product": None,
            "relating_structure": None,
        }
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        contained_in_structure = self.settings["product"].ContainedInStructure
        contains_elements = self.settings["relating_structure"].ContainsElements

        if contains_elements and contained_in_structure and contained_in_structure[0] == contains_elements[0]:
            return

        aggregate = ifcopenshell.util.element.get_aggregate(self.settings["product"])
        if aggregate:
            ifcopenshell.api.run(
                "aggregate.unassign_object", self.file, relating_object=aggregate, product=self.settings["product"]
            )

        if contained_in_structure:
            related_elements = list(contained_in_structure[0].RelatedElements)
            related_elements.remove(self.settings["product"])
            if related_elements:
                contained_in_structure[0].RelatedElements = related_elements
                ifcopenshell.api.run("owner.update_owner_history", self.file, **{"element": contained_in_structure[0]})
            else:
                self.file.remove(contained_in_structure[0])

        if contains_elements:
            related_elements = list(contains_elements[0].RelatedElements)
            related_elements.append(self.settings["product"])
            contains_elements[0].RelatedElements = related_elements
            ifcopenshell.api.run("owner.update_owner_history", self.file, **{"element": contains_elements[0]})
        else:
            contains_elements = self.file.create_entity(
                "IfcRelContainedInSpatialStructure",
                **{
                    "GlobalId": ifcopenshell.guid.new(),
                    "OwnerHistory": ifcopenshell.api.run("owner.create_owner_history", self.file),
                    "RelatedElements": [self.settings["product"]],
                    "RelatingStructure": self.settings["relating_structure"],
                }
            )

        placement = getattr(self.settings["product"], "ObjectPlacement", None)
        if placement and placement.is_a("IfcLocalPlacement"):
            ifcopenshell.api.run(
                "geometry.edit_object_placement",
                self.file,
                product=self.settings["product"],
                matrix=ifcopenshell.util.placement.get_local_placement(self.settings["product"].ObjectPlacement),
                is_si=False,
            )

        return contains_elements
