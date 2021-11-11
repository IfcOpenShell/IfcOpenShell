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
from test.core.bootstrap import ifc, style


class TestAddStyle:
    def predict(self, ifc, style, obj="obj"):
        style.get_name(obj).should_be_called().will_return("name")
        ifc.run("style.add_style", name="name").should_be_called().will_return("style")
        ifc.link("style", obj).should_be_called()
        style.get_surface_rendering_attributes(obj).should_be_called().will_return("attributes")
        ifc.run(
            "style.add_surface_style", style="style", ifc_class="IfcSurfaceStyleRendering", attributes="attributes"
        ).should_be_called()
        ifc.get_entity(obj).should_be_called().will_return(None)

    def test_it_adds_a_style_with_rendering_attributes(self, ifc, style):
        self.predict(ifc, style)
        assert subject.add_style(ifc, style, obj="obj") == "style"

    def test_adding_a_style_linked_to_a_material(self, ifc, style):
        style.get_name("obj").should_be_called().will_return("name")
        ifc.run("style.add_style", name="name").should_be_called().will_return("style")
        ifc.link("style", "obj").should_be_called()
        style.get_surface_rendering_attributes("obj").should_be_called().will_return("attributes")
        ifc.run(
            "style.add_surface_style", style="style", ifc_class="IfcSurfaceStyleRendering", attributes="attributes"
        ).should_be_called()
        ifc.get_entity("obj").should_be_called().will_return("material")
        style.get_context("obj").should_be_called().will_return("context")
        ifc.run("style.assign_material_style", material="material", style="style", context="context").should_be_called()
        assert subject.add_style(ifc, style, obj="obj") == "style"


class TestRemoveStyle:
    def test_run(self, ifc, style):
        style.get_style("obj").should_be_called().will_return("style")
        ifc.unlink(obj="obj", element="style").should_be_called()
        ifc.run("style.remove_style", style="style").should_be_called()
        subject.remove_style(ifc, style, obj="obj")


class TestUpdateStyleColours:
    def test_updating_rendering_colours_if_available(self, ifc, style):
        style.get_surface_rendering_style("obj").should_be_called().will_return("style")
        style.get_surface_rendering_attributes("obj").should_be_called().will_return("attributes")
        ifc.run("style.edit_surface_style", style="style", attributes="attributes").should_be_called()
        subject.update_style_colours(ifc, style, obj="obj")

    def test_updating_shading_colours_as_a_fallback_if_available(self, ifc, style):
        style.get_surface_rendering_style("obj").should_be_called().will_return(None)
        style.get_surface_shading_style("obj").should_be_called().will_return("style")
        style.get_surface_shading_attributes("obj").should_be_called().will_return("attributes")
        ifc.run("style.edit_surface_style", style="style", attributes="attributes").should_be_called()
        subject.update_style_colours(ifc, style, obj="obj")


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
