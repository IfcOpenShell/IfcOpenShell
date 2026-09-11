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

import ifcopenshell.api.sequence
import test.bootstrap
from test.api.sequence.test_assign_product import count_attribute_reads


class TestUnassignProduct(test.bootstrap.IFC4):
    def test_unassigning_a_product(self):
        wall = self.file.createIfcWall()
        task = self.file.createIfcTask()
        ifcopenshell.api.sequence.assign_product(self.file, relating_product=wall, related_object=task)
        ifcopenshell.api.sequence.unassign_product(self.file, relating_product=wall, related_object=task)
        assert len(self.file.by_type("IfcRelAssignsToProduct")) == 0

    def test_unassigning_one_of_many_products_on_the_same_task(self):
        task = self.file.createIfcTask()
        walls = [self.file.createIfcWall() for _ in range(3)]
        for wall in walls:
            ifcopenshell.api.sequence.assign_product(self.file, relating_product=wall, related_object=task)
        ifcopenshell.api.sequence.unassign_product(self.file, relating_product=walls[1], related_object=task)
        assert not walls[1].ReferencedBy
        assert walls[0].ReferencedBy[0].RelatedObjects == (task,)
        assert walls[2].ReferencedBy[0].RelatedObjects == (task,)
        assert len(self.file.by_type("IfcRelAssignsToProduct")) == 2

    def test_unassigning_keeps_the_other_tasks_on_the_product(self):
        wall = self.file.createIfcWall()
        task = self.file.createIfcTask()
        task2 = self.file.createIfcTask()
        ifcopenshell.api.sequence.assign_product(self.file, relating_product=wall, related_object=task)
        ifcopenshell.api.sequence.assign_product(self.file, relating_product=wall, related_object=task2)
        ifcopenshell.api.sequence.unassign_product(self.file, relating_product=wall, related_object=task)
        assert wall.ReferencedBy[0].RelatedObjects == (task2,)
        assert len(self.file.by_type("IfcRelAssignsToProduct")) == 1

    def test_unassigning_an_unassigned_product_does_nothing(self):
        wall = self.file.createIfcWall()
        task = self.file.createIfcTask()
        task2 = self.file.createIfcTask()
        ifcopenshell.api.sequence.assign_product(self.file, relating_product=wall, related_object=task)
        ifcopenshell.api.sequence.unassign_product(self.file, relating_product=wall, related_object=task2)
        assert wall.ReferencedBy[0].RelatedObjects == (task,)

    def test_cost_does_not_grow_with_the_products_assigned_to_the_task(self):
        task = self.file.createIfcTask()
        walls = [self.file.createIfcWall() for _ in range(22)]
        for wall in walls:
            ifcopenshell.api.sequence.assign_product(self.file, relating_product=wall, related_object=task)

        def unassign(wall):
            return lambda: ifcopenshell.api.sequence.unassign_product(
                self.file, relating_product=wall, related_object=task
            )

        late = count_attribute_reads(unassign(walls[21]))
        for wall in walls[11:21]:
            unassign(wall)()
        early = count_attribute_reads(unassign(walls[10]))
        assert early == late


class TestUnassignProductIFC2X3(test.bootstrap.IFC2X3, TestUnassignProduct):
    pass
