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

"""Contract tests for the door swing-arc gizmo positioning.

Each test calls ``GizmoDoorEdition.update_swing_gizmos`` as an unbound method
against a SimpleNamespace stand-in that records ``matrix_basis`` assignments and
``hide`` flags. The expected matrices are recomputed from first principles so
the tests describe the geometric contract directly rather than echoing the
implementation."""

from types import SimpleNamespace
from unittest.mock import MagicMock

import bpy
import pytest
from mathutils import Matrix, Vector

pytestmark = pytest.mark.model


def _make_props(door_type, overall_width=0.9, lining_offset=0.0, is_editing=True):
    return SimpleNamespace(
        door_type=door_type,
        overall_width=overall_width,
        lining_offset=lining_offset,
        is_editing=is_editing,
    )


def _make_fake_group():
    """Stand-in for ``GizmoDoorEdition``: one MagicMock per declared arc gizmo
    plus a stub ``update_gizmo_visibility`` that records the visibility flag on
    each mock's ``hide`` attribute."""
    from bonsai.bim.module.model.door import GizmoDoorEdition

    fake = SimpleNamespace()
    fake.swing_arc_props = GizmoDoorEdition.swing_arc_props

    def update_gizmo_visibility(gizmo, is_visible):
        gizmo.hide = not is_visible
        return is_visible

    fake.update_gizmo_visibility = update_gizmo_visibility

    for cfg in fake.swing_arc_props:
        setattr(fake, f"gizmo_swing_arc_{cfg.name}", MagicMock(spec=["matrix_basis", "hide"]))
        setattr(fake, f"gizmo_swing_arc_{cfg.name}_flip", MagicMock(spec=["matrix_basis", "hide"]))

    return fake


def _call_update(fake, props, mw=None):
    from bonsai.bim.module.model.door import GizmoDoorEdition

    GizmoDoorEdition.update_swing_gizmos(fake, mw or Matrix.Identity(4), props)


def _matrix_approx(actual, expected, abs_tol=1e-6):
    assert isinstance(actual, Matrix), f"matrix_basis was never assigned (got {type(actual).__name__})"
    for i in range(4):
        for j in range(4):
            assert actual[i][j] == pytest.approx(expected[i][j], abs=abs_tol), (
                f"Mismatch at [{i}][{j}]: got {actual[i][j]}, expected {expected[i][j]}\n"
                f"actual=\n{actual}\nexpected=\n{expected}"
            )


_MIRROR_X = Matrix.Scale(-1, 4, (1, 0, 0))
_MIRROR_Y = Matrix.Scale(-1, 4, (0, 1, 0))


def test_single_swing_left_primary_arc_hinges_at_left_edge():
    """Left-hinged single-swing: primary arc at (0, lining_offset), scaled to
    overall_width, no X-mirror. Flip arc same transform composed with Y-mirror.
    Secondary panel hidden."""
    fake = _make_fake_group()
    props = _make_props(door_type="SINGLE_SWING_LEFT", overall_width=0.9, lining_offset=0.05)
    _call_update(fake, props)

    expected = Matrix.Translation(Vector((0.0, 0.05, 0.0))) @ Matrix.Scale(0.9, 4)
    _matrix_approx(fake.gizmo_swing_arc_primary.matrix_basis, expected)
    _matrix_approx(fake.gizmo_swing_arc_primary_flip.matrix_basis, expected @ _MIRROR_Y)
    assert fake.gizmo_swing_arc_secondary.hide is True
    assert fake.gizmo_swing_arc_secondary_flip.hide is True


def test_single_swing_right_primary_arc_hinges_at_right_edge_with_x_mirror():
    """Right-hinged single-swing: primary arc anchored at (overall_width, lining_offset)
    with an X-mirror applied so the arc sweeps back over the door panel rather
    than extending past the right edge."""
    fake = _make_fake_group()
    props = _make_props(door_type="SINGLE_SWING_RIGHT", overall_width=0.9, lining_offset=0.05)
    _call_update(fake, props)

    expected = Matrix.Translation(Vector((0.9, 0.05, 0.0))) @ Matrix.Scale(0.9, 4) @ _MIRROR_X
    _matrix_approx(fake.gizmo_swing_arc_primary.matrix_basis, expected)
    _matrix_approx(fake.gizmo_swing_arc_primary_flip.matrix_basis, expected @ _MIRROR_Y)
    assert fake.gizmo_swing_arc_secondary.hide is True
    assert fake.gizmo_swing_arc_secondary_flip.hide is True


@pytest.mark.parametrize(
    ("double_type", "single_type"),
    [
        ("DOUBLE_SWING_LEFT", "SINGLE_SWING_LEFT"),
        ("DOUBLE_SWING_RIGHT", "SINGLE_SWING_RIGHT"),
    ],
)
def test_double_swing_uses_same_recipe_as_single_swing(double_type, single_type):
    """DOUBLE_SWING_* (one panel that can open both ways) shares the
    single-panel positioning recipe with its SINGLE_SWING_* counterpart."""
    fake_a = _make_fake_group()
    fake_b = _make_fake_group()
    props_a = _make_props(door_type=double_type, overall_width=0.9, lining_offset=0.05)
    props_b = _make_props(door_type=single_type, overall_width=0.9, lining_offset=0.05)
    _call_update(fake_a, props_a)
    _call_update(fake_b, props_b)

    _matrix_approx(
        fake_a.gizmo_swing_arc_primary.matrix_basis,
        fake_b.gizmo_swing_arc_primary.matrix_basis,
    )
    _matrix_approx(
        fake_a.gizmo_swing_arc_primary_flip.matrix_basis,
        fake_b.gizmo_swing_arc_primary_flip.matrix_basis,
    )


def test_double_door_shows_four_arcs_each_scaled_to_half_door_width():
    """DOUBLE_DOOR_SINGLE_SWING: left panel hinged at x=0, right panel hinged
    at x=overall_width with X-mirror, both scaled to overall_width/2. Each
    panel also gets a Y-mirrored flip arc — 4 arcs total."""
    fake = _make_fake_group()
    props = _make_props(door_type="DOUBLE_DOOR_SINGLE_SWING", overall_width=1.6, lining_offset=0.0)
    _call_update(fake, props)

    half = 1.6 / 2
    expected_primary = Matrix.Translation(Vector((0.0, 0.0, 0.0))) @ Matrix.Scale(half, 4)
    expected_secondary = Matrix.Translation(Vector((1.6, 0.0, 0.0))) @ Matrix.Scale(half, 4) @ _MIRROR_X

    _matrix_approx(fake.gizmo_swing_arc_primary.matrix_basis, expected_primary)
    _matrix_approx(fake.gizmo_swing_arc_primary_flip.matrix_basis, expected_primary @ _MIRROR_Y)
    _matrix_approx(fake.gizmo_swing_arc_secondary.matrix_basis, expected_secondary)
    _matrix_approx(fake.gizmo_swing_arc_secondary_flip.matrix_basis, expected_secondary @ _MIRROR_Y)

    for cfg in fake.swing_arc_props:
        assert getattr(fake, f"gizmo_swing_arc_{cfg.name}").hide is False
        assert getattr(fake, f"gizmo_swing_arc_{cfg.name}_flip").hide is False


@pytest.mark.parametrize("door_type", ["SLIDING_TO_LEFT", "SLIDING_TO_RIGHT", "DOUBLE_DOOR_SLIDING"])
def test_sliding_door_types_hide_all_arcs(door_type):
    """Sliding doors don't swing — every arc in ``swing_arc_props`` is hidden."""
    fake = _make_fake_group()
    props = _make_props(door_type=door_type, overall_width=0.9, lining_offset=0.0)
    _call_update(fake, props)

    for cfg in fake.swing_arc_props:
        assert getattr(fake, f"gizmo_swing_arc_{cfg.name}").hide is True
        assert getattr(fake, f"gizmo_swing_arc_{cfg.name}_flip").hide is True


def test_not_editing_hides_all_arcs():
    """``is_editing=False`` collapses every arc's visibility, regardless of door type."""
    fake = _make_fake_group()
    props = _make_props(door_type="SINGLE_SWING_LEFT", overall_width=0.9, is_editing=False)
    _call_update(fake, props)

    for cfg in fake.swing_arc_props:
        assert getattr(fake, f"gizmo_swing_arc_{cfg.name}").hide is True
        assert getattr(fake, f"gizmo_swing_arc_{cfg.name}_flip").hide is True


def test_flip_arc_matrix_is_reassigned_each_refresh():
    """The flip arc's ``matrix_basis`` must be (re-)assigned on every refresh
    so a stale identity matrix can never appear at the world origin."""
    fake = _make_fake_group()
    props = _make_props(door_type="SINGLE_SWING_LEFT", overall_width=0.9, lining_offset=0.1)
    _call_update(fake, props)

    assert isinstance(fake.gizmo_swing_arc_primary_flip.matrix_basis, Matrix)
    assert fake.gizmo_swing_arc_primary_flip.matrix_basis != Matrix.Identity(4)


def test_world_matrix_pre_multiplies_into_arc_transform():
    """The caller's world matrix ``mw`` left-multiplies the per-panel transform:
    a translated ``mw`` shifts every arc by the same offset."""
    fake = _make_fake_group()
    props = _make_props(door_type="SINGLE_SWING_LEFT", overall_width=0.9, lining_offset=0.0)
    mw = Matrix.Translation(Vector((10.0, 20.0, 30.0)))
    _call_update(fake, props, mw=mw)

    expected = mw @ Matrix.Translation(Vector((0.0, 0.0, 0.0))) @ Matrix.Scale(0.9, 4)
    _matrix_approx(fake.gizmo_swing_arc_primary.matrix_basis, expected)
