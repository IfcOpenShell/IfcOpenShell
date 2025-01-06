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
import ifcopenshell.api.pset
import ifcopenshell.api.root
import ifcopenshell.api.style
import ifcopenshell.api.context
import ifcopenshell.api.material
import ifcopenshell.util.element


class TestCopyMaterial(test.bootstrap.IFC4):
    def test_copy_a_single_material(self):
        material = ifcopenshell.api.material.add_material(self.file, name="CON01")
        new = ifcopenshell.api.material.copy_material(self.file, material=material)
        assert new.Name == "CON01"
        assert len(self.file.by_type("IfcMaterial")) == 2

    def test_assignments_are_not_copied(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        material = ifcopenshell.api.material.add_material(self.file, name="CON01")
        ifcopenshell.api.material.assign_material(self.file, products=[element], material=material)
        new = ifcopenshell.api.material.copy_material(self.file, material=material)
        assert ifcopenshell.util.element.get_elements_by_material(self.file, material)
        assert not ifcopenshell.util.element.get_elements_by_material(self.file, new)

    def test_copy_a_material_with_properties(self):
        def get_material_props(material: ifcopenshell.entity_instance) -> list[ifcopenshell.entity_instance]:
            if self.file.schema != "IFC2X3":
                return material.HasProperties
            return [i for i in self.file.get_inverse(material) if i.is_a("IfcMaterialProperties")]

        material = ifcopenshell.api.material.add_material(self.file, name="CON01")
        pset = ifcopenshell.api.pset.add_pset(self.file, product=material, name="Foo_Bar")
        ifcopenshell.api.pset.edit_pset(self.file, pset=pset, properties={"foo": "bar"})
        new = ifcopenshell.api.material.copy_material(self.file, material=material)
        assert new.Name == "CON01"
        assert len(self.file.by_type("IfcMaterial")) == 2
        assert len(self.file.by_type("IfcMaterialProperties")) == 2
        props_old = get_material_props(material)[0]
        props_new = get_material_props(new)[0]
        assert props_old != props_new
        if self.file.schema != "IFC2X3":
            assert props_old.Properties[0] != props_new.Properties[0]
            assert ifcopenshell.util.element.get_pset(new, "Foo_Bar", "foo") == "bar"
        else:
            assert props_old.ExtendedProperties[0] != props_new.ExtendedProperties[0]
            assert props_new.ExtendedProperties[0].NominalValue.wrappedValue == "bar"

    def test_copy_a_material_with_a_style_representation(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        context = ifcopenshell.api.context.add_context(self.file, context_type="Model")
        material = ifcopenshell.api.material.add_material(self.file, name="CON01")
        style = ifcopenshell.api.style.add_style(self.file)
        ifcopenshell.api.style.assign_material_style(self.file, material=material, style=style, context=context)
        new = ifcopenshell.api.material.copy_material(self.file, material=material)
        assert new.Name == "CON01"
        assert len(self.file.by_type("IfcPresentationStyle")) == 1
        assert len(self.file.by_type("IfcMaterialDefinitionRepresentation")) == 2
        assert new.HasRepresentation[0] != material.HasRepresentation[0]
        assert new.HasRepresentation[0].Representations[0] != material.HasRepresentation[0].Representations[0]
        assert new.HasRepresentation[0].Representations[0].ContextOfItems == context

    def test_copy_a_material_constituent_set(self):
        material = ifcopenshell.api.material.add_material(self.file, name="CON01")
        material_set = ifcopenshell.api.material.add_material_set(
            self.file, name="Foo", set_type="IfcMaterialConstituentSet"
        )
        item = ifcopenshell.api.material.add_constituent(self.file, constituent_set=material_set, material=material)

        new = ifcopenshell.api.material.copy_material(self.file, material=material_set)
        assert new != material_set
        assert new.Name == "Foo"
        assert new.MaterialConstituents[0] != item
        assert new.MaterialConstituents[0].Material == material
        assert len(self.file.by_type("IfcMaterialConstituentSet")) == 2
        assert len(self.file.by_type("IfcMaterialConstituent")) == 2
        assert len(self.file.by_type("IfcMaterial")) == 1

    def test_copy_a_material_layer_set(self):
        material = ifcopenshell.api.material.add_material(self.file, name="CON01")
        material_set = ifcopenshell.api.material.add_material_set(self.file, name="Foo", set_type="IfcMaterialLayerSet")
        item = ifcopenshell.api.material.add_layer(self.file, layer_set=material_set, material=material)

        new = ifcopenshell.api.material.copy_material(self.file, material=material_set)
        assert new != material_set
        assert new.LayerSetName == "Foo"
        assert new.MaterialLayers[0] != item
        assert new.MaterialLayers[0].Material == material
        assert len(self.file.by_type("IfcMaterialLayerSet")) == 2
        assert len(self.file.by_type("IfcMaterialLayer")) == 2
        assert len(self.file.by_type("IfcMaterial")) == 1

    def test_copy_a_material_profile_set(self):
        material = ifcopenshell.api.material.add_material(self.file, name="CON01")
        profile = self.file.create_entity(
            "IfcIShapeProfileDef",
            ProfileName="HEA100",
            ProfileType="AREA",
            OverallWidth=100,
            OverallDepth=96,
            WebThickness=5,
            FlangeThickness=8,
            FilletRadius=12,
        )
        material_set = ifcopenshell.api.material.add_material_set(
            self.file, name="Foo", set_type="IfcMaterialProfileSet"
        )
        item = ifcopenshell.api.material.add_profile(
            self.file, profile_set=material_set, material=material, profile=profile
        )

        new = ifcopenshell.api.material.copy_material(self.file, material=material_set)
        assert new != material_set
        assert new.Name == "Foo"
        assert new.MaterialProfiles[0] != item
        assert new.MaterialProfiles[0].Material == material
        assert new.MaterialProfiles[0].Profile == profile
        assert len(self.file.by_type("IfcMaterialProfileSet")) == 2
        assert len(self.file.by_type("IfcMaterialProfile")) == 2
        assert len(self.file.by_type("IfcMaterial")) == 1
        assert len(self.file.by_type("IfcProfileDef")) == 1

    def test_copy_a_material_list(self):
        material = ifcopenshell.api.material.add_material(self.file, name="CON01")
        material_set = ifcopenshell.api.material.add_material_set(self.file, set_type="IfcMaterialList")
        ifcopenshell.api.material.add_list_item(self.file, material_list=material_set, material=material)

        new = ifcopenshell.api.material.copy_material(self.file, material=material_set)
        assert new != material_set
        assert new.Materials[0] == material
        assert len(self.file.by_type("IfcMaterialList")) == 2
        assert len(self.file.by_type("IfcMaterial")) == 1


class TestCopyMaterialIFC2X3(test.bootstrap.IFC2X3, TestCopyMaterial):
    def test_copy_a_material_constituent_set(self):
        return

    def test_copy_a_material_profile_set(self):
        return
