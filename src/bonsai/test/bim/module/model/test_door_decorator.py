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

"""Contract tests for the door swing-arc readonly decorator.

Two layers:

- Pure tests on ``_visible_arcs`` pin the readonly decorator's arc selection
  per ``door_type`` enum value.
- A forward-compat guard walks ``GizmoDoorEdition.swing_arc_props`` and
  asserts the readonly decorator picks the same arcs (hinge / width / mirror)
  the edit-mode gizmo would, so the two surfaces stay visually identical
  even when a new ``door_type`` is added."""

from types import SimpleNamespace
from typing import get_args

import bpy
import pytest

pytestmark = pytest.mark.model


# ----------------------------------------------------------------------------
# _visible_arcs — per-door-type arc selection
# ----------------------------------------------------------------------------


def _arcs(door_type, overall_width=0.9, lining_offset=0.05):
    from bonsai.bim.module.model.decorator import _visible_arcs

    return _visible_arcs(door_type, overall_width, lining_offset)


def test_single_swing_left_one_arc_hinged_at_origin():
    arcs = _arcs("SINGLE_SWING_LEFT")
    assert len(arcs) == 1
    arc = arcs[0]
    assert arc.hinge_x == pytest.approx(0.0)
    assert arc.hinge_y == pytest.approx(0.05)
    assert arc.panel_width == pytest.approx(0.9)
    assert arc.x_mirror is False


def test_single_swing_right_one_arc_hinged_at_right_edge_x_mirrored():
    arcs = _arcs("SINGLE_SWING_RIGHT")
    assert len(arcs) == 1
    arc = arcs[0]
    assert arc.hinge_x == pytest.approx(0.9)
    assert arc.panel_width == pytest.approx(0.9)
    assert arc.x_mirror is True


@pytest.mark.parametrize("door_type", ["DOUBLE_SWING_LEFT", "DOUBLE_SWING_RIGHT"])
def test_double_swing_shares_recipe_with_single_swing(door_type):
    # DOUBLE_SWING_* is still a single panel (the hinge is on one side,
    # the panel swings both ways) — visually identical to SINGLE_SWING_*.
    single_type = door_type.replace("DOUBLE_SWING", "SINGLE_SWING")
    assert _arcs(door_type) == _arcs(single_type)


def test_double_door_single_swing_emits_two_half_width_arcs():
    arcs = _arcs("DOUBLE_DOOR_SINGLE_SWING")
    assert len(arcs) == 2
    left, right = arcs
    assert left.hinge_x == pytest.approx(0.0)
    assert left.panel_width == pytest.approx(0.45)
    assert left.x_mirror is False
    assert right.hinge_x == pytest.approx(0.9)
    assert right.panel_width == pytest.approx(0.45)
    assert right.x_mirror is True


@pytest.mark.parametrize("door_type", ["SLIDING_TO_LEFT", "SLIDING_TO_RIGHT", "DOUBLE_DOOR_SLIDING"])
def test_sliding_doors_emit_no_arcs(door_type):
    assert _arcs(door_type) == []


def test_unknown_door_type_falls_back_to_single_left_swing_arc():
    # Only ``"SLIDING"`` substrings short-circuit the swing predicate; any
    # other novel ``door_type`` falls through to the default left-hinged arc.
    arcs = _arcs("FUTURE_OPERATION_TYPE_42")
    assert len(arcs) == 1
    arc = arcs[0]
    assert arc.hinge_x == pytest.approx(0.0)
    assert arc.panel_width == pytest.approx(0.9)
    assert arc.x_mirror is False


def test_lining_offset_drives_hinge_y_for_every_visible_arc():
    for door_type in ("SINGLE_SWING_LEFT", "SINGLE_SWING_RIGHT", "DOUBLE_DOOR_SINGLE_SWING"):
        for arc in _arcs(door_type, overall_width=0.9, lining_offset=0.12):
            assert arc.hinge_y == pytest.approx(0.12)


# ----------------------------------------------------------------------------
# Forward-compat: readonly decorator and edit-mode gizmo agree per door_type
# ----------------------------------------------------------------------------


def _gizmo_expected(door_type, overall_width, lining_offset):
    """What ``GizmoDoorEdition.swing_arc_props`` would render for the props
    snapshot, with ``is_editing=True`` so its visibility predicates pass."""
    from bonsai.bim.module.model.door import GizmoDoorEdition

    props = SimpleNamespace(
        door_type=door_type,
        overall_width=overall_width,
        lining_offset=lining_offset,
        is_editing=True,
    )
    expected = []
    for cfg in GizmoDoorEdition.swing_arc_props:
        if cfg.visibility_condition(props):
            expected.append(
                (
                    cfg.hinge_x(props),
                    cfg.hinge_y(props),
                    cfg.panel_width(props),
                    cfg.x_mirror(props),
                )
            )
    return expected


def test_visible_arcs_matches_gizmo_swing_arc_props_for_every_door_type():
    import bonsai.tool as tool

    overall_width, lining_offset = 0.9, 0.05
    for door_type in get_args(tool.Model.DoorType):
        expected = _gizmo_expected(door_type, overall_width, lining_offset)
        actual = _arcs(door_type, overall_width, lining_offset)
        actual_tuples = [(a.hinge_x, a.hinge_y, a.panel_width, a.x_mirror) for a in actual]
        assert actual_tuples == expected, (
            f"Readonly decorator drifted from edit-mode gizmo for {door_type!r}: "
            f"expected {expected}, got {actual_tuples}"
        )


# ----------------------------------------------------------------------------
# Decorator gating contract (draw() early-returns)
# ----------------------------------------------------------------------------


def _make_decorator_stub():
    """Build a fresh ``DoorSwingReadonlyDecorator`` instance without going
    through ``install`` (which would attach a draw handler)."""
    from bonsai.bim.module.model.decorator import DoorSwingReadonlyDecorator

    return DoorSwingReadonlyDecorator()


def _draw_with_active(decorator, active_obj):
    """Call ``draw`` with a minimal ``context`` stub."""
    ctx = SimpleNamespace(active_object=active_obj)
    decorator.draw(ctx)


def test_draw_early_returns_when_no_active_object():
    # Should not raise; nothing to draw.
    _draw_with_active(_make_decorator_stub(), None)


def test_draw_early_returns_when_active_not_selected():
    obj = SimpleNamespace(select_get=lambda: False)
    _draw_with_active(_make_decorator_stub(), obj)
