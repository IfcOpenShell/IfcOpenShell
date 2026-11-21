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
from unittest import mock

import blf
import bpy
import ifcopenshell
import ifcopenshell.guid
from mathutils import Vector

import bonsai.bim.module.structural.decorator as decorator_module
import bonsai.tool as tool
from bonsai.bim.module.structural.decorator import LoadsDecorator
from bonsai.bim.module.structural.load_decoration_data import ScreenGrid, ShaderInfo, box_crosses_segments
from test.bim.bootstrap import NewFile


class TestLinearLoadsForMemberWithoutMesh(NewFile):
    def _shader_info(self, ifc):
        member = ifc.createIfcStructuralCurveMember(
            GlobalId=ifcopenshell.guid.new(), PredefinedType="RIGID_JOINED_MEMBER"
        )
        action = ifc.createIfcStructuralLinearAction(GlobalId=ifcopenshell.guid.new(), PredefinedType="CONST")
        info = ShaderInfo()
        info.curve_members = {"1": {"member": member, "activities": [(action, 1.0)]}}
        return info, member

    def test_member_without_object(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        info, _ = self._shader_info(ifc)
        info.get_linear_loads()
        assert info.info == []

    def test_member_with_empty_mesh(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        info, member = self._shader_info(ifc)
        tool.Ifc.link(member, bpy.data.objects.new("Member", bpy.data.meshes.new("Member")))
        info.get_linear_loads()
        assert info.info == []


class TestBoxCrossesSegments:
    # A label's box from (0, 0), 10 wide and 5 high.
    def test_lines_crossing_or_inside(self):
        assert box_crosses_segments(0, 0, 10, 5, [((-5, 2), (15, 2))])
        assert box_crosses_segments(0, 0, 10, 5, [((2, 1), (3, 2))])
        assert box_crosses_segments(0, 0, 10, 5, [((-1, 4), (1, 6))])  # Across a corner.

    def test_lines_clear_of_it(self):
        assert not box_crosses_segments(0, 0, 10, 5, [((-5, 8), (15, 8))])
        assert not box_crosses_segments(0, 0, 10, 5, [((12, 0), (20, 10))])
        assert not box_crosses_segments(0, 0, 10, 5, [])

    def test_any_of_several(self):
        assert box_crosses_segments(0, 0, 10, 5, [((-5, 8), (15, 8)), ((5, -5), (5, 10))])


class TestScreenGrid:
    def test_boxes_in_other_cells_or_beyond_the_margin_are_clear(self):
        grid = ScreenGrid(cell=10)
        grid.add_box(0, 0, 25, 5)  # Across three cells.
        assert grid.overlaps_box(20, 2, 4, 4)
        assert not grid.overlaps_box(30, 0, 4, 4)
        assert grid.overlaps_box(27, 0, 4, 4, margin=3)

    def test_a_line_through_cells_it_does_not_end_in(self):
        grid = ScreenGrid(cell=10)
        grid.add_segment((-50, 15), (50, 15))
        assert grid.crosses_segment(0, 10, 5, 10)
        assert not grid.crosses_segment(0, 20, 5, 5)


class TestPlaceLabelsBeside:
    def place(self, loads: list[tuple[float, float]], length: float = 30.0) -> tuple[list, list]:
        """Label downward arrows ending at the points given on screen, at their tips, as point loads are"""
        arrows = [((x, y + length), (x, y)) for x, y in loads]
        placed = ScreenGrid()
        for arrow in arrows:
            placed.add_segment(*arrow)
        context = SimpleNamespace(region=None, region_data=None)
        decorator = LoadsDecorator.__new__(LoadsDecorator)
        boxes = []
        # On screen as in the X-Z plane, so that a position (x, 0, y) is drawn at (x, y).
        with mock.patch.object(decorator_module, "location_3d_to_region_2d", lambda r, v, p: Vector((p[0], p[2]))):
            for x, y in loads:
                bx, by = decorator.place_beside((x, 0, y), (0, 0, -1), x, y, "12.5 kN", context, placed)
                boxes.append((bx, by, *blf.dimensions(0, "12.5 kN")))
        return arrows, boxes

    def test_labels_keep_off_the_arrows_beside_them(self):
        # Rows of loads closer than a label is wide, as along a beam, whose labels would fall on the next row's arrows.
        arrows, boxes = self.place([(40.0 * i, 35.0 * j) for i in range(8) for j in range(4)])
        assert not any(box_crosses_segments(*box, arrows) for box in boxes)

    def test_labels_keep_off_each_other(self):
        _, boxes = self.place([(10.0 * i, 0.0) for i in range(6)])
        for i, (x1, y1, w1, h1) in enumerate(boxes):
            for x2, y2, w2, h2 in boxes[i + 1 :]:
                assert not (x1 < x2 + w2 and x2 < x1 + w1 and y1 < y2 + h2 and y2 < y1 + h1)
