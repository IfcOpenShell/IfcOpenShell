# This file was generated with the assistance of an AI coding tool.

import ifcopenshell.api.attribute
import ifcopenshell.api.root
import ifcopenshell.api.type
import ifcopenshell.util.element
import test.bootstrap


class TestEditAttributes(test.bootstrap.IFC4):
    def test_editing_a_type_to_a_concrete_predefined_type_clears_its_occurrences(self):
        wall_type = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWallType")
        wall = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        ifcopenshell.api.type.assign_type(self.file, related_objects=[wall], relating_type=wall_type)
        wall.PredefinedType = "NOTDEFINED"
        ifcopenshell.api.attribute.edit_attributes(self.file, wall_type, {"PredefinedType": "MOVABLE"})
        assert wall.PredefinedType is None
        assert ifcopenshell.util.element.get_predefined_type(wall) == "MOVABLE"

    def test_editing_a_type_to_notdefined_keeps_its_occurrences(self):
        wall_type = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWallType")
        wall = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        ifcopenshell.api.type.assign_type(self.file, related_objects=[wall], relating_type=wall_type)
        wall.PredefinedType = "MOVABLE"
        ifcopenshell.api.attribute.edit_attributes(self.file, wall_type, {"PredefinedType": "NOTDEFINED"})
        assert wall.PredefinedType == "MOVABLE"
