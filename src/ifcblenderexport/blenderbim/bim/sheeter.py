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
        root.attrib['viewBox'] = '0 0 841 594'

        view = ET.SubElement(root, 'g')
        view.attrib['data-type'] = 'titleblock'
        titleblock = ET.SubElement(view, 'image')
        titleblock.attrib['xlink:href'] = '../templates/titleblock.svg'
        titleblock.attrib['x'] = '0'
        titleblock.attrib['y'] = '0'
        titleblock.attrib['width'] = '841'
        titleblock.attrib['height'] = '594'

        with open(sheet_path, 'w') as f:
            f.write(minidom.parseString(ET.tostring(root)).toprettyxml(indent='    '))

    def add_drawing(self, view_name, sheet_name):
        sheet_path = os.path.join(self.data_dir, 'sheets', sheet_name + '.svg')
        view_path = os.path.join(self.data_dir, 'diagrams', view_name + '.svg')

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
        view.attrib['data-type'] = 'drawing'
        view_width = self.convert_to_mm(view_root.attrib.get('width'))
        view_height = self.convert_to_mm(view_root.attrib.get('height'))

        background = ET.SubElement(view, 'image')
        background.attrib['xlink:href'] = '../diagrams/{}.png'.format(view_name)
        background.attrib['x'] = '30'
        background.attrib['y'] = '30'
        background.attrib['width'] = str(view_width)
        background.attrib['height'] = str(view_height)

        foreground = ET.SubElement(view, 'image')
        foreground.attrib['xlink:href'] = '../diagrams/{}.svg'.format(view_name)
        foreground.attrib['x'] = '30'
        foreground.attrib['y'] = '30'
        foreground.attrib['width'] = str(view_width)
        foreground.attrib['height'] = str(view_height)

        self.add_view_title(30, view_height+35, view)
        sheet_tree.write(sheet_path)

    def add_schedule(self, schedule_name, sheet_name):
        sheet_path = os.path.join(self.data_dir, 'sheets', sheet_name + '.svg')
        view_path = os.path.join(self.data_dir, 'schedules', schedule_name + '.svg')

        ET.register_namespace('', 'http://www.w3.org/2000/svg')
        ET.register_namespace('xlink', 'http://www.w3.org/1999/xlink')

        sheet_tree = ET.parse(sheet_path)
        sheet_root = sheet_tree.getroot()

        view_tree = ET.parse(view_path)
        view_root = view_tree.getroot()
        view_width = self.convert_to_mm(view_root.attrib.get('width'))
        view_height = self.convert_to_mm(view_root.attrib.get('height'))

        group = ET.SubElement(sheet_root, 'g')
        group.attrib['data-type'] = 'schedule'

        foreground = ET.SubElement(group, 'image')
        foreground.attrib['xlink:href'] = '../schedules/{}.svg'.format(schedule_name)
        foreground.attrib['x'] = '30'
        foreground.attrib['y'] = '30'
        foreground.attrib['width'] = str(view_width)
        foreground.attrib['height'] = str(view_height)

        self.add_view_title(30, view_height+35, group)
        sheet_tree.write(sheet_path)

    def add_view_title(self, x, y, parent):
        title_tree = ET.parse(os.path.join(self.data_dir, 'templates', 'view-title.svg'))
        title_root = title_tree.getroot()
        title = ET.SubElement(parent, 'image')
        title.attrib['xlink:href'] = '../templates/view-title.svg'
        title.attrib['x'] = str(x)
        title.attrib['y'] = str(y)
        title.attrib['width'] = str(self.convert_to_mm(title_root.attrib.get('width')))
        title.attrib['height'] = str(self.convert_to_mm(title_root.attrib.get('height')))


    def build(self, sheet_name):
        os.makedirs('{}build/{}/'.format(self.data_dir, sheet_name), exist_ok=True)

        sheet_path = '{}sheets/{}.svg'.format(self.data_dir, sheet_name)

        ET.register_namespace('', 'http://www.w3.org/2000/svg')
        ET.register_namespace('xlink', 'http://www.w3.org/1999/xlink')

        tree = ET.parse(sheet_path)
        root = tree.getroot()

        titleblock = root.findall('{http://www.w3.org/2000/svg}g[@data-type="titleblock"]')[0]
        image = titleblock.findall('{http://www.w3.org/2000/svg}image')[0]
        titleblock.append(self.parse_embedded_svg(image, {
            'number': sheet_name,
            'revision': 'A'
        }))
        titleblock.remove(image)

        self.group_number = 1
        self.build_drawings(root.findall('{http://www.w3.org/2000/svg}g[@data-type="drawing"]'), sheet_name)
        self.build_schedules(root.findall('{http://www.w3.org/2000/svg}g[@data-type="schedule"]'))

        with open('{}build/{}/{}.svg'.format(self.data_dir, sheet_name, sheet_name), 'wb') as output:
            tree.write(output)

    def build_drawings(self, drawings, sheet_name):
        for view in drawings:
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
                'no' : self.group_number,
                'name': ntpath.basename(foreground_path)[0:-4],
                'scale': self.scale
            }))

            for image in images:
                view.remove(image)

            self.group_number += 1

    def build_schedules(self, schedules):
        for group in schedules:
            images = group.findall('{http://www.w3.org/2000/svg}image')
            schedule = images[0]
            group_title = images[1]
            self.scale = 'NTS'

            group.append(self.parse_embedded_svg(schedule, {}))

            path = self.get_href(schedule)
            group.append(self.parse_embedded_svg(group_title, {
                'no' : self.group_number,
                'name': ntpath.basename(path)[0:-4],
                'scale': self.scale
            }))

            for image in images:
                group.remove(image)

            self.group_number += 1

    def get_href(self, element):
        return urllib.parse.unquote(element.attrib.get('{http://www.w3.org/1999/xlink}href'))

    def parse_embedded_svg(self, image, data):
        group = ET.Element('g')
        group.attrib['transform'] = 'translate({},{})'.format(
            self.convert_to_mm(image.attrib.get('x')),
            self.convert_to_mm(image.attrib.get('y')))
        svg_path = self.get_href(image)
        with open('{}sheets/{}'.format(self.data_dir, svg_path), 'r') as template:
            embedded = ET.fromstring(pystache.render(template.read(), data))
            # viewBox should not be nested
            embedded.attrib['viewBox'] = ''
            # TODO: This should not be in this function
            self.scale = embedded.attrib.get('data-scale')
            images = embedded.findall('{http://www.w3.org/2000/svg}image')
            for image in images:
                new_href = ntpath.basename(image.attrib.get('{http://www.w3.org/1999/xlink}href'))
                image.attrib['{http://www.w3.org/1999/xlink}href'] = new_href
        group.append(embedded)
        return group

    def convert_to_mm(self, value):
        # CSS is what defines these possibilities
        # https://www.w3.org/TR/SVG/refs.html#ref-css-values-3
        # https://www.w3.org/TR/css-values-3/#absolute-lengths
        # The relative units are not implemented. Go fish.
        if 'cm' in value:
            return float(value[0:-2]) * 10
        elif 'mm' in value:
            return float(value[0:-2])
        elif 'Q' in value:
            return float(value[0:-1]) * (1/40) * 10
        elif 'in' in value:
            return float(value[0:-2]) * 2.54 * 10
        elif 'pc' in value:
            return float(value[0:-2]) * (1/6) * 2.54 * 10
        elif 'pt' in value:
            return float(value[0:-2]) * (1/72) * 2.54 * 10
        elif 'px' in value:
            return float(value[0:-2]) * (1/96) * 2.54 * 10
        return float(value)

    def mm_to_px(self, value):
        return (value / 25.4) * 96
