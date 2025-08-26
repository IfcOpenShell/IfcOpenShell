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

import tempfile
import csv
import pytest
import ifcopenshell
import ifcopenshell.api.root
import ifcopenshell.api.unit
import ifcopenshell.util.cost
import ifcopenshell.util.element
import ifc5d.csv2ifc
import ifc5d.ifc5Dspreadsheet
from pathlib import Path


class TestCsv2Ifc:
    @staticmethod
    def setup_ifc_file() -> ifcopenshell.file:
        ifc_file = ifcopenshell.file()
        ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcProject")
        unit = ifcopenshell.api.unit.add_si_unit(ifc_file, unit_type="LENGTHUNIT", prefix="MILLI")
        ifcopenshell.api.unit.assign_unit(ifc_file, units=[unit])
        return ifc_file

    @staticmethod
    def get_items_rows_from_csv(csv_filepath: Path) -> list[list[str]]:
        with csv_filepath.open("r", encoding="utf-8") as csv_file:
            reader = csv.reader(csv_file)
            rows = list(reader)
        rows = rows[1:]  # Skip header.
        rows = filter(lambda l: l[0], rows)  # Skip empty rows.
        rows = list(rows)
        return rows

    @staticmethod
    def validate_ifc_file_against_csv(ifc_file: ifcopenshell.file, csv_filepath: Path) -> None:
        assert len(cost_schedules := ifc_file.by_type("IfcCostSchedule")) == 1
        all_cost_items = ifc_file.by_type("IfcCostItem")

        # Ensure everything was imported.
        rows = TestCsv2Ifc.get_items_rows_from_csv(csv_filepath)
        assert len(rows) == len(all_cost_items)

        # A rought test that some hierarchy was established.
        root_items = ifcopenshell.util.cost.get_root_cost_items(cost_schedules[0])
        assert len(all_cost_items) > len(root_items)
        all_nested_items = [i for item in root_items for i in ifcopenshell.util.cost.get_all_nested_cost_items(item)]
        assert len(all_nested_items + root_items) == len(all_cost_items)

    @pytest.mark.parametrize("csv_filepath", Path(__file__).parent.parent.glob("*.csv"))
    def test_import_sample_files(self, csv_filepath: Path):
        ifc_file = self.setup_ifc_file()
        ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcProject")
        unit = ifcopenshell.api.unit.add_si_unit(ifc_file, unit_type="LENGTHUNIT", prefix="MILLI")
        ifcopenshell.api.unit.assign_unit(ifc_file, units=[unit])

        csv2ifc = ifc5d.csv2ifc.Csv2Ifc(str(csv_filepath), ifc_file)
        csv2ifc.execute()

        self.validate_ifc_file_against_csv(ifc_file, csv_filepath)

    def test_export_import_test(self):
        ifc_file = self.setup_ifc_file()

        csv_filepath = Path(__file__).parent.parent / "sample_cost_schedule_house_FR.csv"
        csv2ifc = ifc5d.csv2ifc.Csv2Ifc(str(csv_filepath), ifc_file)
        csv2ifc.execute()

        self.validate_ifc_file_against_csv(ifc_file, csv_filepath)
        n_rows = len(self.get_items_rows_from_csv(csv_filepath))

        # Export it and import it to different IFC file..
        with tempfile.TemporaryDirectory("w") as temp_csv_dir:
            writer = ifc5d.ifc5Dspreadsheet.Ifc5DCsvWriter(ifc_file, temp_csv_dir)
            writer.write()

            new_csv_filepath = next(Path(temp_csv_dir).glob("*.csv"))
            n_rows_ = len(self.get_items_rows_from_csv(new_csv_filepath))
            assert n_rows == n_rows_

            new_ifc_file = self.setup_ifc_file()
            csv2ifc = ifc5d.csv2ifc.Csv2Ifc(str(new_csv_filepath), new_ifc_file)
            csv2ifc.execute()

            self.validate_ifc_file_against_csv(new_ifc_file, new_csv_filepath)

    def test_export_xlsx_ods(self):
        ifc_file = self.setup_ifc_file()

        csv_filepath = Path(__file__).parent.parent / "sample_cost_schedule_house_FR.csv"
        csv2ifc = ifc5d.csv2ifc.Csv2Ifc(str(csv_filepath), ifc_file)
        csv2ifc.execute()

        self.validate_ifc_file_against_csv(ifc_file, csv_filepath)

        # Just to make sure it works.
        with tempfile.TemporaryDirectory("w") as temp_csv_dir:
            writer = ifc5d.ifc5Dspreadsheet.Ifc5DOdsWriter(ifc_file, temp_csv_dir)
            writer.write()
            writer = ifc5d.ifc5Dspreadsheet.Ifc5DXlsxWriter(ifc_file, temp_csv_dir)
            writer.write()
            assert len(list(Path(temp_csv_dir).glob("*.ods"))) == 1
            assert len(list(Path(temp_csv_dir).glob("*.xlsx"))) == 1
