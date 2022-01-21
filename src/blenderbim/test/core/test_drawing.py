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

import blenderbim.core.drawing as subject
from test.core.bootstrap import ifc, drawing


class TestEnableEditingText:
    def test_run(self, drawing):
        drawing.enable_editing_text("obj").should_be_called()
        drawing.import_text_attributes("obj").should_be_called()
        subject.enable_editing_text(drawing, obj="obj")


class TestDisableEditingText:
    def test_run(self, drawing):
        drawing.disable_editing_text("obj").should_be_called()
        subject.disable_editing_text(drawing, obj="obj")


class TestEditText:
    def test_run(self, ifc, drawing):
        drawing.get_text_literal("obj").should_be_called().will_return("text")
        drawing.export_text_literal_attributes("obj").should_be_called().will_return("attributes")
        ifc.run("drawing.edit_text_literal", text_literal="text", attributes="attributes").should_be_called()
        drawing.update_text_value("obj").should_be_called()
        drawing.disable_editing_text("obj").should_be_called()
        subject.edit_text(ifc, drawing, obj="obj")


class TestEnableEditingTextProduct:
    def test_run(self, drawing):
        drawing.enable_editing_text_product("obj").should_be_called()
        drawing.import_text_product("obj").should_be_called()
        subject.enable_editing_text_product(drawing, obj="obj")


class TestDisableEditingTextProduct:
    def test_run(self, drawing):
        drawing.disable_editing_text_product("obj").should_be_called()
        subject.disable_editing_text_product(drawing, obj="obj")


class TestEditTextProduct:
    def test_run(self, ifc, drawing):
        ifc.get_entity("obj").should_be_called().will_return("element")
        drawing.get_text_product("element").should_be_called().will_return("existing_product")
        ifc.run(
            "drawing.unassign_product", relating_product="existing_product", related_object="element"
        ).should_be_called()
        ifc.run("drawing.assign_product", relating_product="product", related_object="element").should_be_called()
        drawing.update_text_value("obj").should_be_called()
        drawing.disable_editing_text_product("obj").should_be_called()
        subject.edit_text_product(ifc, drawing, obj="obj", product="product")
