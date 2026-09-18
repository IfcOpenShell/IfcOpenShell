# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2026
#
# This file is part of Bonsai.
#
# Bonsai is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Bonsai is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Bonsai.  If not, see <http://www.gnu.org/licenses/>.
#
# This file was generated with the assistance of an AI coding tool.

"""Regression coverage for BIM_OT_change_classification_level.

The operator browses a level of a loaded classification library file via
the ``HasReferences`` inverse. Two failure modes were reachable from the
"Active Classification Library" pencil icon in classification/ui.py
(draw_add_file_ui, "if not self.sprops.available_library_references"):

1. A classification with zero child references (a valid, empty IFC4
   library entry) hit ``assert reference`` with a bare AssertionError,
   because the loop variable was left ``None``.
2. ``HasReferences`` is only defined on IfcClassification /
   IfcClassificationReference from IFC4 onwards. A user-supplied IFC2X3
   classification library has no such inverse at all, so the attribute
   access itself raised AttributeError before the assert was ever reached.
"""

import bpy
import ifcopenshell
import pytest

import bonsai.tool as tool
from bonsai.bim.ifc import IfcStore
from test.bim.bootstrap import NewFile

pytestmark = pytest.mark.classification


class TestChangeClassificationLevel(NewFile):
    def test_empty_has_references_does_not_assert(self):
        """An IFC4 classification with zero child references must not crash
        the operator with a bare AssertionError."""
        bpy.ops.bim.create_project()

        lib = ifcopenshell.file(schema="IFC4")
        classification = lib.create_entity("IfcClassification", Source="Test", Edition="1", Name="EmptyLib")
        assert classification.HasReferences == ()

        IfcStore.classification_file = lib
        props = tool.Classification.get_classification_props()
        props.classification_source = "FILE"

        result = bpy.ops.bim.change_classification_level(parent_id=classification.id())
        assert result == {"FINISHED"}
        assert list(props.available_library_references) == []
        assert props.active_library_referenced_source == 0

    def test_ifc2x3_library_reports_error_instead_of_crashing(self):
        """HasReferences does not exist in IFC2X3. Loading an IFC2X3
        classification library must report a clear error, not raise an
        unhandled AttributeError."""
        bpy.ops.bim.create_project()

        lib = ifcopenshell.file(schema="IFC2X3")
        classification = lib.create_entity("IfcClassification", Source="Test", Edition="1", Name="Lib2x3")
        with pytest.raises(AttributeError):
            classification.HasReferences

        IfcStore.classification_file = lib
        props = tool.Classification.get_classification_props()
        props.classification_source = "FILE"

        with pytest.raises(RuntimeError, match="does not support browsing nested classification references"):
            bpy.ops.bim.change_classification_level(parent_id=classification.id())
