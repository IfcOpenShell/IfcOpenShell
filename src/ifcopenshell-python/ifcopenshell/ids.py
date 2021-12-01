# IDS - Information Delivery Specification.
# Copyright (C) 2021 Artur Tomczak <artomczak@gmail.com>, Thomas Krijnen <mail@thomaskrijnen.com>
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
from datetime import date

import ifcopenshell.util.element
import ifcopenshell.util.placement

from bcf.v2.bcfxml import BcfXml
from bcf.v2 import data as bcf

from xmlschema import XMLSchema
from xmlschema import etree_tostring
from xmlschema.validators import identities


cwd = os.path.dirname(os.path.realpath(__file__))
ids_schema = XMLSchema(os.path.join(cwd, "ids.xsd"))  # source: "http://standards.buildingsmart.org/IDS/ids_04.xsd"


def error(msg):
    raise Exception(msg)


class ids:
    """Represents the XML root <ids> node and its <specification> childNodes."""

    def __init__(
        self,
        ifcversion=None,
        description=None,
        author=None,
        copyright=None,
        version=None,
        creation_date=None,
        purpose=None,
        milestone=None,
    ):
        """Create an IDS object.

        :param ifcversion: IFC schema version. If None, then schema independent. Options: '2.3.0.1'|'4.0.2.1'|'4.3.0.0'|None, defaults to None
        :type ifcversion: str, optional
        :param description:, defaults to None
        :type description: str, optional
        :param author: Email of the IDS author, defaults to None
        :type author: str, optional
        :param copyright:, defaults to None
        :type copyright: str, optional
        :param version: IDS file version, defaults to None
        :type version: float, optional
        :param creation_date: Date in 'yyyy-mm-dd' format, defaults to current date
        :type creation_date: str, optional
        :param purpose:, defaults to None
        :type purpose: str, optional
        :param milestone:, defaults to None
        :type milestone: str, optional
        """
        self.specifications = []
        self.info = {}
        if ifcversion:
            if ifcversion in ["2.3.0.1", "4.0.2.1", "4.3.0.0"]:
                self.info["ifcversion"] = ifcversion
        if author:
            if "@" in author:
                self.info["author"] = author
        if description:
            self.info["description"] = description
        if copyright:
            self.info["copyright"] = copyright
        if version:
            self.info["version"] = version
        if creation_date:
            if re.match(r"\d\d\d\d-\d\d-\d\d", creation_date):
                self.info["date"] = creation_date  # date.fromisoformat(creation_date).isoformat()
        if "date" not in self.info:
            self.info["date"] = date.today().isoformat()
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
            "@xsi:schemaLocation": "http://standards.buildingsmart.org/IDS/ids_04.xsd",
            "specification": [],
            "info": self.info,
        }
        for spec in self.specifications:
            ids_dict["specification"].append(spec.asdict())
        return ids_dict

    def to_xml(self, filepath="./", ids_schema=ids_schema):
        """Save IDS object as .xml file.

        :param filepath: Path for the new file, defaults to "./"
        :type filepath: str, optional
        :param ids_schema: XML Schema for an IDS file, defaults to ids_schema object from buildingSMART
        :type ids_schema: XMLschema, optional
        :return: Result of the newly created file validation against the schema.
        :rtype: bool
        """

        if filepath.endswith("/"):
            filepath = filepath + "IDS"
        if not filepath.endswith(".xml"):
            filepath = filepath + ".xml"

        ids_dict = self.asdict()

        ids_xml = ids_schema.encode(
            ids_dict,
            namespaces={
                "": "http://standards.buildingsmart.org/IDS",
                "xs": "http://www.w3.org/2001/XMLSchema",
                "xsi": "http://www.w3.org/2001/XMLSchema-instance",
                "xsi:schemaLocation": "http://standards.buildingsmart.org/IDS/ids_04.xsd",
            },
        )  # validation='skip',

        ids_str = etree_tostring(
            ids_xml,
            namespaces={
                "": "http://standards.buildingsmart.org/IDS",
                # 'xs': 'http://www.w3.org/2001/XMLSchema',
                # 'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
                # 'xsi:schemaLocation': "http://standards.buildingsmart.org/IDS/ids_04.xsd"
            },
        )

        with open(filepath, "w") as f:
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            f.write("<!-- IDS (INFORMATION DELIVERY SPECIFICATION) CREATED USING IFCOPENSHELL -->\n")
            f.write(ids_str)
            f.close()

        # ids_schema.validate(filepath)
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
        ids_file.specifications = [specification.parse(s) for s in ids_content["specification"]]
        return ids_file

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

        if "ifcversion" in self.info.keys():
            if self.info["ifcversion"] in ["2.3.0.1", "4.0.2.1", "4.3.0.0"]:
                if self.info["ifcversion"][0:3] == "2.3":
                    if not ifc_file.schema.startswith("IFC2x3"):
                        logger.error("IFC file is of %s not of %s schema." % (ifc_file.schema, self.info["ifcversion"]))
                elif self.info["ifcversion"][0:3] == "4.0":
                    if not ifc_file.schema == "IFC4":
                        logger.error("IFC file is of %s not of %s schema." % (ifc_file.schema, self.info["ifcversion"]))
                elif self.info["ifcversion"][0:3] == "4.3":
                    if not ifc_file.schema.startswith("IFC4x3"):
                        logger.error("IFC file is of %s not of %s schema." % (ifc_file.schema, self.info["ifcversion"]))
                else:
                    logger.error("IFC version not recognized")

        # Consider other way around: for elem, for spec so we can see if an element pass all IDSes?
        for spec in self.specifications:
            self.ifc_applicable = 0
            self.ifc_passed = 0
            for elem in ifc_file.by_type("IfcObject"):
                apply, comply = spec(elem, logger)
                if apply:
                    self.ifc_applicable += 1
                if comply:
                    self.ifc_passed += 1
            if self.ifc_applicable == 0:
                if spec.necessity == "required":
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

    def __init__(self, name="Specification", necessity="required"):
        """Create a specification to be added in ids.

        :param name:, defaults to "Specification"
        :type name: str, optional
        :param necessity: 'required'|'optional', defaults to "required"
        :type necessity: str, optional
        """
        self.name = name
        self.applicability = None
        self.requirements = None
        self.necessity = necessity

    def asdict(self):
        """Converts object to a dictionary, adding required attributes.

        :return: Xmlschema compliant dictionary.
        :rtype: dict
        """
        # if older python collections.OrderedDict()
        spec_dict = {
            "@name": self.name,
            "@necessity": self.necessity,
            "applicability": {},
            "requirements": {},
        }
        for x in ["applicability", "requirements"]:
            for fac in (getattr(self, x)).terms:
                fclass = type(fac).__name__
                if fclass in spec_dict[x]:
                    spec_dict[x][fclass].append(fac.asdict())
                else:
                    spec_dict[x][fclass] = [fac.asdict()]
        return spec_dict

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
        spec.name = ids_dict["@name"]
        spec.necessity = ids_dict["@necessity"]
        spec.applicability = boolean_and(parse_rules(ids_dict["applicability"]))
        spec.requirements = boolean_and(parse_rules(ids_dict["requirements"]))
        return spec

    def add_applicability(self, facet):
        """Applicability specifies what conditions must be meet for an IFC object to be used for validation. Note, that at least one entity facet is required.

        :param facet: any of entity|classification|property|material
        :type facet: facet

        Example::

            i = ids.ids()
            i.specifications.append(ids.specification(name="Test_Specification"))
            e = ids.entity.create(name="Test_Name", predefinedtype="Test_PredefinedType")
            i.specifications[0].add_applicability(e)
        """
        if self.applicability:
            self.applicability = boolean_and(self.applicability.terms + [facet])
        else:
            self.applicability = boolean_and([facet])

    def add_requirement(self, facet):
        """Requirement is validated on all applicable IFC elements. Note, that at least one facet of any type is required.

        :param facet: any of entity|classification|property|material
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
        """Represent the specification in human readible sentence.

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

    def __init__(self, node=None, location=None):
        if node:
            self.node = node
            if "@location" in self:
                self.location = self.node["@location"]
            else:
                self.location = "any"
        if location:
            self.location = location
        else:
            self.location = "any"

    def __getattr__(self, k):
        if k in self.node:
            v = self.node[k]
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

    parameters = ["name", "predefinedtype"]

    @staticmethod
    def create(name=None, predefinedtype=None):
        """Create an entity facet that can be added to applicability or requirements of IDS specification.

        :param name: IFC entity name that is required. e.g. IfcWall, defaults to None
        :type name: str, optional
        :param predefinedtype: name of the predefined type, defaults to None
        :type predefinedtype: str, optional
        :return: entity object
        :rtype: entity
        """

        inst = entity()
        inst.name = name
        inst.predefinedtype = predefinedtype
        return inst

    def asdict(self):
        """Converts object to a dictionary, adding required attributes.

        :return: Xmlschema compliant dictionary.
        :rtype: dict
        """
        fac_dict = {"name": parameter_asdict(self.name)}
        try:
            fac_dict["predefinedtype"] = parameter_asdict(self.predefinedtype)
        except (RecursionError, UnboundLocalError) as e:
            print(e)
        return fac_dict

    def __call__(self, inst, logger):
        """Validate an ifc instance against that entity facet.

        :param inst: IFC entity element
        :type inst: IFC entity
        :param logger: Logging object
        :type logger: logging
        :return: result of the validation as bool and message
        :rtype: facet_evaluation(bool, str)
        """

        # @nb with inheritance
        if self.predefinedtype and hasattr(inst, "PredefinedType"):
            self.message = "an entity name '%(name)s' of predefined type '%(predefinedtype)s'"
            return facet_evaluation(
                inst.is_a(self.name) and inst.PredefinedType == self.predefinedtype,
                self.message % {"name": inst.is_a(), "predefinedtype": inst.PredefinedType},
            )
        else:
            self.message = "an entity name '%(name)s'"
            return facet_evaluation(inst.is_a(self.name), self.message % {"name": inst.is_a()})


class classification(facet):
    """
    The IDS classification facet by traversing the HasAssociations inverse attribute
    """

    parameters = ["system", "value", "location"]
    message = "%(location)sclassification reference %(value)s from '%(system)s'"

    @staticmethod
    def create(location="any", value=None, system=None):
        """Create a classification facet that can be added to applicability or requirements of IDS specification.

        :param location: Define where to check for the parameter. One of "any"|"instance"|"type", defaults to "any"
        :type location: str, optional
        :param value: Value that is required. Could be alphanumeric or restriction object, defaults to None
        :type value: restriction|alphanumeric, optional
        :param system: System that is required. Could be alphanumeric or restriction object, defaults to None
        :type system: restriction|alphanumeric, optional
        :return: classification object
        :rtype: classification
        """

        inst = classification()
        inst.location = location
        inst.value = value
        inst.system = system
        return inst

    def asdict(self):
        """Converts object to a dictionary, adding required attributes.

        :return: Xmlschema compliant dictionary.
        :rtype: dict
        """
        fac_dict = {
            "value": parameter_asdict(self.value),
            "system": parameter_asdict(self.system),
            "@location": self.location,
            # "instructions": "SAMPLE_INSTRUCTIONS",
        }
        return fac_dict

    def __call__(self, inst, logger):
        """Validate an ifc instance against that classification facet.

        :param inst: IFC entity element
        :type inst: IFC entity
        :param logger: Logging object
        :type logger: logging
        :return: result of the validation as bool and message
        :rtype: facet_evaluation(bool, str)
        """

        instance_classiciations = inst.HasAssociations
        if ifcopenshell.util.element.get_type(inst):
            type_classifications = ifcopenshell.util.element.get_type(inst).HasAssociations
        else:
            type_classifications = ()

        if self.location == "instance" and instance_classiciations:
            associations = instance_classiciations
        elif self.location == "type" and type_classifications:
            associations = type_classifications
        elif self.location == "any" and (instance_classiciations or type_classifications):
            associations = instance_classiciations + type_classifications
        else:
            associations = ()

        refs = []
        for association in associations:
            if association.is_a("IfcRelAssociatesClassification"):
                cref = association.RelatingClassification
                if hasattr(cref, "ItemReference"):  # IFC2x3
                    refs.append((cref.ReferencedSource.Name, cref.ItemReference))
                elif hasattr(cref, "Identification"):  # IFC4
                    refs.append((cref.ReferencedSource.Name, cref.Identification))

        self.location_msg = location[self.location]

        if refs:
            return facet_evaluation(
                (self.system, self.value) in refs,
                self.message
                % {
                    "system": refs[0][0],
                    "value": "'" + refs[0][1] + "'",
                    "location": self.location_msg,
                },  # what if not first item of refs?
            )
        else:
            return facet_evaluation(False, "does not have %sclassification reference" % self.location_msg)


class property(facet):
    """
    The IDS property facet implemented using `ifcopenshell.util.element`
    """

    parameters = ["name", "propertyset", "value", "location"]
    message = "%(location)sproperty '%(name)s' in '%(propertyset)s' with a value %(value)s"

    @staticmethod
    def create(location="any", propertyset=None, name=None, value=None):
        """Create a property facet that can be added to applicability or requirements of IDS specification.

        :param location: Define where to check for the parameter. One of "any"|"instance"|"type", defaults to "any"
        :type location: str, optional
        :param propertyset: Propertyset that is required. Could be alphanumeric or restriction object, defaults to None
        :type propertyset: restriction|alphanumeric, optional
        :param name: Name that is required. Could be alphanumeric or restriction object, defaults to None
        :type name: restriction|alphanumeric, optional
        :param value: Value that is required. Could be alphanumeric or restriction object, defaults to None
        :type value: restriction|alphanumeric, optional
        :return: property object
        :rtype: property
        """
        inst = property()
        inst.location = location
        inst.propertyset = propertyset
        inst.name = name
        inst.value = value
        # cls.attributes = {'@location': location} # 'type', 'instance', 'any'
        # BUG '@href': 'http://identifier.buildingsmart.org/uri/buildingsmart/ifc-4.3/prop/FireRating', #https://identifier.buildingsmart.org/uri/something
        # BUG 'instructions': 'Please add the desired rating.',
        return inst

    def asdict(self):
        """Converts object to a dictionary, adding required attributes.

        :return: Xmlschema compliant dictionary.
        :rtype: dict
        """
        fac_dict = {
            "@location": self.location,
            "propertyset": parameter_asdict(self.propertyset),
            "name": parameter_asdict(self.name),
            "value": parameter_asdict(self.value),
            # "instructions": "SAMPLE_INSTRUCTIONS",
            # TODO '@href': 'http://identifier.buildingsmart.org/uri/buildingsmart/ifc-4.3/prop/FireRating', #https://identifier.buildingsmart.org/uri/something
        }
        return fac_dict

    def __call__(self, inst, logger):
        """Validate an ifc instance against that property facet.

        :param inst: IFC entity element
        :type inst: IFC entity
        :param logger: Logging object
        :type logger: logging
        :return: result of the validation as bool and message
        :rtype: facet_evaluation(bool, str)
        """

        self.location = self.node["@location"]

        if self.propertyset == "attribute":
            val = {k.lower(): v for k, v in inst.get_info().items()}.get(self.name, None)
        else:
            # TODO sometimes AttributeError: 'str' object has no attribute 'wrappedValue'
            instance_props = ifcopenshell.util.element.get_psets(inst)

            if ifcopenshell.util.element.get_type(inst):
                type_props = ifcopenshell.util.element.get_psets(ifcopenshell.util.element.get_type(inst))
            else:
                type_props = {}

            if self.location == "instance":
                props = instance_props
            elif self.location == "type" and type_props:
                props = type_props
            elif self.location == "any" and (instance_props or type_props):
                props = {**instance_props, **type_props}
            else:
                props = {}

            pset = props.get(self.propertyset)
            val = pset.get(self.name) if pset else None

        self.location_msg = location[self.location]
        di = {"name": self.name, "propertyset": self.propertyset, "value": "'%s'" % val, "location": self.location_msg}

        if val is not None:
            msg = self.message % di
        else:
            if pset:
                msg = "does not have %(location)sproperty '%(name)s' in a set '%(propertyset)s'" % di
            else:
                msg = "does not have %(location)sset '%(propertyset)s'" % di

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

        return facet_evaluation(val == self.value, msg)


class material(facet):
    """The IDS material facet used to traverse the HasAssociations inverse attribute."""

    parameters = ["value", "location"]
    message = "%(location)smaterial '%(value)s'"

    @staticmethod
    def create(location="any", value=None):
        """Create a material facet that can be added to applicability or requirements of IDS specification.

        :param location: Define where to check for the parameter. One of "any"|"instance"|"type", defaults to "any"
        :type location: str, optional
        :param value: Value that is required. Could be alphanumeric or restriction object, defaults to None
        :type value: restriction|alphanumeric, optional
        :return: material object
        :rtype: material
        """
        inst = material()
        inst.location = location
        inst.value = value
        # TODO '@use': 'optional'
        # TODO '@href': 'https://identifier.buildingsmart.org/uri/something',
        # TODO 'instructions': 'Please add the desired...',
        return inst

    def asdict(self):
        """Converts object to a dictionary, adding required attributes.

        :return: Xmlschema compliant dictionary.
        :rtype: dict
        """
        fac_dict = {
            "value": parameter_asdict(self.value),
            "@location": self.location,
            # TODO "instructions": "SAMPLE_INSTRUCTIONS",
            # TODO '@href': 'http://identifier.buildingsmart.org/uri/buildingsmart/ifc-4.3/prop/FireRating', #https://identifier.buildingsmart.org/uri/something
            # TODO '@use': 'optional'
        }
        return fac_dict

    def __call__(self, inst, logger):
        """Validate an ifc instance against that material facet.

        :param inst: IFC entity element
        :type inst: IFC entity
        :param logger: Logging object
        :type logger: logging
        :return: result of the validation as bool and message
        :rtype: facet_evaluation(bool, str)
        """

        self.location = self.node["@location"]

        instance_material_rel = [rel for rel in inst.HasAssociations if rel.is_a("IfcRelAssociatesMaterial")]
        if ifcopenshell.util.element.get_type(inst):
            type_material_rel = [
                rel
                for rel in ifcopenshell.util.element.get_type(inst).HasAssociations
                if rel.is_a("IfcRelAssociatesMaterial")
            ]
        else:
            type_material_rel = []

        if self.location == "instance":
            material_relations = list(instance_material_rel)
        elif self.location == "type" and type_material_rel:
            material_relations = list(type_material_rel)
        elif self.location == "any" and (instance_material_rel or type_material_rel):
            material_relations = instance_material_rel + type_material_rel
        else:
            material_relations = []

        materials = []
        for rel in material_relations:
            if rel.RelatingMaterial.is_a() == "IfcMaterial":
                materials.append(rel.RelatingMaterial.Name)
            elif rel.RelatingMaterial.is_a() == "IfcMaterialMaterialList":  # DEPRECATED in IFC4
                [materials.append(mat.Name) for mat in rel.RelatingMaterial]
            elif rel.RelatingMaterial.is_a() == "IfcMaterialConstituentSet":
                [materials.append(mat.Material.Name) for mat in rel.RelatingMaterial.MaterialConstituents]
            elif rel.RelatingMaterial.is_a() == "IfcMaterialLayerSet":
                [materials.append(mat.Name) for mat in rel.RelatingMaterial.MaterialLayers]
            elif rel.RelatingMaterial.is_a() == "IfcMaterialLayerSetUsage":
                layers = rel.RelatingMaterial.ForLayerSet.MaterialLayers
                [materials.append(layer.Material.Name) for layer in layers]
            elif rel.RelatingMaterial.is_a() == "IfcMaterialProfileSet":
                [materials.append(mat.Material.Name) for mat in rel.RelatingMaterial.MaterialProfiles]
            elif rel.RelatingMaterial.is_a() == "IfcMaterialProfileSetUsage":
                profileSets = rel.RelatingMaterial.ForProfileSet.MaterialProfiles
                [materials.append(pset.Material.Name) for pset in profileSets]
            else:
                raise Exception("IfcRelAssociatesMaterial not implemented")

        if not materials:
            materials.append("UNDEFINED")

        self.location_msg = location[self.location]

        return facet_evaluation(
            self.value in materials,
            self.message % {"value": "'/'".join(materials), "location": self.location_msg},
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
            r.base = ids_dict["@base"][3:]
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
                if "xs:option" not in rest_dict:
                    rest_dict["xs:" + option] = [{"@value": option}]
                else:
                    rest_dict["xs:" + option].append({"@value": self.options[option], "@fixed": False})
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
                Exception("Options were not properly defined.")
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
                translated_pattern = identities.translate_pattern(self.options)
                regex_pattern = re.compile(translated_pattern)
                if regex_pattern.fullmatch(other) is not None:
                    result = True
            # TODO add fractionDigits
            # TODO add totalDigits
            # TODO add whiteSpace
        return result

    def __repr__(self):
        """Represent the restriction in human readible sentence.

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
            self.setLevel(logging.INFO)
        else:
            self.setLevel(logging.ERROR)

    def emit(self, mymsg):
        """Triggered on each use of logging with the Simple handler enabled.

        :param log_content: default logger message
        :type log_content: string|dict
        """
        self.statements.append(mymsg.msg)


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
        try:  # Add viewpoint and link to ifc object
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
        except:
            pass

    def flush(self):
        """Saves the BCF report to file. Triggered at the end of the validation process."""
        if not self.filepath:
            self.filepath = os.getcwd() + r"\IDS_report.bcfzip"
        if not (self.filepath.endswith(".bcf") or self.filepath.endswith(".bcfzip")):
            self.filepath = self.filepath + r"\IDS_report.bcfzip"
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
