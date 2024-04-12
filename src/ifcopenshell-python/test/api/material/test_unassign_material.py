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


class TestUnassignMaterial(test.bootstrap.IFC4):
    def test_unassign_single_material(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        material = ifcopenshell.api.run("material.add_material", self.file, name="CON01")
        ifcopenshell.api.run(
            "material.assign_material", self.file, products=[element], type="IfcMaterial", material=material
        )
        ifcopenshell.api.run("material.unassign_material", self.file, product=element)
        assert len(self.file.by_type("IfcRelAssociatesMaterial")) == 0
        assert len(self.file.by_type("IfcWall")) == 1
        assert len(self.file.by_type("IfcMaterial")) == 1

    def test_unassign_single_material_with_multiple_elements(self):
        element1 = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        element2 = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        material = ifcopenshell.api.run("material.add_material", self.file, name="CON01")
        ifcopenshell.api.run(
            "material.assign_material", self.file, products=[element1], type="IfcMaterial", material=material
        )
        ifcopenshell.api.run(
            "material.assign_material", self.file, products=[element2], type="IfcMaterial", material=material
        )
        ifcopenshell.api.run("material.unassign_material", self.file, product=element2)
        assert element1.HasAssociations
        assert not element2.HasAssociations
        assert len(self.file.by_type("IfcRelAssociatesMaterial")) == 1
        assert len(self.file.by_type("IfcWall")) == 2
        assert len(self.file.by_type("IfcMaterial")) == 1

    def test_unassign_material_layer_set_from_type(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWallType")
        material = ifcopenshell.api.run("material.add_material", self.file, name="CON01")
        ifcopenshell.api.run("material.assign_material", self.file, products=[element], type="IfcMaterialLayerSet")
        ifcopenshell.api.run("material.unassign_material", self.file, product=element)
        assert len(self.file.by_type("IfcRelAssociatesMaterial")) == 0
        assert len(self.file.by_type("IfcWallType")) == 1
        assert len(self.file.by_type("IfcMaterialLayerSet")) == 1

    def test_unassign_material_layer_set_usage_from_element(self):
        element_type = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWallType")
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        ifcopenshell.api.run("type.assign_type", self.file, related_objects=[element], relating_type=element_type)
        material = ifcopenshell.api.run("material.add_material", self.file, name="CON01")
        ifcopenshell.api.run("material.assign_material", self.file, products=[element_type], type="IfcMaterialLayerSet")
        ifcopenshell.api.run("material.assign_material", self.file, products=[element], type="IfcMaterialLayerSetUsage")
        ifcopenshell.api.run("material.unassign_material", self.file, product=element)
        assert len(self.file.by_type("IfcRelAssociatesMaterial")) == 1
        assert element_type.HasAssociations
        assert len(self.file.by_type("IfcWallType")) == 1
        assert len(self.file.by_type("IfcWall")) == 1
        assert len(self.file.by_type("IfcMaterialLayerSet")) == 1
        assert len(self.file.by_type("IfcMaterialLayerSetUsage")) == 0

    def test_unassign_material_layer_set_usage_from_element_with_multiple_invalid_usages(self):
        element_type = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWallType")
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        element2 = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        ifcopenshell.api.run("type.assign_type", self.file, related_objects=[element], relating_type=element_type)
        ifcopenshell.api.run("type.assign_type", self.file, related_objects=[element2], relating_type=element_type)
        material = ifcopenshell.api.run("material.add_material", self.file, name="CON01")
        ifcopenshell.api.run("material.assign_material", self.file, products=[element_type], type="IfcMaterialLayerSet")
        rel = ifcopenshell.api.run(
            "material.assign_material", self.file, products=[element], type="IfcMaterialLayerSetUsage"
        )

        # In some invalid IFCs from Revit, they reuse usages. Let's recreate this invalid scenario
        rel.RelatedObjects = list(rel.RelatedObjects) + [element2]

        ifcopenshell.api.run("material.unassign_material", self.file, product=element)

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

    def test_unassign_material_profile_set_from_type(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWallType")
        material = ifcopenshell.api.run("material.add_material", self.file, name="CON01")
        ifcopenshell.api.run("material.assign_material", self.file, products=[element], type="IfcMaterialProfileSet")
        ifcopenshell.api.run("material.unassign_material", self.file, product=element)
        assert len(self.file.by_type("IfcRelAssociatesMaterial")) == 0
        assert len(self.file.by_type("IfcWallType")) == 1
        assert len(self.file.by_type("IfcMaterialProfileSet")) == 1

    def test_unassign_material_profile_set_usage_from_element(self):
        element_type = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWallType")
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        ifcopenshell.api.run("type.assign_type", self.file, related_objects=[element], relating_type=element_type)
        material = ifcopenshell.api.run("material.add_material", self.file, name="CON01")
        ifcopenshell.api.run("material.assign_material", self.file, products=[element_type], type="IfcMaterialProfileSet")
        ifcopenshell.api.run("material.assign_material", self.file, products=[element], type="IfcMaterialProfileSetUsage")
        ifcopenshell.api.run("material.unassign_material", self.file, product=element)
        assert len(self.file.by_type("IfcRelAssociatesMaterial")) == 1
        assert element_type.HasAssociations
        assert len(self.file.by_type("IfcWallType")) == 1
        assert len(self.file.by_type("IfcWall")) == 1
        assert len(self.file.by_type("IfcMaterialProfileSet")) == 1
        assert len(self.file.by_type("IfcMaterialProfileSetUsage")) == 0

    def test_unassign_material_constituent_set_from_type(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWallType")
        material = ifcopenshell.api.run("material.add_material", self.file, name="CON01")
        ifcopenshell.api.run("material.assign_material", self.file, products=[element], type="IfcMaterialConstituentSet")
        ifcopenshell.api.run("material.unassign_material", self.file, product=element)
        assert len(self.file.by_type("IfcRelAssociatesMaterial")) == 0
        assert len(self.file.by_type("IfcWallType")) == 1
        assert len(self.file.by_type("IfcMaterialConstituentSet")) == 1

    def test_unassign_element_material_list(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        material = ifcopenshell.api.run("material.add_material", self.file, name="CON01")
        ifcopenshell.api.run(
            "material.assign_material", self.file, products=[element], type="IfcMaterialList", material=material
        )
        ifcopenshell.api.run("material.unassign_material", self.file, product=element)
        assert len(self.file.by_type("IfcRelAssociatesMaterial")) == 0
        assert len(self.file.by_type("IfcMaterialList")) == 1
        assert len(self.file.by_type("IfcMaterial")) == 1
