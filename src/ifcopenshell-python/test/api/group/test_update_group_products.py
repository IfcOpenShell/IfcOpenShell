# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2022 Dion Moult <dion@thinkmoult.com>
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

import ifcopenshell.api.group
import ifcopenshell.api.root
import ifcopenshell.util.element
import test.bootstrap


class TestUpdateGroupProductsIFC2X3(test.bootstrap.IFC2X3):
    def test_update_group_without_products(self):
        elements = [ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall") for i in range(4)]
        group = ifcopenshell.api.group.add_group(self.file)
        ifcopenshell.api.group.update_group_products(self.file, products=elements, group=group)
        assert set(ifcopenshell.util.element.get_grouped_by(group)) == set(elements)

    def test_update_group_with_no_existing_rel_and_empty_products_creates_nothing(self):
        group = ifcopenshell.api.group.add_group(self.file)
        result = ifcopenshell.api.group.update_group_products(self.file, products=[], group=group)
        assert result is None
        assert not self.file.by_type("IfcRelAssignsToGroup")

    def test_update_group_to_empty_removes_the_relationship(self):
        elements = [ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall") for i in range(2)]
        group = ifcopenshell.api.group.add_group(self.file)
        ifcopenshell.api.group.update_group_products(self.file, products=elements, group=group)
        assert self.file.by_type("IfcRelAssignsToGroup")

        result = ifcopenshell.api.group.update_group_products(self.file, products=[], group=group)

        assert result is None
        # An empty RelatedObjects is not a valid value: the relationship
        # must be removed instead of left with zero related objects.
        assert not self.file.by_type("IfcRelAssignsToGroup")
        assert ifcopenshell.util.element.get_grouped_by(group) == []

    def test_update_group_products(self):
        elements = [ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall") for i in range(4)]
        group = ifcopenshell.api.group.add_group(self.file)
        ifcopenshell.api.group.assign_group(self.file, products=elements[:2], group=group)
        ifcopenshell.api.group.update_group_products(self.file, products=elements[2:], group=group)
        assert set(ifcopenshell.util.element.get_grouped_by(group)) == set(elements[2:])
        assert ifcopenshell.util.element.get_groups(elements[0]) == []
        assert ifcopenshell.util.element.get_groups(elements[1]) == []


class TestUpdateGroupProductsIFC4(test.bootstrap.IFC4, TestUpdateGroupProductsIFC2X3):
    def test_update_group_products(self):
        # in ifc4 IfcGroup can have multiple rels
        elements = [ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall") for i in range(4)]
        group = ifcopenshell.api.group.add_group(self.file)

        self.file.create_entity("IfcRelAssignsToGroup", RelatingGroup=group, RelatedObjects=elements[:1])
        self.file.create_entity("IfcRelAssignsToGroup", RelatingGroup=group, RelatedObjects=elements[1:2])

        ifcopenshell.api.group.update_group_products(self.file, products=elements[2:], group=group)
        assert len(self.file.by_type("IfcRelAssignsToGroup")) == 1
        assert set(ifcopenshell.util.element.get_grouped_by(group)) == set(elements[2:])
        assert ifcopenshell.util.element.get_groups(elements[0]) == []
        assert ifcopenshell.util.element.get_groups(elements[1]) == []
