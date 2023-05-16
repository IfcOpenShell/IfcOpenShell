# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
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
import bpy
import ifcopenshell.util.element
import ifcopenshell.util.representation
import blenderbim.tool as tool
from pathlib import Path


def refresh():
    ProductAssignmentsData.is_loaded = False
    SheetsData.is_loaded = False
    SchedulesData.is_loaded = False
    DrawingsData.is_loaded = False
    AnnotationData.is_loaded = False
    DecoratorData.data = {}
    DecoratorData.cut_cache = {}
    DecoratorData.layerset_cache = {}


class ProductAssignmentsData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.data = {"relating_product": cls.relating_product()}
        cls.is_loaded = True

    @classmethod
    def relating_product(cls):
        element = tool.Ifc.get_entity(bpy.context.active_object)
        if not element or not element.is_a("IfcAnnotation"):
            return
        for rel in element.HasAssignments:
            if rel.is_a("IfcRelAssignsToProduct"):
                name = rel.RelatingProduct.Name or "Unnamed"
                return f"{rel.RelatingProduct.is_a()}/{name}"


class SheetsData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.data = {
            "has_saved_ifc": cls.has_saved_ifc(),
            "total_sheets": cls.total_sheets(),
            "titleblocks": cls.titleblocks(),
        }
        cls.is_loaded = True

    @classmethod
    def has_saved_ifc(cls):
        return os.path.isfile(tool.Ifc.get_path())

    @classmethod
    def total_sheets(cls):
        return len([d for d in tool.Ifc.get().by_type("IfcDocumentInformation") if d.Scope == "SHEET"])

    @classmethod
    def titleblocks(cls):
        files = Path(os.path.join(bpy.context.scene.BIMProperties.data_dir, "templates", "titleblocks")).glob("*.svg")
        files = [str(f.stem) for f in files]

        if tool.Ifc.get():
            project = tool.Ifc.get().by_type("IfcProject")[0]
            titleblocks_dir = ifcopenshell.util.element.get_pset(project, "BBIM_Documentation", "TitleblocksDir")
            if not titleblocks_dir:
                titleblocks_dir = bpy.context.scene.DocProperties.titleblocks_dir
            titleblocks_dir = tool.Ifc.resolve_uri(titleblocks_dir)
            if os.path.exists(titleblocks_dir):
                files.extend([str(f.stem) for f in Path(titleblocks_dir).glob("*.svg")])

        return [(f, f, "") for f in sorted(list(set(files)))]


class DrawingsData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.data = {
            "has_saved_ifc": cls.has_saved_ifc(),
            "total_drawings": cls.total_drawings(),
            "location_hint": cls.location_hint(),
            "active_drawing_pset_data": cls.active_drawing_pset_data(),
        }
        cls.is_loaded = True

    @classmethod
    def has_saved_ifc(cls):
        return os.path.isfile(tool.Ifc.get_path())

    @classmethod
    def total_drawings(cls):
        return len([e for e in tool.Ifc.get().by_type("IfcAnnotation") if e.ObjectType == "DRAWING"])

    @classmethod
    def location_hint(cls):
        if bpy.context.scene.DocProperties.target_view in ["PLAN_VIEW", "REFLECTED_PLAN_VIEW"]:
            results = [("0", "Origin", "")]
            results.extend(
                [(str(s.id()), s.Name or "Unnamed", "") for s in tool.Ifc.get().by_type("IfcBuildingStorey")]
            )
            return results
        return [(h.upper(), h, "") for h in ["North", "South", "East", "West"]]

    @classmethod
    def active_drawing_pset_data(cls):
        ifc_file = tool.Ifc.get()
        drawing_id = bpy.context.scene.DocProperties.active_drawing_id
        if drawing_id == 0:
            return {}
        drawing = ifc_file.by_id(bpy.context.scene.DocProperties.active_drawing_id)
        return ifcopenshell.util.element.get_pset(drawing, "EPset_Drawing")


class SchedulesData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.data = {"has_saved_ifc": cls.has_saved_ifc(), "total_schedules": cls.total_schedules()}
        cls.is_loaded = True

    @classmethod
    def has_saved_ifc(cls):
        return os.path.isfile(tool.Ifc.get_path())

    @classmethod
    def total_schedules(cls):
        return len([d for d in tool.Ifc.get().by_type("IfcDocumentInformation") if d.Scope == "SCHEDULE"])


FONT_SIZES = {
    "small": 1.8,
    "regular": 2.5,
    "large": 3.5,
    "header": 5.0,
    "title": 7.0,
}


class DecoratorData:
    # stores 1 type of data per object
    data = {}
    cut_cache = {}
    layerset_cache = {}

    # used by Ifc Annotations with ObjectType = "BATTING"
    @classmethod
    def get_batting_thickness(cls, obj):
        result = cls.data.get(obj.name, None)
        if result is not None:
            return result
        element = tool.Ifc.get_entity(obj)
        if element:
            unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
            thickness = ifcopenshell.util.element.get_pset(element, "BBIM_Batting", "Thickness")
            thickness = thickness * unit_scale if thickness else 1.5
            cls.data[obj.name] = thickness
            return thickness

    # used by Ifc Annotations with ObjectType = "SECTION"
    @classmethod
    def get_section_markers_display_data(cls, obj):
        result = cls.data.get(obj.name, None)
        if result is not None:
            return result

        element = tool.Ifc.get_entity(obj)
        if not element:
            return

        # default values
        pset_data = {
            "HasConnectedSectionLine": True,
            "ShowStartArrow": True,
            "StartArrowSymbol": "",
            "ShowEndArrow": True,
            "EndArrowSymbol": "",
        }
        obj_pset_data = ifcopenshell.util.element.get_pset(element, "BBIM_Section") or {}
        pset_data.update(obj_pset_data)

        # create more usable display data
        start_symbol = pset_data["StartArrowSymbol"]
        end_symbol = pset_data["EndArrowSymbol"]
        display_data = {
            "start": {
                "add_circle": pset_data["ShowStartArrow"] and not start_symbol,
                "add_symbol": pset_data["ShowStartArrow"] or bool(start_symbol),
                "symbol": start_symbol or "section-arrow",
            },
            "end": {
                "add_circle": pset_data["ShowEndArrow"] and not end_symbol,
                "add_symbol": pset_data["ShowEndArrow"] or bool(end_symbol),
                "symbol": end_symbol or "section-arrow",
            },
            "connect_markers": pset_data["HasConnectedSectionLine"],
        }

        cls.data[obj.name] = display_data
        return display_data

    # used by Ifc Annotations with ObjectType = "TEXT" / "TEXT_LEADER"
    @classmethod
    def get_ifc_text_data(cls, obj):
        """returns font size in mm for current ifc text object"""
        result = cls.data.get(obj.name, None)
        if result is not None:
            return result

        element = tool.Ifc.get_entity(obj)
        if not element or not tool.Drawing.is_annotation_object_type(element, ["TEXT", "TEXT_LEADER"]):
            return None

        props = obj.BIMTextProperties
        # getting font size
        pset_data = ifcopenshell.util.element.get_pset(element, "EPset_Annotation") or {}
        # use `regular` as default

        # get font size
        classes = pset_data.get("Classes", None) or "regular"
        classes_split = classes.split()
        # prioritize smaller font sizes just like in svg
        font_size_type = next(
            (font_size_type for font_size_type in FONT_SIZES if font_size_type in classes_split), "regular"
        )
        font_size = FONT_SIZES[font_size_type]

        # get symbol
        symbol = pset_data.get("Symbol", None)

        # other attributes
        props_literals = props.literals
        props_literals_n = len(props.literals)
        literals = tool.Drawing.get_text_literal(obj, return_list=True)
        literals_data = []
        for i, literal in enumerate(literals):
            literal_data = {
                "Literal": literal.Literal,
                "BoxAlignment": literal.BoxAlignment,
            }
            if i < props_literals_n:
                literal_data["CurrentValue"] = props_literals[i].value
            else:
                literal_data["CurrentValue"] = literal.Literal

            literals_data.append(literal_data)

        text_data = {"Literals": literals_data, "FontSize": font_size, "Symbol": symbol}
        cls.data[obj.name] = text_data
        return text_data

    # used by Ifc Annotations with ObjectType = "DIMENSION" / "DIAMETER"
    @classmethod
    def get_dimension_data(cls, obj):
        result = cls.data.get(obj.name, None)
        if result is not None:
            return result

        element = tool.Ifc.get_entity(obj)
        supported_object_types = ("DIMENSION", "DIAMETER")
        if not element or not element.is_a("IfcAnnotation") or element.ObjectType not in supported_object_types:
            return None

        dimension_style = "arrow"
        classes = ifcopenshell.util.element.get_pset(element, "EPset_Annotation", "Classes")
        if classes and "oblique" in classes.lower().split():
            dimension_style = "oblique"

        pset_data = ifcopenshell.util.element.get_pset(element, "BBIM_Dimension") or {}
        show_description_only = pset_data.get("ShowDescriptionOnly", False)
        suppress_zero_inches = pset_data.get("SuppressZeroInches", False)
        text_prefix = pset_data.get("TextPrefix", "")
        text_suffix = pset_data.get("TextSuffix", "")

        dimension_data = {
            "dimension_style": dimension_style,
            "show_description_only": show_description_only,
            "suppress_zero_inches": suppress_zero_inches,
            "text_prefix": text_prefix,
            "text_suffix": text_suffix,
        }
        cls.data[obj.name] = dimension_data
        return dimension_data


class AnnotationData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.is_loaded = True
        cls.props = bpy.context.scene.BIMAnnotationProperties
        cls.data["relating_types"] = cls.get_relating_types()

    @classmethod
    def get_relating_types(cls):
        object_type = cls.props.object_type
        relating_types = []
        for relating_type in tool.Ifc.get().by_type("IfcTypeProduct"):
            if tool.Drawing.is_annotation_object_type(relating_type, object_type):
                relating_types.append(relating_type)

        enum_items = [(str(e.id()), e.Name or "Unnamed", e.Description or "") for e in relating_types]

        # item to create anootations without relating types
        enum_items.insert(0, ("0", "-", ""))
        return enum_items
