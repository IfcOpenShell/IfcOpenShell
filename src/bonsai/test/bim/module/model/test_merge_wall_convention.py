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

"""Pins the active-is-survivor merge convention.

``bim.merge_wall`` must consume the non-active selection into the active
one — matching Blender's ``OBJECT_OT_join`` / ``MESH_OT_merge`` "at
last" convention. Users following Ctrl+J muscle-memory click the
surviving wall last; the operator must align with that expectation."""

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

pytestmark = pytest.mark.wall


def _run_perform(active, other):
    """Invoke ``MergeWall._perform`` as an unbound function with the
    two wall stubs in the selection, patching the heavy IFC / Blender
    side effects. Returns the ``(merger_arg_1, merger_arg_2)`` actually
    passed to ``DumbWallJoiner.merge``."""
    from bonsai.bim.module.model.wall import MergeWall

    context = SimpleNamespace(active_object=active)
    captured_call = {}

    def _capture_merge(self, a, b):
        captured_call["wall1"] = a
        captured_call["wall2"] = b

    fake_self = SimpleNamespace()

    with (
        patch("bonsai.bim.module.model.wall.tool.Ifc.get", return_value=MagicMock(name="ifc_file")),
        patch("bonsai.bim.module.model.wall.tool.Model.get_selected_mesh_objects", return_value=[active, other]),
        patch("bonsai.bim.module.model.wall.DumbWallJoiner.__init__", return_value=None),
        patch("bonsai.bim.module.model.wall.DumbWallJoiner.merge", new=_capture_merge),
        patch("bonsai.bim.module.model.wall._maybe_resync_wall_props_from_ifc"),
        patch("bonsai.bim.module.model.wall._regenerate_walls") as regen_walls,
    ):
        result = MergeWall._perform(fake_self, context)

    return captured_call, regen_walls, result


def test_active_wall_is_passed_as_survivor_to_merge():
    """The first argument to ``DumbWallJoiner.merge`` is the survivor;
    the active object must occupy that slot so the wall the user clicked
    last absorbs the other."""
    active = SimpleNamespace(name="active")
    other = SimpleNamespace(name="other")

    captured, _regen, _ = _run_perform(active, other)

    assert captured["wall1"] is active
    assert captured["wall2"] is other


def test_post_merge_resync_targets_active_not_consumed():
    """After the merge ``_regenerate_walls`` rebuilds the survivor's
    body. Targeting the consumed wall would crash on a freed ``bpy_struct``;
    the survivor (active) is the only valid target."""
    active = SimpleNamespace(name="active")
    other = SimpleNamespace(name="other")

    _, regen_walls, _ = _run_perform(active, other)

    regen_walls.assert_called_once_with([active])
