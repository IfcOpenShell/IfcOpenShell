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
import ifcopenshell.api.root
import ifcopenshell.api.type
import ifcopenshell.api.material
import ifcopenshell.util.element


class TestAssignMaterialIFC2X3(test.bootstrap.IFC2X3):
    def test_assign_element_single_material(self):
        element1 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        element2 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        material = ifcopenshell.api.material.add_material(self.file, name="CON01")
        ifcopenshell.api.material.assign_material(
            self.file, products=[element1, element2], type="IfcMaterial", material=material
        )
        assert len(self.file.by_type("IfcRelAssociatesMaterial")) == 1
        assert ifcopenshell.util.element.get_material(element1) == material
        assert ifcopenshell.util.element.get_material(element2) == material

    def test_raise_exception_creating_ifc_material_without(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        ifcopenshell.api.material.assign_material(self.file, products=[element], type="IfcMaterial", material=None)
        assert ifcopenshell.util.element.get_material(element)

    def test_assign_type_single_material(self):
        element1 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWallType")
        element2 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWallType")
        material = ifcopenshell.api.material.add_material(self.file, name="CON01")
        ifcopenshell.api.material.assign_material(
            self.file, products=[element1, element2], type="IfcMaterial", material=material
        )
        assert len(self.file.by_type("IfcRelAssociatesMaterial")) == 1
        assert ifcopenshell.util.element.get_material(element1) == material
        assert ifcopenshell.util.element.get_material(element2) == material

    def test_assign_type_material_layer_set(self):
        element1 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWallType")
        element2 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWallType")
        ifcopenshell.api.material.assign_material(self.file, products=[element1, element2], type="IfcMaterialLayerSet")
        assert len(self.file.by_type("IfcRelAssociatesMaterial")) == 1
        material_set = ifcopenshell.util.element.get_material(element1)
        assert material_set.is_a("IfcMaterialLayerSet")
        assert not material_set.MaterialLayers
        assert ifcopenshell.util.element.get_material(element2) == material_set

    def test_assign_type_material_layer_set_and_element_layer_set_usage(self):
        element_type = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWallType")
        element1 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        element2 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        ifcopenshell.api.type.assign_type(self.file, related_objects=[element1, element2], relating_type=element_type)
        ifcopenshell.api.material.assign_material(self.file, products=[element_type], type="IfcMaterialLayerSet")
        ifcopenshell.api.material.assign_material(
            self.file, products=[element1, element2], type="IfcMaterialLayerSetUsage"
        )
        material_set = ifcopenshell.util.element.get_material(element_type)
        material_usage1 = ifcopenshell.util.element.get_material(element1, should_inherit=False)
        assert material_usage1.is_a("IfcMaterialLayerSetUsage")
        assert material_usage1.ForLayerSet == material_set
        assert ifcopenshell.util.element.get_material(element2, should_inherit=False) == material_usage1

    def test_assign_type_material_layer_set_and_element_layer_set_usage_is_different_for_different_types(self):
        element_type1 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWallType")
        element1 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        ifcopenshell.api.type.assign_type(self.file, related_objects=[element1], relating_type=element_type1)
        ifcopenshell.api.material.assign_material(self.file, products=[element_type1], type="IfcMaterialLayerSet")

        element_type2 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWallType")
        element2 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        ifcopenshell.api.type.assign_type(self.file, related_objects=[element2], relating_type=element_type2)
        ifcopenshell.api.material.assign_material(self.file, products=[element_type2], type="IfcMaterialLayerSet")

        ifcopenshell.api.material.assign_material(
            self.file, products=[element1, element2], type="IfcMaterialLayerSetUsage"
        )
        material_set1 = ifcopenshell.util.element.get_material(element_type1)
        material_usage1 = ifcopenshell.util.element.get_material(element1, should_inherit=False)
        assert material_usage1.is_a("IfcMaterialLayerSetUsage")
        assert material_usage1.ForLayerSet == material_set1

        material_set2 = ifcopenshell.util.element.get_material(element_type2)
        material_usage2 = ifcopenshell.util.element.get_material(element2, should_inherit=False)
        assert material_usage2.is_a("IfcMaterialLayerSetUsage")
        assert material_usage2.ForLayerSet == material_set2
        assert material_usage2 != material_usage1

    def test_assign_element_layer_set_usage_is_different_for_different_layer_set_directions(self):
        element1 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        element2 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcSlab")
        ifcopenshell.api.material.assign_material(
            self.file, products=[element1, element2], type="IfcMaterialLayerSetUsage"
        )

        material_usage1 = ifcopenshell.util.element.get_material(element1, should_inherit=False)
        assert material_usage1.is_a("IfcMaterialLayerSetUsage")
        material_set1 = material_usage1.ForLayerSet
        assert material_set1.is_a("IfcMaterialLayerSet")
        assert material_usage1.LayerSetDirection == "AXIS2"

        material_usage2 = ifcopenshell.util.element.get_material(element2, should_inherit=False)
        assert material_usage2.is_a("IfcMaterialLayerSetUsage")
        material_set2 = material_usage2.ForLayerSet
        assert material_set2.is_a("IfcMaterialLayerSet")
        assert material_usage2.LayerSetDirection == "AXIS3"

        assert material_set1 != material_set2
        assert material_usage1 != material_usage2

    def test_assign_element_material_list(self):
        element1 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        element2 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        material = ifcopenshell.api.material.add_material(self.file, name="CON01")
        ifcopenshell.api.material.assign_material(
            self.file,
            products=[element1, element2],
            type="IfcMaterialList",
            material=material,
        )
        assert len(self.file.by_type("IfcRelAssociatesMaterial")) == 1
        material_list = ifcopenshell.util.element.get_material(element1)
        assert material_list.is_a("IfcMaterialList")
        assert material_list.Materials[0] == material
        assert ifcopenshell.util.element.get_material(element2) == material_list

    def test_assign_element_material_layer_set_usage_with_provided_material_set(self):
        element_type1 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWallType")
        element1 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        ifcopenshell.api.type.assign_type(self.file, related_objects=[element1], relating_type=element_type1)
        ifcopenshell.api.material.assign_material(self.file, products=[element_type1], type="IfcMaterialLayerSet")

        provided_material_set = self.file.create_entity("IfcMaterialLayerSet")
        ifcopenshell.api.material.assign_material(
            self.file, products=[element1], material=provided_material_set, type="IfcMaterialLayerSetUsage"
        )
        assert ifcopenshell.util.element.get_material(element1, should_skip_usage=True) == provided_material_set


class TestAssignMaterialIFC4(test.bootstrap.IFC4, TestAssignMaterialIFC2X3):
    def test_assign_type_material_profile_set(self):
        element1 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWallType")
        element2 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWallType")
        ifcopenshell.api.material.assign_material(
            self.file, products=[element1, element2], type="IfcMaterialProfileSet"
        )
        assert len(self.file.by_type("IfcRelAssociatesMaterial")) == 1
        material_set = ifcopenshell.util.element.get_material(element1)
        assert material_set.is_a("IfcMaterialProfileSet")
        assert not material_set.MaterialProfiles
        assert ifcopenshell.util.element.get_material(element2) == material_set

    def test_assign_type_material_profile_set_and_element_profile_set_usage(self):
        element_type = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWallType")
        element1 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        element2 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        ifcopenshell.api.type.assign_type(self.file, related_objects=[element1, element2], relating_type=element_type)
        ifcopenshell.api.material.assign_material(self.file, products=[element_type], type="IfcMaterialProfileSet")
        ifcopenshell.api.material.assign_material(
            self.file, products=[element1, element2], type="IfcMaterialProfileSetUsage"
        )
        material_set = element_type.HasAssociations[0].RelatingMaterial
        material_usage1 = element1.HasAssociations[0].RelatingMaterial
        assert material_usage1.is_a("IfcMaterialProfileSetUsage")
        assert material_usage1.ForProfileSet == material_set
        assert ifcopenshell.util.element.get_material(element2, should_inherit=False) == material_usage1

    def test_assign_type_material_profile_set_and_element_profile_set_usage_is_different_for_different_types(self):
        element_type1 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWallType")
        element1 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        ifcopenshell.api.type.assign_type(self.file, related_objects=[element1], relating_type=element_type1)
        ifcopenshell.api.material.assign_material(self.file, products=[element_type1], type="IfcMaterialProfileSet")

        element_type2 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWallType")
        element2 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        ifcopenshell.api.type.assign_type(self.file, related_objects=[element2], relating_type=element_type2)
        ifcopenshell.api.material.assign_material(self.file, products=[element_type2], type="IfcMaterialProfileSet")

        ifcopenshell.api.material.assign_material(
            self.file, products=[element1, element2], type="IfcMaterialProfileSetUsage"
        )
        material_set1 = ifcopenshell.util.element.get_material(element_type1)
        material_usage1 = ifcopenshell.util.element.get_material(element1, should_inherit=False)
        assert material_usage1.is_a("IfcMaterialProfileSetUsage")
        assert material_usage1.ForProfileSet == material_set1

        material_set2 = ifcopenshell.util.element.get_material(element_type2)
        material_usage2 = ifcopenshell.util.element.get_material(element2, should_inherit=False)
        assert material_usage2.is_a("IfcMaterialProfileSetUsage")
        assert material_usage2.ForProfileSet == material_set2
        assert material_usage2 != material_usage1

    def test_assign_type_material_constituent_set(self):
        element1 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWallType")
        element2 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWallType")
        ifcopenshell.api.material.assign_material(
            self.file, products=[element1, element2], type="IfcMaterialConstituentSet"
        )
        assert len(self.file.by_type("IfcRelAssociatesMaterial")) == 1
        material_set = ifcopenshell.util.element.get_material(element1)
        assert material_set.is_a("IfcMaterialConstituentSet")
        assert not material_set.MaterialConstituents
        assert ifcopenshell.util.element.get_material(element2) == material_set

    def test_assign_element_material_profile_set_usage_with_provided_material_set(self):
        element_type1 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWallType")
        element1 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        ifcopenshell.api.type.assign_type(self.file, related_objects=[element1], relating_type=element_type1)
        ifcopenshell.api.material.assign_material(self.file, products=[element_type1], type="IfcMaterialProfileSet")

        provided_material_set = self.file.create_entity("IfcMaterialProfileSet")
        ifcopenshell.api.material.assign_material(
            self.file, products=[element1], material=provided_material_set, type="IfcMaterialProfileSetUsage"
        )
        assert ifcopenshell.util.element.get_material(element1, should_skip_usage=True) == provided_material_set
