# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of BlenderBIM Add-on.
#
# BlenderBIM Add-on is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# BlenderBIM Add-on is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with BlenderBIM Add-on.  If not, see <http://www.gnu.org/licenses/>.

import os
import ntpath
import pystache
import urllib.parse
import xml.etree.ElementTree as ET
import blenderbim.tool as tool
from shutil import copy
from xml.dom import minidom


class SheetBuilder:
    def __init__(self):
        self.data_dir = None
        self.scale = "NTS"

    def create(self, sheet_path, titleblock_name):
        root = ET.Element("svg")
        root.attrib["xmlns"] = "http://www.w3.org/2000/svg"
        root.attrib["xmlns:xlink"] = "http://www.w3.org/1999/xlink"
        root.attrib["id"] = "root"
        root.attrib["version"] = "1.1"

        view_root = ET.parse(
            os.path.join(self.data_dir, "templates", "titleblocks", titleblock_name + ".svg")
        ).getroot()
        view_width = self.convert_to_mm(view_root.attrib.get("width"))
        view_height = self.convert_to_mm(view_root.attrib.get("height"))
        view = ET.SubElement(root, "g")
        view.attrib["data-type"] = "titleblock"
        titleblock = ET.SubElement(view, "image")
        titleblock.attrib["xlink:href"] = "../templates/titleblocks/" + titleblock_name + ".svg"
        titleblock.attrib["x"] = "0"
        titleblock.attrib["y"] = "0"
        titleblock.attrib["width"] = str(view_width)
        titleblock.attrib["height"] = str(view_height)

        root.attrib["width"] = "{}mm".format(view_width)
        root.attrib["height"] = "{}mm".format(view_height)
        root.attrib["viewBox"] = "0 0 {} {}".format(view_width, view_height)

        with open(sheet_path, "w") as f:
            f.write(minidom.parseString(ET.tostring(root)).toprettyxml(indent="    "))

    def add_drawing(self, reference, drawing, sheet):
        filename = drawing.Name
        sheet_name = os.path.splitext(os.path.basename(tool.Drawing.get_document_uri(sheet)))[0]
        sheet_dir = os.path.join(self.data_dir, "sheets")
        drawing_dir = os.path.join(self.data_dir, "diagrams")
        sheet_path = os.path.join(sheet_dir, sheet_name + ".svg")
        drawing_path = os.path.join(drawing_dir, filename + ".svg")
        underlay_path = os.path.join(drawing_dir, filename + "-underlay.png")

        if not os.path.isfile(sheet_path):
            raise FileNotFoundError

        ET.register_namespace("", "http://www.w3.org/2000/svg")
        ET.register_namespace("xlink", "http://www.w3.org/1999/xlink")

        sheet_tree = ET.parse(sheet_path)
        sheet_root = sheet_tree.getroot()

        view_tree = ET.parse(drawing_path)
        view_root = view_tree.getroot()

        # The view is placed into a group with a background image element.
        # Although the foreground SVG already has a background, it is duplicated
        # here to accommodate browsers which do not nest images.
        view = ET.SubElement(sheet_root, "g")
        view.attrib["data-type"] = "drawing"
        view.attrib["data-id"] = str(reference.id())
        view.attrib["data-drawing"] = drawing.GlobalId
        view_width = self.convert_to_mm(view_root.attrib.get("width"))
        view_height = self.convert_to_mm(view_root.attrib.get("height"))

        if os.path.isfile(underlay_path):
            background = ET.SubElement(view, "image")
            background.attrib["data-type"] = "background"
            background.attrib["xlink:href"] = os.path.relpath(underlay_path, sheet_dir)
            background.attrib["x"] = "30"
            background.attrib["y"] = "30"
            background.attrib["width"] = str(view_width)
            background.attrib["height"] = str(view_height)

        if os.path.isfile(drawing_path):
            foreground = ET.SubElement(view, "image")
            foreground.attrib["data-type"] = "foreground"
            foreground.attrib["xlink:href"] = os.path.relpath(drawing_path, sheet_dir)
            foreground.attrib["x"] = "30"
            foreground.attrib["y"] = "30"
            foreground.attrib["width"] = str(view_width)
            foreground.attrib["height"] = str(view_height)

        self.add_view_title(30, view_height + 35, view)
        sheet_tree.write(sheet_path)

    def remove_drawing(self, reference, sheet):
        ET.register_namespace("", "http://www.w3.org/2000/svg")

        sheet_path = tool.Drawing.get_document_uri(sheet)
        sheet_tree = ET.parse(sheet_path)
        sheet_root = sheet_tree.getroot()

        for g in sheet_root.findall("{http://www.w3.org/2000/svg}g"):
            if g.attrib.get("data-id") == str(reference.id()):
                sheet_root.remove(g)
                break

        sheet_tree.write(sheet_path)

    def add_schedule(self, reference, schedule, sheet):
        view_path = tool.Drawing.get_document_uri(schedule)
        schedule_name = os.path.splitext(os.path.basename(view_path))[0]
        sheet_path = tool.Drawing.get_document_uri(sheet)

        ET.register_namespace("", "http://www.w3.org/2000/svg")
        ET.register_namespace("xlink", "http://www.w3.org/1999/xlink")

        sheet_tree = ET.parse(sheet_path)
        sheet_root = sheet_tree.getroot()

        view_tree = ET.parse(view_path)
        view_root = view_tree.getroot()
        view_width = self.convert_to_mm(view_root.attrib.get("width"))
        view_height = self.convert_to_mm(view_root.attrib.get("height"))

        view = ET.SubElement(sheet_root, "g")
        view.attrib["data-type"] = "schedule"
        view.attrib["data-id"] = str(reference.id())
        view.attrib["data-schedule"] = str(schedule.id())

        foreground = ET.SubElement(view, "image")
        foreground.attrib["data-type"] = "table"
        foreground.attrib["xlink:href"] = "../schedules/{}.svg".format(schedule_name)
        foreground.attrib["x"] = "30"
        foreground.attrib["y"] = "30"
        foreground.attrib["width"] = str(view_width)
        foreground.attrib["height"] = str(view_height)

        self.add_view_title(30, view_height + 35, view)
        sheet_tree.write(sheet_path)

    def add_view_title(self, x, y, parent):
        title_tree = ET.parse(os.path.join(self.data_dir, "templates", "view-title.svg"))
        title_root = title_tree.getroot()
        title = ET.SubElement(parent, "image")
        title.attrib["data-type"] = "view-title"
        title.attrib["xlink:href"] = "../templates/view-title.svg"
        title.attrib["x"] = str(x)
        title.attrib["y"] = str(y)
        title.attrib["width"] = str(self.convert_to_mm(title_root.attrib.get("width")))
        title.attrib["height"] = str(self.convert_to_mm(title_root.attrib.get("height")))

    def build(self, sheet):
        sheet_name = os.path.splitext(os.path.basename(tool.Drawing.get_document_uri(sheet)))[0]
        os.makedirs(os.path.join(self.data_dir, "build", sheet_name), exist_ok=True)

        sheet_path = os.path.join(self.data_dir, "sheets", f"{sheet_name}.svg")

        ET.register_namespace("", "http://www.w3.org/2000/svg")
        ET.register_namespace("xlink", "http://www.w3.org/1999/xlink")

        tree = ET.parse(sheet_path)
        root = tree.getroot()

        self.build_titleblock(root, sheet)
        self.build_drawings(root, sheet)
        self.build_schedules(root)

        with open(os.path.join(self.data_dir, "build", sheet_name, f"{sheet_name}.svg"), "wb") as output:
            tree.write(output)

    def build_titleblock(self, root, sheet):
        titleblock = root.findall('{http://www.w3.org/2000/svg}g[@data-type="titleblock"]')[0]
        image = titleblock.findall("{http://www.w3.org/2000/svg}image")[0]
        titleblock.append(self.parse_embedded_svg(image, sheet.get_info()))
        titleblock.remove(image)

    def build_drawings(self, root, sheet):
        sheet_name = os.path.splitext(os.path.basename(tool.Drawing.get_document_uri(sheet)))[0]

        for view in root.findall('{http://www.w3.org/2000/svg}g[@data-type="drawing"]'):
            reference = tool.Ifc.get().by_id(int(view.attrib["data-id"]))
            drawing = tool.Ifc.get().by_id(view.attrib["data-drawing"])

            images = view.findall("{http://www.w3.org/2000/svg}image")

            background = None
            foreground = None
            view_title = None

            for image in images:
                if image.attrib["data-type"] == "background":
                    background = image
                elif image.attrib["data-type"] == "foreground":
                    foreground = image
                elif image.attrib["data-type"] == "view-title":
                    view_title = image

            if foreground is not None:
                view.append(self.parse_embedded_svg(foreground, {}))

            if background is not None:
                background_path = os.path.join(self.data_dir, "sheets", self.get_href(background))
                copy(background_path, os.path.join(self.data_dir, "build", sheet_name))

            if view_title is not None:
                foreground_path = self.get_href(foreground)
                data = reference.get_info()
                if not data["Name"]:
                    data["Name"] = ntpath.basename(foreground_path)[0:-4]
                data["Scale"] = tool.Drawing.get_drawing_human_scale(drawing)
                view.append(self.parse_embedded_svg(view_title, data))

            for image in images:
                view.remove(image)

    def build_schedules(self, root):
        for view in root.findall('{http://www.w3.org/2000/svg}g[@data-type="schedule"]'):
            reference = tool.Ifc.get().by_id(int(view.attrib["data-id"]))
            schedule = tool.Ifc.get().by_id(int(view.attrib["data-schedule"]))

            images = view.findall("{http://www.w3.org/2000/svg}image")

            table = None
            view_title = None

            for image in images:
                if image.attrib["data-type"] == "table":
                    table = image
                elif image.attrib["data-type"] == "view-title":
                    view_title = image

            if table is not None:
                view.append(self.parse_embedded_svg(table, {}))

            if view_title is not None:
                path = self.get_href(table)
                data = reference.get_info()
                if not data["Name"]:
                    data["Name"] = schedule.Name or "Unnamed"
                view.append(self.parse_embedded_svg(view_title, data))

            for image in images:
                view.remove(image)

    def get_href(self, element):
        return urllib.parse.unquote(element.attrib.get("{http://www.w3.org/1999/xlink}href"))

    def parse_embedded_svg(self, image, data):
        group = ET.Element("g")
        group.attrib["transform"] = "translate({},{})".format(
            self.convert_to_mm(image.attrib.get("x")), self.convert_to_mm(image.attrib.get("y"))
        )
        svg_path = self.get_href(image)
        with open(os.path.join(self.data_dir, "sheets", svg_path), "r") as template:
            embedded = ET.fromstring(pystache.render(template.read(), data))
            # viewBox should not be nested
            embedded.attrib["viewBox"] = ""
            # TODO: This should not be in this function
            self.scale = embedded.attrib.get("data-scale")
            images = embedded.findall("{http://www.w3.org/2000/svg}image")
            for image in images:
                new_href = ntpath.basename(image.attrib.get("{http://www.w3.org/1999/xlink}href"))
                image.attrib["{http://www.w3.org/1999/xlink}href"] = new_href
        group.append(embedded)
        return group

    def convert_to_mm(self, value):
        # CSS is what defines these possibilities
        # https://www.w3.org/TR/SVG/refs.html#ref-css-values-3
        # https://www.w3.org/TR/css-values-3/#absolute-lengths
        # The relative units are not implemented. Go fish.
        if "cm" in value:
            return float(value[0:-2]) * 10
        elif "mm" in value:
            return float(value[0:-2])
        elif "Q" in value:
            return float(value[0:-1]) * (1 / 40) * 10
        elif "in" in value:
            return float(value[0:-2]) * 2.54 * 10
        elif "pc" in value:
            return float(value[0:-2]) * (1 / 6) * 2.54 * 10
        elif "pt" in value:
            return float(value[0:-2]) * (1 / 72) * 2.54 * 10
        elif "px" in value:
            return float(value[0:-2]) * (1 / 96) * 2.54 * 10
        return float(value)

    def mm_to_px(self, value):
        return (value / 25.4) * 96
