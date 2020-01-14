"""This script converts the computer iterpretable listing ifcXML XSD into a JSON file"""

import xml.etree.ElementTree as ET
import collections
import json

class IFC4Extractor:
    def __init__(self, xsd_file):
        self.xsd_file = xsd_file
        tree = ET.parse(self.xsd_file)
        self.root = tree.getroot()
        self.ns = {'xs': 'http://www.w3.org/2001/XMLSchema'}
        self.elements = {}
        #self.filters = ['IfcBuildingElement']
        #self.filters = ['IfcElement']
        #self.filters = ['IfcSpatialStructureElement']
        #self.filters = ['IfcStructuralActivity', 'IfcStructuralItem']
        #self.filters = ['IfcMaterialDefinition']
        self.filters = ['IfcParameterizedProfileDef']
        self.filtered_elements = {}

    def extract(self):
        for element in self.root.findall("xs:element", self.ns):
            #if self.is_descendant_from_class(element, "IfcRoot"):
            #if self.is_descendant_from_class(element, "IfcMaterialDefinition"):
            if self.is_descendant_from_class(element, "IfcParameterizedProfileDef"):
                print('Processing {}'.format(element.attrib['name']))
                data = {
                    'is_abstract': self.is_abstract(element),
                    'parent': element.attrib['substitutionGroup'].replace('ifc:', ''),
                    'attributes': self.get_attributes(element),
                    'complex_attributes': self.get_complex_attributes(element)
                }
                self.elements[element.attrib['name']] = data
                for filter in self.filters:
                    if self.is_descendant_from_class(element, filter):
                        self.filtered_elements.setdefault(filter, {})[element.attrib['name']] = data

    def export(self):
        final = {}
        for filter in self.filters:
            final.update(self.filtered_elements[filter])
        with open("output.json", "w") as file:
            file.write(json.dumps(collections.OrderedDict(sorted(final.items())), indent=4))

    def is_descendant_from_class(self, element, class_name):
        if element is None \
            or "substitutionGroup" not in element.attrib:
            return False
        if element.attrib["substitutionGroup"] == 'ifc:{}'.format(class_name):
            return True
        return self.is_descendant_from_class(self.get_parent_element(element), class_name)

    def is_abstract(self, element):
        return True if 'abstract' in element.attrib else False

    def get_attributes(self, element, attributes = None):
        if attributes is None:
            attributes = []
        if element.attrib['substitutionGroup'] != self.get_ifcroot_parent_name():
            attributes = self.get_attributes(self.get_parent_element(element), attributes)
        for attribute in self.root.findall(self.get_attribute_xpath(element), self.ns):
            try:
                attributes.append({
                    'name': attribute.attrib['name'],
                    'type': attribute.attrib['type'].replace('ifc:', ''),
                    'is_enum': self.is_enum(attribute),
                    'enum_values': self.get_enum_values(attribute)
                })
            except KeyError as e:
                print('Attribute {} is missing key {}'.format(attribute.attrib, e))
        return attributes

    def get_attribute_xpath(self, element):
        return "./xs:complexType[@name='{}']/xs:complexContent/xs:extension/xs:attribute[@name][@type]".format(element.attrib['name'])

    def get_ifcroot_parent_name(self):
        return "ifc:Entity"

    def get_complex_attributes(self, element, attributes = None):
        if attributes is None:
            attributes = []
        if element.attrib['substitutionGroup'] != self.get_ifcroot_parent_name():
            attributes = self.get_complex_attributes(self.get_parent_element(element), attributes)
        for attribute in self.root.findall(
            "./xs:complexType[@name='{}']/xs:complexContent/xs:extension/xs:sequence/xs:element[@name]".format(
                element.attrib['name']
            ), self.ns):
            if 'type' in attribute.attrib:
                attributes.append({
                    'name': attribute.attrib['name'],
                    'type': attribute.attrib['type'].replace('ifc:', '')
                })
            else:
                type_element = attribute.find('./xs:complexType/xs:sequence/xs:element[@ref]', self.ns)
                if type_element is not None:
                    attributes.append({
                        'name': attribute.attrib['name'],
                        'type': type_element.attrib['ref'].replace('ifc:', '')
                    })
        return attributes

    def get_parent_element(self, element):
        return self.root.find("./xs:element[@name='{}']".format(
            element.attrib["substitutionGroup"].replace('ifc:', '')
        ), self.ns)

    def is_enum(self, attribute):
        return 'Enum' in attribute.attrib['type']

    def get_enum_values(self, attribute):
        if not self.is_enum(attribute):
            return []
        values = []
        for enumeration in self.root.findall(
            "./xs:simpleType[@name='{}']/xs:restriction/xs:enumeration".format(
                attribute.attrib['type'].replace('ifc:', '')
            ), self.ns):
            values.append(enumeration.attrib['value'].upper())
        return values

    def is_ifc_version(self, version):
        return version in self.xsd_file

class IFC2X3Extractor(IFC4Extractor):
    # IFC2X3 seems to store regular attributes where IFC4 stores complex attributes
    def get_attribute_xpath(self, element):
        return "./xs:complexType[@name='{}']/xs:complexContent/xs:extension/xs:sequence/xs:element[@name]".format(element.attrib['name'])

    def get_ifcroot_parent_name(self):
        return "ex:Entity"

    # IFC2X3 does not seem to store complex attributes in the XSD file
    def get_complex_attributes(self, element, attributes = None):
        return []

extractor = IFC4Extractor("IFC4_ADD2.xsd")
#extractor = IFC2X3Extractor("IFC2X3.xsd")
extractor.extract()
extractor.export()
