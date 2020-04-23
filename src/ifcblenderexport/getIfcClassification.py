"""This script converts Graphisoft XML into an IFC file"""

import xml.etree.ElementTree as ET
import ifcopenshell

class IFC4Extractor:
    def __init__(self, xml_file):
        self.xml_file = xml_file
        self.tree = ET.parse(self.xml_file)
        self.root = self.tree.getroot()
        self.ns = {'xs': 'http://www.w3.org/2001/XMLSchema'}
        self.file = ifcopenshell.file()
        self.source_map = {
            'Uniclass 2015': 'RIBA Enterprises Ltd',
            'OmniClass': 'OmniClass'
        }
        self.reference_tokens_map = {
            'Uniclass 2015': ['_'],
            'OmniClass': ['-', ' ']
        }

    def extract(self):
        for system in self.tree.findall('Classification/System'):
            parent = self.file.create_entity('IfcClassification', **{
                'Source': self.source_map[system.find('Name').text],
                'Edition': system.find('EditionVersion').text,
                'EditionDate': self.get_edition_date(system),
                'Name': system.find('Name').text,
                'Description': system.find('Description').text,
                'Location': system.find('Source').text,
                'ReferenceTokens': self.reference_tokens_map[system.find('Name').text]
            })
            children = system.findall('Items/Item')
            self.get_children(children, parent)

    def get_children(self, children, parent):
        for child in children:
            reference = self.file.create_entity('IfcClassificationReference', **{
                'Identification': child.find('ID').text,
                'Name': child.find('Name').text,
                'ReferencedSource': parent,
                'Description': child.find('Description').text
            })
            children = child.find('Children')
            if children:
                self.get_children(children, reference)

    def get_edition_date(self, system):
        d = system.find('EditionDate')
        return '{}-{:02}-{:02}'.format(
            d.find('Year').text, int(d.find('Month').text), int(d.find('Day').text))

    def export(self, filename):
        self.file.write(filename)

filenames = [
    'Uniclass2015_Jan2020',
    'Omniclass_OCCS'
]
for filename in filenames:
    extractor = IFC4Extractor(f'{filename}.xml')
    extractor.extract()
    extractor.export(f'{filename}.ifc')
