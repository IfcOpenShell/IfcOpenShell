# IfcCSV - A utility to interact with IFC data through CSV.
# Copyright (C) 2026 Dion Moult <dion@thinkmoult.com>
#
# This file is part of IfcCSV.
#
# IfcCSV is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcCSV is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcCSV.  If not, see <http://www.gnu.org/licenses/>.

# This file was generated with the assistance of an AI coding tool.

import ifcopenshell
import ifcopenshell.api.pset
import ifcopenshell.api.root

import ifccsv


class TestExportWildcards:
    def setup_method(self):
        self.file = ifcopenshell.file(schema="IFC4")
        self.wall = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall", name="Wall")
        self.wall.Tag = "T1"
        pset = ifcopenshell.api.pset.add_pset(self.file, product=self.wall, name="Pset_WallCommon")
        ifcopenshell.api.pset.edit_pset(self.file, pset=pset, properties={"LoadBearing": False, "IsExternal": True})

    def export(self, attributes):
        ifc_csv = ifccsv.IfcCsv()
        ifc_csv.export(self.file, [self.wall], attributes)
        return ifc_csv.headers, dict(zip(ifc_csv.headers, ifc_csv.results[0]))

    def test_wildcards_expand_to_the_real_columns(self):
        headers, row = self.export(["Name", "*", "Pset_WallCommon.*"])

        assert "*" not in headers
        assert len(headers) == len(set(headers))
        assert row["Name"] == "Wall"
        assert row["Tag"] == "T1"
        assert headers[-2:] == ["Pset_WallCommon.IsExternal", "Pset_WallCommon.LoadBearing"]
        assert row["Pset_WallCommon.IsExternal"] == "YES"
        assert row["Pset_WallCommon.LoadBearing"] == "NO"

    def test_a_regex_query_is_not_treated_as_a_wildcard(self):
        headers, row = self.export(["/Pset_.*/.LoadBearing"])

        assert headers == ["GlobalId", "/Pset_.*/.LoadBearing"]
        assert row["/Pset_.*/.LoadBearing"] == "NO"
