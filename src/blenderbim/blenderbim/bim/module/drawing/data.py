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

import bpy
import ifcopenshell.util.element
import ifcopenshell.util.representation
import blenderbim.tool as tool


def refresh():
    ProductAssignmentsData.is_loaded = False
    SheetsData.is_loaded = False
    SchedulesData.is_loaded = False
    DrawingsData.is_loaded = False
    DecoratorData.data = {}


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
        cls.data = {"total_sheets": cls.total_sheets()}
        cls.is_loaded = True

    @classmethod
    def total_sheets(cls):
        return len([d for d in tool.Ifc.get().by_type("IfcDocumentInformation") if d.Scope == "DOCUMENTATION"])


class DrawingsData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.data = {"total_drawings": cls.total_drawings(), "location_hint": cls.location_hint()}
        cls.is_loaded = True

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


class SchedulesData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.data = {"total_schedules": cls.total_schedules()}
        cls.is_loaded = True

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

    @classmethod
    def get_ifc_text_data(cls, obj):
        """returns font size in mm for current ifc text object"""
        result = cls.data.get(obj.name, None)
        if result is not None:
            return result

        element = tool.Ifc.get_entity(obj)
        if not element or not element.is_a("IfcAnnotation") or element.ObjectType not in ["TEXT", "TEXT_LEADER"]:
            return None

        props = obj.BIMTextProperties
        # getting font size
        classes = ifcopenshell.util.element.get_pset(element, "EPset_Annotation", "Classes")
        # use `regular` as default
        if classes:
            classes_split = classes.split()
            # prioritize smaller font sizes just like in svg
            font_size_type = next(
                (font_size_type for font_size_type in FONT_SIZES if font_size_type in classes_split), "regular"
            )
        else:
            font_size_type = "regular"
        font_size = FONT_SIZES[font_size_type]

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

        text_data = {"Literals": literals_data, "FontSize": font_size}
        cls.data[obj.name] = text_data
        return text_data
