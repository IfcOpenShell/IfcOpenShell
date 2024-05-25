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


class TestRemoveInformation(test.bootstrap.IFC4):
    def test_remove_information(self):
        self.file.createIfcProject()
        element = ifcopenshell.api.run("document.add_information", self.file, parent=None)
        ifcopenshell.api.run("document.remove_information", self.file, information=element)
        assert len(self.file.by_type("IfcDocumentInformation")) == 0
        assert len(self.file.by_type("IfcRelAssociatesDocument")) == 0

    def test_removing_all_references_of_an_information(self):
        self.file.createIfcProject()
        information = ifcopenshell.api.run("document.add_information", self.file, parent=None)
        ifcopenshell.api.run("document.add_reference", self.file, information=information)
        ifcopenshell.api.run("document.remove_information", self.file, information=information)
        assert len(self.file.by_type("IfcDocumentInformation")) == 0
        assert len(self.file.by_type("IfcDocumentReference")) == 0
        assert len(self.file.by_type("IfcRelAssociatesDocument")) == 0

        # test removing relationship to another information if it was the only relating element
        information = ifcopenshell.api.run("document.add_information", self.file, parent=None)
        information1 = ifcopenshell.api.run("document.add_information", self.file, parent=information)
        information2 = ifcopenshell.api.run("document.add_information", self.file, parent=information)

        ifcopenshell.api.run("document.remove_information", self.file, information=information1)
        assert len(self.file.by_type("IfcDocumentInformation")) == 2
        assert len(self.file.by_type("IfcDocumentInformationRelationship")) == 1

        ifcopenshell.api.run("document.remove_information", self.file, information=information2)
        assert len(self.file.by_type("IfcDocumentInformation")) == 1
        assert len(self.file.by_type("IfcDocumentInformationRelationship")) == 0

    def test_removing_all_subdocuments_and_their_references_too(self):
        self.file.createIfcProject()
        information = ifcopenshell.api.run("document.add_information", self.file, parent=None)
        information2 = ifcopenshell.api.run("document.add_information", self.file, parent=information)
        ifcopenshell.api.run("document.add_reference", self.file, information=information2)
        ifcopenshell.api.run("document.remove_information", self.file, information=information)
        assert len(self.file.by_type("IfcDocumentInformation")) == 0
        assert len(self.file.by_type("IfcDocumentReference")) == 0
        assert len(self.file.by_type("IfcRelAssociatesDocument")) == 0
        assert len(self.file.by_type("IfcDocumentInformationRelationship")) == 0


class TestRemoveInformationIFC2X3(TestRemoveInformation, test.bootstrap.IFC2X3):
    pass
