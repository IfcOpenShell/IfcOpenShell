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

import tempfile
from pathlib import Path

import ifcopenshell

from ifc4d.msp2ifc import MSP2Ifc

# A milestone task exported by MS Project has Duration=PT0H0M0S and
# Start == Finish. Zero is the correct, meaningful duration for a milestone
# and must not silently turn into a full day in the IFC file.
MSPDI_XML = """<?xml version="1.0" encoding="UTF-8"?>
<Project xmlns="http://schemas.microsoft.com/project">
  <Name>Milestone Test Project</Name>
  <MinutesPerDay>480</MinutesPerDay>
  <Tasks>
    <Task>
      <UID>1</UID>
      <Name>Design sign-off milestone</Name>
      <OutlineLevel>0</OutlineLevel>
      <OutlineNumber>1</OutlineNumber>
      <WBS>1</WBS>
      <Duration>PT0H0M0S</Duration>
      <Priority>500</Priority>
      <CalendarUID>-1</CalendarUID>
      <Start>2024-01-05T08:00:00</Start>
      <Finish>2024-01-05T08:00:00</Finish>
    </Task>
    <Task>
      <UID>2</UID>
      <Name>Two day task</Name>
      <OutlineLevel>0</OutlineLevel>
      <OutlineNumber>2</OutlineNumber>
      <WBS>2</WBS>
      <Duration>PT16H0M0S</Duration>
      <Priority>500</Priority>
      <CalendarUID>-1</CalendarUID>
      <Start>2024-01-08T08:00:00</Start>
      <Finish>2024-01-09T16:00:00</Finish>
    </Task>
  </Tasks>
  <Calendars/>
</Project>
"""


def convert() -> ifcopenshell.file:
    with tempfile.TemporaryDirectory() as tmp_dir:
        xml_path = Path(tmp_dir) / "project.xml"
        xml_path.write_text(MSPDI_XML)
        converter = MSP2Ifc()
        converter.xml = str(xml_path)
        converter.execute()
        return converter.file


class TestMsp2IfcZeroDuration:
    def test_milestone_zero_duration_is_p0d_not_p1d(self):
        ifc_file = convert()
        task = next(t for t in ifc_file.by_type("IfcTask") if t.Identification == "1")
        assert task.IsMilestone is True
        assert task.TaskTime.ScheduleDuration == "P0D"
        assert task.TaskTime.ScheduleFinish == task.TaskTime.ScheduleStart

    def test_nonzero_duration_is_unaffected(self):
        # 16 hours / 8 hours-per-day (480 minutes-per-day) = 2 days.
        ifc_file = convert()
        task = next(t for t in ifc_file.by_type("IfcTask") if t.Identification == "2")
        assert task.TaskTime.ScheduleDuration == "P2D"
