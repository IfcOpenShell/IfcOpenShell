# IfcTester - IDS based model auditing
# Copyright (C) 2021 Artur Tomczak <artomczak@gmail.com>, Thomas Krijnen <mail@thomaskrijnen.com>, Dion Moult <dion@thinkmoult.com>
#
# This file is part of IfcTester.
#
# IfcTester is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcTester is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcTester.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import annotations

import datetime
import json
import math
import os
import re
import sqlite3
import sys
from collections.abc import Iterable, Iterator
from typing import Literal, Optional, TypedDict, Union

import ifcopenshell
import ifcopenshell.util.element
import ifcopenshell.util.placement
import ifcopenshell.util.unit
from typing_extensions import NotRequired

from .facet import Facet, FacetFailure
from .ids import Ids, Specification

cwd = os.path.dirname(os.path.realpath(__file__))


class Reporter:
    def __init__(self, ids: Ids):
        self.ids = ids

    def report(self, ids):
        pass

    def to_string(self):
        return ""

    def write(self, filepath):
        pass


ResultsPercent = Union[int, Literal["N/A"]]


class Results(TypedDict):
    title: str
    date: str
    filepath: str
    filename: str
    hide_skipped: bool
    specifications: list[ResultsSpecification]
    status: bool
    total_specifications: int
    total_specifications: int
    total_specifications_pass: int
    total_specifications_fail: int
    percent_specifications_pass: ResultsPercent
    total_requirements: int
    total_requirements_pass: int
    total_requirements_fail: int
    percent_requirements_pass: ResultsPercent
    total_checks: int
    total_checks_pass: int
    total_checks_fail: int
    percent_checks_pass: ResultsPercent


class ResultsSpecification(TypedDict):
    name: str
    description: str
    instructions: str
    status: bool
    is_skipped: bool
    is_ifc_version: bool
    total_applicable: int
    total_applicable_pass: int
    total_applicable_fail: int
    applicable_entities: list[ResultsEntity]
    percent_applicable_pass: ResultsPercent
    total_checks: int
    total_checks_pass: int
    total_checks_fail: int
    percent_checks_pass: ResultsPercent
    cardinality: str
    applicability: list[str]
    requirements: list[ResultsRequirement]

    # Filled in by `Html.report()`.
    is_prohibited: NotRequired[bool]
    has_requirements: NotRequired[bool]
    has_omitted_applicable: NotRequired[bool]
    total_omitted_applicable: NotRequired[int]


class ResultsRequirement(TypedDict):
    facet_type: str
    metadata: dict
    label: str
    value: str
    description: str
    status: bool
    passed_entities: list[ResultsEntity]
    failed_entities: list[ResultsEntity]
    total_applicable: int
    total_pass: int
    total_fail: int
    percent_pass: ResultsPercent

    # Filled in by `Html.report()`.
    total_failed_entities: NotRequired[int]
    total_omitted_failures: NotRequired[int]
    has_omitted_failures: NotRequired[bool]
    total_passed_entities: NotRequired[int]
    total_omitted_passes: NotRequired[int]
    has_omitted_passes: NotRequired[bool]
    instructions: NotRequired[str | None]


# use different syntax because of the "class" key
ResultsEntity = TypedDict(
    "ResultsEntity",
    {
        "reason": str,
        "element": ifcopenshell.entity_instance,
        "element_type": Union[ifcopenshell.entity_instance, None],
        "class": str,
        "predefined_type": str,
        "name": Union[str, None],
        "description": Union[str, None],
        "id": int,
        "global_id": Union[str, None],
        "tag": Union[str, None],
    },
)


def get_requirement_label_value(requirement: Facet) -> tuple[Optional[str], str]:
    """Derive a human readable label and value for a requirement facet.

    Facet attributes may hold a `Restriction` rather than a plain string, so
    both are coerced to text. Only `PartOf.relation` may legitimately be None.
    """
    facet_type = type(requirement).__name__
    value = ""
    if facet_type == "Entity":
        if requirement.predefinedType:
            label = "IFC Class / Predefined Type"
            value = f"{requirement.name}.{requirement.predefinedType}"
        else:
            label = "IFC Class"
            value = requirement.name
    elif facet_type == "Attribute":
        label = requirement.name
        if requirement.value:
            value = requirement.value
    elif facet_type == "Classification":
        if requirement.system and requirement.value:
            label = "System / Reference"
            value = f"{requirement.system} / {requirement.value}"
        elif requirement.system:
            label = "System"
            value = requirement.system
        elif requirement.value:
            label = "Reference"
            value = requirement.value
        else:
            assert False, requirement
    elif facet_type == "PartOf":
        label = requirement.relation
        if requirement.predefinedType:
            value = f"{requirement.name}.{requirement.predefinedType}"
        else:
            value = requirement.name
    elif facet_type == "Property":
        label = f"{requirement.propertySet}.{requirement.baseName}"
        if requirement.value:
            value = requirement.value
    elif facet_type == "Material":
        label = "Name / Category"
        if requirement.value:
            value = requirement.value
    else:
        assert False, facet_type
    return None if label is None else str(label), str(value)


def get_cardinality(specification: Specification) -> str:
    if specification.minOccurs == 1 and specification.maxOccurs == "unbounded":
        return "required"
    elif specification.minOccurs == 0 and specification.maxOccurs == "unbounded":
        return "optional"
    elif specification.minOccurs == 0 and specification.maxOccurs == 0:
        return "prohibited"
    elif specification.minOccurs >= 1:
        # Any minimum occurrence >= 1 means the specification is required
        return "required"
    # minOccurs == 0 with any other maxOccurs value means optional
    return "optional"


class Console(Reporter):
    def __init__(self, ids: Ids, use_colour=True):
        super().__init__(ids)
        self.use_colour = use_colour
        self.colours = {
            "red": "\033[1;31m",
            "blue": "\033[1;34m",
            "cyan": "\033[1;36m",
            "green": "\033[0;32m",
            "yellow": "\033[0;33m",
            "purple": "\033[0;95m",
            "grey": "\033[0;90m",
            "reset": "\033[0;0m",
            "bold": "\033[;1m",
            "reverse": "\033[;7m",
        }

    def report(self) -> None:
        self.set_style("bold", "blue")
        self.print(self.ids.info.get("title", "Untitled IDS"))
        for specification in self.ids.specifications:
            self.report_specification(specification)
        self.set_style("reset")

    def report_specification(self, specification: Specification) -> None:
        if specification.status is True:
            self.set_style("bold", "green")
            self.print("[PASS] ", end="")
        elif specification.status is False:
            self.set_style("bold", "red")
            self.print("[FAIL] ", end="")
        elif specification.status is None:
            self.set_style("bold", "yellow")
            self.print("[UNTESTED] ", end="")

        self.set_style("bold")
        total = len(specification.applicable_entities)
        total_successes = total - len(specification.failed_entities)
        self.print(f"({total_successes}/{total}) ", end="")

        if specification.minOccurs != 0:
            self.print(f"*", end="")

        self.print(specification.name)

        self.set_style("cyan")
        self.print(" " * 4 + "Applies to:")
        self.set_style("reset")

        for applicability in specification.applicability:
            self.print(" " * 8 + applicability.to_string("applicability"))

        if not total and specification.status is False:
            return

        self.set_style("cyan")
        self.print(" " * 4 + "Requirements:")
        self.set_style("reset")

        for requirement in specification.requirements:
            self.set_style("reset")
            self.set_style("red") if requirement.failures else self.set_style("green")
            self.print(" " * 8 + requirement.to_string("requirement", specification, requirement))
            self.set_style("reset")
            for failure in requirement.failures[0:10]:
                self.print(" " * 12, end="")
                self.report_reason(failure)
            if len(requirement.failures) > 10:
                self.print(" " * 12 + f"... {len(requirement.failures)} in total ...")
        self.set_style("reset")

    def report_reason(self, failure: FacetFailure) -> None:
        is_bold = False
        for substring in failure["reason"].split('"'):
            if is_bold:
                self.set_style("purple")
            else:
                self.set_style("reset")
            self.print(substring, end="")
            is_bold = not is_bold
        self.set_style("grey")
        self.print(" - " + str(failure["element"]))
        self.set_style("reset")

    def set_style(self, *colours: str):
        if self.use_colour:
            sys.stdout.write("".join([self.colours[c] for c in colours]))

    def print(self, txt: str, end: Optional[str] = None):
        if end is not None:
            print(txt, end=end)
        else:
            print(txt)


class Txt(Console):
    def __init__(self, ids: Ids):
        super().__init__(ids, use_colour=False)
        self.text = ""

    def print(self, txt: str, end: Optional[str] = None):
        self.text += txt + "\n" if end is None else end

    def to_string(self) -> None:
        print(self.text)

    def to_file(self, filepath: str) -> None:
        with open(filepath, "w", encoding="utf-8") as outfile:
            return outfile.write(self.text)


class Json(Reporter):
    def __init__(self, ids: Ids, hide_skipped=False):
        super().__init__(ids)
        self.results = Results()  # ty:ignore[missing-typed-dict-key]
        self.results["hide_skipped"] = hide_skipped

    def report(self) -> Results:
        self.results["title"] = self.ids.info.get("title", "Untitled IDS")
        self.results["date"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.results["filepath"] = self.ids.filepath
        self.results["filename"] = self.ids.filename
        total_specifications = 0
        total_specifications_pass = 0
        total_requirements = 0
        total_requirements_pass = 0
        total_checks = 0
        total_checks_pass = 0
        status = True
        self.results["specifications"] = []
        for specification in self.ids.specifications:
            specification_report = self.report_specification(specification)
            self.results["specifications"].append(specification_report)
            total_specifications += 1
            total_specifications_pass += 1 if specification_report["status"] else 0
            total_requirements += len(specification_report["requirements"])
            total_requirements_pass += len([r for r in specification_report["requirements"] if r["status"]])
            total_checks += specification_report["total_checks"]
            total_checks_pass += specification_report["total_checks_pass"]
            if not specification_report["status"]:
                status = False
        self.results["status"] = status
        self.results["total_specifications"] = total_specifications
        self.results["total_specifications_pass"] = total_specifications_pass
        self.results["total_specifications_fail"] = total_specifications - total_specifications_pass
        self.results["percent_specifications_pass"] = (
            math.floor((total_specifications_pass / total_specifications) * 100) if total_specifications else "N/A"
        )
        self.results["total_requirements"] = total_requirements
        self.results["total_requirements_pass"] = total_requirements_pass
        self.results["total_requirements_fail"] = total_requirements - total_requirements_pass
        self.results["percent_requirements_pass"] = (
            math.floor((total_requirements_pass / total_requirements) * 100) if total_requirements else "N/A"
        )
        self.results["total_checks"] = total_checks
        self.results["total_checks_pass"] = total_checks_pass
        self.results["total_checks_fail"] = total_checks - total_checks_pass
        self.results["percent_checks_pass"] = (
            math.floor((total_checks_pass / total_checks) * 100) if total_checks else "N/A"
        )
        return self.results

    def report_specification(self, specification: Specification) -> ResultsSpecification:
        applicability = [a.to_string("applicability") for a in specification.applicability]
        total_applicable = len(specification.applicable_entities)
        total_checks = 0
        total_checks_pass = 0
        requirements = []
        for requirement in specification.requirements:
            total_fail = len(requirement.failures)
            total_pass = total_applicable - total_fail
            percent_pass = math.floor((total_pass / total_applicable) * 100) if total_applicable else "N/A"
            total_checks += total_applicable
            total_checks_pass += total_pass
            facet_type = type(requirement).__name__
            label, value = get_requirement_label_value(requirement)
            requirements.append(
                ResultsRequirement(
                    facet_type=facet_type,
                    metadata=requirement.asdict("requirement"),
                    label=label,
                    value=value,
                    description=requirement.to_string("requirement", specification, requirement),
                    status=requirement.status,
                    passed_entities=self.report_passed_entities(requirement),
                    failed_entities=self.report_failed_entities(requirement),
                    total_applicable=total_applicable,
                    total_pass=total_pass,
                    total_fail=total_fail,
                    percent_pass=percent_pass,
                )
            )
        total_applicable_pass = total_applicable - len(specification.failed_entities)
        percent_applicable_pass = (
            math.floor((total_applicable_pass / total_applicable) * 100) if total_applicable else "N/A"
        )
        percent_checks_pass = math.floor((total_checks_pass / total_checks) * 100) if total_checks else "N/A"

        cardinality = get_cardinality(specification)

        return ResultsSpecification(
            name=specification.name,
            description=specification.description,
            instructions=specification.instructions,
            status=specification.status,
            is_skipped=cardinality == "optional" and total_checks == 0,
            is_ifc_version=specification.is_ifc_version,
            total_applicable=total_applicable,
            total_applicable_pass=total_applicable_pass,
            total_applicable_fail=total_applicable - total_applicable_pass,
            applicable_entities=self.report_applicable_entities(specification),
            percent_applicable_pass=percent_applicable_pass,
            total_checks=total_checks,
            total_checks_pass=total_checks_pass,
            total_checks_fail=total_checks - total_checks_pass,
            percent_checks_pass=percent_checks_pass,
            cardinality=cardinality,
            applicability=applicability,
            requirements=requirements,
        )

    def report_applicable_entities(self, specification: Specification) -> list[ResultsEntity]:
        return [
            ResultsEntity(
                {
                    "element": e,
                    "element_type": ifcopenshell.util.element.get_type(e),
                    "class": e.is_a(),
                    "predefined_type": ifcopenshell.util.element.get_predefined_type(e),
                    "name": getattr(e, "Name", None),
                    "description": getattr(e, "Description", None),
                    "id": e.id(),
                    "global_id": getattr(e, "GlobalId", None),
                    "tag": getattr(e, "Tag", None),
                }  # ty:ignore[missing-typed-dict-key]
            )
            for e in specification.applicable_entities
        ]

    def report_passed_entities(self, requirement: Facet) -> list[ResultsEntity]:
        return [
            ResultsEntity(
                {
                    "element": e,
                    "element_type": ifcopenshell.util.element.get_type(e),
                    "class": e.is_a(),
                    "predefined_type": ifcopenshell.util.element.get_predefined_type(e),
                    "name": getattr(e, "Name", None),
                    "description": getattr(e, "Description", None),
                    "id": e.id(),
                    "global_id": getattr(e, "GlobalId", None),
                    "tag": getattr(e, "Tag", None),
                }  # ty:ignore[missing-typed-dict-key]
            )
            for e in requirement.passed_entities
        ]

    def report_failed_entities(self, requirement: Facet) -> list[ResultsEntity]:
        return [
            ResultsEntity(
                {
                    "reason": f["reason"],
                    "element": f["element"],
                    "element_type": ifcopenshell.util.element.get_type(f["element"]),
                    "class": f["element"].is_a(),
                    "predefined_type": ifcopenshell.util.element.get_predefined_type(f["element"]),
                    "name": getattr(f["element"], "Name", None),
                    "description": getattr(f["element"], "Description", None),
                    "id": f["element"].id(),
                    "global_id": getattr(f["element"], "GlobalId", None),
                    "tag": getattr(f["element"], "Tag", None),
                }
            )
            for f in requirement.failures
        ]

    def to_string(self) -> str:
        return json.dumps(self.results, default=self.encode)

    def to_file(self, filepath: str) -> None:
        with open(filepath, "w", encoding="utf-8") as outfile:
            return json.dump(self.results, outfile, ensure_ascii=False, default=self.encode)

    def encode(self, obj):
        return str(obj)


class Html(Json):
    def __init__(self, ids: Ids, hide_skipped: bool = False):
        self.entity_limit = 100
        super().__init__(ids)
        self.results["hide_skipped"] = hide_skipped

    def report(self) -> None:
        super().report()
        for spec in self.results["specifications"]:
            spec["is_prohibited"] = spec["cardinality"] == "prohibited"
            spec["cardinality"] = spec["cardinality"].capitalize()
            spec["has_requirements"] = bool(spec["requirements"])
            total_applicable_entities = len(spec["applicable_entities"])
            spec["applicable_entities"] = self.limit_entities(spec["applicable_entities"])
            spec["has_omitted_applicable"] = total_applicable_entities > self.entity_limit
            spec["total_omitted_applicable"] = total_applicable_entities - self.entity_limit
            for requirement in spec["requirements"]:
                total_passed_entities = len(requirement["passed_entities"])
                total_failed_entities = len(requirement["failed_entities"])
                requirement["passed_entities"] = self.limit_entities(requirement["passed_entities"])
                requirement["failed_entities"] = self.limit_entities(requirement["failed_entities"])
                requirement["total_failed_entities"] = total_failed_entities
                requirement["total_omitted_failures"] = total_failed_entities - self.entity_limit
                requirement["has_omitted_failures"] = total_failed_entities > self.entity_limit
                requirement["total_passed_entities"] = total_passed_entities
                requirement["total_omitted_passes"] = total_passed_entities - self.entity_limit
                requirement["has_omitted_passes"] = total_passed_entities > self.entity_limit
                requirement["instructions"] = requirement["metadata"].get("@instructions")

    def limit_entities(self, entities):
        if len(entities) > self.entity_limit:
            if entities[0]["element_type"]:
                return self.group_by_type(entities)
            return entities[0 : self.entity_limit]
        return entities

    def group_by_type(self, entities):
        results = []
        group_limit = 5
        grouped_by_type = {}
        [grouped_by_type.setdefault(e["element_type"], []).append(e) for e in entities]
        total_entities = 0
        for element_type, entities in grouped_by_type.items():
            for i, entity in enumerate(entities):
                results.append(entity)
                total_entities += 1

                if element_type and i > group_limit:
                    results[-1]["type_name"] = element_type.Name if element_type else "Untyped"
                    if element_type:
                        results[-1]["type_tag"] = element_type.Tag
                        results[-1]["type_global_id"] = element_type.GlobalId
                    results[-1]["extra_of_type"] = len(entities) - i
                    if total_entities == self.entity_limit:
                        return results
                    break

                if total_entities == self.entity_limit:
                    results[-1]["type_name"] = element_type.Name if element_type else "Untyped"
                    if element_type:
                        results[-1]["type_tag"] = element_type.Tag
                        results[-1]["type_global_id"] = element_type.GlobalId
                    results[-1]["extra_of_type"] = len(entities) - i
                    return results
        return results

    def to_string(self) -> str:
        import pystache

        with open(os.path.join(cwd, "templates", "report.html"), "r") as file:
            return pystache.render(file.read(), self.results)

    def to_file(self, filepath: str) -> None:
        import pystache

        with open(os.path.join(cwd, "templates", "report.html"), "r") as file:
            with open(filepath, "w", encoding="utf-8") as outfile:
                return outfile.write(pystache.render(file.read(), self.results))


class Ods(Json):
    def __init__(self, ids: Ids, excel_safe=False):
        super().__init__(ids)
        self.excel_safe = excel_safe
        self.colours = {
            "h": "cccccc",  # Header
            "p": "97cc64",  # Pass
            "f": "fb5a3e",  # Fail
            "t": "ffffff",  # Regular text
        }

    def excel_safe_spreadsheet_name(self, name: str) -> str:
        if not self.excel_safe:
            return name

        warning = (
            f'WARNING. Sheet name "{name}" is not valid for Excel and will be changed. '
            "See: https://support.microsoft.com/en-us/office/rename-a-worksheet-3f1f7148-ee83-404d-8ef0-9ff99fbad1f9"
        )

        if not name or name == "History":
            print(warning)
            return "placeholder spreadsheet name"

        if name.startswith("'") or name.endswith("'"):
            print(warning)
            name = name.strip("'")

        pattern = r"[\\\/\?\*\:\[\]]"
        if re.search(pattern, name):
            name = re.sub(pattern, "", name)
            print(warning)

        if len(name) > 31:
            name = name[:31]
            print(warning)
        return name

    def to_file(self, filepath: str) -> None:
        from odf.opendocument import OpenDocumentSpreadsheet
        from odf.style import Style, TableCellProperties
        from odf.table import Table, TableCell, TableRow
        from odf.text import P

        self.doc = OpenDocumentSpreadsheet()

        self.cell_formats = {}
        for key, value in self.colours.items():
            style = Style(name=key, family="table-cell")
            style.addElement(TableCellProperties(backgroundcolor="#" + value))
            self.doc.automaticstyles.addElement(style)
            self.cell_formats[key] = style

        table = Table(name=self.excel_safe_spreadsheet_name(self.results["title"]))
        tr = TableRow()
        for header in ["Specification", "Status", "Total Pass", "Total Checks", "Percentage Pass"]:
            tc = TableCell(valuetype="string", stylename="h")
            tc.addElement(P(text=header))
            tr.addElement(tc)
        table.addElement(tr)

        rows = []
        for specification in self.results["specifications"]:
            rows.append(
                [
                    specification["name"],
                    "Pass" if specification["status"] else "Fail",
                    str(specification["total_checks_pass"]),
                    str(specification["total_checks"]),
                    str(specification["percent_checks_pass"]),
                ]
            )

        for row in rows:
            tr = TableRow()
            c = 0
            stylename = "p" if row[1] == "Pass" else "f"
            for col in row:
                tc = TableCell(valuetype="string", stylename=stylename)
                if col is None:
                    col = "NULL"
                tc.addElement(P(text=col))
                tr.addElement(tc)
                c += 1
            table.addElement(tr)
        self.doc.spreadsheet.addElement(table)

        for specification in self.results["specifications"]:
            if specification["status"]:
                continue
            table = Table(name=self.excel_safe_spreadsheet_name(specification["name"]))
            tr = TableRow()
            for header in [
                "Requirement",
                "Problem",
                "Class",
                "PredefinedType",
                "Name",
                "Description",
                "GlobalId",
                "Tag",
                "Element",
                "ElementType",
            ]:
                tc = TableCell(valuetype="string", stylename="h")
                tc.addElement(P(text=header))
                tr.addElement(tc)
            table.addElement(tr)
            for requirement in specification["requirements"]:
                if requirement["status"]:
                    continue
                for failure in requirement["failed_entities"]:
                    element = failure.get("element", None)
                    element_type = failure.get("element_type", None)
                    row = [
                        requirement["description"],
                        failure.get("reason", "No reason provided"),
                        failure["class"],
                        failure["predefined_type"],
                        failure["name"],
                        failure["description"],
                        failure["global_id"],
                        failure["tag"],
                        str(element) if element else "N/A",
                        str(element_type) if element_type else "N/A",
                    ]
                    tr = TableRow()
                    c = 0
                    for col in row:
                        tc = TableCell(valuetype="string", stylename="t")
                        if col is None:
                            col = "NULL"
                        tc.addElement(P(text=col))
                        tr.addElement(tc)
                        c += 1
                    table.addElement(tr)
            self.doc.spreadsheet.addElement(table)

        self.doc.save(filepath, addsuffix=not filepath.lower().endswith(".ods"))


class OdsSummary(Json):
    def __init__(self, ids: Ids, excel_safe=False):
        super().__init__(ids)
        self.excel_safe = excel_safe
        self.colours = {
            "h": "cccccc",  # Header
            "p": "97cc64",  # Pass
            "f": "fb5a3e",  # Fail
            "t": "ffffff",  # Regular text
        }

    def excel_safe_spreadsheet_name(self, name: str) -> str:
        if not self.excel_safe:
            return name

        warning = (
            f'WARNING. Sheet name "{name}" is not valid for Excel and will be changed. '
            "See: https://support.microsoft.com/en-us/office/rename-a-worksheet-3f1f7148-ee83-404d-8ef0-9ff99fbad1f9"
        )

        if not name or name == "History":
            print(warning)
            return "placeholder spreadsheet name"

        if name.startswith("'") or name.endswith("'"):
            print(warning)
            name = name.strip("'")

        pattern = r"[\\\/\?\*\:\[\]]"
        if re.search(pattern, name):
            name = re.sub(pattern, "", name)
            print(warning)

        if len(name) > 31:
            name = name[:31]
            print(warning)
        return name

    def to_file(self, filepath: str) -> None:
        from odf.opendocument import OpenDocumentSpreadsheet
        from odf.style import Style, TableCellProperties
        from odf.table import Table, TableCell, TableRow
        from odf.text import P

        self.doc = OpenDocumentSpreadsheet()

        self.cell_formats = {}
        for key, value in self.colours.items():
            style = Style(name=key, family="table-cell")
            style.addElement(TableCellProperties(backgroundcolor="#" + value))
            self.doc.automaticstyles.addElement(style)
            self.cell_formats[key] = style

        table = Table(name=self.excel_safe_spreadsheet_name(self.results["title"]))
        tr = TableRow()
        for header in ["Specification", "Applicability", "Facet Type", "Data Name", "Value Requirements"]:
            tc = TableCell(valuetype="string", stylename="h")
            tc.addElement(P(text=header))
            tr.addElement(tc)
        table.addElement(tr)

        rows = []
        for specification in self.results["specifications"]:
            applicability = ", ".join(specification["applicability"])
            for requirement in specification["requirements"]:
                rows.append(
                    [
                        specification["name"],
                        applicability,
                        requirement["facet_type"],
                        requirement["label"],
                        requirement["value"],
                    ]
                )

        for row in rows:
            tr = TableRow()
            c = 0
            for col in row:
                tc = TableCell(valuetype="string")
                if col is None:
                    col = "NULL"
                tc.addElement(P(text=col))
                tr.addElement(tc)
                c += 1
            table.addElement(tr)
        self.doc.spreadsheet.addElement(table)

        while False:
            for requirement in specification["requirements"]:
                if requirement["status"]:
                    continue
                for failure in requirement["failed_entities"]:
                    element = failure.get("element", None)
                    element_type = failure.get("element_type", None)
                    row = [
                        requirement["description"],
                        failure.get("reason", "No reason provided"),
                        failure["class"],
                        failure["predefined_type"],
                        failure["name"],
                        failure["description"],
                        failure["global_id"],
                        failure["tag"],
                        str(element) if element else "N/A",
                        str(element_type) if element_type else "N/A",
                    ]
                    tr = TableRow()
                    c = 0
                    for col in row:
                        tc = TableCell(valuetype="string", stylename="t")
                        if col is None:
                            col = "NULL"
                        tc.addElement(P(text=col))
                        tr.addElement(tc)
                        c += 1
                    table.addElement(tr)
            self.doc.spreadsheet.addElement(table)

        self.doc.save(filepath, addsuffix=not filepath.lower().endswith(".ods"))


class Bcf(Json):
    def report_failed_entities(self, requirement: Facet) -> list[FacetFailure]:
        return [FacetFailure(f) for f in requirement.failures]

    def to_file(self, filepath: str) -> None:
        import numpy as np
        from bcf.v2.bcfxml import BcfXml

        unit_scale = None
        bcfxml = BcfXml.create_new(self.results["title"])
        for specification in self.results["specifications"]:
            if specification["status"]:
                continue
            for requirement in specification["requirements"]:
                if requirement["status"]:
                    continue
                for failure in requirement["failed_entities"]:
                    element = failure["element"]
                    title_components = []
                    for title_component in [
                        element.is_a(),
                        getattr(element, "Name", "") or "Unnamed",
                        failure.get("reason", "No reason"),
                        getattr(element, "GlobalId", ""),
                        getattr(element, "Tag", ""),
                    ]:
                        if title_component:
                            title_components.append(title_component)
                    title = " - ".join(title_components)
                    description = f'{specification["name"]} - {requirement["description"]}'
                    topic = bcfxml.add_topic(title, description, "IfcTester")
                    if getattr(element, "ObjectPlacement", None):
                        placement = ifcopenshell.util.placement.get_local_placement(element.ObjectPlacement)
                        if unit_scale is None:
                            unit_scale = ifcopenshell.util.unit.calculate_unit_scale(element.file)
                        location = [(o * unit_scale) + 5.0 for o in placement[:, 3][:3]]
                        viewpoint = topic.add_viewpoint_from_point_and_guids(np.array(location), element.GlobalId)
                    if element.is_a("IfcElement"):
                        topic.add_viewpoint(element)
        bcfxml.save_project(filepath)


class Sqlite(Reporter):
    """Stores audit results in a normalised SQLite database.

    Where `Json` repeats every entity's attributes once per specification and
    once more per requirement, entities are stored once in the `entity` table
    and referenced by ID everywhere else. Only failures are stored: a passing
    check is any applicable entity without a failure row, which the `passed`
    view derives on demand.

    This keeps reports for large models orders of magnitude smaller, and lets
    consumers page through results with a query instead of parsing an entire
    document. Note that `report` is a no-op: rows are written during `to_file`
    so that no intermediate result tree is ever built.
    """

    SCHEMA_VERSION = 1

    SCHEMA = """
        CREATE TABLE meta (
            key TEXT PRIMARY KEY,
            value TEXT  -- All values are stored as text
        );

        CREATE TABLE entity (
            id INTEGER PRIMARY KEY,  -- The IFC STEP ID
            global_id TEXT,
            class TEXT,
            predefined_type TEXT,
            name TEXT,
            description TEXT,
            tag TEXT,
            type_id INTEGER REFERENCES entity(id)
        );

        CREATE TABLE specification (
            id INTEGER PRIMARY KEY,
            name TEXT,
            description TEXT,
            instructions TEXT,
            cardinality TEXT,
            applicability TEXT,  -- One human readable clause per line
            status INTEGER,  -- 1 pass, 0 fail, NULL untested
            is_ifc_version INTEGER,
            is_skipped INTEGER,
            total_applicable INTEGER,
            total_applicable_pass INTEGER,
            total_checks INTEGER,
            total_checks_pass INTEGER
        );

        CREATE TABLE requirement (
            id INTEGER PRIMARY KEY,
            specification_id INTEGER REFERENCES specification(id),
            facet_type TEXT,
            label TEXT,
            value TEXT,
            description TEXT,
            instructions TEXT,
            metadata TEXT,  -- The facet as JSON
            status INTEGER,
            total_applicable INTEGER,
            total_pass INTEGER,
            total_fail INTEGER
        );

        -- Failure reasons are interned, as the same reason typically applies
        -- to thousands of entities.
        CREATE TABLE reason (
            id INTEGER PRIMARY KEY,
            text TEXT
        );

        CREATE TABLE applicability (
            specification_id INTEGER REFERENCES specification(id),
            entity_id INTEGER REFERENCES entity(id)
        );

        CREATE TABLE failure (
            requirement_id INTEGER REFERENCES requirement(id),
            entity_id INTEGER REFERENCES entity(id),
            reason_id INTEGER REFERENCES reason(id)
        );

        -- Passes are derived, not stored: an applicable entity with no failure.
        CREATE VIEW passed AS
        SELECT r.id AS requirement_id, a.entity_id AS entity_id
        FROM requirement r
        JOIN applicability a ON a.specification_id = r.specification_id
        LEFT JOIN failure f ON f.requirement_id = r.id AND f.entity_id = a.entity_id
        WHERE f.entity_id IS NULL;
    """

    # Created after the bulk inserts, as maintaining them during is slower.
    INDEXES = """
        CREATE INDEX idx_requirement_specification ON requirement(specification_id);
        CREATE INDEX idx_applicability_specification ON applicability(specification_id);
        CREATE INDEX idx_applicability_entity ON applicability(entity_id);
        CREATE INDEX idx_failure_requirement ON failure(requirement_id);
        CREATE INDEX idx_failure_entity ON failure(entity_id);
    """

    def __init__(self, ids: Ids):
        super().__init__(ids)
        self.reasons: dict[str, int] = {}
        self.entity_ids: set[int] = set()

    def report(self) -> None:
        """Results are written directly to the database in `to_file`, so that
        no intermediate result tree is materialised in memory."""

    def to_string(self) -> str:
        raise NotImplementedError("The Sqlite reporter writes a database, so an output filepath is required")

    def to_file(self, filepath: str) -> None:
        self.reasons.clear()
        self.entity_ids.clear()

        if os.path.exists(filepath):
            os.remove(filepath)

        db = sqlite3.connect(filepath)
        try:
            db.executescript(self.SCHEMA)
            requirement_id = 0
            for specification_id, specification in enumerate(self.ids.specifications):
                requirement_id = self.write_specification(db, specification, specification_id, requirement_id)
                # Commit per specification so that the journal stays bounded.
                db.commit()
            db.executemany("INSERT INTO reason VALUES (?, ?)", ((i, text) for text, i in self.reasons.items()))
            self.write_meta(db)
            db.executescript(self.INDEXES)
            db.commit()
            db.execute("VACUUM")
        finally:
            db.close()

    def write_specification(
        self, db: sqlite3.Connection, specification: Specification, specification_id: int, requirement_id: int
    ) -> int:
        """Write a specification and its requirements. Returns the next free requirement ID."""
        db.executemany(
            "INSERT INTO entity VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            self.iter_entity_rows(specification.applicable_entities),
        )
        db.executemany(
            "INSERT INTO applicability VALUES (?, ?)",
            ((specification_id, e.id()) for e in specification.applicable_entities),
        )

        total_checks_pass = 0
        for requirement in specification.requirements:
            total_checks_pass += self.write_requirement(
                db, specification, specification_id, requirement, requirement_id
            )
            requirement_id += 1

        total_applicable = len(specification.applicable_entities)
        total_checks = total_applicable * len(specification.requirements)
        cardinality = get_cardinality(specification)
        db.execute(
            "INSERT INTO specification VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                specification_id,
                specification.name,
                specification.description,
                specification.instructions,
                cardinality,
                "\n".join(a.to_string("applicability") for a in specification.applicability),
                specification.status,
                specification.is_ifc_version,
                cardinality == "optional" and total_checks == 0,
                total_applicable,
                total_applicable - len(specification.failed_entities),
                total_checks,
                total_checks_pass,
            ),
        )
        return requirement_id

    def write_requirement(
        self,
        db: sqlite3.Connection,
        specification: Specification,
        specification_id: int,
        requirement: Facet,
        requirement_id: int,
    ) -> int:
        """Write a requirement and its failures. Returns the number of passing checks."""
        db.executemany(
            "INSERT INTO failure VALUES (?, ?, ?)",
            ((requirement_id, f["element"].id(), self.get_reason_id(f["reason"])) for f in requirement.failures),
        )
        label, value = get_requirement_label_value(requirement)
        metadata = requirement.asdict("requirement")
        total_applicable = len(specification.applicable_entities)
        total_fail = len(requirement.failures)
        total_pass = total_applicable - total_fail
        db.execute(
            "INSERT INTO requirement VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                requirement_id,
                specification_id,
                type(requirement).__name__,
                label,
                value,
                requirement.to_string("requirement", specification, requirement),
                metadata.get("@instructions"),
                json.dumps(metadata, default=str),
                requirement.status,
                total_applicable,
                total_pass,
                total_fail,
            ),
        )
        return total_pass

    def write_meta(self, db: sqlite3.Connection) -> None:
        (
            total_specifications,
            total_specifications_pass,
            total_requirements,
            total_requirements_pass,
            total_checks,
            total_checks_pass,
        ) = db.execute(
            """
            SELECT
                (SELECT count(*) FROM specification),
                (SELECT count(*) FROM specification WHERE status = 1),
                (SELECT count(*) FROM requirement),
                (SELECT count(*) FROM requirement WHERE status = 1),
                (SELECT coalesce(sum(total_checks), 0) FROM specification),
                (SELECT coalesce(sum(total_checks_pass), 0) FROM specification)
            """
        ).fetchone()
        db.executemany(
            "INSERT INTO meta VALUES (?, ?)",
            (
                ("format", "ifctester"),
                ("schema_version", str(self.SCHEMA_VERSION)),
                ("title", self.ids.info.get("title", "Untitled IDS")),
                ("date", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                ("filepath", self.ids.filepath),
                ("filename", self.ids.filename),
                ("status", str(int(total_specifications_pass == total_specifications))),
                ("total_specifications", str(total_specifications)),
                ("total_specifications_pass", str(total_specifications_pass)),
                ("total_specifications_fail", str(total_specifications - total_specifications_pass)),
                ("total_requirements", str(total_requirements)),
                ("total_requirements_pass", str(total_requirements_pass)),
                ("total_requirements_fail", str(total_requirements - total_requirements_pass)),
                ("total_checks", str(total_checks)),
                ("total_checks_pass", str(total_checks_pass)),
                ("total_checks_fail", str(total_checks - total_checks_pass)),
            ),
        )

    def iter_entity_rows(self, elements: Iterable[ifcopenshell.entity_instance]) -> Iterator[tuple]:
        """Yield rows for elements not yet written, and for the types they occur as."""
        for element in elements:
            element_id = element.id()
            if element_id in self.entity_ids:
                continue
            self.entity_ids.add(element_id)
            element_type = ifcopenshell.util.element.get_type(element)
            type_id = None
            if element_type is not None:
                type_id = element_type.id()
                if type_id not in self.entity_ids:
                    self.entity_ids.add(type_id)
                    yield self.get_entity_row(element_type, None)
            yield self.get_entity_row(element, type_id)

    def get_entity_row(self, element: ifcopenshell.entity_instance, type_id: Optional[int]) -> tuple:
        return (
            element.id(),
            getattr(element, "GlobalId", None),
            element.is_a(),
            ifcopenshell.util.element.get_predefined_type(element),
            getattr(element, "Name", None),
            getattr(element, "Description", None),
            getattr(element, "Tag", None),
            type_id,
        )

    def get_reason_id(self, reason: str) -> int:
        reason_id = self.reasons.get(reason)
        if reason_id is None:
            reason_id = self.reasons[reason] = len(self.reasons)
        return reason_id
