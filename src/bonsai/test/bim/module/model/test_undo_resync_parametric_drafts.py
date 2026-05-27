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

"""Tests for ``parametric_lifecycle.resync_parametric_drafts_after_undo``.

Blender's undo restores PropertyGroup field values but does not refire
their ``update`` callbacks, so the preview mesh of an in-progress
parametric draft desyncs from the gizmo dimension widget after Ctrl+Z.
The resync helper walks active drafts and re-runs the per-type
regenerator to bring preview back in line with the (restored) draft
state. This file pins the dispatch contract."""

from unittest.mock import MagicMock, patch

import bpy
import pytest

import bonsai.tool as tool
from bonsai.bim import parametric_lifecycle

pytestmark = pytest.mark.model


def test_undo_regenerators_target_registered_parametric_types():
    """Every entry in ``UNDO_REGENERATORS`` must name a real parametric
    type. A typo would silently no-op on Ctrl+Z, restoring the desync
    this helper is meant to prevent."""
    registered_names = {f.name for f in tool.Parametric.EDIT_TYPES}
    unknown = set(parametric_lifecycle.UNDO_REGENERATORS) - registered_names
    assert not unknown, f"UNDO_REGENERATORS keys {unknown} are not in tool.Parametric.EDIT_TYPES"


def test_resync_skips_objects_not_in_parametric_edit():
    """Objects with no active parametric edit must not trigger any
    regenerator — the helper is called from undo_post which fires on
    every undo, including undos that touch zero parametric drafts."""
    captured = []

    def fake_dispatch(obj):
        captured.append(obj)

    with patch.dict(parametric_lifecycle.UNDO_REGENERATORS, {"wall": fake_dispatch}, clear=False), patch.object(
        tool.Parametric, "is_object_editing", return_value=None
    ):
        parametric_lifecycle.resync_parametric_drafts_after_undo()

    assert captured == []


def test_resync_dispatches_to_registered_regenerator_for_editing_object():
    """When an object is in parametric edit and its type has a registered
    regenerator, the regenerator must run with that object as the sole
    arg. This is the load-bearing branch: preview mesh re-renders from
    current props, so the gizmo and preview re-sync."""
    captured = []

    def fake_wall_regenerator(obj):
        captured.append(obj)

    fake_feature = MagicMock(spec=tool.parametric.ParametricObject)
    fake_feature.name = "wall"

    obj = bpy.data.objects.new("test_wall_obj", bpy.data.meshes.new("test_wall_mesh"))
    try:
        with patch.dict(
            parametric_lifecycle.UNDO_REGENERATORS, {"wall": fake_wall_regenerator}, clear=False
        ), patch.object(tool.Parametric, "is_object_editing", side_effect=lambda o: fake_feature if o is obj else None):
            parametric_lifecycle.resync_parametric_drafts_after_undo()
    finally:
        bpy.data.objects.remove(obj, do_unlink=True)

    assert captured == [obj]


def test_resync_skips_editing_object_whose_type_has_no_regenerator():
    """A parametric type without an ``UNDO_REGENERATORS`` entry (door /
    window / array — IFC-derived preview, no desync) must not raise; the
    helper silently skips it."""
    fake_feature = MagicMock(spec=tool.parametric.ParametricObject)
    fake_feature.name = "door"  # door has no entry in UNDO_REGENERATORS

    obj = bpy.data.objects.new("test_door_obj", bpy.data.meshes.new("test_door_mesh"))
    try:
        with patch.object(
            tool.Parametric, "is_object_editing", side_effect=lambda o: fake_feature if o is obj else None
        ):
            parametric_lifecycle.resync_parametric_drafts_after_undo()
    finally:
        bpy.data.objects.remove(obj, do_unlink=True)
