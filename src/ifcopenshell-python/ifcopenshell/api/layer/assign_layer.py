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
    def __init__(self, file, item=None, layer=None):
        """Assigns a representation item to a layer

        In IFC, instead of objects being assigned to layers, representation
        items are assigned to layers. Representation items are portions of the
        object's representation. For example, this allows a single IFC Window
        element to have portions of its 2D linework (e.g. the cross section of
        its frame) assigned to one layer, and another portion (e.g. the glazing
        panels) assigned to another layer.

        :param item: The IfcRepresentationItem to assign to the layer. This
            should be one of the items in the object's IfcShapeRepresentation.
        :type item: ifcopenshell.entity_instance.entity_instance
        :param layer: The IfcPresentationLayerAssignment layer to assign the
            item to.
        :type layer: ifcopenshell.entity_instance.entity_instance
        :return: None
        :rtype: None

        Example:

        .. code:: python

            # Remember, all geometry needs to specify the context it is part of first.
            # See ifcopenshell.api.context.add_context for details.
            model = ifcopenshell.api.run("context.add_context", model, context_type="Model")
            body = ifcopenshell.api.run("context.add_context", model,
                context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=model
            )

            wall = ifcopenshell.api.run("root.create_entity", model, ifc_class="IfcWall")
            representation = ifcopenshell.api.run("geometry.add_wall_representation", model,
                context=body, length=5, height=3, thickness=0.2)
            ifcopenshell.api.run("geometry.assign_representation", model,
                product=wall, representation=representation)
            ifcopenshell.api.run("geometry.edit_object_placement", model, product=wall)

            # Now let's create a layer that contains walls
            layer = ifcopenshell.api.run("layer.add_layer", model, Name="AI-WALL")

            # And assign our wall representation item (in this example, there is
            # only one item) to the layer.
            ifcopenshell.api.run("layer.assign_layer", model, item=representation.Items[0], layer=layer)
        """
        self.file = file
        self.settings = {
            "item": item,
            "layer": layer,
        }

    def execute(self):
        assigned_items = set(self.settings["layer"].AssignedItems or [])
        assigned_items.add(self.settings["item"])
        self.settings["layer"].AssignedItems = list(assigned_items)
