# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2026 Petru Conduraru <petru@bimvoice.com>
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
#
# This file was generated with the assistance of an AI coding tool.

import datetime
import re
import tempfile
from pathlib import Path

import ifcopenshell
import ifcopenshell.api.control
import ifcopenshell.api.sequence

from ifc4d.ifc2p6 import Ifc2P6


class TestIfc2P6RelationshipType:
    """IfcSequenceEnum has 6 members: START_START, START_FINISH, FINISH_START,
    FINISH_FINISH, USERDEFINED, NOTDEFINED. Only the first 4 mapped to a P6
    relationship type text; USERDEFINED and NOTDEFINED fell through a plain
    dict lookup and raised KeyError, crashing the whole export.
    """

    @staticmethod
    def build_ifc(sequence_type: "str | None") -> ifcopenshell.file:
        ifc_file = ifcopenshell.file()
        ifc_file.create_entity("IfcProject", GlobalId=ifcopenshell.guid.new(), Name="P")
        schedule = ifcopenshell.api.sequence.add_work_schedule(ifc_file, name="Schedule A")
        calendar = ifcopenshell.api.sequence.add_work_calendar(ifc_file, name="Cal A")
        t1 = ifcopenshell.api.sequence.add_task(ifc_file, work_schedule=schedule, name="T1", identification="1")
        t2 = ifcopenshell.api.sequence.add_task(ifc_file, work_schedule=schedule, name="T2", identification="2")
        ifcopenshell.api.control.assign_control(ifc_file, relating_control=calendar, related_objects=[t1, t2])
        for task in (t1, t2):
            task_time = ifcopenshell.api.sequence.add_task_time(ifc_file, task=task)
            ifcopenshell.api.sequence.edit_task_time(
                ifc_file,
                task_time=task_time,
                attributes={"ScheduleDuration": "P1D", "ScheduleStart": "2024-01-01T08:00:00"},
            )
        rel = ifcopenshell.api.sequence.assign_sequence(ifc_file, relating_process=t1, related_process=t2)
        if sequence_type is not None:
            ifcopenshell.api.sequence.edit_sequence(
                ifc_file, rel_sequence=rel, attributes={"SequenceType": sequence_type}
            )
        return ifc_file

    @staticmethod
    def export(ifc_file: ifcopenshell.file) -> str:
        converter = Ifc2P6()
        converter.file = ifc_file
        converter.holiday_start_date = datetime.date(2024, 1, 1)
        converter.holiday_finish_date = datetime.date(2024, 1, 1)
        with tempfile.TemporaryDirectory() as tmp_dir:
            converter.xml = str(Path(tmp_dir) / "out.xml")
            converter.execute()
            return Path(converter.xml).read_text()

    def test_userdefined_sequence_type_does_not_crash_the_export(self):
        # Before the fix: KeyError: 'USERDEFINED'.
        ifc_file = self.build_ifc("USERDEFINED")
        xml = self.export(ifc_file)
        assert re.findall(r"<Relationship>.*?<Type>([^<]*)</Type>", xml) == ["Finish to Start"]

    def test_notdefined_sequence_type_does_not_crash_the_export(self):
        # Before the fix: KeyError: 'NOTDEFINED'.
        ifc_file = self.build_ifc("NOTDEFINED")
        xml = self.export(ifc_file)
        assert re.findall(r"<Relationship>.*?<Type>([^<]*)</Type>", xml) == ["Finish to Start"]

    def test_absent_sequence_type_still_defaults_to_finish_to_start(self):
        ifc_file = self.build_ifc(None)
        xml = self.export(ifc_file)
        assert re.findall(r"<Relationship>.*?<Type>([^<]*)</Type>", xml) == ["Finish to Start"]

    def test_finish_start_sequence_type_is_still_mapped_correctly(self):
        ifc_file = self.build_ifc("FINISH_START")
        xml = self.export(ifc_file)
        assert re.findall(r"<Relationship>.*?<Type>([^<]*)</Type>", xml) == ["Finish to Start"]

    def test_start_start_sequence_type_is_still_mapped_correctly(self):
        ifc_file = self.build_ifc("START_START")
        xml = self.export(ifc_file)
        assert re.findall(r"<Relationship>.*?<Type>([^<]*)</Type>", xml) == ["Start to Start"]
