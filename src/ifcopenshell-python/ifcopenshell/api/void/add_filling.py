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


class Usecase:
    def __init__(self, file, opening=None, element=None):
        """Fill an opening with an element

        Physical elements may have openings in them. For example, a wall might
        have an opening for a door. That opening is then filled by the door.
        This indicates that when the door moves, the opening will move with it.
        Or if the door is removed, then the opening may remain and need to be
        filled.

        :param opening: The IfcOpeningElement to fill with the element.
        :type opening: ifcopenshell.entity_instance.entity_instance
        :param element: The IfcElement to be inserted into the opening.
        :type element: ifcopenshell.entity_instance.entity_instance
        :return: The new IfcRelFillsElement relationship
        :rtype: ifcopenshell.entity_instance.entity_instance

        Example:

        .. code:: python

            # A bit of preparation, let's create some geometric contexts since
            # we want to create some geometry for our wall and opening.
            model3d = ifcopenshell.api.run("context.add_context", model, context_type="Model")
            body = ifcopenshell.api.run("context.add_context", model,
                context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=model3d)

            # Create a wall
            wall = ifcopenshell.api.run("root.create_entity", model, ifc_class="IfcWall")

            # Let's use the "3D Body" representation we created earlier to add a
            # new wall-like body geometry, 5 meters long, 3 meters high, and
            # 200mm thick
            representation = ifcopenshell.api.run("geometry.add_wall_representation", model,
                context=body, length=5, height=3, thickness=0.2)
            ifcopenshell.api.run("geometry.assign_representation", model,
                product=wall, representation=representation)

            # Place our wall at the origin
            ifcopenshell.api.run("geometry.edit_object_placement", model, product=wall)

            # Create an opening, such as for a service penetration with fire and
            # acoustic requirements.
            opening = ifcopenshell.api.run("root.create_entity", model, ifc_class="IfcOpeningElement")

            # Let's create an opening representation of a 950mm x 2100mm door.
            # Notice how the thickness is greater than the wall thickness, this
            # helps resolve floating point resolution errors in 3D.
            representation = ifcopenshell.api.run("geometry.add_wall_representation", model,
                context=body, length=.95, height=2.1, thickness=0.4)
            ifcopenshell.api.run("geometry.assign_representation", model,
                product=opening, representation=representation)

            # Let's shift our door 1 meter along the wall and 100mm along the
            # wall, to create a nice overlap for the opening boolean.
            matrix = np.identity(4)
            matrix[:,3] = [1, -.1, 0, 0]
            ifcopenshell.api.run("geometry.edit_object_placement", model, product=opening, matrix=matrix)

            # The opening will now void the wall.
            ifcopenshell.api.run("void.add_opening", model, opening=opening, element=wall)

            # Create a door
            door = ifcopenshell.api.run("root.create_entity", model, ifc_class="IfcDoor")

            # Let's create a door representation of a 950mm x 2100mm door.
            representation = ifcopenshell.api.run("geometry.add_wall_representation", model,
                context=body, length=.95, height=2.1, thickness=0.05)
            ifcopenshell.api.run("geometry.assign_representation", model,
                product=door, representation=representation)

            # Let's shift our door 1 meter along the wall and 100mm along the
            # wall, which lines up with our opening.
            matrix = np.identity(4)
            matrix[:,3] = [1, .05, 0, 0]
            ifcopenshell.api.run("geometry.edit_object_placement", model, product=door, matrix=matrix)

            # The door will now fill the opening.
            ifcopenshell.api.run("void.add_filling", model, opening=opening, element=door)
        """
        self.file = file
        self.settings = {"opening": opening, "element": element}

    def execute(self):
        fills_voids = self.settings["element"].FillsVoids

        if fills_voids:
            if fills_voids[0].RelatingOpeningElement == self.settings["opening"]:
                return
            self.file.remove(fills_voids[0])

        self.file.create_entity(
            "IfcRelFillsElement",
            **{
                "GlobalId": ifcopenshell.guid.new(),
                "RelatingOpeningElement": self.settings["opening"],
                "RelatedBuildingElement": self.settings["element"],
            }
        )
