# This file was generated with the assistance of an AI coding tool.

import ifcopenshell.api.attribute
import ifcopenshell.api.root
import ifcopenshell.guid
import test.bootstrap


class TestEditAttributes(test.bootstrap.IFC4X3):
    def create_typed_annotation(self, type_class, predefined_type=None):
        annotation = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcAnnotation")
        relating_type = ifcopenshell.api.root.create_entity(
            self.file, ifc_class=type_class, predefined_type=predefined_type
        )
        self.file.create_entity(
            "IfcRelDefinesByType",
            GlobalId=ifcopenshell.guid.new(),
            RelatedObjects=[annotation],
            RelatingType=relating_type,
        )
        return annotation

    def test_editing_an_annotation_typed_by_a_type_without_a_predefined_type(self):
        annotation = self.create_typed_annotation("IfcFurnishingElementType")
        ifcopenshell.api.attribute.edit_attributes(self.file, product=annotation, attributes={"Name": "Label"})
        assert annotation.Name == "Label"

    def test_a_relating_type_with_a_predefined_type_clears_the_occurrence_type(self):
        annotation = self.create_typed_annotation("IfcAirTerminalType", "DIFFUSER")
        annotation.ObjectType = "Custom"
        ifcopenshell.api.attribute.edit_attributes(self.file, product=annotation, attributes={"Name": "Label"})
        assert annotation.ObjectType is None
