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

import test.bootstrap
import ifcopenshell.api.feature
import ifcopenshell.api.root


class TestRemoveFeature(test.bootstrap.IFC4):
    def test_removing_a_simple_feature(self):
        feature = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcOpeningElement")
        ifcopenshell.api.feature.remove_feature(self.file, feature=feature)
        assert len(list(self.file)) == 0

    def test_removing_an_opening_voiding_a_wall(self):
        wall = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        opening = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcOpeningElement")
        ifcopenshell.api.feature.add_feature(self.file, feature=opening, element=wall)
        ifcopenshell.api.feature.remove_feature(self.file, feature=opening)
        assert len(self.file.by_type("IfcOpeningElement")) == 0
        assert len(self.file.by_type("IfcRelVoidsElement")) == 0
        assert wall

    def test_removing_an_opening_voiding_a_wall_with_a_filling(self):
        wall = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        opening = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcOpeningElement")
        door = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcDoor")
        ifcopenshell.api.feature.add_feature(self.file, feature=opening, element=wall)
        ifcopenshell.api.feature.add_filling(self.file, opening=opening, element=door)
        ifcopenshell.api.feature.remove_feature(self.file, feature=opening)
        assert len(self.file.by_type("IfcOpeningElement")) == 0
        assert len(self.file.by_type("IfcRelVoidsElement")) == 0
        assert len(self.file.by_type("IfcRelFillsElement")) == 0
        assert wall
        assert door


class TestRemoveFeatureIFC2X3(test.bootstrap.IFC2X3, TestRemoveFeature):
    pass
