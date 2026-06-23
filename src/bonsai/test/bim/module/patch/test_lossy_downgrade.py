# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2026 Dion Moult <dion@thinkmoult.com>
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

import tempfile
from pathlib import Path

import bpy
import ifcopenshell
import pytest

import bonsai.tool as tool
from test.bim.bootstrap import NewFile

pytestmark = pytest.mark.patch


def _set_patch_state(*, recipe: str, target_schema: str | None, source_ifc: ifcopenshell.file | None = None) -> None:
    """Drive the BIMPatchProperties into the configuration that a user produces
    by picking Recipe + Schema in the panel + checking "Load from memory".
    Setting the recipe fires UpdateIfcPatchArguments which builds the dynamic
    args collection — only then can we assign the schema arg's enum_value."""
    props = tool.Patch.get_patch_props()
    if source_ifc is not None:
        tool.Ifc.set(source_ifc)
        props.should_load_from_memory = True
    props.ifc_patch_recipes = recipe  # update callback builds ifc_patch_args_attr
    if target_schema is not None:
        schema_arg = next(a for a in props.ifc_patch_args_attr if a.name == "Schema")
        schema_arg.enum_value = target_schema


class TestMigrationIsLossyDowngrade(NewFile):
    """Pins the predicate that gates ``ExecuteIfcPatch.invoke``'s
    confirmation popup. Every row of the truth table corresponds to a real
    user-facing flow — wrong answers either nag the user on safe migrations
    or silently let lossy ones through with no warning."""

    def test_ifc4_to_ifc2x3_in_memory_is_lossy(self):
        ifc = ifcopenshell.file(schema="IFC4")
        _set_patch_state(recipe="Migrate", target_schema="IFC2X3", source_ifc=ifc)
        assert tool.Patch.migration_is_lossy_downgrade() is True

    def test_ifc4x3_to_ifc2x3_in_memory_is_lossy(self):
        # Regression for the gate that originally only fired for self.file.schema == "IFC4",
        # silently leaving IFC4X3 sources crashing on IFC4-only geometry.
        ifc = ifcopenshell.file(schema="IFC4X3")
        _set_patch_state(recipe="Migrate", target_schema="IFC2X3", source_ifc=ifc)
        assert tool.Patch.migration_is_lossy_downgrade() is True

    def test_ifc2x3_to_ifc4_upgrade_is_not_lossy(self):
        ifc = ifcopenshell.file(schema="IFC2X3")
        _set_patch_state(recipe="Migrate", target_schema="IFC4", source_ifc=ifc)
        assert tool.Patch.migration_is_lossy_downgrade() is False

    def test_ifc4_to_ifc4_same_schema_is_not_lossy(self):
        ifc = ifcopenshell.file(schema="IFC4")
        _set_patch_state(recipe="Migrate", target_schema="IFC4", source_ifc=ifc)
        assert tool.Patch.migration_is_lossy_downgrade() is False

    def test_non_migrate_recipe_is_not_lossy(self):
        # The popup only ever applies to the Migrate recipe — other recipes
        # (ExtractElements, TessellateElements, …) handle their own warnings.
        ifc = ifcopenshell.file(schema="IFC4")
        _set_patch_state(recipe="ExtractElements", target_schema=None, source_ifc=ifc)
        assert tool.Patch.migration_is_lossy_downgrade() is False

    def test_no_source_set_is_not_lossy(self):
        # Without an input file or in-memory IFC, the predicate cannot tell
        # what the source schema is — defaults to False so the popup doesn't
        # block harmless cases where the user is still configuring the panel.
        props = tool.Patch.get_patch_props()
        props.ifc_patch_recipes = "Migrate"
        schema_arg = next(a for a in props.ifc_patch_args_attr if a.name == "Schema")
        schema_arg.enum_value = "IFC2X3"
        assert tool.Patch.migration_is_lossy_downgrade() is False


class TestPatchSourceSchemaSniff(NewFile):
    """End-to-end pin on the header-only schema parsing. The IFC4X3 misdetection
    bug originally lived in this code path — a raw startswith(\"IFC4\") loop
    matching IFC4X3_ADD2 before the IFC4X3 base check was reached."""

    def test_in_memory_ifc4x3_source_resolves_to_ifc4x3(self):
        ifc = ifcopenshell.file(schema="IFC4X3")
        tool.Ifc.set(ifc)
        props = tool.Patch.get_patch_props()
        props.should_load_from_memory = True
        assert tool.Patch._patch_source_schema() == "IFC4X3"

    def test_file_path_ifc4x3_add2_source_resolves_to_ifc4x3(self):
        # Writes a real .ifc file with IFC4X3_ADD2 in the FILE_SCHEMA header
        # and confirms the regex + get_fallback_schema normaliser correctly
        # collapse it to IFC4X3, not IFC4.
        with tempfile.TemporaryDirectory() as tmpdir:
            ifc_path = Path(tmpdir) / "sample.ifc"
            ifc_path.write_text(
                "ISO-10303-21;\n"
                "HEADER;\n"
                "FILE_DESCRIPTION((''),'2;1');\n"
                "FILE_NAME('','2026',(''),(''),'','','');\n"
                "FILE_SCHEMA(('IFC4X3_ADD2'));\n"
                "ENDSEC;\n"
                "DATA;\nENDSEC;\nEND-ISO-10303-21;\n"
            )
            props = tool.Patch.get_patch_props()
            props.should_load_from_memory = False
            props.ifc_patch_input = str(ifc_path)
            assert tool.Patch._patch_source_schema() == "IFC4X3"

    def test_missing_input_returns_empty_string(self):
        props = tool.Patch.get_patch_props()
        props.should_load_from_memory = False
        props.ifc_patch_input = ""
        assert tool.Patch._patch_source_schema() == ""
