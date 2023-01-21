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


class Usecase:
    def __init__(self, file, element=None):
        """Remove a filling relationship

        If an element is filling an opening, this removes the relationship such
        that the opening and element both still exist, but the element no longer
        fills the opening.

        :param element: The element filling an opening.
        :type element: ifcopenshell.entity_instance.entity_instance
        :return: None
        :rtype: None

        Example:

        .. code:: python

            # Create a wall
            wall = ifcopenshell.api.run("root.create_entity", model, ifc_class="IfcWall")

            # Create an opening, such as for a service penetration with fire and
            # acoustic requirements.
            opening = ifcopenshell.api.run("root.create_entity", model, ifc_class="IfcOpeningElement")

            # Create a door
            door = ifcopenshell.api.run("root.create_entity", model, ifc_class="IfcDoor")

            # The door will now fill the opening.
            ifcopenshell.api.run("void.add_filling", model, opening=opening, element=door)

            # Not anymore!
            ifcopenshell.api.run("void.remove_filling", model, element=door)
        """
        self.file = file
        self.settings = {"element": element}

    def execute(self):
        for rel in self.file.by_type("IfcRelFillsElement"):
            if rel.RelatedBuildingElement == self.settings["element"]:
                self.file.remove(rel)
                break
