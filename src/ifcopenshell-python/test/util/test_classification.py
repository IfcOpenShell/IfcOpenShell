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
import ifcopenshell.api.type
import ifcopenshell.api.classification
import ifcopenshell.util.classification as subject


class TestGetReferences(test.bootstrap.IFC4):
    def test_get_references_of_an_element(self):
        library = ifcopenshell.file()
        classification = library.createIfcClassification(Name="Name")
        reference1 = library.createIfcClassificationReference(Identification="1", ReferencedSource=classification)
        reference2 = library.createIfcClassificationReference(Identification="2", ReferencedSource=classification)
        project = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        ifcopenshell.api.classification.add_classification(self.file, classification=classification)
        ifcopenshell.api.classification.add_reference(
            self.file,
            products=[element],
            reference=reference1,
            classification=classification,
        )
        ifcopenshell.api.classification.add_reference(
            self.file,
            products=[element],
            reference=reference2,
            classification=classification,
        )
        assert subject.get_references(element) == set(self.file.by_type("IfcClassificationReference"))

    def test_get_references_of_a_non_rooted_element(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        element = self.file.createIfcMaterial()
        result = ifcopenshell.api.classification.add_classification(self.file, classification="Name")
        ifcopenshell.api.classification.add_reference(
            self.file,
            products=[element],
            identification="X",
            name="Foobar",
            classification=result,
        )
        assert subject.get_references(element) == set(self.file.by_type("IfcClassificationReference"))

    def test_get_inherited_classifications(self):
        library = ifcopenshell.file()
        classification = library.createIfcClassification(Name="Name")
        reference1 = library.createIfcClassificationReference(Identification="1", ReferencedSource=classification)
        reference2 = library.createIfcClassificationReference(Identification="2", ReferencedSource=classification)
        project = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        element_type = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWallType")
        ifcopenshell.api.type.assign_type(self.file, related_objects=[element], relating_type=element_type)
        ifcopenshell.api.classification.add_classification(self.file, classification=classification)
        ifcopenshell.api.classification.add_reference(
            self.file,
            products=[element],
            reference=reference1,
            classification=classification,
        )
        ifcopenshell.api.classification.add_reference(
            self.file,
            products=[element_type],
            reference=reference2,
            classification=classification,
        )
        reference1 = next(r for r in self.file.by_type("IfcClassificationReference") if r.Identification == "1")
        reference2 = next(r for r in self.file.by_type("IfcClassificationReference") if r.Identification == "2")
        assert subject.get_references(element_type) == set([reference2])
        assert subject.get_references(element) == set([reference1])

    def test_getting_direct_classifications(self):
        library = ifcopenshell.file()
        classification = library.createIfcClassification(Name="Name")
        reference1 = library.createIfcClassificationReference(Identification="1", ReferencedSource=classification)
        reference2 = library.createIfcClassificationReference(Identification="2", ReferencedSource=classification)
        project = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        element_type = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWallType")
        ifcopenshell.api.type.assign_type(self.file, related_objects=[element], relating_type=element_type)
        ifcopenshell.api.classification.add_classification(self.file, classification=classification)
        ifcopenshell.api.classification.add_reference(
            self.file,
            products=[element],
            reference=reference1,
            classification=classification,
        )
        ifcopenshell.api.classification.add_reference(
            self.file,
            products=[element_type],
            reference=reference2,
            classification=classification,
        )
        results = list(subject.get_references(element, should_inherit=False))
        assert len(results) == 1
        assert results[0].Identification == "1"


class TestGetClassification(test.bootstrap.IFC4):
    def test_get_lightweight_classification(self):
        classification = self.file.createIfcClassification(Name="Name")
        reference = self.file.createIfcClassificationReference(ReferencedSource=classification)
        assert subject.get_classification(reference) == classification

    def test_get_full_classification(self):
        classification = self.file.createIfcClassification(Name="Name")
        reference1 = self.file.createIfcClassificationReference(ReferencedSource=classification)
        reference2 = self.file.createIfcClassificationReference(ReferencedSource=reference1)
        assert subject.get_classification(reference2) == classification


class TestGetInheritedReferences(test.bootstrap.IFC4):
    def test_single_reference(self):
        classification = self.file.createIfcClassification(Name="Name")
        reference = self.file.createIfcClassificationReference(ReferencedSource=classification)
        assert subject.get_inherited_references(reference) == [reference]

    def test_multiple_references(self):
        classification = self.file.createIfcClassification(Name="Name")
        reference1 = self.file.createIfcClassificationReference(ReferencedSource=classification)
        reference2 = self.file.createIfcClassificationReference(ReferencedSource=reference1)
        assert subject.get_inherited_references(reference2) == [reference2, reference1]
