# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2026
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

from types import SimpleNamespace

import blf
import bpy
from bpy_extras import view3d_utils

import bonsai.tool as tool
from bonsai.bim.module.nest.decorator import NestModeDecorator
from test.bim.bootstrap import NewFile


class TestNestModeDecorator(NewFile):
    def test_nest_label_is_skipped_when_nest_is_behind_the_camera(self, monkeypatch):
        nest_obj = bpy.data.objects.new("Nest", None)
        bpy.context.scene.collection.objects.link(nest_obj)
        tool.Nest.get_nest_props().editing_nest = nest_obj
        monkeypatch.setattr(view3d_utils, "location_3d_to_region_2d", lambda *args, **kwargs: None)
        draw_calls = []
        monkeypatch.setattr(blf, "draw", lambda *args, **kwargs: draw_calls.append(args))
        context = SimpleNamespace(mode="OBJECT", region=SimpleNamespace(data=None), selected_objects=[])
        NestModeDecorator().draw_nest_name(context)
        assert draw_calls == []
