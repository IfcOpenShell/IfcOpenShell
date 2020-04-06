# Unix:
# $ pyinstaller --onefile --clean --icon=icon.ico --add-data "features:features" bimtester.py`
# Windows:
# $ pyinstaller --onefile --clean --icon=icon.ico --add-data "features;features" bimtester.py`

from behave.__main__ import main as behave_main
import behave.formatter.pretty # Needed for pyinstaller to package it
import xml.etree.ElementTree as ET
import ifcopenshell
import pystache
import os
import sys
import json
import argparse
import csv
import re
import shutil
from pathlib import Path


try:
    # PyInstaller creates a temp folder and stores path in _MEIPASS
    base_path = sys._MEIPASS
    is_dist = True
except Exception:
    base_path = os.path.abspath(".")
    is_dist = False


def get_resource_path(relative_path):
    return os.path.join(base_path, relative_path)


def run_tests(args):
    if not get_features(args):
        sys.exit('No requirements could be found to check.')
    behave_args = [get_resource_path('features')]
    if args.advanced_arguments:
        behave_args.extend(args.advanced_arguments.split())
    else:
        behave_args.extend(['--junit', '--junit-directory', args.junit_directory])
    behave_main(behave_args)
    print('# All tests are finished.')


def get_features(args):
    has_features = False
    if os.path.exists('features') and is_dist:
        shutil.copytree('features', get_resource_path('features'))
        has_features = True
    for f in os.listdir('.'):
        if not f.endswith('.requirement'):
            continue
        if args.feature and args.feature != f:
            continue
        has_features = True
        shutil.copyfile(f, os.path.join(
            get_resource_path('features'),
            os.path.basename(f)[0:-len('.requirement')] + '.feature'))
    return has_features


def generate_report(args):
    print('# Generating HTML reports now.')
    if not os.path.exists('report'):
        os.mkdir('report')
    if not os.path.exists(args.junit_directory):
        os.mkdir(args.junit_directory)
    for f in os.listdir(args.junit_directory):
        if not f.endswith('.xml'):
            continue
        print(f'Processing {f} ...')
        root = ET.parse('{}{}'.format(args.junit_directory, f)).getroot()
        data = {
            'report_name': root.get('name'),
            'testcases': []
            }
        for testcase in root.findall('testcase'):
            steps = []
            system_out = testcase.findall('system-out')[0].text.splitlines()
            for line in system_out:
                if line.strip()[0:4] in ['Give', 'Then', 'When', 'And '] \
                        or line.strip()[0:2] == '* ':
                    is_success = True if ' ... passed in ' in line else False
                    name, time = line.strip().split(' ... ')
                    if name[0:2] == '* ':
                        name = name[2:]
                    steps.append({
                        'name': name,
                        'time': time,
                        'is_success': is_success
                    })
            total_passes = len([s for s in steps if s['is_success'] == True])
            total_steps = len(steps)
            pass_rate = round((total_passes / total_steps) * 100)
            data['testcases'].append({
                'name': testcase.get('name'),
                'is_success': testcase.get('status') == 'passed',
                'time': testcase.get('time'),
                'steps': steps,
                'total_passes': total_passes,
                'total_steps': total_steps,
                'pass_rate': pass_rate
                })
        with open('report/{}.html'.format(f[0:-4]), 'w') as out:
            with open(get_resource_path('features/template.html')) as template:
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
    '-j',
    '--junit-directory',
    type=str,
    help='Specify your own JUnit directory',
    default='junit/')
parser.add_argument(
    '-f',
    '--feature',
    type=str,
    help='Specify a requirements feature file to test',
    default='')
parser.add_argument(
    '-a',
    '--advanced-arguments',
    type=str,
    help='Specify your own arguments to Python\'s Behave',
    default='')
args = parser.parse_args()

if args.purge:
    TestPurger().purge()
elif args.report:
    generate_report(args)
else:
    run_tests(args)

print('# All tasks are complete :-)')
