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

import ntpath
import os
import re
import shutil
import urllib.parse
import uuid
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Union
from xml.dom import minidom

import ifcopenshell.util.element
import ifcopenshell.util.geolocation
import pystache
from mathutils import Vector

import bonsai.tool as tool

VIEW_TITLE_OFFSET_Y = 5
DRAWING_PADDING = 10
DEFAULT_POSITION = Vector((30, 30))
SVG = "{http://www.w3.org/2000/svg}"
XLINK = "{http://www.w3.org/1999/xlink}"

#: The spatial elements a sheet can be about, by the prefix of their titleblock
#: fields - {{SiteName}}, {{BuildingTown}} - with the IFC class of each and the
#: attribute holding its postal address. The prefix alone names the sheet's link
#: to one: its value is that element's GlobalId.
SPATIAL_ELEMENTS = {"Site": ("IfcSite", "SiteAddress"), "Building": ("IfcBuilding", "BuildingAddress")}
#: What follows the prefix: the element's own attributes, then its address's.
#: `<prefix>Address` is the whole address on one line.
ELEMENT_ATTRIBUTES = ("Name", "Description")
ADDRESS_ATTRIBUTES = ("AddressLines", "PostalBox", "Town", "Region", "PostalCode", "Country")
#: {field: (prefix, attribute, is_address)} for every such field.
SPATIAL_FIELDS = {
    prefix + attribute: (prefix, attribute, attribute in ADDRESS_ATTRIBUTES)
    for prefix in SPATIAL_ELEMENTS
    for attribute in ELEMENT_ATTRIBUTES + ADDRESS_ATTRIBUTES
}


def as_template_data(value):
    """A value as a sheet template sees it, in a form that survives JSON.

    pystache renders a variable with str(), so everything becomes text - an unset
    attribute is "None" - except what templates test and iterate: booleans, and
    lists of rows such as the titleblock's revisions.
    """
    if isinstance(value, dict):
        return {k: as_template_data(v) for k, v in value.items()}
    if isinstance(value, bool):
        return value
    if isinstance(value, list) and all(isinstance(v, dict) for v in value):
        return [as_template_data(v) for v in value]
    return str(value)


class SheetBuilder:
    def __init__(self):
        self.scale = "NTS"

    def create(self, layout_path: str, titleblock_name: str) -> None:
        root = ET.Element("svg")
        root.attrib["xmlns"] = "http://www.w3.org/2000/svg"
        root.attrib["xmlns:xlink"] = "http://www.w3.org/1999/xlink"
        root.attrib["xmlns:sodipodi"] = "http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd"
        root.attrib["id"] = "root"
        root.attrib["version"] = "1.1"

        sheet_dir = os.path.dirname(layout_path)
        ootb_titleblock_path = tool.Blender.get_data_dir_path(
            Path("templates") / "titleblocks" / (titleblock_name + ".svg")
        )
        titleblock_path = tool.Ifc.resolve_uri(tool.Drawing.get_default_titleblock_path(titleblock_name))

        os.makedirs(sheet_dir, exist_ok=True)
        os.makedirs(os.path.dirname(titleblock_path), exist_ok=True)
        if not os.path.exists(titleblock_path):
            shutil.copy(ootb_titleblock_path, titleblock_path)

        view_root = ET.parse(titleblock_path).getroot()
        view_width = self.convert_to_mm(view_root.attrib["width"])
        view_height = self.convert_to_mm(view_root.attrib["height"])
        view = ET.SubElement(root, "g")
        view.attrib["data-type"] = "titleblock"
        view.attrib["sodipodi:insensitive"] = "true"
        titleblock = ET.SubElement(view, "image")
        titleblock.attrib["xlink:href"] = Path(os.path.relpath(titleblock_path, sheet_dir)).as_posix()
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
        assert layout_path
        layout_dir = os.path.dirname(layout_path)

        drawing_path = tool.Drawing.get_document_uri(tool.Drawing.get_drawing_reference(drawing))

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
        view_width = self.convert_to_mm(view_root.attrib["width"])
        view_height = self.convert_to_mm(view_root.attrib["height"])

        x, y = self.next_drawing_location(layout_root, view_width)

        # add foreground
        if os.path.isfile(drawing_path):
            foreground = ET.SubElement(view, "image")
            foreground.attrib["data-type"] = "foreground"
            foreground.attrib["xlink:href"] = os.path.relpath(drawing_path, layout_dir)
            foreground.attrib["x"] = str(x)
            foreground.attrib["y"] = str(y)
            foreground.attrib["width"] = str(view_width)
            foreground.attrib["height"] = str(view_height)

        self.add_view_title(x, view_height + y + VIEW_TITLE_OFFSET_Y, view, layout_dir)
        layout_tree.write(layout_path)

    def next_drawing_location(self, layout_root: ET.Element, next_width: float) -> list:
        titleblocks = layout_root.findall(f'{SVG}g[@data-type="titleblock"]')
        drawings = layout_root.findall(f'{SVG}g[@data-type="drawing"]')

        # how wide is the title block frame
        try:
            titleblock_width = self.convert_to_mm(titleblocks[0][0].attrib["width"])
        except (IndexError, AttributeError):
            titleblock_width = 840.0

        # where does the last drawing finish
        try:
            last = drawings[-1][0]
            last_width = self.convert_to_mm(last.attrib["width"])
            last_x = self.convert_to_mm(last.attrib["x"])
            last_y = self.convert_to_mm(last.attrib["y"])
        except (IndexError, AttributeError):
            return [DEFAULT_POSITION.x, DEFAULT_POSITION.y]

        # check if the new drawing fits in the current row
        if last_x + last_width + DRAWING_PADDING + next_width + DEFAULT_POSITION.x < titleblock_width:
            return [last_x + last_width + DRAWING_PADDING, last_y]

        # start a new row, find the y
        for drawing in drawings:
            for image in drawing:
                try:
                    image_y = self.convert_to_mm(image.attrib["y"])
                    image_height = self.convert_to_mm(image.attrib["height"])
                except AttributeError:
                    return [DEFAULT_POSITION.x, DEFAULT_POSITION.y]
                if image_y + image_height + DRAWING_PADDING > last_y:
                    last_y = image_y + image_height + DRAWING_PADDING
        return [DEFAULT_POSITION.x, last_y]

    def update_sheet_drawing_sizes(self, sheet: ifcopenshell.entity_instance) -> None:
        ET.register_namespace("", "http://www.w3.org/2000/svg")

        layout_path = tool.Drawing.get_document_uri(sheet, "LAYOUT")
        assert layout_path
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
        assert layout_path
        if not os.path.exists(layout_path):
            return
        layout_tree = ET.parse(layout_path)
        layout_root = layout_tree.getroot()

        for g in layout_root.findall(f"{SVG}g"):
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
        assert layout_path
        layout_dir = os.path.dirname(layout_path)

        ET.register_namespace("", "http://www.w3.org/2000/svg")
        ET.register_namespace("xlink", "http://www.w3.org/1999/xlink")

        layout_tree = ET.parse(layout_path)
        layout_root = layout_tree.getroot()

        view_tree = ET.parse(view_path)
        view_root = view_tree.getroot()
        view_width = self.convert_to_mm(view_root.attrib.get("width"))
        view_height = self.convert_to_mm(view_root.attrib.get("height"))

        x, y = self.next_drawing_location(layout_root, view_width)

        view = ET.SubElement(layout_root, "g")
        view.attrib["data-id"] = str(reference.id())
        view.attrib["data-type"] = document.Scope.lower()
        view.attrib["data-document"] = str(document.id())

        foreground = ET.SubElement(view, "image")
        foreground.attrib["data-type"] = "content"
        foreground.attrib["xlink:href"] = os.path.relpath(view_path, layout_dir)
        foreground.attrib["x"] = str(x)
        foreground.attrib["y"] = str(y)
        foreground.attrib["width"] = str(view_width)
        foreground.attrib["height"] = str(view_height)

        self.add_view_title(x, view_height + y + VIEW_TITLE_OFFSET_Y, view, layout_dir)
        layout_tree.write(layout_path)

    def add_view_title(self, x: float, y: float, parent: ET.Element, layout_dir: str) -> None:
        title_path = os.path.join(layout_dir, "assets", "view-title.svg")
        os.makedirs(os.path.dirname(title_path), exist_ok=True)
        if not os.path.exists(title_path):
            ootb_title = tool.Blender.get_data_dir_path(Path("assets") / "view-title.svg")
            shutil.copy(ootb_title, title_path)

        title_tree = ET.parse(title_path)
        title_root = title_tree.getroot()
        title = ET.SubElement(parent, "image")
        title.attrib["data-type"] = "view-title"
        title.attrib["xlink:href"] = os.path.relpath(title_path, layout_dir)
        title.attrib["x"] = str(x)
        title.attrib["y"] = str(y)
        title.attrib["width"] = str(self.convert_to_mm(title_root.attrib["width"]))
        title.attrib["height"] = str(self.convert_to_mm(title_root.attrib["height"]))

    def build(self, sheet: ifcopenshell.entity_instance) -> dict[str, str]:
        layout_path = tool.Drawing.get_document_uri(sheet, "LAYOUT")
        assert layout_path
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

        return {"SHEET": sheet_path}

    def get_titleblock_data(self, sheet: ifcopenshell.entity_instance) -> dict:
        """Template data for a sheet's titleblock.

        Shared by `build_titleblock` and `get_template_values`.
        """
        data = sheet.get_info()
        data.update(self.get_spatial_data(sheet))
        return data

    def get_sheet_links(self, sheet: ifcopenshell.entity_instance) -> dict:
        """The site and building a sheet names itself, as {"Site": ..., "Building": ...}.

        A sheet names them by a document association - the IFC relationship for
        "this document is about this object" - so the link is ordinary IFC that
        survives a re-serialised model, and goes when the sheet does.

        A sheet linked to two sites names neither. IFC keeps the links as a set,
        so "the first" would be whichever the file happens to list first; that is
        a guess, and the fields stay blank instead. Linking one replaces both.
        """
        return {prefix: self._only(elements) for prefix, elements in self.get_all_sheet_links(sheet).items()}

    def get_all_sheet_links(self, sheet: ifcopenshell.entity_instance) -> dict:
        """Everything a sheet is linked to, by prefix - more than one is a conflict to resolve."""
        linked = {prefix: [] for prefix in SPATIAL_ELEMENTS}
        for rel in self._sheet_associations(sheet):
            for element in rel.RelatedObjects:
                for prefix, (ifc_class, _) in SPATIAL_ELEMENTS.items():
                    if element.is_a(ifc_class) and element not in linked[prefix]:
                        linked[prefix].append(element)
        return linked

    def get_sheet_spatial(self, sheet: ifcopenshell.entity_instance, links: Union[dict, None] = None) -> dict:
        """The site and building a sheet is about, as {"Site": ..., "Building": ...}.

        What the sheet links to, or - for one it does not - whatever has a single
        answer: a building's own site, the model's only top-level site, the site's
        only building. With several to choose from it is None and its fields are
        blank. A titleblock quietly showing one building's address on another
        building's sheet would be worse than an empty box.

        :param links: Links to use in place of the sheet's own, by prefix - to see
            what an edit would resolve to before making it.
        """
        linked = self.get_sheet_links(sheet) | (links or {})
        site, building = linked["Site"], linked["Building"]
        if site is None and building is not None:
            site = self._containing(building, "IfcSite")
        if site is None:
            site = self._only(self._top_level_sites(sheet.file))
        if building is None:
            building = self._only(self._buildings_in(sheet.file, site))
        return {"Site": site, "Building": building}

    def get_spatial_data(self, sheet: ifcopenshell.entity_instance) -> dict:
        """The {{Site...}} and {{Building...}} fields of a sheet's titleblock.

        Unset values are empty rather than "None": an address reading "None, None"
        on a sheet looks broken where an unset revision code does not.
        """

        def get(entity, name):
            return (getattr(entity, name, None) if entity else None) or ""

        data = {}
        for prefix, element in self.get_sheet_spatial(sheet).items():
            address = get(element, SPATIAL_ELEMENTS[prefix][1]) or None
            for name in ELEMENT_ATTRIBUTES:
                data[prefix + name] = get(element, name)
            for name in ADDRESS_ATTRIBUTES:
                data[prefix + name] = get(address, name)
            # Several lines are shown as one: a field is a single box of text.
            data[prefix + "AddressLines"] = ", ".join(get(address, "AddressLines"))
            region = " ".join(p for p in (data[prefix + "Region"], data[prefix + "PostalCode"]) if p)
            parts = (
                data[prefix + "AddressLines"],
                data[prefix + "PostalBox"],
                data[prefix + "Town"],
                region,
                data[prefix + "Country"],
            )
            data[prefix + "Address"] = ", ".join(p for p in parts if p)
        return data

    def get_link_field(self, sheet: ifcopenshell.entity_instance, prefix: str) -> dict:
        """The Site or Building a sheet is linked to, as a field with a choice of values.

        The first choice is to link nothing, labelled with what that resolves to,
        so the list says what the sheet will show either way.
        """
        ifc_class = SPATIAL_ELEMENTS[prefix][0]
        noun = ifc_class[3:].lower()
        linked_all = self.get_all_sheet_links(sheet)[prefix]
        linked = self._only(linked_all)
        automatic = self.get_sheet_spatial(sheet, {prefix: None})[prefix]
        candidates = sorted(tool.Ifc.get().by_type(ifc_class), key=lambda e: (e.Name or "", e.GlobalId))
        names = [e.Name or f"Unnamed {noun}" for e in candidates]

        if automatic is not None:
            label = f"Automatic ({automatic.Name or f'Unnamed {noun}'})"
        elif candidates:
            label = "Automatic (none - more than one to choose from)"
        else:
            label = f"Automatic (none - this model has no {noun})"
        options = [{"value": "", "label": label}]
        if len(linked_all) > 1:
            # Shown as the current value, so the conflict is visible and picking
            # anything - Automatic included - replaces every link.
            options.insert(0, {"value": self.CONFLICT, "label": f"{len(linked_all)} {noun}s linked - pick one"})
        for element, name in zip(candidates, names):
            # Two with the same name are told apart by their GlobalId.
            options.append(
                {"value": element.GlobalId, "label": name if names.count(name) == 1 else f"{name} ({element.GlobalId})"}
            )
        return {
            "name": prefix,
            "value": self.CONFLICT if len(linked_all) > 1 else (linked.GlobalId if linked else ""),
            "editable": True,
            "options": options,
        }

    #: The Site or Building value of a sheet linked to more than one.
    CONFLICT = "*"

    def set_sheet_links(self, sheet: ifcopenshell.entity_instance, links: dict) -> None:
        """Link a sheet to a site or building, replacing what it linked to. None unlinks."""
        for prefix, element in links.items():
            ifc_class = SPATIAL_ELEMENTS[prefix][0]
            for rel in self._sheet_associations(sheet):
                for current in list(rel.RelatedObjects):
                    if current.is_a(ifc_class) and current != element:
                        tool.Ifc.run("document.unassign_document", products=[current], document=sheet)
            if element is not None:
                tool.Ifc.run("document.assign_document", products=[element], document=sheet)

    def set_spatial_fields(self, elements: dict, values: dict) -> None:
        """Write {{Site...}} and {{Building...}} fields to the elements they show."""
        own, addresses = {}, {}
        for field, value in values.items():
            prefix, name, is_address = SPATIAL_FIELDS[field]
            if is_address and name == "AddressLines":
                # Typed as one line, kept as one: splitting on commas would break
                # a line that has one of its own.
                value = [value] if value else None
            (addresses if is_address else own).setdefault(prefix, {})[name] = value or None
        for prefix, attributes in own.items():
            self._edit_spatial_element(elements[prefix], attributes)
        for prefix, attributes in addresses.items():
            self._edit_address(elements[prefix], SPATIAL_ELEMENTS[prefix][1], attributes)

    def _parse_links(self, values: dict) -> dict:
        """The elements Site and Building values name, by GlobalId; empty unlinks."""
        links = {}
        for prefix, (ifc_class, _) in SPATIAL_ELEMENTS.items():
            if prefix not in values or values[prefix] == self.CONFLICT:
                continue
            if not values[prefix]:
                links[prefix] = None
                continue
            try:
                element = tool.Ifc.get().by_guid(values[prefix])
            except RuntimeError:
                element = None
            if element is None or not element.is_a(ifc_class):
                raise ValueError(f"That {ifc_class[3:].lower()} is no longer in the model.")
            links[prefix] = element
        return links

    def _no_spatial_reason(self, prefix: str) -> str:
        ifc_class = SPATIAL_ELEMENTS[prefix][0]
        noun = ifc_class[3:].lower()
        if not tool.Ifc.get().by_type(ifc_class):
            return f"This model has no {noun} - add an {ifc_class} in Bonsai first."
        return f"This sheet has no {noun} - pick one in its {prefix} list first."

    def _edit_spatial_element(self, element: ifcopenshell.entity_instance, attributes: dict) -> None:
        """Edit a site's or building's attributes, as Bonsai's attribute panel does.

        Its name is also its Blender object's name and its label in the spatial
        tree, so both are brought up to date with it.
        """
        tool.Ifc.run("attribute.edit_attributes", product=element, attributes=attributes)
        if "Name" in attributes:
            if obj := tool.Ifc.get_object(element):
                tool.Root.set_object_name(obj, element)
            import bonsai.core.spatial

            bonsai.core.spatial.import_spatial_decomposition(tool.Spatial)

    def _edit_address(self, element: ifcopenshell.entity_instance, attribute: str, attributes: dict) -> None:
        """Edit an element's postal address, giving it one if it has none.

        An address shared with another element - a site and its building often
        share one - changes for both, which is what sharing it means.
        """
        ifc_file = tool.Ifc.get()
        address = getattr(element, attribute)
        if address is None:
            if not any(attributes.values()):
                return
            address = ifc_file.createIfcPostalAddress(Purpose="SITE" if element.is_a("IfcSite") else None)
            tool.Ifc.run("attribute.edit_attributes", product=element, attributes={attribute: address})

        tool.Ifc.run("owner.edit_address", address=address, attributes=attributes)

        # An address with nothing in it is invalid IFC (IfcPostalAddress.WR1), so
        # clearing every part removes it rather than leaving it empty.
        parts = ("InternalLocation", "AddressLines", "PostalBox", "PostalCode", "Town", "Region", "Country")
        if not any(getattr(address, name, None) for name in parts):
            for inverse in ifc_file.get_inverse(address):
                for name in ("SiteAddress", "BuildingAddress"):
                    if getattr(inverse, name, None) == address:
                        tool.Ifc.run("attribute.edit_attributes", product=inverse, attributes={name: None})
            if not ifc_file.get_total_inverses(address):
                ifc_file.remove(address)

    @staticmethod
    def _sheet_associations(sheet: ifcopenshell.entity_instance) -> list:
        if sheet.file.schema == "IFC2X3":
            return [r for r in sheet.file.by_type("IfcRelAssociatesDocument") if r.RelatingDocument == sheet]
        return list(sheet.DocumentInfoForObjects or [])

    @staticmethod
    def _only(elements: list) -> Union[ifcopenshell.entity_instance, None]:
        return elements[0] if len(elements) == 1 else None

    @staticmethod
    def _containing(element: ifcopenshell.entity_instance, ifc_class: str) -> Union[ifcopenshell.entity_instance, None]:
        """The nearest element of this class that `element` is part of."""
        parent = ifcopenshell.util.element.get_aggregate(element)
        while parent is not None and not parent.is_a(ifc_class):
            parent = ifcopenshell.util.element.get_aggregate(parent)
        return parent

    def _top_level_sites(self, ifc_file: ifcopenshell.file) -> list:
        """Sites directly under the project, or under nothing - not the lots of a site complex."""
        sites = []
        for site in ifc_file.by_type("IfcSite"):
            parent = ifcopenshell.util.element.get_aggregate(site)
            if parent is None or parent.is_a("IfcProject"):
                sites.append(site)
        return sites

    def _buildings_in(self, ifc_file: ifcopenshell.file, site: Union[ifcopenshell.entity_instance, None]) -> list:
        """The outermost buildings on a site, or in the model - not a building complex's parts."""
        if site is None:
            return [b for b in ifc_file.by_type("IfcBuilding") if not self._containing(b, "IfcBuilding")]
        found, queue = [], [site]
        while queue:
            for part in ifcopenshell.util.element.get_parts(queue.pop()):
                if part.is_a("IfcBuilding"):
                    found.append(part)
                elif part.is_a("IfcSite"):
                    queue.append(part)
        return found

    def build_titleblock(self, root: ET.Element, sheet: ifcopenshell.entity_instance) -> None:
        titleblock = root.findall(f'{SVG}g[@data-type="titleblock"]')[0]
        image = titleblock.findall(f"{SVG}image")[0]
        g = self.parse_embedded_svg(image, self.get_titleblock_data(sheet))
        grid_north = ifcopenshell.util.geolocation.get_grid_north(tool.Ifc.get()) * -1
        true_north = ifcopenshell.util.geolocation.get_true_north(tool.Ifc.get()) * -1
        for north in g.iterfind(f'.//{SVG}g[@data-type="grid-north"]'):
            north.attrib["transform"] = f"rotate({grid_north})"
        for north in g.iterfind(f'.//{SVG}g[@data-type="true-north"]'):
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
        assert style is not None
        style_data = style.text
        assert style_data is not None
        text = ""
        brackets_level = 0
        selector_buffer = ""  # Buffer to accumulate selectors across lines

        for l in style_data:
            if l == "{":
                if brackets_level == 0:
                    # Get all accumulated selector text (may span multiple lines)
                    # Find where the last rule ended (after last }) or start of text
                    last_close = text.rfind("}")
                    if last_close == -1:
                        selector_text = text
                        text = ""
                    else:
                        selector_text = text[last_close + 1 :]
                        text = text[: last_close + 1]

                    # Process all selectors (split by comma)
                    css_selectors = []
                    for css_selector in selector_text.split(","):
                        css_selector = css_selector.strip()
                        if css_selector:  # Only process non-empty selectors
                            css_selector = f"{css_selector}.{prefix}"
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
            if "style" in attrib:
                attrib["style"] = replace_urls(attrib["style"])
            if svg_element.tag == f"{SVG}use":
                href_attrib = f"{XLINK}href"
                if href_attrib in attrib:
                    href = attrib[href_attrib]
                    if href.startswith("#"):
                        attrib[href_attrib] = f"#{prefix}-{href[1:]}"

        return svg

    def build_drawings(self, root: ET.Element, sheet: ifcopenshell.entity_instance):
        for view in root.findall(f'{SVG}g[@data-type="drawing"]'):
            drawing_id = int(view.attrib["data-id"])
            try:
                reference = tool.Ifc.get().by_id(int(view.attrib["data-id"]))
                drawing = tool.Ifc.get().by_guid(view.attrib["data-drawing"])
            except RuntimeError:
                # Perhaps the SVG has outdated content or is edited externally which we cannot control.
                continue

            images = view.findall(f"{SVG}image")

            foreground = None
            view_title = None

            for image in images:
                if image.attrib["data-type"] == "foreground":
                    foreground = image
                elif image.attrib["data-type"] == "view-title":
                    view_title = image

            if foreground is not None:
                svg = self.parse_embedded_svg(foreground, {})
                svg = self.ensure_drawing_unique_styles(svg, drawing_id)
                view.append(svg)

            if view_title is not None:
                assert foreground is not None
                foreground_path = self.get_href(foreground)
                data = self.get_drawing_view_title_data(reference, sheet, drawing, foreground_path)
                view.append(self.parse_embedded_svg(view_title, data))

            for image in images:
                view.remove(image)

    def get_drawing_view_title_data(
        self,
        reference: ifcopenshell.entity_instance,
        sheet: ifcopenshell.entity_instance,
        drawing: ifcopenshell.entity_instance,
        foreground_path: str,
    ) -> dict:
        """Template data for a drawing's view-title.

        Shared by `build_drawings` and `get_template_values`, so a tool showing a
        sheet without building it fills the title exactly as a build would.
        """
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
        return data

    def build_documents(self, root: ET.Element, sheet: ifcopenshell.entity_instance) -> None:
        schedules = root.findall(f'{SVG}g[@data-type="schedule"]')
        references = root.findall(f'{SVG}g[@data-type="reference"]')
        documents = schedules + references
        for view in documents:
            try:
                reference = tool.Ifc.get().by_id(int(view.attrib["data-id"]))
                document = tool.Ifc.get().by_id(int(view.attrib["data-document"]))
            except:
                # Perhaps the SVG has outdated content or is edited externally which we cannot control.
                continue

            images = view.findall(f"{SVG}image")

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
                data = self.get_document_view_title_data(reference, sheet, document)
                view.append(self.parse_embedded_svg(view_title, data))

            for image in images:
                view.remove(image)

    def get_document_view_title_data(
        self,
        reference: ifcopenshell.entity_instance,
        sheet: ifcopenshell.entity_instance,
        document: ifcopenshell.entity_instance,
    ) -> dict:
        """Template data for a schedule's or reference's view-title.

        Shared by `build_documents` and `get_template_values`.
        """
        data = reference.get_info()
        data.update({"Sheet" + k: v for k, v in sheet.get_info().items()})
        if not data["Name"]:
            data["Name"] = document.Name or "Unnamed"
        return data

    def get_template_values(self) -> dict:
        """The data every sheet's templates are filled with, without building.

        For tools that display sheets from their layouts, rendering them live,
        so view-titles and titleblocks read as a build would. The data comes from
        the same methods `build` uses, and from the model in memory, unsaved
        edits included.

        Sheets are keyed by their layout's path and placements by the path of the
        file they place: a layout's ``data-id`` is a STEP id, which does not
        survive a re-serialised model. Values are text, as pystache renders them,
        except the booleans and lists of rows that templates test and iterate.

        ::

            {
                "ifc": "<absolute path, or empty if unsaved>",
                "sheets": [
                    {
                        "identification": "A01",
                        "layout": "<absolute path>",
                        "values": {...titleblock data...},
                        "placements": {"<absolute path>": {...view-title data...}},
                        "drawings": {"<drawing GlobalId>": {...the same, for drawings...}},
                    }
                ],
                "north": {"grid": "rotate(...)", "true": "rotate(...)"},
            }
        """
        ifc_file = tool.Ifc.get()
        ifc_path = tool.Ifc.get_path()
        result = {
            "ifc": os.path.abspath(ifc_path) if ifc_path else "",
            "sheets": [],
            "north": {"grid": "rotate(0)", "true": "rotate(0)"},
        }
        if not ifc_file:
            return result

        key = self._path_key
        drawings = self._drawings_by_uri()
        documents = self._documents_by_uri()

        for sheet in ifc_file.by_type("IfcDocumentInformation"):
            if sheet.Scope != "SHEET":
                continue
            layout = tool.Drawing.get_document_uri(sheet, "LAYOUT")
            if not layout:
                continue

            placements = {}
            by_drawing = {}
            for reference in tool.Drawing.get_document_references(sheet):
                kind = tool.Drawing.get_reference_description(reference)
                if kind in ("LAYOUT", "TITLEBLOCK", "SHEET"):
                    continue
                uri = tool.Drawing.get_document_uri(reference)
                if not uri:
                    continue
                if kind == "DRAWING":
                    if (drawing := drawings.get(key(uri))) is None:
                        continue
                    data = self.get_drawing_view_title_data(reference, sheet, drawing, uri)
                    by_drawing[drawing.GlobalId] = as_template_data(data)
                else:
                    if (document := documents.get(key(uri))) is None:
                        continue
                    data = self.get_document_view_title_data(reference, sheet, document)
                placements[os.path.abspath(uri)] = as_template_data(data)

            result["sheets"].append(
                {
                    "identification": str(tool.Drawing.get_sheet_identification(sheet)),
                    "layout": os.path.abspath(layout),
                    "values": as_template_data(self.get_titleblock_data(sheet)),
                    "placements": placements,
                    "drawings": by_drawing,
                }
            )

        grid_north = ifcopenshell.util.geolocation.get_grid_north(ifc_file) * -1
        true_north = ifcopenshell.util.geolocation.get_true_north(ifc_file) * -1
        result["north"] = {"grid": f"rotate({grid_north})", "true": f"rotate({true_north})"}
        return result

    def find_sheet(self, layout: str) -> Union[ifcopenshell.entity_instance, None]:
        """The sheet whose layout is at `layout`, or None.

        By path, as `get_template_values` keys its sheets: a layout's STEP id
        does not survive a re-serialised model, and the same file can be spelled
        several ways on Windows.
        """
        ifc_file = tool.Ifc.get()
        if not ifc_file:
            return None
        target = self._path_key(layout)
        for sheet in ifc_file.by_type("IfcDocumentInformation"):
            if sheet.Scope != "SHEET":
                continue
            uri = tool.Drawing.get_document_uri(sheet, "LAYOUT")
            if uri and self._path_key(uri) == target:
                return sheet
        return None

    def get_editable_fields(self, layout: str, target: dict, fields: list[str]) -> dict:
        """Which of `fields` can be written back on this view, and what they hold.

        `fields` are the placeholders a template actually uses, so a tool can
        offer what is on the sheet rather than every attribute of the entity
        behind it. Whether a field is writable is answered here, beside the
        operations that would apply it: a tool deciding for itself would drift
        from what `set_template_values` accepts.

        ::

            {"fields": [{"name": "Name", "value": "SITE PLAN", "editable": True},
                        {"name": "Scale", "value": "1:100", "editable": False,
                         "reason": "..."}]}
        """
        sheet = self._require_sheet(layout)
        kind, reference, entity = self._find_target(sheet, target)
        data = self._view_data(sheet, kind, reference, entity)
        writable = self.WRITABLE_FIELDS[kind]

        answer = []
        for name in fields:
            if kind == "sheet" and name in SPATIAL_ELEMENTS:
                answer.append(self.get_link_field(sheet, name))
                continue
            # Unset reads as empty here, not as the "None" a build prints: this
            # value goes into a box someone types in, and saving it back would
            # otherwise set the attribute to the word.
            value = data.get(name)
            field = {"name": name, "value": "" if value is None else as_template_data(value)}
            if name in writable:
                field["editable"] = True
            else:
                field["editable"] = False
                if reason := self._read_only_reason(kind, name):
                    field["reason"] = reason
            answer.append(field)
        return {"fields": answer, "kind": kind}

    def check_template_values(self, layout: str, target: dict, values: dict) -> dict:
        """Refuse what `set_template_values` would refuse, without writing anything.

        A caller applying an edit as an undoable operator asks this first, so a
        refusal comes back as its reason rather than as a failed operator, and
        leaves nothing in the undo history. Returns the values as text.
        """
        sheet = self._require_sheet(layout)
        kind, _, _ = self._find_target(sheet, target)
        writable = self.WRITABLE_FIELDS[kind]
        for name in values:
            if name not in writable:
                raise ValueError(f"{name} cannot be edited: {self._read_only_reason(kind, name)}")
        values = {name: ("" if value is None else str(value)) for name, value in values.items()}
        if kind == "sheet":
            # Links first, then whether each field has an element to go to once
            # they apply.
            links = self._parse_links(values)
            elements = self.get_sheet_spatial(sheet, links)
            for prefix in {SPATIAL_FIELDS[field][0] for field in values if field in SPATIAL_FIELDS}:
                if elements[prefix] is None:
                    raise ValueError(self._no_spatial_reason(prefix))
        return values

    def set_template_values(self, layout: str, target: dict, values: dict) -> dict:
        """Apply template values to the model in memory, through Bonsai.

        Every field goes through the operation Bonsai itself uses, because
        several of them are not just an attribute: renaming a sheet moves its
        layout and its built sheet, renaming a drawing moves its SVG and relinks
        every layout that places it. Writing the attribute alone would leave the
        model naming files that are not there.

        Raises ValueError with a reason a person can read - the caller is a
        remote tool, and the message is what it shows. Everything that can be
        refused is, before anything is written (`check_template_values`).
        """
        import bonsai.core.drawing as core

        values = self.check_template_values(layout, target, values)
        if not values:
            return {"changed": []}
        sheet = self._require_sheet(layout)
        kind, reference, entity = self._find_target(sheet, target)

        if kind == "sheet":
            links = self._parse_links(values)
            spatial = {k: v for k, v in values.items() if k in SPATIAL_FIELDS}
            elements = self.get_sheet_spatial(sheet, links)
            # Identification and Name name the layout and sheet files together,
            # so they are renamed together, keeping whichever is not being set.
            if "Identification" in values or "Name" in values:
                core.rename_sheet(
                    tool.Ifc,
                    tool.Drawing,
                    sheet=sheet,
                    identification=values.get("Identification", str(tool.Drawing.get_sheet_identification(sheet))),
                    name=values.get("Name", sheet.Name or ""),
                )
            if links:
                self.set_sheet_links(sheet, links)
            # The site's and building's, not the sheet's: every sheet on them shows it.
            if spatial:
                self.set_spatial_fields(elements, spatial)
            attributes = {
                k: v
                for k, v in values.items()
                if k not in ("Identification", "Name") and k not in SPATIAL_FIELDS and k not in SPATIAL_ELEMENTS
            }
            if attributes:
                tool.Ifc.run("document.edit_information", information=sheet, attributes=attributes)
            tool.Drawing.import_sheets()
        else:
            if "Identification" in values:
                core.rename_reference(tool.Ifc, tool.Drawing, reference=reference, identification=values["Identification"])
            if "Name" in values:
                # A view-title shows the reference's own name when it has one and
                # falls back to the drawing's, so the edit goes wherever the
                # displayed value came from (`get_drawing_view_title_data`).
                if reference.Name:
                    tool.Ifc.run("document.edit_reference", reference=reference, attributes={"Name": values["Name"]})
                elif kind == "drawing":
                    core.update_drawing_name(tool.Ifc, tool.Drawing, drawing=entity, name=values["Name"])
                else:
                    tool.Ifc.run("document.edit_information", information=entity, attributes={"Name": values["Name"]})
            attributes = {k: v for k, v in values.items() if k not in ("Identification", "Name")}
            if attributes:
                tool.Ifc.run("document.edit_reference", reference=reference, attributes=attributes)
            tool.Drawing.import_sheets()
            if kind == "drawing":
                tool.Drawing.import_drawings()

        # Where the sheet is now: renaming one moves its layout, so the path the
        # caller asked about no longer exists. Saying so is what lets a tool ask
        # again straight away rather than wait to notice the file move.
        moved = tool.Drawing.get_document_uri(sheet, "LAYOUT")
        return {"changed": sorted(values), "layout": os.path.abspath(moved) if moved else ""}

    #: What each kind of view can write back. An allow-list, because the rest of
    #: a document's attributes are either maintained by Bonsai alongside files on
    #: disk, or are entities rather than text.
    WRITABLE_FIELDS = {
        "sheet": (
            "Identification",
            "Name",
            "Description",
            "Purpose",
            "IntendedUse",
            "Revision",
            "Status",
            "Confidentiality",
            "ElectronicFormat",
            "CreationTime",
            "LastRevisionTime",
            "ValidFrom",
            "ValidUntil",
            *SPATIAL_ELEMENTS,
            *SPATIAL_FIELDS,
        ),
        "drawing": ("Identification", "Name", "Description"),
        "document": ("Identification", "Name", "Description"),
    }

    #: Why a field a template uses cannot be written, where there is more to say
    #: than that Bonsai has no operation for it.
    READ_ONLY_REASONS = {
        "Scale": "The scale comes from the drawing's camera.",
        "Scope": "Scope is what makes this document a sheet.",
        "Location": "This is a file path, which Bonsai maintains as things are renamed.",
        "DocumentOwner": "An owner is a person or organisation in the model, not text.",
        "Editors": "Editors are people or organisations in the model, not text.",
        "ReferencedDocument": "This points at another document in the model, not text.",
        "id": "A STEP id belongs to the file, not the sheet.",
        "type": "This is the IFC class of the entity behind the view.",
        "GlobalId": "A GlobalId identifies the drawing; changing it would unlink it.",
        "OwnerHistory": "Ownership is recorded by IFC, not typed in.",
        # The whole address on one line, beside its editable parts: plainly what
        # it is, so nothing is said.
        "SiteAddress": "",
        "BuildingAddress": "",
    }

    def _read_only_reason(self, kind: str, name: str) -> str:
        if kind != "sheet" and name.startswith("Sheet"):
            return "This is the sheet's own field - edit it on the titleblock."
        return self.READ_ONLY_REASONS.get(name, "Bonsai has no operation for this field.")

    @staticmethod
    def _path_key(path: str) -> str:
        return os.path.normcase(os.path.abspath(path))

    def _require_sheet(self, layout: str) -> ifcopenshell.entity_instance:
        sheet = self.find_sheet(layout)
        if sheet is None:
            raise ValueError(f"no sheet in this model uses the layout {os.path.basename(layout)}")
        return sheet

    def _drawings_by_uri(self) -> dict:
        """Every drawing in the model, by the path of the SVG it is drawn into."""
        drawings = {}
        for drawing in tool.Ifc.get().by_type("IfcAnnotation"):
            if drawing.ObjectType != "DRAWING":
                continue
            document = tool.Drawing.get_drawing_document(drawing)
            if document and (uri := tool.Drawing.get_document_uri(document)):
                drawings[self._path_key(uri)] = drawing
        return drawings

    def _documents_by_uri(self) -> dict:
        """Every schedule and reference, by the path of the file it is kept in.

        A schedule is kept as a spreadsheet and placed as the SVG rendered
        beside it (`add_document`), so the sheet's reference names a file the
        document itself never does. Both spellings are keyed, or a schedule
        would be looked up by the `.svg` and never found.
        """
        documents = {}
        for information in tool.Ifc.get().by_type("IfcDocumentInformation"):
            if information.Scope not in ("SCHEDULE", "REFERENCE"):
                continue
            for reference in tool.Drawing.get_document_references(information):
                if uri := tool.Drawing.get_document_uri(reference):
                    for path in (uri, tool.Drawing.get_path_with_ext(uri, "svg")):
                        documents.setdefault(self._path_key(path), information)
        return documents

    def _find_target(self, sheet: ifcopenshell.entity_instance, target: dict) -> tuple:
        """The view a request names, as (kind, reference, entity).

        A view is named by the GlobalId of its drawing or by the path of the file
        it places - the same two handles `get_template_values` answers with, and
        the only two that survive a re-serialised model.
        """
        kind = target.get("kind", "sheet")
        if kind in ("sheet", "titleblock"):
            return "sheet", None, sheet

        wanted_guid = target.get("globalId")
        wanted_path = self._path_key(target["path"]) if target.get("path") else None
        if not wanted_guid and not wanted_path:
            raise ValueError("a view has to be named by its drawing's GlobalId or by its file")

        drawings = self._drawings_by_uri()
        documents = self._documents_by_uri()
        for reference in tool.Drawing.get_document_references(sheet):
            description = tool.Drawing.get_reference_description(reference)
            if description in ("LAYOUT", "TITLEBLOCK", "SHEET"):
                continue
            uri = tool.Drawing.get_document_uri(reference)
            if not uri:
                continue
            uri_key = self._path_key(uri)
            drawing = drawings.get(uri_key)
            if wanted_guid and drawing is not None and drawing.GlobalId == wanted_guid:
                return "drawing", reference, drawing
            if wanted_path and uri_key == wanted_path:
                if drawing is not None:
                    return "drawing", reference, drawing
                document = documents.get(uri_key)
                if document is not None:
                    return "document", reference, document
        raise ValueError(f"{sheet.Name or 'this sheet'} has no such view - it may have been moved or removed")

    def _view_data(
        self,
        sheet: ifcopenshell.entity_instance,
        kind: str,
        reference: Union[ifcopenshell.entity_instance, None],
        entity: ifcopenshell.entity_instance,
    ) -> dict:
        """What this view's template is filled with - the same data a build uses."""
        if kind == "sheet":
            return self.get_titleblock_data(sheet)
        if kind == "drawing":
            uri = tool.Drawing.get_document_uri(reference) or ""
            return self.get_drawing_view_title_data(reference, sheet, entity, uri)
        return self.get_document_view_title_data(reference, sheet, entity)

    def get_href(self, element: ET.Element) -> str:
        return urllib.parse.unquote(element.attrib[f"{XLINK}href"]).replace("\\", "/")

    def parse_embedded_svg(self, image: ET.Element, data: dict) -> ET.Element:
        group = ET.Element("g")
        x, y = self.convert_to_mm(image.attrib["x"]), self.convert_to_mm(image.attrib["y"])
        group.attrib["transform"] = f"translate({x},{y})"

        # Convert viewBox into a clip path
        clip_id = str(uuid.uuid4())
        group.attrib["clip-path"] = f"url(#{clip_id})"
        clip_path = ET.Element("clipPath")
        clip_path.attrib["id"] = clip_id
        rect = ET.Element("rect")
        rect.attrib["x"] = "0"
        rect.attrib["y"] = "0"
        rect.attrib["width"] = str(self.convert_to_mm(image.attrib["width"]))
        rect.attrib["height"] = str(self.convert_to_mm(image.attrib["height"]))
        clip_path.append(rect)
        self.defs.append(clip_path)

        svg_path = self.get_href(image)
        with open(os.path.join(self.layout_dir, svg_path), "r") as template:
            embedded = ET.fromstring(pystache.render(template.read(), data))
            # viewBox should not be nested
            embedded.attrib["viewBox"] = ""
            # TODO: This should not be in this function
            self.scale = embedded.attrib.get("data-scale")
            images = embedded.findall(f"{SVG}image")
            for image in images:
                old_href = Path(image.attrib[f"{XLINK}href"])
                if not os.path.isabs(old_href):
                    template_dir = Path(os.path.join(self.layout_dir, svg_path)).resolve().parent
                    old_href = Path(os.path.join(template_dir, old_href))
                old_href = old_href.absolute().resolve().as_posix()
                new_href = Path(os.path.join(self.sheets_dir, Path(old_href).name)).absolute().resolve().as_posix()
                shutil.copy(old_href, new_href)
                image.attrib[f"{XLINK}href"] = Path(old_href).name
        for child in embedded:
            if "namedview" in child.tag:
                continue
            group.append(child)
        return group

    def change_titleblock(self, sheet: ifcopenshell.entity_instance, titleblock_name: str) -> None:
        ootb_titleblock_path = tool.Blender.get_data_dir_path(
            Path("templates") / "titleblocks" / (titleblock_name + ".svg")
        )
        titleblock_path = tool.Ifc.resolve_uri(tool.Drawing.get_default_titleblock_path(titleblock_name))
        sheet_path = tool.Drawing.get_document_uri(sheet, "LAYOUT")
        assert sheet_path is not None
        sheet_dir = os.path.dirname(sheet_path)

        os.makedirs(sheet_dir, exist_ok=True)
        os.makedirs(os.path.dirname(titleblock_path), exist_ok=True)
        if not os.path.exists(titleblock_path):
            shutil.copy(ootb_titleblock_path, titleblock_path)

        ET.register_namespace("", "http://www.w3.org/2000/svg")
        ET.register_namespace("xlink", "http://www.w3.org/1999/xlink")

        view_root = ET.parse(titleblock_path).getroot()
        view_width = self.convert_to_mm(view_root.attrib["width"])
        view_height = self.convert_to_mm(view_root.attrib["height"])

        sheet_tree = ET.parse(sheet_path)
        root = sheet_tree.getroot()

        titleblock = sheet_tree.findall(f'{SVG}g[@data-type="titleblock"]')[0]
        image = titleblock.findall(f"{SVG}image[@{XLINK}href]")[0]
        image.attrib[f"{XLINK}href"] = os.path.relpath(titleblock_path, sheet_dir)
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
