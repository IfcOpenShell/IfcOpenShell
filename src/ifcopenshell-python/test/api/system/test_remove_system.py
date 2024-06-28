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
import ifcopenshell.api.root
import ifcopenshell.api.pset
import ifcopenshell.api.system


class TestRemoveSystem(test.bootstrap.IFC4):
    def test_removing_a_system(self):
        system = ifcopenshell.api.system.add_system(self.file, ifc_class="IfcSystem")
        ifcopenshell.api.system.remove_system(self.file, system=system)
        assert len(self.file.by_type("IfcSystem")) == 0

    def test_removing_orphaned_group_relationships(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcFlowTerminal")
        system = ifcopenshell.api.system.add_system(self.file, ifc_class="IfcSystem")
        ifcopenshell.api.system.assign_system(self.file, products=[element], system=system)
        ifcopenshell.api.system.remove_system(self.file, system=system)
        assert not self.file.by_type("IfcRelAssignsToGroup")

    def test_removing_orphaned_property_relationships(self):
        system = ifcopenshell.api.system.add_system(self.file, ifc_class="IfcSystem")
        pset = ifcopenshell.api.pset.add_pset(self.file, product=system, name="Foo_Bar")
        ifcopenshell.api.pset.edit_pset(self.file, pset=pset, properties={"Foo": "Bar"})
        ifcopenshell.api.system.remove_system(self.file, system=system)
        assert not self.file.by_type("IfcRelDefinesByProperties")
        assert not self.file.by_type("IfcPropertySet")
        assert not self.file.by_type("IfcPropertySingleValue")


class TestRemoveSystemIFC2X3(test.bootstrap.IFC2X3, TestRemoveSystem):
    pass
