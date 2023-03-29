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


class Usecase:
    def __init__(self, file, relating_product=None, related_object=None):
        """Assigns a product to be produced as a result of a process

        A construction task may result in products (e.g. a wall) being
        constructed. These task "Outputs" are defined in IFC through product
        relationships.

        Not all tasks have Outputs. For example, maintenance tasks will
        typically not have any outputs.

        See ifcopenshell.api.sequence.assign_process for Inputs and other types
        of process relationships that can be described in manufacturing
        process modeling.

        :param relating_product: The IfcProduct that was constructed as a result
            of the task.
        :type relating_product: ifcopenshell.entity_instance.entity_instance
        :param related_object: The IfcProcess (typically IfcTask) of the
            construction task.
        :type related_object: ifcopenshell.entity_instance.entity_instance
        :return: The newly created IfcRelAssignsToProduct relationship
        :rtype: ifcopenshell.entity_instance.entity_instance

        Example:

        .. code:: python

            # Let's imagine we are creating a construction schedule. All tasks
            # need to be part of a work schedule.
            schedule = ifcopenshell.api.run("sequence.add_work_schedule", model, name="Construction Schedule A")

            # Let's create a construction task. Note that the predefined type is
            # important to distinguish types of tasks.
            task = ifcopenshell.api.run("sequence.add_task", model,
                work_schedule=schedule, name="Build wall", identification="A", predefined_type="CONSTRUCTION")

            # Let's say we have a wall somewhere.
            wall = ifcopenshell.api.run("root.create_entity", model, ifc_class="IfcWall")

            # Let's construct that wall!
            ifcopenshell.api.run("sequence.assign_product", relating_product=wall, related_object=task)
        """
        self.file = file
        self.settings = {
            "relating_product": relating_product,
            "related_object": related_object,
        }

    def execute(self):
        if self.settings["related_object"].HasAssignments:
            for assignment in self.settings["related_object"].HasAssignments:
                if (
                    assignment.is_a("IfcRelAssignsToProduct")
                    and assignment.RelatingProduct == self.settings["relating_product"]
                ):
                    return

        referenced_by = None
        if self.settings["relating_product"].ReferencedBy:
            referenced_by = self.settings["relating_product"].ReferencedBy[0]

        if referenced_by:
            related_objects = list(referenced_by.RelatedObjects)
            related_objects.append(self.settings["related_object"])
            referenced_by.RelatedObjects = related_objects
            ifcopenshell.api.run(
                "owner.update_owner_history", self.file, **{"element": referenced_by}
            )
        else:
            referenced_by = self.file.create_entity(
                "IfcRelAssignsToProduct",
                **{
                    "GlobalId": ifcopenshell.guid.new(),
                    "OwnerHistory": ifcopenshell.api.run(
                        "owner.create_owner_history", self.file
                    ),
                    "RelatedObjects": [self.settings["related_object"]],
                    "RelatingProduct": self.settings["relating_product"],
                }
            )
        return referenced_by
