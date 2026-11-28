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

import math

import bpy
import ifcopenshell.api.attribute
from mathutils import Vector

import bonsai.tool as tool
from bonsai.bim.module.system.data import ObjectSystemData, SystemDecorationData
from bonsai.tool.system import System as subject
from bonsai.tool.system import bend_curve_points
from test.bim.bootstrap import NewFile


class TestBendCurvePoints:
    PORT_A = Vector((2.7, 2.0, 0.0))
    AXIS_A = Vector((1.0, 0.0, 0.0))
    PORT_B = Vector((3.075, 1.625, 0.0))
    AXIS_B = Vector((0.0, 1.0, 0.0))

    def test_90_degree_bend_hugs_the_true_arc(self):
        points = bend_curve_points(self.PORT_A, self.AXIS_A, self.PORT_B, self.AXIS_B)
        assert points is not None
        assert points[0] == self.PORT_A
        assert points[-1] == self.PORT_B

        center = Vector((2.7, 1.625, 0.0))
        radius = 0.375
        true_arc_midpoint = center + ((self.PORT_A - center) + (self.PORT_B - center)).normalized() * radius
        curve_midpoint = points[len(points) // 2]
        chord_midpoint = (self.PORT_A + self.PORT_B) / 2

        curve_error = (curve_midpoint - true_arc_midpoint).length
        chord_error = (chord_midpoint - true_arc_midpoint).length
        assert curve_error < 1e-4
        assert chord_error > 0.1
        assert curve_error < chord_error / 100

    def test_degenerate_axes_fall_back_to_straight_line(self):
        assert bend_curve_points(Vector((0, 0, 0)), Vector((1, 0, 0)), Vector((2, 0, 0)), Vector((-1, 0, 0))) is None
        assert bend_curve_points(Vector((0, 0, 0)), None, Vector((2, 0, 0)), Vector((1, 0, 0))) is None
        assert bend_curve_points(Vector((0, 0, 0)), Vector((0, 0, 0)), Vector((2, 0, 0)), Vector((1, 0, 0))) is None
        assert bend_curve_points(Vector((0, 0, 0)), Vector((-1, 0, 0)), Vector((2, 0, 0)), Vector((1, 0, 0))) is None
        assert bend_curve_points(Vector((1, 1, 1)), Vector((1, 0, 0)), Vector((1, 1, 1)), Vector((0, 1, 0))) is None

    def test_shallow_and_sharp_angles_stay_close_to_the_true_arc(self):
        center = Vector((0.0, 1.0, 0.0))
        radius = 1.0
        port_a = center + Vector((0, -1, 0)) * radius
        axis_a = Vector((1, 0, 0))
        for degrees in (5, 10, 30, 45, 90):
            theta = math.radians(degrees)
            port_b = center + Vector((math.sin(theta), -math.cos(theta), 0)) * radius
            axis_b = -Vector((math.cos(theta), math.sin(theta), 0))
            points = bend_curve_points(port_a, axis_a, port_b, axis_b)
            assert points is not None, f"expected a curve at {degrees} degrees"
            true_mid = center + ((port_a - center) + (port_b - center)).normalized() * radius
            curve_mid = points[len(points) // 2]
            assert (curve_mid - true_mid).length < 0.011, f"curve strayed too far from the arc at {degrees} degrees"

    def test_extreme_near_reversal_falls_back_to_straight_line(self):
        center = Vector((0.0, 1.0, 0.0))
        radius = 1.0
        port_a = center + Vector((0, -1, 0)) * radius
        axis_a = Vector((1, 0, 0))
        theta = math.radians(170)
        port_b = center + Vector((math.sin(theta), -math.cos(theta), 0)) * radius
        axis_b = -Vector((math.cos(theta), math.sin(theta), 0))
        assert bend_curve_points(port_a, axis_a, port_b, axis_b) is None


class TestBuildDecorationDataBendCurve(NewFile):
    FIXTURE = "test/files/mep-duct-bend-flow-direction.ifc"
    SEGMENT_UPSTREAM_ID = 4276
    SEGMENT_DOWNSTREAM_ID = 4298
    UPSTREAM_PORT_ID = 4350
    STRAIGHT_SEGMENT_ID = 4252

    def _build_bend(self):
        result = bpy.ops.bim.load_project(filepath=self.FIXTURE)
        assert result == {"FINISHED"}
        ifc = tool.Ifc.get()

        upstream_obj = tool.Ifc.get_object(ifc.by_id(self.SEGMENT_UPSTREAM_ID))
        downstream_obj = tool.Ifc.get_object(ifc.by_id(self.SEGMENT_DOWNSTREAM_ID))
        bpy.context.view_layer.objects.active = upstream_obj
        upstream_obj.select_set(True)
        downstream_obj.select_set(True)

        result = bpy.ops.bim.mep_add_bend(
            start_segment_id=ifc.by_id(self.SEGMENT_UPSTREAM_ID).id(),
            end_segment_id=ifc.by_id(self.SEGMENT_DOWNSTREAM_ID).id(),
        )
        assert result == {"FINISHED"}

        fitting_port = subject.get_connected_port(ifc.by_id(self.UPSTREAM_PORT_ID))
        fitting = subject.get_port_relating_element(fitting_port)
        assert fitting.is_a("IfcDuctFitting")

        for port in subject.get_ports(fitting):
            ifcopenshell.api.attribute.edit_attributes(
                ifc, product=port, attributes={"FlowDirection": "SINK" if port == fitting_port else "SOURCE"}
            )
        return ifc, fitting

    def _decoration_for(self, ifc, element):
        obj = tool.Ifc.get_object(element)
        bpy.ops.object.select_all(action="DESELECT")
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        bpy.context.view_layer.update()

        ObjectSystemData.is_loaded = False
        ObjectSystemData.load()
        SystemDecorationData.is_loaded = False
        SystemDecorationData.load()
        SystemDecorationData.data["decorated_elements"] = {element}
        subject._decoration_data_cache_key = None
        subject._decoration_data_cache = None
        return subject._build_decoration_data()

    def test_bend_fitting_draws_a_curve_not_a_chord(self):
        ifc, fitting = self._build_bend()
        data = self._decoration_for(ifc, fitting)

        assert len(data["all_vertices"]) > 14
        port_a, port_b = data["all_vertices"][0], data["all_vertices"][1]
        max_deviation = 0.0
        chord_dir = (port_b - port_a).normalized()
        for vertex in data["all_vertices"][2:]:
            offset = vertex - port_a
            lateral = offset - chord_dir * offset.dot(chord_dir)
            max_deviation = max(max_deviation, lateral.length)
        assert max_deviation > 0.05

    def test_straight_segment_decoration_is_unaffected(self):
        ifc, _fitting = self._build_bend()

        segment = ifc.by_id(self.STRAIGHT_SEGMENT_ID)
        ports = subject.get_ports(segment)
        for i, port in enumerate(ports):
            ifcopenshell.api.attribute.edit_attributes(
                ifc, product=port, attributes={"FlowDirection": "SOURCE" if i == 0 else "SINK"}
            )

        data = self._decoration_for(ifc, segment)
        assert data["selected_edges"][0] == (0, 1)
        port_a, port_b = data["all_vertices"][0], data["all_vertices"][1]
        chord_dir = (port_b - port_a).normalized()
        direction_lines_width = 0.05
        for vertex in data["all_vertices"][2:]:
            offset = vertex - port_a
            lateral = offset - chord_dir * offset.dot(chord_dir)
            assert lateral.length < 1e-4 or abs(lateral.length - direction_lines_width) < 1e-4
