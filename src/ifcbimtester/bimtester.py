# This can be packaged with `pyinstaller --onefile --clean --icon=icon.ico bimtester.py`

from behave.__main__ import main as behave_main
import behave.formatter.pretty # Needed for pyinstaller to package it
import xml.etree.ElementTree as ET
import ifcopenshell
import pystache
import os
import sys
import json
from pathlib import Path

def run_tests():
    behave_main(['features', '--junit', '--junit-directory', 'junit/'])
    print('# All tests have finished. Generating HTML reports now.')
    if not os.path.exists('report'):
        os.mkdir('report')
    for file in os.listdir('junit/'):
        if not file.endswith('.xml'):
            continue
        root = ET.parse('junit/{}'.format(file)).getroot()
        data = {
            'report_name': root.get('name'),
            'testcases': []
            }
        for testcase in root.findall('testcase'):
            steps = []
            system_out = testcase.findall('system-out')[0].text.splitlines()
            for line in system_out:
                if line.strip()[0:5] in ['Given', 'Then ', 'When ']:
                    is_success = True if ' ... passed in ' in line else False
                    steps.append({
                        'name': line.strip().split(' ... ')[0],
                        'time': line.strip().split(' ... ')[1],
                        'is_success': is_success
                        })
            data['testcases'].append({
                'name': testcase.get('name'),
                'is_success': testcase.get('status') == 'passed',
                'time': testcase.get('time'),
                'steps': steps,
                'total_passes': len([s for s in steps if s['is_success'] == True]),
                'total_steps': len(steps)
                })
        with open('report/{}.html'.format(file[0:-4]), 'w') as out:
            with open('features/template.html') as template:
                out.write(pystache.render(template.read(), data))


class TestPurger:
    def __init__(self):
        self.file = None

    def purge(self):
        for filename in Path('features/').glob('*.feature'):
            with open(filename, 'r') as feature_file:
                old_file = feature_file.readlines()
            with open(filename, 'w') as new_file:
                for line in old_file:
                    is_purged = False
                    if 'Given the IFC file ' in line and 'exists' not in line:
                        filename = line.split('"')[1]
                        print('Loading file {} ...'.format(filename))
                        self.file = ifcopenshell.open(filename)
                    if line.strip()[0:4] == 'Then':
                        words = line.strip().split()
                        for word in words:
                            if self.is_a_global_id(word):
                                if not self.does_global_id_exist(word):
                                    print('Test for {} purged ...'.format(word))
                                    is_purged = True
                    if not is_purged:
                        new_file.write(line)

    def is_a_global_id(self, word):
        return word[0] in ['0', '1', '2', '3'] and len(word) == 22

    def does_global_id_exist(self, global_id):
        try:
            self.file.by_guid(global_id)
            return True
        except:
            return False

print('# BIMTester')
print('''
BIMTester is free software developed under the IfcOpenShell and BlenderBIM
projects. BIMTester allows advanced, fast, and human-readable BIM data analysis,
and can be run automatically on open-source BIM servers. To learn more, visit:

 - http://ifcopenshell.org
 - https://blenderbim.org

To run, a `features/` folder is required in the current folder.

Please choose from the following options:

 1. Run all tests
 2. Purge non-existent element tests
''')

value = input('Please select an option: [1-2] ')
if value == '1':
    run_tests()
elif value == '2':
    TestPurger().purge()
else:
    quit()
print('# All tasks are complete :-)')
input('Press <enter> to quit.')
