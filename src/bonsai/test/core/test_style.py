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

import bonsai.core.style as subject
from test.core.bootstrap import ifc, material, style, spatial


class TestAddStyle:
    def add_style_common(self, ifc, style):
        style.get_name("obj").should_be_called().will_return("name")
        ifc.run("style.add_style", name="name").should_be_called().will_return("element")
        ifc.link("element", "obj").should_be_called()

    def test_it_adds_a_style_with_rendering_attributes(self, ifc, style):
        self.add_style_common(ifc, style)

        style.can_support_rendering_style("obj").should_be_called().will_return(True)
        style.get_surface_rendering_attributes("obj").should_be_called().will_return("attributes")
        ifc.run(
            "style.add_surface_style", style="element", ifc_class="IfcSurfaceStyleRendering", attributes="attributes"
        ).should_be_called()

        assert subject.add_style(ifc, style, obj="obj") == "element"

    def test_it_adds_a_style_with_shading_attributes(self, ifc, style):
        self.add_style_common(ifc, style)

        style.can_support_rendering_style("obj").should_be_called().will_return(False)
        style.get_surface_shading_attributes("obj").should_be_called().will_return("attributes")
        ifc.run(
            "style.add_surface_style", style="element", ifc_class="IfcSurfaceStyleShading", attributes="attributes"
        ).should_be_called()
        assert subject.add_style(ifc, style, obj="obj") == "element"


class TestRemoveStyle:
    def remove_a_style_common(self, ifc, style):
        ifc.get_object("style").should_be_called().will_return("obj")
        ifc.unlink(element="style").should_be_called()
        ifc.run("style.remove_style", style="style").should_be_called()
        style.delete_object("obj").should_be_called()
        style.get_active_style_type().should_be_called().will_return("style_type")

    def test_removing_a_style(self, ifc, style):
        self.remove_a_style_common(ifc, style)
        subject.remove_style(ifc, style, style="style")

    def test_removing_a_style_and_reloading_imported_styles(self, ifc, style):
        self.remove_a_style_common(ifc, style)
        style.is_editing_styles().should_be_called().will_return(True)
        style.import_presentation_styles("style_type").should_be_called()
        subject.remove_style(ifc, style, style="style", reload_styles_ui=True)


class TestUpdateStyleColours:
    def test_updating_rendering_style_if_available(self, ifc, style):
        ifc.get_entity("obj").should_be_called().will_return("element")
        style.can_support_rendering_style("obj").should_be_called().will_return(True)

        style.get_surface_rendering_style("obj").should_be_called().will_return("rendering_style")
        style.get_texture_style("obj").should_be_called().will_return("texture_style")
        style.get_surface_rendering_attributes("obj", "verbose").should_be_called().will_return("attributes")
        ifc.run("style.edit_surface_style", style="rendering_style", attributes="attributes").should_be_called()

        ifc.run("style.add_surface_textures", material="obj").should_be_called().will_return("textures")
        ifc.run(
            "style.edit_surface_style", style="texture_style", attributes={"Textures": "textures"}
        ).should_be_called().will_return("textures")

        subject.update_style_colours(ifc, style, obj="obj", verbose="verbose")

    def test_adding_a_rendering_style_if_not_available(self, ifc, style):
        ifc.get_entity("obj").should_be_called().will_return("element")
        style.can_support_rendering_style("obj").should_be_called().will_return(True)

        style.get_surface_rendering_style("obj").should_be_called().will_return(None)
        style.get_texture_style("obj").should_be_called().will_return(None)
        style.get_surface_rendering_attributes("obj", "verbose").should_be_called().will_return("attributes")
        ifc.run(
            "style.add_surface_style", style="element", ifc_class="IfcSurfaceStyleRendering", attributes="attributes"
        ).should_be_called()

        ifc.run("style.add_surface_textures", material="obj").should_be_called().will_return("textures")
        ifc.run(
            "style.add_surface_style",
            style="element",
            ifc_class="IfcSurfaceStyleWithTextures",
            attributes={"Textures": "textures"},
        ).should_be_called()

        subject.update_style_colours(ifc, style, obj="obj", verbose="verbose")

    def test_updating_shading_style_as_a_fallback_if_available(self, ifc, style):
        ifc.get_entity("obj").should_be_called().will_return("element")
        style.can_support_rendering_style("obj").should_be_called().will_return(False)
        style.get_surface_shading_style("obj").should_be_called().will_return("style")
        style.get_surface_shading_attributes("obj").should_be_called().will_return("attributes")
        ifc.run("style.edit_surface_style", style="style", attributes="attributes").should_be_called()
        subject.update_style_colours(ifc, style, obj="obj")

    def test_adding_a_shading_style_as_a_fallback_if_not_available(self, ifc, style):
        ifc.get_entity("obj").should_be_called().will_return("element")
        style.can_support_rendering_style("obj").should_be_called().will_return(False)
        style.get_surface_shading_style("obj").should_be_called().will_return(None)
        style.get_surface_shading_attributes("obj").should_be_called().will_return("attributes")
        ifc.run(
            "style.add_surface_style", style="element", ifc_class="IfcSurfaceStyleShading", attributes="attributes"
        ).should_be_called()
        subject.update_style_colours(ifc, style, obj="obj")


class TestUpdateStyleTextures:
    def test_updating_an_existing_texture_style(self, ifc, style):
        ifc.get_entity("obj").should_be_called().will_return("element")
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
        ifc.get_entity("obj").should_be_called().will_return("element")
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
        ifc.get_entity("obj").should_be_called().will_return("element")
        style.get_uv_maps("representation").should_be_called().will_return("uv_maps")
        ifc.run("style.add_surface_textures", material="obj", uv_maps="uv_maps").should_be_called().will_return(None)
        style.get_surface_texture_style("obj").should_be_called().will_return("style")
        ifc.run("style.remove_surface_style", style="style").should_be_called()
        subject.update_style_textures(ifc, style, obj="obj", representation="representation")

    def test_doing_nothing_if_no_existing_texture_and_we_cannot_add_a_new_texture(self, ifc, style):
        ifc.get_entity("obj").should_be_called().will_return("element")
        style.get_uv_maps("representation").should_be_called().will_return("uv_maps")
        ifc.run("style.add_surface_textures", material="obj", uv_maps="uv_maps").should_be_called().will_return(None)
        style.get_surface_texture_style("obj").should_be_called().will_return(None)
        subject.update_style_textures(ifc, style, obj="obj", representation="representation")


class TestUnlinkStyle:
    def test_run(self, ifc):
        ifc.unlink(element="style").should_be_called()
        subject.unlink_style(ifc, style="style")


class TestEnableEditingStyle:
    def test_run(self, style):
        style.enable_editing("style_element").should_be_called()
        style.import_surface_attributes("style_element").should_be_called()
        subject.enable_editing_style(style, style="style_element")


class TestDisableEditingStyle:
    def test_run(self, style):
        style.get_currently_edited_material().should_be_called().will_return("obj")
        style.reload_material_from_ifc("obj").should_be_called()
        style.disable_editing().should_be_called()
        style.reload_material_from_ifc("obj").should_be_called()
        subject.disable_editing_style(style)


class TestEditStyle:
    def test_run_side_attr_updated(self, ifc, style):
        style.get_currently_edited_material().should_be_called().will_return("obj")
        ifc.get_entity("obj").should_be_called().will_return("style_element")
        style.export_surface_attributes().should_be_called().will_return("attributes")
        style.is_style_side_attribute_edited("style_element", "attributes").should_be_called().will_return(True)
        ifc.run("style.edit_presentation_style", style="style_element", attributes="attributes").should_be_called()
        style.disable_editing().should_be_called()
        style.get_active_style_type().should_be_called().will_return("style_type")

        # Calling core.load_styles.
        style.import_presentation_styles("style_type").should_be_called()
        style.enable_editing_styles().should_be_called()

        style.reload_repersentations("style_element").should_be_called()

        subject.edit_style(ifc, style)

    def test_run_side_attr_unchanged(self, ifc, style):
        style.get_currently_edited_material().should_be_called().will_return("obj")
        ifc.get_entity("obj").should_be_called().will_return("style_element")
        style.export_surface_attributes().should_be_called().will_return("attributes")
        style.is_style_side_attribute_edited("style_element", "attributes").should_be_called().will_return(False)
        ifc.run("style.edit_presentation_style", style="style_element", attributes="attributes").should_be_called()
        style.disable_editing().should_be_called()
        style.get_active_style_type().should_be_called().will_return("style_type")

        # Calling core.load_styles.
        style.import_presentation_styles("style_type").should_be_called()
        style.enable_editing_styles().should_be_called()

        subject.edit_style(ifc, style)


class TestLoadStyles:
    def test_run(self, style):
        style.import_presentation_styles("style_type").should_be_called()
        style.enable_editing_styles().should_be_called()
        subject.load_styles(style, style_type="style_type")


class TestDisableEditingStyles:
    def test_run(self, style):
        style.disable_editing_styles().should_be_called()
        subject.disable_editing_styles(style)


class TestSelectByStyle:
    def test_run(self, style, spatial):
        style.get_elements_by_style("style").should_be_called().will_return("elements")
        spatial.select_products("elements").should_be_called()
        subject.select_by_style(style, spatial, style="style")
