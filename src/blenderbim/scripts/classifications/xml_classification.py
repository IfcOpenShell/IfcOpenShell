# coding=utf-8

"""This script converts Graphisoft XML into an IFC file"""

import xml.etree.ElementTree as ET
import ifcopenshell
import os

class IFC4Extractor:
    def __init__(self, xml_file):
        self.xml_file = xml_file
        self.tree = ET.parse(self.xml_file)
        self.root = self.tree.getroot()
        self.ns = {'xs': 'http://www.w3.org/2001/XMLSchema'}
        self.file = ifcopenshell.file()
        self.data = {
            'BB/SfB (3/4 cijfers)': {'source': 'Regie der Gebouwen', 'tokens': ['.']},
            'BIMTypeCode': {'source': 'BIMStockholm', 'tokens': None},
            'Common Arrangement of Work Sections (CAWS)': {'source': 'NBS', 'tokens': ['/']},
            'CBI Classification - Level 2': {'source': 'Masterspec', 'tokens': None},
            'CBI Classification - Level 4': {'source': 'Masterspec', 'tokens': None},
            'Rumsfunktionskoder CC001 - 001': {'source': 'BIMAlliance', 'tokens': ['-']},
            'CCS': {'source': 'Molio', 'tokens': None},
            'CCTB': {'source': 'CCT-Bâtiments', 'tokens': ['.']},
            'Funktionskoder Regionservice CD001 - 001': {'source': 'BIMAlliance', 'tokens': None},
            'Rumsfunktion Blekinge CD002 - 001': {'source': 'BIMAlliance', 'tokens': None},
            'EcoQuaestor Codetabel': {'source': 'EcoQuaestor', 'tokens': ['.', '-']},
            'GuBIMclass CA': {'source': 'GuBIMClass', 'tokens': ['.']},
            'GuBIMclass ES': {'source': 'GuBIMClass', 'tokens': ['.']},
            'MasterFormat': {'source': 'CSI', 'tokens': [' ', '.']},
            'NATSPEC Worksections': {'source': 'NATSPEC', 'tokens': None},
            'NBS Create': {'source': 'NBS', 'tokens': ['_', '/']},
            'NL/SfB (4 cijfers)': {'source': 'BIMLoket', 'tokens': ['.']},
            'NS 3451 - Bygningsdelstabell': {'source': 'Standard Norge', 'tokens': None},
            'OmniClass': {'source': 'OmniClass', 'tokens': ['-', ' ']},
            'ÖNORM 6241-2': {'source': 'freeBIM 2', 'tokens': None},
            'RICS NRM1': {'source': 'RICS', 'tokens': ['.']},
            'RICS NRM3': {'source': 'RICS', 'tokens': ['.']},
            'SFG20': {'source': 'SFG20', 'tokens': ['-']},
            'SINAPI': {'source': 'Caixa', 'tokens': ['/']},
            'STABU-Element': {'source': 'STABU', 'tokens': ['.']},
            'TALO 2000 Building Component Classification': {'source': 'Rakennustieto', 'tokens': ['.']},
            'TALO 2000 Hankenimikkeistö': {'source': 'Rakennustieto', 'tokens': ['.']},
            'Uniclass': {'source': 'RIBA Enterprises Ltd', 'tokens': ['_']},
            'Uniclass 2015': {'source': 'RIBA Enterprises Ltd', 'tokens': ['_']},
            'UniFormat': {'source': 'UniFormat', 'tokens': ['.']},
            'Uniformat': {'source': 'UniFormat', 'tokens': ['.']},
            'VMSW': {'source': 'VMSW', 'tokens': ['.']}
        }

    def extract(self):
        for system in self.tree.findall('Classification/System'):
            project = self.file.create_entity('IfcProjectLibrary', Name=system.find('Name').text)
            parent = self.file.create_entity('IfcClassification', **{
                'Source': self.data[system.find('Name').text]['source'],
                'Edition': system.find('EditionVersion').text,
                'EditionDate': self.get_edition_date(system),
                'Name': system.find('Name').text,
                'Description': system.find('Description').text,
                'Location': system.find('Source').text,
                'ReferenceTokens': self.data[system.find('Name').text]['tokens']
            })
            self.file.createIfcRelAssociatesClassification(
                ifcopenshell.guid.new(), None, None, None, [project], parent)
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

for filename in os.listdir('xml/'):
    extractor = IFC4Extractor(f'xml/{filename}')
    extractor.extract()
    extractor.export(f'ifc/{filename[0:-3]}ifc')
