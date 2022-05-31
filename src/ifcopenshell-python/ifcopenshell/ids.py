# IDS - Information Delivery Specification.
# Copyright (C) 2021 Artur Tomczak <artomczak@gmail.com>, Thomas Krijnen <mail@thomaskrijnen.com>, Dion Moult <dion@thinkmoult.com>
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

import os
import re
import logging
import numpy as np
import datetime
import ifcopenshell.util.unit
import ifcopenshell.util.element
import ifcopenshell.util.placement
import ifcopenshell.util.classification
from bcf.v2.bcfxml import BcfXml
from bcf.v2 import data as bcf
from xmlschema import XMLSchema
from xmlschema import etree_tostring
from xmlschema.validators import identities
from xml.etree import ElementTree as ET


# http://standards.buildingsmart.org/IDS/ids_05.xsd
cwd = os.path.dirname(os.path.realpath(__file__))
ids_schema = XMLSchema(os.path.join(cwd, "ids.xsd"))


def error(msg):
    raise Exception(msg)


class ids:
    """Represents the XML root <ids> node and its <specification> childNodes."""

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
        """Create an IDS object.

        :param title: Name of the IDS file, defaults to None
        :type title: str, required
        :param copyright:, defaults to None
        :type copyright: str, optional
        :param version: IDS file version, defaults to None
        :type version: float, optional
        :param description:, defaults to None
        :type description: str, optional
        :param author: Email of the IDS author, defaults to None
        :type author: str, optional
        :param date: Date in 'yyyy-mm-dd' format, defaults to current date
        :type date: str, optional
        :param purpose:, defaults to None
        :type purpose: str, optional
        :param milestone:, defaults to None
        :type milestone: str, optional
        """
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
        """Converts object to a dictionary, adding required attributes.

        :return: Xmlschema compliant dictionary.
        :rtype: dict
        """
        ids_dict = {
            "@xmlns": "http://standards.buildingsmart.org/IDS",
            "@xmlns:xs": "http://www.w3.org/2001/XMLSchema",
            "@xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
            "@xsi:schemaLocation": "http://standards.buildingsmart.org/IDS/ids_05.xsd",
            "info": self.info,
            "specifications": {"specification": []},
        }
        for spec in self.specifications:
            ids_dict["specifications"]["specification"].append(spec.asdict())
        return ids_dict

    def to_string(self, ids_schema=ids_schema):
        """Convert IDS object to XML string

        :param ids_schema: XML Schema for an IDS file, defaults to ids_schema object from buildingSMART
        :type ids_schema: XMLschema, optional
        :return: The contents of the XML data in string form
        :rtype: string
        """
        ns = {"": "http://standards.buildingsmart.org/IDS"}
        return etree_tostring(ids_schema.encode(self.asdict()), namespaces=ns)

    def to_xml(self, filepath="output.xml", ids_schema=ids_schema):
        """Writes IDS object to an XML file.

        :param filepath: Path to the file, defaults to "output.xml"
        :type filepath: str, optional
        :param ids_schema: XML Schema for an IDS file, defaults to ids_schema object from buildingSMART
        :type ids_schema: XMLschema, optional
        :return: Result of the newly created file validation against the schema.
        :rtype: bool
        """
        ET.register_namespace("", "http://standards.buildingsmart.org/IDS")
        ET.ElementTree(ids_schema.encode(self.asdict())).write(filepath, encoding="utf-8", xml_declaration=True)
        return ids_schema.is_valid(filepath)

    @staticmethod
    def open(filepath, ids_schema=ids_schema):
        """Use to open ids.xml files

        :param filepath: ids file path
        :type filepath: str
        :param ids_schema: XML Schema for an IDS file, defaults to ids_schema object from buildingSMART
        :type ids_schema: XMLschema, optional
        :return: IDS file as a python object
        :rtype: ids object
        """

        ids_schema.validate(filepath)
        ids_content = ids_schema.decode(
            filepath, strip_namespaces=True, namespaces={"": "http://standards.buildingsmart.org/IDS"}
        )
        ids_file = ids()
        ids_file.specifications = [specification.parse(s) for s in ids_content["specifications"]["specification"]]
        return ids_file

    def validate2(self, ifc_file):
        """Use to validate IFC model against IDS specifications.

        :param ifc_file: path to ifc file
        :type ifc_file: str
        :param logger: Logging object with handlers, defaults to None
        :type logger: logging, optional
        """
        for specification in self.specifications:
            specification.applicable_entities.clear()
            specification.failed_entities.clear()
            specification.status = None
        for element in ifc_file:
            for specification in self.specifications:
                if not specification.applicability(element, None):
                    continue
                specification.applicable_entities.append(element)
                if specification.requirements(element, None):
                    specification.status = True
                else:
                    specification.status = False
                    specification.failed_entities.append(element)

    def validate(self, ifc_file, logger=None):
        """Use to validate IFC model against IDS specifications.

        :param ifc_file: path to ifc file
        :type ifc_file: str
        :param logger: Logging object with handlers, defaults to None
        :type logger: logging, optional
        """
        if not isinstance(logger, logging.Logger):
            logger = logging.getLogger("IDS_Logger")
            logging.basicConfig(level=logging.INFO, format="%(message)s")
            logger.setLevel(logging.INFO)

        # Consider other way around: for elem, for spec so we can see if an element pass all IDSes?
        for spec in self.specifications:
            self.ifc_applicable = 0
            self.ifc_passed = 0
            for elem in ifc_file:
                apply, comply = spec(elem, logger)
                if apply:
                    self.ifc_applicable += 1
                if comply:
                    self.ifc_passed += 1
            if self.ifc_applicable == 0:
                if spec.minOccurs != "0":
                    logger.error("No applicable elements found. Minimum 1 applicable element required.")
                else:
                    logger.debug("No applicable elements found. None required.")

            try:
                percentage = self.ifc_passed / self.ifc_applicable * 100
            except ZeroDivisionError:
                percentage = 0

            logger.debug(
                "Out of %s IFC elements, %s were applicable and %s of them passed (%s)."
                % (
                    len(ifc_file.by_type("IfcProduct")),
                    self.ifc_applicable,
                    self.ifc_passed,
                    str(percentage) + "%",
                )
            )
        for h in logger.handlers:
            h.flush()


class specification:
    """Represents the XML <specification> node and its two children <applicability> and <requirements>"""

    def __init__(
        self,
        name="Unnamed",
        minOccurs=None,
        maxOccurs=None,
        ifcVersion=["IFC2X3", "IFC4"],
        identifier=None,
        description=None,
        instructions=None,
    ):
        """Create a specification to be added in ids.

        :param name: Name describing the specification to a contract reader
        :type name: str
        :param minOccurs: The minimum total entities that should pass as an integer >= 0
        :type minOccurs: str, optional
        :param maxOccurs: The maximum total entities that should pass as an integer >= 0 or "unbounded"
        :type maxOccurs: str, optional
        """
        self.name = name or "Unnamed"
        self.applicability = None
        self.requirements = None
        self.minOccurs = minOccurs
        self.maxOccurs = maxOccurs
        self.ifcVersion = ifcVersion
        self.identifier = identifier
        self.description = description
        self.instructions = instructions

        self.applicable_entities = []
        self.failed_entities = []
        self.status = None

    def asdict(self):
        """Converts object to a dictionary, adding required attributes.

        :return: Xmlschema compliant dictionary.
        :rtype: dict
        """
        # if older python collections.OrderedDict()
        results = {
            "@name": self.name,
            "@ifcVersion": self.ifcVersion,
            "applicability": {},
            "requirements": {},
        }
        for attribute in ["identifier", "description", "instructions", "minOccurs", "maxOccurs"]:
            value = getattr(self, attribute)
            if value:
                results[f"@{attribute}"] = value
        for clause_type in ["applicability", "requirements"]:
            clause = getattr(self, clause_type)
            if not clause:
                continue
            for fac in clause.terms:
                fclass = type(fac).__name__
                if fclass in results[clause_type]:
                    results[clause_type][fclass].append(fac.asdict())
                else:
                    results[clause_type][fclass] = [fac.asdict()]
        return results

    @staticmethod
    def parse(ids_dict):
        """Parse xml specification to python object.

        :param ids_dict:
        :type ids_dict: dict
        """

        def parse_rules(dict):
            facet_names = list(dict.keys())
            facet_properties = [v[0] if isinstance(v, list) else v for v in list(dict.values())]
            classes = [meta_facet.facets.__getitem__(f) for f in facet_names]
            facets = [cls(n) for cls, n in zip(classes, facet_properties)]
            return facets

        spec = specification()
        try:
            spec.name = ids_dict["@name"]
        except KeyError:
            spec.name = ""
        spec.minOccurs = ids_dict["@minOccurs"]
        spec.maxOccurs = ids_dict["@maxOccurs"]
        spec.ifcVersion = ids_dict["@ifcVersion"]
        spec.applicability = boolean_and(parse_rules(ids_dict["applicability"]))
        spec.requirements = boolean_and(parse_rules(ids_dict["requirements"]))
        return spec

    def add_applicability(self, facet):
        """Applicability specifies a filter for IFC entities are to be validated.

        At least one filter must be added.

        :param facet: any of entity|attribute|classification|property|material
        :type facet: facet

        Example::

            specs = ids.ids()
            spec = ids.specification(name="Test_Specification")
            spec.add_applicability(ids.entity.create(name="IfcWall"))
            specs.specifications.append(spec)
        """
        if self.applicability:
            self.applicability = boolean_and(self.applicability.terms + [facet])
        else:
            self.applicability = boolean_and([facet])

    def add_requirement(self, facet):
        """A requirement specifies data to be checked for all applicable entities.

        At least one requirement must be added.

        :param facet: any of entity|attribute|classification|property|material|partOf
        :type facet: facet
        """
        if self.requirements:
            self.requirements = boolean_and(self.requirements.terms + [facet])
        else:
            self.requirements = boolean_and([facet])

    def __call__(self, inst, logger):
        """When specification is called on an ifc instance, it validates against applicability and requirements.

        :param inst: IFC entity element
        :type inst: IFC entity
        :param logger: Logging object
        :type logger: logging
        :return: results of validation on applicability and requirements
        :rtype: [bool,bool]
        """
        if self.applicability(inst, logger):
            valid = self.requirements(inst, logger)

            if valid:
                logger.info(
                    {
                        "guid": inst.GlobalId,
                        "result": valid.success,
                        "sentence": str(self)
                        + ".\n"
                        + inst.is_a()
                        + " '"
                        + str(inst.Name)
                        + "' (#"
                        + str(inst.id())
                        + ") has "
                        + str(valid)
                        + " so is compliant",
                        "ifc_element": inst,
                    }
                )
                return True, True
            else:
                # BUG "has does not have"
                logger.error(
                    {
                        "guid": inst.GlobalId,
                        "result": valid.success,
                        "sentence": str(self)
                        + ".\n"
                        + inst.is_a()
                        + " '"
                        + str(inst.Name)
                        + "' (#"
                        + str(inst.id())
                        + ") has "
                        + str(valid)
                        + " so is not compliant",
                        "ifc_element": inst,
                    }
                )
                return True, False
        else:
            return False, False

    def __str__(self):
        """Represent the specification in human readable sentence.

        :return: sentence
        :rtype: str
        """
        return "Given an instance with %(applicability)s\nWe expect %(requirements)s" % self.__dict__


class facet_evaluation:
    """The evaluation of a facet with data from IFC. Converts to bool and has a human readable string format."""

    def __init__(self, success, str):
        self.success = success
        self.str = str

    def __bool__(self):
        return self.success

    def __str__(self):
        return self.str


class meta_facet(type):
    """A metaclass for automatically registering facets in a map to be instantiated based on XML tagnames."""

    facets = {}

    def __new__(cls, clsname, bases, attrs):
        newclass = super(meta_facet, cls).__new__(cls, clsname, bases, attrs)
        meta_facet.facets[clsname] = newclass
        return newclass


class facet(metaclass=meta_facet):
    """
    The base class for IDS facets. IDS facets are functors constructed from
    XML nodes that return True or False. A getattr method is provided for
    conveniently extracting XML child node text content.
    Use child classes instead: entity, classification, property and material.
    """

    def __init__(self, node=None):
        if node:
            self.node = node

    def __getattr__(self, attr):

        if attr in getattr(self, "node", None):
            v = self.node[attr]

            # BUG list of dictionaries should not happen
            if isinstance(v, list):
                v = v[0]

            if "simpleValue" in list(v):
                return v["simpleValue"]
            elif "restriction" in list(v):
                return restriction.parse(v["restriction"][0])
                # TODO handle more than one restriction: return [restriction(r) for r in v["restriction"]]
            else:
                raise Exception("Unknown value declaration.")
        # except KeyError:
        else:
            return None

    def __iter__(self):
        for k in self.parameters:
            yield k, getattr(self, k)

    def __str__(self):
        di = dict(list(self))
        for k, v in di.items():
            if isinstance(v, str) and not len(v):
                di[k] = "not specified"
        return self.message % di


class entity(facet):
    """The IDS entity facet currently *with* inheritance"""

    parameters = ["name", "predefinedType", "instructions"]

    @staticmethod
    def create(name=None, predefinedType=None, instructions=None):
        """Create an entity facet that can be added to applicability or requirements of IDS specification.

        :param name: IFC entity name that is required. e.g. IfcWall, defaults to None
        :type name: str, optional
        :param predefinedType: name of the predefined type, defaults to None
        :type predefinedType: str, optional
        :return: entity object
        :rtype: entity
        """

        inst = entity()
        inst.name = name
        inst.predefinedType = predefinedType
        inst.instructions = instructions
        return inst

    def asdict(self):
        """Converts object to a dictionary, adding required attributes.

        :return: Xmlschema compliant dictionary.
        :rtype: dict
        """
        results = {"name": parameter_asdict(self.name)}
        if self.predefinedType:
            results["predefinedType"] = parameter_asdict(self.predefinedType)
        if self.instructions:
            results["@instructions"] = self.instructions
        return results

    def __call__(self, inst, logger=None):
        """Validate an entity.

        Subclasses are not considered to pass the requirements. PredefinedType
        checks support userdefined types for both element and type elements.

        :param inst: IFC entity element
        :type inst: IFC entity
        :param logger: Logging object
        :type logger: logging
        :return: result of the validation as bool and message
        :rtype: facet_evaluation(bool, str)
        """
        is_pass = inst.is_a().upper() == self.name
        if is_pass and self.predefinedType:
            predefined_type = ifcopenshell.util.element.get_predefined_type(inst)
            is_pass = predefined_type == self.predefinedType

        if self.predefinedType:
            self.message = "an entity name '%(name)s' of predefined type '%(predefinedType)s'"
            return facet_evaluation(is_pass, self.message % {"name": inst.is_a(), "predefinedType": predefined_type})
        else:
            self.message = "an entity name '%(name)s'"
            return facet_evaluation(is_pass, self.message % {"name": inst.is_a()})


class attribute(facet):
    """The IDS attribute facet"""

    parameters = ["name", "value", "minOccurs", "maxOccurs", "instructions"]

    @staticmethod
    def create(name="Name", value=None, minOccurs=None, maxOccurs=None, instructions=None):
        """Create an attribute facet that can be added to applicability or requirements of IDS specification.

        :param name: Attribute name, such as "Description"
        :type name: str
        :param value: Attribute value, with type being strictly checked
        :type value: str, optional
        :param minOccurs: The minimum total entities that should pass as an integer >= 0
        :type minOccurs: str, optional
        :param maxOccurs: The maximum total entities that should pass as an integer >= 0 or "unbounded"
        :type maxOccurs: str, optional
        :param instructions: Instructions as a guide for model authors when reading the requirements
        :type instructions: str, optional
        :return: entity object
        :rtype: entity
        """

        inst = attribute()
        inst.name = name
        inst.value = value
        inst.minOccurs = minOccurs
        inst.maxOccurs = maxOccurs
        inst.instructions = instructions
        return inst

    def asdict(self):
        """Converts object to a dictionary, adding required attributes.

        :return: Xmlschema compliant dictionary.
        :rtype: dict
        """
        results = {"name": parameter_asdict(self.name)}
        if self.value:
            results["value"] = parameter_asdict(self.value)
        if self.minOccurs:
            results["@minOccurs"] = self.minOccurs
        if self.maxOccurs:
            results["@maxOccurs"] = self.maxOccurs
        if self.instructions:
            results["@instructions"] = self.instructions
        return results

    def __call__(self, inst, logger=None):
        """Validate an ifc instance.

        :param inst: IFC entity element
        :type inst: IFC entity
        :param logger: Logging object
        :type logger: logging
        :return: result of the validation as bool and message
        :rtype: facet_evaluation(bool, str)
        """

        def get_values(element, name):
            if isinstance(name, str):
                return [getattr(element, name, None)]
            return [v for k, v in element.get_info().items() if k == name]

        element_type = ifcopenshell.util.element.get_type(inst)

        if isinstance(self.name, str):
            type_value = getattr(element_type, self.name, None) if element_type else None
            occurrence_value = getattr(inst, self.name, None)
            names = [self.name]
            values = [occurrence_value if occurrence_value is not None else type_value]
        else:
            if element_type:
                info = element_type.get_info()
                info.update({k: v for k, v in inst.get_info().items() if v is not None})
            else:
                info = inst.get_info()
            names = []
            values = []
            for k, v in info.items():
                if k == self.name:
                    names.append(k)
                    values.append(v)

        is_pass = bool(values)

        if is_pass:
            for i, value in enumerate(values):
                if value is None:
                    is_pass = False
                elif value == "":
                    is_pass = False
                elif value == tuple():
                    is_pass = False
                elif (
                    inst.attribute_type(inst.wrapped_data.get_argument_index(names[i])) == "LOGICAL"
                    and value == "UNKNOWN"
                ):
                    is_pass = False
                if not is_pass:
                    break

        if is_pass and self.value:
            is_pass = all([v == self.value for v in values])

        if self.value:
            self.message = "foo"
            return facet_evaluation(is_pass, f"an entity with {self.name} set to something wrong")
        else:
            return facet_evaluation(is_pass, f"an entity with {self.name}")


class classification(facet):
    """
    The IDS classification facet by traversing the HasAssociations inverse attribute
    """

    parameters = ["system", "value", "uri", "minOccurs", "maxOccurs" "instructions"]
    message = "sclassification reference %(value)s from '%(system)s'"

    @staticmethod
    def create(value=None, system=None, uri=None, minOccurs=None, maxOccurs=None, instructions=None):
        """Create a classification facet that can be added to applicability or requirements of IDS specification.

        :param value: Value that is required. Could be alphanumeric or restriction object, defaults to None
        :type value: restriction|alphanumeric, optional
        :param system: System that is required. Could be alphanumeric or restriction object, defaults to None
        :type system: restriction|alphanumeric, optional
        :param minOccurs: The minimum total entities that should pass as an integer >= 0
        :type minOccurs: str, optional
        :param maxOccurs: The maximum total entities that should pass as an integer >= 0 or "unbounded"
        :type maxOccurs: str, optional
        :return: classification object
        :rtype: classification
        """
        inst = classification()
        inst.value = value
        inst.system = system
        inst.uri = uri
        inst.minOccurs = minOccurs
        inst.maxOccurs = maxOccurs
        inst.instructions = instructions
        return inst

    def asdict(self):
        """Converts object to a dictionary, adding required attributes.

        :return: Xmlschema compliant dictionary.
        :rtype: dict
        """
        results = {}
        if self.value:
            results["value"] = parameter_asdict(self.value)
        if self.system:
            results["system"] = parameter_asdict(self.system)
        if self.uri:
            results["@uri"] = self.uri
        if self.minOccurs:
            results["@minOccurs"] = self.minOccurs
        if self.maxOccurs:
            results["@maxOccurs"] = self.maxOccurs
        if self.instructions:
            results["@instructions"] = self.instructions
        return results

    def __call__(self, inst, logger=None):
        """Validate an ifc instance against that classification facet.

        :param inst: IFC entity element
        :type inst: IFC entity
        :param logger: Logging object
        :type logger: logging
        :return: result of the validation as bool and message
        :rtype: facet_evaluation(bool, str)
        """
        leaf_references = ifcopenshell.util.classification.get_references(inst)

        references = leaf_references.copy()
        for leaf_reference in leaf_references:
            references.update(ifcopenshell.util.classification.get_inherited_references(leaf_reference))

        is_pass = bool(references)
        if is_pass and self.value:
            is_pass = any(
                [self.value == getattr(r, "Identification", getattr(r, "ItemReference", None)) for r in references]
            )
        if is_pass and self.system:
            is_pass = any(
                [self.system == ifcopenshell.util.classification.get_classification(r).Name for r in references]
            )

        if references:
            return facet_evaluation(
                is_pass,
                self.message
                % {
                    "system": list(references)[0][0],
                    "value": list(references)[0][1],
                },  # TODO Fix this 0 index reference assumption when I refactor out the messages
            )
        else:
            return facet_evaluation(False, "does not have classification reference")


class partOf(facet):
    """
    The IDS partOf facet by traversing the _______ inverse attribute
    """

    parameters = ["entity"]
    message = "relation as part of %(entity)s"

    @staticmethod
    def create(entity="IfcSystem"):
        """Create a partOf facet that can be added to applicability or requirements of IDS specification.

        :param entity: Entity that should contain this object. Could be alphanumeric or restriction object, defaults to None
        :type entity: restriction|alphanumeric, optional
        :return: partOf object
        :rtype: partOf
        """

        inst = partOf()
        inst.entity = entity
        return inst

    def asdict(self):
        """Converts object to a dictionary, adding required attributes.

        :return: Xmlschema compliant dictionary.
        :rtype: dict
        """
        return {"@entity": self.entity}

    def __call__(self, inst, logger=None):
        """Validate an ifc instance against that partOf facet.

        :param inst: IFC entity element
        :type inst: IFC entity
        :param logger: Logging object
        :type logger: logging
        :return: result of the validation as bool and message
        :rtype: facet_evaluation(bool, str)
        """
        if self.entity == "IfcElementAssembly":
            is_pass = False
            aggregate = ifcopenshell.util.element.get_aggregate(inst)
            while aggregate is not None:
                if aggregate.is_a() == "IfcElementAssembly":
                    is_pass = True
                    break
                aggregate = ifcopenshell.util.element.get_aggregate(aggregate)
        else:
            is_pass = False
            for rel in getattr(inst, "HasAssignments", []) or []:
                if rel.is_a("IfcRelAssignsToGroup") and rel.RelatingGroup.is_a(self.entity):
                    is_pass = True

        return facet_evaluation(is_pass, "is not a part of")


class property(facet):
    """
    The IDS property facet implemented using `ifcopenshell.util.element`
    """

    parameters = ["name", "propertySet", "value"]
    message = "property '%(name)s' in '%(propertySet)s' with a value %(value)s"

    @staticmethod
    def create(
        propertySet="Property_Set",
        name="PropertyName",
        value=None,
        measure=None,
        uri=None,
        minOccurs=None,
        maxOccurs=None,
        instructions=None,
    ):
        """Create a property facet that can be added to applicability or requirements of IDS specification.

        :param propertySet: Propertyset that is required. Could be alphanumeric or restriction object, defaults to None
        :type propertySet: restriction|alphanumeric, optional
        :param name: Name that is required. Could be alphanumeric or restriction object, defaults to None
        :type name: restriction|alphanumeric, optional
        :param value: Value that is required. Could be alphanumeric or restriction object, defaults to None
        :type value: restriction|alphanumeric, optional
        :param minOccurs: The minimum total entities that should pass as an integer >= 0
        :type minOccurs: str, optional
        :param maxOccurs: The maximum total entities that should pass as an integer >= 0 or "unbounded"
        :type maxOccurs: str, optional
        :return: property object
        :rtype: property
        """
        inst = property()
        inst.propertySet = propertySet
        inst.name = name
        inst.value = value
        inst.measure = measure
        inst.uri = uri
        inst.minOccurs = minOccurs
        inst.maxOccurs = maxOccurs
        inst.instructions = instructions
        return inst

    def asdict(self):
        """Converts object to a dictionary, adding required attributes.

        :return: Xmlschema compliant dictionary.
        :rtype: dict
        """
        results = {
            "propertySet": parameter_asdict(self.propertySet),
            "name": parameter_asdict(self.name),
        }
        if self.value:
            results["value"] = parameter_asdict(self.value)
        if self.measure:
            results["@measure"] = self.measure
        if self.uri:
            results["@uri"] = self.uri
        if self.minOccurs:
            results["@minOccurs"] = self.minOccurs
        if self.maxOccurs:
            results["@maxOccurs"] = self.maxOccurs
        if self.instructions:
            results["@instructions"] = self.instructions
        # TODO '@href': 'http://identifier.buildingsmart.org/uri/buildingsmart/ifc-4.3/prop/FireRating', #https://identifier.buildingsmart.org/uri/something
        return results

    def __call__(self, inst, logger=None):
        """Validate an ifc instance against that property facet.

        :param inst: IFC entity element
        :type inst: IFC entity
        :param logger: Logging object
        :type logger: logging
        :return: result of the validation as bool and message
        :rtype: facet_evaluation(bool, str)
        """
        all_psets = ifcopenshell.util.element.get_psets(inst)

        if isinstance(self.propertySet, str):
            pset = all_psets.get(self.propertySet, None)
            psets = {self.propertySet: pset} if pset else {}
        else:
            psets = {k: v for k, v in all_psets.items() if k == self.propertySet}

        is_pass = bool(psets)

        if is_pass:
            props = {}
            for pset_name, pset_props in psets.items():
                props[pset_name] = {}
                if isinstance(self.name, str):
                    prop = pset_props.get(self.name)
                    if prop:
                        props[pset_name][self.name] = prop
                else:
                    props[pset_name] = {k: v for k, v in pset_props.items() if k == self.name}

                if not bool(props[pset_name]):
                    is_pass = False
                    break

                if self.measure:
                    pset_entity = inst.wrapped_data.file.by_id(pset_props["id"])
                    for prop_entity in pset_entity.HasProperties:
                        if (
                            prop_entity.Name not in props[pset_name].keys()
                            or not prop_entity.is_a("IfcPropertySingleValue")
                            or prop_entity.NominalValue is None
                        ):
                            continue

                        data_type = prop_entity.NominalValue.is_a().replace("Ifc", "").replace("Measure", "")

                        if data_type != self.measure:
                            is_pass = False
                            break

                        unit = ifcopenshell.util.unit.get_property_unit(prop_entity, inst.wrapped_data.file)

                        props[pset_name][prop_entity.Name] = ifcopenshell.util.unit.convert(
                            prop_entity.NominalValue.wrappedValue,
                            getattr(unit, "Prefix", None),
                            unit.Name,
                            None,
                            ifcopenshell.util.unit.si_type_names[unit.UnitType],
                        )

                if not is_pass:
                    break

                if self.value:
                    if any([v != self.value for v in props[pset_name].values()]):
                        is_pass = False
                        break

        # TODO implement data type comparison
        # xs:string
        # xs:decimal
        # xs:integer
        # xs:boolean
        # xs:anyURI
        # xs:date 		YYYY-MM-DD
        # xs:time 		hh:mm:ss
        # xs:dateTime 	YYYY-MM-DDThh:mm:ss
        # xs:duration	PnYnMnDTnHnMnS

        return facet_evaluation(is_pass, "todo")


class material(facet):
    """The IDS material facet used to traverse the HasAssociations inverse attribute."""

    parameters = ["value"]
    message = "material '%(value)s'"

    @staticmethod
    def create(value=None, uri=None, minOccurs=None, maxOccurs=None, instructions=None):
        """Create a material facet that can be added to applicability or requirements of IDS specification.

        :param value: Value that is required. Could be alphanumeric or restriction object, defaults to None
        :type value: restriction|alphanumeric, optional
        :return: material object
        :rtype: material
        """
        inst = material()
        inst.value = value
        inst.uri = uri
        inst.minOccurs = minOccurs
        inst.maxOccurs = maxOccurs
        inst.instructions = instructions
        return inst

    def asdict(self):
        """Converts object to a dictionary, adding required attributes.

        :return: Xmlschema compliant dictionary.
        :rtype: dict
        """
        results = {}
        if self.value:
            results["value"] = parameter_asdict(self.value)
        if self.uri:
            results["@uri"] = self.uri
        if self.minOccurs:
            results["@minOccurs"] = self.minOccurs
        if self.maxOccurs:
            results["@maxOccurs"] = self.maxOccurs
        if self.instructions:
            results["@instructions"] = self.instructions
        return results

    def __call__(self, inst, logger=None):
        """Validate an ifc instance against that material facet.

        :param inst: IFC entity element
        :type inst: IFC entity
        :param logger: Logging object
        :type logger: logging
        :return: result of the validation as bool and message
        :rtype: facet_evaluation(bool, str)
        """
        material = ifcopenshell.util.element.get_material(inst, should_skip_usage=True)

        is_pass = material is not None

        if is_pass and self.value:
            if material.is_a("IfcMaterial"):
                values = {material.Name, getattr(material, "Category")}
            elif material.is_a("IfcMaterialList"):
                values = set()
                for mat in material.Materials or []:
                    values.update([mat.Name, getattr(mat, "Category")])
            elif material.is_a("IfcMaterialLayerSet"):
                values = {material.LayerSetName}
                for item in material.MaterialLayers or []:
                    values.update([item.Name, item.Category, item.Material.Name, getattr(item.Material, "Category")])
            elif material.is_a("IfcMaterialProfileSet"):
                values = {material.Name}
                for item in material.MaterialProfiles or []:
                    values.update([item.Name, item.Category, item.Material.Name, getattr(item.Material, "Category")])
            elif material.is_a("IfcMaterialConstituentSet"):
                values = {material.Name}
                for item in material.MaterialConstituents or []:
                    values.update([item.Name, item.Category, item.Material.Name, getattr(item.Material, "Category")])

            is_pass = False
            for value in values:
                if value == self.value:
                    is_pass = True
                    break

        return facet_evaluation(
            is_pass,
            self.message % {"value": "todo", "location": "todo"},
        )


def parameter_asdict(parameter):
    """Converts parameter to an IDS compliant dictionary, handling both value and restrictions.

    :return: Xmlschema compliant dictionary.
    :rtype: dict
    """
    if isinstance(parameter, str):
        parameter_dict = {"simpleValue": parameter}
    elif isinstance(parameter, restriction):
        parameter_dict = {"xs:restriction": [parameter.asdict()]}
    elif isinstance(parameter, list):
        restrictions = {"@base": "xs:" + parameter[0].base}
        for p in parameter:
            x = p.asdict()
            restrictions[list(x)[1]] = x[list(x)[1]]
        parameter_dict = {"xs:restriction": [restrictions]}
    else:
        raise Exception(str(parameter) + " was not able to be converted into 'Parameter_dict'")
    return parameter_dict


class boolean_logic:
    """Boolean conjunction over a collection of functions"""

    def __init__(self, terms):
        self.terms = terms

    def __call__(self, *args):
        eval = [t(*args) for t in self.terms]
        join = [" and ", " or "][self.fold == any]
        return facet_evaluation(self.fold(eval), join.join(map(str, eval)))

    def __str__(self):
        return [" and ", " or "][self.fold == any].join(map(str, self.terms))


class boolean_and(boolean_logic):
    fold = all


class boolean_or(boolean_logic):
    fold = any


class restriction:
    """
    The value restriction from XSD implemented as a list of values and a containment test
    """

    def __init__(self):
        """Create a restriction that can be used instead of value of a parameter."""
        self.type = ""
        self.options = []

    @staticmethod
    def parse(ids_dict):
        """Parse xml restriction to python object.

        :param ids_dict:
        :type ids_dict: dict
        """
        r = restriction()
        if ids_dict:
            # TODO 'base' missing in some IDS?!

            try:
                r.base = ids_dict["@base"][3:]
            except KeyError:
                r.base = "String"

            for n in ids_dict:
                if n == "enumeration":
                    r.type = "enumeration"
                    for x in ids_dict[n]:
                        r.options.append(x["@value"])
                elif n[-7:] == "clusive":
                    r.type = "bounds"
                    r.options.append({n: ids_dict[n]["@value"]})
                elif n[-5:] == "ength":
                    r.type = "length"
                    if n[3:6] == "min":
                        r.options.append(">=")
                    elif n[3:6] == "max":
                        r.options.append("<=")
                    else:
                        r.options.append("==")
                    r.options[-1] += str(ids_dict[n]["@value"])
                elif n == "pattern":
                    r.type = "pattern"
                    r.options.append(ids_dict[n]["@value"])
                # TODO add fractionDigits
                # TODO add totalDigits
                # TODO add whiteSpace
                elif n == "@base":
                    pass
                else:
                    print("Error! Restriction not implemented")
        return r

    def asdict(self):
        """Converts object to a dictionary, adding required attributes.

        :return: Xmlschema compliant dictionary.
        :rtype: dict
        """
        rest_dict = {"@base": "xs:" + self.base}
        if self.type == "enumeration":
            for option in self.options:
                if "xs:enumeration" not in rest_dict:
                    rest_dict["xs:enumeration"] = [{"@value": option}]
                else:
                    rest_dict["xs:enumeration"].append({"@value": option})
        elif self.type == "bounds":
            for option in self.options:
                rest_dict["xs:" + option] = [{"@value": str(self.options[option]), "@fixed": False}]
        elif self.type == "pattern":
            if "xs:pattern" not in rest_dict:
                rest_dict["xs:pattern"] = [{"@value": self.options}]
            else:
                rest_dict["xs:pattern"].append({"@value": self.options})
        return rest_dict

    @staticmethod
    def create(options, type="pattern", base="string"):
        """Create restriction instead of simpleValue

        :param type: One of "enumeration"|"pattern"|"bounds", defaults to "pattern"
        :type type: str, optional
        :param options: if enumeration: list of possible values
                        if pattern: xml regular expression string
                        if bounds: dictionary with possible keys: 'minInclusive', 'maxInclusive', 'minExclusive', 'maxExclusive'
        :type options: list|str|dict
        :param base: One of "string"|"boolean"|"decimal"|"integer", defaults to "string"
        :type base: str, optional
        :raises Exception: If not properly defined restriction.
        :return: restriction object
        :rtype: restriction
        """
        rest = restriction()
        if type in ["enumeration", "pattern", "bounds"]:
            rest.type = type
            rest.base = base
            rest.options = options
            if (
                (type == "enumeration" and isinstance(options, list))
                or (type == "bounds" and isinstance(options, dict))
                or (type == "pattern" and isinstance(options, str))
            ):
                rest.options = options
            else:
                raise Exception("Options were not properly defined.")
            return rest
        else:
            raise Exception(
                "Such restriction not implemented. Try: 'enumeration', 'pattern' or 'min/maxInclusive' or 'min/maxExclusive'."
            )

    def __eq__(self, other):
        """Evaluate the restriction using equality sign.

        :param other: value to compare with the restriction.
        :type other: str|float|int
        :return: True if 'other' match the restriction, False if not.
        :rtype: bool
        """
        result = False
        # TODO implement data type comparison
        if self and (other or other == 0):
            if self.type == "enumeration" and self.base == "bool":
                self.options = [x.lower() for x in self.options]
                result = str(other).lower() in self.options
            elif self.type == "enumeration":
                result = other in self.options
            elif self.type == "bounds":
                result = True
                for sign in self.options.keys():
                    if sign == "minInclusive" and other < self.options[sign]:
                        result = False
                    elif sign == "maxInclusive" and other > self.options[sign]:
                        result = False
                    elif sign == "minExclusive" and other <= self.options[sign]:
                        result = False
                    elif sign == "maxExclusive" and other >= self.options[sign]:
                        result = False
            elif self.type == "length":
                for op in self.options:
                    if eval(str(len(other)) + op):  # TODO eval not safe?
                        result = True
            elif self.type == "pattern":
                if isinstance(self.options, list):
                    # TODO handle case with multiple pattern options
                    translated_pattern = identities.translate_pattern(self.options[0])
                else:
                    translated_pattern = identities.translate_pattern(self.options)
                regex_pattern = re.compile(translated_pattern)
                if regex_pattern.fullmatch(other) is not None:
                    result = True
            # TODO add fractionDigits
            # TODO add totalDigits
            # TODO add whiteSpace
        return result

    def __repr__(self):
        """Represent the restriction in human readable sentence.

        :return: sentence
        :rtype: str
        """
        msg = "of type '%s', " % (self.base)
        if self.type == "enumeration":
            msg = msg + "of value: '%s'" % "' or '".join(self.options)
        elif self.type == "bounds":
            msg = msg + "of value %s" % ", and ".join([bounds[x] + str(self.options[x]) for x in self.options])
        elif self.type == "length":
            msg = msg + "with %s letters" % " and ".join(self.options)
        elif self.type == "pattern":
            msg = msg + "respecting the pattern '%s'" % self.options
        # TODO add fractionDigits
        # TODO add totalDigits
        # TODO add whiteSpace
        return msg


class SimpleHandler(logging.StreamHandler):
    """Logging handler listing all cases in python list."""

    def __init__(self, report_valid=False):
        """Logging handler listing all cases in python list.

        :param report_valid: True if you want to list all the compliant cases as well, defaults to False
        :type report_valid: bool, optional
        """
        logging.StreamHandler.__init__(self)
        self.statements = []
        if report_valid:
            self.setLevel(logging.DEBUG)
        else:
            self.setLevel(logging.ERROR)

    def emit(self, mymsg):
        """Triggered on each use of logging with the Simple handler enabled.

        :param log_content: default logger message
        :type log_content: string|dict
        """
        self.statements.append(mymsg.msg)


class CsvHandler(logging.StreamHandler):
    """Logging handler listing all cases in csv file."""

    def __init__(self, filepath="./Report.csv", report_valid=False):
        """Logging handler listing all cases in csv file.

        :param report_valid: True if you want to list all the compliant cases as well, defaults to False
        :type report_valid: bool, optional
        """
        import csv

        logging.StreamHandler.__init__(self)
        if report_valid:
            self.setLevel(logging.INFO)
        else:
            self.setLevel(logging.ERROR)
        self.file = open(filepath, "w", encoding="UTF8", newline="")
        self.csvwriter = csv.writer(self.file)
        self.csvwriter.writerow(["guid", "result", "sentence"])  # header

    def emit(self, mymsg):
        """Triggered on each use of logging with the Simple handler enabled.

        :param log_content: default logger message
        :type log_content: string|dict
        """
        # BUG  bytes-like object is required, not 'str'
        self.csvwriter.writerow(mymsg.msg)

    def flush(self):
        self.file.close()


class BcfHandler(logging.StreamHandler):
    """Logging handler for creation of BCF report files.

    :param project_name: defaults to "IDS Project"
    :type project_name: str, optional
    :param author: Email of the person creating the BCF report, defaults to "your@email.com"
    :type author: str, optional
    :param filepath: Path to save the BCF report, defaults to None
    :type filepath: str, optional
    :param report_valid: True if you want to list all the compliant cases as well, defaults to False
    :type report_valid: bool, optional

    Example::

        bcf_handler = BcfHandler(
            project_name="Default IDS Project",
            author="your@email.com",
            filepath="example.bcf",
        )
        logger = logging.getLogger("IDS_Logger")
        logging.basicConfig(level=logging.INFO, format="%(message)s")
        logger.addHandler(bcf_handler)
    """

    def __init__(self, project_name="IDS Project", author="your@email.com", filepath=None, report_valid=False):

        logging.StreamHandler.__init__(self)
        if report_valid:
            self.setLevel(logging.INFO)
        else:
            self.setLevel(logging.ERROR)
        self.bcf = BcfXml()
        self.bcf.author = author
        self.bcf.new_project()
        self.bcf.project.name = project_name
        self.filepath = filepath
        self.bcf.edit_project()

    def emit(self, log_content):
        """Triggered on each use of logging with the BCF handler enabled.

        :param log_content: default logger message
        :type log_content: string|dict
        """
        topic = bcf.Topic()
        topic.title = log_content.msg["sentence"].split(".\n")[1]
        topic.description = log_content.msg["sentence"].split(".\n")[0]
        self.bcf.add_topic(topic)
        # try:  # Add viewpoint and link to ifc object
        viewpoint = bcf.Viewpoint()
        viewpoint.perspective_camera = bcf.PerspectiveCamera()
        ifc_elem = log_content.msg["ifc_element"]
        # ifc_elem = ifc_file.by_guid(log_content.msg["guid"])
        target_position = np.array(ifcopenshell.util.placement.get_local_placement(ifc_elem.ObjectPlacement))
        target_position = target_position[:, 3][0:3]
        camera_position = target_position + np.array((5, 5, 5))
        viewpoint.perspective_camera.camera_view_point.x = camera_position[0]
        viewpoint.perspective_camera.camera_view_point.y = camera_position[1]
        viewpoint.perspective_camera.camera_view_point.z = camera_position[2]
        camera_direction = camera_position - target_position
        camera_direction = camera_direction / np.linalg.norm(camera_direction)
        camera_right = np.cross(np.array([0.0, 0.0, 1.0]), camera_direction)
        camera_right = camera_right / np.linalg.norm(camera_right)
        camera_up = np.cross(camera_direction, camera_right)
        camera_up = camera_up / np.linalg.norm(camera_up)
        rotation_transform = np.zeros((4, 4))
        rotation_transform[0, :3] = camera_right
        rotation_transform[1, :3] = camera_up
        rotation_transform[2, :3] = camera_direction
        rotation_transform[-1, -1] = 1
        translation_transform = np.eye(4)
        translation_transform[:3, -1] = -camera_position
        look_at_transform = np.matmul(rotation_transform, translation_transform)
        mat = np.linalg.inv(look_at_transform)
        viewpoint.perspective_camera.camera_direction.x = mat[0][2] * -1
        viewpoint.perspective_camera.camera_direction.y = mat[1][2] * -1
        viewpoint.perspective_camera.camera_direction.z = mat[2][2] * -1
        viewpoint.perspective_camera.camera_up_vector.x = mat[0][1]
        viewpoint.perspective_camera.camera_up_vector.y = mat[1][1]
        viewpoint.perspective_camera.camera_up_vector.z = mat[2][1]
        viewpoint.components = bcf.Components()
        c = bcf.Component()
        c.ifc_guid = log_content.msg["guid"]
        viewpoint.components.selection.append(c)
        viewpoint.components.visibility = bcf.ComponentVisibility()
        viewpoint.components.visibility.default_visibility = True
        viewpoint.snapshot = None
        self.bcf.add_viewpoint(topic, viewpoint)

    def flush(self):
        """Saves the BCF report to file. Triggered at the end of the validation process."""
        if not self.filepath:
            self.filepath = os.getcwd() + r"\IDS_report.bcf"
        if not (self.filepath.endswith(".bcf") or self.filepath.endswith(".bcfzip")):
            self.filepath = self.filepath + r"\IDS_report.bcf"
        self.bcf.save_project(self.filepath)


location = {"instance": "an instance ", "type": "a type ", "any": "a "}

bounds = {
    "minInclusive": "larger or equal ",
    "maxInclusive": "smaller or equal ",
    "minExclusive": "larger than ",
    "maxExclusive": "smaller than ",
}

if __name__ == "__main__":
    import sys, os
    import ifcopenshell

    ids_file = ids.open(sys.argv[1])
    ifc_file = ifcopenshell.open(sys.argv[2])
    filepath = sys.argv[3]

    logger = logging.getLogger("IDS_Logger")
    logging.basicConfig(filename=filepath, level=logging.INFO, format="%(message)s")
    logging.FileHandler(filepath + r"\report.txt", mode="w")

    bcf_handler = BcfHandler(
        project_name="Default IDS Project",
        author="your@email.com",
        filepath=filepath + r"\report.bcfzip",
    )
    logger.addHandler(bcf_handler)

    report = SimpleHandler()
    logger.addHandler(report)

    ids_file.validate(ifc_file, logger)
