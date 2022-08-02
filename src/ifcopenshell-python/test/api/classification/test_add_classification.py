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


class TestAddClassification(test.bootstrap.IFC4):
    def test_adding_a_classification(self):
        ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcProject")
        ifcopenshell.api.run("classification.add_classification", self.file, classification="Name")
        assert self.file.by_type("IfcClassification")[0].Name == "Name"

    def test_adding_a_classification_from_a_library(self):
        library = ifcopenshell.file()
        classification = library.createIfcClassification(Name="Name")
        ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcProject")
        ifcopenshell.api.run("classification.add_classification", self.file, classification=classification)
        assert self.file.by_type("IfcClassification")[0].Name == "Name"
