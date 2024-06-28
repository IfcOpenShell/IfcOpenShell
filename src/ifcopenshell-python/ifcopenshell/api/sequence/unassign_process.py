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


def unassign_process(
    file: ifcopenshell.file,
    relating_process: ifcopenshell.entity_instance,
    related_object: ifcopenshell.entity_instance,
) -> None:
    """Unassigns a process and object relationship

    See ifcopenshell.api.sequence.assign_process for details.

    :param relating_process: The IfcTask in the relationship.
    :type relating_process: ifcopenshell.entity_instance
    :param related_object: The related object.
    :type related_object: ifcopenshell.entity_instance
    :return: None
    :rtype: None

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

        # Change our mind.
        ifcopenshell.api.sequence.unassign_process(model, relating_process=task, related_object=wall)
    """
    settings = {
        "relating_process": relating_process,
        "related_object": related_object,
    }

    for rel in settings["related_object"].HasAssignments or []:
        if not rel.is_a("IfcRelAssignsToProcess") or rel.RelatingProcess != settings["relating_process"]:
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
        ifcopenshell.api.owner.update_owner_history(file, element=rel)
        return rel
