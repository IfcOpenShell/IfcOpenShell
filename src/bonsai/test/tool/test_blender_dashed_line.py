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

"""Tests for the world-space dashed-line segmentation helper in tool.Blender.

The helper slices each input edge into world-space dash chunks so callers can
build a vanilla LINES batch (any shader, including ``POLYLINE_UNIFORM_COLOR``)
that renders as dashes. Sharing the front-pass shader for the occluded back
pass is what keeps depth values coherent between the visible / occluded
outlines — a custom dashed shader against a builtin solid shader produces
inter-pass z-fighting and the wrong portion of the outline ends up dashed."""

import math
import types

import bpy
import pytest

import bonsai.tool as tool

pytestmark = pytest.mark.model


@pytest.fixture(autouse=True)
def _require_real_bpy():
    if not isinstance(bpy, types.ModuleType) or hasattr(bpy, "_mock_name"):
        pytest.skip("requires real Blender (bpy is mocked or absent)")


class TestBuildDashedLineSegments:
    def test_unit_edge_produces_expected_dash_count(self):
        verts, edges = tool.Blender.build_dashed_line_segments(
            [(0.0, 0.0, 0.0), (1.0, 0.0, 0.0)],
            [(0, 1)],
            dash_period=0.20,
            dash_width=0.10,
        )
        assert len(edges) == 5
        assert len(verts) == 10

    def test_each_dash_runs_dash_width_along_the_edge(self):
        verts, edges = tool.Blender.build_dashed_line_segments(
            [(0.0, 0.0, 0.0), (1.0, 0.0, 0.0)],
            [(0, 1)],
            dash_period=0.20,
            dash_width=0.10,
        )
        for i, j in edges:
            dx = verts[j][0] - verts[i][0]
            assert math.isclose(dx, 0.10, abs_tol=1e-9)

    def test_dash_phase_resets_per_input_edge(self):
        verts, edges = tool.Blender.build_dashed_line_segments(
            [(0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (1.0, 0.0, 0.0), (1.0, 1.0, 0.0)],
            [(0, 1), (2, 3)],
            dash_period=0.20,
            dash_width=0.10,
        )
        first_dash_start = verts[edges[0][0]]
        second_edge_first_dash_start = verts[edges[5][0]]
        assert math.isclose(first_dash_start[0], 0.0, abs_tol=1e-9)
        assert math.isclose(second_edge_first_dash_start[1], 0.0, abs_tol=1e-9)

    def test_trailing_partial_dash_is_clamped_to_edge_end(self):
        verts, edges = tool.Blender.build_dashed_line_segments(
            [(0.0, 0.0, 0.0), (0.25, 0.0, 0.0)],
            [(0, 1)],
            dash_period=0.20,
            dash_width=0.10,
        )
        last_x = verts[edges[-1][1]][0]
        assert last_x <= 0.25 + 1e-9

    def test_zero_length_edge_emits_no_dashes(self):
        verts, edges = tool.Blender.build_dashed_line_segments(
            [(0.0, 0.0, 0.0), (0.0, 0.0, 0.0)],
            [(0, 1)],
            dash_period=0.20,
            dash_width=0.10,
        )
        assert verts == []
        assert edges == []

    def test_invalid_dash_parameters_return_empty(self):
        assert tool.Blender.build_dashed_line_segments(
            [(0.0, 0.0, 0.0), (1.0, 0.0, 0.0)], [(0, 1)], dash_period=0.0, dash_width=0.10
        ) == ([], [])
        assert tool.Blender.build_dashed_line_segments(
            [(0.0, 0.0, 0.0), (1.0, 0.0, 0.0)], [(0, 1)], dash_period=0.20, dash_width=-0.10
        ) == ([], [])
