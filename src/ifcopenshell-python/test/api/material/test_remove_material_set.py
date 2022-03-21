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


class TestRemoveMaterialSet(test.bootstrap.IFC4):
    def test_removing_material_set(self):
        material = ifcopenshell.api.run("material.add_material_set", self.file, set_type="IfcMaterialLayerSet")
        ifcopenshell.api.run("material.remove_material_set", self.file, material=material)
        assert len(self.file.by_type("IfcMaterialLayerSet")) == 0

    def test_removing_material_set_with_associations(self):
        wall = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        material = ifcopenshell.api.run("material.add_material_set", self.file, set_type="IfcMaterialLayerSet")
        ifcopenshell.api.run("material.assign_material", self.file, product=wall, material=material)
        ifcopenshell.api.run("material.remove_material_set", self.file, material=material)
        assert len(self.file.by_type("IfcMaterialLayerSet")) == 0
        assert len(self.file.by_type("IfcRelAssociatesMaterial")) == 0

    def test_removing_a_material_set_with_set_items_but_preserving_materials(self):
        material = ifcopenshell.api.run("material.add_material", self.file)
        material_set = ifcopenshell.api.run("material.add_material_set", self.file, set_type="IfcMaterialLayerSet")
        ifcopenshell.api.run("material.add_layer", self.file, layer_set=material_set, material=material)
        ifcopenshell.api.run("material.remove_material_set", self.file, material=material_set)
        assert len(self.file.by_type("IfcMaterialLayerSet")) == 0
        assert len(self.file.by_type("IfcMaterialLayer")) == 0
        assert len(self.file.by_type("IfcMaterial")) == 1

    def test_removing_a_material_set_with_properties(self):
        material = ifcopenshell.api.run("material.add_material_set", self.file, set_type="IfcMaterialLayerSet")
        pset = ifcopenshell.api.run("pset.add_pset", self.file, product=material, name="Foo_Bar")
        ifcopenshell.api.run("pset.edit_pset", self.file, pset=pset, properties={"Foo": "Bar"})
        assert material.HasProperties
        ifcopenshell.api.run("material.remove_material_set", self.file, material=material)
        assert len(self.file.by_type("IfcMaterialProperties")) == 0
        assert len(self.file.by_type("IfcPropertySingleValue")) == 0
