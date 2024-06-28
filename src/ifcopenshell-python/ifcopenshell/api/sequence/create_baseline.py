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
import ifcopenshell.api.owner
import ifcopenshell.api.control
import ifcopenshell.api.sequence
import ifcopenshell.guid
import ifcopenshell.util.element
import ifcopenshell.util.sequence
import ifcopenshell.util.system
from typing import Optional


def create_baseline(
    file: ifcopenshell.file, work_schedule: ifcopenshell.entity_instance, name: Optional[str] = None
) -> None:
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
    :type work_schedule: ifcopenshell.entity_instance
    :param name: baseline work schedule name
    :type name: str, optional
    :return: The baseline work_schedule
    :rtype: ifcopenshell.entity_instance

    Example:

    .. code:: python

        # We have a Work Schedule
        planned_work_schedule = WorkSchedule(name="Design new feature",predefinedType="PLANNED", deadline="2023-03-01")

        # And now we have a baseline for our Work Schedule
        baseline_work_schedule = ifcopenshell.api.sequence.create_baseline(file, work_schedule=planned_work_schedule, name="Baseline 1")
    """
    usecase = Usecase()
    usecase.file = file
    usecase.settings = {"work_schedule": work_schedule, "name": name}
    return usecase.execute()


class Usecase:
    def execute(self):
        result = self.create_baseline_work_schedule(self.settings["work_schedule"])
        return result

    def create_baseline_work_schedule(self, work_schedule):
        # create work schedule
        if not work_schedule.PredefinedType == "PLANNED":
            return
        baseline_work_schedule = ifcopenshell.api.sequence.add_work_schedule(
            self.file, name=work_schedule.Name, predefined_type="BASELINE"
        )
        baseline_work_schedule.Name = self.settings["name"]
        self.create_baseline_reference(work_schedule, baseline_work_schedule)
        for summary_task in ifcopenshell.util.sequence.get_root_tasks(work_schedule):
            current, duplicate = ifcopenshell.api.sequence.duplicate_task(self.file, task=summary_task)
            ifcopenshell.api.control.assign_control(
                self.file, relating_control=baseline_work_schedule, related_object=duplicate[0]
            )
            for i, task in enumerate(current):
                self.create_baseline_reference(task, duplicate[i])

    def create_baseline_reference(self, relating_object, related_object):
        referenced_by = None
        if relating_object.Declares:
            referenced_by = relating_object.Declares[0]
        if referenced_by:
            related_objects = list(referenced_by.RelatedObjects)
            related_objects.append(related_object)
            referenced_by.RelatedObjects = related_objects
            ifcopenshell.api.owner.update_owner_history(self.file, **{"element": referenced_by})
        else:
            referenced_by = self.file.create_entity(
                "IfcRelDefinesByObject",
                GlobalId=ifcopenshell.guid.new(),
                OwnerHistory=ifcopenshell.api.owner.create_owner_history(self.file),
                RelatedObjects=[related_object],
                RelatingObject=relating_object,
            )
        return referenced_by
