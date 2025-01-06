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
import ifcopenshell.api.sequence
import ifcopenshell.guid


def assign_sequence(
    file: ifcopenshell.file,
    relating_process: ifcopenshell.entity_instance,
    related_process: ifcopenshell.entity_instance,
    sequence_type: str = "FINISH_START",
) -> ifcopenshell.entity_instance:
    """Assign a sequential relationship between tasks

    Tasks in construction sequencing typically have sequence relationships
    between them, indicating that one task must happen after another. This
    is used to automatically compute new start and end dates and cascade
    changes when dates are changed. This is also used to calculate critical
    paths and floats.

    There are four types of sequence relationships, known as finish to
    start, finish to finish, start to start, and start to finish, sometimes
    abbreviated as a (FS, FF, SS, and SF). The most common is the finish to
    start relationship, indicating that the previous task must finish before
    the next task can start.

    You must not create cyclical task sequences. This makes the computer
    unhappy.

    Note that "previous" or "next" does not necessarily mean the task
    chronologically happens before or after. They simply indicate the order
    of the sequence relationship. For this reason, they are often called
    predecessor and successor tasks in the planning profession.

    :param relating_process: The previous / predecessor task.
    :type relating_process: ifcopenshell.entity_instance
    :param related_process: The next / successor task.
    :type related_process: ifcopenshell.entity_instance
    :param sequence_type: Choose from FINISH_START, FINISH_FINISH,
        START_START, or START_FINISH.
    :return: The newly created IfcRelSequence
    :rtype: ifcopenshell.entity_instance

    Example:

    .. code:: python

        # Let's imagine we are creating a construction schedule. All tasks
        # need to be part of a work schedule.
        schedule = ifcopenshell.api.sequence.add_work_schedule(model, name="Construction Schedule A")

        # Let's imagine a root construction task
        construction = ifcopenshell.api.sequence.add_task(model,
            work_schedule=schedule, name="Construction", identification="C")

        # Let's imagine we're doing a typically formwork, reinforcement,
        # pour sequence. Let's start with the formwork. It'll take us 2
        # days.
        formwork = ifcopenshell.api.sequence.add_task(model,
            parent_task=construction, name="Formwork", identification="C.1")
        time = ifcopenshell.api.sequence.add_task_time(model, task=formwork)
        ifcopenshell.api.sequence.edit_task_time(model,
            task_time=time, attributes={"ScheduleStart": "2000-01-01", "ScheduleDuration": "P2D"})

        # Now let's do the reinforcement. It'll take us another 2 days.
        reinforcement = ifcopenshell.api.sequence.add_task(model,
            parent_task=construction, name="Reinforcement", identification="C.2")
        time = ifcopenshell.api.sequence.add_task_time(model, task=reinforcement)
        ifcopenshell.api.sequence.edit_task_time(model,
            task_time=time, attributes={"ScheduleStart": "2000-01-01", "ScheduleDuration": "P2D"})

        # Now the pour it It'll only take 1 day.
        pour = ifcopenshell.api.sequence.add_task(model,
            parent_task=construction, name="Reinforcement", identification="C.3")
        time = ifcopenshell.api.sequence.add_task_time(model, task=pour)
        ifcopenshell.api.sequence.edit_task_time(model,
            task_time=time, attributes={"ScheduleStart": "2000-01-01", "ScheduleDuration": "P1D"})

        # Now let's say the formwork must finish before the reinforcement
        # can start, and the reinforcement must finish before the pour can
        # start. This is a typical finish to start relationship (FS).
        ifcopenshell.api.sequence.assign_sequence(model,
            relating_process=formwork, related_process=reinforcement)
        ifcopenshell.api.sequence.assign_sequence(model,
            relating_process=reinforcement, related_process=pour)

        # Notice how we set all the scheduled start dates arbitrarily at
        # 2000-01-01. This is because we can ask IfcOpenShell to
        # automatically cascade the dates, starting from any task. This will
        # update the reinforcement date to be 2000-01-03 and the pour date
        # to be 2000-01-05.
        ifcopenshell.api.sequence.cascade_schedule(model, task=formwork)
    """
    settings = {
        "relating_process": relating_process,
        "related_process": related_process,
        "sequence_type": sequence_type,
    }

    for rel in settings["related_process"].IsSuccessorFrom or []:
        if rel.RelatingProcess == settings["relating_process"]:
            return rel
    rel = file.create_entity(
        "IfcRelSequence",
        **{
            "GlobalId": ifcopenshell.guid.new(),
            "OwnerHistory": ifcopenshell.api.owner.create_owner_history(file),
            "RelatingProcess": settings["relating_process"],
            "RelatedProcess": settings["related_process"],
            "SequenceType": settings["sequence_type"],
        }
    )
    ifcopenshell.api.sequence.cascade_schedule(file, task=settings["relating_process"])
    return rel
