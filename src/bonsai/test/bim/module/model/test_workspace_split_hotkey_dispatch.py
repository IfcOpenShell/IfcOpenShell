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

"""Dispatch-wiring test for ``Hotkey.hotkey_S_K`` (#3941).

Walls already had a Shift+K split path (``bim.split_wall``, dispatched off
``active_material_usage == "LAYER2"``); pipe and duct segments had the
underlying split operators (``bim.split_pipe_segment_at_cursor`` /
``bim.split_duct_segment_at_cursor``, exercised via the cursor-anchored
gizmo icon) but ``hotkey_S_K`` never dispatched to them, so Shift+K was a
no-op on a selected segment. This pins the dispatch table so a future
regression (e.g. reordering the elif chain, or a typo in the operator
name) is caught without needing a live Blender scene."""

from unittest.mock import Mock, patch

import pytest

pytestmark = pytest.mark.model


def _hotkey_self(*, active_class=None, active_material_usage=None):
    """Duck-typed stand-in for a ``Hotkey`` operator instance mid-``_execute``
    — only the two attributes ``hotkey_S_K`` reads are set."""
    fake = Mock()
    fake.active_class = active_class
    fake.active_material_usage = active_material_usage
    return fake


@pytest.mark.parametrize(
    "active_class,active_material_usage,expected_op",
    [
        ("IfcWall", "LAYER2", "split_wall"),
        ("IfcPipeSegment", "PROFILE", "split_pipe_segment_at_cursor"),
        ("IfcDuctSegment", "PROFILE", "split_duct_segment_at_cursor"),
    ],
)
def test_hotkey_s_k_dispatches_to_the_matching_split_operator(active_class, active_material_usage, expected_op):
    from bonsai.bim.module.model import workspace

    fake_self = _hotkey_self(active_class=active_class, active_material_usage=active_material_usage)

    with patch("bpy.context") as mock_context, patch("bpy.ops.bim") as mock_bim_ops:
        mock_context.selected_objects = [Mock()]
        workspace.Hotkey.hotkey_S_K(fake_self)

    called_op = getattr(mock_bim_ops, expected_op)
    called_op.assert_called_once()

    # None of the sibling split operators should have fired.
    for other_op in ("split_wall", "split_pipe_segment_at_cursor", "split_duct_segment_at_cursor"):
        if other_op == expected_op:
            continue
        assert not getattr(mock_bim_ops, other_op).called, f"{other_op} should not have been dispatched"


@pytest.mark.parametrize(
    "active_class,active_material_usage",
    [
        (None, None),  # no IFC entity (context.active_object had none)
        ("IfcColumn", "PROFILE"),  # PROFILE usage, but not a pipe/duct segment
        ("IfcCableSegment", "PROFILE"),  # MEP segment class the split operators don't cover
    ],
)
def test_hotkey_s_k_is_a_no_op_for_unsupported_classes(active_class, active_material_usage):
    from bonsai.bim.module.model import workspace

    fake_self = _hotkey_self(active_class=active_class, active_material_usage=active_material_usage)

    with patch("bpy.context") as mock_context, patch("bpy.ops.bim") as mock_bim_ops:
        mock_context.selected_objects = [Mock()]
        workspace.Hotkey.hotkey_S_K(fake_self)

    for op in ("split_wall", "split_pipe_segment_at_cursor", "split_duct_segment_at_cursor"):
        assert not getattr(mock_bim_ops, op).called


def test_hotkey_s_k_does_nothing_without_a_selection():
    from bonsai.bim.module.model import workspace

    fake_self = _hotkey_self(active_class="IfcPipeSegment", active_material_usage="PROFILE")

    with patch("bpy.context") as mock_context, patch("bpy.ops.bim") as mock_bim_ops:
        mock_context.selected_objects = []
        workspace.Hotkey.hotkey_S_K(fake_self)

    assert not mock_bim_ops.split_pipe_segment_at_cursor.called
