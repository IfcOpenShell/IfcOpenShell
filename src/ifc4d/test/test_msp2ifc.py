# This file was generated with the assistance of an AI coding tool.

import datetime

import ifcopenshell.util.date

from ifc4d.msp2ifc import MSP2Ifc


def test_ms_project_relationship_lags_are_imported(tmp_path):
    xml = """\
<?xml version="1.0" encoding="UTF-8"?>
<Project xmlns="http://schemas.microsoft.com/project">
  <Name>Relationship lag test</Name>
  <MinutesPerDay>480</MinutesPerDay>
  <Tasks>
    <Task>
      <UID>1</UID>
      <Name>Predecessor</Name>
      <WBS>1</WBS>
      <OutlineNumber>1</OutlineNumber>
      <OutlineLevel>0</OutlineLevel>
      <Start>2024-01-01T08:00:00</Start>
      <Finish>2024-01-01T16:00:00</Finish>
      <Duration>PT8H0M0S</Duration>
      <Priority>500</Priority>
      <CalendarUID>-1</CalendarUID>
    </Task>
    <Task>
      <UID>2</UID>
      <Name>Working time lag</Name>
      <WBS>2</WBS>
      <OutlineNumber>2</OutlineNumber>
      <OutlineLevel>0</OutlineLevel>
      <Start>2024-01-08T08:00:00</Start>
      <Finish>2024-01-08T16:00:00</Finish>
      <Duration>PT8H0M0S</Duration>
      <Priority>500</Priority>
      <CalendarUID>-1</CalendarUID>
      <PredecessorLink>
        <PredecessorUID>1</PredecessorUID>
        <Type>1</Type>
        <LinkLag>24000</LinkLag>
        <LagFormat>7</LagFormat>
      </PredecessorLink>
    </Task>
    <Task>
      <UID>3</UID>
      <Name>Elapsed time lag</Name>
      <WBS>3</WBS>
      <OutlineNumber>3</OutlineNumber>
      <OutlineLevel>0</OutlineLevel>
      <Start>2024-03-23T08:00:00</Start>
      <Finish>2024-03-23T16:00:00</Finish>
      <Duration>PT8H0M0S</Duration>
      <Priority>500</Priority>
      <CalendarUID>-1</CalendarUID>
      <PredecessorLink>
        <PredecessorUID>2</PredecessorUID>
        <Type>1</Type>
        <LinkLag>1080000</LinkLag>
        <LagFormat>8</LagFormat>
      </PredecessorLink>
    </Task>
    <Task>
      <UID>4</UID>
      <Name>Negative working time lag</Name>
      <WBS>4</WBS>
      <OutlineNumber>4</OutlineNumber>
      <OutlineLevel>0</OutlineLevel>
      <Start>2024-03-22T08:00:00</Start>
      <Finish>2024-03-22T16:00:00</Finish>
      <Duration>PT8H0M0S</Duration>
      <Priority>500</Priority>
      <CalendarUID>-1</CalendarUID>
      <PredecessorLink>
        <PredecessorUID>3</PredecessorUID>
        <Type>1</Type>
        <LinkLag>-4800</LinkLag>
        <LagFormat>7</LagFormat>
      </PredecessorLink>
    </Task>
    <Task>
      <UID>5</UID>
      <Name>Zero lag</Name>
      <WBS>5</WBS>
      <OutlineNumber>5</OutlineNumber>
      <OutlineLevel>0</OutlineLevel>
      <Start>2024-03-25T08:00:00</Start>
      <Finish>2024-03-25T16:00:00</Finish>
      <Duration>PT8H0M0S</Duration>
      <Priority>500</Priority>
      <CalendarUID>-1</CalendarUID>
      <PredecessorLink>
        <PredecessorUID>4</PredecessorUID>
        <Type>1</Type>
        <LinkLag>0</LinkLag>
        <LagFormat>7</LagFormat>
      </PredecessorLink>
    </Task>
  </Tasks>
  <Calendars />
</Project>
"""
    xml_path = tmp_path / "relationship-lags.xml"
    xml_path.write_text(xml)

    importer = MSP2Ifc()
    importer.xml = xml_path
    importer.execute()

    relationships = {
        (relationship.RelatingProcess.Identification, relationship.RelatedProcess.Identification): relationship
        for relationship in importer.file.by_type("IfcRelSequence")
    }

    working_lag = relationships[("1", "2")].TimeLag
    assert working_lag.DurationType == "WORKTIME"
    assert ifcopenshell.util.date.ifc2datetime(working_lag.LagValue.wrappedValue) == datetime.timedelta(days=5)

    elapsed_lag = relationships[("2", "3")].TimeLag
    assert elapsed_lag.DurationType == "ELAPSEDTIME"
    assert ifcopenshell.util.date.ifc2datetime(elapsed_lag.LagValue.wrappedValue) == datetime.timedelta(days=75)

    negative_lag = relationships[("3", "4")].TimeLag
    assert negative_lag.DurationType == "WORKTIME"
    assert ifcopenshell.util.date.ifc2datetime(negative_lag.LagValue.wrappedValue) == datetime.timedelta(days=-1)

    assert relationships[("4", "5")].TimeLag is None
