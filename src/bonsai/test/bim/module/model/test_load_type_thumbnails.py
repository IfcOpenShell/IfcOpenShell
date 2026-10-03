# This file was generated with the assistance of an AI coding tool.
# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2025 Dion Moult <dion@thinkmoult.com>
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

import types

import bpy

import bonsai.bim.module.model.product as product_module
import bonsai.tool as tool
import bonsai.tool.model as model_module
from test.bim.bootstrap import NewFile


class ForegroundBpy:
    def __init__(self, real):
        self._real = real
        self.app = types.SimpleNamespace(background=False)

    def __getattr__(self, name):
        return getattr(self._real, name)


class TestLoadTypeThumbnails(NewFile):
    def test_kilometre_demo_project_survives_undrawable_profile(self, monkeypatch):
        monkeypatch.setattr(product_module, "bpy", ForegroundBpy(bpy))
        monkeypatch.setattr(model_module, "bpy", ForegroundBpy(bpy))
        bpy.context.scene.unit_settings.system = "METRIC"
        bpy.context.scene.unit_settings.length_unit = "KILOMETERS"
        props = tool.Project.get_project_props()
        props.export_schema = "IFC4"
        props.template_file = "IFC4 Demo Template.ifc"
        bpy.ops.bim.create_project()
        model_props = tool.Model.get_model_props()
        assert model_props.extrusion_depth == 3
        assert model_props.rl1 == 0
