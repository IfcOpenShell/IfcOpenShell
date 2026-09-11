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

"""Regression test for the Shift+E (``bim.hotkey`` / ``hotkey_S_E``) crash on
IFC objects with no representation.

``hotkey_S_E`` (bound to the ``BimTool`` workspace-tool keymap as Shift+E,
see ``BimTool.bl_keymap`` in ``workspace.py``) used to compute
``tool.Geometry.resolve_mapped_representation(tool.Geometry.get_active_representation(obj))``
for any selected object without a usage type, then discard the result
without ever reading it. ``get_active_representation`` returns ``None`` for
an object with no representation (e.g. a Blender Empty standing in for an
IFC element that was never given geometry), and
``resolve_mapped_representation(None)`` raises ``AttributeError`` reading
``None.RepresentationType`` - crashing the operator before the dead value
was ever used."""

from unittest.mock import MagicMock, Mock, patch

import bpy
import pytest

pytestmark = pytest.mark.model


def _make_op(**fields):
    """Stand-in for the ``Hotkey`` operator's ``self``. Subclassing a
    ``bpy.types.Operator`` outside Blender's registration machinery raises
    a ``bpy_struct.__new__`` error, so the test calls ``hotkey_S_E`` as an
    unbound function with this Mock as the first argument."""
    op = Mock()
    for k, v in fields.items():
        setattr(op, k, v)
    op.report = MagicMock()
    return op


def test_hotkey_s_e_does_not_crash_on_object_without_representation():
    """A selected+active object with an IFC element, no usage type, and no
    active representation must not raise. Reproduces the crash from an
    unmodified object with ``tool.Geometry.get_active_representation``
    returning ``None`` (the real-world shape for an Empty linked to an IFC
    element that has no ``Representation``)."""
    from bonsai.bim.module.model import workspace

    obj = Mock()
    element = Mock()

    op = _make_op(active_material_usage=None)
    ctx = MagicMock()
    ctx.selected_objects = [obj]
    ctx.active_object = obj

    # `wraps=` keeps the *real* resolve_mapped_representation implementation
    # live (only get_active_representation is stubbed to return None, which
    # is the real-world return value for a no-representation object) so this
    # test reproduces the actual AttributeError on unfixed code instead of
    # masking it behind a mock.
    with patch.object(workspace.bpy, "context", ctx), patch.object(
        workspace.tool.Ifc, "get_entity", return_value=element
    ), patch.object(workspace.tool.Model, "get_usage_type", return_value=None), patch.object(
        workspace.tool.Geometry, "get_active_representation", return_value=None
    ), patch.object(
        workspace.tool.Geometry,
        "resolve_mapped_representation",
        wraps=workspace.tool.Geometry.resolve_mapped_representation,
    ) as resolve_mapped:
        # Must not raise (this is what "crashed" before the fix).
        workspace.Hotkey.hotkey_S_E(op)

    # The dead computation is gone entirely - nothing should call
    # resolve_mapped_representation() from this code path any more.
    resolve_mapped.assert_not_called()


def test_hotkey_s_e_still_dispatches_layer2_extend_to_cursor():
    """Guard against the fix accidentally deleting more than the dead
    store: a single selected LAYER2 (wall) object must still reach
    ``core.extend_walls`` as before."""
    from bonsai.bim.module.model import workspace

    obj = Mock()
    element = Mock()

    op = _make_op(active_material_usage="LAYER2")
    ctx = MagicMock()
    ctx.selected_objects = [obj]
    ctx.active_object = obj
    ctx.scene.cursor.location = (0, 0, 0)

    with patch.object(workspace.bpy, "context", ctx), patch.object(
        workspace.tool.Ifc, "get_entity", return_value=element
    ), patch.object(workspace.tool.Model, "get_usage_type", return_value="LAYER2"), patch.object(
        workspace, "core"
    ) as core_mock, patch.object(
        workspace, "DumbWallJoiner"
    ):
        workspace.Hotkey.hotkey_S_E(op)

    core_mock.extend_walls.assert_called_once()
