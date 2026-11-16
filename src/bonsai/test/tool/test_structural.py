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

import ifcopenshell
import pytest

import bonsai.core.tool
import bonsai.tool as tool
from bonsai.tool.structural import Structural as subject
from test.bim.bootstrap import NewFile


class TestImplementsTool(NewFile):
    def test_run(self):
        assert isinstance(subject(), bonsai.core.tool.Structural)


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


class TestGetStructuralItemPredefinedTypes(NewFile):
    def test_a_curve_member_without_userdefined(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        types = subject.get_structural_item_predefined_types("IfcStructuralCurveMember")
        assert "RIGID_JOINED_MEMBER" in types
        assert "NOTDEFINED" in types
        assert "USERDEFINED" not in types

    def test_a_connection_has_none(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        assert subject.get_structural_item_predefined_types("IfcStructuralPointConnection") == []


class TestGetStructuralItemRepresentationTemplate(NewFile):
    def test_run(self):
        assert subject.get_structural_item_representation_template("IfcStructuralPointConnection") == "VERTEX"
        assert subject.get_structural_item_representation_template("IfcStructuralCurveMember") == "EDGE"
        assert subject.get_structural_item_representation_template("IfcStructuralCurveConnection") == "EDGE"
        assert subject.get_structural_item_representation_template("IfcStructuralSurfaceMember") == "FACE"
        assert subject.get_structural_item_representation_template("IfcStructuralSurfaceConnection") == "FACE"

    def test_an_item_of_no_dimension(self):
        with pytest.raises(ValueError):
            subject.get_structural_item_representation_template("IfcStructuralItem")
