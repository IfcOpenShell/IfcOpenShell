# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2021-2022 Dion Moult <dion@thinkmoult.com>, Yassine Oualid <yassine@sigmadimensions.com>
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
import ifcopenshell.util.system
import ifcopenshell.util.element


class Usecase:
    def __init__(self, file, work_schedule=None, name=None):
        """Creates a baseline for your Work Schedule

        Using a IfcWorkSchdule having PredefinedType=PLANNED,
        We can create a baseline for our work schedule. This IfcWorkSchedule will have PredefinedType=BASELINE
        and the IfcWorkSchedule.CreationDate indicating the date of the baseline creation, and IfcWorkSchedule.Name indicating the name of the baseline.

        The following relationships are also baselined:

        * Same Tasks & attributes
        * Same Task Relationships
        * Same Construction Resources
        * Same Resource Relationships

        :param work_schedule: The planned work_schedule to baseline
        :type work_schedule: ifcopenshell.entity_instance.entity_instance
        :return: The baseline work_schedule
        :rtype: ifcopenshell.entity_instance.entity_instance

        Example:
        .. code:: python

            # We have a Work Schedule
            planned_work_schedule = WorkSchedule(name="Design new feature",predefinedType="PLANNED", deadline="2023-03-01")

            # And now we have a baseline for our Work Schedule
            baseline_work_schedule = ifcopenshell.api.run("sequence.create_baseline",file, work_schedule= planned_work_schedule, name="Baseline 1")
        """
        self.file = file
        self.settings = {"work_schedule": work_schedule, "name": name}

    def execute(self):
        result = self.create_baseline_work_schedule(self.settings["work_schedule"])
        return result

    def create_baseline_work_schedule(self, work_schedule):
        # create work schedule
        if not work_schedule.PredefinedType == "PLANNED":
            return
        baseline_work_schedule = ifcopenshell.api.run(
            "sequence.add_work_schedule",
            self.file,
            name=work_schedule.Name,
            predefined_type="BASELINE",
        )
        baseline_work_schedule.Name = self.settings["name"]
        self.create_baseline_reference(work_schedule, baseline_work_schedule)
        self.task_tracker = {"current": [], "duplicate": []}
        self.copy_tasks_with_reference(
            work_schedule, baseline_work_schedule
        )  # TODO: Fix task nesting order when duplicating children
        self.copy_sequence_relationship(
            self.task_tracker["current"], self.task_tracker["duplicate"]
        )

    def create_baseline_reference(self, relating_object, related_object):
        referenced_by = None
        if relating_object.Declares:
            referenced_by = relating_object.Declares[0]
        if referenced_by:
            related_objects = list(referenced_by.RelatedObjects)
            related_objects.append(related_object)
            referenced_by.RelatedObjects = related_objects
            ifcopenshell.api.run(
                "owner.update_owner_history", self.file, **{"element": referenced_by}
            )
        else:
            referenced_by = self.file.create_entity(
                "IfcRelDefinesByObject",
                **{
                    "GlobalId": ifcopenshell.guid.new(),
                    "OwnerHistory": ifcopenshell.api.run(
                        "owner.create_owner_history", self.file
                    ),
                    "RelatedObjects": [related_object],
                    "RelatingObject": relating_object,
                }
            )
        return referenced_by

    def copy_tasks_with_reference(self, work_schedule, baseline_work_schedule):
        for task in ifcopenshell.util.sequence.get_root_tasks(work_schedule):
            new_task = self.copy_task(task)
            self.file.create_entity(
                "IfcRelAssignsToControl",
                **{
                    "GlobalId": ifcopenshell.guid.new(),
                    "OwnerHistory": ifcopenshell.api.run(
                        "owner.create_owner_history", self.file
                    ),
                    "RelatedObjects": [new_task],
                    "RelatingControl": baseline_work_schedule,
                }
            )

    def copy_task(self, task):
        new_task = ifcopenshell.util.element.copy_deep(self.file, task)
        self.task_tracker["current"].append(task)
        self.task_tracker["duplicate"].append(new_task)
        self.create_baseline_reference(task, new_task)
        self.copy_indirect_attributes(task, new_task)
        return new_task

    def copy_indirect_attributes(self, from_element, to_element):
        for inverse in self.file.get_inverse(from_element):
            if inverse.is_a("IfcRelDefinesByProperties"):
                inverse = ifcopenshell.util.element.copy(self.file, inverse)
                inverse.RelatedObjects = [to_element]
                pset = ifcopenshell.util.element.copy_deep(
                    self.file, inverse.RelatingPropertyDefinition
                )
                inverse.RelatingPropertyDefinition = pset
            elif inverse.is_a("IfcRelNests") and inverse.RelatingObject == from_element:
                nested_tasks = [e for e in inverse.RelatedObjects]
                if nested_tasks:
                    new_tasks = []
                    for t in nested_tasks:
                        new_task = self.copy_task(t)
                        new_tasks.append(new_task)
                    inverse = ifcopenshell.util.element.copy(self.file, inverse)
                    inverse.RelatingObject = to_element
                    inverse.RelatedObjects = new_tasks
                    for t in new_tasks:
                        ifcopenshell.api.run(
                            "nest.unassign_object", self.file, related_object=t
                        )
                        rel = ifcopenshell.api.run(
                            "nest.assign_object",
                            self.file,
                            related_object=t,
                            relating_object=to_element,
                        )
            elif inverse.is_a("IfcRelSequence") and (
                inverse.RelatingProcess == from_element
                or inverse.RelatedProcess == from_element
            ):
                continue
            elif inverse.is_a(
                "IfcRelAssignsToControl"
            ) and inverse.RelatingControl.is_a("IfcWorkSchedule"):
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

    def copy_sequence_relationship(self, original_tasks, duplicated_tasks):
        for i, original_task in enumerate(original_tasks):
            for inverse in self.file.get_inverse(original_task):
                if inverse.is_a("IfcRelSequence") and (
                    inverse.RelatingProcess == original_task
                    or inverse.RelatedProcess == original_task
                ):
                    original_task_index = original_tasks.index(original_task)
                    duplicated_task = duplicated_tasks[original_task_index]
                    relating_process, related_process = None, None
                    if inverse.RelatingProcess == original_task:
                        relating_process = duplicated_task
                    else:
                        related_process = duplicated_task
                    if inverse.RelatedProcess in original_tasks:
                        related_process_index = original_tasks.index(
                            inverse.RelatedProcess
                        )
                        related_process = duplicated_tasks[related_process_index]
                    if inverse.RelatingProcess in original_tasks:
                        relating_process_index = original_tasks.index(
                            inverse.RelatingProcess
                        )
                        relating_process = duplicated_tasks[relating_process_index]
                    if relating_process and related_process:
                        rel = ifcopenshell.api.run(
                            "sequence.assign_sequence",
                            self.file,
                            relating_process=relating_process,
                            related_process=related_process,
                        )
                        if inverse.TimeLag:
                            ifcopenshell.api.run(
                                "sequence.assign_lag_time",
                                self.file,
                                sequence=rel,
                                lag_time=inverse.TimeLag.LagValue,
                                duration_type=inverse.TimeLag.DurationType,
                            )
