# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2026 Petru Conduraru <petru@bimvoice.com>
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

# This file was generated with the assistance of an AI coding tool.

import ifcopenshell.api.root
import ifcopenshell.api.type

import ifcpatch
import test.bootstrap


class TestFixDoubleTypedPredefinedType(test.bootstrap.IFC4):
    def test_clears_occurrence_under_concrete_type(self):
        wall_type = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWallType", name="WT1")
        wall_type.PredefinedType = "MOVABLE"
        wall = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        wall.PredefinedType = "NOTDEFINED"
        wall.ObjectType = "Some legacy value"
        ifcopenshell.api.type.assign_type(
            self.file, related_objects=[wall], relating_type=wall_type, should_map_representations=False
        )
        # assign_type would already clear these; force them back to simulate
        # a legacy file where the occurrence was typed before this cleanup
        # existed.
        wall.PredefinedType = "NOTDEFINED"
        wall.ObjectType = "Some legacy value"

        output = ifcpatch.execute({"file": self.file, "recipe": "FixDoubleTypedPredefinedType", "arguments": []})

        assert wall.PredefinedType is None
        assert wall.ObjectType is None
        assert output == self.file

    def test_leaves_occurrence_under_notdefined_type_untouched(self):
        wall_type = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWallType", name="WT1")
        wall_type.PredefinedType = "NOTDEFINED"
        wall = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        wall.PredefinedType = "MOVABLE"
        wall.ObjectType = "Legitimate own value"
        ifcopenshell.api.type.assign_type(
            self.file, related_objects=[wall], relating_type=wall_type, should_map_representations=False
        )
        wall.PredefinedType = "MOVABLE"
        wall.ObjectType = "Legitimate own value"

        ifcpatch.execute({"file": self.file, "recipe": "FixDoubleTypedPredefinedType", "arguments": []})

        assert wall.PredefinedType == "MOVABLE"
        assert wall.ObjectType == "Legitimate own value"

    def test_leaves_untyped_element_untouched(self):
        wall = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        wall.PredefinedType = "NOTDEFINED"
        wall.ObjectType = "Untyped value"

        ifcpatch.execute({"file": self.file, "recipe": "FixDoubleTypedPredefinedType", "arguments": []})

        assert wall.PredefinedType == "NOTDEFINED"
        assert wall.ObjectType == "Untyped value"

    def test_userdefined_type_with_custom_description_clears_occurrence(self):
        # Mirrors ifcopenshell.api.type.assign_type: a USERDEFINED type only
        # counts as "concrete" if it also has a custom type name to fall
        # back on (here IfcWallType.ElementType).
        wall_type = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWallType", name="WT1")
        wall_type.PredefinedType = "USERDEFINED"
        wall_type.ElementType = "MyCustomWall"
        wall = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        wall.PredefinedType = "NOTDEFINED"
        wall.ObjectType = "Some legacy value"
        ifcopenshell.api.type.assign_type(
            self.file, related_objects=[wall], relating_type=wall_type, should_map_representations=False
        )
        wall.PredefinedType = "NOTDEFINED"
        wall.ObjectType = "Some legacy value"

        ifcpatch.execute({"file": self.file, "recipe": "FixDoubleTypedPredefinedType", "arguments": []})

        assert wall.PredefinedType is None
        assert wall.ObjectType is None

    def test_userdefined_type_without_custom_description_untouched(self):
        # A USERDEFINED type with no ElementType/ObjectType of its own
        # carries no real type information, so assign_type leaves the
        # occurrence alone. This recipe mirrors that.
        wall_type = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWallType", name="WT1")
        wall_type.PredefinedType = "USERDEFINED"
        wall = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        wall.PredefinedType = "NOTDEFINED"
        wall.ObjectType = "Kept because type has no description"
        ifcopenshell.api.type.assign_type(
            self.file, related_objects=[wall], relating_type=wall_type, should_map_representations=False
        )
        wall.PredefinedType = "NOTDEFINED"
        wall.ObjectType = "Kept because type has no description"

        ifcpatch.execute({"file": self.file, "recipe": "FixDoubleTypedPredefinedType", "arguments": []})

        assert wall.PredefinedType == "NOTDEFINED"
        assert wall.ObjectType == "Kept because type has no description"

    def test_already_clean_file_is_a_no_op(self):
        wall_type = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWallType", name="WT1")
        wall_type.PredefinedType = "MOVABLE"
        wall = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        ifcopenshell.api.type.assign_type(
            self.file, related_objects=[wall], relating_type=wall_type, should_map_representations=False
        )
        assert wall.PredefinedType is None
        assert wall.ObjectType is None
        before = self.file.to_string()

        ifcpatch.execute({"file": self.file, "recipe": "FixDoubleTypedPredefinedType", "arguments": []})

        assert self.file.to_string() == before

    def test_query_restricts_which_occurrences_are_touched(self):
        wall_type = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWallType", name="WT1")
        wall_type.PredefinedType = "MOVABLE"
        wall = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        wall.PredefinedType = "NOTDEFINED"
        column_type = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcColumnType", name="CT1")
        column_type.PredefinedType = "COLUMN"
        column = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcColumn")
        column.PredefinedType = "NOTDEFINED"
        ifcopenshell.api.type.assign_type(
            self.file, related_objects=[wall], relating_type=wall_type, should_map_representations=False
        )
        ifcopenshell.api.type.assign_type(
            self.file, related_objects=[column], relating_type=column_type, should_map_representations=False
        )
        wall.PredefinedType = "NOTDEFINED"
        column.PredefinedType = "NOTDEFINED"

        ifcpatch.execute({"file": self.file, "recipe": "FixDoubleTypedPredefinedType", "arguments": ["IfcWall"]})

        assert wall.PredefinedType is None
        assert column.PredefinedType == "NOTDEFINED"


class TestFixDoubleTypedPredefinedTypeIFC2X3(test.bootstrap.IFC2X3):
    def test_ifc2x3_occurrence_without_predefined_type_attribute_is_guarded(self):
        # IFC2X3 IfcWallStandardCase has no PredefinedType attribute at all;
        # only ObjectType may be cleared there.
        wall_type = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWallType", name="WT1")
        wall_type.PredefinedType = "STANDARD"
        wall = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWallStandardCase")
        wall.ObjectType = "Some legacy value"
        assert not hasattr(wall, "PredefinedType")
        ifcopenshell.api.type.assign_type(
            self.file, related_objects=[wall], relating_type=wall_type, should_map_representations=False
        )
        wall.ObjectType = "Some legacy value"

        ifcpatch.execute({"file": self.file, "recipe": "FixDoubleTypedPredefinedType", "arguments": []})

        assert wall.ObjectType is None

    def test_ifc2x3_userdefined_type_without_elementtype_untouched(self):
        wall_type = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWallType", name="WT1")
        wall_type.PredefinedType = "USERDEFINED"
        wall = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWallStandardCase")
        wall.ObjectType = "Kept because type has no description"
        ifcopenshell.api.type.assign_type(
            self.file, related_objects=[wall], relating_type=wall_type, should_map_representations=False
        )
        wall.ObjectType = "Kept because type has no description"

        ifcpatch.execute({"file": self.file, "recipe": "FixDoubleTypedPredefinedType", "arguments": []})

        assert wall.ObjectType == "Kept because type has no description"
