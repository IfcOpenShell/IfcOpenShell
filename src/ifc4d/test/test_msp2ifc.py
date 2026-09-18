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

# Minimal MSPDI export with 4 tasks in a chain:
#   Task 1 -> Task 2: no lag (LinkLag 0)
#   Task 2 -> Task 3: 3 working days lag (LinkLag 14400, LagFormat 7 "Days")
#   Task 3 -> Task 4: 2 elapsed days lag (LinkLag 28800, LagFormat 8 "Elapsed Days")
#
# LinkLag/LagFormat values and their tenths-of-a-minute encoding were verified
# against a real MS Project XML export attached to
# https://github.com/IfcOpenShell/IfcOpenShell/issues/4185, where these lags
# were silently dropped on import.
MSPDI_XML = """<?xml version="1.0" encoding="UTF-8"?>
<Project xmlns="http://schemas.microsoft.com/project">
  <Name>Lag Test Project</Name>
  <MinutesPerDay>480</MinutesPerDay>
  <Tasks>
    <Task>
      <UID>1</UID>
      <Name>Task 1</Name>
      <OutlineLevel>0</OutlineLevel>
      <OutlineNumber>1</OutlineNumber>
      <WBS>1</WBS>
      <Duration>PT8H0M0S</Duration>
      <Priority>500</Priority>
      <CalendarUID>-1</CalendarUID>
      <Start>2024-01-01T08:00:00</Start>
      <Finish>2024-01-01T16:00:00</Finish>
    </Task>
    <Task>
      <UID>2</UID>
      <Name>Task 2</Name>
      <OutlineLevel>0</OutlineLevel>
      <OutlineNumber>2</OutlineNumber>
      <WBS>2</WBS>
      <Duration>PT8H0M0S</Duration>
      <Priority>500</Priority>
      <CalendarUID>-1</CalendarUID>
      <Start>2024-01-02T08:00:00</Start>
      <Finish>2024-01-02T16:00:00</Finish>
      <PredecessorLink>
        <PredecessorUID>1</PredecessorUID>
        <Type>1</Type>
        <CrossProject>0</CrossProject>
        <LinkLag>0</LinkLag>
        <LagFormat>7</LagFormat>
      </PredecessorLink>
    </Task>
    <Task>
      <UID>3</UID>
      <Name>Task 3</Name>
      <OutlineLevel>0</OutlineLevel>
      <OutlineNumber>3</OutlineNumber>
      <WBS>3</WBS>
      <Duration>PT8H0M0S</Duration>
      <Priority>500</Priority>
      <CalendarUID>-1</CalendarUID>
      <Start>2024-01-08T08:00:00</Start>
      <Finish>2024-01-08T16:00:00</Finish>
      <PredecessorLink>
        <PredecessorUID>2</PredecessorUID>
        <Type>1</Type>
        <CrossProject>0</CrossProject>
        <LinkLag>14400</LinkLag>
        <LagFormat>7</LagFormat>
      </PredecessorLink>
    </Task>
    <Task>
      <UID>4</UID>
      <Name>Task 4</Name>
      <OutlineLevel>0</OutlineLevel>
      <OutlineNumber>4</OutlineNumber>
      <WBS>4</WBS>
      <Duration>PT8H0M0S</Duration>
      <Priority>500</Priority>
      <CalendarUID>-1</CalendarUID>
      <Start>2024-01-11T08:00:00</Start>
      <Finish>2024-01-11T16:00:00</Finish>
      <PredecessorLink>
        <PredecessorUID>3</PredecessorUID>
        <Type>1</Type>
        <CrossProject>0</CrossProject>
        <LinkLag>28800</LinkLag>
        <LagFormat>8</LagFormat>
      </PredecessorLink>
    </Task>
  </Tasks>
  <Calendars/>
</Project>
"""


class TestMsp2IfcLag:
    @staticmethod
    def convert() -> ifcopenshell.file:
        with tempfile.TemporaryDirectory() as tmp_dir:
            xml_path = Path(tmp_dir) / "project.xml"
            xml_path.write_text(MSPDI_XML)
            converter = MSP2Ifc()
            converter.xml = str(xml_path)
            converter.execute()
            return converter.file

    @staticmethod
    def get_rel_sequence(ifc_file, predecessor_identification: str, successor_identification: str):
        for rel in ifc_file.by_type("IfcRelSequence"):
            if (
                rel.RelatingProcess.Identification == predecessor_identification
                and rel.RelatedProcess.Identification == successor_identification
            ):
                return rel
        assert False, f"No IfcRelSequence found for {predecessor_identification} -> {successor_identification}"

    def test_zero_lag_leaves_time_lag_unset(self):
        ifc_file = self.convert()
        rel = self.get_rel_sequence(ifc_file, "1", "2")
        assert rel.TimeLag is None

    def test_worktime_lag_is_converted_from_tenths_of_a_minute(self):
        # LinkLag 14400 (tenths of a minute) / 10 / 60 = 24 hours = 3 working
        # days at the project's 8 hours (480 minutes) per day calendar.
        ifc_file = self.convert()
        rel = self.get_rel_sequence(ifc_file, "2", "3")
        assert rel.TimeLag is not None
        assert rel.TimeLag.DurationType == "WORKTIME"
        assert rel.TimeLag.LagValue.wrappedValue == "P3D"

    def test_elapsed_lag_uses_24_hour_days(self):
        # LinkLag 28800 (tenths of a minute) / 10 / 60 = 48 hours = 2 elapsed
        # (24/7) days, independent of the calendar's working hours per day.
        ifc_file = self.convert()
        rel = self.get_rel_sequence(ifc_file, "3", "4")
        assert rel.TimeLag is not None
        assert rel.TimeLag.DurationType == "ELAPSEDTIME"
        assert rel.TimeLag.LagValue.wrappedValue == "P2D"
