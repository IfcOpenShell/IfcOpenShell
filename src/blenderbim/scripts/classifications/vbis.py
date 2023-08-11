import csv
import os
import json
#import pystache
import subprocess
import ifcopenshell
from pathlib import Path

class Generator():
    def __init__(self):
        self.file = ifcopenshell.file(schema='IFC4')
        self.out_dir = './'

    def generate(self):
        classification = self.file.create_entity('IfcClassification', **{
            'Source': 'VBIS',
            'Edition': 'May-20',
            'EditionDate': '2020-05-01',
            'Name': 'VBIS',
            'Description': '',
            'Location': 'https://vbis.com.au/',
            'ReferenceTokens': ['-']
        })
        # We assume all the Excel spreadsheets are re-exported in CSV format
        for filename in Path('./').glob('*.csv'):
            with open(filename, newline='') as csvfile:
                reader = csv.reader(csvfile, delimiter=',', quotechar='"')
                name = None
                levels = [None, None, None, None]
                ref = classification
                for i, row in enumerate(reader):
                    if i <= 4:
                        continue
                    if row[0]:
                        name = row[0]
                    elif row[1]:
                        name = row[1]
                    elif row[2]:
                        name = row[2]
                    elif row[3]:
                        name = row[3]
                    ref = self.file.create_entity('IfcClassificationReference', **{
                        'Identification': row[4],
                        'Name': name
                    })
                    cur_level = len(row[4].split('-')) - 1
                    levels[cur_level] = ref
                    if cur_level == 0:
                        ref.ReferencedSource = classification
                    else:
                        ref.ReferencedSource = levels[cur_level-1]
        self.file.write('VBIS.ifc')

generator = Generator()
generator.generate()
