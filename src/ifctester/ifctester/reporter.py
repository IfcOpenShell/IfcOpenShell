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
import os
import re
import sys
import math
import datetime
import ifcopenshell
import ifcopenshell.util.unit
import ifcopenshell.util.element
from .ids import Specification, Ids
from .facet import Facet, FacetFailure
from typing import TypedDict, Union, Literal, Optional

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
    is_ifc_version: bool
    total_applicable: int
    total_applicable_pass: int
    total_applicable_fail: int
    percent_applicable_pass: ResultsPercent
    total_checks: int
    total_checks_pass: int
    total_checks_fail: int
    percent_checks_pass: ResultsPercent
    required: bool
    applicability: list[str]
    requirements: list[ResultsRequirement]


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
    def __init__(self, ids: Ids):
        super().__init__(ids)
        self.results = Results()

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

        return ResultsSpecification(
            name=specification.name,
            description=specification.description,
            instructions=specification.instructions,
            status=specification.status,
            is_ifc_version=specification.is_ifc_version,
            total_applicable=total_applicable,
            total_applicable_pass=total_applicable_pass,
            total_applicable_fail=total_applicable - total_applicable_pass,
            percent_applicable_pass=percent_applicable_pass,
            total_checks=total_checks,
            total_checks_pass=total_checks_pass,
            total_checks_fail=total_checks - total_checks_pass,
            percent_checks_pass=percent_checks_pass,
            required=specification.minOccurs != 0,
            applicability=applicability,
            requirements=requirements,
        )

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
                }
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
        import json

        return json.dumps(self.results, default=self.encode)

    def to_file(self, filepath: str) -> None:
        import json

        with open(filepath, "w", encoding="utf-8") as outfile:
            return json.dump(self.results, outfile, ensure_ascii=False, default=self.encode)

    def encode(self, obj):
        return str(obj)


class Html(Json):
    def __init__(self, ids: Ids):
        self.entity_limit = 100
        super().__init__(ids)

    def report(self) -> None:
        super().report()
        for spec in self.results["specifications"]:
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
        from odf.table import Table, TableRow, TableCell
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
        from odf.table import Table, TableRow, TableCell
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
        import ifcopenshell.util.placement
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
                            unit_scale = ifcopenshell.util.unit.calculate_unit_scale(element.wrapped_data.file)
                        location = [(o * unit_scale) + 5.0 for o in placement[:, 3][:3]]
                        viewpoint = topic.add_viewpoint_from_point_and_guids(np.array(location), element.GlobalId)
                    if element.is_a("IfcElement"):
                        topic.add_viewpoint(element)
        bcfxml.save_project(filepath)
