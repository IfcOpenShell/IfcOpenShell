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

import ifcopenshell.api.control
import ifcopenshell.api.root
import ifcopenshell.api.nest
import ifcopenshell
from typing import Optional


def add_task(
    file: ifcopenshell.file,
    work_schedule: Optional[ifcopenshell.entity_instance] = None,
    parent_task: Optional[ifcopenshell.entity_instance] = None,
    name: Optional[str] = None,
    description: Optional[str] = None,
    identification: Optional[str] = None,
    predefined_type: str = "NOTDEFINED",
) -> ifcopenshell.entity_instance:
    """Adds a new task

    Tasks are typically used for two purposes: construction scheduling and
    facility management.

    In construction scheduling, a task represents a job to be done in a work
    schedule. Tasks are organised in a hierarchical manner known as a work
    breakdown structure (WBS) and have lots of sequential relationships
    (e.g. this task must finish before the next task can start) and date
    information (e.g. durations, start dates). This is often represented as
    a gantt chart and used to analyse critical paths to try and reduce
    project time to stay on-time and within budget.

    In facility management, a task represents a maintenance task to maintain
    a piece of equipment. Tasks are broken down into a punch list, or simply
    a bulleted or ordered sequence of tasks to be performed (e.g. turn off
    equipment, check power connection, etc) in order to maintain the
    equipment. Tasks will also typically have recurring scheduled dates in
    line with the maintenance schedule. These maintenance tasks and
    procedures are typically published as part of an operations and
    maintenance manual.

    All tasks must be grouped in a work schedule, either directly as a root
    or top-level task, or indirectly as a child or subtask of a parent task.
    In construction scheduling, tasks may be nested many times to create the
    work breakdown structure, and the "leaf" tasks (i.e. tasks with no more
    subtasks) are considered to be the activities with dates, whereas all
    parent tasks are part of the breakdown structure used for categorisation
    purposes. In facility management, top-level tasks represent the overall
    maintenance job to be performed, and child tasks represent an ordered
    list of things to do for that maintenance. These form a 2-level
    hierarchy. No further child tasks are recommended.

    :param work_schedule: The work schedule to group the task in, if the
        task is to be a top-level or root task. This is mutually exclusive
        with the parent_task parameter.
    :param parent_task: The parent task, if the task is to be a subtask or
        child task. This is mutually exclusive with the work_schedule
        parameter.
    :param name: The name of the task.
    :param description: The description of the task.
    :param identification: The identification code of the task.
    :param predefined_type: The predefined type of the task. Common ones
        include CONSTRUCTION, DEMOLITION, or MAINTENANCE. Consultant the
        IFC documentation for IfcTaskTypeEnum for more information.
    :return: The newly created IfcTask

    Example:

    .. code:: python

        # Let's imagine we are creating a construction schedule. All tasks
        # need to be part of a work schedule.
        schedule = ifcopenshell.api.sequence.add_work_schedule(model, name="Construction Schedule A")

        # Add a root task to represent the design milestones, and major
        # project phases.
        ifcopenshell.api.sequence.add_task(model,
            work_schedule=schedule, name="Milestones", identification="A")
        ifcopenshell.api.sequence.add_task(model,
            work_schedule=schedule, name="Design", identification="B")
        construction = ifcopenshell.api.sequence.add_task(model,
            work_schedule=schedule, name="Construction", identification="C")

        # Let's start creating our work breakdown structure.
        ifcopenshell.api.sequence.add_task(model,
            parent_task=construction, name="Early Works", identification="C1")
        ifcopenshell.api.sequence.add_task(model,
            parent_task=construction, name="Substructure", identification="C2")
        superstructure = ifcopenshell.api.sequence.add_task(model,
            parent_task=construction, name="Superstructure", identification="C3")

        # Notice how the leaf task is the actual activity
        ifcopenshell.api.sequence.add_task(model,
            parent_task=superstructure, name="Ground Floor FRP", identification="C3.1")

        # Let's imagine we are digitising an operations and maintenance
        # manual for the mechanical discipline.
        maintenance = ifcopenshell.api.sequence.add_work_schedule(model, name="Mechanical Maintenance")

        # Imagine we have to clean the condenser coils for a chiller every
        # month. Like the schedule above, to keep things simple we won't
        # show scheduling times and calendars. This root task represents the
        # overall maintenance task.
        cleaning = ifcopenshell.api.sequence.add_task(model,
            work_schedule=maintenance, name="Condenser coil cleaning")

        # These subtasks represent the punch list of maintenance tasks.
        ifcopenshell.api.sequence.add_task(model, parent_task=cleaning, identification="1",
            description="Prior to work, wear safety shoes, gloves, and goggles.")
        ifcopenshell.api.sequence.add_task(model, parent_task=cleaning, identification="2",
            description="Prepare jet pump, screwdriver, hose clamp, and control panel door key.")
        ifcopenshell.api.sequence.add_task(model, parent_task=cleaning, identification="3",
            description="Switch OFF the chiller unit.")
        ifcopenshell.api.sequence.add_task(model, parent_task=cleaning, identification="3",
            description="Open the isolator switch.")
        ifcopenshell.api.sequence.add_task(model, parent_task=cleaning, identification="3",
            description="Setup the water pressure by tapping to a water supply and connecting to a ...")
    """
    task = ifcopenshell.api.root.create_entity(file, ifc_class="IfcTask", name=name, predefined_type=predefined_type)
    if description:
        task.Description = description
    if identification:
        task.Identification = identification
    task.IsMilestone = False
    if work_schedule:
        ifcopenshell.api.control.assign_control(file, work_schedule, [task])
    elif parent_task:
        rel = ifcopenshell.api.nest.assign_object(
            file,
            related_objects=[task],
            relating_object=parent_task,
        )
        if file.schema != "IFC2X3" and parent_task.Identification:
            assert rel
            task.Identification = parent_task.Identification + "." + str(len(rel.RelatedObjects))
    return task
