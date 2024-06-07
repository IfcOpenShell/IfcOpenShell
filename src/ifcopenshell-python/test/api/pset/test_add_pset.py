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
import ifcopenshell.util.element


class TestAddPset(test.bootstrap.IFC4):
    def test_adding_a_pset_to_an_object(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        pset = ifcopenshell.api.run("pset.add_pset", self.file, product=element, name="Pset_WallCommon")
        assert pset.is_a("IfcPropertySet")
        assert "Pset_WallCommon" in ifcopenshell.util.element.get_psets(element)

    def test_adding_a_pset_to_a_type_object(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWallType")
        pset = ifcopenshell.api.run("pset.add_pset", self.file, product=element, name="Pset_WallCommon")
        assert pset.is_a("IfcPropertySet")
        assert "Pset_WallCommon" in ifcopenshell.util.element.get_psets(element)

    def test_adding_a_pset_to_a_material(self):
        material = ifcopenshell.api.run("material.add_material", self.file)
        pset = ifcopenshell.api.run("pset.add_pset", self.file, product=material, name="Pset_MaterialCommon")
        assert pset.is_a("IfcMaterialProperties")
        assert pset.Name == "Pset_MaterialCommon"
        assert pset.Material == material

    def test_adding_a_pset_to_a_profile(self):
        profile = ifcopenshell.api.run("profile.add_parameterized_profile", self.file, ifc_class="IfcCircleProfileDef")
        pset = ifcopenshell.api.run("pset.add_pset", self.file, product=profile, name="Pset_ProfileMechanical")
        assert pset.is_a("IfcProfileProperties")
        if self.file.schema != "IFC2X3":
            assert pset.Name == "Pset_ProfileMechanical"
        assert pset.ProfileDefinition == profile

    def test_adding_a_pset_to_a_context(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcProject")
        pset = ifcopenshell.api.run("pset.add_pset", self.file, product=element, name="Custom_Pset")
        assert pset.is_a("IfcPropertySet")
        assert "Custom_Pset" in ifcopenshell.util.element.get_psets(element)


class TestAddPsetIFC2X3(test.bootstrap.IFC2X3, TestAddPset):
    def test_adding_a_pset_to_a_project(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcProject")
        pset = ifcopenshell.api.run("pset.add_pset", self.file, product=element, name="Custom_Pset")
        assert pset.is_a("IfcPropertySet")
        assert "Custom_Pset" in ifcopenshell.util.element.get_psets(element)
