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

"""Regression tests for the post-IFC-commit refresh path.

Two invariants:

* Every commit bumps ``_geom_generation`` so caches keyed off it drop
  stale entries on the next read.
* The BIM Tool header float refresh (``refresh_bim_tool_headers``) fires
  only for commits whose operator is a parametric ``finish_op`` from
  ``tool.Parametric.EDIT_TYPES`` — the validate-gizmo path. Other
  operators skip it; their commit context may lack the view-layer
  attributes the refresh reads."""

import types
from unittest.mock import MagicMock, patch

import bpy
import pytest

pytestmark = pytest.mark.wall


def test_refresh_post_commit_bumps_generation_for_every_operator():
    """The generation counter advances on every commit, regardless of
    operator class — it's the cache-invalidation signal for any code
    keyed off ``tool.Parametric.get_geom_generation()``."""
    from bonsai import tool

    before = tool.Parametric.get_geom_generation()
    tool.Parametric.refresh_post_commit(MagicMock(bl_idname="bim.append_library_element"))
    assert tool.Parametric.get_geom_generation() == before + 1


def test_refresh_post_commit_refreshes_headers_for_validate_gizmo_operators():
    """Operators whose ``bl_idname`` matches a ``ParametricObject.finish_op``
    in ``EDIT_TYPES`` are the validate-gizmo path: selection didn't
    change, but the IFC values backing the BIM Tool header did. The
    commit hook must push the new IFC state into the header floats."""
    import bonsai.bim.handler as handler
    from bonsai import tool

    finish_op_idname = tool.Parametric.EDIT_TYPES[0].finish_op
    with patch.object(handler, "refresh_bim_tool_headers") as mock_refresh:
        tool.Parametric.refresh_post_commit(MagicMock(bl_idname=finish_op_idname))
    mock_refresh.assert_called_once()


def test_refresh_post_commit_skips_header_refresh_for_non_finish_operators():
    """Other operators must not trigger the header refresh. The refresh
    reads ``bpy.context``; for commits invoked from a stripped operator
    context (e.g. nested ``bpy.ops`` calls during project setup) this
    would raise ``AttributeError`` and break the outer operator chain."""
    import bonsai.bim.handler as handler
    from bonsai import tool

    with patch.object(handler, "refresh_bim_tool_headers") as mock_refresh:
        tool.Parametric.refresh_post_commit(MagicMock(bl_idname="bim.append_library_element"))
    mock_refresh.assert_not_called()


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
