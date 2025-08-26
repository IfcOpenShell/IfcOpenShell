# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2021-2022 Dion Moult <dion@thinkmoult.com>, Yassine Oualid <yassine@sigmadimensions.com>
#
# This self.file is part of IfcOpenShell.
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
import ifcopenshell.guid
import ifcopenshell.api.nest
import ifcopenshell.api.owner
import ifcopenshell.api.sequence
import ifcopenshell.util.date
import ifcopenshell.util.element


# TODO: inconsistent name with other copy_xxx api methods.
def duplicate_task(
    file: ifcopenshell.file, task: ifcopenshell.entity_instance
) -> tuple[list[ifcopenshell.entity_instance], list[ifcopenshell.entity_instance]]:
    """Duplicates a task in the project

    The following relationships are also duplicated:

    * The copy will have the same attributes and property sets as the original task
    * The copy will be assigned to the parent task or work schedule
    * The copy will have duplicated nested tasks

    :param task: The task to be duplicated
    :return: A tuple that consists of two lists of tasks:

        - Original task and it's nested tasks.
        - Their corresponding duplicated tasks.

    Example:
    .. code:: python

        # We have a task
        original_task = ifcopenshell.api.sequence.add_task(
            model, work_schedule=work_schedule,
            name="Design new feature",
        )

        # And now we have two
        original_tasks, duplicated_tasks = ifcopenshell.api.sequence.duplicate_task(original_task)
        print(duplicated_tasks[0])  # A copy of ``original_task``.
    """
    usecase = Usecase()
    usecase.file = file
    return usecase.execute(task)


class Usecase:
    file: ifcopenshell.file
    current: list[ifcopenshell.entity_instance]
    duplicate: list[ifcopenshell.entity_instance]

    def execute(
        self, task: ifcopenshell.entity_instance
    ) -> tuple[list[ifcopenshell.entity_instance], list[ifcopenshell.entity_instance]]:
        self.current = []
        self.duplicate = []
        self.duplicate_task(task)
        self.copy_sequence_relationship()
        return self.current, self.duplicate

    def duplicate_task(self, task: ifcopenshell.entity_instance) -> ifcopenshell.entity_instance:
        new_task = ifcopenshell.util.element.copy_deep(self.file, task)
        self.current.append(task)
        self.duplicate.append(new_task)
        self.copy_indirect_attributes(task, new_task)
        return new_task

    def copy_indirect_attributes(
        self, from_element: ifcopenshell.entity_instance, to_element: ifcopenshell.entity_instance
    ) -> None:
        for inverse in self.file.get_inverse(from_element):
            if inverse.is_a("IfcRelDefinesByProperties"):
                inverse = ifcopenshell.util.element.copy(self.file, inverse)
                inverse.RelatedObjects = [to_element]
                pset = ifcopenshell.util.element.copy_deep(self.file, inverse.RelatingPropertyDefinition)
                inverse.RelatingPropertyDefinition = pset
            elif inverse.is_a("IfcRelNests") and inverse.RelatingObject == from_element:
                nested_tasks = [e for e in inverse.RelatedObjects]
                if nested_tasks:
                    new_tasks = []
                    for t in nested_tasks:
                        new_task = self.duplicate_task(t)
                        new_tasks.append(new_task)
                    inverse = ifcopenshell.util.element.copy(self.file, inverse)
                    inverse.RelatingObject = to_element
                    inverse.RelatedObjects = new_tasks
                    ifcopenshell.api.nest.unassign_object(self.file, related_objects=new_tasks)
                    ifcopenshell.api.nest.assign_object(
                        self.file,
                        related_objects=new_tasks,
                        relating_object=to_element,
                    )

            elif inverse.is_a("IfcRelSequence") and (
                inverse.RelatingProcess == from_element or inverse.RelatedProcess == from_element
            ):
                continue
            elif inverse.is_a("IfcRelAssignsToControl") and inverse.RelatingControl.is_a("IfcWorkSchedule"):
                continue
            elif inverse.is_a("IfcRelDefinesByObject"):
                continue
            else:
                for i, value in enumerate(inverse):
                    if value == from_element:
                        new_inverse = ifcopenshell.util.element.copy(self.file, inverse)
                        new_inverse[i] = to_element
                    elif isinstance(value, (tuple, list)) and from_element in value:
                        new_value = list(value)
                        new_value.append(to_element)
                        inverse[i] = new_value

    def copy_sequence_relationship(self) -> None:
        original_tasks = self.current
        duplicated_tasks = self.duplicate
        for i, original_task in enumerate(original_tasks):
            for inverse in self.file.get_inverse(original_task):
                if inverse.is_a("IfcRelSequence") and (
                    inverse.RelatingProcess == original_task or inverse.RelatedProcess == original_task
                ):
                    original_task_index = original_tasks.index(original_task)
                    duplicated_task = duplicated_tasks[original_task_index]
                    relating_process, related_process = None, None
                    if inverse.RelatingProcess == original_task:
                        relating_process = duplicated_task
                    else:
                        related_process = duplicated_task
                    if inverse.RelatedProcess in original_tasks:
                        related_process_index = original_tasks.index(inverse.RelatedProcess)
                        related_process = duplicated_tasks[related_process_index]
                    else:  # thus the related process is not part of the duplicated tasks
                        related_process = inverse.RelatedProcess
                    if inverse.RelatingProcess in original_tasks:
                        relating_process_index = original_tasks.index(inverse.RelatingProcess)
                        relating_process = duplicated_tasks[relating_process_index]
                    else:  # thus the relating process is not part of the duplicated tasks
                        relating_process = inverse.RelatingProcess
                    if relating_process and related_process:
                        rel = ifcopenshell.api.sequence.assign_sequence(
                            self.file,
                            relating_process=relating_process,
                            related_process=related_process,
                        )
                        if inverse.TimeLag:
                            ifcopenshell.api.sequence.assign_lag_time(
                                self.file,
                                rel_sequence=rel,
                                lag_value=(
                                    ifcopenshell.util.date.ifc2datetime(inverse.TimeLag.LagValue.wrappedValue)
                                    if inverse.TimeLag.LagValue
                                    else None
                                ),
                                duration_type=inverse.TimeLag.DurationType,
                            )

    def create_object_reference(
        self, relating_object: ifcopenshell.entity_instance, related_object: ifcopenshell.entity_instance
    ) -> ifcopenshell.entity_instance:
        referenced_by = None
        if relating_object.Declares:
            referenced_by = relating_object.Declares[0]
        if referenced_by:
            related_objects = list(referenced_by.RelatedObjects)
            related_objects.append(related_object)
            referenced_by.RelatedObjects = related_objects
            ifcopenshell.api.owner.update_owner_history(self.file, element=referenced_by)
        else:
            referenced_by = self.file.create_entity(
                "IfcRelDefinesByObject",
                **{
                    "GlobalId": ifcopenshell.guid.new(),
                    "OwnerHistory": ifcopenshell.api.owner.create_owner_history(self.file),
                    "RelatedObjects": [related_object],
                    "RelatingObject": relating_object,
                }
            )
        return referenced_by
