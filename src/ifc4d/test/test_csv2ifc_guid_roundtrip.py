# This file was generated with the assistance of an AI coding tool.

import csv

import ifcopenshell
import ifcopenshell.api.resource
import ifcopenshell.api.root
import ifcopenshell.guid
import pytest

from ifc4d.csv2ifc import Csv2Ifc

HEADERS = [
    "HIERARCHY",
    "TYPE",
    "ACTIVITY/RESOURCE NAME",
    "DESCRIPTION",
    "COST",
    "USAGE",
    "QUANTITY NAME",
    "LABOR OUTPUT",
    "EQUIPMENT OUTPUT",
    "GUID",
]


class TestCsv2IfcReimport:
    def write_csv(self, path, guid: str) -> str:
        filepath = str(path / "resources.csv")
        with open(filepath, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(HEADERS)
            writer.writerow(["1", "LABOR", "Crew A", "", "50", "", "", "", "", guid])
        return filepath

    def create_file_with_resource(self) -> tuple[ifcopenshell.file, ifcopenshell.entity_instance]:
        file = ifcopenshell.file(schema="IFC4")
        ifcopenshell.api.root.create_entity(file, ifc_class="IfcProject")
        resource = ifcopenshell.api.resource.add_resource(file, ifc_class="IfcLaborResource")
        resource.Name = "Crew A"
        return file, resource

    def test_row_with_a_known_guid_updates_the_resource(self, tmp_path):
        file, resource = self.create_file_with_resource()
        Csv2Ifc(self.write_csv(tmp_path, resource.GlobalId), file).execute()
        assert len(file.by_type("IfcLaborResource")) == 1
        assert resource.BaseCosts[0].AppliedValue.wrappedValue == pytest.approx(50.0)

    def test_row_with_an_unknown_guid_creates_a_resource(self, tmp_path):
        file, resource = self.create_file_with_resource()
        Csv2Ifc(self.write_csv(tmp_path, ifcopenshell.guid.new()), file).execute()
        assert len(file.by_type("IfcLaborResource")) == 2
