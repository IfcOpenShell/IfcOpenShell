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


def unassign_sequence(
    file: ifcopenshell.file,
    relating_process: ifcopenshell.entity_instance,
    related_process: ifcopenshell.entity_instance,
) -> None:
    """Removes a sequence relationship between tasks

    :param relating_process: The previous / predecessor task.
    :type relating_process: ifcopenshell.entity_instance
    :param related_process: The next / successor task.
    :type related_process: ifcopenshell.entity_instance
    :return: None
    :rtype: None

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
    settings = {
        "relating_process": relating_process,
        "related_process": related_process,
    }

    for rel in settings["related_process"].IsSuccessorFrom or []:
        if rel.RelatingProcess == settings["relating_process"]:
            history = rel.OwnerHistory
            file.remove(rel)
            if history:
                ifcopenshell.util.element.remove_deep2(file, history)
    ifcopenshell.api.sequence.cascade_schedule(file, task=settings["related_process"])
