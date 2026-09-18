# BCF - BCF Python library
# Copyright (C) 2026 IfcOpenShell contributors
#
# This file is part of BCF.
#
# BCF is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# BCF is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with BCF.  If not, see <http://www.gnu.org/licenses/>.

# This file was generated with the assistance of an AI coding tool.

"""Export BCF topics to a spreadsheet (CSV, XLSX, or ODS) for reporting.

This mirrors the format handling conventions of the IfcCSV module, but is
kept dependency-free for CSV (the ``xlsx``/``ods`` formats require the
optional ``openpyxl``/``odfpy`` packages, same as IfcCSV).
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any, Literal, Optional, Union

import bcf.v2.bcfxml
import bcf.v2.topic
import bcf.v3.bcfxml
import bcf.v3.topic

try:
    import openpyxl
except ImportError:
    openpyxl = None  # type: ignore[assignment]

try:
    from odf.opendocument import OpenDocumentSpreadsheet
    from odf.table import Table, TableCell, TableRow
    from odf.text import P
except ImportError:
    OpenDocumentSpreadsheet = None  # type: ignore[assignment, misc]


BcfXml = Union[bcf.v2.bcfxml.BcfXml, bcf.v3.bcfxml.BcfXml]
TopicHandler = Union[bcf.v2.topic.TopicHandler, bcf.v3.topic.TopicHandler]

FILE_FORMAT = Literal["csv", "xlsx", "ods"]

HEADERS = [
    "Index",
    "GUID",
    "Title",
    "Type",
    "Status",
    "Priority",
    "Stage",
    "Assigned To",
    "Author",
    "Creation Date",
    "Modified Author",
    "Modified Date",
    "Due Date",
    "Labels",
    "Description",
    "Comments",
]


class Reporter:
    """Export the topics of a BCF file to a spreadsheet.

    Each row represents one topic (BCF "issue"), similar to the reports
    produced by tools such as BIMcollab or Solibri. Comments are
    concatenated into a single cell per topic.
    """

    headers: list[str]
    rows: list[list[Any]]

    def __init__(self) -> None:
        self.headers = list(HEADERS)
        self.rows = []

    def export(
        self,
        bcfxml: BcfXml,
        output: Optional[Union[str, Path]] = None,
        format: Optional[FILE_FORMAT] = None,
        delimiter: str = ",",
    ) -> list[list[Any]]:
        """Build the report rows, optionally writing them to ``output``.

        :param bcfxml: A loaded BCF v2 or v3 file.
        :param output: If provided, the report is written to this path.
        :param format: One of "csv", "xlsx", or "ods". If not provided, it
            is guessed from the ``output`` file extension, defaulting to
            "csv".
        :param delimiter: The field delimiter to use for CSV output.
        :return: The report rows (excluding the header row).
        """
        self.rows = [self.get_topic_row(topic_handler) for topic_handler in bcfxml.topics.values()]

        if output:
            format = format or (Path(output).suffix.lstrip(".").lower() or "csv")
            if format == "csv":
                self.export_csv(output, delimiter=delimiter)
            elif format == "xlsx":
                self.export_xlsx(output)
            elif format == "ods":
                self.export_ods(output)
            else:
                raise ValueError(f"Unsupported format: '{format}'. Use 'csv', 'xlsx', or 'ods'.")

        return self.rows

    def get_topic_row(self, topic_handler: TopicHandler) -> list[Any]:
        """Build a single report row from a topic."""
        topic = topic_handler.topic

        labels = topic.labels
        if labels is not None and not isinstance(labels, list):
            # BCF v3 wraps labels in a TopicLabels element, unlike v2's plain list.
            labels = labels.label

        comments = "; ".join(comment.comment for comment in topic_handler.comments if comment.comment)

        return [
            topic.index,
            topic.guid,
            topic.title,
            topic.topic_type,
            topic.topic_status,
            topic.priority,
            topic.stage,
            topic.assigned_to,
            topic.creation_author,
            self.format_date(topic.creation_date),
            topic.modified_author,
            self.format_date(topic.modified_date),
            self.format_date(topic.due_date),
            ", ".join(labels) if labels else None,
            topic.description,
            comments,
        ]

    @staticmethod
    def format_date(value: Any) -> Optional[str]:
        return str(value) if value is not None else None

    def export_csv(self, output: Union[str, Path], delimiter: str = ",") -> None:
        with open(output, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f, delimiter=delimiter)
            writer.writerow(self.headers)
            writer.writerows(self.rows)

    def export_xlsx(self, output: Union[str, Path]) -> None:
        if not openpyxl:
            raise ImportError("openpyxl is required to export to XLSX. Install it with `pip install openpyxl`.")
        workbook = openpyxl.Workbook()
        worksheet = workbook.active
        worksheet.append(self.headers)
        for row in self.rows:
            worksheet.append(row)
        workbook.save(output)

    def export_ods(self, output: Union[str, Path]) -> None:
        if not OpenDocumentSpreadsheet:
            raise ImportError("odfpy is required to export to ODS. Install it with `pip install odfpy`.")
        document = OpenDocumentSpreadsheet()
        table = Table(name="BCF Topics")
        table.addElement(self._build_ods_row(self.headers))
        for row in self.rows:
            table.addElement(self._build_ods_row(row))
        document.spreadsheet.addElement(table)
        document.save(output)

    @staticmethod
    def _build_ods_row(values: list[Any]) -> "TableRow":
        row = TableRow()
        for value in values:
            cell = TableCell()
            cell.addElement(P(text="" if value is None else str(value)))
            row.addElement(cell)
        return row
