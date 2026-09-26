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

"""Placement math for parametric arrays — ``tool.Array.child_matrix``.

This is the single source of truth both the regenerator
(``tool.Model._regenerate_array_body``) and the drag-time ghost preview
(``ArrayPreviewDecorator``) place instances from. Before it existed each
carried its own copy of the offset formula, so the preview could drift from
what Finish actually built; these cases pin the behaviour that unification
has to preserve exactly.

Tolerances are 1e-5, not something tighter: ``mathutils`` is
single-precision (``Vector((1/3,))`` stores 0.3333333432674408), and a
composed transform accumulates ~1e-6 of float32 round-off.
"""

import math

import pytest
from mathutils import Matrix

import bonsai.tool as tool

pytestmark = pytest.mark.model

# Float32 round-off ceiling for a composed transform.
EPS = 1e-5

IDENTITY = Matrix.Identity(4)


def assert_vec(actual, expected, eps=EPS):
    assert all(abs(a - b) < eps for a, b in zip(actual, expected)), f"{tuple(actual)} != {tuple(expected)}"


def linear_layer(**overrides) -> dict:
    layer = {
        "count": 5,
        "method": "OFFSET",
        "x": 2.0,
        "y": 0.0,
        "z": 0.0,
        "use_local_space": True,
    }
    layer.update(overrides)
    return layer


class TestLinearPlacement:
    def test_offset_steps_by_a_fixed_amount(self):
        assert_vec(tool.Array.child_matrix(IDENTITY, linear_layer(), 3, 1.0).translation, (6, 0, 0))

    def test_distribute_spreads_across_a_fixed_span(self):
        layer = linear_layer(method="DISTRIBUTE")
        assert_vec(tool.Array.child_matrix(IDENTITY, layer, 4, 1.0).translation, (2, 0, 0))
        assert_vec(tool.Array.child_matrix(IDENTITY, layer, 1, 1.0).translation, (0.5, 0, 0))

    def test_unit_scale_converts_project_units_to_si(self):
        assert_vec(tool.Array.child_matrix(IDENTITY, linear_layer(), 1, 0.001).translation, (0.002, 0, 0))

    def test_index_zero_is_the_source_itself(self):
        assert_vec(tool.Array.child_matrix(IDENTITY, linear_layer(), 0, 1.0).translation, (0, 0, 0))

    def test_local_space_offsets_in_the_parent_frame(self):
        turned = Matrix.Rotation(math.radians(90), 4, "Z")
        # +X in the parent's frame is +Y in world once the parent is turned 90 degrees.
        assert_vec(tool.Array.child_matrix(turned, linear_layer(), 1, 1.0).translation, (0, 2, 0), eps=1e-4)

    def test_world_space_offsets_along_world_axes(self):
        turned = Matrix.Rotation(math.radians(90), 4, "Z")
        layer = linear_layer(use_local_space=False)
        assert_vec(tool.Array.child_matrix(turned, layer, 1, 1.0).translation, (2, 0, 0), eps=1e-4)

    def test_count_of_one_does_not_divide_by_zero(self):
        """Every array starts at count 1, so the DISTRIBUTE divisor must be floored."""
        assert tool.Array.step_divisor({"count": 1, "method": "DISTRIBUTE"}) == 1
        assert tool.Array.step_divisor({"count": 0, "method": "DISTRIBUTE"}) == 1
        tool.Array.child_matrix(IDENTITY, linear_layer(count=1, method="DISTRIBUTE"), 0, 1.0)
