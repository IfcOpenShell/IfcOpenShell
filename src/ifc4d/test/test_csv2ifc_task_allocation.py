# This file was generated with the assistance of an AI coding tool.

import csv

import ifcopenshell
import ifcopenshell.api.root
import ifcopenshell.api.sequence

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
    "TASK GUID",
]


class TestCsv2IfcTaskAllocation:
    def write_csv(self, path, task_guid: str) -> str:
        filepath = str(path / "resources.csv")
        with open(filepath, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(HEADERS)
            writer.writerow(["1", "LABOR", "Crew A", "", "", "", "", "", "", task_guid])
        return filepath

    def create_file_with_task(self) -> tuple[ifcopenshell.file, ifcopenshell.entity_instance]:
        file = ifcopenshell.file(schema="IFC4")
        ifcopenshell.api.root.create_entity(file, ifc_class="IfcProject")
        work_schedule = ifcopenshell.api.sequence.add_work_schedule(file, name="Schedule")
        task = ifcopenshell.api.sequence.add_task(file, work_schedule=work_schedule, name="Pour")
        return file, task

    def test_row_with_a_task_guid_allocates_the_resource(self, tmp_path):
        file, task = self.create_file_with_task()
        Csv2Ifc(self.write_csv(tmp_path, task.GlobalId), file).execute()
        resource = file.by_type("IfcLaborResource")[0]
        assert task.OperatesOn[0].RelatedObjects == (resource,)

    def test_row_with_an_unknown_task_guid_is_skipped(self, tmp_path):
        file, task = self.create_file_with_task()
        Csv2Ifc(self.write_csv(tmp_path, "3vB2YO$MX4xv5uCqZZG05x"), file).execute()
        assert len(file.by_type("IfcLaborResource")) == 1
        assert not file.by_type("IfcRelAssignsToProcess")
