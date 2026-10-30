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

# This file was generated with the assistance of an AI coding tool.

import json

import bpy
import pytest

import bonsai.tool as tool
from bonsai.bim.module.search.data import ColourByPropertyData
from test.bim.bootstrap import NewFile

pytestmark = pytest.mark.search


class TestColourschemeKey(NewFile):
    def _setup(self):
        bpy.ops.bim.create_project()
        bpy.ops.mesh.primitive_cube_add()
        bpy.ops.bim.assign_class(ifc_class="IfcWall", predefined_type="", userdefined_type="")
        ColourByPropertyData.is_loaded = False
        props = tool.Search.get_search_props()
        colour = props.colourscheme.add()
        colour.name = "Wall"
        colour.total = 1
        return props

    def test_key_is_saved_and_restored(self):
        props = self._setup()
        props.colourscheme_key = "Name"
        bpy.ops.bim.save_colourscheme(name="Scheme")
        group = next(g for g in tool.Ifc.get().by_type("IfcGroup") if g.Name == "Scheme")
        assert json.loads(group.Description)["colourscheme_key"] == "Name"

        props.colourscheme_key = "QUERY"
        ColourByPropertyData.is_loaded = False
        props.saved_colourschemes = str(group.id())
        bpy.ops.bim.load_colourscheme()
        assert props.colourscheme_key == "Name"

    def test_unavailable_key_falls_back_to_custom_query(self):
        props = self._setup()
        props.colourscheme_key = "Name"
        bpy.ops.bim.save_colourscheme(name="Scheme")
        group = next(g for g in tool.Ifc.get().by_type("IfcGroup") if g.Name == "Scheme")
        description = json.loads(group.Description)
        description["colourscheme_key"] = 'Missing."Property"'
        group.Description = json.dumps(description)

        ColourByPropertyData.is_loaded = False
        props.saved_colourschemes = str(group.id())
        bpy.ops.bim.load_colourscheme()
        assert props.colourscheme_key == "QUERY"
