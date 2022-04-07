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

import blenderbim.core.style as subject
from test.core.bootstrap import ifc, material, style


class TestAddStyle:
    def test_it_adds_a_style_with_rendering_attributes(self, ifc, style):
        style.get_name("obj").should_be_called().will_return("name")
        ifc.run("style.add_style", name="name").should_be_called().will_return("style")
        ifc.link("style", "obj").should_be_called()

        style.can_support_rendering_style("obj").should_be_called().will_return(True)
        style.get_surface_rendering_attributes("obj").should_be_called().will_return("attributes")
        ifc.run(
            "style.add_surface_style", style="style", ifc_class="IfcSurfaceStyleRendering", attributes="attributes"
        ).should_be_called()

        ifc.get_entity("obj").should_be_called().will_return(None)
        assert subject.add_style(ifc, style, obj="obj") == "style"

    def test_adding_a_style_linked_to_a_material(self, ifc, style):
        style.get_name("obj").should_be_called().will_return("name")
        ifc.run("style.add_style", name="name").should_be_called().will_return("style")
        ifc.link("style", "obj").should_be_called()

        style.can_support_rendering_style("obj").should_be_called().will_return(False)
        style.get_surface_shading_attributes("obj").should_be_called().will_return("attributes")
        ifc.run(
            "style.add_surface_style", style="style", ifc_class="IfcSurfaceStyleShading", attributes="attributes"
        ).should_be_called()

        ifc.get_entity("obj").should_be_called().will_return("material")
        style.get_context("obj").should_be_called().will_return("context")
        ifc.run("style.assign_material_style", material="material", style="style", context="context").should_be_called()
        assert subject.add_style(ifc, style, obj="obj") == "style"


class TestRemoveStyle:
    def test_removing_a_style(self, ifc, material, style):
        ifc.get_object("style").should_be_called().will_return("obj")
        ifc.unlink(obj="obj", element="style").should_be_called()
        ifc.run("style.remove_style", style="style").should_be_called()
        ifc.get_entity("obj").should_be_called().will_return("material")
        style.is_editing_styles().should_be_called().will_return(False)
        subject.remove_style(ifc, material, style, style="style")

    def test_removing_a_style_and_reloading_imported_styles(self, ifc, material, style):
        ifc.get_object("style").should_be_called().will_return("obj")
        ifc.unlink(obj="obj", element="style").should_be_called()
        ifc.run("style.remove_style", style="style").should_be_called()
        ifc.get_entity("obj").should_be_called().will_return("material")
        style.is_editing_styles().should_be_called().will_return(True)
        style.get_active_style_type().should_be_called().will_return("style_type")
        style.import_presentation_styles("style_type").should_be_called()
        subject.remove_style(ifc, material, style, style="style")

    def test_removing_an_object_if_it_is_not_still_used_for_a_material(self, ifc, material, style):
        ifc.get_object("style").should_be_called().will_return("obj")
        ifc.unlink(obj="obj", element="style").should_be_called()
        ifc.run("style.remove_style", style="style").should_be_called()
        ifc.get_entity("obj").should_be_called().will_return(None)
        material.delete_object("obj").should_be_called()
        style.is_editing_styles().should_be_called().will_return(False)
        subject.remove_style(ifc, material, style, style="style")


class TestUpdateStyleColours:
    def test_updating_rendering_style_if_available(self, ifc, style):
        style.get_style("obj").should_be_called().will_return("element")
        style.can_support_rendering_style("obj").should_be_called().will_return(True)
        style.get_surface_rendering_style("obj").should_be_called().will_return("style")
        style.get_surface_rendering_attributes("obj").should_be_called().will_return("attributes")
        ifc.run("style.edit_surface_style", style="style", attributes="attributes").should_be_called()
        subject.update_style_colours(ifc, style, obj="obj")

    def test_adding_a_rendering_style_if_not_available(self, ifc, style):
        style.get_style("obj").should_be_called().will_return("element")
        style.can_support_rendering_style("obj").should_be_called().will_return(True)
        style.get_surface_rendering_style("obj").should_be_called().will_return(None)
        style.get_surface_rendering_attributes("obj").should_be_called().will_return("attributes")
        ifc.run(
            "style.add_surface_style", style="element", ifc_class="IfcSurfaceStyleRendering", attributes="attributes"
        ).should_be_called()
        subject.update_style_colours(ifc, style, obj="obj")

    def test_updating_shading_style_as_a_fallback_if_available(self, ifc, style):
        style.get_style("obj").should_be_called().will_return("element")
        style.can_support_rendering_style("obj").should_be_called().will_return(False)
        style.get_surface_shading_style("obj").should_be_called().will_return("style")
        style.get_surface_shading_attributes("obj").should_be_called().will_return("attributes")
        ifc.run("style.edit_surface_style", style="style", attributes="attributes").should_be_called()
        subject.update_style_colours(ifc, style, obj="obj")

    def test_adding_a_shading_style_as_a_fallback_if_not_available(self, ifc, style):
        style.get_style("obj").should_be_called().will_return("element")
        style.can_support_rendering_style("obj").should_be_called().will_return(False)
        style.get_surface_shading_style("obj").should_be_called().will_return(None)
        style.get_surface_shading_attributes("obj").should_be_called().will_return("attributes")
        ifc.run(
            "style.add_surface_style", style="element", ifc_class="IfcSurfaceStyleShading", attributes="attributes"
        ).should_be_called()
        subject.update_style_colours(ifc, style, obj="obj")


class TestUpdateStyleTextures:
    def test_updating_an_existing_texture_style(self, ifc, style):
        style.get_style("obj").should_be_called().will_return("element")
        style.get_uv_maps("representation").should_be_called().will_return("uv_maps")
        ifc.run("style.add_surface_textures", material="obj", uv_maps="uv_maps").should_be_called().will_return(
            "textures"
        )
        style.get_surface_texture_style("obj").should_be_called().will_return("style")
        ifc.run("style.remove_surface_style", style="style").should_be_called()
        ifc.run(
            "style.add_surface_style",
            style="element",
            ifc_class="IfcSurfaceStyleWithTextures",
            attributes={"Textures": "textures"},
        ).should_be_called()
        subject.update_style_textures(ifc, style, obj="obj", representation="representation")

    def test_adding_a_fresh_texture_style(self, ifc, style):
        style.get_style("obj").should_be_called().will_return("element")
        style.get_uv_maps("representation").should_be_called().will_return("uv_maps")
        ifc.run("style.add_surface_textures", material="obj", uv_maps="uv_maps").should_be_called().will_return(
            "textures"
        )
        style.get_surface_texture_style("obj").should_be_called().will_return(None)
        ifc.run(
            "style.add_surface_style",
            style="element",
            ifc_class="IfcSurfaceStyleWithTextures",
            attributes={"Textures": "textures"},
        ).should_be_called()
        subject.update_style_textures(ifc, style, obj="obj", representation="representation")

    def test_removing_an_texture_if_no_textures_can_be_added(self, ifc, style):
        style.get_style("obj").should_be_called().will_return("element")
        style.get_uv_maps("representation").should_be_called().will_return("uv_maps")
        ifc.run("style.add_surface_textures", material="obj", uv_maps="uv_maps").should_be_called().will_return(None)
        style.get_surface_texture_style("obj").should_be_called().will_return("style")
        ifc.run("style.remove_surface_style", style="style").should_be_called()
        subject.update_style_textures(ifc, style, obj="obj", representation="representation")

    def test_doing_nothing_if_no_existing_texture_and_we_cannot_add_a_new_texture(self, ifc, style):
        style.get_style("obj").should_be_called().will_return("element")
        style.get_uv_maps("representation").should_be_called().will_return("uv_maps")
        ifc.run("style.add_surface_textures", material="obj", uv_maps="uv_maps").should_be_called().will_return(None)
        style.get_surface_texture_style("obj").should_be_called().will_return(None)
        subject.update_style_textures(ifc, style, obj="obj", representation="representation")


class TestUnlinkStyle:
    def test_run(self, ifc, style):
        style.get_style("obj").should_be_called().will_return("style")
        ifc.unlink(obj="obj", element="style").should_be_called()
        subject.unlink_style(ifc, style, obj="obj")


class TestEnableEditingStyle:
    def test_run(self, style):
        style.enable_editing("obj").should_be_called()
        style.get_style("obj").should_be_called().will_return("style")
        style.import_surface_attributes("style", "obj").should_be_called()
        subject.enable_editing_style(style, obj="obj")


class TestDisableEditingStyle:
    def test_run(self, style):
        style.disable_editing("obj").should_be_called()
        subject.disable_editing_style(style, obj="obj")


class TestEditStyle:
    def test_run(self, ifc, style):
        style.get_style("obj").should_be_called().will_return("style")
        style.export_surface_attributes("obj").should_be_called().will_return("attributes")
        ifc.run("style.edit_presentation_style", style="style", attributes="attributes").should_be_called()
        style.disable_editing("obj").should_be_called()
        subject.edit_style(ifc, style, obj="obj")


class TestLoadStyles:
    def test_run(self, style):
        style.import_presentation_styles("style_type").should_be_called()
        style.enable_editing_styles().should_be_called()
        subject.load_styles(style, style_type="style_type")


class TestDisableEditingStyles:
    def test_run(self, style):
        style.disable_editing_styles().should_be_called()
        subject.disable_editing_styles(style)
