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

import test.bootstrap
import ifcopenshell.api.pset
import ifcopenshell.api.root
import ifcopenshell.api.group


class TestRemoveGroup(test.bootstrap.IFC4):
    def test_removing_a_group(self):
        group = ifcopenshell.api.group.add_group(self.file)
        ifcopenshell.api.group.remove_group(self.file, group=group)
        assert len(self.file.by_type("IfcGroup")) == 0

    def test_removing_orphaned_group_relationships(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        group = ifcopenshell.api.group.add_group(self.file)
        ifcopenshell.api.group.assign_group(self.file, products=[element], group=group)
        ifcopenshell.api.group.remove_group(self.file, group=group)
        assert not self.file.by_type("IfcRelAssignsToGroup")

    def test_removing_orphaned_property_relationships(self):
        group = ifcopenshell.api.group.add_group(self.file)
        pset = ifcopenshell.api.pset.add_pset(self.file, product=group, name="Foo_Bar")
        ifcopenshell.api.pset.edit_pset(self.file, pset=pset, properties={"Foo": "Bar"})
        ifcopenshell.api.group.remove_group(self.file, group=group)
        assert not self.file.by_type("IfcRelDefinesByProperties")
        assert not self.file.by_type("IfcPropertySet")
        assert not self.file.by_type("IfcPropertySingleValue")


class TestRemoveGroupIFC2X3(test.bootstrap.IFC2X3, TestRemoveGroup):
    pass
