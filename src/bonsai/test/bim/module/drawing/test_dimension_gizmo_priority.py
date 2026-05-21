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

"""Regression guard: overlapping distance gizmos must let the smaller one win.

When two ``GizmoDimension`` instances overlap on screen (e.g. a short dimension
nested inside a longer one along the same axis), the longer one's hit box fully
contains the shorter one's. Without a depth bias the longer one wins the GPU
select tie-break and the shorter one becomes unreachable.

``GizmoDimension.set_dimension_length`` writes ``select_bias = -dimension_length``
so the smaller one writes a higher (less-negative) bias and wins. The longer one
stays clickable at its exposed ends regardless of bias.

We call ``set_dimension_length`` as an unbound method on a ``SimpleNamespace``
fake ``self``. Its body only *writes* attributes (``_display_value``,
``_dimension_length``, ``select_bias``), so it doesn't need a real
``bpy.types.Gizmo`` instance — those only exist inside a registered
``GizmoGroup`` and aren't constructible in a headless test."""

import types
from types import SimpleNamespace

import bpy
import pytest

from bonsai.bim.module.drawing.gizmos import GizmoDimension

pytestmark = pytest.mark.drawing


@pytest.fixture(autouse=True)
def _require_real_bpy():
    if not isinstance(bpy, types.ModuleType) or hasattr(bpy, "_mock_name"):
        pytest.skip("requires real Blender (bpy is mocked or absent)")


def test_smaller_dimension_wins_select_bias():
    small = SimpleNamespace()
    large = SimpleNamespace()
    GizmoDimension.set_dimension_length(small, 0.077)
    GizmoDimension.set_dimension_length(large, 0.109)
    assert small.select_bias > large.select_bias


@pytest.mark.parametrize(
    "lengths",
    [
        [0.0, 0.05, 0.077, 0.109, 1.0, 5.0, 10.0],
        [0.001, 0.5, 2.5, 100.0, 9999.0],
    ],
)
def test_select_bias_is_non_increasing_in_length(lengths):
    """A monotonic mapping is all Blender's GPU select needs to break the tie."""
    biases = []
    for length in lengths:
        gizmo = SimpleNamespace()
        GizmoDimension.set_dimension_length(gizmo, length)
        biases.append(gizmo.select_bias)
    for prev, curr in zip(biases, biases[1:]):
        assert prev >= curr, f"select_bias must be non-increasing in length, got {biases}"


def test_negative_length_uses_absolute_value_for_bias():
    """Negative dimension values (e.g. inverted angles) clamp to abs() for hit-box scaling;
    select_bias follows the same clamped magnitude so signed-direction gizmos still
    obey the smaller-wins rule against their positive-sided peers."""
    positive = SimpleNamespace()
    negative = SimpleNamespace()
    GizmoDimension.set_dimension_length(positive, 0.5)
    GizmoDimension.set_dimension_length(negative, -0.5)
    assert positive.select_bias == negative.select_bias


def test_nan_and_inf_length_falls_back_to_zero_bias():
    """Invalid inputs are coerced to 0.0 before the bias is written, so a malformed
    update can't push a gizmo arbitrarily far forward or backward in the select buffer."""
    import math

    for bad in (math.nan, math.inf, -math.inf, "not a number"):
        gizmo = SimpleNamespace()
        GizmoDimension.set_dimension_length(gizmo, bad)
        assert gizmo.select_bias == 0.0
