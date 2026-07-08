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


def remove_empty_layers(file: ifcopenshell.file) -> list[ifcopenshell.entity_instance]:
    """Removes presentation layers that have no assigned items

    An ``IfcPresentationLayerAssignment`` requires its ``AssignedItems`` to be
    a set of at least one item (``SET [1:?]``). A layer with no items is
    therefore schema invalid and, being empty, has no effect on the model.
    This can happen when a layer is created but never assigned to any
    representation item, or when it is otherwise left empty.

    :func:`ifcopenshell.api.layer.unassign_layer` already removes a layer as
    soon as its last item is unassigned. This function covers the
    complementary case of a layer that was created empty and never populated,
    so that it never persists as invalid data.

    :param file: The IFC file.
    :return: The list of removed IfcPresentationLayerAssignment elements.

    Example:

    .. code:: python

        # A layer created but never assigned is schema invalid.
        ifcopenshell.api.layer.add_layer(model, name="AI-WALL")

        # Prune it (e.g. right before writing the file to disk).
        ifcopenshell.api.layer.remove_empty_layers(model)
    """
    removed: list[ifcopenshell.entity_instance] = []
    for layer in file.by_type("IfcPresentationLayerAssignment"):
        if not layer.AssignedItems:
            file.remove(layer)
            removed.append(layer)
    return removed
