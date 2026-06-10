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

"""Tests for the parametric-edit preview registry contract.

Every test reads the live ``PREVIEW_CANCEL_OPS`` registry rather than hard-
coding preview keys or cancel-operator names, so adding a new preview to the
registry automatically exercises the same invariants without test changes."""

import types

import bpy
import pytest

pytestmark = pytest.mark.model


def _registry():
    from bonsai.bim.module.model.preview_base import PREVIEW_CANCEL_OPS

    return PREVIEW_CANCEL_OPS


def _preview_umbrella():
    return getattr(bpy.context.scene, "BIMPreviewProperties", None)


def _registered_previews():
    """``[(attr, op_name, props)]`` for every registry entry that has a real
    child PropertyGroup on the umbrella in the current addon build."""
    umbrella = _preview_umbrella()
    if umbrella is None:
        return []
    out = []
    for attr, op_name in _registry():
        props = getattr(umbrella, attr, None)
        if props is not None:
            out.append((attr, op_name, props))
    return out


class TestRegistryContract:
    """Pins the invariant that every entry in PREVIEW_CANCEL_OPS resolves to
    a real cancel operator the addon registers. A new preview added to the
    registry without its matching cancel operator would otherwise crash
    ``try_cancel_active_preview`` on the first Esc."""

    def test_every_registered_cancel_op_is_callable(self):
        for attr, op_name in _registry():
            op = getattr(bpy.ops.bim, op_name, None)
            assert op is not None and callable(op), (
                f"Preview '{attr}' in PREVIEW_CANCEL_OPS points to bim.{op_name} "
                f"but no such operator is registered."
            )


class TestGetPreviewPropsTolerance:
    """The bug-class fixed in commit ee63137c6: ``get_preview_props`` is called
    from gizmo polls during addon init and from test mocks built on
    ``SimpleNamespace`` — neither has a fully-formed Blender context. The
    helper must return None rather than raise."""

    def test_returns_none_when_context_has_no_scene(self):
        from bonsai.bim.module.model.preview_base import get_preview_props

        # Pass an arbitrary attr name — the contract is the same for every
        # preview key, so picking one literally would be a maintenance trap.
        for attr, _ in _registry():
            assert get_preview_props(types.SimpleNamespace(), attr) is None
            break

    def test_returns_none_when_scene_lacks_umbrella(self):
        from bonsai.bim.module.model.preview_base import get_preview_props

        ctx = types.SimpleNamespace(scene=types.SimpleNamespace())
        for attr, _ in _registry():
            assert get_preview_props(ctx, attr) is None
            break


class TestActivationCycle:
    """End-to-end contract on the real addon: each registered preview can be
    activated and then cancelled to inactive. Runs for every preview that
    has a wired PropertyGroup, so a new preview added to the registry +
    umbrella is covered without test edits."""

    def test_any_preview_active_reflects_each_preview_state(self):
        from bonsai.bim.module.model.preview_base import any_preview_active

        registered = _registered_previews()
        if not registered:
            pytest.skip("No previews wired in this build — registry-only entries")

        # All inactive baseline.
        for _, _, props in registered:
            props.is_active = False
        assert any_preview_active(bpy.context) is False

        # Flip each one independently — the helper must report True.
        for _, _, props in registered:
            props.is_active = True
            assert any_preview_active(bpy.context) is True
            props.is_active = False

    def test_discard_pending_previews_clears_every_active_flag(self):
        from bonsai.bim.module.model.preview_base import discard_pending_previews

        registered = _registered_previews()
        if not registered:
            pytest.skip("No previews wired in this build — registry-only entries")

        for _, _, props in registered:
            props.is_active = True
        discard_pending_previews(bpy.context.scene)
        for attr, _, props in registered:
            assert props.is_active is False, f"discard_pending_previews left '{attr}' active"


class TestClearPreviewState:
    """``clear_preview_state`` is the shared cleanup routine every preview
    operator calls on commit / cancel. The contract is: ``is_active`` flips
    to False, every ``*_id`` IntProperty zeroes, everything else stays."""

    def test_clears_is_active_and_id_fields_on_real_property_groups(self):
        from bonsai.bim.module.model.preview_base import clear_preview_state

        registered = _registered_previews()
        if not registered:
            pytest.skip("No previews wired in this build — registry-only entries")

        for attr, _, props in registered:
            # Seed every *_id IntProperty with a non-zero sentinel and flip
            # the activity flag so the helper has something to clear.
            id_fields = [
                name for name, rna in props.bl_rna.properties.items() if name.endswith("_id") and rna.type == "INT"
            ]
            assert id_fields, f"Preview '{attr}' has no *_id IntProperty — registry shape changed"
            for name in id_fields:
                setattr(props, name, 42)
            props.is_active = True

            clear_preview_state(props)

            assert props.is_active is False, f"Preview '{attr}' is_active not cleared"
            for name in id_fields:
                assert getattr(props, name) == 0, f"Preview '{attr}' field '{name}' not zeroed"

    def test_leaves_non_id_fields_untouched(self):
        """Non-``*_id`` fields (FloatProperty params like ``radius``,
        ``start_length``) must survive the reset — they re-seed on the next
        enable, so untouching them here avoids a redundant write."""
        from bonsai.bim.module.model.preview_base import clear_preview_state

        bend = getattr(_preview_umbrella(), "bend", None)
        if bend is None:
            pytest.skip("Bend preview not wired in this build")

        bend.is_active = True
        bend.start_length = 0.42
        bend.radius = 0.99
        clear_preview_state(bend)

        assert bend.is_active is False
        assert bend.start_length == pytest.approx(0.42)
        assert bend.radius == pytest.approx(0.99)


class TestSaveOnDiscardWired:
    """Pins that the SaveProject operator clears preview state before writing
    the IFC file — a stuck is_active flag persisted through the save would
    silently hide sister gizmos on the next file load.

    Structural check: the SaveProject operator class must reference the
    discard helper somewhere in its execute path. Behavioural integration
    (actually saving a .blend with an active preview and reloading) belongs
    in the bim feature suite; this is the small guard against accidental
    removal of the call site."""

    def test_save_project_dispatches_discard_pending_previews(self):
        import inspect

        from bonsai.bim.module.model import preview_base
        from bonsai.bim.module.project import operator as project_operator

        # Find the project save operator dynamically — looking for any
        # Operator class whose bl_idname is "bim.save_project". Avoids
        # hard-coding the class identifier.
        save_op = None
        for name in dir(project_operator):
            obj = getattr(project_operator, name)
            if isinstance(obj, type) and getattr(obj, "bl_idname", None) == "bim.save_project":
                save_op = obj
                break
        assert save_op is not None, "Expected an operator with bl_idname='bim.save_project' in project/operator.py"

        # Walk the class's methods for the discard call. Avoids pinning a
        # specific method name (_execute vs execute vs an inner helper) so
        # the test survives operator refactors.
        source = inspect.getsource(save_op)
        assert preview_base.discard_pending_previews.__name__ in source, (
            f"{save_op.__name__} does not reference discard_pending_previews. "
            "Saving with a preview open would persist its is_active flag to the "
            ".blend file and silently hide sister gizmos on reopen."
        )
