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

"""Behaviour contract: every parametric gizmo group hides while a Blender
transform modal (G/R/S and siblings) is dragging ``matrix_world``.

Discovery walks each parametric-edit module rather than naming gizmo groups —
adding a new group automatically joins the test. The test exercises the
BEHAVIOUR (poll returns False / draw_prepare early-returns when a transform
modal is active) without pinning the name of the helper used internally."""

import importlib
from unittest.mock import MagicMock, patch

import bpy
import pytest

pytestmark = pytest.mark.model

PARAMETRIC_MODULES = (
    "bonsai.bim.module.model.array",
    "bonsai.bim.module.model.door",
    "bonsai.bim.module.model.host_add_opening_gizmo",
    "bonsai.bim.module.model.roof",
    "bonsai.bim.module.model.stair",
    "bonsai.bim.module.model.wall",
    "bonsai.bim.module.model.window",
)


def _discover_parametric_gizmo_groups():
    """Walk each parametric-edit module for ``bpy.types.GizmoGroup`` subclasses
    defined locally. Preview-owning gizmo groups (bl_idname contains 'preview')
    are excluded from the poll-level test: their poll legitimately fires while
    the preview is active, and the transform-modal hide for them lives in
    ``draw_prepare`` via ``BillboardingGizmoGroupMixin``."""
    out = []
    for mod_path in PARAMETRIC_MODULES:
        mod = importlib.import_module(mod_path)
        for name in dir(mod):
            obj = getattr(mod, name)
            if not isinstance(obj, type):
                continue
            if not issubclass(obj, bpy.types.GizmoGroup) or obj is bpy.types.GizmoGroup:
                continue
            if obj.__module__ != mod.__name__:
                continue
            bl_idname = (getattr(obj, "bl_idname", "") or "").lower()
            if "preview" in bl_idname:
                continue
            out.append((f"{mod_path.rsplit('.', 1)[-1]}.{name}", obj))
    return out


class TestDiscoveryFindsParametricGizmoGroups:
    def test_at_least_one_group_per_canonical_module(self):
        """If discovery returns zero groups for a module the walk has drifted —
        likely the gizmo group moved to a different file. Surface the drift
        with the module name in the diagnostic."""
        per_module: dict[str, int] = {}
        for fq_name, _cls in _discover_parametric_gizmo_groups():
            mod_short = fq_name.split(".", 1)[0]
            per_module[mod_short] = per_module.get(mod_short, 0) + 1
        empty = [m.rsplit(".", 1)[-1] for m in PARAMETRIC_MODULES if per_module.get(m.rsplit(".", 1)[-1], 0) == 0]
        assert not empty, (
            f"Parametric modules with zero GizmoGroup subclasses (discovery walk drifted?): {empty}. "
            "Update PARAMETRIC_MODULES or check whether the gizmo groups moved to a new file."
        )


class TestParametricGizmoPollsHideDuringTransformModal:
    """For each discovered parametric gizmo group, mock the transform-modal
    detector to True and call ``poll(bpy.context)``. Every poll must return
    False — any True is a poll that wouldn't hide during a G/R/S drag, leaving
    the gizmos jittering against the dragging matrix."""

    def test_every_group_poll_returns_false_when_transform_modal_active(self):
        groups = _discover_parametric_gizmo_groups()
        offenders = []
        with patch(
            "bonsai.bim.module.drawing.gizmos._is_transform_modal_active",
            return_value=True,
        ):
            for name, cls in groups:
                poll = getattr(cls, "poll", None)
                if poll is None:
                    continue
                try:
                    result = poll(bpy.context)
                except Exception as exc:  # noqa: BLE001
                    offenders.append((name, f"poll raised: {type(exc).__name__}: {exc}"))
                    continue
                if result:
                    offenders.append((name, "poll returned True with transform modal active"))

        assert not offenders, (
            "Parametric gizmo polls that don't gate on the transform-modal detector "
            "(or raise instead of returning False): "
            + ", ".join(f"{n} — {why}" for n, why in offenders)
            + ". Hide parametric gizmos while Blender's transform modal is dragging "
            "matrix_world so they don't jitter off-cursor. The conventional path is to "
            "early-return from poll when _is_transform_modal_active(context) is True."
        )


class TestBaseParametricPollHidesDuringTransformModal:
    """Cross-feature base poll: door / window / stair / roof / railing / array
    all inherit ``BaseParametricGizmoGroup``. Its poll must short-circuit on
    the transform-modal detector so every inheriting feature behaves uniformly."""

    def test_base_parametric_poll_returns_false(self):
        from bonsai.bim.module.drawing.gizmos import BaseParametricGizmoGroup

        with patch("bonsai.tool.Blender.get_active_object", return_value=object()):
            with patch("bonsai.tool.Blender.are_viewport_gizmos_enabled", return_value=True):
                with patch(
                    "bonsai.bim.module.model.preview_base.any_preview_active",
                    return_value=False,
                ):
                    with patch(
                        "bonsai.bim.module.drawing.gizmos._is_transform_modal_active",
                        return_value=True,
                    ):
                        assert BaseParametricGizmoGroup.poll(bpy.context) is False


class TestBaseIconActionPollHidesDuringTransformModal:
    """``BaseIconActionGroup`` is the parent of the simple icon-row gizmo
    groups; its poll mirrors the base parametric gate for forward-compat
    symmetry. Pinning here ensures a future icon-row group authored via this
    base inherits the transform-modal hide for free."""

    def test_base_icon_action_poll_returns_false(self):
        from bonsai.bim.module.drawing.gizmos import BaseIconActionGroup

        with patch("bonsai.tool.Blender.get_active_object", return_value=object()):
            with patch("bonsai.tool.Blender.are_viewport_gizmos_enabled", return_value=True):
                with patch(
                    "bonsai.bim.module.drawing.gizmos._is_transform_modal_active",
                    return_value=True,
                ):
                    assert BaseIconActionGroup.poll(bpy.context) is False


class TestHelperReadsWindowModalOperators:
    """Pin the public contract of ``_is_transform_modal_active``: it reads
    ``context.window.modal_operators`` (Blender 4.2+) and returns True iff any
    operator's ``bl_idname`` starts with ``TRANSFORM_OT_``. The check itself
    is dependency-free and worth pinning so a future refactor that swaps the
    detection mechanism either keeps the contract or updates the test."""

    def test_returns_true_for_transform_translate(self):
        from bonsai.bim.module.drawing.gizmos import _is_transform_modal_active

        fake_op = MagicMock()
        fake_op.bl_idname = "TRANSFORM_OT_translate"
        fake_context = MagicMock()
        fake_context.window.modal_operators = [fake_op]
        assert _is_transform_modal_active(fake_context) is True

    def test_returns_true_for_transform_rotate_and_resize(self):
        from bonsai.bim.module.drawing.gizmos import _is_transform_modal_active

        for idname in ("TRANSFORM_OT_rotate", "TRANSFORM_OT_resize", "TRANSFORM_OT_shear"):
            fake_op = MagicMock()
            fake_op.bl_idname = idname
            fake_context = MagicMock()
            fake_context.window.modal_operators = [fake_op]
            assert _is_transform_modal_active(fake_context) is True, f"missed {idname}"

    def test_returns_false_for_non_transform_modal(self):
        from bonsai.bim.module.drawing.gizmos import _is_transform_modal_active

        fake_op = MagicMock()
        fake_op.bl_idname = "VIEW3D_OT_select_box"
        fake_context = MagicMock()
        fake_context.window.modal_operators = [fake_op]
        assert _is_transform_modal_active(fake_context) is False

    def test_returns_true_for_bonsai_move_macro(self):
        """Bonsai overrides the G key with a macro that wraps
        ``TRANSFORM_OT_translate``. While the macro is the outer modal entry
        the inner transform does not surface in ``modal_operators``; matching
        the macro idname covers the gap. Note Blender exposes ``bl_idname``
        at runtime in the ``BIM_OT_<verb_noun>`` form, not the ``bim.<verb_noun>``
        form used in the class declaration — verified via real-Blender modal
        introspection during grab."""
        from bonsai.bim.module.drawing.gizmos import _is_transform_modal_active

        macros = (
            "BIM_OT_override_move_macro",
            "BIM_OT_override_object_duplicate_move_macro",
            "BIM_OT_override_object_duplicate_move_linked_macro",
            "BIM_OT_object_duplicate_move_linked_aggregate_macro",
        )
        for idname in macros:
            fake_op = MagicMock()
            fake_op.bl_idname = idname
            fake_context = MagicMock()
            fake_context.window.modal_operators = [fake_op]
            assert _is_transform_modal_active(fake_context) is True, f"missed {idname}"

    def test_returns_false_for_empty_modal_stack(self):
        from bonsai.bim.module.drawing.gizmos import _is_transform_modal_active

        fake_context = MagicMock()
        fake_context.window.modal_operators = []
        assert _is_transform_modal_active(fake_context) is False

    def test_returns_false_when_window_is_none(self):
        from bonsai.bim.module.drawing.gizmos import _is_transform_modal_active

        fake_context = MagicMock()
        fake_context.window = None
        assert _is_transform_modal_active(fake_context) is False
