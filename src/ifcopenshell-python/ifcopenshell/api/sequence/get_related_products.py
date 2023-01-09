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


class Usecase:
    def __init__(self, file, relating_product=None, related_object=None):
        """Gets the related products being output by a task

        This API function will be removed in the future and migrated to a
        utility module.

        :param relating_product: One of the products already output by the task.
        :type relating_product: ifcopenshell.entity_instance.entity_instance
        :param related_object: The IfcTask that you want to get all the related
            products for.
        :type related_object: ifcopenshell.entity_instance.entity_instance
        :return: A set of IfcProducts output by the IfcTask.
        :rtype: set[ifcopenshell.entity_instance.entity_instance]

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

            # This will give us a set with that wall in it.
            products = ifcopenshell.api.run("sequence.get_related_products", model, related_object=task)
        """
        self.file = file
        self.settings = {
            "relating_product": relating_product,
            "related_object": related_object,
        }

    def execute(self):
        products = set()
        related_object = None
        if self.settings["related_object"]:
            related_object = self.settings["related_object"]
        elif self.settings["relating_product"]:
            for reference in self.settings["relating_product"].ReferencedBy:
                if reference.is_a("IfcRelAssignsToProduct"):
                    related_object = referenced_by.RelatedObjects[0]
        if related_object:
            assignments = self.settings["related_object"].HasAssignments
            for assignment in assignments:
                if assignment.is_a("IfcRelAssignsToProduct"):
                    products.add(assignment.RelatingProduct.id())
        return products
