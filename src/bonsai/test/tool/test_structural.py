# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2026 Ryan Schultz
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

# This file was generated with the assistance of an AI coding tool.

import math

import bpy
import ifcopenshell
import ifcopenshell.api.context
import ifcopenshell.api.geometry
import ifcopenshell.api.profile
import ifcopenshell.api.root
import ifcopenshell.api.structural
import numpy as np

import bonsai.core.tool
import bonsai.tool as tool
from bonsai.tool.structural import Structural as subject
from test.bim.bootstrap import NewFile


class TestImplementsTool(NewFile):
    def test_run(self):
        assert isinstance(subject(), bonsai.core.tool.Structural)


class TestFindNearbyConnection(NewFile):
    def test_zero_tolerance_does_not_merge_coincident_points(self):
        assert subject.find_nearby_connection((0, 0, 0), [((0, 0, 0), "first")], 0) is None

    def test_finds_nearest_connection_within_tolerance(self):
        connections = [((0, 0, 0), "first"), ((0.09, 0, 0), "second")]
        assert subject.find_nearby_connection((0.08, 0, 0), connections, 0.1) == "second"
        assert subject.find_nearby_connection((1, 0, 0), connections, 0.1) is None


class TestIsGeneratedConnection(NewFile):
    def test_only_connections_of_linked_curve_members_are_generated(self):
        ifc = ifcopenshell.file(schema="IFC4")
        node = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcStructuralPointConnection")
        member = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcStructuralCurveMember")
        source = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcBeam")
        assert not subject.is_generated_connection(node)
        ifcopenshell.api.structural.assign_product(ifc, relating_product=source, related_object=member)
        ifcopenshell.api.structural.add_structural_member_connection(
            ifc, relating_structural_member=member, related_structural_connection=node
        )
        assert subject.is_generated_connection(node)
        external = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcStructuralCurveMember")
        ifcopenshell.api.structural.add_structural_member_connection(
            ifc, relating_structural_member=external, related_structural_connection=node
        )
        assert not subject.is_generated_connection(node)


class TestGetPhysicalMemberAxis(NewFile):
    def test_profile_orientation_is_projected_onto_the_member_section(self):
        direction = subject.get_member_orientation(np.array((0.0, 0.0, 1.0)), np.array((1.0, 0.0, 1.0)))
        assert np.allclose(direction, (-(2**-0.5), 0.0, 2**-0.5))
        assert subject.get_member_orientation(np.array((0.0, 0.0, 1.0)), np.array((0.0, 0.0, 1.0))) is None
        assert subject.get_member_orientation(np.array((0.0, 0.0, 1.0)), np.zeros(3)) is None

    def test_profile_extrusion_and_object_placement(self):
        ifc = ifcopenshell.file(schema="IFC4")
        tool.Ifc.set(ifc)
        ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcProject")
        model = ifcopenshell.api.context.add_context(ifc, context_type="Model")
        body = ifcopenshell.api.context.add_context(
            ifc, context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=model
        )
        profile = ifcopenshell.api.profile.add_parameterized_profile(ifc, ifc_class="IfcRectangleProfileDef")
        profile.XDim, profile.YDim = 0.2, 0.3
        element = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcColumn")
        representation = ifcopenshell.api.geometry.add_profile_representation(
            ifc, context=body, profile=profile, depth=3
        )
        ifcopenshell.api.geometry.assign_representation(ifc, product=element, representation=representation)
        obj = bpy.data.objects.new("Column", None)
        bpy.context.scene.collection.objects.link(obj)
        tool.Ifc.link(element, obj)
        obj.location = (2, 4, 1)
        bpy.context.view_layer.update()
        start, end = subject.get_physical_member_axis(obj)
        assert np.allclose(start, (2, 4, 1))
        assert np.allclose(end, (2, 4, 4))
        obj.rotation_euler.y = math.pi / 2
        bpy.context.view_layer.update()
        start, end = subject.get_physical_member_axis(obj)
        assert np.allclose(start, (2, 4, 1))
        assert np.allclose(end, (5, 4, 1), atol=1e-6)


class TestGetInPlaneComponents(NewFile):
    def test_an_angle_above_the_horizontal(self):
        x, z = subject.get_in_plane_components("ANGLE", magnitude=10, angle=30)
        assert math.isclose(x, 10 * math.cos(math.radians(30)))
        assert math.isclose(z, 5)

    def test_a_slope(self):
        x, z = subject.get_in_plane_components("SLOPE", magnitude=10, rise=5, run=12)
        assert math.isclose(x, 120 / 13)
        assert math.isclose(z, 50 / 13)

    def test_directions_measure_from_the_nearest_horizontal(self):
        x, z = subject.get_in_plane_components("ANGLE", magnitude=100, angle=40, direction="UP_LEFT")
        assert math.isclose(x, -100 * math.cos(math.radians(40)))
        assert math.isclose(z, 100 * math.sin(math.radians(40)))
        x, z = subject.get_in_plane_components("SLOPE", magnitude=200, rise=3, run=4, direction="DOWN_LEFT")
        assert math.isclose(x, -160)
        assert math.isclose(z, -120)
        x, z = subject.get_in_plane_components("ANGLE", magnitude=1, angle=60, direction="DOWN_RIGHT")
        assert x > 0 and z < 0

    def test_a_zero_slope_gives_no_force(self):
        assert subject.get_in_plane_components("SLOPE", magnitude=10, rise=0, run=0) == (0.0, 0.0)


class TestGetSimpleSlope(NewFile):
    def test_reducing_to_small_whole_numbers(self):
        assert subject.get_simple_slope(-160, -120) == (-3, -4)
        assert subject.get_simple_slope(134.16407864998737, -268.3281572999747) == (-2, 1)

    def test_axis_aligned_components(self):
        assert subject.get_simple_slope(5, 0) == (0.0, 1.0)
        assert subject.get_simple_slope(0, -5) == (-1.0, 0.0)

    def test_no_force_gives_a_unit_slope(self):
        assert subject.get_simple_slope(0, 0) == (1.0, 1.0)

    def test_falling_back_to_a_unit_slope(self):
        rise, run = subject.get_simple_slope(3, 7.1)
        assert math.isclose(math.hypot(rise, run), 1)
        assert math.isclose(rise / run, 7.1 / 3)
