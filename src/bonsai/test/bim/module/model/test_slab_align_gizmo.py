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

"""Unit tests for ``GizmoSlabAlign`` (#6211): the 3D-viewport Exterior /
Centreline / Interior align icons for a selected IfcSlab.

Only ``poll()`` is exercised here — ``setup()`` / ``position_gizmos()``
create real ``bpy.types.Gizmo`` instances via ``self.gizmos.new(...)``,
which requires the gizmo group to be instantiated by Blender's own gizmo
manager (not directly constructible in a test), matching the existing
convention across this test directory (no sibling gizmo test calls
``setup()`` directly either)."""

from unittest.mock import patch

import bpy
import pytest

from bonsai.bim.module.model.wall import GizmoSlabAlign
from test.bim.module.model.conftest import make_element, make_obj

pytestmark = pytest.mark.model


class TestGizmoSlabAlignPoll:
    def test_true_with_two_selected_and_active_slab(self, patched_tool):
        obj_a, obj_b = make_obj(), make_obj()
        slab = make_element(ifc_class="IfcSlab")
        with patched_tool(
            viewport_gizmos=True,
            selected=[obj_a, obj_b],
            entity=lambda o: slab,
            modifier_predicates={"any_selected_is_array_child": False},
        ):
            with patch("bonsai.tool.Blender.get_active_object", return_value=obj_a):
                assert GizmoSlabAlign.poll(bpy.context) is True

    def test_false_with_only_one_selected(self, patched_tool):
        obj_a = make_obj()
        with patched_tool(
            viewport_gizmos=True,
            selected=[obj_a],
            modifier_predicates={"any_selected_is_array_child": False},
        ):
            assert GizmoSlabAlign.poll(bpy.context) is False

    def test_false_when_active_is_not_a_slab(self, patched_tool):
        obj_a, obj_b = make_obj(), make_obj()
        wall = make_element(ifc_class="IfcWall")
        with patched_tool(
            viewport_gizmos=True,
            selected=[obj_a, obj_b],
            entity=lambda o: wall,
            modifier_predicates={"any_selected_is_array_child": False},
        ):
            with patch("bonsai.tool.Blender.get_active_object", return_value=obj_a):
                assert GizmoSlabAlign.poll(bpy.context) is False

    def test_false_when_active_has_no_ifc_entity(self, patched_tool):
        obj_a, obj_b = make_obj(), make_obj()
        with patched_tool(
            viewport_gizmos=True,
            selected=[obj_a, obj_b],
            entity=None,
            modifier_predicates={"any_selected_is_array_child": False},
        ):
            with patch("bonsai.tool.Blender.get_active_object", return_value=obj_a):
                assert GizmoSlabAlign.poll(bpy.context) is False

    def test_false_when_viewport_gizmos_disabled(self, patched_tool):
        obj_a, obj_b = make_obj(), make_obj()
        with patched_tool(viewport_gizmos=False, selected=[obj_a, obj_b]):
            assert GizmoSlabAlign.poll(bpy.context) is False

    def test_false_when_active_slab_is_an_array_child(self, patched_tool):
        obj_a, obj_b = make_obj(), make_obj()
        slab = make_element(ifc_class="IfcSlab")
        with patched_tool(
            viewport_gizmos=True,
            selected=[obj_a, obj_b],
            entity=lambda o: slab,
            modifier_predicates={"any_selected_is_array_child": True},
        ):
            with patch("bonsai.tool.Blender.get_active_object", return_value=obj_a):
                assert GizmoSlabAlign.poll(bpy.context) is False

    def test_false_when_no_active_object(self, patched_tool):
        obj_a, obj_b = make_obj(), make_obj()
        with patched_tool(
            viewport_gizmos=True,
            selected=[obj_a, obj_b],
            modifier_predicates={"any_selected_is_array_child": False},
        ):
            with patch("bonsai.tool.Blender.get_active_object", return_value=None):
                assert GizmoSlabAlign.poll(bpy.context) is False


class TestGizmoSlabAlignDispatchesExistingAlignOperator:
    """The icons dispatch through ``bim.hotkey`` with the same S_X / S_C / S_V
    hotkeys the N-panel Align row already uses (``EditObjectUI.draw_align`` in
    workspace.py) — pin that the setup wiring references those exact hotkeys
    so the alignment math (``core.align_objects`` / ``core.align_walls``)
    stays defined in exactly one place."""

    def test_setup_source_wires_the_same_hotkeys_as_the_npanel_align_row(self):
        import inspect

        src = inspect.getsource(GizmoSlabAlign.setup)
        assert '"bim.hotkey"' in src
        assert 'hotkey = "S_X"' in src
        assert 'hotkey = "S_C"' in src
        assert 'hotkey = "S_V"' in src
