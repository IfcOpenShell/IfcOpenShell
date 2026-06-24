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


class TestExecuteIfcPatchDowngradeEndToEnd(NewFile):
    """Drives the full panel flow the user sees: load IFC4 in memory, pick
    Migrate + IFC2X3, click Execute, get an IFC2X3 file on disk with the
    expected IfcBuildingElementProxy fallback + ObjectType encoding.

    A regression here means a real user clicking Execute either crashes
    Blender, produces a broken file, or silently drops type information
    that the recipe is supposed to preserve via ObjectType."""

    def test_ifc4_with_ifclamp_downgrades_to_ifc2x3_with_proxy_and_object_type(self):
        ifc = ifcopenshell.file(schema="IFC4")
        ifc.create_entity("IfcLamp", GlobalId="2K6Z3DR8X37AS9XFvX8GcW", PredefinedType="COMPACTFLUORESCENT")
        tool.Ifc.set(ifc)

        props = tool.Patch.get_patch_props()
        props.should_load_from_memory = True
        props.ifc_patch_recipes = "Migrate"
        next(a for a in props.ifc_patch_args_attr if a.name == "Schema").enum_value = "IFC2X3"

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "downgraded.ifc"
            props.ifc_patch_output = str(output_path)

            result = bpy.ops.bim.execute_ifc_patch()

            assert result == {"FINISHED"}
            assert output_path.exists(), "Recipe ran but no output file was written"

            written = ifcopenshell.open(str(output_path))
            assert written.schema == "IFC2X3"
            proxies = written.by_type("IfcBuildingElementProxy")
            assert len(proxies) == 1, "IfcLamp should fall back to a single IfcBuildingElementProxy"
            assert proxies[0].ObjectType == "IfcLamp/COMPACTFLUORESCENT", (
                "Original class + PredefinedType must be encoded into ObjectType "
                "so the downgrade isn't a total information loss"
            )
            assert proxies[0].GlobalId == "2K6Z3DR8X37AS9XFvX8GcW"
