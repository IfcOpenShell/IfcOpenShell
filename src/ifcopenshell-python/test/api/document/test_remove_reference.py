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


class TestRemoveReference(test.bootstrap.IFC4):
    def test_removing_reference(self):
        project = self.file.createIfcProject()
        information = ifcopenshell.api.run("document.add_information", self.file, parent=None)
        reference = ifcopenshell.api.run("document.add_reference", self.file, information=information)
        ifcopenshell.api.run("document.remove_reference", self.file, reference=reference)
        assert len(self.file.by_type("IfcDocumentReference")) == 0
        assert len(self.file.by_type("IfcDocumentInformation")) == 1
        assert len(self.file.by_type("IfcRelAssociatesDocument")) == 1

    def test_removing_a_reference_assigned_to_an_object(self):
        project = self.file.createIfcProject()
        wall = self.file.createIfcWall()
        information = ifcopenshell.api.run("document.add_information", self.file, parent=None)
        reference = ifcopenshell.api.run("document.add_reference", self.file, information=information)
        ifcopenshell.api.run("document.assign_document", self.file, product=wall, document=reference)
        assert len(self.file.by_type("IfcRelAssociatesDocument")) == 2
        ifcopenshell.api.run("document.remove_reference", self.file, reference=reference)
        assert len(self.file.by_type("IfcDocumentReference")) == 0
        assert len(self.file.by_type("IfcDocumentInformation")) == 1
        assert len(self.file.by_type("IfcRelAssociatesDocument")) == 1
