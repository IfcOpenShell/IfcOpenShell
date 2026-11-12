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

"""Restricted-context regression test for ``tool.Blender.get_active_object``.

Some Blender contexts (e.g. the C-side operator context handed to
programmatically-invoked nested ``bpy.ops`` calls) lack the view-layer
attributes a normal UI context exposes. The canonical accessor must
return ``None`` in that case rather than ``AttributeError`` — otherwise
every caller routed through it inherits the same crash class that
originally broke ``bpy.ops.bim.new_project(preset='demo')``."""

from unittest.mock import patch

import pytest

pytestmark = pytest.mark.model


class _RestrictedContext:
    """Stand-in for a ``bpy.context`` stripped of view-layer attributes."""

    def __getattr__(self, name):
        raise AttributeError(name)


def test_get_active_object_returns_none_in_restricted_context():
    """``tool.Blender.get_active_object`` is the canonical defensive
    accessor. Both the primary read (``bpy.context.active_object``) and
    the fallback (``bpy.context.view_layer.objects.active``) must
    tolerate a stripped context — otherwise the 150+ callers in the
    codebase that route through this helper inherit the crash."""
    import bonsai.tool.blender as blender_tool

    with patch.object(blender_tool, "bpy") as bpy_patch:
        bpy_patch.context = _RestrictedContext()
        assert blender_tool.Blender.get_active_object() is None


def test_property_header_tools_whitelists_bim_tool_family_only():
    """``tool.Blender.get_property_header_tools`` gates the validate-
    gizmo header refresh. Parametric ``BimTool`` subclasses and the
    base ``BimTool`` itself must be included; ``AnnotationTool`` and
    workspace tools outside the ``BimTool`` family (spatial, structural,
    etc.) must not — they don't surface these header floats."""
    import bonsai.tool as tool_

    # Ensure the lru_cache picks up subclasses registered by the
    # current Blender session (idempotent if already populated).
    tool_.Blender.get_property_header_tools.cache_clear()
    headers = tool_.Blender.get_property_header_tools()

    assert "bim.bim_tool" in headers, "base BimTool must surface property headers"
    assert "bim.wall_tool" in headers, "parametric BimTool subclass must surface property headers"
    assert "bim.annotation_tool" not in headers, "AnnotationTool is not a BimTool subclass — no header surface"
    assert "bim.spatial_tool" not in headers, "SpatialTool is not BimTool-derived"
    assert "bim.structural_tool" not in headers, "StructuralTool is not BimTool-derived"
