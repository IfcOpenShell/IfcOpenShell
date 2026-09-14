# IfcResources - IFC resources utility
# Copyright (C) 2026 Dion Moult <dion@thinkmoult.com>
#
# This file is part of IfcResources.
#
# IfcResources is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcResources is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcResources.  If not, see <http://www.gnu.org/licenses/>.

# This file was generated with the assistance of an AI coding tool.

import datetime
import tempfile
from pathlib import Path

import ifcopenshell
import ifcopenshell.api.pset
import ifcopenshell.api.resource
import ifcopenshell.api.root
import ifcopenshell.api.unit
import ifcopenshell.util.date

from ifc4d.csv2ifc import Ifc2Csv


class TestIfc2CsvOutputColumns:
    @staticmethod
    def setup_ifc_file() -> ifcopenshell.file:
        ifc_file = ifcopenshell.file()
        ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcProject")
        ifcopenshell.api.unit.assign_unit(ifc_file)
        return ifc_file

    @staticmethod
    def add_resource_with_productivity(
        ifc_file: ifcopenshell.file, ifc_class: str, name: str, hours: float
    ) -> ifcopenshell.entity_instance:
        resource = ifcopenshell.api.resource.add_resource(ifc_file, ifc_class=ifc_class)
        resource.Name = name
        pset = ifcopenshell.api.pset.add_pset(ifc_file, product=resource, name="EPset_Productivity")
        duration = ifcopenshell.util.date.datetime2ifc(datetime.timedelta(hours=hours), "IfcDuration")
        ifcopenshell.api.pset.edit_pset(
            ifc_file,
            pset=pset,
            properties={
                "BaseQuantityConsumed": duration,
                "BaseQuantityProducedName": "m3",
                "BaseQuantityProducedValue": 1.0,
            },
        )
        return resource

    def test_equipment_output_is_not_written_to_labor_output_column(self) -> None:
        # An equipment resource's productivity must land in EQUIPMENT
        # OUTPUT, not LABOR OUTPUT, which must stay empty for it.
        ifc_file = self.setup_ifc_file()
        self.add_resource_with_productivity(ifc_file, "IfcConstructionEquipmentResource", "Excavator", 2.0)
        self.add_resource_with_productivity(ifc_file, "IfcLaborResource", "Carpenter", 1.0)

        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = Path(tmpdir) / "resources.csv"
            Ifc2Csv(str(csv_path), ifc_file).execute()
            rows = csv_path.read_text().splitlines()

        header = rows[0].split(",")
        labor_i = header.index("LABOR OUTPUT")
        equipment_i = header.index("EQUIPMENT OUTPUT")

        excavator_row = next(r for r in rows[1:] if "Excavator" in r).split(",")
        carpenter_row = next(r for r in rows[1:] if "Carpenter" in r).split(",")

        assert excavator_row[equipment_i] == "2.0"
        assert excavator_row[labor_i] == ""
        assert carpenter_row[labor_i] == "1.0"
        assert carpenter_row[equipment_i] == ""
