import xml.etree.ElementTree as ET
import pystache
import ntpath
import os

sheet_path = 'sheets/sheet1.svg'
sheet_filename = ntpath.basename(sheet_path)
sheet_name = sheet_filename[0:-4]

# hardcoded for testing
data = [
    {'number': 'ASDF', 'revision': 'A'},
    {},
    {'no': '01', 'name': 'HOUSE', 'scale': '1:100'},
    {},
    {'no': '02', 'name': 'ELEVATION', 'scale': '1:100'},
    {},
    {'no': '03', 'name': 'PLAN', 'scale': '1:100'},
    {},
    {'no': '04', 'name': 'SECTION', 'scale': '1:100'},
    ]
tree = ET.parse(sheet_path)
root = tree.getroot()
embedded_svgs = root.findall('{http://www.w3.org/2000/svg}svg')
n = 0
for svg in embedded_svgs:
    use = svg.findall('{http://www.w3.org/2000/svg}use')[0]
    source = use.attrib.get('{http://www.w3.org/1999/xlink}href')
    source_path = source.split('#')[0]
    source_filename = ntpath.basename(source_path)
    source_anchor = source.split('#')[1]
    dest_filename = '{}-{}.svg'.format(source_filename[0:-4], n)
    print(dest_filename)
    os.makedirs('build/refs/{}/'.format(sheet_name), exist_ok=True)
    with open('build/refs/{}/{}'.format(sheet_name, dest_filename), 'w') as out:
        with open('sheets/{}'.format(source_path), 'r') as template:
            out.write(pystache.render(template.read(), data[n]))
            use.set('{http://www.w3.org/1999/xlink}href',
                'refs/{}/{}#{}'.format(sheet_name, dest_filename, source_anchor))
    n += 1

with open('build/{}'.format(sheet_filename), 'wb') as output:
    tree.write(output)
