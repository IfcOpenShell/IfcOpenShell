# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2026 Dion Moult <dion@thinkmoult.com>
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

"""End-to-end regression coverage for https://github.com/IfcOpenShell/IfcOpenShell/issues/6278.

Reporter's repro: connect three ``IfcDuctSegment``s with an established
flow direction, select two contiguous segments and "Add Bend". The bend
fitting gets spliced in, but ``MEPAddBend`` used to hardcode
``direction="NOTDEFINED"`` for both new fitting<->segment port
connections, unconditionally wiping whatever flow direction the spliced
segments already had. Manually re-establishing the direction afterwards
(one connection at a time) easily leaves the fitting's own two ports
non-complementary (e.g. both ``SOURCE`` or both ``SINK``), which is what
the reporter saw as the fitting's flow "looking reversed" relative to its
segments.

The fixture ``test/files/mep-duct-bend-flow-direction.ifc`` is the exact
file the reporter attached: three ``IfcDuctSegment``s, two of which
(#4276 / #4298) are still directly port-connected (no fitting) with an
established ``SOURCE`` -> ``SINK`` pair, exactly matching the "select two
contiguous segments and Add Bend" step. These tests drive the real
``bim.mep_add_bend`` operator against that fixture and assert on the
resulting IFC port graph."""

import bpy
import ifcopenshell.api.attribute

import bonsai.tool as tool
from test.bim.bootstrap import NewFile

FIXTURE = "test/files/mep-duct-bend-flow-direction.ifc"

# The two segments that are directly port-connected (no fitting) in the
# fixture, with an established SOURCE (#4276) -> SINK (#4298) pair.
SEGMENT_UPSTREAM_ID = 4276
SEGMENT_DOWNSTREAM_ID = 4298
UPSTREAM_PORT_ID = 4350
DOWNSTREAM_PORT_ID = 4409


def _port_flow_direction(ifc, port_id):
    return ifc.by_id(port_id).FlowDirection


def _connected_port(ifc, port_id):
    return tool.System.get_connected_port(ifc.by_id(port_id))


def _select_and_add_bend(upstream_obj, downstream_obj, **kwargs):
    bpy.context.view_layer.objects.active = upstream_obj
    upstream_obj.select_set(True)
    downstream_obj.select_set(True)
    return bpy.ops.bim.mep_add_bend(
        start_segment_id=tool.Ifc.get_entity(upstream_obj).id(),
        end_segment_id=tool.Ifc.get_entity(downstream_obj).id(),
        **kwargs,
    )


class TestMepAddBendPreservesFlowDirection(NewFile):
    def test_add_bend_preserves_established_flow_direction(self):
        """The reported case: splicing a bend into an already-flow-assigned
        connection must not reset it, and the new fitting's two ports must
        end up complementary (one SOURCE, one SINK) rather than reversed
        or independently inconsistent."""
        result = bpy.ops.bim.load_project(filepath=FIXTURE)
        assert result == {"FINISHED"}
        ifc = tool.Ifc.get()

        assert _port_flow_direction(ifc, UPSTREAM_PORT_ID) == "SOURCE"
        assert _port_flow_direction(ifc, DOWNSTREAM_PORT_ID) == "SINK"

        upstream_obj = tool.Ifc.get_object(ifc.by_id(SEGMENT_UPSTREAM_ID))
        downstream_obj = tool.Ifc.get_object(ifc.by_id(SEGMENT_DOWNSTREAM_ID))

        result = _select_and_add_bend(upstream_obj, downstream_obj)
        assert result == {"FINISHED"}

        # The segments' own flow direction must survive the splice unchanged.
        assert _port_flow_direction(ifc, UPSTREAM_PORT_ID) == "SOURCE"
        assert _port_flow_direction(ifc, DOWNSTREAM_PORT_ID) == "SINK"

        # Each segment must now be connected to the new fitting (not to
        # each other directly, and not left NOTDEFINED).
        fitting_port_near_upstream = _connected_port(ifc, UPSTREAM_PORT_ID)
        fitting_port_near_downstream = _connected_port(ifc, DOWNSTREAM_PORT_ID)
        assert fitting_port_near_upstream is not None
        assert fitting_port_near_downstream is not None
        assert fitting_port_near_upstream.is_a("IfcDistributionPort")
        assert fitting_port_near_downstream.is_a("IfcDistributionPort")

        fitting = tool.System.get_port_relating_element(fitting_port_near_upstream)
        assert fitting.is_a("IfcDuctFitting")
        assert tool.System.get_port_relating_element(fitting_port_near_downstream) == fitting

        # The fitting's own pass-through must be internally consistent:
        # SINK on the upstream side (flow enters the fitting from the
        # SOURCE segment), SOURCE on the downstream side (flow leaves the
        # fitting into the SINK segment) - never NOTDEFINED, never the
        # same value on both ports.
        assert fitting_port_near_upstream.FlowDirection == "SINK"
        assert fitting_port_near_downstream.FlowDirection == "SOURCE"
        assert {fitting_port_near_upstream.FlowDirection, fitting_port_near_downstream.FlowDirection} == {
            "SOURCE",
            "SINK",
        }

    def test_add_bend_with_no_established_flow_direction_stays_notdefined(self):
        """No regression: when the spliced connection never had a flow
        direction assigned, the new fitting's ports must still default to
        NOTDEFINED exactly like before this fix (the common / simplest
        two-segment bend case)."""
        result = bpy.ops.bim.load_project(filepath=FIXTURE)
        assert result == {"FINISHED"}
        ifc = tool.Ifc.get()

        ifcopenshell.api.attribute.edit_attributes(
            ifc, product=ifc.by_id(UPSTREAM_PORT_ID), attributes={"FlowDirection": "NOTDEFINED"}
        )
        ifcopenshell.api.attribute.edit_attributes(
            ifc, product=ifc.by_id(DOWNSTREAM_PORT_ID), attributes={"FlowDirection": "NOTDEFINED"}
        )

        upstream_obj = tool.Ifc.get_object(ifc.by_id(SEGMENT_UPSTREAM_ID))
        downstream_obj = tool.Ifc.get_object(ifc.by_id(SEGMENT_DOWNSTREAM_ID))

        result = _select_and_add_bend(upstream_obj, downstream_obj)
        assert result == {"FINISHED"}

        assert _port_flow_direction(ifc, UPSTREAM_PORT_ID) == "NOTDEFINED"
        assert _port_flow_direction(ifc, DOWNSTREAM_PORT_ID) == "NOTDEFINED"

        fitting_port_near_upstream = _connected_port(ifc, UPSTREAM_PORT_ID)
        fitting_port_near_downstream = _connected_port(ifc, DOWNSTREAM_PORT_ID)
        assert fitting_port_near_upstream.FlowDirection == "NOTDEFINED"
        assert fitting_port_near_downstream.FlowDirection == "NOTDEFINED"

    def test_reediting_bend_preserves_flow_direction(self):
        """Re-editing an existing bend (e.g. changing its radius, which
        deletes and recreates the fitting) must preserve the same flow
        direction the first splice established, not just on first
        creation."""
        result = bpy.ops.bim.load_project(filepath=FIXTURE)
        assert result == {"FINISHED"}
        ifc = tool.Ifc.get()

        upstream_obj = tool.Ifc.get_object(ifc.by_id(SEGMENT_UPSTREAM_ID))
        downstream_obj = tool.Ifc.get_object(ifc.by_id(SEGMENT_DOWNSTREAM_ID))
        result = _select_and_add_bend(upstream_obj, downstream_obj)
        assert result == {"FINISHED"}

        fitting_port_near_upstream = _connected_port(ifc, UPSTREAM_PORT_ID)
        fitting = tool.System.get_port_relating_element(fitting_port_near_upstream)

        upstream_obj = tool.Ifc.get_object(ifc.by_id(SEGMENT_UPSTREAM_ID))
        downstream_obj = tool.Ifc.get_object(ifc.by_id(SEGMENT_DOWNSTREAM_ID))
        result = _select_and_add_bend(upstream_obj, downstream_obj, editing_bend_id=fitting.id(), radius=0.3)
        assert result == {"FINISHED"}

        assert _port_flow_direction(ifc, UPSTREAM_PORT_ID) == "SOURCE"
        assert _port_flow_direction(ifc, DOWNSTREAM_PORT_ID) == "SINK"

        new_fitting_port_near_upstream = _connected_port(ifc, UPSTREAM_PORT_ID)
        new_fitting_port_near_downstream = _connected_port(ifc, DOWNSTREAM_PORT_ID)
        assert new_fitting_port_near_upstream.FlowDirection == "SINK"
        assert new_fitting_port_near_downstream.FlowDirection == "SOURCE"
