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

import bpy
import ifcopenshell.api.attribute

import bonsai.tool as tool
from test.bim.bootstrap import NewFile

FIXTURE = "test/files/mep-duct-bend-flow-direction.ifc"

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
    def test_add_bend_preserves_flow_direction_and_makes_fitting_ports_complementary(self):
        result = bpy.ops.bim.load_project(filepath=FIXTURE)
        assert result == {"FINISHED"}
        ifc = tool.Ifc.get()

        assert _port_flow_direction(ifc, UPSTREAM_PORT_ID) == "SOURCE"
        assert _port_flow_direction(ifc, DOWNSTREAM_PORT_ID) == "SINK"

        upstream_obj = tool.Ifc.get_object(ifc.by_id(SEGMENT_UPSTREAM_ID))
        downstream_obj = tool.Ifc.get_object(ifc.by_id(SEGMENT_DOWNSTREAM_ID))

        result = _select_and_add_bend(upstream_obj, downstream_obj)
        assert result == {"FINISHED"}

        assert _port_flow_direction(ifc, UPSTREAM_PORT_ID) == "SOURCE"
        assert _port_flow_direction(ifc, DOWNSTREAM_PORT_ID) == "SINK"

        fitting_port_near_upstream = _connected_port(ifc, UPSTREAM_PORT_ID)
        fitting_port_near_downstream = _connected_port(ifc, DOWNSTREAM_PORT_ID)
        assert fitting_port_near_upstream is not None
        assert fitting_port_near_downstream is not None
        assert fitting_port_near_upstream.is_a("IfcDistributionPort")
        assert fitting_port_near_downstream.is_a("IfcDistributionPort")

        fitting = tool.System.get_port_relating_element(fitting_port_near_upstream)
        assert fitting.is_a("IfcDuctFitting")
        assert tool.System.get_port_relating_element(fitting_port_near_downstream) == fitting

        assert fitting_port_near_upstream.FlowDirection == "SINK"
        assert fitting_port_near_downstream.FlowDirection == "SOURCE"
        assert {fitting_port_near_upstream.FlowDirection, fitting_port_near_downstream.FlowDirection} == {
            "SOURCE",
            "SINK",
        }

    def test_add_bend_with_no_established_flow_direction_stays_notdefined(self):
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
