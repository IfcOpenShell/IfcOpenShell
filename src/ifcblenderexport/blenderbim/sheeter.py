import xml.etree.ElementTree as ET
import pystache
import ntpath
import os
from shutil import copy
from xml.dom import minidom

class SheetBuilder:
    def __init__(self):
        self.data_dir = None

    def create(self, name):
        sheet_path = '{}sheets/{}.svg'.format(self.data_dir, name)
        root = ET.Element('svg')
        root.attrib['xmlns'] = 'http://www.w3.org/2000/svg'
        root.attrib['xmlns:xlink'] = 'http://www.w3.org/1999/xlink'
        root.attrib['id'] = 'root'
        root.attrib['version'] = '1.1'
        root.attrib['width'] = '841mm'
        root.attrib['height'] = '594mm'

        titleblock = ET.SubElement(root, 'image')
        titleblock.attrib['xlink:href'] = '../templates/titleblock.svg'
        titleblock.attrib['x'] = '0'
        titleblock.attrib['y'] = '0'
        titleblock.attrib['width'] = '841mm'
        titleblock.attrib['height'] = '594mm'

        with open(sheet_path, 'w') as f:
            f.write(minidom.parseString(ET.tostring(root)).toprettyxml(indent='    '))

    def add_view(self, view_name, sheet_name):
        sheet_path = '{}sheets/{}.svg'.format(self.data_dir, sheet_name)
        view_path = '{}diagrams/{}.svg'.format(self.data_dir, view_name)

        ET.register_namespace('', 'http://www.w3.org/2000/svg')
        ET.register_namespace('xlink', 'http://www.w3.org/1999/xlink')

        sheet_tree = ET.parse(sheet_path)
        sheet_root = sheet_tree.getroot()

        view_tree = ET.parse(view_path)
        view_root = view_tree.getroot()

        # The view is placed into a group with a background image element.
        # Although the foreground SVG already has a background, it is duplicated
        # here to accommodate browsers which do not nest images.
        view = ET.SubElement(sheet_root, 'g')

        background = ET.SubElement(view, 'image')
        background.attrib['xlink:href'] = '../diagrams/{}.png'.format(view_name)
        background.attrib['x'] = '0'
        background.attrib['y'] = '0'
        background.attrib['width'] = view_root.attrib.get('width')
        background.attrib['height'] = view_root.attrib.get('height')

        foreground = ET.SubElement(view, 'image')
        foreground.attrib['xlink:href'] = '../diagrams/{}.svg'.format(view_name)
        foreground.attrib['x'] = '0'
        foreground.attrib['y'] = '0'
        foreground.attrib['width'] = view_root.attrib.get('width')
        foreground.attrib['height'] = view_root.attrib.get('height')

        title = ET.SubElement(view, 'image')
        title.attrib['xlink:href'] = '../templates/view-title.svg'
        title.attrib['x'] = '0'
        title.attrib['y'] = view_root.attrib.get('height')

        sheet_tree.write(sheet_path)

    def build(self):
        sheet_path = '{}sheets/sheet1.svg'.format(self.data_dir)
        sheet_filename = ntpath.basename(sheet_path)
        sheet_name = sheet_filename[0:-4]

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
            source_background = '{}diagrams/{}.png'.format(self.data_dir, source_filename[0:-4])
            source_anchor = source.split('#')[1]
            dest_filename = '{}-{}.svg'.format(source_filename[0:-4], n)
            os.makedirs('{}build/{}/'.format(self.data_dir, sheet_name), exist_ok=True)
            with open('{}build/{}/{}'.format(self.data_dir, sheet_name, dest_filename), 'w') as out:
                with open('{}sheets/{}'.format(self.data_dir, source_path), 'r') as template:
                    out.write(pystache.render(template.read(), data[n]))
                    use.set('{http://www.w3.org/1999/xlink}href',
                        '{}#{}'.format(dest_filename, source_anchor))
            # TODO: hardcoded that all diagrams have a raster background
            if 'diagrams/' in source_path:
                copy(source_background, '{}build/{}/'.format(self.data_dir, sheet_name))
            n += 1

        with open('{}build/{}/{}'.format(self.data_dir, sheet_name, sheet_filename), 'wb') as output:
            tree.write(output)
