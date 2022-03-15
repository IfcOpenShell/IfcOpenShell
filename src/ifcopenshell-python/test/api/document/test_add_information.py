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


class TestAddInformation(test.bootstrap.IFC4):
    def test_adding_information(self):
        project = self.file.createIfcProject()
        element = ifcopenshell.api.run("document.add_information", self.file, parent=None)
        assert element.is_a("IfcDocumentInformation")
        assert len(self.file.by_type("IfcDocumentInformation")) == 1

    def test_adding_information_to_the_project(self):
        project = self.file.createIfcProject()
        element = ifcopenshell.api.run("document.add_information", self.file, parent=None)
        rel = element.DocumentInfoForObjects[0]
        assert rel.is_a("IfcRelAssociatesDocument")
        assert rel.RelatedObjects[0] == project

    def test_adding_a_subdocument(self):
        project = self.file.createIfcProject()
        parent = ifcopenshell.api.run("document.add_information", self.file, parent=None)
        element = ifcopenshell.api.run("document.add_information", self.file, parent=parent)
        assert element.is_a("IfcDocumentInformation")
        assert len(self.file.by_type("IfcDocumentInformation")) == 2
        assert element.IsPointedTo[0].RelatingDocument == parent
        assert parent.IsPointer[0].RelatedDocuments[0] == element
        element2 = ifcopenshell.api.run("document.add_information", self.file, parent=parent)
        assert element in parent.IsPointer[0].RelatedDocuments
        assert element2 in parent.IsPointer[0].RelatedDocuments
