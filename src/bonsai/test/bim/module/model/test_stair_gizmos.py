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

"""Regression guard for the stair icon billboard fix.

Before the fix, ``set_icon_gizmo_position`` in ``bim.module.drawing.gizmos``
composed ``mw @ (Translation @ billboard_rot @ Scale)``, which applied the
stair's world rotation on top of the billboard rotation. The result was
icons (validate / cancel / lock / +/- / cycle / tread_lock) drawn edge-on
to the camera for any stair rotated in plan — effectively unclickable.

The fix routes through ``billboarded_at(world_pos, billboard_rot, scale)``,
which computes ``Translation(world_pos) @ billboard_rot @ Scale`` — the
object's rotation is folded into the translation only, never the rotation."""

import math
import types

import bpy
import pytest

pytestmark = pytest.mark.model


def _rotation_close(a, b, tol: float = 1e-6) -> bool:
    for row_a, row_b in zip(a, b):
        for va, vb in zip(row_a, row_b):
            if abs(va - vb) > tol:
                return False
    return True


@pytest.mark.parametrize("angle_deg", [0, 30, 45, 90, 135, 217])
def test_billboarded_at_rotation_is_pure_billboard(angle_deg):
    """Object rotation must not leak into the gizmo's rotation part."""
    from mathutils import Matrix, Vector

    from bonsai.bim.module.drawing.gizmos import billboarded_at

    mw = Matrix.Rotation(math.radians(angle_deg), 4, "Z") @ Matrix.Translation((3, 4, 5))
    billboard_rot = Matrix.Rotation(math.radians(30), 4, "X")

    world_pos = mw @ Vector((1, 0, 2))
    result = billboarded_at(world_pos, billboard_rot, scale=0.5)

    # The rotation part of result, after stripping the 0.5 uniform scale,
    # must equal billboard_rot — no contribution from mw's rotation.
    rotation_part = result.to_3x3() * 2.0
    assert _rotation_close(rotation_part.to_4x4(), billboard_rot)


def test_billboarded_at_translation_is_world_pos():
    """Translation lands exactly at the world-space target."""
    from mathutils import Matrix, Vector

    from bonsai.bim.module.drawing.gizmos import billboarded_at

    world_pos = Vector((1.23, 4.56, 7.89))
    result = billboarded_at(world_pos, Matrix.Identity(4), scale=0.5)
    assert (result.translation - world_pos).length < 1e-6


def test_set_icon_gizmo_position_does_not_apply_object_rotation():
    """End-to-end: the helper used by every stair icon (and shared with all
    parametric gizmo groups) must produce a matrix whose rotation part is
    billboard_rot, not mw_rotation @ billboard_rot. This is the exact bug
    that left stair icons edge-on to the camera."""
    from mathutils import Matrix, Vector

    from bonsai.bim.module.drawing.gizmos import (
        BaseParametricGizmoGroup,
        billboarded_at,
    )

    # Same inputs as the real call site (stair.py:747-765), but we drive the
    # helper directly so we don't need a registered GizmoGroup. We bind a
    # stand-in `get_gizmo_if_visible` that returns a tiny mock; the helper's
    # observable output is the matrix_basis it assigns.
    captured = {}

    class _GizmoStub:
        matrix_basis = Matrix.Identity(4)

    stub = _GizmoStub()

    def _fake_get(name):
        captured["name"] = name
        return stub

    # Bind the helper to a throwaway instance so `self.get_gizmo_if_visible`
    # resolves to our stub without registering a real GizmoGroup with Blender.
    fake_self = types.SimpleNamespace(get_gizmo_if_visible=_fake_get)
    mw = Matrix.Rotation(math.radians(45), 4, "Z") @ Matrix.Translation((3, 4, 5))
    billboard_rot = Matrix.Rotation(math.radians(30), 4, "X")
    local_pos = Vector((1, 0, 2))
    BaseParametricGizmoGroup.set_icon_gizmo_position(
        fake_self,
        "validate_gizmo",
        mw=mw,
        x=local_pos.x,
        y=local_pos.y,
        z=local_pos.z,
        billboard_rot=billboard_rot,
        scale=0.5,
    )

    expected = billboarded_at(mw @ local_pos, billboard_rot, 0.5)

    assert captured["name"] == "validate_gizmo"
    for row_a, row_b in zip(stub.matrix_basis, expected):
        for va, vb in zip(row_a, row_b):
            assert abs(va - vb) < 1e-6


def test_icon_slot_placeholder_skips_validation_and_returns_no_attrs():
    """Placeholder slots reserve an X position without an auto-created gizmo:
    construction must not require ``gizmo_idname`` / ``operator``, and
    ``gizmo_attrs()`` must return an empty tuple so the base class's
    setup/positioning loops naturally skip the slot."""
    from bonsai.bim.module.drawing.gizmos import IconSlot

    slot = IconSlot(name="my_label", placeholder=True)
    assert slot.placeholder is True
    assert slot.gizmo_attrs() == ()

    with pytest.raises(TypeError, match="gizmo_idname"):
        IconSlot(name="broken")


def test_count_label_gizmo_is_registered():
    """The shared text-only ``xN`` gizmo must register so the stair group's
    ``gizmos.new("BIM_GT_count_label")`` resolves."""
    from bonsai.bim.module.drawing.gizmos import GizmoCountLabel

    assert GizmoCountLabel.bl_idname == "BIM_GT_count_label"
    assert bpy.types.Gizmo.bl_rna_get_subclass_py("BIM_GT_count_label") is GizmoCountLabel


def test_stair_edit_row_reserves_label_slot_between_tread_lock_and_plus():
    """The ``tread_count_label`` placeholder slot must sit one
    ``ICON_ARRAY_GAP`` past the tread-lock and one gap before the plus
    icon, so the layout naturally allocates the count label's X without
    any subclass-side gap math."""
    from bonsai.bim.module.drawing.gizmos import BaseParametricGizmoGroup
    from bonsai.bim.module.model.stair import GizmoStairEdition

    slot_x = GizmoStairEdition._slot_x_positions()
    gap = BaseParametricGizmoGroup.ICON_ARRAY_GAP

    assert "tread_count_label" in slot_x
    assert slot_x["tread_count_label"] - slot_x["tread_lock"] == pytest.approx(gap)
    assert slot_x["plus"] - slot_x["tread_count_label"] == pytest.approx(gap)
    assert slot_x["minus"] - slot_x["plus"] == pytest.approx(gap)


def test_update_tread_count_gizmos_toggles_label_with_editing():
    """``update_tread_count_gizmos`` must propagate ``props.is_editing``
    to the label's hide state so the badge appears only inside edit mode."""
    from bonsai.bim.module.drawing.gizmos import BaseParametricGizmoGroup
    from bonsai.bim.module.model.stair import GizmoStairEdition

    class _GizmoStub:
        def __init__(self):
            self.hide = False

    plus_gz = _GizmoStub()
    minus_gz = _GizmoStub()
    label_gz = _GizmoStub()

    fake_self = types.SimpleNamespace(
        plus_gizmo=plus_gz,
        minus_gizmo=minus_gz,
        tread_count_label_gizmo=label_gz,
        update_gizmo_visibility=lambda g, v: BaseParametricGizmoGroup.update_gizmo_visibility(fake_self, g, v),
        is_gizmo_hidden_by_modal=lambda g: False,
    )

    props_editing = types.SimpleNamespace(is_editing=True, number_of_treads=5)
    GizmoStairEdition.update_tread_count_gizmos(fake_self, props_editing)
    assert label_gz.hide is False

    props_idle = types.SimpleNamespace(is_editing=False, number_of_treads=5)
    GizmoStairEdition.update_tread_count_gizmos(fake_self, props_idle)
    assert label_gz.hide is True
