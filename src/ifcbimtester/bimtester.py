#!/usr/bin/env python3
# Unix:
# $ pyinstaller --onefile --clean --icon=icon.ico --add-data "features:features" bimtester.py`
# Windows:
# $ pyinstaller --onefile --clean --icon=icon.ico --add-data "features;features" bimtester.py`

from behave.__main__ import main as behave_main
import behave.formatter.pretty # Needed for pyinstaller to package it
import ifcopenshell
import pystache
import os
import sys
import json
import argparse
import csv
import re
import shutil
import webbrowser
import datetime
from pathlib import Path

try:
    # PyInstaller creates a temp folder and stores path in _MEIPASS
    base_path = sys._MEIPASS
except Exception:
    base_path = os.path.dirname(os.path.realpath(__file__))


def get_resource_path(relative_path):
    return os.path.join(base_path, relative_path)


def run_tests(args):
    if not get_features(args):
        print('No features could be found to check.')
        return False
    behave_args = [get_resource_path('features')]
    if args['advanced_arguments']:
        behave_args.extend(args['advanced_arguments'].split())
    elif not args['console']:
        behave_args.extend(['--format', 'json.pretty', '--outfile', 'report/report.json'])
    behave_main(behave_args)
    print('# All tests are finished.')
    return True


def get_features(args):
    current_path = os.path.abspath(".")
    features_dir = get_resource_path('features')
    for f in os.listdir(features_dir):
        if f.endswith('.feature'):
            os.remove(os.path.join(features_dir, f))
    if args['feature']:
        shutil.copyfile(args['feature'], os.path.join(
            get_resource_path('features'),
            os.path.basename(args['feature'])))
        return True
    if os.path.exists('features'):
        shutil.copytree('features', get_resource_path('features'))
        return True
    has_features = False
    for f in os.listdir('.'):
        if not f.endswith('.feature'):
            continue
        if args['feature'] and args['feature'] != f:
            continue
        has_features = True
        shutil.copyfile(f, os.path.join(
            get_resource_path('features'),
            os.path.basename(f)))
    return has_features


def generate_report():
    print('# Generating HTML reports now.')
    if not os.path.exists('report'):
        os.mkdir('report')
    report_path = 'report/report.json'
    if not os.path.exists(report_path):
        return print('No report data was found.')
    report = json.loads(open(report_path).read())
    for feature in report:
        file_name = os.path.basename(feature['location']).split(':')[0]
        data = {
            'file_name': file_name,
            'time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'name': feature['name'],
            'description': feature['description'],
            'is_success': feature['status'] == 'passed',
            'scenarios': []
            }
        for scenario in feature['elements']:
            steps = []
            total_duration = 0
            for step in scenario['steps']:
                if 'result' in step:
                    total_duration += step['result']['duration']
                name = step['name']
                if 'match' in step and 'arguments' in step['match']:
                    for a in step['match']['arguments']:
                        name = name.replace(a['value'], '<b>' + a['value'] + '</b>')
                if 'result' not in step or step['result']['status'] == 'undefined':
                    step['result'] = {}
                    step['result']['status'] = 'undefined'
                    step['result']['duration'] = 0
                    step['result']['error_message'] = 'This requirement has not yet been specified.'
                steps.append({
                    'name': name,
                    'time': round(step['result']['duration'], 2),
                    'is_success': step['result']['status'] == 'passed',
                    'is_unspecified': 'result' not in step or step['result']['status'] == 'undefined',
                    'error_message': None if step['result']['status'] == 'passed' else step['result']['error_message']
                })
            total_passes = len([s for s in steps if s['is_success'] == True])
            total_steps = len(steps)
            pass_rate = round((total_passes / total_steps) * 100)
            data['scenarios'].append({
                'name': scenario['name'],
                'is_success': scenario['status'] == 'passed',
                'time': round(total_duration, 2),
                'steps': steps,
                'total_passes': total_passes,
                'total_steps': total_steps,
                'pass_rate': pass_rate
                })
        data['total_passes'] = sum([s['total_passes'] for s in data['scenarios']])
        data['total_steps'] = sum([s['total_steps'] for s in data['scenarios']])
        data['pass_rate'] = round((data['total_passes'] / data['total_steps']) * 100)

        with open('report/{}.html'.format(file_name), 'w') as out:
            with open(get_resource_path('features/template.html')) as template:
                out.write(pystache.render(template.read(), data))


class TestPurger:
    def __init__(self):
        self.file = None

    def purge(self):
        filenames = []
        if os.path.exists('features'):
            for filename in Path('features/').glob('*.feature'):
                filenames.append(filename)
        for f in os.listdir('.'):
            if f.endswith('.feature'):
                filenames.append(f)

        for filename in filenames:
            with open(filename, 'r') as feature_file:
                old_file = feature_file.readlines()
            with open(filename, 'w') as new_file:
                for line in old_file:
                    is_purged = False
                    if 'The IFC file "' in line and '" must be provided' in line:
                        filename = line.split('"')[1]
                        print('Loading file {} ...'.format(filename))
                        self.file = ifcopenshell.open(filename)
                    if line.strip()[0:2] == '* ':
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


if __name__ == '__main__':
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
        '-c',
        '--console',
        action='store_true',
        help='Show results in the console')
    parser.add_argument(
        '-f',
        '--feature',
        type=str,
        help='Specify a feature file to test',
        default='')
    parser.add_argument(
        '-a',
        '--advanced-arguments',
        type=str,
        help='Specify your own arguments to Python\'s Behave',
        default='')
    args = vars(parser.parse_args())

    if args['purge']:
        TestPurger().purge()
    elif args['report']:
        generate_report()
    else:
        run_tests(args)
    print('# All tasks are complete :-)')
