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
import ifcopenshell.api


class TestRemovePset(test.bootstrap.IFC4):
    def test_removing_pset(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        pset = ifcopenshell.api.run("pset.add_pset", self.file, product=element, name="Foo_Bar")
        assert len(self.file.by_type("IfcRelDefinesByProperties")) == 1
        ifcopenshell.api.run("pset.remove_pset", self.file, product=element, pset=pset)
        assert len(self.file.by_type("IfcRelDefinesByProperties")) == 0
        assert len(self.file.by_type("IfcPropertySet")) == 0

    def test_only_unassigning_if_pset_is_used_by_other_elements(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        element2 = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        pset = ifcopenshell.api.run("pset.add_pset", self.file, product=element, name="Foo_Bar")
        rel = self.file.by_type("IfcRelDefinesByProperties")[0]
        rel.RelatedObjects = [element, element2]
        assert len(self.file.by_type("IfcRelDefinesByProperties")) == 1
        ifcopenshell.api.run("pset.remove_pset", self.file, product=element, pset=pset)
        assert ifcopenshell.util.element.get_psets(element) == {}
        assert "Foo_Bar" in ifcopenshell.util.element.get_psets(element2)

    def test_removing_a_pset_with_properties(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        pset = ifcopenshell.api.run("pset.add_pset", self.file, product=element, name="Foo_Bar")
        ifcopenshell.api.run("pset.edit_pset", self.file, pset=pset, properties={"Foo": "Bar"})
        ifcopenshell.api.run("pset.remove_pset", self.file, product=element, pset=pset)
        assert len(self.file.by_type("IfcRelDefinesByProperties")) == 0
        assert len(self.file.by_type("IfcPropertySet")) == 0
        assert len(self.file.by_type("IfcPropertySingleValue")) == 0

    def test_removing_a_qto_with_quantities(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        qto = ifcopenshell.api.run("pset.add_qto", self.file, product=element, name="Foo_Bar")
        ifcopenshell.api.run("pset.edit_qto", self.file, qto=qto, properties={"Foo": 42})
        ifcopenshell.api.run("pset.remove_pset", self.file, product=element, pset=qto)
        assert len(self.file.by_type("IfcRelDefinesByProperties")) == 0
        assert len(self.file.by_type("IfcQuantitySet")) == 0
        assert len(self.file.by_type("IfcPhysicalSimpleQuantity")) == 0
