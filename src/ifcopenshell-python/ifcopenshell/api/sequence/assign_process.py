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


def assign_process(
    file: ifcopenshell.file,
    relating_process: ifcopenshell.entity_instance,
    related_object: ifcopenshell.entity_instance,
) -> ifcopenshell.entity_instance:
    """Assigns an object to be related to a process, typically a construction task

    Processes work using the ICOM (Input, Controls, Outputs, Mechanisms)
    paradigm in IFC. This process model is commonly used in modeling
    manufacturing functions.

    For example, processes (such as tasks) consume Inputs and transform them
    into Outputs. The process may only occur within the limits of Controls
    (e.g. cost items) and may require Mechanisms (ISO9000 calls them
    Mechanisms, whereas IFC calls them resources, such as raw materials,
    labour, or equipment).

                  +----------+
                  | Controls |
                  +----------+
                        |
                        V
    +--------+     +---------+     +---------+
    | Inputs | --> | Process | --> | Outputs |
    +--------+     +---------+     +---------+
                        ^
                        |
                  +-----------+
                  | Resources |
                  +-----------+

    There are three main scenarios where an object may be related to a
    task: defining inputs, controls, and resources of a process.

    For inputs, a product (i.e. wall) may be defined as an input to a task,
    such as when the task is to demolish the wall (i.e. the wall is an
    input, and there is no output).

    For controls, a cost item may be defined as a control to a task.

    For resources, any construction resource may be assigned to a task.

    :param relating_process: The IfcProcess (typically IfcTask) that the
        input, control, or resource is related to.
    :type relating_process: ifcopenshell.entity_instance
    :param related_object: The IfcProduct (for input), IfcCostItem (for
        control) or IfcConstructionResource (for resource).
    :type related_object: ifcopenshell.entity_instance
    :return: The newly created IfcRelAssignsToProcess relationship
    :rtype: ifcopenshell.entity_instance

    Example:

    .. code:: python

        # Let's imagine we are creating a construction schedule. All tasks
        # need to be part of a work schedule.
        schedule = ifcopenshell.api.sequence.add_work_schedule(model, name="Construction Schedule A")

        # Let's create a construction task. Note that the predefined type is
        # important to distinguish types of tasks.
        task = ifcopenshell.api.sequence.add_task(model,
            work_schedule=schedule, name="Demolish existing", identification="A", predefined_type="DEMOLITION")

        # Let's say we have a wall somewhere.
        wall = ifcopenshell.api.root.create_entity(model, ifc_class="IfcWall")

        # Let's demolish that wall!
        ifcopenshell.api.sequence.assign_process(model, relating_process=task, related_object=wall)
    """
    settings = {
        "relating_process": relating_process,
        "related_object": related_object,
    }

    if settings["related_object"].HasAssignments:
        for assignment in settings["related_object"].HasAssignments:
            if assignment.is_a("IfcRelAssignsToProcess") and assignment.RelatingProcess == settings["relating_process"]:
                return

    operates_on = None
    if settings["relating_process"].OperatesOn:
        operates_on = settings["relating_process"].OperatesOn[0]

    if operates_on:
        related_objects = list(operates_on.RelatedObjects)
        related_objects.append(settings["related_object"])
        operates_on.RelatedObjects = related_objects
        ifcopenshell.api.owner.update_owner_history(file, **{"element": operates_on})
    else:
        operates_on = file.create_entity(
            "IfcRelAssignsToProcess",
            **{
                "GlobalId": ifcopenshell.guid.new(),
                "OwnerHistory": ifcopenshell.api.owner.create_owner_history(file),
                "RelatedObjects": [settings["related_object"]],
                "RelatingProcess": settings["relating_process"],
            }
        )
    return operates_on
