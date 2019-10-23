# This can be packaged with `pyinstaller --onefile --clean --icon=icon.ico bimtester.py`

from behave.__main__ import main as behave_main
import behave.formatter.pretty # Needed for pyinstaller to package it
import xml.etree.ElementTree as ET
import ifcopenshell # Needed for pyinstaller to package it
import pystache
import os
import sys

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


print('# BIMTester')
print('''
BIMTester is free software developed under the IfcOpenShell and BlenderBIM
projects. BIMTester allows advanced, fast, and human-readable BIM data analysis,
and can be run automatically on open-source BIM servers. To learn more, visit:

 - http://ifcopenshell.org
 - https://blenderbim.org

To run, a `features/` folder is required in the current folder.
''')

value = input('Would you like to run the tests? [Y/n] ')
if value == 'n':
    quit()
run_tests()
print('# All tests and reports are complete :-)')
input('Press <enter> to quit.')
