# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2021-2022, Dion Moult <dion@thinkmoult.com>, Yassine Oualid <yassine@sigmadimensions.com>
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

import ifcopenshell.api


class Usecase:
    def __init__(self, file, resource=None):
        """Removes a resource and all relationships

        Example:

        .. code:: python

            # Add our own crew
            crew = ifcopenshell.api.run("resource.add_resource", model, ifc_class="IfcCrewResource")

            # Fire our crew
            ifcopenshell.api.run("resource.remove_resource", model, resource=crew)
        """
        self.file = file
        self.settings = {"resource": resource}

    def execute(self):
        # TODO: review deep purge
        for inverse in self.file.get_inverse(self.settings["resource"]):
            if inverse.is_a("IfcRelNests"):
                if inverse.RelatingObject == self.settings["resource"]:
                    for related_object in inverse.RelatedObjects:
                        ifcopenshell.api.run(
                            "resource.remove_resource",
                            self.file,
                            resource=related_object,
                        )
                    self.file.remove(inverse)
            elif inverse.is_a("IfcRelAssignsToControl"):
                if len(inverse.RelatedObjects) == 1:
                    self.file.remove(inverse)
                else:
                    related_objects = list(inverse.RelatedObjects)
                    related_objects.remove(self.settings["resource"])
                    inverse.RelatedObjects = related_objects
            elif inverse.is_a("IfcRelAssignsToResource"):
                if inverse.RelatingResource == self.settings["resource"]:
                    for related_object in inverse.RelatedObjects:
                        ifcopenshell.api.run(
                            "resource.unassign_resource",
                            self.file,
                            related_object=related_object,
                            resource=self.settings["resource"],
                        )
                elif inverse.RelatedObjects == tuple(self.settings["resource"]):
                    self.file.remove(inverse)
        if self.settings["resource"].Usage:
            self.file.remove(self.settings["resource"].Usage)
        if self.settings["resource"].BaseQuantity:
            ifcopenshell.api.run(
                "resource.remove_resource_quantity",
                self.file,
                resource=self.settings["resource"],
            )
        self.file.remove(self.settings["resource"])
