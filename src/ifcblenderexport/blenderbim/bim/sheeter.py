import xml.etree.ElementTree as ET
import urllib.parse
import pystache
import ntpath
import os
from shutil import copy
from xml.dom import minidom

class SheetBuilder:
    def __init__(self):
        self.data_dir = None
        self.scale = 'NTS'

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

    def build(self, sheet_name):
        os.makedirs('{}build/{}/'.format(self.data_dir, sheet_name), exist_ok=True)

        sheet_path = '{}sheets/{}.svg'.format(self.data_dir, sheet_name)

        ET.register_namespace('', 'http://www.w3.org/2000/svg')
        ET.register_namespace('xlink', 'http://www.w3.org/1999/xlink')

        tree = ET.parse(sheet_path)
        root = tree.getroot()

        titleblock = root.findall('{http://www.w3.org/2000/svg}image')[0]
        root.append(self.parse_embedded_svg(titleblock, {
            'number': sheet_name,
            'revision': 'A'
        }))
        root.remove(titleblock)

        views = root.findall('{http://www.w3.org/2000/svg}g')

        view_number = 1
        for view in views:
            images = view.findall('{http://www.w3.org/2000/svg}image')
            background = images[0]
            foreground = images[1]
            view_title = images[2]
            self.scale = 'NTS'

            # Add foreground
            view.append(self.parse_embedded_svg(foreground, {}))

            # Add background
            background_path = '{}sheets/{}'.format(self.data_dir, self.get_href(background))
            copy(background_path, '{}build/{}/'.format(self.data_dir, sheet_name))

            # Add view title
            foreground_path = self.get_href(foreground)
            view.append(self.parse_embedded_svg(view_title, {
                'no' : view_number,
                'name': ntpath.basename(foreground_path)[0:-4],
                'scale': self.scale
            }))

            for image in images:
                view.remove(image)

            view_number += 1

        with open('{}build/{}/{}.svg'.format(self.data_dir, sheet_name, sheet_name), 'wb') as output:
            tree.write(output)

    def get_href(self, element):
        return urllib.parse.unquote(element.attrib.get('{http://www.w3.org/1999/xlink}href'))

    def parse_embedded_svg(self, image, data):
        group = ET.Element('g')
        group.attrib['transform'] = 'translate({},{})'.format(image.attrib.get('x'), image.attrib.get('y'))
        svg_path = self.get_href(image)
        with open('{}sheets/{}'.format(self.data_dir, svg_path), 'r') as template:
            embedded = ET.fromstring(pystache.render(template.read(), data))
            self.scale = embedded.attrib.get('data-scale')
            images = embedded.findall('{http://www.w3.org/2000/svg}image')
            for image in images:
                new_href = ntpath.basename(image.attrib.get('{http://www.w3.org/1999/xlink}href'))
                image.attrib['{http://www.w3.org/1999/xlink}href'] = new_href
        group.append(embedded)
        return group
