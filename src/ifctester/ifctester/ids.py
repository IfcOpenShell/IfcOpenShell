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

import os
import datetime
from xmlschema import XMLSchema
from xmlschema import etree_tostring
from xml.etree import ElementTree as ET
from .facet import Entity, Attribute, Classification, Property, PartOf, Material, Restriction


cwd = os.path.dirname(os.path.realpath(__file__))
schema = None


def open(filepath, validate=False):
    if validate:
        get_schema().validate(filepath)
    return Ids().parse(
        get_schema().decode(filepath, strip_namespaces=True, namespaces={"": "http://standards.buildingsmart.org/IDS"})
    )


def get_schema():
    global schema
    if schema is None:
        schema = XMLSchema(os.path.join(cwd, "ids.xsd"))
    return schema


class Ids:
    def __init__(
        self,
        title="Untitled",
        copyright=None,
        version=None,
        description=None,
        author=None,
        date=None,
        purpose=None,
        milestone=None,
    ):
        self.specifications = []
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
        ids_dict = {
            "@xmlns": "http://standards.buildingsmart.org/IDS",
            "@xmlns:xs": "http://www.w3.org/2001/XMLSchema",
            "@xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
            "@xsi:schemaLocation": "http://standards.buildingsmart.org/IDS http://standards.buildingsmart.org/IDS/0.9.6/ids.xsd",
            "info": self.info,
            "specifications": {"specification": []},
        }
        for spec in self.specifications:
            ids_dict["specifications"]["specification"].append(spec.asdict())
        return ids_dict

    def parse(self, data):
        for attribute in ["title", "copyright", "version", "description", "author"]:
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

    def validate(self, ifc_file, filter_version=False):
        for specification in self.specifications:
            specification.reset_status()
            specification.validate(ifc_file, filter_version=filter_version)


class Specification:
    def __init__(
        self,
        name="Unnamed",
        minOccurs=0,
        maxOccurs="unbounded",
        ifcVersion=["IFC2X3", "IFC4"],
        identifier=None,
        description=None,
        instructions=None,
    ):
        self.name = name or "Unnamed"
        self.applicability = []
        self.requirements = []
        self.minOccurs = minOccurs
        self.maxOccurs = maxOccurs
        self.ifcVersion = ifcVersion
        self.identifier = identifier
        self.description = description
        self.instructions = instructions

        self.applicable_entities = []
        self.status = None

    def asdict(self):
        results = {
            "@name": self.name,
            "@ifcVersion": self.ifcVersion,
            "applicability": {},
            "requirements": {},
        }
        for attribute in ["identifier", "description", "instructions", "minOccurs", "maxOccurs"]:
            value = getattr(self, attribute)
            if value is not None:
                results[f"@{attribute}"] = value
        for clause_type in ["applicability", "requirements"]:
            clause = getattr(self, clause_type)
            if not clause:
                continue
            for facet in clause:
                facet_type = type(facet).__name__
                facet_type = facet_type[0].lower() + facet_type[1:]
                if facet_type in results[clause_type]:
                    results[clause_type][facet_type].append(facet.asdict())
                else:
                    results[clause_type][facet_type] = [facet.asdict()]
        return results

    def parse(self, ids_dict):
        self.name = ids_dict.get("@name", "")
        self.description = ids_dict.get("@description", "")
        self.instructions = ids_dict.get("@instructions", "")
        self.minOccurs = ids_dict["@minOccurs"]
        self.maxOccurs = ids_dict["@maxOccurs"]
        self.ifcVersion = ids_dict["@ifcVersion"]
        self.applicability = self.parse_clause(ids_dict["applicability"]) if "applicability" in ids_dict else []
        self.requirements = self.parse_clause(ids_dict["requirements"]) if "requirements" in ids_dict else []
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
        self.failed_entities = set()
        for facet in self.requirements:
            facet.status = None
            facet.failed_entities.clear()
        self.status = None

    def validate(self, ifc_file, filter_version=False):
        if filter_version and ifc_file.schema not in self.ifcVersion:
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
                if not bool(result):
                    self.failed_entities.add(element)
                    facet.failed_entities.append(element)
                    facet.failed_reasons.append(str(result))

        for facet in self.requirements:
            if facet.minOccurs != 0:
                facet.status = not bool(facet.failed_entities)
            elif facet.minOccurs == 0 and facet.maxOccurs != 0:
                facet.status = True
            elif facet.maxOccurs == 0:
                facet.status = bool(facet.failed_entities)

        self.status = True
        if self.minOccurs != 0:
            if not self.applicable_entities:
                self.status = False
                for facet in self.requirements:
                    facet.status = False
            elif self.failed_entities:
                self.status = False
        elif self.minOccurs == 0 and self.maxOccurs != 0: 
            if self.failed_entities:
                self.status = False
        elif self.maxOccurs == 0:
            if (len(self.applicable_entities)) > 0 and len(self.requirements) == 0:
                self.status = False
            if (len(self.applicable_entities)) > 0 and (len(self.applicable_entities) - len(self.failed_entities)) > 0:
                self.status = False

    def get_usage(self):
        if self.minOccurs != 0:
            return "required"
        elif self.minOccurs == 0 and self.maxOccurs != 0:
            return "optional"
        elif self.maxOccurs == 0:
            return "prohibited"
