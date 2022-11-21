# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
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

import ifcopenshell
import test.bootstrap
import ifcopenshell.util.placement as subject


class TestGetStoreyElevationIFC4(test.bootstrap.IFC4):
    def test_run(self):
        storey = self.file.createIfcBuildingStorey()
        placement = self.file.createIfcLocalPlacement()
        placement.RelativePlacement = self.file.createIfcAxis2Placement3D(
            self.file.createIfcCartesianPoint((0.0, 0.0, 3.0))
        )
        storey.ObjectPlacement = placement
        assert subject.get_storey_elevation(storey) == 3.0

    def test_getting_the_elevation_if_no_z_location(self):
        storey = self.file.createIfcBuildingStorey()
        storey.Elevation = 3.0
        assert subject.get_storey_elevation(storey) == 3.0

    def test_returning_0_as_a_fallback(self):
        storey = self.file.createIfcBuildingStorey()
        assert subject.get_storey_elevation(storey) == 0.0
        building = self.file.createIfcBuilding()
        assert subject.get_storey_elevation(building) == 0.0
