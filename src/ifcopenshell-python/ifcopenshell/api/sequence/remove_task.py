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
import ifcopenshell.api
import ifcopenshell.util.element


def remove_task(file: ifcopenshell.file, task: ifcopenshell.entity_instance) -> None:
    """Removes a task

    All subtasks are also removed recursively. Any relationships such as
    sequences or controls are also removed.

    :param task: The IfcTask to remove.
    :type task: ifcopenshell.entity_instance
    :return: None
    :rtype: None

    Example:

    .. code:: python

        # Let's imagine we are creating a construction schedule. All tasks
        # need to be part of a work schedule.
        schedule = ifcopenshell.api.run("sequence.add_work_schedule", model, name="Construction Schedule A")

        # Add a root task to represent the design milestones, and major
        # project phases.
        ifcopenshell.api.run("sequence.add_task", model,
            work_schedule=schedule, name="Milestones", identification="A")
        design = ifcopenshell.api.run("sequence.add_task", model,
            work_schedule=schedule, name="Design", identification="B")
        ifcopenshell.api.run("sequence.add_task", model,
            work_schedule=schedule, name="Construction", identification="C")

        # Ah, let's delete the design section, who needs it anyway we'll
        # just fix it on site.
        ifcopenshell.api.run("sequence.remove_task", model, task=design)
    """
    settings = {"task": task}

    # TODO: do a deep purge
    ifcopenshell.api.run(
        "project.unassign_declaration",
        file,
        definitions=[settings["task"]],
        relating_context=file.by_type("IfcContext")[0],
    )
    if settings["task"].TaskTime:
        file.remove(settings["task"].TaskTime)
    for inverse in file.get_inverse(settings["task"]):
        if inverse.is_a("IfcRelSequence"):
            history = inverse.OwnerHistory
            file.remove(inverse)
            if history:
                ifcopenshell.util.element.remove_deep2(file, history)
        elif inverse.is_a("IfcRelNests"):
            if inverse.RelatingObject == settings["task"]:
                for related_object in inverse.RelatedObjects:
                    ifcopenshell.api.run("sequence.remove_task", file, task=related_object)
            elif not inverse.RelatedObjects:
                history = inverse.OwnerHistory
                file.remove(inverse)
                if history:
                    ifcopenshell.util.element.remove_deep2(file, history)
            elif settings["task"] in inverse.RelatedObjects:
                related_objects = list(inverse.RelatedObjects)
                related_objects.remove(settings["task"])
                if not related_objects:
                    file.remove(inverse)
                else:
                    inverse.RelatedObjects = related_objects
        elif inverse.is_a("IfcRelAssignsToControl"):
            if inverse.RelatingControl == settings["task"] or len(inverse.RelatedObjects) == 1:
                history = inverse.OwnerHistory
                file.remove(inverse)
                if history:
                    ifcopenshell.util.element.remove_deep2(file, history)
            else:
                related_objects = list(inverse.RelatedObjects)
                related_objects.remove(settings["task"])
                inverse.RelatedObjects = related_objects
        elif inverse.is_a("IfcRelDefinesByProperties"):
            ifcopenshell.api.run(
                "pset.remove_pset",
                file,
                product=settings["task"],
                pset=inverse.RelatingPropertyDefinition,
            )
        elif inverse.is_a("IfcRelAssignsToProcess"):
            if inverse.RelatingProcess == settings["task"] or len(inverse.RelatedObjects) == 1:
                history = inverse.OwnerHistory
                file.remove(inverse)
                if history:
                    ifcopenshell.util.element.remove_deep2(file, history)
        elif inverse.is_a("IfcRelAssignsToProduct"):
            if inverse.RelatingProduct == settings["task"] or len(inverse.RelatedObjects) == 1:
                history = inverse.OwnerHistory
                file.remove(inverse)
                if history:
                    ifcopenshell.util.element.remove_deep2(file, history)
            else:
                related_objects = list(inverse.RelatedObjects)
                related_objects.remove(settings["task"])
                inverse.RelatedObjects = related_objects
        elif inverse.is_a("IfcRelAssignsToObject"):
            if inverse.RelatingObject == settings["task"] or len(inverse.RelatedObjects) == 1:
                history = inverse.OwnerHistory
                file.remove(inverse)
                if history:
                    ifcopenshell.util.element.remove_deep2(file, history)
            else:
                related_objects = list(inverse.RelatedObjects)
                related_objects.remove(settings["task"])
                inverse.RelatedObjects = related_objects
        elif inverse.is_a("IfcRelAssignsToProcess"):
            history = inverse.OwnerHistory
            file.remove(inverse)
            if history:
                ifcopenshell.util.element.remove_deep2(file, history)

    history = settings["task"].OwnerHistory
    file.remove(settings["task"])
    if history:
        ifcopenshell.util.element.remove_deep2(file, history)
