# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2022 Dion Moult <dion@thinkmoult.com>
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

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any

import bpy
import ifcopenshell
import ifcopenshell.util.schema
import ifcpatch

import bonsai.core.tool
import bonsai.tool

if TYPE_CHECKING:
    from bonsai.bim.module.patch.prop import BIMPatchProperties


# Lower index = older schema. Used to detect downgrades vs upgrades.
_SCHEMA_AGE = {"IFC2X3": 0, "IFC4": 1, "IFC4X3": 2}

# Pretty-printed argument name for the ``Migrate`` recipe's schema parameter
# (see UpdateIfcPatchArguments.pretty_arg_name in bim/module/patch/operator.py).
_MIGRATE_SCHEMA_ARG_NAME = "Schema"

# Match a STEP-encoded FILE_SCHEMA header: ``FILE_SCHEMA(('IFC4'));`` and the
# IFC4X3_ADD2 / IFC2X3_TC1 variants. Captures the bare schema identifier.
_IFC_FILE_SCHEMA_RE = re.compile(r"FILE_SCHEMA\s*\(\s*\(\s*'([^']+)'", re.IGNORECASE)


class Patch(bonsai.core.tool.Patch):
    @classmethod
    def get_patch_props(cls) -> BIMPatchProperties:
        return bpy.context.scene.BIMPatchProperties

    @classmethod
    def run_migrate_patch(cls, infile: str, outfile: str, schema: str) -> None:
        output = ifcpatch.execute(
            {"input": infile, "file": ifcopenshell.open(infile), "recipe": "Migrate", "arguments": [schema]}
        )
        ifcpatch.write(output, outfile)

    @classmethod
    def is_filepath_argument(cls, arg_info: ifcpatch.InputDoc) -> bool:
        # There is probably a more explicit way to do this
        return "filepath" in arg_info["name"] or arg_info["name"].endswith("_dir") or "filter_glob" in arg_info

    @classmethod
    def does_patch_has_output(cls, recipe: str) -> bool:
        return recipe not in (
            "Ifc2Sql",
            "SplitByBuildingStorey",
        )

    @classmethod
    def get_preset_subdir(cls) -> str:
        """Resolve the preset subdirectory for the currently selected recipe.

        Returns a stable string for the ``-`` placeholder so the menu and save
        operator remain usable when no real recipe has been picked yet."""
        recipe = cls.get_patch_props().ifc_patch_recipes or "-"
        return f"bonsai/ifc_patch/{recipe}"

    @classmethod
    def migration_is_lossy_downgrade(cls) -> bool:
        """``True`` when the currently configured patch is the ``Migrate``
        recipe targeting an older schema than the input file. Used to gate
        the destructive-migration confirmation dialog."""
        props = cls.get_patch_props()
        if props.ifc_patch_recipes != "Migrate":
            return False
        target_schema = next(
            (arg.get_value() for arg in props.ifc_patch_args_attr if arg.name == _MIGRATE_SCHEMA_ARG_NAME),
            None,
        )
        if not target_schema:
            return False
        source_schema = cls._patch_source_schema()
        if not source_schema:
            return False
        return _SCHEMA_AGE.get(target_schema, -1) < _SCHEMA_AGE.get(source_schema, -1)

    @classmethod
    def _patch_source_schema(cls) -> str:
        """Resolve the IFC schema of the configured input without parsing the
        full file. For loaded-from-memory the schema is in the entity_instance
        wrapper; for disk paths we read only the STEP file header (first ~2KB)
        rather than ``ifcopenshell.open`` which parses the whole file."""
        props = cls.get_patch_props()
        if props.should_load_from_memory:
            ifc_file = bonsai.tool.Ifc.get()
            return ifc_file.schema if ifc_file else ""
        if not props.ifc_patch_input:
            return ""
        try:
            with open(props.ifc_patch_input, "rb") as f:
                header = f.read(2048).decode("utf-8", errors="ignore")
        except OSError:
            return ""
        match = _IFC_FILE_SCHEMA_RE.search(header)
        if not match:
            return ""
        # Collapse IFC4X3_ADD2 / IFC2X3_TC1 / IFC4_ADD2 / IFC4X1 etc. to their
        # base via the canonical normaliser — handles longest-prefix-first
        # ordering correctly (IFC4X3 before IFC4) so we don't misclassify
        # IFC4X3 files as IFC4.
        try:
            return ifcopenshell.util.schema.get_fallback_schema(match.group(1).upper())
        except AssertionError:
            return ""

    @classmethod
    def post_process_patch_arguments(cls, recipe: str, args: list[Any]) -> list[Any]:
        if recipe == "ExtractElements":
            query = args[0]
            assert isinstance(query, str)
            if "bpy.data.texts" in query:
                text_name = query.split("bpy.data.texts")[1][2:-2]
                args[0] = bpy.data.texts[text_name].as_string()
        return args
