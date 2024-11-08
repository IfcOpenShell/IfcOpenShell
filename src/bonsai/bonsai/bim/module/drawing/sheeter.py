# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of Bonsai.
#
# Bonsai is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Bonsai is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Bonsai.  If not, see <http://www.gnu.org/licenses/>.

import os
import bpy
import uuid
import shutil
import ntpath
import pystache
import urllib.parse
import xml.etree.ElementTree as ET
import bonsai.tool as tool
import ifcopenshell.util.geolocation
from xml.dom import minidom
from mathutils import Vector
import re

VIEW_TITLE_OFFSET_Y = 5
DEFAULT_POSITION = Vector((30, 30))
SVG = "{http://www.w3.org/2000/svg}"
XLINK = "{http://www.w3.org/1999/xlink}"


class SheetBuilder:
    def __init__(self):
        self.data_dir = None
        self.scale = "NTS"

    def create(self, layout_path: str, titleblock_name: str) -> None:
        root = ET.Element("svg")
        root.attrib["xmlns"] = "http://www.w3.org/2000/svg"
        root.attrib["xmlns:xlink"] = "http://www.w3.org/1999/xlink"
        root.attrib["id"] = "root"
        root.attrib["version"] = "1.1"

        sheet_dir = os.path.dirname(layout_path)
        ootb_titleblock_path = os.path.join(self.data_dir, "templates", "titleblocks", titleblock_name + ".svg")
        titleblock_path = tool.Ifc.resolve_uri(tool.Drawing.get_default_titleblock_path(titleblock_name))

        os.makedirs(sheet_dir, exist_ok=True)
        os.makedirs(os.path.dirname(titleblock_path), exist_ok=True)
        if not os.path.exists(titleblock_path):
            shutil.copy(ootb_titleblock_path, titleblock_path)

        view_root = ET.parse(titleblock_path).getroot()
        view_width = self.convert_to_mm(view_root.attrib.get("width"))
        view_height = self.convert_to_mm(view_root.attrib.get("height"))
        view = ET.SubElement(root, "g")
        view.attrib["data-type"] = "titleblock"
        titleblock = ET.SubElement(view, "image")
        titleblock.attrib["xlink:href"] = os.path.relpath(titleblock_path, sheet_dir)
        titleblock.attrib["x"] = "0"
        titleblock.attrib["y"] = "0"
        titleblock.attrib["width"] = str(view_width)
        titleblock.attrib["height"] = str(view_height)

        root.attrib["width"] = "{}mm".format(view_width)
        root.attrib["height"] = "{}mm".format(view_height)
        root.attrib["viewBox"] = "0 0 {} {}".format(view_width, view_height)

        with open(layout_path, "w") as f:
            f.write(minidom.parseString(ET.tostring(root)).toprettyxml(indent="    "))

    def add_drawing(
        self,
        reference: ifcopenshell.entity_instance,
        drawing: ifcopenshell.entity_instance,
        sheet: ifcopenshell.entity_instance,
    ) -> None:
        filename = drawing.Name
        layout_path = tool.Drawing.get_document_uri(sheet, "LAYOUT")
        layout_dir = os.path.dirname(layout_path)

        drawing_path = tool.Drawing.get_document_uri(tool.Drawing.get_drawing_reference(drawing))
        underlay_path = os.path.splitext(drawing_path)[0] + "-underlay.png"

        if not os.path.exists(layout_path) or not os.path.exists(drawing_path):
            raise FileNotFoundError

        ET.register_namespace("", "http://www.w3.org/2000/svg")
        ET.register_namespace("xlink", "http://www.w3.org/1999/xlink")

        layout_tree = ET.parse(layout_path)
        layout_root = layout_tree.getroot()

        view_tree = ET.parse(drawing_path)
        view_root = view_tree.getroot()

        # The view is placed into a group with a background image element.
        # Although the foreground SVG already has a background, it is duplicated
        # here to accommodate browsers which do not nest images.
        view = ET.SubElement(layout_root, "g")
        view.attrib["data-type"] = "drawing"
        view.attrib["data-id"] = str(reference.id())
        view.attrib["data-drawing"] = drawing.GlobalId
        view_width = self.convert_to_mm(view_root.attrib.get("width"))
        view_height = self.convert_to_mm(view_root.attrib.get("height"))

        # add background
        if os.path.isfile(underlay_path):
            background = ET.SubElement(view, "image")
            background.attrib["data-type"] = "background"
            background.attrib["xlink:href"] = os.path.relpath(underlay_path, layout_dir)
            background.attrib["x"] = str(DEFAULT_POSITION.x)
            background.attrib["y"] = str(DEFAULT_POSITION.y)
            background.attrib["width"] = str(view_width)
            background.attrib["height"] = str(view_height)

        # add foreground
        if os.path.isfile(drawing_path):
            foreground = ET.SubElement(view, "image")
            foreground.attrib["data-type"] = "foreground"
            foreground.attrib["xlink:href"] = os.path.relpath(drawing_path, layout_dir)
            foreground.attrib["x"] = str(DEFAULT_POSITION.x)
            foreground.attrib["y"] = str(DEFAULT_POSITION.y)
            foreground.attrib["width"] = str(view_width)
            foreground.attrib["height"] = str(view_height)

        self.add_view_title(
            DEFAULT_POSITION.x, view_height + DEFAULT_POSITION.y + VIEW_TITLE_OFFSET_Y, view, layout_dir
        )
        layout_tree.write(layout_path)

    def update_sheet_drawing_sizes(self, sheet: ifcopenshell.entity_instance) -> None:
        ET.register_namespace("", "http://www.w3.org/2000/svg")

        layout_path = tool.Drawing.get_document_uri(sheet, "LAYOUT")
        layout_tree = ET.parse(layout_path)
        layout_root = layout_tree.getroot()
        ifc_file = tool.Ifc.get()

        # iterate over all drawings in the sheet
        drawings_views = layout_root.findall(f'{SVG}g[@data-type="drawing"]')

        for drawing_view in drawings_views:
            # find drawing in ifc file to get the drawing dimensions
            drawing = ifc_file.by_guid(drawing_view.attrib.get("data-drawing"))
            drawing_path = tool.Drawing.get_document_uri(tool.Drawing.get_drawing_reference(drawing))
            drawing_tree = ET.parse(drawing_path)
            drawing_root = drawing_tree.getroot()
            view_width = round(self.convert_to_mm(drawing_root.attrib.get("width")), 2)
            view_height = round(self.convert_to_mm(drawing_root.attrib.get("height")), 2)

            foreground = drawing_view.find(f'.//{SVG}image[@data-type="foreground"]')
            current_width = round(float(foreground.attrib["width"]), 2)
            current_height = round(float(foreground.attrib["height"]), 2)

            # Check if the dimensions have changed
            if current_width != view_width or current_height != view_height:
                readjust = Vector((current_width - view_width, current_height - view_height)) / 2

                for image in drawing_view.findall(f"{SVG}image"):
                    x = float(image.attrib["x"])
                    y = float(image.attrib["y"])
                    if image.attrib["data-type"] == "view-title":
                        image.attrib["x"] = str(x + readjust.x)
                        # negate y offset because view-title comes AFTER foreground
                        image.attrib["y"] = str(y - readjust.y)
                    else:
                        image.attrib["x"] = str(x + readjust.x)
                        image.attrib["y"] = str(y + readjust.y)
                        image.attrib["width"] = str(view_width)
                        image.attrib["height"] = str(view_height)

        layout_tree.write(layout_path)

    def remove_drawing(self, reference: ifcopenshell.entity_instance, sheet: ifcopenshell.entity_instance) -> None:
        ET.register_namespace("", "http://www.w3.org/2000/svg")

        layout_path = tool.Drawing.get_document_uri(sheet, "LAYOUT")
        if not os.path.exists(layout_path):
            return
        layout_tree = ET.parse(layout_path)
        layout_root = layout_tree.getroot()

        for g in layout_root.findall("{http://www.w3.org/2000/svg}g"):
            if g.attrib.get("data-id") == str(reference.id()):
                layout_root.remove(g)
                break

        layout_tree.write(layout_path)

    def add_document(
        self,
        reference: ifcopenshell.entity_instance,
        document: ifcopenshell.entity_instance,
        sheet: ifcopenshell.entity_instance,
    ) -> None:
        view_path = tool.Drawing.get_path_with_ext(tool.Drawing.get_document_uri(document), "svg")
        if not os.path.exists(view_path):
            tool.Drawing.create_svg_document(document)
        document_name = os.path.splitext(os.path.basename(view_path))[0]
        layout_path = tool.Drawing.get_document_uri(sheet, "LAYOUT")
        layout_dir = os.path.dirname(layout_path)

        ET.register_namespace("", "http://www.w3.org/2000/svg")
        ET.register_namespace("xlink", "http://www.w3.org/1999/xlink")

        layout_tree = ET.parse(layout_path)
        layout_root = layout_tree.getroot()

        view_tree = ET.parse(view_path)
        view_root = view_tree.getroot()
        view_width = self.convert_to_mm(view_root.attrib.get("width"))
        view_height = self.convert_to_mm(view_root.attrib.get("height"))

        view = ET.SubElement(layout_root, "g")
        view.attrib["data-id"] = str(reference.id())
        view.attrib["data-type"] = document.Scope.lower()
        view.attrib["data-document"] = str(document.id())

        foreground = ET.SubElement(view, "image")
        foreground.attrib["data-type"] = "content"
        foreground.attrib["xlink:href"] = os.path.relpath(view_path, layout_dir)
        foreground.attrib["x"] = str(DEFAULT_POSITION.x)
        foreground.attrib["y"] = str(DEFAULT_POSITION.y)
        foreground.attrib["width"] = str(view_width)
        foreground.attrib["height"] = str(view_height)

        self.add_view_title(
            DEFAULT_POSITION.x, view_height + DEFAULT_POSITION.y + VIEW_TITLE_OFFSET_Y, view, layout_dir
        )
        layout_tree.write(layout_path)

    def add_view_title(self, x: float, y: float, parent: ET.Element, layout_dir: str) -> None:
        title_path = os.path.join(layout_dir, "assets", "view-title.svg")
        os.makedirs(os.path.dirname(title_path), exist_ok=True)
        if not os.path.exists(title_path):
            ootb_title = os.path.join(bpy.context.scene.BIMProperties.data_dir, "assets", "view-title.svg")
            shutil.copy(ootb_title, title_path)

        title_tree = ET.parse(title_path)
        title_root = title_tree.getroot()
        title = ET.SubElement(parent, "image")
        title.attrib["data-type"] = "view-title"
        title.attrib["xlink:href"] = os.path.relpath(title_path, layout_dir)
        title.attrib["x"] = str(x)
        title.attrib["y"] = str(y)
        title.attrib["width"] = str(self.convert_to_mm(title_root.attrib.get("width")))
        title.attrib["height"] = str(self.convert_to_mm(title_root.attrib.get("height")))

    def build(self, sheet: ifcopenshell.entity_instance) -> dict:
        self.references = {"SHEET": None, "RASTER": []}

        layout_path = tool.Drawing.get_document_uri(sheet, "LAYOUT")
        self.layout_dir = os.path.dirname(layout_path)

        sheet_path = tool.Ifc.resolve_uri(tool.Drawing.get_default_sheet_path(sheet[0], sheet.Name))
        self.sheets_dir = os.path.dirname(sheet_path)

        os.makedirs(self.sheets_dir, exist_ok=True)

        ET.register_namespace("", "http://www.w3.org/2000/svg")
        ET.register_namespace("xlink", "http://www.w3.org/1999/xlink")

        tree = ET.parse(layout_path)
        root = tree.getroot()

        self.defs = ET.Element("defs")
        root.append(self.defs)

        self.build_titleblock(root, sheet)
        self.build_drawings(root, sheet)
        self.build_documents(root, sheet)

        with open(sheet_path, "wb") as output:
            tree.write(output)

        self.references["SHEET"] = sheet_path

        return self.references

    def build_titleblock(self, root: ET.Element, sheet: ifcopenshell.entity_instance) -> None:
        titleblock = root.findall('{http://www.w3.org/2000/svg}g[@data-type="titleblock"]')[0]
        image = titleblock.findall("{http://www.w3.org/2000/svg}image")[0]
        g = self.parse_embedded_svg(image, sheet.get_info())
        grid_north = ifcopenshell.util.geolocation.get_grid_north(tool.Ifc.get()) * -1
        true_north = ifcopenshell.util.geolocation.get_true_north(tool.Ifc.get()) * -1
        for north in g.iterfind('.//{http://www.w3.org/2000/svg}g[@data-type="grid-north"]'):
            north.attrib["transform"] = f"rotate({grid_north})"
        for north in g.iterfind('.//{http://www.w3.org/2000/svg}g[@data-type="true-north"]'):
            north.attrib["transform"] = f"rotate({true_north})"
        titleblock.append(g)
        titleblock.remove(image)

    def ensure_drawing_unique_styles(self, svg: ET.Element, drawing_id: int) -> ET.Element:
        """ensures all drawing's classes and ids will be unique for the whole sheet
        by adding `drawing_id` based prefix
        """
        prefix = f"d{drawing_id}"  # just number doesn't work

        # add .prefix class to all css selectors
        style = svg.find(f"{SVG}defs/{SVG}style")
        style_data = style.text
        text = ""
        brackets_level = 0
        for l in style_data:
            if l == "{":
                if brackets_level == 0:
                    cur_line = text.splitlines()[-1]
                    text = text[: -len(cur_line)]
                    css_selectors = []
                    # making sure cases like "text, tspan" will be
                    # converted to "text.prefix, tspan.prefix"
                    for css_selector in cur_line.split(","):
                        css_selector = f"{css_selector.strip()}.{prefix}"
                        css_selectors.append(css_selector)
                    text += ", ".join(css_selectors) + " "
                brackets_level += 1
            elif l == "}":
                brackets_level -= 1
            text += l

        def replace_urls(text: str) -> str:
            """replace urls `url(#marker)` with `url(#prefix-marker)`
            since `url(#marker.prefix)` doesn't seem to work
            """
            return re.sub(r"url\(#([^\)]+)\)", rf"url(#{prefix}-\1)", text)

        style.text = replace_urls(text)

        for svg_element in svg.findall(f".//*"):
            if svg_element.tag in (f"{SVG}style", f"{SVG}svg"):
                continue
            attrib = svg_element.attrib
            # add "prefix-" to all ids
            if "id" in attrib:
                attrib["id"] = f"{prefix}-{attrib['id']}"
            # add class "prefix" to all classes
            if "class" in attrib:
                attrib["class"] += f" {prefix}"
            if "filter" in attrib:
                # example use "#fill-background" filter
                attrib["filter"] = replace_urls(attrib["filter"])
            if svg_element.tag == f"{SVG}use":
                href_attrib = f"{XLINK}href"
                if href_attrib in attrib:
                    href = attrib[href_attrib]
                    if href.startswith("#"):
                        attrib[href_attrib] = f"#{prefix}-{href[1:]}"

        return svg

    def build_drawings(self, root: ET.Element, sheet: ifcopenshell.entity_instance):
        for view in root.findall('{http://www.w3.org/2000/svg}g[@data-type="drawing"]'):
            drawing_id = int(view.attrib["data-id"])
            try:
                reference = tool.Ifc.get().by_id(int(view.attrib["data-id"]))
                drawing = tool.Ifc.get().by_id(view.attrib["data-drawing"])
            except:
                # Perhaps the SVG has outdated content or is edited externally which we cannot control.
                continue

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
                svg = self.parse_embedded_svg(foreground, {})
                svg = self.ensure_drawing_unique_styles(svg, drawing_id)
                view.append(svg)

            if background is not None:
                background_path = os.path.join(self.layout_dir, self.get_href(background))
                raster_path = os.path.join(self.sheets_dir, os.path.basename(background_path))
                shutil.copy(background_path, raster_path)
                self.references["RASTER"].append(raster_path)

            if view_title is not None:
                foreground_path = self.get_href(foreground)
                data = reference.get_info()
                data.update({"Sheet" + k: v for k, v in sheet.get_info().items()})
                if not data["Name"]:
                    data["Name"] = ntpath.basename(foreground_path)[0:-4]

                # If a perspective drawing, don't add scale to view title
                try:
                    is_perspective = (
                        drawing.Representation.Representations[0]
                        .Items[0]
                        .TreeRootExpression.FirstOperand.is_a("IfcRectangularPyramid")
                    )
                except AttributeError:
                    is_perspective = False

                if not is_perspective:
                    data["Scale"] = tool.Drawing.get_drawing_human_scale(drawing)
                view.append(self.parse_embedded_svg(view_title, data))

            for image in images:
                view.remove(image)

    def build_documents(self, root: ET.Element, sheet: ifcopenshell.entity_instance) -> None:
        schedules = root.findall('{http://www.w3.org/2000/svg}g[@data-type="schedule"]')
        references = root.findall('{http://www.w3.org/2000/svg}g[@data-type="reference"]')
        documents = schedules + references
        for view in documents:
            try:
                reference = tool.Ifc.get().by_id(int(view.attrib["data-id"]))
                document = tool.Ifc.get().by_id(int(view.attrib["data-document"]))
            except:
                # Perhaps the SVG has outdated content or is edited externally which we cannot control.
                continue

            images = view.findall("{http://www.w3.org/2000/svg}image")

            table = None
            view_title = None

            for image in images:
                if image.attrib["data-type"] == "content":
                    table = image
                elif image.attrib["data-type"] == "view-title":
                    view_title = image

            if table is not None:
                view.append(self.parse_embedded_svg(table, {}))

            if view_title is not None:
                path = self.get_href(table)
                data = reference.get_info()
                data.update({"Sheet" + k: v for k, v in sheet.get_info().items()})
                if not data["Name"]:
                    data["Name"] = document.Name or "Unnamed"
                view.append(self.parse_embedded_svg(view_title, data))

            for image in images:
                view.remove(image)

    def get_href(self, element: ET.Element) -> str:
        return urllib.parse.unquote(element.attrib.get("{http://www.w3.org/1999/xlink}href")).replace("\\", "/")

    def parse_embedded_svg(self, image: ET.Element, data: dict) -> ET.Element:
        group = ET.Element("g")
        group.attrib["transform"] = "translate({},{})".format(
            self.convert_to_mm(image.attrib.get("x")), self.convert_to_mm(image.attrib.get("y"))
        )

        # Convert viewBox into a clip path
        clip_id = str(uuid.uuid4())
        group.attrib["clip-path"] = f"url(#{clip_id})"
        clip_path = ET.Element("clipPath")
        clip_path.attrib["id"] = clip_id
        rect = ET.Element("rect")
        rect.attrib["x"] = "0"
        rect.attrib["y"] = "0"
        rect.attrib["width"] = str(self.convert_to_mm(image.attrib.get("width")))
        rect.attrib["height"] = str(self.convert_to_mm(image.attrib.get("height")))
        clip_path.append(rect)
        self.defs.append(clip_path)

        svg_path = self.get_href(image)
        with open(os.path.join(self.layout_dir, svg_path), "r") as template:
            embedded = ET.fromstring(pystache.render(template.read(), data))
            # viewBox should not be nested
            embedded.attrib["viewBox"] = ""
            # TODO: This should not be in this function
            self.scale = embedded.attrib.get("data-scale")
            images = embedded.findall("{http://www.w3.org/2000/svg}image")
            for image in images:
                new_href = ntpath.basename(image.attrib.get("{http://www.w3.org/1999/xlink}href"))
                image.attrib["{http://www.w3.org/1999/xlink}href"] = new_href
        for child in embedded:
            if "namedview" in child.tag:
                continue
            group.append(child)
        return group

    def change_titleblock(self, sheet: ifcopenshell.entity_instance, titleblock_name: str) -> None:
        ootb_titleblock_path = os.path.join(self.data_dir, "templates", "titleblocks", titleblock_name + ".svg")
        titleblock_path = tool.Drawing.get_default_titleblock_path(titleblock_name)
        sheet_path = tool.Drawing.get_document_uri(sheet, "LAYOUT")
        sheet_dir = os.path.dirname(sheet_path)

        os.makedirs(sheet_dir, exist_ok=True)
        os.makedirs(os.path.dirname(titleblock_path), exist_ok=True)
        if not os.path.exists(titleblock_path):
            shutil.copy(ootb_titleblock_path, titleblock_path)

        ET.register_namespace("", "http://www.w3.org/2000/svg")
        ET.register_namespace("xlink", "http://www.w3.org/1999/xlink")

        view_root = ET.parse(ootb_titleblock_path).getroot()
        view_width = self.convert_to_mm(view_root.attrib.get("width"))
        view_height = self.convert_to_mm(view_root.attrib.get("height"))

        sheet_tree = ET.parse(sheet_path)
        root = sheet_tree.getroot()

        titleblock = sheet_tree.findall('{http://www.w3.org/2000/svg}g[@data-type="titleblock"]')[0]
        image = titleblock.findall("{http://www.w3.org/2000/svg}image[@{http://www.w3.org/1999/xlink}href]")[0]
        image.attrib["{http://www.w3.org/1999/xlink}href"] = os.path.relpath(titleblock_path, sheet_dir)
        image.attrib["width"] = str(view_width)
        image.attrib["height"] = str(view_height)

        root.attrib["width"] = "{}mm".format(view_width)
        root.attrib["height"] = "{}mm".format(view_height)
        root.attrib["viewBox"] = "0 0 {} {}".format(view_width, view_height)

        sheet_tree.write(sheet_path)

    def convert_to_mm(self, value: str) -> float:
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

    def mm_to_px(self, value: float) -> float:
        return (value / 25.4) * 96
