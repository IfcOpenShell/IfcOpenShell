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
import ifcopenshell.api.material
import ifcopenshell.api.pset
import ifcopenshell.api.root
import ifcopenshell.api.style

import bonsai.core.tool
import bonsai.tool as tool
from bonsai.tool.material import Material as subject
from test.bim.bootstrap import NewFile


class TestImplementsTool(NewFile):
    def test_run(self):
        assert isinstance(subject(), bonsai.core.tool.Material)


class TestDisableEditingMaterials(NewFile):
    def test_run(self):
        props = tool.Material.get_material_props()
        props.is_editing = True
        subject.disable_editing_materials()
        assert props.is_editing is False


class TestEnableEditingMaterials(NewFile):
    def test_run(self):
        props = tool.Material.get_material_props()
        props.is_editing = False
        subject.enable_editing_materials()
        assert props.is_editing is True


class TestGetActiveMaterialType(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        props = tool.Material.get_material_props()
        props.material_type = "IfcMaterial"
        assert subject.get_active_material_type() == "IfcMaterial"
        props.material_type = "IfcMaterialLayerSet"
        assert subject.get_active_material_type() == "IfcMaterialLayerSet"


class TestSelectMaterialInMaterialsUI(NewFile):
    def test_material_type_follows_the_selected_material_set(self):
        bpy.ops.bim.create_project()
        ifc = tool.Ifc.get()
        layer_set = ifcopenshell.api.material.add_material_set(ifc, name="Set", set_type="IfcMaterialLayerSet")
        bpy.ops.bim.material_ui_select(material_id=layer_set.id())
        assert tool.Material.get_material_props().material_type == "IfcMaterialLayerSet"


class TestGetElementsByMaterial(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        element = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcWall")
        material = ifcopenshell.api.material.add_material(ifc)
        ifcopenshell.api.material.assign_material(ifc, products=[element], material=material)
        assert subject.get_elements_by_material(material) == {element}


class TestImportMaterialDefinitions(NewFile):
    def test_import_materials_grouped_by_categories(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        material = ifc.createIfcMaterial(Name="Name", Category="Category")
        subject.import_material_definitions("IfcMaterial")
        props = tool.Material.get_material_props()
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
        props = tool.Material.get_material_props()
        props.materials[0].is_expanded = True
        subject.import_material_definitions("IfcMaterial")
        assert len(props.materials) == 2
        assert props.materials[1].ifc_definition_id == material.id()
        assert props.materials[1].name == "Name"
        assert props.materials[1].total_elements == 0

    def test_importing_collapsed_material_categories_when_filter_is_active(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        material = ifc.createIfcMaterial(Name="Name", Category="Category")
        props = tool.Material.get_material_props()
        props.material_filter = "nam"
        subject.import_material_definitions("IfcMaterial")
        assert len(props.materials) == 2
        assert props.materials[0].name == "Category"
        assert props.materials[0].is_category is True
        assert props.materials[0].is_expanded is False
        assert props.materials[1].ifc_definition_id == material.id()
        assert props.materials[1].name == "Name"

    def test_importing_materials_preserves_selected_material(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        ifc.createIfcMaterial(Name="A1", Category="A")
        selected = ifc.createIfcMaterial(Name="B1", Category="B")
        props = tool.Material.get_material_props()
        props.material_filter = "1"
        props.active_material_index = next(
            index for index, material in enumerate(props.materials) if material.ifc_definition_id == selected.id()
        )
        # Shift the selected material to a higher index.
        ifc.createIfcMaterial(Name="A0", Category="A")
        subject.import_material_definitions("IfcMaterial")
        assert props.materials[props.active_material_index].ifc_definition_id == selected.id()

    def test_import_material_layer_sets(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        material = ifc.createIfcMaterialLayerSet(LayerSetName="Name")
        subject.import_material_definitions("IfcMaterialLayerSet")
        props = tool.Material.get_material_props()
        assert props.materials[0].ifc_definition_id == material.id()
        assert props.materials[0].name == "Name"
        assert props.materials[0].total_elements == 0

    def test_import_material_profile_sets(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        material = ifc.createIfcMaterialProfileSet(Name="Name")
        subject.import_material_definitions("IfcMaterialProfileSet")
        props = tool.Material.get_material_props()
        assert props.materials[0].ifc_definition_id == material.id()
        assert props.materials[0].name == "Name"
        assert props.materials[0].total_elements == 0

    def test_import_material_constituent_sets(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        material = ifc.createIfcMaterialConstituentSet(Name="Name")
        subject.import_material_definitions("IfcMaterialConstituentSet")
        props = tool.Material.get_material_props()
        assert props.materials[0].ifc_definition_id == material.id()
        assert props.materials[0].name == "Name"
        assert props.materials[0].total_elements == 0

    def test_import_material_lists(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        material = ifc.createIfcMaterialList()
        subject.import_material_definitions("IfcMaterialList")
        props = tool.Material.get_material_props()
        assert props.materials[0].ifc_definition_id == material.id()
        assert props.materials[0].name == "Unnamed"
        assert props.materials[0].total_elements == 0


class TestUpdateMaterialFilter(NewFile):
    def test_changing_filter_text_while_active_does_not_reload_materials(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        ifc.createIfcMaterial(Name="Existing", Category="ExistingCategory")
        props = tool.Material.get_material_props()
        props.material_filter = "e"
        assert len(props.materials) == 2
        ifc.createIfcMaterial(Name="New", Category="NewCategory")
        props.material_filter = "ex"
        assert len(props.materials) == 2
        assert all(material.name != "New" for material in props.materials)

    def test_clearing_filter_restores_collapsed_categories(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        ifc.createIfcMaterial(Name="Name", Category="Category")
        props = tool.Material.get_material_props()
        props.material_filter = "nam"
        assert len(props.materials) == 2
        props.material_filter = ""
        assert len(props.materials) == 1
        assert props.materials[0].is_category is True
        assert props.materials[0].is_expanded is False

    def test_clearing_filter_selects_the_category_of_the_selected_material(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        material = ifc.createIfcMaterial(Name="Name", Category="Category")
        props = tool.Material.get_material_props()
        props.material_filter = "nam"
        props.active_material_index = next(
            index for index, item in enumerate(props.materials) if item.ifc_definition_id == material.id()
        )
        props.material_filter = ""
        assert props.materials[props.active_material_index].is_category is True
        assert props.materials[props.active_material_index].name == "Category"


class TestRefresh(NewFile):
    def test_run(self):
        from bonsai.bim.module.material.data import MaterialsData, ObjectMaterialData

        MaterialsData.is_loaded = True
        ObjectMaterialData.is_loaded = True
        subject.refresh()
        assert MaterialsData.is_loaded is False
        assert ObjectMaterialData.is_loaded is False


class TestIsEditingMaterials(NewFile):
    def test_run(self):
        props = tool.Material.get_material_props()
        props.is_editing = False
        assert subject.is_editing_materials() is False
        props.is_editing = True
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
