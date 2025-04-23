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


class TestUnassignMaterialIFC2X3(test.bootstrap.IFC2X3):
    def test_unassign_single_material(self):
        element1 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        element2 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        material = ifcopenshell.api.material.add_material(self.file, name="CON01")
        ifcopenshell.api.material.assign_material(
            self.file, products=[element1, element2], type="IfcMaterial", material=material
        )
        ifcopenshell.api.material.unassign_material(self.file, products=[element1, element2])
        assert len(self.file.by_type("IfcRelAssociatesMaterial")) == 0
        assert len(self.file.by_type("IfcWall")) == 2
        assert len(self.file.by_type("IfcMaterial")) == 1

    def test_unassign_single_material_with_multiple_elements(self):
        element1 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        element2 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        material = ifcopenshell.api.material.add_material(self.file, name="CON01")
        ifcopenshell.api.material.assign_material(
            self.file, products=[element1, element2], type="IfcMaterial", material=material
        )
        ifcopenshell.api.material.unassign_material(self.file, products=[element2])
        assert element1.HasAssociations
        assert not element2.HasAssociations
        assert len(self.file.by_type("IfcRelAssociatesMaterial")) == 1
        assert len(self.file.by_type("IfcWall")) == 2
        assert len(self.file.by_type("IfcMaterial")) == 1

    def test_unassign_material_layer_set_from_type(self):
        element1 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWallType")
        element2 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWallType")
        ifcopenshell.api.material.assign_material(self.file, products=[element1, element2], type="IfcMaterialLayerSet")
        ifcopenshell.api.material.unassign_material(self.file, products=[element1, element2])
        assert len(self.file.by_type("IfcRelAssociatesMaterial")) == 0
        assert len(self.file.by_type("IfcWallType")) == 2
        assert len(self.file.by_type("IfcMaterialLayerSet")) == 1

    def test_unassign_material_layer_set_usage_from_element(self):
        element_type = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWallType")
        element1 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        element2 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        ifcopenshell.api.type.assign_type(self.file, related_objects=[element1, element2], relating_type=element_type)
        ifcopenshell.api.material.assign_material(self.file, products=[element_type], type="IfcMaterialLayerSet")
        ifcopenshell.api.material.assign_material(
            self.file, products=[element1, element2], type="IfcMaterialLayerSetUsage"
        )
        ifcopenshell.api.material.unassign_material(self.file, products=[element1, element2])
        assert len(self.file.by_type("IfcRelAssociatesMaterial")) == 1
        assert element_type.HasAssociations
        assert len(self.file.by_type("IfcWallType")) == 1
        assert len(self.file.by_type("IfcWall")) == 2
        assert len(self.file.by_type("IfcMaterialLayerSet")) == 1
        assert len(self.file.by_type("IfcMaterialLayerSetUsage")) == 0

    def test_unassign_material_layer_set_usage_shouldnt_remove_other_usages_of_the_type(self):
        element_type = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWallType")
        element1 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        element2 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        ifcopenshell.api.type.assign_type(self.file, related_objects=[element1, element2], relating_type=element_type)
        ifcopenshell.api.material.assign_material(self.file, products=[element_type], type="IfcMaterialLayerSet")
        ifcopenshell.api.material.assign_material(self.file, products=[element1], type="IfcMaterialLayerSetUsage")
        ifcopenshell.api.material.assign_material(self.file, products=[element2], type="IfcMaterialLayerSetUsage")
        ifcopenshell.api.material.unassign_material(self.file, products=[element1])
        assert len(self.file.by_type("IfcRelAssociatesMaterial")) == 2
        assert element_type.HasAssociations
        assert len(self.file.by_type("IfcWallType")) == 1
        assert len(self.file.by_type("IfcWall")) == 2
        assert len(self.file.by_type("IfcMaterialLayerSet")) == 1
        assert len(self.file.by_type("IfcMaterialLayerSetUsage")) == 1

    def test_unassign_material_layer_set_usage_from_element_with_multiple_invalid_usages(self):
        element_type = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWallType")
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        element2 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        ifcopenshell.api.type.assign_type(self.file, related_objects=[element], relating_type=element_type)
        ifcopenshell.api.type.assign_type(self.file, related_objects=[element2], relating_type=element_type)
        ifcopenshell.api.material.assign_material(self.file, products=[element_type], type="IfcMaterialLayerSet")
        rel = ifcopenshell.api.material.assign_material(self.file, products=[element], type="IfcMaterialLayerSetUsage")

        # In some invalid IFCs from Revit, they reuse usages. Let's recreate this invalid scenario
        rel.RelatedObjects = list(rel.RelatedObjects) + [element2]

        ifcopenshell.api.material.unassign_material(self.file, products=[element])

        assert len(self.file.by_type("IfcRelAssociatesMaterial")) == 2
        for rel in self.file.by_type("IfcRelAssociatesMaterial"):
            assert rel.RelatingMaterial
        assert element_type.HasAssociations
        assert len(self.file.by_type("IfcWallType")) == 1
        assert len(self.file.by_type("IfcWall")) == 2
        assert len(self.file.by_type("IfcMaterialLayerSet")) == 1
        assert len(self.file.by_type("IfcMaterialLayerSetUsage")) == 1
        assert ifcopenshell.util.element.get_material(element, should_inherit=False) is None
        assert ifcopenshell.util.element.get_material(element2, should_inherit=False).is_a("IfcMaterialLayerSetUsage")

    def test_unassign_element_material_list(self):
        element1 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        element2 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        material1 = ifcopenshell.api.material.add_material(self.file, name="CON01")
        ifcopenshell.api.material.assign_material(
            self.file,
            products=[element1, element2],
            type="IfcMaterialList",
            material=material1,
        )
        element3 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        material3 = ifcopenshell.api.material.add_material(self.file, name="CON01")
        ifcopenshell.api.material.assign_material(
            self.file, products=[element3], type="IfcMaterialList", material=material3
        )
        ifcopenshell.api.material.unassign_material(self.file, products=[element1, element2, element3])
        assert len(self.file.by_type("IfcRelAssociatesMaterial")) == 0
        assert len(self.file.by_type("IfcMaterialList")) == 2
        assert len(self.file.by_type("IfcMaterial")) == 2


class TestUnassignMaterialIFC4(test.bootstrap.IFC4, TestUnassignMaterialIFC2X3):

    def test_unassign_material_profile_set_from_type(self):
        element1 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWallType")
        ifcopenshell.api.material.assign_material(self.file, products=[element1], type="IfcMaterialProfileSet")
        element2 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWallType")
        ifcopenshell.api.material.assign_material(self.file, products=[element2], type="IfcMaterialProfileSet")
        ifcopenshell.api.material.unassign_material(self.file, products=[element1, element2])
        assert len(self.file.by_type("IfcRelAssociatesMaterial")) == 0
        assert len(self.file.by_type("IfcWallType")) == 2
        assert len(self.file.by_type("IfcMaterialProfileSet")) == 2

    def test_unassign_material_profile_set_usage_from_element(self):
        element_type = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWallType")
        element1 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        element2 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        ifcopenshell.api.type.assign_type(self.file, related_objects=[element1, element2], relating_type=element_type)
        ifcopenshell.api.material.assign_material(self.file, products=[element_type], type="IfcMaterialProfileSet")
        ifcopenshell.api.material.assign_material(
            self.file, products=[element1, element2], type="IfcMaterialProfileSetUsage"
        )
        ifcopenshell.api.material.unassign_material(self.file, products=[element1, element2])
        assert len(self.file.by_type("IfcRelAssociatesMaterial")) == 1
        assert element_type.HasAssociations
        assert len(self.file.by_type("IfcWallType")) == 1
        assert len(self.file.by_type("IfcWall")) == 2
        assert len(self.file.by_type("IfcMaterialProfileSet")) == 1
        assert len(self.file.by_type("IfcMaterialProfileSetUsage")) == 0

    def test_unassign_material_constituent_set_from_type(self):
        element1 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWallType")
        element2 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWallType")
        ifcopenshell.api.material.assign_material(
            self.file, products=[element1, element2], type="IfcMaterialConstituentSet"
        )
        element3 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWallType")
        ifcopenshell.api.material.assign_material(self.file, products=[element3], type="IfcMaterialConstituentSet")
        ifcopenshell.api.material.unassign_material(self.file, products=[element1, element2, element3])
        assert len(self.file.by_type("IfcRelAssociatesMaterial")) == 0
        assert len(self.file.by_type("IfcWallType")) == 3
        assert len(self.file.by_type("IfcMaterialConstituentSet")) == 2
