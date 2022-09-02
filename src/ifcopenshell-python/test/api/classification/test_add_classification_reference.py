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
import ifcopenshell.util.classification


class TestAddReference(test.bootstrap.IFC4):
    def test_adding_a_reference(self):
        ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcProject")
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        result = ifcopenshell.api.run("classification.add_classification", self.file, classification="Name")
        ifcopenshell.api.run(
            "classification.add_reference",
            self.file,
            product=element,
            identification="X",
            name="Foobar",
            classification=result,
        )
        references = list(ifcopenshell.util.classification.get_references(element))
        assert len(references) == 1
        assert references[0].Identification == "X"
        assert references[0].Name == "Foobar"
        assert references[0].ReferencedSource == self.file.by_type("IfcClassification")[0]

        element2 = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        ifcopenshell.api.run(
            "classification.add_reference",
            self.file,
            product=element2,
            identification="X",
            name="Foobar",
            classification=result,
        )
        assert list(ifcopenshell.util.classification.get_references(element2))[0].Identification == "X"
        assert list(ifcopenshell.util.classification.get_references(element2))[0].Name == "Foobar"
        assert list(ifcopenshell.util.classification.get_references(element2))[0] == references[0]

    def test_adding_a_library_based_reference(self):
        library = ifcopenshell.file()
        classification = library.createIfcClassification(Name="Name")
        reference = library.createIfcClassificationReference(Identification="1", ReferencedSource=classification)

        ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcProject")
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        result = ifcopenshell.api.run("classification.add_classification", self.file, classification=classification)
        ifcopenshell.api.run(
            "classification.add_reference",
            self.file,
            product=element,
            reference=reference,
            classification=result,
        )
        references = list(ifcopenshell.util.classification.get_references(element))
        assert len(references) == 1
        assert references[0].Identification == "1"
        assert references[0].ReferencedSource == self.file.by_type("IfcClassification")[0]

    def test_adding_a_reference_to_a_resource(self):
        ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcProject")
        element = self.file.createIfcMaterial()
        result = ifcopenshell.api.run("classification.add_classification", self.file, classification="Name")
        ifcopenshell.api.run(
            "classification.add_reference",
            self.file,
            product=element,
            identification="X",
            name="Foobar",
            classification=result,
        )
        references = list(ifcopenshell.util.classification.get_references(element))
        assert len(references) == 1
        assert references[0].Identification == "X"
        assert references[0].Name == "Foobar"
        assert references[0].ReferencedSource == self.file.by_type("IfcClassification")[0]

        element2 = self.file.createIfcCostValue()
        ifcopenshell.api.run(
            "classification.add_reference",
            self.file,
            product=element2,
            identification="X",
            name="Foobar",
            classification=result,
        )
        assert list(ifcopenshell.util.classification.get_references(element2))[0].Identification == "X"
        assert list(ifcopenshell.util.classification.get_references(element2))[0].Name == "Foobar"
        assert list(ifcopenshell.util.classification.get_references(element2))[0] == references[0]

        assert len(self.file.by_type("IfcExternalReferenceRelationship")[0].RelatedResourceObjects) == 2
