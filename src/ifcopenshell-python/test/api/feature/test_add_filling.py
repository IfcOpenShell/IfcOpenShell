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


class TestAddFilling(test.bootstrap.IFC4):
    def test_adding_a_filling(self):
        opening = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcOpeningElement")
        door = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcDoor")
        ifcopenshell.api.feature.add_filling(self.file, opening=opening, element=door)
        assert door.FillsVoids[0].RelatingOpeningElement == opening

    def test_adding_a_filling_twice(self):
        opening = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcOpeningElement")
        door = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcDoor")
        ifcopenshell.api.feature.add_filling(self.file, opening=opening, element=door)
        ifcopenshell.api.feature.add_filling(self.file, opening=opening, element=door)
        assert door.FillsVoids[0].RelatingOpeningElement == opening
        assert len(opening.HasFillings) == 1

    def test_adding_a_filling_which_is_already_filling_another_opening(self):
        door = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcDoor")
        opening1 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcOpeningElement")
        opening2 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcOpeningElement")
        ifcopenshell.api.feature.add_filling(self.file, opening=opening1, element=door)
        ifcopenshell.api.feature.add_filling(self.file, opening=opening2, element=door)
        assert not opening1.HasFillings
        assert opening2.HasFillings[0].RelatedBuildingElement == door


class TestAddFillingIFC2X3(test.bootstrap.IFC2X3, TestAddFilling):
    pass
