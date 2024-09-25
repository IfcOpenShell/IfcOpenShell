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

import ifcpatch
import ifcopenshell
import ifcopenshell.api.context
import ifcopenshell.api.geometry
import ifcopenshell.api.georeference
import ifcopenshell.geom
import ifcopenshell.util.geolocation
import ifcopenshell.util.placement
import ifcopenshell.util.representation
import ifcopenshell.util.shape
import ifcopenshell.util.shape_builder
import test.bootstrap
from pathlib import Path


class TestIfc2Sql:
    def test_run(self):
        TEST_FILE = Path(__file__).parent / "files" / "basic.ifc"
        sqlite_path = ifcpatch.execute(
            {"file": ifcopenshell.open(TEST_FILE), "recipe": "Ifc2Sql", "arguments": ["sqlite"]}
        )
        assert isinstance(sqlite_path, str)
        assert sqlite_path.endswith(".ifcsqlite")

        # Ensure file is valid.
        ifc_sqlite = ifcopenshell.open(sqlite_path)
        assert isinstance(ifc_sqlite, ifcopenshell.sqlite)
        assert ifc_sqlite.by_id(1)
