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
    def test_connecting_a_path(self):
        wall1 = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        wall2 = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        rel = self.connect_path(wall1, wall2, "ATSTART", "ATEND", description="MITRE")
        assert rel.is_a("IfcRelConnectsPathElements")
        assert rel.RelatingElement == wall1
        assert rel.RelatedElement == wall2
        assert rel.RelatingConnectionType == "ATSTART"
        assert rel.RelatedConnectionType == "ATEND"
        assert rel.Description == "MITRE"

    def test_doing_nothing_if_the_element_is_already_connected(self):
        wall1 = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        wall2 = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        self.connect_path(wall1, wall2)
        total_elements = len([e for e in self.file])
        self.connect_path(wall1, wall2)
        assert len([e for e in self.file]) == total_elements

    def test_updating_the_connection_type_if_already_connected(self):
        wall1 = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        wall2 = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        ifcopenshell.api.run("geometry.connect_path", self.file, relating_element=wall1, related_element=wall2)
        total_elements = len([e for e in self.file])
        rel = self.connect_path(wall1, wall2, "ATSTART")
        assert rel.RelatingConnectionType == "ATSTART"
        assert rel.RelatedConnectionType == "NOTDEFINED"

    def test_preventing_cyclical_connections(self):
        wall1 = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        wall2 = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        ifcopenshell.api.run("geometry.connect_path", self.file, relating_element=wall1, related_element=wall2)
        total_elements = len([e for e in self.file])
        ifcopenshell.api.run("geometry.connect_path", self.file, relating_element=wall2, related_element=wall1)
        assert len([e for e in self.file]) == total_elements

    def test_a_relating_element_can_have_multiple_path_connections(self):
        wall1 = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        wall2 = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        wall3 = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        rel1 = self.connect_path(wall1, wall2, "ATPATH", "ATEND")
        rel2 = self.connect_path(wall1, wall3, "ATPATH", "ATSTART")
        assert len(self.file.by_type("IfcRelConnectsPathElements")) == 2
        assert rel1.RelatingElement == wall1
        assert rel1.RelatedElement == wall2
        assert rel1.RelatingConnectionType == "ATPATH"
        assert rel1.RelatedConnectionType == "ATEND"
        assert rel2.RelatingElement == wall1
        assert rel2.RelatedElement == wall3
        assert rel2.RelatingConnectionType == "ATPATH"
        assert rel2.RelatedConnectionType == "ATSTART"

    def test_a_element_can_only_have_up_to_one_start_or_end_connections(self):
        wall1 = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        wall2 = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        wall3 = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        rel1 = self.connect_path(wall1, wall2, "ATSTART", "ATEND")
        rel2 = self.connect_path(wall1, wall3, "ATEND", "ATSTART")
        assert len(self.file.by_type("IfcRelConnectsPathElements")) == 2

        self.file = ifcopenshell.file()
        wall1 = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        wall2 = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        wall3 = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        rel1 = self.connect_path(wall1, wall2, "ATSTART", "ATEND")
        rel2 = self.connect_path(wall1, wall3, "ATSTART", "ATSTART")
        assert len(self.file.by_type("IfcRelConnectsPathElements")) == 1

        self.file = ifcopenshell.file()
        wall1 = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        wall2 = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        wall3 = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        rel1 = self.connect_path(wall1, wall2, "ATEND", "ATEND")
        rel2 = self.connect_path(wall1, wall3, "ATEND", "ATSTART")
        assert len(self.file.by_type("IfcRelConnectsPathElements")) == 1

        self.file = ifcopenshell.file()
        wall1 = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        wall2 = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        wall3 = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        rel1 = self.connect_path(wall1, wall2, "ATPATH", "ATEND")
        rel2 = self.connect_path(wall1, wall3, "ATPATH", "ATSTART")
        assert len(self.file.by_type("IfcRelConnectsPathElements")) == 2

        self.file = ifcopenshell.file()
        wall1 = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        wall2 = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        wall3 = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        rel1 = self.connect_path(wall2, wall1, "ATPATH", "ATEND")
        rel2 = self.connect_path(wall3, wall1, "ATPATH", "ATSTART")
        assert len(self.file.by_type("IfcRelConnectsPathElements")) == 2

        self.file = ifcopenshell.file()
        wall1 = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        wall2 = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        wall3 = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        rel1 = self.connect_path(wall2, wall1, "ATPATH", "ATSTART")
        rel2 = self.connect_path(wall3, wall1, "ATPATH", "ATSTART")
        assert len(self.file.by_type("IfcRelConnectsPathElements")) == 1

        self.file = ifcopenshell.file()
        wall1 = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        wall2 = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        wall3 = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        rel1 = self.connect_path(wall2, wall1, "ATPATH", "ATEND")
        rel2 = self.connect_path(wall3, wall1, "ATPATH", "ATEND")
        assert len(self.file.by_type("IfcRelConnectsPathElements")) == 1

    def connect_path(
        self,
        relating_element,
        related_element,
        relating_connection="NOTDEFINED",
        related_connection="NOTDEFINED",
        description=None,
    ):
        return ifcopenshell.api.run(
            "geometry.connect_path",
            self.file,
            relating_element=relating_element,
            related_element=related_element,
            relating_connection=relating_connection,
            related_connection=related_connection,
            description=description,
        )
