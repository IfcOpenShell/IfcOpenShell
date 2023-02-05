# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2023 Dion Moult <dion@thinkmoult.com>
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


class TestAssignMaterial(test.bootstrap.IFC4):
    def test_assign_element_single_material(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        material = ifcopenshell.api.run("material.add_material", self.file, name="CON01")
        ifcopenshell.api.run("material.assign_material", self.file, product=element, type="IfcMaterial", material=material)
        assert len(self.file.by_type("IfcRelAssociatesMaterial")) == 1
        assert element.HasAssociations[0].RelatingMaterial == material

    def test_assign_type_single_material(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWallType")
        material = ifcopenshell.api.run("material.add_material", self.file, name="CON01")
        ifcopenshell.api.run("material.assign_material", self.file, product=element, type="IfcMaterial", material=material)
        assert len(self.file.by_type("IfcRelAssociatesMaterial")) == 1
        assert element.HasAssociations[0].RelatingMaterial == material

    def test_assign_type_material_layer_set(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWallType")
        material = ifcopenshell.api.run("material.add_material", self.file, name="CON01")
        ifcopenshell.api.run("material.assign_material", self.file, product=element, type="IfcMaterialLayerSet")
        assert len(self.file.by_type("IfcRelAssociatesMaterial")) == 1
        material_set = element.HasAssociations[0].RelatingMaterial
        assert material_set.is_a("IfcMaterialLayerSet")
        assert not material_set.MaterialLayers

    def test_assign_type_material_layer_set_and_element_layer_set_usage(self):
        element_type = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWallType")
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        ifcopenshell.api.run("type.assign_type", self.file, related_object=element, relating_type=element_type)
        material = ifcopenshell.api.run("material.add_material", self.file, name="CON01")
        ifcopenshell.api.run("material.assign_material", self.file, product=element_type, type="IfcMaterialLayerSet")
        ifcopenshell.api.run("material.assign_material", self.file, product=element, type="IfcMaterialLayerSetUsage")
        material_set = element_type.HasAssociations[0].RelatingMaterial
        material_usage = element.HasAssociations[0].RelatingMaterial
        assert material_usage.is_a("IfcMaterialLayerSetUsage")
        assert material_usage.ForLayerSet == material_set

    def test_assign_type_material_profile_set(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWallType")
        material = ifcopenshell.api.run("material.add_material", self.file, name="CON01")
        ifcopenshell.api.run("material.assign_material", self.file, product=element, type="IfcMaterialProfileSet")
        assert len(self.file.by_type("IfcRelAssociatesMaterial")) == 1
        material_set = element.HasAssociations[0].RelatingMaterial
        assert material_set.is_a("IfcMaterialProfileSet")
        assert not material_set.MaterialProfiles

    def test_assign_type_material_profile_set_and_element_profile_set_usage(self):
        element_type = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWallType")
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        ifcopenshell.api.run("type.assign_type", self.file, related_object=element, relating_type=element_type)
        material = ifcopenshell.api.run("material.add_material", self.file, name="CON01")
        ifcopenshell.api.run("material.assign_material", self.file, product=element_type, type="IfcMaterialProfileSet")
        ifcopenshell.api.run("material.assign_material", self.file, product=element, type="IfcMaterialProfileSetUsage")
        material_set = element_type.HasAssociations[0].RelatingMaterial
        material_usage = element.HasAssociations[0].RelatingMaterial
        assert material_usage.is_a("IfcMaterialProfileSetUsage")
        assert material_usage.ForProfileSet == material_set

    def test_assign_type_material_constituent_set(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWallType")
        material = ifcopenshell.api.run("material.add_material", self.file, name="CON01")
        ifcopenshell.api.run("material.assign_material", self.file, product=element, type="IfcMaterialConstituentSet")
        assert len(self.file.by_type("IfcRelAssociatesMaterial")) == 1
        material_set = element.HasAssociations[0].RelatingMaterial
        assert material_set.is_a("IfcMaterialConstituentSet")
        assert not material_set.MaterialConstituents

    def test_assign_element_material_list(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        material = ifcopenshell.api.run("material.add_material", self.file, name="CON01")
        ifcopenshell.api.run("material.assign_material", self.file, product=element, type="IfcMaterialList", material=material)
        assert len(self.file.by_type("IfcRelAssociatesMaterial")) == 1
        material_list = element.HasAssociations[0].RelatingMaterial
        assert material_list.is_a("IfcMaterialList")
        assert material_list.Materials[0] == material
