from behave.__main__ import main as behave_main
import xml.etree.ElementTree as ET
import pystache

behave_main(['features', '--junit', '--junit-directory', 'junit/'])

with open('junit/template.html') as template:
    root = ET.parse('junit/TESTS-example.xml').getroot()
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
    with open('junit/results.html', 'w') as out:
        out.write(pystache.render(template.read(), data))
