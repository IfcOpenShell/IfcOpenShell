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


class TestRemoveMaterial(test.bootstrap.IFC4):
    def test_removing_material(self):
        material = ifcopenshell.api.run("material.add_material", self.file)
        ifcopenshell.api.run("material.remove_material", self.file, material=material)
        assert len(self.file.by_type("IfcMaterial")) == 0

    def test_removing_material_with_associations(self):
        wall = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        material = ifcopenshell.api.run("material.add_material", self.file)
        ifcopenshell.api.run("material.assign_material", self.file, product=wall, material=material)
        ifcopenshell.api.run("material.remove_material", self.file, material=material)
        assert len(self.file.by_type("IfcMaterial")) == 0
        assert len(self.file.by_type("IfcRelAssociatesMaterial")) == 0

    def test_removing_material_in_layer(self):
        wall = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        material = ifcopenshell.api.run("material.add_material", self.file)
        material_set = ifcopenshell.api.run(
            "material.add_material_set", self.file, set_type="IfcMaterialLayerSet"
        )
        ifcopenshell.api.run("material.add_layer", self.file, layer_set=material_set, material=material)
        ifcopenshell.api.run("material.assign_material", self.file, product=wall, material=material_set)
        assert len(self.file.by_type("IfcMaterialLayerSet")[0].MaterialLayers) == 1
        ifcopenshell.api.run("material.remove_material", self.file, material=material)
        assert len(self.file.by_type("IfcMaterial")) == 0
        assert len(self.file.by_type("IfcRelAssociatesMaterial")) == 1
        assert len(self.file.by_type("IfcMaterialLayerSet")[0].MaterialLayers) == 0

    def test_removing_material_in_profile(self):
        wall = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        material = ifcopenshell.api.run("material.add_material", self.file)
        material_set = ifcopenshell.api.run(
            "material.add_material_set", self.file, set_type="IfcMaterialProfileSet"
        )
        ifcopenshell.api.run("material.add_profile", self.file, profile_set=material_set, material=material)
        ifcopenshell.api.run("material.assign_material", self.file, product=wall, material=material_set)
        assert len(self.file.by_type("IfcMaterialProfileSet")[0].MaterialProfiles) == 1
        ifcopenshell.api.run("material.remove_material", self.file, material=material)
        assert len(self.file.by_type("IfcMaterial")) == 0
        assert len(self.file.by_type("IfcRelAssociatesMaterial")) == 1
        assert len(self.file.by_type("IfcMaterialProfileSet")[0].MaterialProfiles) == 0

    def test_removing_material_in_constituent(self):
        wall = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        material = ifcopenshell.api.run("material.add_material", self.file)
        material_set = ifcopenshell.api.run(
            "material.add_material_set", self.file, set_type="IfcMaterialConstituentSet"
        )
        ifcopenshell.api.run("material.add_constituent", self.file, constituent_set=material_set, material=material)
        ifcopenshell.api.run("material.assign_material", self.file, product=wall, material=material_set)
        assert len(self.file.by_type("IfcMaterialConstituentSet")[0].MaterialConstituents) == 1
        ifcopenshell.api.run("material.remove_material", self.file, material=material)
        assert len(self.file.by_type("IfcMaterial")) == 0
        assert len(self.file.by_type("IfcRelAssociatesMaterial")) == 1
        assert self.file.by_type("IfcMaterialConstituentSet")[0].MaterialConstituents is None

    def test_removing_material_in_list(self):
        wall = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        material = ifcopenshell.api.run("material.add_material", self.file)
        material_set = ifcopenshell.api.run(
            "material.add_material_set", self.file, set_type="IfcMaterialList"
        )
        ifcopenshell.api.run("material.add_list_item", self.file, material_list=material_set, material=material)
        ifcopenshell.api.run("material.assign_material", self.file, product=wall, material=material_set)
        assert len(self.file.by_type("IfcMaterialList")[0].Materials) == 1
        ifcopenshell.api.run("material.remove_material", self.file, material=material)
        assert len(self.file.by_type("IfcMaterial")) == 0
        assert len(self.file.by_type("IfcRelAssociatesMaterial")) == 1
        assert len(self.file.by_type("IfcMaterialList")[0].Materials) == 0
