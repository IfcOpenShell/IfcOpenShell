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

"""Wall and profile joins keep the side of each element the user clicked (#10152).

Without a click, or for joiners not asked to look at clicks (tools joining
elements they just drew), the old midpoint rule must still decide."""

from unittest.mock import Mock, patch

import pytest
from mathutils import Vector

import bonsai.tool as tool
from bonsai.bim.module.model.profile import DumbProfileJoiner
from bonsai.bim.module.model.wall import DumbWallJoiner

pytestmark = pytest.mark.model


@pytest.fixture(autouse=True)
def no_clicks():
    tool.Model.clicked_rays.clear()
    yield
    tool.Model.clicked_rays.clear()


def _obj(name):
    obj = Mock()
    obj.name = name
    return obj


def _click(obj, x, y):
    """A plan-view click straight down through (x, y)."""
    tool.Model.clicked_rays[obj.name] = (Vector((x, y, 10.0)), Vector((0.0, 0.0, -1.0)))


def _joiner(cls, keep_clicked_side):
    joiner = cls.__new__(cls)  # Skip __init__, which needs a loaded IFC.
    joiner.keep_clicked_side = keep_clicked_side
    return joiner


class TestWallConnectPath:
    """wall1 runs (0,0)->(10,0); wall2 runs (5,-2)->(5,8), crossing it at 50% / 20%."""

    LINES = {
        "wall1": [Vector((0.0, 0.0, 0.0)), Vector((10.0, 0.0, 0.0))],
        "wall2": [Vector((5.0, -2.0, 0.0)), Vector((5.0, 8.0, 0.0))],
    }

    def _connect(self, keep_clicked_side=True, is_atpath=False, clicks=()):
        obj1, obj2 = _obj("wall1"), _obj("wall2")
        for name, x, y in clicks:
            _click({"wall1": obj1, "wall2": obj2}[name], x, y)
        joiner = _joiner(DumbWallJoiner, keep_clicked_side)
        joiner.get_world_reference_line = lambda obj, element: self.LINES[obj.name]
        with (
            patch.object(tool.Ifc, "get_entity", side_effect=lambda obj: f"{obj.name}-element"),
            patch.object(tool.Ifc, "get"),
            patch("ifcopenshell.api.geometry.connect_path") as connect_path,
            patch("ifcopenshell.api.geometry.connect_wall") as connect_wall,
        ):
            joiner.connect_path(obj1, obj2, is_atpath=is_atpath)
        return connect_path, connect_wall

    def test_keeps_the_clicked_side_of_both_walls(self):
        connect_path, connect_wall = self._connect(clicks=[("wall1", 8.0, 0.2), ("wall2", 5.0, 6.0)])
        connect_wall.assert_not_called()
        kwargs = connect_path.call_args.kwargs
        assert (kwargs["relating_connection"], kwargs["related_connection"]) == ("ATSTART", "ATSTART")

    def test_the_other_side_when_clicked_there(self):
        connect_path, _ = self._connect(clicks=[("wall1", 2.0, 0.0), ("wall2", 5.0, -1.5)])
        kwargs = connect_path.call_args.kwargs
        assert (kwargs["relating_connection"], kwargs["related_connection"]) == ("ATEND", "ATEND")

    def test_an_unclicked_wall_falls_back_to_the_nearer_end(self):
        connect_path, _ = self._connect(clicks=[("wall1", 8.0, 0.0)])
        kwargs = connect_path.call_args.kwargs
        assert (kwargs["relating_connection"], kwargs["related_connection"]) == ("ATSTART", "ATSTART")

    def test_extending_to_a_wall_connects_at_its_path(self):
        connect_path, _ = self._connect(is_atpath=True, clicks=[("wall1", 8.0, 0.0), ("wall2", 5.0, 6.0)])
        kwargs = connect_path.call_args.kwargs
        assert (kwargs["relating_connection"], kwargs["related_connection"]) == ("ATSTART", "ATPATH")

    def test_no_clicks_leaves_it_to_connect_wall(self):
        connect_path, connect_wall = self._connect()
        connect_path.assert_not_called()
        connect_wall.assert_called_once_with(
            connect_wall.call_args.args[0], wall1="wall1-element", wall2="wall2-element", is_atpath=False
        )

    def test_clicks_are_ignored_unless_asked_for(self):
        connect_path, connect_wall = self._connect(keep_clicked_side=False, clicks=[("wall1", 8.0, 0.0)])
        connect_path.assert_not_called()
        connect_wall.assert_called_once()


class TestProfileConnectionEnd:
    AXIS = [Vector((0.0, 0.0, 0.0)), Vector((0.0, 0.0, 10.0))]  # A column, seen from the side.

    def _side_click(self, obj, z):
        tool.Model.clicked_rays[obj.name] = (Vector((10.0, 0.0, z)), Vector((-1.0, 0.0, 0.0)))

    def test_keeps_the_clicked_side(self):
        obj = _obj("column")
        self._side_click(obj, 9.0)
        assert _joiner(DumbProfileJoiner, True).get_connection_end(obj, self.AXIS, 0.6) == "ATSTART"
        self._side_click(obj, 1.0)
        assert _joiner(DumbProfileJoiner, True).get_connection_end(obj, self.AXIS, 0.6) == "ATEND"

    def test_falls_back_to_the_midpoint_rule(self):
        obj = _obj("column")
        assert _joiner(DumbProfileJoiner, True).get_connection_end(obj, self.AXIS, 0.6) == "ATEND"
        self._side_click(obj, 9.0)
        assert _joiner(DumbProfileJoiner, False).get_connection_end(obj, self.AXIS, 0.6) == "ATEND"
