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

import pytest
import test.bootstrap
import ifcopenshell.api.root
import ifcopenshell.api.classification
import ifcopenshell.util.classification


class TestAddReference(test.bootstrap.IFC4):
    def test_adding_a_reference(self):
        is_ifc2x3 = self.file.schema == "IFC2X3"

        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        element2 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        result = ifcopenshell.api.classification.add_classification(self.file, classification="Name")
        ifcopenshell.api.classification.add_reference(
            self.file,
            products=[element, element2],
            identification="X",
            name="Foobar",
            classification=result,
        )
        references = list(ifcopenshell.util.classification.get_references(element))
        assert len(references) == 1
        assert getattr(references[0], "ItemReference" if is_ifc2x3 else "Identification") == "X"
        assert references[0].Name == "Foobar"
        assert references[0].ReferencedSource == self.file.by_type("IfcClassification")[0]

        references2 = list(ifcopenshell.util.classification.get_references(element))
        assert len(references2) == 1
        assert getattr(references2[0], "ItemReference" if is_ifc2x3 else "Identification") == "X"
        assert references2[0].Name == "Foobar"
        assert references2[0] == references[0]

        rel = next(
            rel
            for rel in self.file.by_type("IfcRelAssociatesClassification")
            if rel.RelatingClassification == references[0]
        )
        assert len(rel.RelatedObjects) == 2

    def test_adding_a_library_based_reference(self):
        is_ifc2x3 = self.file.schema == "IFC2X3"

        library = ifcopenshell.file()
        classification = library.createIfcClassification(Name="Name")
        reference = library.createIfcClassificationReference(Identification="1", ReferencedSource=classification)

        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        element2 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        result = ifcopenshell.api.classification.add_classification(self.file, classification=classification)
        ifcopenshell.api.classification.add_reference(
            self.file,
            products=[element, element2],
            reference=reference,
            classification=result,
        )
        references = list(ifcopenshell.util.classification.get_references(element))
        assert len(references) == 1
        assert getattr(references[0], "ItemReference" if is_ifc2x3 else "Identification") == "1"
        assert references[0].ReferencedSource == self.file.by_type("IfcClassification")[0]

        references2 = list(ifcopenshell.util.classification.get_references(element2))
        assert len(references2) == 1
        assert getattr(references2[0], "ItemReference" if is_ifc2x3 else "Identification") == "1"
        assert references2[0].ReferencedSource == self.file.by_type("IfcClassification")[0]
        assert references[0] == references2[0]

        rel = next(
            rel
            for rel in self.file.by_type("IfcRelAssociatesClassification")
            if rel.RelatingClassification == references[0]
        )
        assert len(rel.RelatedObjects) == 2

    def test_adding_a_reference_to_a_resource_and_to_a_root(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        element = self.file.createIfcMaterial()
        element2 = self.file.createIfcCostValue()
        element3 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        result = ifcopenshell.api.classification.add_classification(self.file, classification="Name")

        if self.file.schema == "IFC2X3":
            with pytest.raises(TypeError):
                ifcopenshell.api.classification.add_reference(
                    self.file,
                    products=[element, element2, element3],
                    identification="X",
                    name="Foobar",
                    classification=result,
                )
            return
        else:
            ifcopenshell.api.classification.add_reference(
                self.file,
                products=[element, element2, element3],
                identification="X",
                name="Foobar",
                classification=result,
            )

        references = list(ifcopenshell.util.classification.get_references(element))
        assert len(references) == 1
        assert references[0].Identification == "X"
        assert references[0].Name == "Foobar"
        assert references[0].ReferencedSource == self.file.by_type("IfcClassification")[0]

        references2 = list(ifcopenshell.util.classification.get_references(element2))
        assert references2[0].Identification == "X"
        assert references2[0].Name == "Foobar"
        assert references2[0] == references[0]

        references3 = list(ifcopenshell.util.classification.get_references(element3))
        assert references3[0].Identification == "X"
        assert references3[0].Name == "Foobar"
        assert references3[0] == references[0]

        assert len(self.file.by_type("IfcExternalReferenceRelationship")[0].RelatedResourceObjects) == 2
        rel = next(
            rel
            for rel in self.file.by_type("IfcRelAssociatesClassification")
            if rel.RelatingClassification == references[0]
        )
        assert len(rel.RelatedObjects) == 1


class TestAddReferenceIFC2X3(test.bootstrap.IFC2X3, TestAddReference):
    pass
