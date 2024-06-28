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
import ifcopenshell.api.root
import ifcopenshell.api.classification


class TestRemoveClassification(test.bootstrap.IFC4):
    def test_removing_a_classification(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        element = ifcopenshell.api.classification.add_classification(self.file, classification="Name")
        ifcopenshell.api.classification.remove_classification(self.file, classification=element)
        assert not self.file.by_type("IfcClassification")

    def test_removing_a_classification_and_all_of_its_references(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        result = ifcopenshell.api.classification.add_classification(self.file, classification="Name")
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        ifcopenshell.api.classification.add_reference(
            self.file,
            products=[element],
            identification="X",
            name="Foobar",
            classification=result,
        )
        ifcopenshell.api.classification.remove_classification(self.file, classification=result)
        assert not self.file.by_type("IfcClassification")
        assert not self.file.by_type("IfcClassificationReference")
        assert not self.file.by_type("IfcRelAssociatesClassification")

    def test_removing_a_classification_and_all_of_its_references_when_associated_with_a_resource(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        result = ifcopenshell.api.classification.add_classification(self.file, classification="Name")
        element = self.file.create_entity("IfcWall", Name="Wall")
        ifcopenshell.api.classification.add_reference(
            self.file,
            products=[element],
            identification="X",
            name="Foobar",
            classification=result,
        )
        ifcopenshell.api.classification.remove_classification(self.file, classification=result)
        assert not self.file.by_type("IfcClassification")
        assert not self.file.by_type("IfcClassificationReference")
        if self.file.schema != "IFC2X3":
            assert not self.file.by_type("IfcExternalReferenceRelationship")


class TestRemoveClassificationIFC2X3(test.bootstrap.IFC2X3, TestRemoveClassification):
    pass
