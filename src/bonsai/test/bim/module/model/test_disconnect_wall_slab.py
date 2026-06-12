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

"""Behaviour tests for ``bim.disconnect_wall_slab``.

Pins the dispatch contract: resolves the wall + slab from GlobalIds, finds the
specific ``IfcRelConnectsElements(TOP)`` rel, removes it via the IFC API, then
delegates to ``core.regenerate_wall_to_underside`` to re-clip the wall against
any remaining slab connections."""

from unittest.mock import MagicMock, Mock, patch

import pytest

pytestmark = pytest.mark.model


def _make_op(*, wall_guid="WALL-GUID", slab_guid="SLAB-GUID"):
    op = Mock()
    op.wall_guid = wall_guid
    op.slab_guid = slab_guid
    op.report = Mock()
    return op


def _ifc_file_with(*, walls: dict | None = None, slabs: dict | None = None):
    ifc = MagicMock(name="ifc_file")
    walls = walls or {}
    slabs = slabs or {}

    def _by_guid(guid):
        if guid in walls:
            return walls[guid]
        if guid in slabs:
            return slabs[guid]
        raise RuntimeError(f"no entity with guid {guid}")

    ifc.by_guid.side_effect = _by_guid
    return ifc


def test_disconnect_removes_rel_then_regenerates():
    """Happy path: resolve both endpoints, find rel, call disconnect_element,
    then regenerate so remaining slabs re-clip cleanly."""
    from bonsai.bim.module.model.wall import DisconnectWallSlab

    wall = Mock(name="wall")
    slab = Mock(name="slab")
    rel = Mock(name="rel")
    wall_obj = Mock(name="wall_obj")
    ifc_file = _ifc_file_with(walls={"WALL-GUID": wall}, slabs={"SLAB-GUID": slab})
    op = _make_op()

    with patch("bonsai.bim.module.model.wall.tool.Ifc.get", return_value=ifc_file), patch(
        "bonsai.bim.module.model.wall.tool.Ifc.get_object", return_value=wall_obj
    ), patch("bonsai.bim.module.model.wall.tool.Wall.find_wall_slab_rel", return_value=rel), patch(
        "bonsai.bim.module.model.wall.ifcopenshell.api.geometry.disconnect_element"
    ) as disconnect, patch(
        "bonsai.bim.module.model.wall.core.regenerate_wall_to_underside"
    ) as regen:
        DisconnectWallSlab._perform(op, context=MagicMock())

    disconnect.assert_called_once_with(ifc_file, relating_element=slab, related_element=wall)
    regen.assert_called_once()
    args, _ = regen.call_args
    assert args[3] == [wall_obj]
    op.report.assert_not_called()


def test_disconnect_reports_when_guids_unknown():
    """Stale UI state can dispatch with guids no longer in the file — surface
    an ERROR rather than crashing on RuntimeError from by_guid."""
    from bonsai.bim.module.model.wall import DisconnectWallSlab

    ifc_file = _ifc_file_with()
    op = _make_op(wall_guid="MISSING", slab_guid="ALSO-MISSING")

    with patch("bonsai.bim.module.model.wall.tool.Ifc.get", return_value=ifc_file), patch(
        "bonsai.bim.module.model.wall.ifcopenshell.api.geometry.disconnect_element"
    ) as disconnect, patch("bonsai.bim.module.model.wall.core.regenerate_wall_to_underside") as regen:
        DisconnectWallSlab._perform(op, context=MagicMock())

    disconnect.assert_not_called()
    regen.assert_not_called()
    op.report.assert_called_once()
    args, _ = op.report.call_args
    assert args[0] == {"ERROR"}


def test_disconnect_reports_when_rel_missing():
    """find_wall_slab_rel returns None when the rel doesn't exist (UI was
    showing a stale icon). Operator reports + skips the mutation."""
    from bonsai.bim.module.model.wall import DisconnectWallSlab

    wall = Mock(name="wall")
    slab = Mock(name="slab")
    wall_obj = Mock(name="wall_obj")
    ifc_file = _ifc_file_with(walls={"WALL-GUID": wall}, slabs={"SLAB-GUID": slab})
    op = _make_op()

    with patch("bonsai.bim.module.model.wall.tool.Ifc.get", return_value=ifc_file), patch(
        "bonsai.bim.module.model.wall.tool.Ifc.get_object", return_value=wall_obj
    ), patch("bonsai.bim.module.model.wall.tool.Wall.find_wall_slab_rel", return_value=None), patch(
        "bonsai.bim.module.model.wall.ifcopenshell.api.geometry.disconnect_element"
    ) as disconnect, patch(
        "bonsai.bim.module.model.wall.core.regenerate_wall_to_underside"
    ) as regen:
        DisconnectWallSlab._perform(op, context=MagicMock())

    disconnect.assert_not_called()
    regen.assert_not_called()
    op.report.assert_called_once()
    args, _ = op.report.call_args
    assert args[0] == {"ERROR"}


def test_disconnect_reports_when_wall_obj_missing():
    """The wall entity exists but has no Blender object — surface ERROR
    rather than silently no-op (or crash trying to pass None to regen)."""
    from bonsai.bim.module.model.wall import DisconnectWallSlab

    wall = Mock(name="wall")
    slab = Mock(name="slab")
    ifc_file = _ifc_file_with(walls={"WALL-GUID": wall}, slabs={"SLAB-GUID": slab})
    op = _make_op()

    with patch("bonsai.bim.module.model.wall.tool.Ifc.get", return_value=ifc_file), patch(
        "bonsai.bim.module.model.wall.tool.Ifc.get_object", return_value=None
    ), patch("bonsai.bim.module.model.wall.ifcopenshell.api.geometry.disconnect_element") as disconnect, patch(
        "bonsai.bim.module.model.wall.core.regenerate_wall_to_underside"
    ) as regen:
        DisconnectWallSlab._perform(op, context=MagicMock())

    disconnect.assert_not_called()
    regen.assert_not_called()
    op.report.assert_called_once()


def test_disconnect_operator_is_registered():
    """Catches a forgotten classes-tuple update — the operator file can be
    saved cleanly but the class never reaches Blender's registry without
    the __init__.py entry."""
    from bonsai.bim.module import model

    assert any(
        getattr(cls, "bl_idname", None) == "bim.disconnect_wall_slab" for cls in model.classes
    ), "DisconnectWallSlab is not in the model classes tuple"
