# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of Bonsai.
#
# Bonsai is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Bonsai is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Bonsai.  If not, see <http://www.gnu.org/licenses/>.

import bpy
import ifcopenshell
import ifcopenshell.api
import ifcopenshell.api.material
import ifcopenshell.api.pset
import ifcopenshell.api.style
import bonsai.core.tool
import bonsai.tool as tool
from test.bim.bootstrap import NewFile
from bonsai.tool.material import Material as subject


class TestImplementsTool(NewFile):
    def test_run(self):
        assert isinstance(subject(), bonsai.core.tool.Material)


class TestDisableEditingMaterials(NewFile):
    def test_run(self):
        bpy.context.scene.BIMMaterialProperties.is_editing = True
        subject.disable_editing_materials()
        assert bpy.context.scene.BIMMaterialProperties.is_editing is False


class TestEnableEditingMaterials(NewFile):
    def test_run(self):
        bpy.context.scene.BIMMaterialProperties.is_editing = False
        subject.enable_editing_materials()
        assert bpy.context.scene.BIMMaterialProperties.is_editing is True


class TestGetActiveMaterialType(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        bpy.context.scene.BIMMaterialProperties.material_type = "IfcMaterial"
        assert subject.get_active_material_type() == "IfcMaterial"
        bpy.context.scene.BIMMaterialProperties.material_type = "IfcMaterialLayerSet"
        assert subject.get_active_material_type() == "IfcMaterialLayerSet"


class TestGetElementsByMaterial(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        element = ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcWall")
        material = ifcopenshell.api.run("material.add_material", ifc)
        ifcopenshell.api.run("material.assign_material", ifc, products=[element], material=material)
        assert subject.get_elements_by_material(material) == {element}


class TestImportMaterialDefinitions(NewFile):
    def test_import_materials_grouped_by_categories(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        material = ifc.createIfcMaterial(Name="Name", Category="Category")
        subject.import_material_definitions("IfcMaterial")
        props = bpy.context.scene.BIMMaterialProperties
        assert props.materials[0].ifc_definition_id == 0
        assert props.materials[0].name == "Category"
        assert props.materials[0].is_category is True
        assert props.materials[0].is_expanded is False
        assert len(props.materials) == 1

    def test_importing_expanded_material_categories(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        material = ifc.createIfcMaterial(Name="Name", Category="Category")
        subject.import_material_definitions("IfcMaterial")
        props = bpy.context.scene.BIMMaterialProperties
        props.materials[0].is_expanded = True
        subject.import_material_definitions("IfcMaterial")
        assert len(props.materials) == 2
        assert props.materials[1].ifc_definition_id == material.id()
        assert props.materials[1].name == "Name"
        assert props.materials[1].total_elements == 0

    def test_import_material_layer_sets(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        material = ifc.createIfcMaterialLayerSet(LayerSetName="Name")
        subject.import_material_definitions("IfcMaterialLayerSet")
        props = bpy.context.scene.BIMMaterialProperties
        assert props.materials[0].ifc_definition_id == material.id()
        assert props.materials[0].name == "Name"
        assert props.materials[0].total_elements == 0

    def test_import_material_profile_sets(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        material = ifc.createIfcMaterialProfileSet(Name="Name")
        subject.import_material_definitions("IfcMaterialProfileSet")
        props = bpy.context.scene.BIMMaterialProperties
        assert props.materials[0].ifc_definition_id == material.id()
        assert props.materials[0].name == "Name"
        assert props.materials[0].total_elements == 0

    def test_import_material_constituent_sets(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        material = ifc.createIfcMaterialConstituentSet(Name="Name")
        subject.import_material_definitions("IfcMaterialConstituentSet")
        props = bpy.context.scene.BIMMaterialProperties
        assert props.materials[0].ifc_definition_id == material.id()
        assert props.materials[0].name == "Name"
        assert props.materials[0].total_elements == 0

    def test_import_material_lists(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        material = ifc.createIfcMaterialList()
        subject.import_material_definitions("IfcMaterialList")
        props = bpy.context.scene.BIMMaterialProperties
        assert props.materials[0].ifc_definition_id == material.id()
        assert props.materials[0].name == "Unnamed"
        assert props.materials[0].total_elements == 0


class TestIsEditingMaterials(NewFile):
    def test_run(self):
        bpy.context.scene.BIMMaterialProperties.is_editing = False
        assert subject.is_editing_materials() is False
        bpy.context.scene.BIMMaterialProperties.is_editing = True
        assert subject.is_editing_materials() is True


class TestIsMaterialUsedInSets(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        material_set = ifc.createIfcMaterialLayerSet()
        material_set_item = ifc.createIfcMaterialLayer()
        material = ifc.createIfcMaterial()
        assert subject.is_material_used_in_sets(material) is False
        material_set.MaterialLayers = [material_set_item]
        material_set_item.Material = material
        assert subject.is_material_used_in_sets(material) is True


class TestEnsureNewMaterialSetIsValid(NewFile):
    def test_material_constituent_set(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        material_set = ifc.create_entity("IfcMaterialConstituentSet")
        subject.ensure_new_material_set_is_valid(material_set)
        assert len(constituents := material_set.MaterialConstituents) == 1
        assert constituents[0].Material

    def test_material_layer_set(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        material_set = ifc.create_entity("IfcMaterialLayerSet")
        subject.ensure_new_material_set_is_valid(material_set)
        assert len(layers := material_set.MaterialLayers) == 1
        assert layers[0].Material

    def test_material_profile_set(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        material_set = ifc.create_entity("IfcMaterialProfileSet")
        subject.ensure_new_material_set_is_valid(material_set)
        assert len(profiles := material_set.MaterialProfiles) == 1
        assert profiles[0].Profile

    def test_material_list(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        material_set = ifc.create_entity("IfcMaterialList")
        subject.ensure_new_material_set_is_valid(material_set)
        assert len(material_set.Materials) == 1


class TestPurgeUnusedMaterials(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        material = ifcopenshell.api.material.add_material(ifc)
        # Add pset.
        ifcopenshell.api.pset.add_pset(ifc, material, "Foo")
        # Add style.
        style = ifcopenshell.api.style.add_style(ifc)
        context = ifc.create_entity("IfcRepresentationContext")
        ifcopenshell.api.style.assign_material_style(ifc, material, style, context)

        assert subject.purge_unused_materials() == 1
        assert not ifc.by_type("IfcMaterial")
