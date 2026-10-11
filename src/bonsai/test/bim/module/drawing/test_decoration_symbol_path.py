# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2026 Dion Moult <dion@thinkmoult.com>
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
#
# This file was generated with the assistance of an AI coding tool.

import os
from types import SimpleNamespace
from unittest.mock import Mock, patch

import bpy
import ifcopenshell.api.pset
import pytest
from mathutils import Vector

import bonsai.tool as tool
from bonsai.bim.module.drawing.decoration import BaseDecorator
from test.bim.bootstrap import NewFile

CUSTOM_SYMBOLS = '<svg xmlns="http://www.w3.org/2000/svg"><g id="custom-tag"><circle cx="0" cy="0" r="5"/></g></svg>'


class TestDrawGlyph(NewFile):
    def test_glyph_is_drawn_at_its_printed_size(self):
        decorator = Mock()
        decorator.get_symbols_path.return_value = BaseDecorator.get_symbols_path(None)
        decorator.camera_zoom_to_factor.return_value = 1
        decorator.get_camera_width_mm.return_value = 0.5
        decorator.get_viewport_drawing_scale = lambda context: BaseDecorator.get_viewport_drawing_scale(
            decorator, context
        )
        region_3d = SimpleNamespace(view_camera_zoom=0)
        context = SimpleNamespace(region=SimpleNamespace(width=1000), space_data=SimpleNamespace(region_3d=region_3d))

        with patch("bonsai.bim.module.drawing.decoration.worldspace_to_winspace", return_value=[Vector((0, 0, 0))]):
            BaseDecorator.draw_glyph(decorator, context, "door-tag", Vector((0, 0, 0)))

        xs = [vert[0] for vert in decorator.draw_lines.call_args.args[2]]
        assert max(xs) - min(xs) == pytest.approx(20)


class TestGetSymbolsPath(NewFile):
    def write_symbols(self):
        path = os.path.join(bpy.app.tempdir, "custom-symbols.svg")
        with open(path, "w") as f:
            f.write(CUSTOM_SYMBOLS)
        return path

    def test_falls_back_to_the_bundled_symbols(self):
        bpy.ops.bim.create_project()
        path = BaseDecorator.get_symbols_path(None)
        assert os.path.basename(path) == "symbols.svg"
        assert os.path.exists(path)

    def test_uses_the_project_symbols_path(self):
        bpy.ops.bim.create_project()
        custom = self.write_symbols()
        project = tool.Ifc.get().by_type("IfcProject")[0]
        pset = ifcopenshell.api.pset.add_pset(tool.Ifc.get(), product=project, name="BBIM_Documentation")
        ifcopenshell.api.pset.edit_pset(tool.Ifc.get(), pset=pset, properties={"SymbolsPath": custom})
        assert BaseDecorator.get_symbols_path(None) == custom

    def test_uses_the_preference_symbols_path(self):
        bpy.ops.bim.create_project()
        custom = self.write_symbols()
        doc_prefs = tool.Blender.get_addon_preferences().doc
        original = doc_prefs.symbols_path
        doc_prefs.symbols_path = custom
        try:
            assert BaseDecorator.get_symbols_path(None) == custom
        finally:
            doc_prefs.symbols_path = original
