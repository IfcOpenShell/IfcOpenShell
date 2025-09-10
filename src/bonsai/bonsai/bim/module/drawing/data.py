# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
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
import json
import ifcopenshell.util.element
import ifcopenshell.util.representation
import ifcopenshell.util.unit
import bonsai.tool as tool
from pathlib import Path
from typing import Any, Union
from natsort import natsorted


def refresh():
    ProductAssignmentsData.is_loaded = False
    SheetsData.is_loaded = False
    DocumentsData.is_loaded = False
    DrawingsData.is_loaded = False
    ElementFiltersData.is_loaded = False
    AnnotationData.is_loaded = False
    DecoratorData.is_loaded = False


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
        files = [p.stem for p in tool.Blender.get_data_dir_paths(Path("templates") / "titleblocks", "*.svg")]

        if tool.Ifc.get():
            project = tool.Ifc.get().by_type("IfcProject")[0]
            titleblocks_dir = ifcopenshell.util.element.get_pset(project, "BBIM_Documentation", "TitleblocksDir")
            if not titleblocks_dir:
                prefs = tool.Blender.get_addon_preferences()
                titleblocks_dir = prefs.doc.titleblocks_dir
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
    def location_hint(cls) -> list[tuple[tool.Drawing.LocationHintType, str, str]]:
        props = tool.Drawing.get_document_props()
        if props.target_view in ["PLAN_VIEW", "REFLECTED_PLAN_VIEW"]:
            results = [("0", "Origin", "")]
            results.extend(
                [(str(s.id()), s.Name or "Unnamed", "") for s in tool.Ifc.get().by_type("IfcBuildingStorey")]
            )
            return results
        elif props.target_view in ["MODEL_VIEW"]:
            return [(h.upper(), h, "") for h in ["Orthographic", "Perspective"]]
        return [(h.upper(), h, "") for h in ["North", "South", "East", "West"]]

    @classmethod
    def active_drawing_pset_data(cls):
        props = tool.Drawing.get_document_props()
        drawing = props.get_active_drawing()
        if drawing is None:
            return {}
        return ifcopenshell.util.element.get_pset(drawing, "EPset_Drawing")


class ElementFiltersData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.data = {
            "saved_searches": cls.saved_searches(),
            "has_include_filter": cls.has_include_filter(),
            "has_exclude_filter": cls.has_exclude_filter(),
        }
        cls.is_loaded = True

    @classmethod
    def saved_searches(cls):
        if not tool.Ifc.get():
            return []
        groups = tool.Ifc.get().by_type("IfcGroup")
        results = []
        for group in groups:
            try:
                data = json.loads(group.Description)
                if isinstance(data, dict) and data.get("type", None) == "BBIM_Search" and data.get("query", None):
                    results.append(group)
            except:
                pass
        return [(str(g.id()), g.Name or "Unnamed", "") for g in sorted(results, key=lambda x: x.Name or "Unnamed")]

    @classmethod
    def has_include_filter(cls):
        obj = bpy.context.scene.camera
        if not obj:
            return
        element = tool.Ifc.get_entity(obj)
        if not element:
            return
        return bool(ifcopenshell.util.element.get_pset(element, "EPset_Drawing", "Include"))

    @classmethod
    def has_exclude_filter(cls):
        obj = bpy.context.scene.camera
        if not obj:
            return
        element = tool.Ifc.get_entity(obj)
        if not element:
            return
        return bool(ifcopenshell.util.element.get_pset(element, "EPset_Drawing", "Exclude"))


class DocumentsData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        documents = cls.count_documents()
        cls.data = {
            "has_saved_ifc": cls.has_saved_ifc(),
            "total_schedules": documents["SCHEDULE"],
            "total_references": documents["REFERENCE"],
        }
        cls.is_loaded = True

    @classmethod
    def has_saved_ifc(cls):
        return os.path.isfile(tool.Ifc.get_path())

    @classmethod
    def count_documents(cls):
        documents = {
            "SCHEDULE": 0,
            "REFERENCE": 0,
        }
        for d in tool.Ifc.get().by_type("IfcDocumentInformation"):
            scope = d.Scope
            documents[scope] = documents.get(scope, 0) + 1

        return documents


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
    slice_cache = {}
    fill_cache = {}
    camera_location_checksum = ""
    camera_rotation_checksum = ""

    @classmethod
    def clear_cache(cls):
        cls.cut_cache = {}
        cls.layerset_cache = {}
        cls.fill_cache = {}

    @classmethod
    def load(cls, handler):
        cls.is_loaded = True

        text = {}
        dimension = {}
        fall = {}
        symbol = {}
        for obj in bpy.context.visible_objects:
            if not (element := tool.Ifc.get_entity(obj)):
                continue
            if tool.Drawing.is_annotation_object_type(element, ("TEXT", "TEXT_LEADER")):
                text[obj.name] = cls.get_text_data(obj)
                if text[obj.name]["Symbol"]:
                    symbol[obj.name] = cls.get_symbol_data(obj)
            elif tool.Drawing.is_annotation_object_type(
                element, ("DIMENSION", "DIAMETER", "SECTION_LEVEL", "PLAN_LEVEL", "RADIUS")
            ):
                dimension[obj.name] = cls.get_dimension_data(obj)
            elif tool.Drawing.is_annotation_object_type(
                element, ("FALL", "SLOPE_ANGLE", "SLOPE_FRACTION", "SLOPE_PERCENT")
            ):
                fall[obj.name] = cls.get_fall_data(obj)
            elif tool.Drawing.is_annotation_object_type(element, ("SYMBOL",)):
                symbol[obj.name] = cls.get_symbol_data(obj)
        cls.data = {
            "text": text,
            "dimension": dimension,
            "fall": fall,
            "symbol": symbol,
            "object_decorators": cls.object_decorators(handler),
        }

    @classmethod
    def get_batting_thickness(cls, obj):
        """used by IfcAnnotations with ObjectType = "BATTING" """
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
    def get_section_markers_display_data(cls, obj: bpy.types.Object) -> Union[dict[str, Any], None]:
        """used by IfcAnnotations with ObjectType = "SECTION" """
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
    def get_text_data(cls, obj: bpy.types.Object) -> dict[str, Any]:
        """used by Ifc Annotations with ObjectType = "TEXT" / "TEXT_LEADER"\n
        returns font size in mm for current ifc text object"""
        element = tool.Ifc.get_entity(obj)
        assert element

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
        symbol = tool.Drawing.get_annotation_symbol(element)
        newline_at = pset_data.get("Newline_At", 0)
        reverse_list = pset_data.get("Reverse_List", False)
        list_separator = pset_data.get("List_Separator") or ", "

        # other attributes
        literals = tool.Drawing.get_text_literal(obj, return_list=True)
        assert isinstance(literals, list)
        literals_data: list[dict[str, Any]] = []
        product = tool.Drawing.get_assigned_product(element) or element
        for literal in literals:
            literal_value = literal.Literal
            
            try:
                current_value = tool.Drawing.replace_text_literal_variables(literal_value, product)
            except Exception:
                current_value = literal_value
            
            literal_data = {
                "Literal": literal_value,
                "BoxAlignment": literal.BoxAlignment,
                "CurrentValue": tool.Drawing.replace_text_literal_variables(
                    literal_value, product, reverse_list, list_separator
                ),
            }
            literals_data.append(literal_data)

        return {
            "Literals": literals_data,
            "FontSize": font_size,
            "Symbol": symbol,
            "Newline_At": newline_at,
            "Reverse_List": reverse_list,
            "List_Separator": list_separator,
        }

    @classmethod
    def get_dimension_data(cls, obj: bpy.types.Object) -> dict[str, Any]:
        """used by Ifc Annotations with ObjectType:

        DIMENSION / DIAMETER / SECTION_LEVEL / PLAN_LEVEL / RADIUS
        """
        element = tool.Ifc.get_entity(obj)
        assert element
        dimension_style = "arrow"
        fill_bg = False
        classes = ifcopenshell.util.element.get_pset(element, "EPset_Annotation", "Classes")
        if classes:
            assert type(classes) is str
            classes_split = classes.lower().split()
            if "oblique" in classes_split:
                dimension_style = "oblique"
            elif "fill-bg" in classes_split:
                fill_bg = True

        pset_data = ifcopenshell.util.element.get_pset(element, "BBIM_Dimension") or {}
        show_description_only = pset_data.get("ShowDescriptionOnly", False)
        suppress_zero_inches = pset_data.get("SuppressZeroInches", False)
        text_prefix = pset_data.get("TextPrefix", None) or ""
        text_suffix = pset_data.get("TextSuffix", None) or ""
        custom_unit_list = pset_data.get("CustomUnit", None) or ""
        custom_unit = custom_unit_list[0] if custom_unit_list else ""

        return {
            "dimension_style": dimension_style,
            "show_description_only": show_description_only,
            "suppress_zero_inches": suppress_zero_inches,
            "text_prefix": text_prefix,
            "text_suffix": text_suffix,
            "fill_bg": fill_bg,
            "custom_unit": custom_unit,
        }

    @classmethod
    def get_fall_data(cls, obj: bpy.types.Object) -> dict[str, Union[str, None]]:
        object_type = None
        if element := tool.Ifc.get_entity(obj):
            object_type = ifcopenshell.util.element.get_predefined_type(element)
        return {"object_type": object_type}

    @classmethod
    def get_symbol_data(cls, obj: bpy.types.Object) -> Union[str, None]:
        element = tool.Ifc.get_entity(obj)
        assert element
        return tool.Drawing.get_annotation_symbol(element)

    @classmethod
    def object_decorators(cls, handler):
        import bonsai.bim.module.drawing.decoration

        if not bonsai.bim.module.drawing.decoration.DecorationsHandler.installed:
            return []

        props = tool.Drawing.get_document_props()
        if (drawing := props.get_active_drawing()) is None:
            return []

        camera = tool.Ifc.get_object(drawing)
        assert isinstance(camera, bpy.types.Object)
        collection = tool.Blender.get_object_bim_props(camera).collection
        assert collection

        results = []
        viewport = tool.Blender.get_view3d_space()

        for obj in collection.all_objects:
            if not obj.visible_get(viewport=viewport):
                continue
            element = tool.Ifc.get_entity(obj)
            if not element:
                continue
            if not element.is_a("IfcAnnotation"):
                continue
            object_type: Union[str, None] = ifcopenshell.util.element.get_predefined_type(element)
            if object_type == "DRAWING":
                continue
            if dec := handler.decorators.get(object_type, None):
                results.append((obj, dec))
            elif isinstance(obj.data, bpy.types.Mesh):
                if object_type == "LINEWORK" and "dashed" in str(
                    ifcopenshell.util.element.get_pset(element, "EPset_Annotation", "Classes")
                ).split(" "):
                    results.append((obj, handler.decorators["HIDDEN_LINE"]))
                else:
                    results.append((obj, handler.decorators["MISC"]))

        return results


class AnnotationData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.is_loaded = True
        cls.props = tool.Drawing.get_annotation_props()
        cls.data["relating_type_id"] = cls.relating_type_id()
        cls.data["relating_types"] = cls.relating_types()

    @classmethod
    def relating_type_id(cls):
        object_type = cls.props.object_type
        relating_types = []
        for relating_type in tool.Ifc.get().by_type("IfcTypeProduct"):
            if tool.Drawing.is_annotation_object_type(relating_type, object_type):
                relating_types.append(relating_type)

        results = [(str(e.id()), e.Name or "Unnamed", e.Description or "") for e in relating_types]
        results = natsorted(results, key=lambda x: x[1])
        results = [("0", "Untyped", "")] + results
        return results

    @classmethod
    def relating_types(cls):
        object_type = cls.props.object_type
        relating_types = []
        for relating_type in tool.Ifc.get().by_type("IfcTypeProduct"):
            if tool.Drawing.is_annotation_object_type(relating_type, object_type):
                relating_types.append(
                    {
                        "id": relating_type.id(),
                        "name": relating_type.Name or "Unnamed",
                        "description": relating_type.Description or "No Description",
                    }
                )

        return sorted(relating_types, key=lambda x: x["name"])


class ElementValuesData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.is_loaded = True

    @classmethod
    def get_available_element_value_keys(cls, element: ifcopenshell.entity_instance) -> dict[str, list[tuple[str, str]]]:
        """Get all available selector syntax keys for the element following IfcOpenshell selector syntax documentation"""
        keys = {}
        
        basic_keys = []
        basic_keys.append(("id", f"IFC ID: {element.id()}"))
        basic_keys.append(("class", f"IFC Class: {element.is_a()}"))
        
        predefined_type = ifcopenshell.util.element.get_predefined_type(element)
        if predefined_type and predefined_type != "NOTDEFINED":
            basic_keys.append(("predefined_type", f"Predefined Type: {predefined_type}"))
        
        keys["Basic"] = basic_keys
        
        element_attrs = []
        excluded_attrs = {'id', 'type', 'GlobalId', 'OwnerHistory', 'ObjectPlacement', 'Representation'}
        
        for attr_name in element.get_info().keys():
            if attr_name not in excluded_attrs:
                attr_value = getattr(element, attr_name, None)
                if attr_value is not None:
                    element_attrs.append((attr_name, f"{attr_name}: {attr_value}"))
        
        keys["Attributes"] = element_attrs
        
        pset_keys = []
        psets = ifcopenshell.util.element.get_psets(element, psets_only=True)
        if psets:
            for pset_name, props in psets.items():
                for prop_name, prop_value in props.items():
                    if isinstance(prop_value, (str, int, float, bool)):
                        pset_keys.append((f"{pset_name}.{prop_name}", f"{pset_name}.{prop_name}: {prop_value}"))
        
        keys["Property Sets"] = pset_keys
        
        qset_keys = []
        qsets = ifcopenshell.util.element.get_psets(element, qtos_only=True)
        if qsets:
            for qset_name, quantities in qsets.items():
                for qty_name, qty_value in quantities.items():
                    if isinstance(qty_value, (str, int, float)):
                        qset_keys.append((f"{qset_name}.{qty_name}", f"{qset_name}.{qty_name}: {qty_value}"))
        
        keys["Quantity Sets"] = qset_keys
        
        type_keys = []
        if hasattr(element, 'IsTypedBy') and element.IsTypedBy:
            element_type = element.IsTypedBy[0].RelatingType
            if hasattr(element_type, 'Name') and element_type.Name:
                type_keys.append((f"type.name", f"Type Name: {element_type.Name}"))
        
        keys["Type"] = type_keys
        
        spatial_keys = []
        
        if hasattr(element, 'ContainedInStructure') and element.ContainedInStructure:
            container = element.ContainedInStructure[0].RelatingStructure
            if hasattr(container, 'Name') and container.Name:
                spatial_keys.append((f"container.name", f"Container: {container.Name}"))
        
        keys["Spatial"] = spatial_keys
        
        parent_keys = []
        parent = ifcopenshell.util.element.get_aggregate(element)
        if parent and hasattr(parent, 'Name') and parent.Name:
            parent_keys.append((f"parent.name", f"Parent: {parent.Name}"))
        
        keys["Parent"] = parent_keys
        
        classification_keys = []
        classifications = ifcopenshell.util.classification.get_references(element)
        if classifications:
            for i, classification in enumerate(classifications):
                if hasattr(classification, 'Name') and classification.Name:
                    classification_keys.append((f"classification[{i}].name", f"Classification: {classification.Name}"))
        
        keys["Classification"] = classification_keys
        
        group_keys = []
        system_keys = []
        zone_keys = []
        
        if hasattr(element, 'HasAssignments'):
            for assignment in element.HasAssignments:
                if assignment.is_a('IfcRelAssignsToGroup'):
                    group = assignment.RelatingGroup
                    if group.is_a('IfcGroup') and not group.is_a('IfcSystem') and not group.is_a('IfcZone') and group.Name:
                        group_keys.append((f"group.name", f"Group: {group.Name}"))
                    elif group.is_a('IfcSystem') and group.Name:
                        system_keys.append((f"system.name", f"System: {group.Name}"))
                    elif group.is_a('IfcZone') and group.Name:
                        zone_keys.append((f"zone.name", f"Zone: {group.Name}"))
        
        keys["Groups"] = group_keys
        keys["Systems"] = system_keys
        keys["Zones"] = zone_keys
        
        material_keys = []
        material = ifcopenshell.util.element.get_material(element, should_skip_usage=True)
        if material:
            if hasattr(material, 'Name') and material.Name:
                material_keys.append((f"material.name", f"Material: {material.Name}"))
        
        keys["Material"] = material_keys
        
        coordinate_keys = []
        coordinate_keys.append(("x", "X Coordinate"))
        coordinate_keys.append(("y", "Y Coordinate"))
        coordinate_keys.append(("z", "Z Coordinate"))
        coordinate_keys.append(("easting", "Easting"))
        coordinate_keys.append(("northing", "Northing"))
        coordinate_keys.append(("elevation", "Elevation"))
        
        keys["Coordinates"] = coordinate_keys
        
        return keys