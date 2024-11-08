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
import datetime
import ifcopenshell
from xmlschema.validators.exceptions import XMLSchemaValidationError
from xmlschema import XMLSchema
from xmlschema import etree_tostring
from xml.etree import ElementTree as ET
from .facet import (
    Facet,
    Entity,
    Attribute,
    Classification,
    Property,
    PartOf,
    Material,
    Restriction,
    get_pset,
    get_psets,
    Cardinality,
    FacetFailure,
)
from typing import List, Optional, Union, overload, Literal

cwd = os.path.dirname(os.path.realpath(__file__))
schema = None


class IdsXmlValidationError(Exception):
    def __init__(self, xml_error: XMLSchemaValidationError, message: str):
        self.xml_error = xml_error
        super().__init__(message)


@overload
def open(filepath: str, validate: Literal[False] = False) -> Ids: ...
@overload
def open(filepath: str, validate: Literal[True]) -> None: ...
def open(filepath: str, validate=False) -> Union[Ids, None]:
    try:
        if validate:
            get_schema().validate(filepath)
        decode = get_schema().decode(
            filepath, strip_namespaces=True, namespaces={"": "http://standards.buildingsmart.org/IDS"}
        )
    except XMLSchemaValidationError as e:
        raise IdsXmlValidationError(e, f"Provided .ids file ({filepath}) appears to be invalid. See details above.")
    return Ids().parse(decode)


def get_schema():
    global schema
    if schema is None:
        schema = XMLSchema(os.path.join(cwd, "ids.xsd"))
    return schema


class Ids:
    def __init__(
        self,
        title: Optional[str] = "Untitled",
        copyright=None,
        version=None,
        description=None,
        author=None,
        date=None,
        purpose=None,
        milestone=None,
    ):
        # Not part of the IDS spec, but very useful in practice
        self.filepath: Optional[str] = None
        self.filename: Optional[str] = None

        self.specifications: List[Specification] = []
        self.info = {}
        self.info["title"] = title or "Untitled"
        if copyright:
            self.info["copyright"] = copyright
        if version:
            self.info["version"] = version
        if description:
            self.info["description"] = description
        if author and "@" in author:
            self.info["author"] = author
        if date:
            try:
                self.info["date"] = datetime.date.fromisoformat(date).isoformat()
            except ValueError:
                pass
        if purpose:
            self.info["purpose"] = purpose
        if milestone:
            self.info["milestone"] = milestone

    def asdict(self):
        info = {}
        for attr in ["title", "copyright", "version", "description", "author", "date", "purpose", "milestone"]:
            if attr in self.info:
                info[attr] = self.info[attr]
        ids_dict = {
            "@xmlns": "http://standards.buildingsmart.org/IDS",
            "@xmlns:xs": "http://www.w3.org/2001/XMLSchema",
            "@xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
            "@xsi:schemaLocation": "http://standards.buildingsmart.org/IDS http://standards.buildingsmart.org/IDS/1.0/ids.xsd",
            "info": info,
            "specifications": {"specification": []},
        }
        for spec in self.specifications:
            ids_dict["specifications"]["specification"].append(spec.asdict())
        return ids_dict

    def parse(self, data):
        for attribute in ["title", "copyright", "version", "description", "author", "date", "purpose", "milestone"]:
            value = data["info"].get(attribute)
            if value:
                self.info[attribute] = value
        xml_specs = data["specifications"]["specification"]
        if not isinstance(xml_specs, list):
            xml_specs = [xml_specs]
        for xml_spec in xml_specs:
            spec = Specification()
            spec.parse(xml_spec)
            self.specifications.append(spec)
        return self

    def to_string(self):
        ns = {"": "http://standards.buildingsmart.org/IDS"}
        return etree_tostring(get_schema().encode(self.asdict()), namespaces=ns)

    def to_xml(self, filepath="output.xml"):
        ET.register_namespace("", "http://standards.buildingsmart.org/IDS")
        ET.ElementTree(get_schema().encode(self.asdict())).write(filepath, encoding="utf-8", xml_declaration=True)
        return get_schema().is_valid(filepath)

    def validate(
        self, ifc_file: ifcopenshell.file, should_filter_version: bool = False, filepath: Optional[str] = None
    ) -> None:
        if filepath:
            self.filepath = filepath
            self.filename = os.path.basename(filepath)
        else:
            self.filepath = self.filename = None
        get_pset.cache_clear()
        get_psets.cache_clear()
        for specification in self.specifications:
            specification.reset_status()
            specification.check_ifc_version(ifc_file)
            specification.validate(ifc_file, should_filter_version=should_filter_version)


class Specification:
    def __init__(
        self,
        name="Unnamed",
        minOccurs=0,
        maxOccurs="unbounded",
        ifcVersion=["IFC2X3", "IFC4", "IFC4X3_ADD2"],
        identifier=None,
        description=None,
        instructions=None,
    ):
        self.name = name or "Unnamed"
        self.applicability: List[Facet] = []
        self.requirements: List[Facet] = []
        self.minOccurs: Union[int, str] = minOccurs
        self.maxOccurs: Union[int, str] = maxOccurs
        self.ifcVersion = ifcVersion
        self.identifier = identifier
        self.description = description
        self.instructions = instructions

        self.applicable_entities: list[ifcopenshell.entity_instance] = []
        self.passed_entities: set[ifcopenshell.entity_instance] = set()
        self.failed_entities: set[ifcopenshell.entity_instance] = set()
        self.status = None
        self.is_ifc_version = None

    def asdict(self):
        results = {
            "@name": self.name,
            "@ifcVersion": self.ifcVersion,
            "applicability": {},
            "requirements": {},
        }
        for attribute in ["identifier", "description", "instructions"]:
            value = getattr(self, attribute)
            if value is not None:
                results[f"@{attribute}"] = value
        for clause_type in ["applicability", "requirements"]:
            clause = getattr(self, clause_type)
            if not clause:
                continue
            facets = {}
            for facet in clause:
                facet_type = type(facet).__name__
                facet_type = facet_type[0].lower() + facet_type[1:]
                facets.setdefault(facet_type, []).append(facet.asdict(clause_type))
            # Canonicalise ordering as per XSD requirements
            for facet_type in ("entity", "partOf", "classification", "attribute", "property", "material"):
                if facet_type in facets:
                    results[clause_type][facet_type] = facets[facet_type]
            if clause_type == "applicability":
                for attribute in ["minOccurs", "maxOccurs"]:
                    value = getattr(self, attribute)
                    if value is not None:
                        results[clause_type][f"@{attribute}"] = value
        return results

    def parse(self, ids_dict):
        self.name = ids_dict.get("@name", "")
        self.description = ids_dict.get("@description", "")
        self.instructions = ids_dict.get("@instructions", "")
        self.minOccurs = ids_dict.get("applicability", {}).get("@minOccurs", 0)
        self.maxOccurs = ids_dict.get("applicability", {}).get("@maxOccurs", "unbounded")
        self.ifcVersion = ids_dict["@ifcVersion"]
        self.applicability = (
            self.parse_clause(ids_dict["applicability"]) if ids_dict.get("applicability", None) is not None else []
        )
        self.requirements = (
            self.parse_clause(ids_dict["requirements"]) if ids_dict.get("requirements", None) is not None else []
        )
        return self

    def parse_clause(self, clause):
        results = []
        for name, facets in clause.items():
            if name not in ["entity", "attribute", "classification", "partOf", "property", "material"]:
                continue
            if not isinstance(facets, list):
                facets = [facets]
            for facet_xml in facets:
                name_capitalised = name[0].upper() + name[1:]
                facet = globals()[name_capitalised]().parse(facet_xml)
                results.append(facet)
        return results

    def reset_status(self):
        self.applicable_entities.clear()
        self.passed_entities: set[ifcopenshell.entity_instance] = set()
        self.failed_entities: set[ifcopenshell.entity_instance] = set()
        for facet in self.requirements:
            facet.status = None
            facet.failures.clear()
        self.status = None

    def check_ifc_version(self, ifc_file: ifcopenshell.file) -> bool:
        self.is_ifc_version = ifc_file.schema_identifier in self.ifcVersion
        return self.is_ifc_version

    def validate(self, ifc_file: ifcopenshell.file, should_filter_version: bool = False) -> None:
        if should_filter_version and not self.is_ifc_version:
            return

        elements = None

        # This is a broadphase filter of applicability. We almost never want to
        # test every single class in an IFC model.
        for i, facet in enumerate(self.applicability):
            elements = facet.filter(ifc_file, elements)

        for element in elements or []:
            is_applicable = True
            for facet in self.applicability:
                if isinstance(facet, Entity):
                    continue
                if not bool(facet(element)):
                    is_applicable = False
                    break
            if not is_applicable:
                continue
            self.applicable_entities.append(element)
            for facet in self.requirements:
                result = facet(element)
                is_pass = bool(result)
                if self.maxOccurs != 0:  # This is a required or optional specification
                    if is_pass:
                        self.passed_entities.add(element)
                        facet.passed_entities.add(element)
                    else:
                        self.failed_entities.add(element)
                        facet.failures.append(FacetFailure(element=element, reason=str(result)))
                else:  # This is a prohibited specification
                    if is_pass:
                        self.failed_entities.add(element)
                        facet.failures.append(FacetFailure(element=element, reason=str(result)))
                    else:
                        self.passed_entities.add(element)
                        facet.passed_entities.add(element)

        self.status = True
        for facet in self.requirements:
            facet.status = not bool(facet.failures)
            if not facet.status:
                self.status = False

        if self.minOccurs != 0:  # Required specification
            if not self.applicable_entities:
                self.status = False
                for facet in self.requirements:
                    facet.status = False
        elif self.maxOccurs == 0:  # Prohibited specification
            if self.applicable_entities and not self.requirements:
                self.status = False

    def get_usage(self) -> Cardinality:
        if self.minOccurs != 0:
            return "required"
        elif self.minOccurs == 0 and self.maxOccurs != 0:
            return "optional"
        elif self.maxOccurs == 0:
            return "prohibited"
        return "required"  # Fallback

    def set_usage(self, usage: Cardinality) -> None:
        if usage == "optional":
            self.minOccurs = 0
            self.maxOccurs = "unbounded"
        elif usage == "prohibited":
            self.minOccurs = 0
            self.maxOccurs = 0
        else:  # required
            self.minOccurs = 1
            self.maxOccurs = "unbounded"
