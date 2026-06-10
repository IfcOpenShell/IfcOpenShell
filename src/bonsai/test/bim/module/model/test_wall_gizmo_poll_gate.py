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

"""Behaviour contract: every wall gizmo group hides while a parametric-edit
preview is active.

Enumerates wall gizmo groups by walking the wall module for ``bpy.types.GizmoGroup``
subclasses rather than naming them — adding a new wall gizmo group automatically
joins the test. The test then asserts the BEHAVIOUR (poll returns False when
``preview_base.any_preview_active`` is True) without pinning the name of the
helper function the gizmo uses internally to enforce it."""

import inspect
from unittest.mock import patch

import bpy
import pytest

pytestmark = pytest.mark.model


def _wall_gizmo_groups():
    """Walk the wall module for ``bpy.types.GizmoGroup`` subclasses defined
    locally (skip imported references). Returns a list of (name, cls) tuples.

    A gizmo group whose ``poll`` legitimately needs to fire WHILE a preview
    is active — i.e. it IS the preview's own gizmo group — is excluded by
    convention: classes whose bl_idname references the preview surface
    (``preview`` in the idname) are the preview-owner exception."""
    from bonsai.bim.module.model import wall as wall_mod

    out = []
    for name in dir(wall_mod):
        obj = getattr(wall_mod, name)
        if not isinstance(obj, type):
            continue
        if not issubclass(obj, bpy.types.GizmoGroup) or obj is bpy.types.GizmoGroup:
            continue
        # Local definitions only — skip re-exports / aliases.
        if obj.__module__ != wall_mod.__name__:
            continue
        # Preview-owner exception: the gizmo group that drives a preview
        # itself must remain visible while its preview is active, so a
        # "no preview active" gate would self-block it. The bl_idname
        # contains the substring 'preview' for these groups by Bonsai
        # convention (e.g. OBJECT_GGT_bim_wall_fillet_preview).
        bl_idname = getattr(obj, "bl_idname", "") or ""
        if "preview" in bl_idname.lower():
            continue
        out.append((name, obj))
    return out


class TestWallGizmoGroupsHideDuringPreview:
    """Behaviour contract: a parametric-edit preview is the only interactive
    surface in the viewport, so every sister wall gizmo must self-hide via
    its poll. The test exercises this BEHAVIOUR — when ``any_preview_active``
    reports True, every wall gizmo's poll returns False — without pinning
    the helper function name each poll uses internally."""

    def test_discovery_finds_wall_gizmo_groups(self):
        """Sanity check: at least one wall gizmo group is found. If this fails,
        the discovery walk drifted out of sync with the module structure (e.g.
        wall gizmo groups got moved to a separate file)."""
        groups = _wall_gizmo_groups()
        assert groups, "Expected at least one wall GizmoGroup subclass in wall.py — discovery walk broke?"

    def test_every_wall_gizmo_hides_when_a_preview_is_active(self):
        """For each discovered wall gizmo group, mock ``any_preview_active`` to
        True and call ``poll(bpy.context)``. Every poll must return False —
        any True is a poll that wouldn't hide during a fillet/bend preview,
        leaving the user with two competing icon stacks on the same selection."""
        groups = _wall_gizmo_groups()
        offenders = []
        with patch("bonsai.bim.module.model.preview_base.any_preview_active", return_value=True):
            for name, cls in groups:
                poll = getattr(cls, "poll", None)
                if poll is None:
                    # Inherits poll from a mixin / base — the base poll's gating
                    # is covered separately. Skip rather than crash.
                    continue
                try:
                    result = poll(bpy.context)
                except Exception as exc:  # noqa: BLE001
                    offenders.append((name, f"poll raised: {type(exc).__name__}: {exc}"))
                    continue
                if result:
                    offenders.append((name, "poll returned True with preview active"))

        assert not offenders, (
            "Wall gizmo polls that don't gate on any_preview_active "
            "(or raise instead of returning False): "
            + ", ".join(f"{n} — {why}" for n, why in offenders)
            + ". Hide sister gizmos during previews so the preview is the only "
            "interactive surface in the viewport. The conventional path is to "
            "early-return from poll when preview_base.any_preview_active(context) "
            "is True."
        )


class TestBaseParametricGizmoPollHidesDuringPreview:
    """Mirror of the wall-specific test for the cross-feature parametric
    framework: door / window / stair / roof / railing / array all inherit
    ``BaseParametricGizmoGroup``. Its poll must also short-circuit on
    ``any_preview_active`` so sister features behave consistently with walls."""

    def test_base_parametric_poll_returns_false_when_a_preview_is_active(self):
        from bonsai.bim.module.drawing.gizmos import BaseParametricGizmoGroup

        # The base poll requires an active selected object before checking the
        # preview gate. Mock both the selected-object check (return a sentinel)
        # AND the gate so the test exercises ONLY the preview short-circuit.
        with patch("bonsai.tool.Blender.get_active_object", return_value=object()):
            with patch("bonsai.tool.Blender.are_viewport_gizmos_enabled", return_value=True):
                with patch(
                    "bonsai.bim.module.model.preview_base.any_preview_active",
                    return_value=True,
                ):
                    assert BaseParametricGizmoGroup.poll(bpy.context) is False


class TestModulePathIsFindable:
    """If wall.py is split across multiple modules (e.g. wall_gizmos.py),
    update ``_wall_gizmo_groups`` to walk each. This sanity check fails first
    so the diagnostic message is obvious."""

    def test_wall_module_resolves(self):
        from bonsai.bim.module.model import wall as wall_mod

        assert inspect.ismodule(wall_mod)
