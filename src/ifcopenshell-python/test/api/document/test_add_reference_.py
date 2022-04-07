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


class TestAddReference(test.bootstrap.IFC4):
    def test_adding_a_reference(self):
        element = ifcopenshell.api.run("document.add_reference", self.file, information=None)
        assert element.is_a("IfcDocumentReference")
        assert len(self.file.by_type("IfcDocumentReference")) == 1

    def test_adding_a_reference_to_an_information(self):
        self.file.createIfcProject()
        information = ifcopenshell.api.run("document.add_information", self.file, parent=None)
        element = ifcopenshell.api.run("document.add_reference", self.file, information=information)
        assert element.is_a("IfcDocumentReference")
        assert len(self.file.by_type("IfcDocumentReference")) == 1
        assert element.ReferencedDocument == information
