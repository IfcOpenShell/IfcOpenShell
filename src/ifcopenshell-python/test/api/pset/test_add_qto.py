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


class TestAddQto(test.bootstrap.IFC4):
    def test_adding_a_qto_to_an_object(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        qto = ifcopenshell.api.run("pset.add_qto", self.file, product=element, name="Qto_WallBaseQuantities")
        assert qto.is_a("IfcElementQuantity")
        assert "Qto_WallBaseQuantities" in ifcopenshell.util.element.get_psets(element)

    def test_adding_a_qto_to_a_type_object(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWallType")
        qto = ifcopenshell.api.run("pset.add_qto", self.file, product=element, name="Custom_Qto")
        assert qto.is_a("IfcElementQuantity")
        assert "Custom_Qto" in ifcopenshell.util.element.get_psets(element)

    def test_adding_a_qto_to_a_context(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcProject")
        qto = ifcopenshell.api.run("pset.add_qto", self.file, product=element, name="Custom_Qto")
        assert qto.is_a("IfcElementQuantity")
        assert "Custom_Qto" in ifcopenshell.util.element.get_psets(element)


class TestAddQtoIFC2X3(test.bootstrap.IFC2X3):
    def test_adding_a_qto_to_a_project(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcProject")
        qto = ifcopenshell.api.run("pset.add_qto", self.file, product=element, name="Custom_Qto")
        assert qto.is_a("IfcElementQuantity")
        assert "Custom_Qto" in ifcopenshell.util.element.get_psets(element)
