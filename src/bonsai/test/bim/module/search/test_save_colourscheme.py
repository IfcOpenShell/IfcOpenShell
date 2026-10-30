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

import json

import bpy
import ifcopenshell.api.group
import pytest

import bonsai.tool as tool
from test.bim.bootstrap import NewFile

pytestmark = pytest.mark.search


def groups_named(name):
    return [g for g in tool.Ifc.get().by_type("IfcGroup") if g.Name == name]


class TestSaveColourscheme(NewFile):
    def test_adding_a_new_colourscheme(self):
        bpy.ops.bim.create_project()
        bpy.ops.bim.save_colourscheme(name="Scheme")
        (group,) = groups_named("Scheme")
        assert tool.Group.get_description_type(group) == "BBIM_Search"
        assert "colourscheme" in json.loads(group.Description)

    def test_adding_to_a_saved_search_with_the_same_name(self):
        bpy.ops.bim.create_project()
        description = json.dumps({"type": "BBIM_Search", "query": "IfcWall"})
        search = ifcopenshell.api.group.add_group(tool.Ifc.get(), name="Walls", description=description)
        bpy.ops.bim.save_colourscheme(name="Walls")
        assert groups_named("Walls") == [search]
        data = json.loads(search.Description)
        assert data["query"] == "IfcWall"
        assert "colourscheme" in data

    @pytest.mark.parametrize("description", [None, "Not JSON"])
    def test_not_reusing_a_user_group_with_the_same_name(self, description):
        bpy.ops.bim.create_project()
        user_group = ifcopenshell.api.group.add_group(tool.Ifc.get(), name="Scheme", description=description)
        bpy.ops.bim.save_colourscheme(name="Scheme")
        assert len(groups_named("Scheme")) == 2
        assert user_group.Description == description
