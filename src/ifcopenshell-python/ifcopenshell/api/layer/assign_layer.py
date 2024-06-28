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


def assign_layer(
    file: ifcopenshell.file, items: list[ifcopenshell.entity_instance], layer: ifcopenshell.entity_instance
) -> None:
    """Assigns representation items to a layer

    In IFC, instead of objects being assigned to layers, representation
    items are assigned to layers. Representation items are portions of the
    object's representation. For example, this allows a single IFC Window
    element to have portions of its 2D linework (e.g. the cross section of
    its frame) assigned to one layer, and another portion (e.g. the glazing
    panels) assigned to another layer.

    :param items: The list of IfcRepresentationItems to assign to the layer. This
        should be the items from the object's IfcShapeRepresentation.
    :type items: list[ifcopenshell.entity_instance]
    :param layer: The IfcPresentationLayerAssignment layer to assign the
        item to.
    :type layer: ifcopenshell.entity_instance
    :return: None
    :rtype: None

    Example:

    .. code:: python

        # Remember, all geometry needs to specify the context it is part of first.
        # See ifcopenshell.api.context.add_context for details.
        model = ifcopenshell.api.context.add_context(model, context_type="Model")
        body = ifcopenshell.api.context.add_context(model,
            context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=model
        )

        wall = ifcopenshell.api.root.create_entity(model, ifc_class="IfcWall")
        representation = ifcopenshell.api.geometry.add_wall_representation(model,
            context=body, length=5, height=3, thickness=0.2)
        ifcopenshell.api.geometry.assign_representation(model,
            product=wall, representation=representation)
        ifcopenshell.api.geometry.edit_object_placement(model, product=wall)

        # Now let's create a layer that contains walls
        layer = ifcopenshell.api.layer.add_layer(model, name="AI-WALL")

        # And assign our wall representation item (in this example, there is
        # only one item) to the layer.
        ifcopenshell.api.layer.assign_layer(model, items=[representation.Items[0]], layer=layer)
    """
    settings = {
        "items": items,
        "layer": layer,
    }

    # support AssignedItems == None since layer might just got created
    layer = settings["layer"]
    assigned_items = set(layer.AssignedItems or [])
    items = set(settings["items"])
    if items.issubset(assigned_items):
        return
    layer.AssignedItems = list(assigned_items | items)
