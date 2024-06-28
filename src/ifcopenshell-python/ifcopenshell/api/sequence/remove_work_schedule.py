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
import ifcopenshell.api.project
import ifcopenshell.api.sequence
import ifcopenshell.api.aggregate
import ifcopenshell.util.element


def remove_work_schedule(file: ifcopenshell.file, work_schedule: ifcopenshell.entity_instance) -> None:
    """Removes a work schedule

    All tasks in the work schedule are also removed recursively.

    :param work_schedule: The IfcWorkSchedule to remove.
    :type work_schedule: ifcopenshell.entity_instance
    :return: None
    :rtype: None

    Example:

    .. code:: python

        # This will hold all our construction schedules
        work_plan = ifcopenshell.api.sequence.add_work_plan(model, name="Construction")

        # Let's imagine this is one of our schedules in our work plan.
        schedule = ifcopenshell.api.sequence.add_work_schedule(model,
            name="Construction Schedule A", work_plan=work_plan)

        # And remove it immediately
        ifcopenshell.api.sequence.remove_work_schedule(model, work_schedule=schedule)
    """
    settings = {"work_schedule": work_schedule}

    # TODO: do a deep purge
    ifcopenshell.api.project.unassign_declaration(
        file, definitions=[settings["work_schedule"]], relating_context=file.by_type("IfcContext")[0]
    )

    if settings["work_schedule"].Declares:
        for rel in settings["work_schedule"].Declares:
            for work_schedule in rel.RelatedObjects:
                ifcopenshell.api.sequence.remove_work_schedule(file, work_schedule=work_schedule)

    # Unassign from work plans.
    if settings["work_schedule"].Decomposes:
        ifcopenshell.api.aggregate.unassign_object(file, [settings["work_schedule"]])

    for inverse in file.get_inverse(settings["work_schedule"]):
        if inverse.is_a("IfcRelDefinesByObject"):
            if inverse.RelatingObject == settings["work_schedule"] or len(inverse.RelatedObjects) == 1:
                history = inverse.OwnerHistory
                file.remove(inverse)
                if history:
                    ifcopenshell.util.element.remove_deep2(file, history)
            else:
                related_objects = list(inverse.RelatedObjects)
                related_objects.remove(settings["work_schedule"])
                inverse.RelatedObjects = related_objects
        elif inverse.is_a("IfcRelAssignsToControl"):
            [
                ifcopenshell.api.sequence.remove_task(file, task=related_object)
                for related_object in inverse.RelatedObjects
                if related_object.is_a("IfcTask")
            ]

    history = settings["work_schedule"].OwnerHistory
    file.remove(settings["work_schedule"])
    if history:
        ifcopenshell.util.element.remove_deep2(file, history)
