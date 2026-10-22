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
import ifcopenshell.util.element
import ifcopenshell.util.selector

import ifccsv


class TestSummaryTotal:
    def test_sum_covers_every_element_not_only_the_last_of_each_group(self):
        ifc_file = ifcopenshell.file(schema="IFC4")
        walls = []
        for name, area in (("A", 100.0), ("A", 150.0), ("B", 100.0)):
            wall = ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcWall", name=name)
            pset = ifcopenshell.api.pset.add_pset(ifc_file, product=wall, name="Pset_Test")
            ifcopenshell.api.pset.edit_pset(ifc_file, pset=pset, properties={"Area": area})
            walls.append(wall)

        ifc_csv = ifccsv.IfcCsv()
        ifc_csv.export(
            ifc_file,
            walls,
            ["Name", "Pset_Test.Area"],
            groups=[{"name": "Name", "type": "GROUP"}],
            summaries=[{"name": "Pset_Test.Area", "type": "SUM"}],
        )

        assert ifc_csv.summaries[2] == "Sum: 350.0"

    def test_summary_of_a_grouped_column_is_taken_from_the_group_values(self):
        ifc_file = ifcopenshell.file(schema="IFC4")
        walls = []
        for name, area in (("A", 100.0), ("A", 150.0), ("B", 100.0)):
            wall = ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcWall", name=name)
            pset = ifcopenshell.api.pset.add_pset(ifc_file, product=wall, name="Pset_Test")
            ifcopenshell.api.pset.edit_pset(ifc_file, pset=pset, properties={"Area": area})
            walls.append(wall)

        ifc_csv = ifccsv.IfcCsv()
        ifc_csv.export(
            ifc_file,
            walls,
            ["Name", "Pset_Test.Area"],
            groups=[{"name": "Name", "type": "GROUP"}, {"name": "Pset_Test.Area", "type": "SUM"}],
            summaries=[{"name": "Pset_Test.Area", "type": "MAX"}],
        )

        assert [row[2] for row in ifc_csv.results] == [250.0, 100.0]
        assert ifc_csv.summaries[2] == "Max: 250.0"


class TestImportReadOnlyColumns:
    def test_country_is_imported_while_count_is_skipped(self, tmp_path, monkeypatch):
        ifc_file = ifcopenshell.file(schema="IFC4")
        wall = ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcWall", name="Wall")
        pset = ifcopenshell.api.pset.add_pset(ifc_file, product=wall, name="Pset_Address")
        ifcopenshell.api.pset.edit_pset(ifc_file, pset=pset, properties={"Country": "Old"})
        table = tmp_path / "edited.csv"
        table.write_text(f"GlobalId,Pset_Address.Country,Count\n{wall.GlobalId},New,99\n", encoding="utf-8")

        set_keys = []
        set_element_value = ifcopenshell.util.selector.set_element_value

        def recording_set_element_value(ifc_file, element, key, *args, **kwargs):
            set_keys.append(key)
            return set_element_value(ifc_file, element, key, *args, **kwargs)

        monkeypatch.setattr(ifcopenshell.util.selector, "set_element_value", recording_set_element_value)

        ifccsv.IfcCsv().Import(ifc_file, str(table))

        assert ifcopenshell.util.element.get_pset(wall, "Pset_Address", "Country") == "New"
        assert set_keys == ["Pset_Address.Country"]
