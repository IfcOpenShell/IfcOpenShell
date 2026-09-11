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
import test.bootstrap


def count_attribute_reads(func):
    """Number of entity attribute reads performed by func."""
    original = ifcopenshell.entity_instance.__getattr__
    reads = 0

    def counting(instance, name):
        nonlocal reads
        reads += 1
        return original(instance, name)

    ifcopenshell.entity_instance.__getattr__ = counting
    try:
        func()
    finally:
        ifcopenshell.entity_instance.__getattr__ = original
    return reads


class TestAssignProduct(test.bootstrap.IFC4):
    def test_assigning_a_product(self):
        wall = self.file.createIfcWall()
        task = self.file.createIfcTask()
        task2 = self.file.createIfcTask()
        ifcopenshell.api.sequence.assign_product(self.file, relating_product=wall, related_object=task)
        assert wall.ReferencedBy[0].RelatedObjects == (task,)
        ifcopenshell.api.sequence.assign_product(self.file, relating_product=wall, related_object=task2)
        assert wall.ReferencedBy[0].RelatedObjects == (task, task2)

    def test_not_assigning_twice(self):
        wall = self.file.createIfcWall()
        task = self.file.createIfcTask()
        rel = ifcopenshell.api.sequence.assign_product(self.file, relating_product=wall, related_object=task)
        again = ifcopenshell.api.sequence.assign_product(self.file, relating_product=wall, related_object=task)
        assert again == rel
        assert wall.ReferencedBy[0].RelatedObjects == (task,)
        assert len(self.file.by_type("IfcRelAssignsToProduct")) == 1

    def test_not_assigning_twice_when_the_task_already_has_other_products(self):
        task = self.file.createIfcTask()
        walls = [self.file.createIfcWall() for _ in range(3)]
        rels = [
            ifcopenshell.api.sequence.assign_product(self.file, relating_product=wall, related_object=task)
            for wall in walls
        ]
        for wall, rel in zip(walls, rels):
            assert (
                ifcopenshell.api.sequence.assign_product(self.file, relating_product=wall, related_object=task) == rel
            )
        assert len(self.file.by_type("IfcRelAssignsToProduct")) == 3
        for wall in walls:
            assert wall.ReferencedBy[0].RelatedObjects == (task,)

    def test_not_assigning_twice_when_the_product_already_has_other_tasks(self):
        wall = self.file.createIfcWall()
        task = self.file.createIfcTask()
        task2 = self.file.createIfcTask()
        rel = ifcopenshell.api.sequence.assign_product(self.file, relating_product=wall, related_object=task)
        assert ifcopenshell.api.sequence.assign_product(self.file, relating_product=wall, related_object=task2) == rel
        assert ifcopenshell.api.sequence.assign_product(self.file, relating_product=wall, related_object=task) == rel
        assert wall.ReferencedBy[0].RelatedObjects == (task, task2)
        assert len(self.file.by_type("IfcRelAssignsToProduct")) == 1

    def test_cost_does_not_grow_with_the_products_already_assigned_to_the_task(self):
        task = self.file.createIfcTask()
        walls = [self.file.createIfcWall() for _ in range(22)]

        def assign(wall):
            return lambda: ifcopenshell.api.sequence.assign_product(
                self.file, relating_product=wall, related_object=task
            )

        for wall in walls[:10]:
            assign(wall)()
        early = count_attribute_reads(assign(walls[10]))
        for wall in walls[11:21]:
            assign(wall)()
        late = count_attribute_reads(assign(walls[21]))
        assert early == late


class TestAssignProductIFC2X3(test.bootstrap.IFC2X3, TestAssignProduct):
    pass
