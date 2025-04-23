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
import ifcopenshell.guid
from typing import Union


def assign_control(
    file: ifcopenshell.file,
    relating_control: ifcopenshell.entity_instance,
    related_object: ifcopenshell.entity_instance,
) -> Union[ifcopenshell.entity_instance, None]:
    """Assigns a planning control or constraint to an object

    IFC can describe concepts that control other objects. For example, a
    planning calendar controls the availability of working days for
    construction planning. As another example, a cost item might constrain
    or limit the ability to procure and build a product.

    This usecase lets you assign controls following the rules of the IFC
    specification. This is an advanced topic and assumes knowledge of the
    IFC concepts to determine what is allowed to control what. In the
    future, this API will likely be deprecated in favour of multiple usecase
    specific APIs.

    :param relating_control: The IfcControl entity that is creating the
        control or constraint
    :param related_object: The IfcObjectDefinition that is being controlled
    :return: The newly created IfcRelAssignsToControl. If relationship already
        existed before and wasn't changed then returns None.

    Example:

    .. code:: python

        # One common usecase is to assign a calendar to a task
        calendar = ifcopenshell.api.sequence.add_work_calendar(model)
        schedule = ifcopenshell.api.sequence.add_work_schedule(model)
        task = ifcopenshell.api.sequence.add_task(model,
            work_schedule=schedule)

        # All subtasks will inherit this calendar, so assigning a single
        # calendar to the root task effectively defines a "default" calendar
        ifcopenshell.api.control.assign_control(model,
            relating_control=calendar, related_object=task)

        # Another common example might be relating a cost item and a product
        wall = ifcopenshell.api.root.create_entity(model, ifc_class="IfcWall")
        schedule = ifcopenshell.api.cost.add_cost_schedule(model)
        cost_item = ifcopenshell.api.cost.add_cost_item(model,
            cost_schedule=schedule)
        ifcopenshell.api.control.assign_control(model,
            relating_control=cost_item, related_object=wall)
    """
    if related_object.HasAssignments:
        for assignment in related_object.HasAssignments:
            if assignment.is_a("IfcRelAssignsToControl") and assignment.RelatingControl == relating_control:
                return

    controls = None
    if relating_control.Controls:
        controls = relating_control.Controls[0]

    if controls:
        if related_object in controls.RelatedObjects:
            return
        related_objects = set(controls.RelatedObjects)
        related_objects.add(related_object)
        controls.RelatedObjects = list(related_objects)
        ifcopenshell.api.owner.update_owner_history(file, **{"element": controls})
    else:
        controls = file.create_entity(
            "IfcRelAssignsToControl",
            **{
                "GlobalId": ifcopenshell.guid.new(),
                "OwnerHistory": ifcopenshell.api.owner.create_owner_history(file),
                "RelatedObjects": [related_object],
                "RelatingControl": relating_control,
            },
        )
    return controls
