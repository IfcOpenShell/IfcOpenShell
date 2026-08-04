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
import ifcopenshell.api.sequence
import ifcopenshell.util.element
from typing import Optional


def unassign_sequence(
    file: ifcopenshell.file,
    relating_process: ifcopenshell.entity_instance,
    related_process: ifcopenshell.entity_instance,
    sequence_type: Optional[str] = None,
) -> None:
    """Removes a sequence relationship between tasks

    Two tasks may be sequenced more than once with different types — see
    :func:`ifcopenshell.api.sequence.assign_sequence` — so removing "the"
    relationship between a pair is ambiguous. Left unspecified, every sequence
    between the two is removed, which is what "make them unrelated" means and
    what this did before the parameter existed. Name a type to remove only that
    one and leave any others in place.

    :param relating_process: The previous / predecessor task.
    :param related_process: The next / successor task.
    :param sequence_type: Optionally, remove only the sequence of this type.
        Choose from FINISH_START, FINISH_FINISH, START_START, or START_FINISH.
    :return: None

    Example:

    .. code:: python

        # Let's imagine we are creating a construction schedule. All tasks
        # need to be part of a work schedule.
        schedule = ifcopenshell.api.sequence.add_work_schedule(model, name="Construction Schedule A")

        # Let's imagine a root construction task
        construction = ifcopenshell.api.sequence.add_task(model,
            work_schedule=schedule, name="Construction", identification="C")

        # Let's imagine we're building 2 zones, one after another.
        zone1 = ifcopenshell.api.sequence.add_task(model,
            parent_task=construction, name="Zone 1", identification="C.1")
        zone2 = ifcopenshell.api.sequence.add_task(model,
            parent_task=construction, name="Zone 2", identification="C.2")

        # Zone 1 finishes, then zone 2 starts.
        ifcopenshell.api.sequence.assign_sequence(model, relating_process=zone1, related_process=zone2)

        # Let's make them unrelated
        ifcopenshell.api.sequence.unassign_sequence(model,
            relating_process=zone1, related_process=zone2)
    """
    for rel in related_process.IsSuccessorFrom or []:
        if rel.RelatingProcess != relating_process:
            continue
        if sequence_type is not None and rel.SequenceType != sequence_type:
            continue
        history = rel.OwnerHistory
        file.remove(rel)
        if history:
            ifcopenshell.util.element.remove_deep2(file, history)
    ifcopenshell.api.sequence.cascade_schedule(file, task=related_process)
