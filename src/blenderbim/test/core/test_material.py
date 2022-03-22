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

import blenderbim.core.material as subject
from test.core.bootstrap import ifc, material, style


class TestUnlinkMaterial:
    def test_run(self, ifc):
        ifc.unlink(obj="obj").should_be_called()
        subject.unlink_material(ifc, obj="obj")


class TestAddMaterial:
    def test_add_a_default_material(self, ifc, material, style):
        material.add_default_material_object().should_be_called().will_return("obj")
        material.get_name("obj").should_be_called().will_return("name")
        ifc.run("material.add_material", name="name").should_be_called().will_return("material")
        ifc.link("material", "obj").should_be_called()
        style.get_style("obj").should_be_called().will_return(None)
        material.is_editing_materials().should_be_called().will_return(False)
        assert subject.add_material(ifc, material, style) == "material"

    def test_add_a_material_to_a_blender_material_object(self, ifc, material, style):
        material.get_name("obj").should_be_called().will_return("name")
        ifc.run("material.add_material", name="name").should_be_called().will_return("material")
        ifc.link("material", "obj").should_be_called()
        style.get_style("obj").should_be_called().will_return(None)
        material.is_editing_materials().should_be_called().will_return(False)
        assert subject.add_material(ifc, material, style, obj="obj") == "material"

    def test_reloading_imported_materials_if_you_are_editing_scene_materials(self, ifc, material, style):
        material.get_name("obj").should_be_called().will_return("name")
        ifc.run("material.add_material", name="name").should_be_called().will_return("material")
        ifc.link("material", "obj").should_be_called()
        style.get_style("obj").should_be_called().will_return(None)
        material.is_editing_materials().should_be_called().will_return(True)
        material.get_active_material_type().should_be_called().will_return("material_type")
        material.import_material_definitions("material_type").should_be_called()
        assert subject.add_material(ifc, material, style, obj="obj") == "material"

    def test_add_a_style_to_the_material_if_the_object_also_has_an_attached_style(self, ifc, material, style):
        material.get_name("obj").should_be_called().will_return("name")
        ifc.run("material.add_material", name="name").should_be_called().will_return("material")
        ifc.link("material", "obj").should_be_called()
        style.get_style("obj").should_be_called().will_return("style")
        style.get_context("obj").should_be_called().will_return("context")
        ifc.run("style.assign_material_style", material="material", style="style", context="context").should_be_called()
        material.is_editing_materials().should_be_called().will_return(False)
        assert subject.add_material(ifc, material, style, obj="obj") == "material"

    def test_not_adding_a_style_if_there_is_no_style_context_available(self, ifc, material, style):
        material.get_name("obj").should_be_called().will_return("name")
        ifc.run("material.add_material", name="name").should_be_called().will_return("material")
        ifc.link("material", "obj").should_be_called()
        style.get_style("obj").should_be_called().will_return("style")
        style.get_context("obj").should_be_called().will_return(None)
        material.is_editing_materials().should_be_called().will_return(False)
        assert subject.add_material(ifc, material, style, obj="obj") == "material"


class TestAddMaterialSet:
    def test_adding_a_material_set(self, ifc, material):
        ifc.run("material.add_material_set", name="Unnamed", set_type="set_type").should_be_called().will_return(
            "material"
        )
        material.is_editing_materials().should_be_called().will_return(False)
        assert subject.add_material_set(ifc, material, set_type="set_type") == "material"

    def test_adding_a_material_set_and_reloading_imported_materials(self, ifc, material):
        ifc.run("material.add_material_set", name="Unnamed", set_type="set_type").should_be_called().will_return(
            "material"
        )
        material.is_editing_materials().should_be_called().will_return(True)
        material.get_active_material_type().should_be_called().will_return("material_type")
        material.import_material_definitions("material_type").should_be_called()
        assert subject.add_material_set(ifc, material, set_type="set_type") == "material"


class TestRemoveMaterial:
    def test_removing_a_material(self, ifc, material, style):
        ifc.get_object("material").should_be_called().will_return(None)
        ifc.unlink(element="material").should_be_called()
        ifc.run("material.remove_material", material="material").should_be_called()
        material.is_editing_materials().should_be_called().will_return(False)
        subject.remove_material(ifc, material, style, material="material")

    def test_removing_a_material_and_reloading_imported_materials(self, ifc, material, style):
        ifc.get_object("material").should_be_called().will_return(None)
        ifc.unlink(element="material").should_be_called()
        ifc.run("material.remove_material", material="material").should_be_called()
        material.is_editing_materials().should_be_called().will_return(True)
        material.get_active_material_type().should_be_called().will_return("material_type")
        material.import_material_definitions("material_type").should_be_called()
        subject.remove_material(ifc, material, style, material="material")

    def test_removing_a_material_object_if_it_has_no_style(self, ifc, material, style):
        ifc.get_object("material").should_be_called().will_return("obj")
        ifc.unlink(element="material").should_be_called()
        ifc.run("material.remove_material", material="material").should_be_called()
        style.get_style("obj").should_be_called().will_return(None)
        material.delete_object("obj").should_be_called()
        material.is_editing_materials().should_be_called().will_return(False)
        subject.remove_material(ifc, material, style, material="material")

    def test_preserving_a_material_object_if_it_is_still_used_as_a_style(self, ifc, material, style):
        ifc.get_object("material").should_be_called().will_return("obj")
        ifc.unlink(element="material").should_be_called()
        ifc.run("material.remove_material", material="material").should_be_called()
        style.get_style("obj").should_be_called().will_return("style")
        material.is_editing_materials().should_be_called().will_return(False)
        subject.remove_material(ifc, material, style, material="material")


class TestRemoveMaterialSet:
    def test_run(self, ifc, material):
        ifc.run("material.remove_material_set", material="material").should_be_called()
        material.is_editing_materials().should_be_called().will_return(True)
        material.get_active_material_type().should_be_called().will_return("material_type")
        material.import_material_definitions("material_type").should_be_called()
        subject.remove_material_set(ifc, material, material="material")


class TestLoadMaterials:
    def test_run(self, material):
        material.import_material_definitions("material_type").should_be_called()
        material.enable_editing_materials().should_be_called()
        subject.load_materials(material, "material_type")


class TestDisableEditingMaterials:
    def test_run(self, material):
        material.disable_editing_materials().should_be_called()
        subject.disable_editing_materials(material)


class TestSelectByMaterial:
    def test_run(self, material):
        material.get_elements_by_material("material").should_be_called().will_return("elements")
        material.select_elements("elements").should_be_called()
        subject.select_by_material(material, material="material")
