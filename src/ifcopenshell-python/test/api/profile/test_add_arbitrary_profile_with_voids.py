# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2026 Dion Moult <dion@thinkmoult.com>
#
# This file is part of IfcOpenShell.
#
# IfcOpenShell is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcOpenShell is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcOpenShell.  If not, see <http://www.gnu.org/licenses/>.

# This file was generated with the assistance of an AI coding tool.

import ifcopenshell.api.profile
import test.bootstrap


class TestAddArbitraryProfileWithVoidsIFC4(test.bootstrap.IFC4):
    def test_2d_profile_uses_a_2d_point_list_for_the_outer_curve(self):
        profile = ifcopenshell.api.profile.add_arbitrary_profile_with_voids(
            self.file,
            outer_profile=[(0.0, 0.0), (0.4, 0.0), (0.4, 0.4), (0.0, 0.4), (0.0, 0.0)],
            inner_profiles=[[(0.1, 0.1), (0.3, 0.1), (0.3, 0.3), (0.1, 0.3), (0.1, 0.1)]],
            name="Test",
        )
        outer_points = profile.OuterCurve.Points
        assert outer_points.is_a("IfcCartesianPointList2D")
        assert all(len(co) == 2 for co in outer_points.CoordList)
        assert profile.OuterCurve.Dim == 2

    def test_3d_profile_still_uses_a_3d_point_list_for_the_outer_curve(self):
        profile = ifcopenshell.api.profile.add_arbitrary_profile_with_voids(
            self.file,
            outer_profile=[(0.0, 0.0, 0.0), (0.4, 0.0, 0.0), (0.4, 0.4, 0.0), (0.0, 0.4, 0.0), (0.0, 0.0, 0.0)],
            inner_profiles=[[(0.1, 0.1, 0.0), (0.3, 0.1, 0.0), (0.3, 0.3, 0.0), (0.1, 0.3, 0.0), (0.1, 0.1, 0.0)]],
            name="Test",
        )
        outer_points = profile.OuterCurve.Points
        assert outer_points.is_a("IfcCartesianPointList3D")
        assert all(len(co) == 3 for co in outer_points.CoordList)
