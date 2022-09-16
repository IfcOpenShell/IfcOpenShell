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


class TestDisconnectPath(test.bootstrap.IFC4):
    def test_disconnecting_a_path(self):
        wall1 = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        wall2 = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        ifcopenshell.api.run("geometry.connect_path", self.file, relating_element=wall1, related_element=wall2)
        ifcopenshell.api.run("geometry.disconnect_path", self.file, relating_element=wall1, related_element=wall2)
        assert not self.file.by_type("IfcRelConnectsPathElements")

    def test_disconnecting_by_connection_type(self):
        wall1 = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        wall2 = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        ifcopenshell.api.run(
            "geometry.connect_path",
            self.file,
            relating_element=wall1,
            related_element=wall2,
            relating_connection="ATSTART",
            related_connection="ATEND",
        )
        ifcopenshell.api.run("geometry.disconnect_path", self.file, element=wall1, connection_type="ATEND")
        assert self.file.by_type("IfcRelConnectsPathElements")
        ifcopenshell.api.run("geometry.disconnect_path", self.file, element=wall1, connection_type="ATSTART")
        assert not self.file.by_type("IfcRelConnectsPathElements")
        ifcopenshell.api.run(
            "geometry.connect_path",
            self.file,
            relating_element=wall1,
            related_element=wall2,
            relating_connection="ATSTART",
            related_connection="ATEND",
        )
        ifcopenshell.api.run("geometry.disconnect_path", self.file, element=wall2, connection_type="ATEND")
        assert not self.file.by_type("IfcRelConnectsPathElements")

    def test_doing_nothing_if_there_is_no_connection(self):
        wall1 = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        wall2 = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        total_elements = len([e for e in self.file])
        ifcopenshell.api.run("geometry.disconnect_path", self.file, relating_element=wall1, related_element=wall2)
        assert len([e for e in self.file]) == total_elements

    def test_that_order_matters(self):
        wall1 = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        wall2 = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        ifcopenshell.api.run("geometry.connect_path", self.file, relating_element=wall1, related_element=wall2)
        total_elements = len([e for e in self.file])
        ifcopenshell.api.run("geometry.disconnect_path", self.file, relating_element=wall2, related_element=wall1)
        assert len([e for e in self.file]) == total_elements
