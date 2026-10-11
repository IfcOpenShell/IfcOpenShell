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

import bpy
import pytest

import bonsai.tool as tool
from test.bim.bootstrap import NewIfc

pytestmark = pytest.mark.wall


def select_only(*objs):
    bpy.ops.object.select_all(action="DESELECT")
    for obj in objs:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = objs[-1]


def add_occurrence(ifc_class, type_name, location):
    ifc_file = tool.Ifc.get()
    props = tool.Model.get_model_props()
    props.ifc_class = ifc_class
    props.relating_type_id = str(next(e for e in ifc_file.by_type(ifc_class) if e.Name == type_name).id())
    bpy.context.scene.cursor.location = location
    bpy.ops.bim.add_occurrence()


def add_two_walls_and_a_door():
    bpy.ops.bim.select_library_file(filepath="./bonsai/bim/data/libraries/IFC4 Demo Library.ifc", append_all=True)
    add_occurrence("IfcWallType", "WAL100", (0, 0, 0))
    first_wall = bpy.data.objects["IfcWall/Wall"]
    select_only(first_wall)
    bpy.context.scene.cursor.location = (10, 0, 0)
    bpy.ops.bim.hotkey(hotkey="S_E")
    add_occurrence("IfcWallType", "WAL100", (0, 5, 0))
    second_wall = bpy.data.objects["IfcWall/Wall.001"]
    add_occurrence("IfcDoorType", "DT01", (7, 0, 0))
    return first_wall, second_wall, bpy.data.objects["IfcDoor/Door"]


class TestTrimAndMergePoll(NewIfc):
    def test_buttons_are_disabled_unless_two_walls_are_selected(self):
        first_wall, second_wall, _door = add_two_walls_and_a_door()

        select_only(first_wall)
        assert not bpy.ops.bim.trim_wall.poll()
        assert not bpy.ops.bim.merge_wall.poll()

        select_only(first_wall, second_wall)
        assert bpy.ops.bim.trim_wall.poll()
        assert bpy.ops.bim.merge_wall.poll()

    def test_merge_is_disabled_when_one_of_the_two_items_is_not_a_wall(self):
        first_wall, _second_wall, door = add_two_walls_and_a_door()

        select_only(first_wall, door)

        assert not bpy.ops.bim.merge_wall.poll()
        assert not bpy.ops.bim.trim_wall.poll()
