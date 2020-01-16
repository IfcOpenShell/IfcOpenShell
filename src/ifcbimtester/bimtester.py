# This can be packaged with `pyinstaller --onefile --clean --icon=icon.ico bimtester.py`

from behave.__main__ import main as behave_main
import behave.formatter.pretty # Needed for pyinstaller to package it
import xml.etree.ElementTree as ET
import ifcopenshell
import pystache
import os
import sys
import json
import argparse
from pathlib import Path

def run_tests(args):
    behave_args = ['features', '--junit', '--junit-directory', 'junit/']
    if args.advanced_arguments:
        behave_args = args.advanced_arguments.split()
    behave_main(behave_args)
    print('# All tests are finished.')
    if args.report:
        generate_report()

def generate_report():
    print('# Generating HTML reports now.')
    if not os.path.exists('report'):
        os.mkdir('report')
    if not os.path.exists('junit'):
        os.mkdir('junit')
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
                if line.strip()[0:4] in ['Give', 'Then', 'When', 'And ']:
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

parser = argparse.ArgumentParser(
    description='Runs unit tests for BIM data')
parser.add_argument(
    '-p',
    '--purge',
    action='store_true',
    help='Purge tests of deleted elements')
parser.add_argument(
    '-r',
    '--report',
    action='store_true',
    help='Generate a HTML report')
parser.add_argument(
    '-a',
    '--advanced-arguments',
    type=str,
    help='Specify your own arguments to Python\'s Behave',
    default='')
args = parser.parse_args()

if not os.path.exists('features'):
    sys.exit('''
    BIMTester requires a features folder to exist within the current folder.
    Visit https://blenderbim.org/ to learn more about how to use BIMTester.
    ''')

if args.purge:
    TestPurger().purge()
else:
    run_tests(args)

print('# All tasks are complete :-)')
