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

from unittest.mock import patch

import bpy
import ifcopenshell
import pytest

import bonsai.tool as tool
from test.bim.bootstrap import NewIfc

pytestmark = pytest.mark.project


def _populate_pending(*element_ids: int) -> None:
    pending = tool.Project.get_project_props().pending_opening_recut
    pending.clear()
    for eid in element_ids:
        pending.add().ifc_definition_id = eid


def _make_linked_wall(name: str = "Wall") -> tuple[ifcopenshell.entity_instance, bpy.types.Object]:
    ifc_file = tool.Ifc.get()
    element = ifc_file.create_entity("IfcWall", GlobalId=ifcopenshell.guid.new(), Name=name)
    obj = bpy.data.objects.new(name, bpy.data.meshes.new(name))
    bpy.context.scene.collection.objects.link(obj)
    tool.Ifc.link(element, obj)
    return element, obj


class TestApplyPendingOpeningCuts(NewIfc):
    def test_clears_pending_and_calls_reimport_with_apply_openings(self):
        element, obj = _make_linked_wall()
        _populate_pending(element.id())

        with patch.object(tool.Geometry, "reimport_element_representations") as mock_reimport, patch(
            "ifcopenshell.util.representation.get_representation",
            return_value=object(),
        ):
            result = bpy.ops.bim.apply_pending_opening_cuts()

        assert result == {"FINISHED"}
        assert len(tool.Project.get_project_props().pending_opening_recut) == 0
        mock_reimport.assert_called_once()
        _, kwargs = mock_reimport.call_args
        assert kwargs.get("apply_openings") is True

    def test_skips_entries_whose_entity_is_gone(self):
        _populate_pending(99999)  # ID guaranteed not present

        with patch.object(tool.Geometry, "reimport_element_representations") as mock_reimport:
            result = bpy.ops.bim.apply_pending_opening_cuts()

        assert result == {"FINISHED"}
        assert len(tool.Project.get_project_props().pending_opening_recut) == 0
        mock_reimport.assert_not_called()


class TestDismissPendingOpeningCuts(NewIfc):
    def test_clears_collection_without_calling_reimport(self):
        element, _obj = _make_linked_wall()
        _populate_pending(element.id())

        with patch.object(tool.Geometry, "reimport_element_representations") as mock_reimport:
            result = bpy.ops.bim.dismiss_pending_opening_cuts()

        assert result == {"FINISHED"}
        assert len(tool.Project.get_project_props().pending_opening_recut) == 0
        mock_reimport.assert_not_called()


class TestSelectPendingOpeningCuts(NewIfc):
    def test_selects_objects_for_each_pending_entry(self):
        e1, o1 = _make_linked_wall("WallA")
        e2, o2 = _make_linked_wall("WallB")
        _populate_pending(e1.id(), e2.id())

        for obj in bpy.context.view_layer.objects:
            obj.select_set(False)

        result = bpy.ops.bim.select_pending_opening_cuts()

        assert result == {"FINISHED"}
        assert o1.select_get() and o2.select_get()
        assert bpy.context.view_layer.objects.active in (o1, o2)

    def test_cancels_when_no_objects_match(self):
        _populate_pending(99999)
        result = bpy.ops.bim.select_pending_opening_cuts()
        assert result == {"CANCELLED"}
