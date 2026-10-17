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

import bpy
import ifcopenshell.api.group

import bonsai.tool as tool
from bonsai.bim.module.group.data import ObjectGroupsData
from test.bim.bootstrap import NewFile


class TestObjectGroupsData(NewFile):
    def setup_object(self):
        bpy.ops.bim.create_project()
        ifc = tool.Ifc.get()
        bpy.ops.mesh.primitive_cube_add()
        obj = bpy.context.active_object
        wall = ifc.create_entity("IfcWall")
        tool.Ifc.link(wall, obj)
        user_group = ifcopenshell.api.group.add_group(ifc, name="Furniture")
        drawing_group = ifcopenshell.api.group.add_group(ifc, name="Plan")
        drawing_group.ObjectType = "DRAWING"
        ifcopenshell.api.group.assign_group(ifc, products=[wall], group=user_group)
        ifcopenshell.api.group.assign_group(ifc, products=[wall], group=drawing_group)

    def test_hiding_internal_groups(self):
        self.setup_object()
        ObjectGroupsData.load()
        assert [g["name"] for g in ObjectGroupsData.data["groups"]] == ["Furniture"]
        assert ObjectGroupsData.data["total_hidden"] == 1

    def test_showing_internal_groups_when_toggled(self):
        self.setup_object()
        tool.Group.get_group_props().should_show_internal = True
        ObjectGroupsData.load()
        assert sorted(g["name"] for g in ObjectGroupsData.data["groups"]) == ["Furniture", "Plan"]
        assert ObjectGroupsData.data["total_hidden"] == 0
