# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of BlenderBIM Add-on.
#
# BlenderBIM Add-on is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# BlenderBIM Add-on is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with BlenderBIM Add-on.  If not, see <http://www.gnu.org/licenses/>.

import bpy
import ifcopenshell
import blenderbim.core.tool
import blenderbim.tool as tool
from test.bim.bootstrap import NewFile
from blenderbim.tool.material import Material as subject


class TestImplementsTool(NewFile):
    def test_run(self):
        assert isinstance(subject(), blenderbim.core.tool.Material)


class TestAddDefaultMaterialObject(NewFile):
    def test_run(self):
        material = subject.add_default_material_object()
        assert isinstance(material, bpy.types.Material)
        assert material.name == "Default"


class TestDeleteObject(NewFile):
    def test_run(self):
        material = subject.add_default_material_object()
        assert bpy.data.materials.get("Default")
        subject.delete_object(material)
        assert not bpy.data.materials.get("Default")


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


class TestGetName(NewFile):
    def test_run(self):
        assert subject.get_name(bpy.data.materials.new("Material")) == "Material"


class TestImportMaterialDefinitions(NewFile):
    def test_import_materials(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        material = ifc.createIfcMaterial(Name="Name")
        subject.import_material_definitions("IfcMaterial")
        props = bpy.context.scene.BIMMaterialProperties
        assert props.materials[0].ifc_definition_id == material.id()
        assert props.materials[0].name == "Name"

    def test_import_material_layer_sets(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        material = ifc.createIfcMaterialLayerSet(LayerSetName="Name")
        subject.import_material_definitions("IfcMaterialLayerSet")
        props = bpy.context.scene.BIMMaterialProperties
        assert props.materials[0].ifc_definition_id == material.id()
        assert props.materials[0].name == "Name"

    def test_import_material_profile_sets(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        material = ifc.createIfcMaterialProfileSet(Name="Name")
        subject.import_material_definitions("IfcMaterialProfileSet")
        props = bpy.context.scene.BIMMaterialProperties
        assert props.materials[0].ifc_definition_id == material.id()
        assert props.materials[0].name == "Name"

    def test_import_material_constituent_sets(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        material = ifc.createIfcMaterialConstituentSet(Name="Name")
        subject.import_material_definitions("IfcMaterialConstituentSet")
        props = bpy.context.scene.BIMMaterialProperties
        assert props.materials[0].ifc_definition_id == material.id()
        assert props.materials[0].name == "Name"

    def test_import_material_lists(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        material = ifc.createIfcMaterialList()
        subject.import_material_definitions("IfcMaterialList")
        props = bpy.context.scene.BIMMaterialProperties
        assert props.materials[0].ifc_definition_id == material.id()
        assert props.materials[0].name == "Unnamed"


class TestIsEditingMaterials(NewFile):
    def test_run(self):
        bpy.context.scene.BIMMaterialProperties.is_editing = False
        subject.is_editing_materials() is False
        bpy.context.scene.BIMMaterialProperties.is_editing = True
        subject.is_editing_materials() is True
