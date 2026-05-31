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

"""Regression tests for the post-IFC-commit refresh path that re-syncs the
workspace tool header (``BIMModelProperties``) and invalidates the per-wall
gizmo geometry cache.

Bug repro before the fix: hotkey operators that edited the active wall in
place (``bpy.ops.bim.hotkey(hotkey="S_E")`` / ``"C_E"``) mutated IFC but never
fired ``active_object_callback`` (no selection change), so the header H/L/A
fields and the gizmo cache both kept showing stale values. ``refresh_ui_data``
ran, but it never resynced ``BIMModelProperties`` and never invalidated the
per-gizmo-group geometry cache. The fix wires both refreshes through
``tool.Parametric.refresh_post_commit`` and calls it from every
``tool.Ifc.Operator`` epilogue."""

import types
from unittest.mock import patch

import bpy
import pytest

pytestmark = pytest.mark.wall


@pytest.fixture(autouse=True)
def _require_real_bpy():
    if not isinstance(bpy, types.ModuleType) or hasattr(bpy, "_mock_name"):
        pytest.skip("requires real Blender (bpy is mocked or absent)")


def test_refresh_post_commit_bumps_generation_and_resyncs_header():
    """``refresh_post_commit`` must bump the generation counter and call
    ``update_bim_tool_props`` so the workspace tool header re-syncs from IFC."""
    import bonsai.bim.handler as handler
    from bonsai import tool

    before = tool.Parametric.get_geom_generation()
    with patch.object(handler, "update_bim_tool_props") as mock_resync:
        tool.Parametric.refresh_post_commit()
    assert tool.Parametric.get_geom_generation() == before + 1
    mock_resync.assert_called_once()


def test_geom_generation_invalidates_wall_geom_cache():
    """Bumping the generation must cause ``_get_wall_geom_cached`` to drop its
    stored entries on the next read, even when the same gizmo group instance
    and the same wall object are reused (the case Blender's
    ``GizmoGroup.refresh()`` does not cover)."""
    from bonsai import tool
    from bonsai.bim.module.model import wall as wall_mod

    class _FakeGroup:
        pass

    group = _FakeGroup()
    fake_obj = types.SimpleNamespace(name="Wall/W001")
    sentinel_a = {"length": 1.0, "height": 2.0, "x_angle": 0.0}
    sentinel_b = {"length": 1.5, "height": 2.5, "x_angle": 0.0}

    with patch.object(tool.Wall, "read_geometry", side_effect=[sentinel_a, sentinel_b]):
        first = wall_mod._get_wall_geom_cached(group, fake_obj)
        assert first is sentinel_a
        # Same call without a generation bump must hit the cache (no extra read).
        assert wall_mod._get_wall_geom_cached(group, fake_obj) is sentinel_a
        # Simulate an IFC commit: generation advances, cache must drop.
        tool.Parametric._geom_generation += 1
        second = wall_mod._get_wall_geom_cached(group, fake_obj)
        assert second is sentinel_b
        assert second is not first
