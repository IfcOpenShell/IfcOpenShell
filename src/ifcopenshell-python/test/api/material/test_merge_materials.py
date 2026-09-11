# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2024 Dion Moult <dion@thinkmoult.com>
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

# This file was generated with the assistance of an AI coding tool.

import ifcopenshell.api.context
import ifcopenshell.api.material
import ifcopenshell.api.pset
import ifcopenshell.api.root
import ifcopenshell.api.style
import ifcopenshell.util.element
import test.bootstrap


class TestMergeMaterialsIFC2X3(test.bootstrap.IFC2X3):
    def test_merging_two_materials_used_by_products(self):
        wall1 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        wall2 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        m1 = ifcopenshell.api.material.add_material(self.file, name="M1")
        m2 = ifcopenshell.api.material.add_material(self.file, name="M2")
        ifcopenshell.api.material.assign_material(self.file, products=[wall1], material=m1)
        ifcopenshell.api.material.assign_material(self.file, products=[wall2], material=m2)

        ifcopenshell.api.material.merge_materials(self.file, materials=[m1, m2], merge_into=m1)

        assert self.file.by_type("IfcMaterial") == [m1]
        assert ifcopenshell.util.element.get_material(wall1) == m1
        assert ifcopenshell.util.element.get_material(wall2) == m1
        # No dangling IfcRelAssociatesMaterial pointing at the removed material.
        assert all(r.RelatingMaterial != m2 for r in self.file.by_type("IfcRelAssociatesMaterial"))

    def test_merging_material_that_shares_a_product_with_the_target(self):
        # Both m1 and m2 assigned (at different times) to the same wall - only
        # the last assignment sticks, but merging should not error regardless.
        wall = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        m1 = ifcopenshell.api.material.add_material(self.file, name="M1")
        m2 = ifcopenshell.api.material.add_material(self.file, name="M2")
        ifcopenshell.api.material.assign_material(self.file, products=[wall], material=m2)

        ifcopenshell.api.material.merge_materials(self.file, materials=[m1, m2], merge_into=m1)

        assert self.file.by_type("IfcMaterial") == [m1]
        assert ifcopenshell.util.element.get_material(wall) == m1
        assert len(self.file.by_type("IfcRelAssociatesMaterial")) == 1

    def test_merging_material_used_in_a_layer_set(self):
        wall_type = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWallType")
        m1 = ifcopenshell.api.material.add_material(self.file, name="M1")
        m2 = ifcopenshell.api.material.add_material(self.file, name="M2")
        material_set = ifcopenshell.api.material.add_material_set(self.file, set_type="IfcMaterialLayerSet")
        layer1 = ifcopenshell.api.material.add_layer(self.file, layer_set=material_set, material=m1)
        layer2 = ifcopenshell.api.material.add_layer(self.file, layer_set=material_set, material=m2)
        ifcopenshell.api.material.assign_material(self.file, products=[wall_type], material=material_set)

        ifcopenshell.api.material.merge_materials(self.file, materials=[m1, m2], merge_into=m1)

        assert self.file.by_type("IfcMaterial") == [m1]
        assert layer1.Material == m1
        assert layer2.Material == m1
        # The layers themselves are untouched, only their material.
        assert len(material_set.MaterialLayers) == 2

    def test_merging_material_used_in_a_material_list(self):
        wall = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        m1 = ifcopenshell.api.material.add_material(self.file, name="M1")
        m2 = ifcopenshell.api.material.add_material(self.file, name="M2")
        material_set = ifcopenshell.api.material.add_material_set(self.file, set_type="IfcMaterialList")
        ifcopenshell.api.material.add_list_item(self.file, material_list=material_set, material=m1)
        ifcopenshell.api.material.add_list_item(self.file, material_list=material_set, material=m2)
        ifcopenshell.api.material.assign_material(self.file, products=[wall], material=material_set)

        ifcopenshell.api.material.merge_materials(self.file, materials=[m1, m2], merge_into=m1)

        assert self.file.by_type("IfcMaterial") == [m1]
        # No duplicate entries even though both list items now point at m1.
        assert list(material_set.Materials) == [m1]

    def test_merging_material_discards_its_own_style_and_properties(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        context = ifcopenshell.api.context.add_context(self.file, context_type="Model")
        m1 = ifcopenshell.api.material.add_material(self.file, name="M1")
        m2 = ifcopenshell.api.material.add_material(self.file, name="M2")
        style = ifcopenshell.api.style.add_style(self.file)
        ifcopenshell.api.style.assign_material_style(self.file, material=m2, style=style, context=context)
        pset = ifcopenshell.api.pset.add_pset(self.file, product=m2, name="Foo_Bar")
        ifcopenshell.api.pset.edit_pset(self.file, pset=pset, properties={"Foo": "Bar"})

        ifcopenshell.api.material.merge_materials(self.file, materials=[m1, m2], merge_into=m1)

        assert self.file.by_type("IfcMaterial") == [m1]
        assert self.file.by_type("IfcMaterialDefinitionRepresentation") == []
        assert self.file.by_type("IfcMaterialProperties") == []
        # The style itself is not deleted, only its assignment to the removed material.
        assert self.file.by_type("IfcSurfaceStyle") == [style]

    def test_merging_no_materials_does_nothing(self):
        m1 = ifcopenshell.api.material.add_material(self.file, name="M1")
        ifcopenshell.api.material.merge_materials(self.file, materials=[], merge_into=m1)
        assert self.file.by_type("IfcMaterial") == [m1]

    def test_merging_only_the_target_does_nothing(self):
        m1 = ifcopenshell.api.material.add_material(self.file, name="M1")
        ifcopenshell.api.material.merge_materials(self.file, materials=[m1], merge_into=m1)
        assert self.file.by_type("IfcMaterial") == [m1]


class TestMergeMaterialsIFC4(test.bootstrap.IFC4, TestMergeMaterialsIFC2X3):
    def test_merging_material_used_in_a_profile_set(self):
        column_type = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcColumnType")
        m1 = ifcopenshell.api.material.add_material(self.file, name="M1")
        m2 = ifcopenshell.api.material.add_material(self.file, name="M2")
        material_set = ifcopenshell.api.material.add_material_set(self.file, set_type="IfcMaterialProfileSet")
        profile1 = ifcopenshell.api.material.add_profile(self.file, profile_set=material_set, material=m1)
        profile2 = ifcopenshell.api.material.add_profile(self.file, profile_set=material_set, material=m2)
        ifcopenshell.api.material.assign_material(self.file, products=[column_type], material=material_set)

        ifcopenshell.api.material.merge_materials(self.file, materials=[m1, m2], merge_into=m1)

        assert self.file.by_type("IfcMaterial") == [m1]
        assert profile1.Material == m1
        assert profile2.Material == m1

    def test_merging_material_used_in_a_constituent_set(self):
        wall_type = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWallType")
        m1 = ifcopenshell.api.material.add_material(self.file, name="M1")
        m2 = ifcopenshell.api.material.add_material(self.file, name="M2")
        material_set = ifcopenshell.api.material.add_material_set(self.file, set_type="IfcMaterialConstituentSet")
        constituent1 = ifcopenshell.api.material.add_constituent(self.file, constituent_set=material_set, material=m1)
        constituent2 = ifcopenshell.api.material.add_constituent(self.file, constituent_set=material_set, material=m2)
        ifcopenshell.api.material.assign_material(self.file, products=[wall_type], material=material_set)

        ifcopenshell.api.material.merge_materials(self.file, materials=[m1, m2], merge_into=m1)

        assert self.file.by_type("IfcMaterial") == [m1]
        assert constituent1.Material == m1
        assert constituent2.Material == m1

    def test_merging_three_materials_into_one(self):
        wall1 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        wall2 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        wall3 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        target = ifcopenshell.api.material.add_material(self.file, name="Target")
        m1 = ifcopenshell.api.material.add_material(self.file, name="M1")
        m2 = ifcopenshell.api.material.add_material(self.file, name="M2")
        ifcopenshell.api.material.assign_material(self.file, products=[wall1], material=target)
        ifcopenshell.api.material.assign_material(self.file, products=[wall2], material=m1)
        ifcopenshell.api.material.assign_material(self.file, products=[wall3], material=m2)

        # Passing the target along with the redundant materials should be safe.
        ifcopenshell.api.material.merge_materials(self.file, materials=[target, m1, m2], merge_into=target)

        assert self.file.by_type("IfcMaterial") == [target]
        for wall in (wall1, wall2, wall3):
            assert ifcopenshell.util.element.get_material(wall) == target
