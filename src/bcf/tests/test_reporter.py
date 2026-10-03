# This file was generated with the assistance of an AI coding tool.

"""Tests for bcf.agnostic.reporter, exercising both BCF v2 and v3 files."""

import csv
import datetime
import uuid
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest
from xsdata.models.datatype import XmlDateTime

import bcf.v2.model as mdl2
import bcf.v3.model as mdl3
from bcf.agnostic.reporter import HEADERS, Reporter
from bcf.v2.bcfxml import BcfXml as BcfXmlV2
from bcf.v3.bcfxml import BcfXml as BcfXmlV3
from bcf.xml_parser import XmlParserSerializer


def build_bcf_v2(xml_handler: XmlParserSerializer) -> BcfXmlV2:
    bcf = BcfXmlV2.create_new("Test project", xml_handler=xml_handler)
    topic_handler = bcf.add_topic("Leaking pipe", "The pipe is leaking.", "alice@example.com", "Clash")
    topic = topic_handler.topic
    topic.topic_status = "Open"
    topic.priority = "High"
    topic.index = 3
    topic.labels = ["plumbing", "urgent"]
    topic.assigned_to = "bob@example.com"

    topic_handler.comments = [
        mdl2.Comment(
            date=XmlDateTime.from_datetime(datetime.datetime(2026, 1, 1)),
            author="alice@example.com",
            comment="Please fix ASAP.",
            guid=str(uuid.uuid4()),
        ),
        mdl2.Comment(
            date=XmlDateTime.from_datetime(datetime.datetime(2026, 1, 2)),
            author="bob@example.com",
            comment="Scheduled for tomorrow.",
            guid=str(uuid.uuid4()),
        ),
    ]
    return bcf


def build_bcf_v3(xml_handler: XmlParserSerializer) -> BcfXmlV3:
    bcf = BcfXmlV3.create_new("Test project", xml_handler=xml_handler)
    topic_handler = bcf.add_topic("Leaking pipe", "The pipe is leaking.", "alice@example.com", "Clash")
    topic = topic_handler.topic
    topic.topic_status = "Open"
    topic.priority = "High"
    topic.index = 3
    topic.labels = mdl3.TopicLabels(label=["plumbing", "urgent"])
    topic.assigned_to = "bob@example.com"

    topic_handler.comments = [
        mdl3.Comment(
            date=XmlDateTime.from_datetime(datetime.datetime(2026, 1, 1)),
            author="alice@example.com",
            comment="Please fix ASAP.",
            guid=str(uuid.uuid4()),
        ),
        mdl3.Comment(
            date=XmlDateTime.from_datetime(datetime.datetime(2026, 1, 2)),
            author="bob@example.com",
            comment="Scheduled for tomorrow.",
            guid=str(uuid.uuid4()),
        ),
    ]
    return bcf


BUILDERS = [build_bcf_v2, build_bcf_v3]


@pytest.mark.parametrize("build_bcf", BUILDERS)
def test_export_builds_one_row_per_topic(xml_handler, build_bcf):
    bcf = build_bcf(xml_handler)
    reporter = Reporter()
    rows = reporter.export(bcf)

    assert len(rows) == 1
    row = dict(zip(HEADERS, rows[0]))
    assert row["Title"] == "Leaking pipe"
    assert row["Type"] == "Clash"
    assert row["Status"] == "Open"
    assert row["Priority"] == "High"
    assert row["Index"] == 3
    assert row["Assigned To"] == "bob@example.com"
    assert row["Author"] == "alice@example.com"
    assert row["Description"] == "The pipe is leaking."
    assert row["Labels"] == "plumbing, urgent"
    assert row["Comments"] == "Please fix ASAP.; Scheduled for tomorrow."


@pytest.mark.parametrize("build_bcf", BUILDERS)
def test_export_writes_csv(xml_handler, build_bcf):
    bcf = build_bcf(xml_handler)
    reporter = Reporter()
    with TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "report.csv"
        reporter.export(bcf, output=output)

        with open(output, newline="", encoding="utf-8") as f:
            rows = list(csv.reader(f))

        assert rows[0] == HEADERS
        assert rows[1][HEADERS.index("Title")] == "Leaking pipe"
        assert rows[1][HEADERS.index("Comments")] == "Please fix ASAP.; Scheduled for tomorrow."


def test_export_format_is_inferred_from_output_suffix(xml_handler):
    bcf = build_bcf_v2(xml_handler)
    reporter = Reporter()
    with TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "report.csv"
        reporter.export(bcf, output=output)
        assert output.exists()


def test_export_rejects_unsupported_format(xml_handler):
    bcf = build_bcf_v2(xml_handler)
    reporter = Reporter()
    with TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "report.pdf"
        with pytest.raises(ValueError):
            reporter.export(bcf, output=output)


def test_export_xlsx(xml_handler):
    openpyxl = pytest.importorskip("openpyxl")
    bcf = build_bcf_v2(xml_handler)
    reporter = Reporter()
    with TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "report.xlsx"
        reporter.export(bcf, output=output)

        workbook = openpyxl.load_workbook(output)
        worksheet = workbook.active
        rows = list(worksheet.iter_rows(values_only=True))
        assert rows[0] == tuple(HEADERS)
        assert rows[1][HEADERS.index("Title")] == "Leaking pipe"


def test_export_ods(xml_handler):
    pytest.importorskip("odf")
    bcf = build_bcf_v2(xml_handler)
    reporter = Reporter()
    with TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "report.ods"
        reporter.export(bcf, output=output)
        assert output.exists()
        assert output.stat().st_size > 0
