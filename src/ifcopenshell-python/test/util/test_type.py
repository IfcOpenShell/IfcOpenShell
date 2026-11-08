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

import ifcopenshell
import ifcopenshell.api.root
import ifcopenshell.api.type
import ifcopenshell.express.rule_executor
import ifcopenshell.util.schema
import ifcopenshell.util.type as subject
import ifcopenshell.validate
import test.bootstrap

SCHEMAS = ["IFC2X3", "IFC4", "IFC4X3_ADD2"]


def concrete_subtypes(schema_name: str, ifc_class: str) -> list[str]:
    schema = ifcopenshell.schema_by_name(schema_name)
    return [d.name() for d in ifcopenshell.util.schema.get_subtypes(schema.declaration_by_name(ifc_class))]


class TestGetApplicableTypes(test.bootstrap.IFC4):
    def test_run(self):
        assert subject.get_applicable_types("IfcWall") == ["IfcWallType"]
        assert subject.get_applicable_types("IfcWallStandardCase") == ["IfcWallType"]
        assert subject.get_applicable_types("IfcDuctSegment") == ["IfcDuctSegmentType"]
        assert subject.get_applicable_types("IfcTask") == ["IfcTaskType"]
        assert subject.get_applicable_types("IfcAnnotation") == ["IfcTypeProduct"]
        assert subject.get_applicable_types("IfcElement") == []

    def test_an_occurrence_without_a_rule_accepts_the_types_of_its_family(self):
        types = subject.get_applicable_types("IfcFlowSegment")
        assert "IfcDuctSegmentType" in types
        assert "IfcDistributionElementType" not in types
        assert "IfcWallType" not in types

    def test_passing_an_instance(self):
        wall = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        assert subject.get_applicable_types(wall) == ["IfcWallType"]


class TestGetApplicableTypesIFC2X3(test.bootstrap.IFC2X3):
    def test_run(self):
        assert subject.get_applicable_types("IfcWall", schema="IFC2X3") == ["IfcWallType"]
        assert subject.get_applicable_types("IfcWallStandardCase", schema="IFC2X3") == ["IfcWallType"]
        assert subject.get_applicable_types("IfcBuildingElementProxy", schema="IFC2X3") == [
            "IfcBuildingElementProxyType"
        ]
        assert subject.get_applicable_types("IfcDoor", schema="IFC2X3") == ["IfcDoorStyle"]
        assert subject.get_applicable_types("IfcStair", schema="IFC2X3") == ["IfcTypeProduct"]


class TestGetApplicableEntities(test.bootstrap.IFC4):
    def test_run(self):
        entities = subject.get_applicable_entities("IfcWallType")
        assert entities[0] == subject.ApplicableOccurrence("IfcWall", None)
        assert {e.ifc_class for e in entities} == {"IfcWall", "IfcWallElementedCase", "IfcWallStandardCase"}
        assert subject.get_applicable_entities("IfcTaskType") == [subject.ApplicableOccurrence("IfcTask", None)]

    def test_the_primary_occurrence_comes_first(self):
        assert subject.get_applicable_entities("IfcPumpType")[0].ifc_class == "IfcPump"
        assert subject.get_applicable_entities("IfcFurnitureType")[0].ifc_class == "IfcFurniture"

    def test_a_generic_type_product_types_products_without_a_rule_only(self):
        classes = {e.ifc_class for e in subject.get_applicable_entities("IfcTypeProduct")}
        assert {"IfcAnnotation", "IfcOpeningElement", "IfcGrid"} <= classes
        assert "IfcWall" not in classes
        assert "IfcTask" not in classes

    def test_applicable_occurrence_narrows_the_schema_answer(self):
        wall_type = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWallType")
        wall_type.ApplicableOccurrence = "IfcWall/STANDARD, IfcWallStandardCase"
        assert subject.get_applicable_entities(wall_type) == [
            subject.ApplicableOccurrence("IfcWall", "STANDARD"),
            subject.ApplicableOccurrence("IfcWallStandardCase", None),
        ]

    def test_applicable_occurrence_cannot_widen_or_contradict_the_schema(self):
        wall_type = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWallType")
        wall_type.ApplicableOccurrence = "IfcDoor"
        assert {e.ifc_class for e in subject.get_applicable_entities(wall_type)} == {
            "IfcWall",
            "IfcWallElementedCase",
            "IfcWallStandardCase",
        }
        wall_type.ApplicableOccurrence = "IfcDoor, IfcWall/PARTITIONING, NotAnEntity"
        assert subject.get_applicable_entities(wall_type) == [subject.ApplicableOccurrence("IfcWall", "PARTITIONING")]

    def test_applicable_occurrence_of_an_annotation_type(self):
        annotation_type = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcTypeProduct")
        annotation_type.ApplicableOccurrence = "IfcAnnotation/TEXT"
        assert subject.get_applicable_entities(annotation_type) == [
            subject.ApplicableOccurrence("IfcAnnotation", "TEXT")
        ]


class TestGetApplicableEntitiesIFC2X3(test.bootstrap.IFC2X3):
    def test_run(self):
        entities = subject.get_applicable_entities("IfcWallType", schema="IFC2X3")
        assert {e.ifc_class for e in entities} == {"IfcWall", "IfcWallStandardCase"}
        assert subject.get_applicable_entities("IfcBuildingElementProxyType", schema="IFC2X3") == [
            subject.ApplicableOccurrence("IfcBuildingElementProxy", None)
        ]
        assert subject.get_applicable_entities("IfcDoorStyle", schema="IFC2X3") == [
            subject.ApplicableOccurrence("IfcDoor", None)
        ]

    def test_a_generic_type_product_types_a_stair(self):
        assert "IfcStair" in {e.ifc_class for e in subject.get_applicable_entities("IfcTypeProduct", schema="IFC2X3")}


class TestIsApplicable(test.bootstrap.IFC4):
    def test_run(self):
        wall = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        door = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcDoor")
        wall_type = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWallType")
        assert subject.is_applicable(wall_type, wall) is True
        assert subject.is_applicable(wall_type, door) is False

    def test_applicable_occurrence_is_honoured(self):
        wall = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        standard_case = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWallStandardCase")
        wall_type = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWallType")
        wall_type.ApplicableOccurrence = "IfcWallStandardCase"
        assert subject.is_applicable(wall_type, standard_case) is True
        assert subject.is_applicable(wall_type, wall) is False


class TestEveryTypeClassIsCovered:
    @pytest.mark.parametrize("schema_name", SCHEMAS)
    def test_every_type_class_has_applicable_entities(self, schema_name):
        schema = ifcopenshell.schema_by_name(schema_name)
        for type_class in concrete_subtypes(schema_name, "IfcTypeObject"):
            entities = subject.get_applicable_entities(type_class, schema_name)
            assert entities, type_class
            for entity in entities:
                assert not schema.declaration_by_name(entity.ifc_class).is_abstract(), (type_class, entity)

    @pytest.mark.parametrize("schema_name", SCHEMAS)
    def test_every_occurrence_class_has_applicable_types(self, schema_name):
        for ifc_class in concrete_subtypes(schema_name, "IfcObject"):
            assert subject.get_applicable_types(ifc_class, schema_name), ifc_class

    @pytest.mark.parametrize("schema_name", SCHEMAS)
    def test_every_primary_pairing_satisfies_the_schema_rules(self, schema_name):
        file = ifcopenshell.file(schema=schema_name)
        for type_class in concrete_subtypes(schema_name, "IfcTypeObject"):
            if schema_name == "IFC4" and type_class == "IfcTransformerType":
                continue  # IFC4 misspells it as IFCTRANFORMERTYPE in IfcTransformer.CorrectTypeAssigned.
            relating_type = ifcopenshell.api.root.create_entity(file, ifc_class=type_class, name=type_class)
            occurrence_class = subject.get_applicable_entities(type_class, schema_name)[0].ifc_class
            occurrence = ifcopenshell.api.root.create_entity(file, ifc_class=occurrence_class)
            ifcopenshell.api.type.assign_type(file, related_objects=[occurrence], relating_type=relating_type)

        logger = ifcopenshell.validate.json_logger()
        ifcopenshell.express.rule_executor.run(file, logger)
        type_rules = ("IfcTypeProduct.WR41", "IfcTypeProduct.ApplicableOccurrence")
        violations = [
            s
            for s in logger.statements
            if s.get("attribute", "").endswith(".CorrectTypeAssigned") or s.get("attribute") in type_rules
        ]
        assert violations == []
