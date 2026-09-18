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

"""End-to-end integration tests for ``mep.split_mep_segment`` (#3941).

Builds a real pipe run through the actual authoring flow — ``bim.add_default_type``
+ ``bim.add_occurrence`` (the same path ``DrawOccurrence`` uses) — three
segments long: an upstream segment, the segment under test, and a
downstream segment, joined end to end via real ``IfcRelConnectsPorts``.
Then calls ``mep.split_mep_segment`` on the middle segment and pins:

- both halves get the correct extruded length (geometry, not just IFC
  attribute bookkeeping),
- the new joint between the two halves is connected,
- the original upstream/downstream connections survive untouched.

None of this had a live-fixture test before (see the "deferred to a later
integration session" note in ``test_mep_segment_edition.py``); this fills
that gap for the split path specifically, since it's the one operator
in this file with no test coverage at all prior to #3941."""

import bpy
import ifcopenshell.api.system
import pytest
from mathutils import Vector

import bonsai.tool as tool
from bonsai.bim.module.model import mep
from test.bim.bootstrap import NewFile

pytestmark = pytest.mark.model


class TestMEPSegmentSplitIntegration(NewFile):
    def _make_pipe_type(self):
        bpy.ops.bim.add_default_type(ifc_element_type="IfcPipeSegmentType")
        return tool.Ifc.get_entity(bpy.context.active_object)

    def _place_segment(self, type_element, cursor_xy, depth):
        """Places one occurrence of ``type_element`` through the real
        ``bim.add_occurrence`` authoring path (``DumbProfileGenerator`` +
        ``MEPGenerator.setup_ports``), at ``cursor_xy`` with the given
        extrusion depth. Segments extrude along the type's default axis
        from the cursor location, so laying out non-overlapping segments
        along that axis is done by spacing ``cursor_xy`` accordingly."""
        props = tool.Model.get_model_props()
        props.relating_type_id = str(type_element.id())
        props.extrusion_depth = depth
        bpy.context.scene.cursor.location = Vector((cursor_xy[0], cursor_xy[1], 0.0))
        bpy.ops.bim.add_occurrence()
        obj = bpy.context.active_object
        return obj, tool.Ifc.get_entity(obj)

    def _axis_len(self, obj):
        bpy.context.view_layer.update()
        start, end = tool.Model.get_flow_segment_axis(obj)
        return (end - start).length

    def _setup_three_segment_run(self):
        """Builds up -> mid -> down, each 2m long, connected end to end,
        and returns (mid_obj, up_data, mid_data, down_data)."""
        bpy.ops.bim.create_project()
        pipe_type = self._make_pipe_type()

        up_obj, up_elem = self._place_segment(pipe_type, (-2.0, 0.0), 2.0)
        mid_obj, mid_elem = self._place_segment(pipe_type, (0.0, 0.0), 2.0)
        down_obj, down_elem = self._place_segment(pipe_type, (2.0, 0.0), 2.0)

        up_data = mep.MEPGenerator.get_segment_data(up_elem)
        mid_data = mep.MEPGenerator.get_segment_data(mid_elem)
        down_data = mep.MEPGenerator.get_segment_data(down_elem)

        ifcopenshell.api.system.connect_port(
            tool.Ifc.get(), port1=up_data["end_port"], port2=mid_data["start_port"], direction="NOTDEFINED"
        )
        ifcopenshell.api.system.connect_port(
            tool.Ifc.get(), port1=mid_data["end_port"], port2=down_data["start_port"], direction="NOTDEFINED"
        )
        return mid_obj, up_data, mid_data, down_data

    def test_split_produces_correctly_sized_halves(self):
        mid_obj, up_data, mid_data, down_data = self._setup_three_segment_run()
        assert self._axis_len(mid_obj) == pytest.approx(2.0, abs=0.01)

        new_obj = mep.split_mep_segment(mid_obj, 0.8)
        assert new_obj is not None

        assert self._axis_len(mid_obj) == pytest.approx(0.8, abs=0.01)
        assert self._axis_len(new_obj) == pytest.approx(1.2, abs=0.01)

    def test_split_connects_the_new_joint_and_preserves_original_connections(self):
        mid_obj, up_data, mid_data, down_data = self._setup_three_segment_run()

        new_obj = mep.split_mep_segment(mid_obj, 0.8)
        assert new_obj is not None

        mid_elem_after = tool.Ifc.get_entity(mid_obj)
        new_elem = tool.Ifc.get_entity(new_obj)
        mid_data_after = mep.MEPGenerator.get_segment_data(mid_elem_after)
        new_data = mep.MEPGenerator.get_segment_data(new_elem)

        # Original start of the split segment is untouched: still wired to
        # whatever was upstream before the split.
        assert tool.System.get_connected_port(mid_data_after["start_port"]) == up_data["end_port"]

        # The new joint between the two halves is connected both ways.
        assert tool.System.get_connected_port(mid_data_after["end_port"]) == new_data["start_port"]
        assert tool.System.get_connected_port(new_data["start_port"]) == mid_data_after["end_port"]

        # Original end of the split segment is preserved on the new half:
        # still wired to whatever was downstream before the split.
        assert tool.System.get_connected_port(new_data["end_port"]) == down_data["start_port"]

    def test_split_rejects_cut_too_close_to_an_endpoint(self):
        """``split_mep_segment`` rejects cuts within 0.01m of either
        endpoint rather than producing a degenerate zero-length half."""
        mid_obj, up_data, mid_data, down_data = self._setup_three_segment_run()

        assert mep.split_mep_segment(mid_obj, 0.005) is None
        assert mep.split_mep_segment(mid_obj, 1.995) is None
        # segment itself must be untouched by the rejected attempts
        assert self._axis_len(mid_obj) == pytest.approx(2.0, abs=0.01)
