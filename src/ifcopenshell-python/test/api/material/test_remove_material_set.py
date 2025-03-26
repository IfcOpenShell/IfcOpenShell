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
import ifcopenshell.api.material
import ifcopenshell.api.pset
import ifcopenshell.api.root
import ifcopenshell.api.type


class TestRemoveMaterialSetIFC2X3(test.bootstrap.IFC2X3):
    def test_removing_material_set(self):
        material = ifcopenshell.api.material.add_material_set(self.file, set_type="IfcMaterialLayerSet")
        ifcopenshell.api.material.remove_material_set(self.file, material=material)
        assert len(self.file.by_type("IfcMaterialLayerSet")) == 0

    def test_removing_material_set_with_associations(self):
        wall = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        material = ifcopenshell.api.material.add_material_set(self.file, set_type="IfcMaterialLayerSet")
        ifcopenshell.api.material.assign_material(self.file, products=[wall], material=material)
        ifcopenshell.api.material.remove_material_set(self.file, material=material)
        assert len(self.file.by_type("IfcMaterialLayerSet")) == 0
        assert len(self.file.by_type("IfcRelAssociatesMaterial")) == 0

    def test_removing_a_material_set_with_set_items_but_preserving_materials(self):
        material = ifcopenshell.api.material.add_material(self.file)
        material_set = ifcopenshell.api.material.add_material_set(self.file, set_type="IfcMaterialLayerSet")
        ifcopenshell.api.material.add_layer(self.file, layer_set=material_set, material=material)
        ifcopenshell.api.material.remove_material_set(self.file, material=material_set)
        assert len(self.file.by_type("IfcMaterialLayerSet")) == 0
        assert len(self.file.by_type("IfcMaterialLayer")) == 0
        assert len(self.file.by_type("IfcMaterial")) == 1

    def test_removing_a_material_set_with_usages(self):
        material = ifcopenshell.api.material.add_material_set(self.file, set_type="IfcMaterialLayerSet")
        element_type = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWallType")
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        ifcopenshell.api.type.assign_type(self.file, related_objects=[element], relating_type=element_type)
        ifcopenshell.api.material.assign_material(self.file, products=[element_type], material=material)
        ifcopenshell.api.material.assign_material(
            self.file, products=[element], material=material, type="IfcMaterialLayerSetUsage"
        )
        ifcopenshell.api.material.remove_material_set(self.file, material=material)
        assert len(self.file.by_type("IfcMaterialLayerSet")) == 0
        assert len(self.file.by_type("IfcMaterialLayerSetUsage")) == 0


class TestRemoveMaterialSetIFC4(test.bootstrap.IFC4, TestRemoveMaterialSetIFC2X3):
    # IFC2X3 doesn't support adding a pset to IfcMaterialLayerSet
    def test_removing_a_material_set_with_properties(self):
        material = ifcopenshell.api.material.add_material_set(self.file, set_type="IfcMaterialLayerSet")
        pset = ifcopenshell.api.pset.add_pset(self.file, product=material, name="Foo_Bar")
        ifcopenshell.api.pset.edit_pset(self.file, pset=pset, properties={"Foo": "Bar"})
        assert material.HasProperties
        ifcopenshell.api.material.remove_material_set(self.file, material=material)
        assert len(self.file.by_type("IfcMaterialProperties")) == 0
        assert len(self.file.by_type("IfcPropertySingleValue")) == 0
