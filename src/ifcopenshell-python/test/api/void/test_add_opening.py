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
import ifcopenshell.api


class TestAddOpening(test.bootstrap.IFC4):
    def test_adding_an_opening(self):
        wall = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        opening = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcOpeningElement")
        ifcopenshell.api.run("void.add_opening", self.file, opening=opening, element=wall)
        assert wall.HasOpenings[0].RelatedOpeningElement == opening

    def test_adding_an_opening_twice(self):
        wall = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        opening = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcOpeningElement")
        ifcopenshell.api.run("void.add_opening", self.file, opening=opening, element=wall)
        ifcopenshell.api.run("void.add_opening", self.file, opening=opening, element=wall)
        assert wall.HasOpenings[0].RelatedOpeningElement == opening
        assert len(wall.HasOpenings) == 1

    def test_adding_an_opening_which_is_already_voiding_another_element(self):
        slab = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcSlab")
        wall = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        opening = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcOpeningElement")
        ifcopenshell.api.run("void.add_opening", self.file, opening=opening, element=slab)
        ifcopenshell.api.run("void.add_opening", self.file, opening=opening, element=wall)
        assert not slab.HasOpenings
        assert wall.HasOpenings[0].RelatedOpeningElement == opening
