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
import webbrowser
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
        print('No requirements could be found to check.')
        return False
    behave_args = [get_resource_path('features')]
    if args.advanced_arguments:
        behave_args.extend(args.advanced_arguments.split())
    else:
        behave_args.extend(['--junit', '--junit-directory', args.junit_directory])
    behave_main(behave_args)
    print('# All tests are finished.')
    return True


def get_features(args):
    has_features = False
    if args.feature:
        shutil.copyfile(args.feature, os.path.join(
            get_resource_path('features'),
            os.path.basename(args.feature)[0:-len('.requirement')] + '.feature'))
        return True
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
        filenames = []
        if os.path.exists('features'):
            for filename in Path('features/').glob('*.feature'):
                filenames.append(filename)
        for f in os.listdir('.'):
            if f.endswith('.requirement'):
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


parser = argparse.ArgumentParser(
    description='Runs unit tests for BIM data')
parser.add_argument(
    '-p',
    '--purge',
    action='store_true',
    help='Purge tests of deleted elements')
parser.add_argument(
    '-c',
    '--cli',
    action='store_true',
    help='Run without a GUI, just as a CLI')
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

if args.cli:
    if args.purge:
        TestPurger().purge()
    elif args.report:
        generate_report(args)
    else:
        run_tests(args)
    print('# All tasks are complete :-)')
    sys.exit()

import tkinter
import tkinter.filedialog
import tkinter.messagebox

class Application(tkinter.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.title('BIMTester')
        self.pack()
        self.create_widgets()
        self.directory = None

    def create_widgets(self):
        self.top_frame = tkinter.Frame(self, padx=5, pady=5)
        self.top_frame.pack(side='top')
        self.bottom_frame = tkinter.Frame(self, padx=5, pady=5)
        self.bottom_frame.pack(side='bottom')

        self.description = tkinter.Label(self.top_frame)
        self.description['text'] = 'BIMTester'
        self.description.pack(side='top')

        self.browse = tkinter.Button(self.bottom_frame)
        self.browse['text'] = 'Load Directory'
        self.browse['command'] = self.load_file
        self.browse.pack(side='left')

        self.execute = tkinter.Button(self.bottom_frame)
        self.execute['text'] = 'Check Requirements'
        self.execute['command'] = self.check_requirements
        self.execute.pack(side='right')

    def load_file(self):
        self.directory = tkinter.filedialog.askdirectory(parent=root, title='Choose a directory')
        if self.directory:
            os.chdir(self.directory)

    def check_requirements(self):
        if not self.directory:
            tkinter.messagebox.showerror(message='Please select a directory first.')
            return
        if run_tests(args):
            generate_report(args)
            webbrowser.open(os.path.join(self.directory, 'report/'))
        else:
            tkinter.messagebox.showerror(message='No requirements were found or they were not able to be checked.')

root = tkinter.Tk()
app = Application(master=root)
app.mainloop()
