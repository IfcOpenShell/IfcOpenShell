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

import bpy
import ifcopenshell.api.material
import ifcopenshell.api.root
import ifcopenshell.util.element
import ifcopenshell.util.system

import bonsai.tool as tool
from bonsai.bim.module.model.mep import MEPGenerator
from test.bim.bootstrap import NewFile


def _add_profiled_segment_type(ifc, ifc_class, profile, name):
    segment_type = ifcopenshell.api.root.create_entity(ifc, ifc_class=ifc_class, name=name)
    material = ifcopenshell.api.material.add_material(ifc, name=name)
    profile_set = ifcopenshell.api.material.add_material_set(ifc, name=name, set_type="IfcMaterialProfileSet")
    ifcopenshell.api.material.add_profile(ifc, profile_set=profile_set, material=material, profile=profile)
    ifcopenshell.api.material.assign_material(
        ifc, products=[segment_type], type="IfcMaterialProfileSet", material=profile_set
    )
    return segment_type


class TestMEPConnectPorts(NewFile):
    def _pipe_occurrence(self, segment_type):
        bpy.ops.bim.add_occurrence(relating_type_id=segment_type.id())
        return bpy.context.active_object, tool.Ifc.get_entity(bpy.context.active_object)

    def _select_free_ports(self, seg_a, seg_b):
        for segment in (seg_a, seg_b):
            tool.Blender.select_and_activate_single_object(bpy.context, tool.Ifc.get_object(segment))
            bpy.ops.bim.show_ports()
        port_a = MEPGenerator.get_segment_data(seg_a)["end_port"]
        port_b = MEPGenerator.get_segment_data(seg_b)["start_port"]
        port_a_obj = tool.Ifc.get_object(port_a)
        port_b_obj = tool.Ifc.get_object(port_b)
        assert port_a_obj and port_b_obj
        bpy.ops.object.select_all(action="DESELECT")
        port_a_obj.select_set(True)
        port_b_obj.select_set(True)
        bpy.context.view_layer.objects.active = port_a_obj
        return port_a, port_b

    def _make_collinear_segments(self, type_a, type_b):
        obj_a, seg_a = self._pipe_occurrence(type_a)
        obj_b, seg_b = self._pipe_occurrence(type_b)
        axis_start, axis_end = tool.Model.get_flow_segment_axis(obj_a)
        axis_dir = (axis_end - axis_start).normalized()
        length = (axis_end - axis_start).length
        obj_b.matrix_world = obj_a.matrix_world.copy()
        obj_b.matrix_world.translation = axis_end + axis_dir * length
        bpy.context.view_layer.update()
        tool.System.run_geometry_edit_object_placement(obj_b)
        return seg_a, seg_b

    def test_connect_same_profile_ports_with_bridging_segment(self):
        bpy.ops.bim.create_project()
        ifc = tool.Ifc.get()
        profile = ifc.create_entity("IfcCircleProfileDef", ProfileType="AREA", ProfileName="DN100", Radius=50.0)
        type_a = _add_profiled_segment_type(ifc, "IfcPipeSegmentType", profile, "A")
        seg_a, seg_b = self._make_collinear_segments(type_a, type_a)
        port_a, port_b = self._select_free_ports(seg_a, seg_b)

        assert bpy.ops.bim.mep_connect_ports() == {"FINISHED"}

        bridge_port = ifcopenshell.util.system.get_connected_port(port_a)
        assert bridge_port
        bridge = ifcopenshell.util.system.get_port_element(bridge_port)
        assert bridge.is_a("IfcPipeSegment") and bridge not in (seg_a, seg_b)
        assert ifcopenshell.util.element.get_type(bridge) == type_a
        far_port = ifcopenshell.util.system.get_connected_port(port_b)
        assert far_port and ifcopenshell.util.system.get_port_element(far_port) == bridge
        assert len(ifc.by_type("IfcPipeFitting")) == 0

    def test_connect_differing_profiles_inserts_transition(self):
        bpy.ops.bim.create_project()
        ifc = tool.Ifc.get()
        profile_a = ifc.create_entity("IfcCircleProfileDef", ProfileType="AREA", ProfileName="DN100", Radius=0.05)
        profile_b = ifc.create_entity("IfcCircleProfileDef", ProfileType="AREA", ProfileName="DN50", Radius=0.025)
        type_a = _add_profiled_segment_type(ifc, "IfcPipeSegmentType", profile_a, "A")
        type_b = _add_profiled_segment_type(ifc, "IfcPipeSegmentType", profile_b, "B")
        seg_a, seg_b = self._make_collinear_segments(type_a, type_b)
        port_a, port_b = self._select_free_ports(seg_a, seg_b)

        assert bpy.ops.bim.mep_connect_ports() == {"FINISHED"}

        bridge_port = ifcopenshell.util.system.get_connected_port(port_a)
        assert bridge_port
        bridge = ifcopenshell.util.system.get_port_element(bridge_port)
        assert bridge.is_a("IfcPipeSegment") and ifcopenshell.util.element.get_type(bridge) == type_a
        fittings = ifc.by_type("IfcPipeFitting")
        assert len(fittings) == 1
        assert ifcopenshell.util.element.get_predefined_type(fittings[0]) == "TRANSITION"
        far_port = ifcopenshell.util.system.get_connected_port(port_b)
        assert far_port and ifcopenshell.util.system.get_port_element(far_port) == fittings[0]
