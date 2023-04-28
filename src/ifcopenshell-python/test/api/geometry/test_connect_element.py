# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2022 Dion Moult <dion@thinkmoult.com>
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


class TestConnectPath(test.bootstrap.IFC4):
    def test_connecting_an_element(self):
        wall1 = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        wall2 = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        rel = ifcopenshell.api.run(
            "geometry.connect_element",
            self.file,
            relating_element=wall1,
            related_element=wall2,
            description="FOOBAR",
        )
        assert rel.is_a() == "IfcRelConnectsElements"
        assert rel.RelatingElement == wall1
        assert rel.RelatedElement == wall2
        assert rel.Description == "FOOBAR"

    def test_reconnecting_an_element_changes_the_description(self):
        wall1 = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        wall2 = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        rel = ifcopenshell.api.run(
            "geometry.connect_element",
            self.file,
            relating_element=wall1,
            related_element=wall2,
            description="FOOBAR",
        )
        assert rel.is_a() == "IfcRelConnectsElements"
        assert rel.RelatingElement == wall1
        assert rel.RelatedElement == wall2
        assert rel.Description == "FOOBAR"

        total_elements = len([e for e in self.file])
        rel = ifcopenshell.api.run(
            "geometry.connect_element",
            self.file,
            relating_element=wall1,
            related_element=wall2,
            description="FOOBAZ",
        )
        assert len([e for e in self.file]) == total_elements
        assert rel.Description == "FOOBAZ"

    def test_reconnecting_and_changing_the_order(self):
        wall1 = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        wall2 = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        rel = ifcopenshell.api.run(
            "geometry.connect_element",
            self.file,
            relating_element=wall1,
            related_element=wall2,
            description="FOOBAR",
        )
        assert rel.RelatingElement == wall1
        assert rel.RelatedElement == wall2

        total_elements = len([e for e in self.file])
        rel = ifcopenshell.api.run(
            "geometry.connect_element",
            self.file,
            relating_element=wall2,
            related_element=wall1,
            description="FOOBAZ",
        )
        assert rel.RelatingElement == wall2
        assert rel.RelatedElement == wall1
