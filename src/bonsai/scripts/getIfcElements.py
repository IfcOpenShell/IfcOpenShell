# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of Bonsai.
#
# Bonsai is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Bonsai is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Bonsai.  If not, see <http://www.gnu.org/licenses/>.

"""This script converts the computer iterpretable listing ifcXML XSD into a JSON file"""

import xml.etree.ElementTree as ET
import collections
import json


class IFC4Extractor:
    def __init__(self, xsd_file):
        self.xsd_file = xsd_file
        tree = ET.parse(self.xsd_file)
        self.root = tree.getroot()
        self.ns = {"xs": "http://www.w3.org/2001/XMLSchema"}
        self.elements = {}
        self.filters = []
        self.filtered_elements = {}

    def extract(self):
        for element in self.root.findall("xs:element", self.ns):
            print("Processing {}".format(element.attrib["name"]))
            if not "substitutionGroup" in element.attrib or self.is_descendant_from_class(element, "uos"):
                continue
            data = {
                "is_abstract": self.is_abstract(element),
                "parent": element.attrib["substitutionGroup"].replace("ifc:", ""),
                "attributes": self.get_attributes(element),
                "complex_attributes": self.get_complex_attributes(element),
            }
            self.elements[element.attrib["name"]] = data
            for filter in self.filters:
                if self.is_descendant_from_class(element, filter) and not data["is_abstract"]:
                    self.filtered_elements.setdefault(filter, {})[element.attrib["name"]] = data

    def export(self, filename):
        final = {}
        for filter in self.filters:
            final.update(self.filtered_elements[filter])
        with open(filename, "w") as file:
            file.write(json.dumps(collections.OrderedDict(sorted(final.items())), indent=4))

    def is_descendant_from_class(self, element, class_name):
        if element is None or "substitutionGroup" not in element.attrib or "type" not in element.attrib:
            return False
        if element.attrib["substitutionGroup"] == "ifc:{}".format(class_name) or element.attrib[
            "type"
        ] == "ifc:{}".format(class_name):
            return True
        return self.is_descendant_from_class(self.get_parent_element(element), class_name)

    def is_abstract(self, element):
        return True if "abstract" in element.attrib else False

    def get_attributes(self, element, attributes=None):
        if attributes is None:
            attributes = []
        if element.attrib["substitutionGroup"] != self.get_ifcroot_parent_name():
            attributes = self.get_attributes(self.get_parent_element(element), attributes)
        for attribute in self.root.findall(self.get_attribute_xpath(element), self.ns):
            try:
                attributes.append(
                    {
                        "name": attribute.attrib["name"],
                        "type": attribute.attrib["type"].replace("ifc:", ""),
                        "is_enum": self.is_enum(attribute),
                        "enum_values": self.get_enum_values(attribute),
                    }
                )
            except KeyError as e:
                print("Attribute {} is missing key {}".format(attribute.attrib, e))
        return attributes

    def get_attribute_xpath(self, element):
        return "./xs:complexType[@name='{}']/xs:complexContent/xs:extension/xs:attribute[@name][@type]".format(
            element.attrib["name"]
        )

    def get_ifcroot_parent_name(self):
        return "ifc:Entity"

    def get_complex_attributes(self, element, attributes=None):
        if attributes is None:
            attributes = []
        if element.attrib["substitutionGroup"] != self.get_ifcroot_parent_name():
            attributes = self.get_complex_attributes(self.get_parent_element(element), attributes)
        for attribute in self.root.findall(
            "./xs:complexType[@name='{}']/xs:complexContent/xs:extension/xs:sequence/xs:element[@name]".format(
                element.attrib["name"]
            ),
            self.ns,
        ):
            if "type" in attribute.attrib:
                attributes.append(
                    {
                        "name": attribute.attrib["name"],
                        "type": attribute.attrib["type"].replace("ifc:", ""),
                        "is_select": False,
                        "select_types": [],
                    }
                )
            else:
                type_element = attribute.find("./xs:complexType/xs:sequence/xs:element[@ref]", self.ns)
                is_select = False
                select_types = []
                if not type_element:
                    # Handle select (i.e. group) attributes
                    type_element = attribute.find("./xs:complexType/xs:group", self.ns)
                    if type_element is not None:
                        is_select = True
                        select_types = [
                            e.attrib["ref"].replace("ifc:", "").replace("-wrapper", "")
                            for e in self.root.findall(
                                "./xs:group[@name='{}']/xs:choice/xs:element[@ref]".format(
                                    type_element.attrib["ref"].replace("ifc:", "")
                                ),
                                self.ns,
                            )
                        ]
                if type_element is not None:
                    attributes.append(
                        {
                            "name": attribute.attrib["name"],
                            "type": type_element.attrib["ref"].replace("ifc:", ""),
                            "is_select": is_select,
                            "select_types": select_types,
                        }
                    )
        return attributes

    def get_parent_element(self, element):
        return self.root.find(
            "./xs:element[@name='{}']".format(element.attrib["substitutionGroup"].replace("ifc:", "")), self.ns
        )

    def is_enum(self, attribute):
        return "Enum" in attribute.attrib["type"]

    def get_enum_values(self, attribute):
        if not self.is_enum(attribute):
            return []
        values = []
        for enumeration in self.root.findall(
            "./xs:simpleType[@name='{}']/xs:restriction/xs:enumeration".format(
                attribute.attrib["type"].replace("ifc:", "")
            ),
            self.ns,
        ):
            values.append(enumeration.attrib["value"].upper())
        return values

    def is_ifc_version(self, version):
        return version in self.xsd_file


class IFC2X3Extractor(IFC4Extractor):
    # IFC2X3 seems to store regular attributes where IFC4 stores complex attributes
    def get_attribute_xpath(self, element):
        return "./xs:complexType[@name='{}']/xs:complexContent/xs:extension/xs:sequence/xs:element[@name]".format(
            element.attrib["name"]
        )

    def get_ifcroot_parent_name(self):
        return "ex:Entity"

    # IFC2X3 does not seem to store complex attributes in the XSD file
    def get_complex_attributes(self, element, attributes=None):
        return []


filename_filters = {
    "IfcContext_IFC4.json": ["IfcContext"],
    "IfcElement_IFC4.json": ["IfcElement"],
    "IfcSpatialElement_IFC4.json": ["IfcSpatialElement"],
    "IfcGroup_IFC4.json": ["IfcGroup"],
    "IfcStructural_IFC4.json": ["IfcStructuralActivity", "IfcStructuralItem"],
    "IfcMaterialDefinition_IFC4.json": ["IfcMaterialDefinition"],
    "IfcParameterizedProfileDef_IFC4.json": ["IfcParameterizedProfileDef"],
    "IfcBoundaryCondition_IFC4.json": ["IfcBoundaryCondition"],
    "IfcElementType_IFC4.json": ["IfcElementType", "IfcSpatialElementType"],
    "IfcAnnotation_IFC4.json": ["IfcAnnotation"],
    "IfcPositioningElement_IFC4.json": ["IfcGrid", "IfcGridAxis"],  # IfcPositioningElement in the future
}

for filename, filters in filename_filters.items():
    extractor = IFC4Extractor("IFC4_ADD2.xsd")
    extractor.filters = filters
    # extractor = IFC2X3Extractor("IFC2X3.xsd")
    extractor.extract()
    extractor.export(filename)
