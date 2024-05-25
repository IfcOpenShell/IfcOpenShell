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
import ifcopenshell.util.element


def unassign_layer(
    file: ifcopenshell.file, items: list[ifcopenshell.entity_instance], layer: ifcopenshell.entity_instance
) -> None:
    """Unassigns representation items from a layer

    If the representation item isn't assigned to the layer, nothing will
    happen.
    If after unassignment layer won't have any assigned items it will be
    removed to keep IFC valid.

    :param items: A list IfcRepresentationItem elements to unassign
    :type items: list[ifcopenshell.entity_instance]
    :param layer: The IfcPresentationLayerAssignment to unassign from
    :type layer: ifcopenshell.entity_instance
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
        layer = ifcopenshell.api.run("layer.add_layer", model, name="AI-WALL")

        # And assign our wall representation item (in this example, there is
        # only one item) to the layer.
        ifcopenshell.api.run("layer.assign_layer", model, items=[representation.Items[0]], layer=layer)

        # Let's undo it!
        ifcopenshell.api.run("layer.unassign_layer", model, items=[representation.Items[0]], layer=layer)
    """
    settings = {
        "items": items,
        "layer": layer,
    }

    layer = settings["layer"]
    assigned_items = set(layer.AssignedItems) or set()
    items = set(settings["items"])
    if not items.issubset(assigned_items):
        return
    assigned_items = list(assigned_items - items)

    # keep IFC valid in case if there are no items left
    if assigned_items:
        layer.AssignedItems = assigned_items
    else:
        file.remove(layer)
