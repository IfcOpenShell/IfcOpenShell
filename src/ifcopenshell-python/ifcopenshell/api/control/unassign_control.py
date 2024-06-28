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
import ifcopenshell.api.owner
import ifcopenshell.util.element
from typing import Union


def unassign_control(
    file: ifcopenshell.file,
    relating_control: ifcopenshell.entity_instance,
    related_object: ifcopenshell.entity_instance,
) -> Union[ifcopenshell.entity_instance, None]:
    """Unassigns a planning control or constraint to an object

    :param relating_control: The IfcControl entity that is creating the
        control or constraint
    :type relating_control: ifcopenshell.entity_instance
    :param related_object: The IfcObjectDefinition that is being controlled
    :type related_object: ifcopenshell.entity_instance
    :return: If the control still is related to other objects, the
        IfcRelAssignsToControl is returned, otherwise None.
    :rtype: ifcopenshell.entity_instance, None

    Example:

    .. code:: python

        # Let's relate a cost item and a product
        wall = ifcopenshell.api.root.create_entity(model, ifc_class="IfcWall")
        schedule = ifcopenshell.api.cost.add_cost_schedule(model)
        cost_item = ifcopenshell.api.cost.add_cost_item(model,
            cost_schedule=schedule)
        ifcopenshell.api.control.assign_control(model,
            relating_control=cost_item, related_object=wall)

        # And now let's change our mind
        ifcopenshell.api.control.unassign_control(model,
            relating_control=cost_item, related_object=wall)
    """

    settings = {
        "relating_control": relating_control,
        "related_object": related_object,
    }

    for rel in settings["related_object"].HasAssignments or []:
        if not rel.is_a("IfcRelAssignsToControl") or rel.RelatingControl != settings["relating_control"]:
            continue
        if len(rel.RelatedObjects) == 1:
            history = rel.OwnerHistory
            file.remove(rel)
            if history:
                ifcopenshell.util.element.remove_deep2(file, history)
            return
        related_objects = list(rel.RelatedObjects)
        related_objects.remove(settings["related_object"])
        rel.RelatedObjects = related_objects
        ifcopenshell.api.owner.update_owner_history(file, **{"element": rel})
        return rel
