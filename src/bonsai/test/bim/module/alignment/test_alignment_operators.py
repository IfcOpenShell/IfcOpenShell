# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2026 Michael Yoder <myoder@desertspringscivil.com>
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

"""Headless operator tests for the Saikei alignment module.

Tests non-modal alignment operators end-to-end in Blender headless mode.
Follows Bonsai's existing test patterns (NewIfc4X3 base class from bootstrap).

Operators tested:
    CSV import: import_alignment_csv (EXEC_DEFAULT with explicit filepath)
"""

import pytest

import bpy
import ifcopenshell
import ifcopenshell.api.alignment as align_api

import bonsai.tool as tool
from test.bim.bootstrap import NewIfc4X3


def _geometry_mapping_available() -> bool:
    """True when the modular geometry-mapping plugins are present.

    v0.9.0 evaluates segment endpoints through the geometry engine, which
    loads per-schema ifcopenshell_geometry_mapping_* plugins at runtime. The
    win64 v0.9.0alpha0 builds ship without them (IfcOpenShell#9301), so
    geometry-dependent tests skip locally and run in CI where builds are
    complete.
    """
    import pathlib

    package_root = pathlib.Path(ifcopenshell.__file__).parent
    return any(f.name.startswith("ifcopenshell_geometry_mapping_") for f in package_root.iterdir())


requires_geometry_engine = pytest.mark.skipif(
    not _geometry_mapping_available(),
    reason="geometry mapping plugins unavailable (IfcOpenShell#9301); covered in CI",
)

pytestmark = pytest.mark.alignment


@requires_geometry_engine
class TestImportAlignmentCsv(NewIfc4X3):
    """bim.import_alignment_csv — the single, merged CSV import path.

    CSV rows use full X,Y,R (or D,Z,L) triples: the first and last R/L values
    are placeholders per the API's create_from_csv contract.
    """

    def _write_csv(self, tmp_path, rows):
        path = tmp_path / "alignment.csv"
        path.write_text("\n".join(rows) + "\n", encoding="utf-8")
        return str(path)

    def test_import_sets_active_alignment_and_builds_hierarchy(self, tmp_path):
        filepath = self._write_csv(tmp_path, ["0,0,0,1000,0,300,2000,800,0"])
        result = bpy.ops.bim.import_alignment_csv("EXEC_DEFAULT", filepath=filepath)
        assert result == {"FINISHED"}

        alignment = tool.Alignment.get_active_alignment()
        assert alignment is not None
        assert alignment.is_a("IfcAlignment")
        assert tool.Ifc.get_object(alignment) is not None

    def test_import_with_vertical_row_creates_vertical_layout(self, tmp_path):
        filepath = self._write_csv(
            tmp_path,
            [
                "0,0,0,1000,0,300,2000,800,0",
                "0,100,0,500,110,200,1000,105,0",
            ],
        )
        result = bpy.ops.bim.import_alignment_csv("EXEC_DEFAULT", filepath=filepath)
        assert result == {"FINISHED"}

        alignment = tool.Alignment.get_active_alignment()
        assert align_api.get_vertical_layout(alignment) is not None
