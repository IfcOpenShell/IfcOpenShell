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

import json
import os
from pathlib import Path
from typing import Any, Union

import bpy
import ifcopenshell.util.classification
import ifcopenshell.util.element
import ifcopenshell.util.placement
import ifcopenshell.util.unit
from natsort import natsorted

import bonsai.tool as tool


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
        """used by Ifc Annotations with ObjectType = "TEXT" / "TEXT_LEADER"
        returns font size in mm for current ifc text object"""
        element = tool.Ifc.get_entity(obj)
        assert element

        # getting font size
        pset_data = ifcopenshell.util.element.get_pset(element, "EPset_Annotation") or {}

        # get font size
        classes = pset_data.get("Classes", None) or "regular"
        classes_split = classes.split()
        font_size_type = next(
            (font_size_type for font_size_type in FONT_SIZES if font_size_type in classes_split), "regular"
        )
        font_size = FONT_SIZES[font_size_type]
        symbol = tool.Drawing.get_annotation_symbol(element)
        newline_at = pset_data.get("Newline_At", 0)

        # other attributes
        literals = tool.Drawing.get_text_literal(obj, return_list=True)
        assert isinstance(literals, list)
        literals_data: list[dict[str, Any]] = []

        product = cls.get_product_for_element_values(obj, element)

        for literal in literals:
            literal_value = literal.Literal
            literal_data = {
                "Literal": literal_value,
                "BoxAlignment": literal.BoxAlignment,
                "CurrentValue": tool.Drawing.replace_text_literal_variables(literal_value, product),
            }
            literals_data.append(literal_data)

        return {
            "Literals": literals_data,
            "FontSize": font_size,
            "Symbol": symbol,
            "Newline_At": newline_at,
        }

    @classmethod
    def get_product_for_element_values(cls, text_obj: bpy.types.Object, element: ifcopenshell.entity_instance):
        """Get the product to use for element values - either ProductUsed or assigned product"""
        props = tool.Drawing.get_text_props(text_obj)
        if props.literals:
            for literal_props in props.literals:
                if hasattr(literal_props, "product_used") and literal_props.product_used:
                    return tool.Ifc.get_entity(literal_props.product_used)

        assigned_product = tool.Drawing.get_assigned_product(element)
        if assigned_product:
            return assigned_product

        return element

    @classmethod
    def get_element_value_by_key(cls, element: ifcopenshell.entity_instance, key: str):
        """Get element value by its key using IfcOpenShell selector syntax"""
        try:
            # Basic keys
            if key == "id":
                return element.id()
            elif key == "class":
                return element.is_a()
            elif key == "predefined_type":
                return ifcopenshell.util.element.get_predefined_type(element)

            # Direct attributes
            elif hasattr(element, key):
                return getattr(element, key)

            # Material keys
            elif key.startswith("material"):
                return cls._get_material_value(element, key)

            # Type keys
            elif key.startswith("type."):
                if hasattr(element, "IsTypedBy") and element.IsTypedBy:
                    element_type = element.IsTypedBy[0].RelatingType
                    attr_name = key.split(".", 1)[1]
                    if hasattr(element_type, attr_name):
                        return getattr(element_type, attr_name)

            elif key == "types.count":
                if hasattr(element, "IsTypedBy") and element.IsTypedBy:
                    element_type = element.IsTypedBy[0].RelatingType
                    occurrence_count = 0
                    if hasattr(element_type, "Types"):
                        for rel in element_type.Types:
                            if hasattr(rel, "RelatedObjects"):
                                occurrence_count += len(rel.RelatedObjects)
                    return occurrence_count

            elif key == "occurrences.count":
                if element.is_a("IfcTypeProduct"):
                    occurrence_count = 0
                    if hasattr(element, "Types"):
                        for rel in element.Types:
                            if hasattr(rel, "RelatedObjects"):
                                occurrence_count += len(rel.RelatedObjects)
                    return occurrence_count

            # Spatial keys
            elif key.startswith("container."):
                container = ifcopenshell.util.element.get_container(element)
                if container:
                    attr_name = key.split(".", 1)[1]
                    if hasattr(container, attr_name):
                        return getattr(container, attr_name)

            elif key.startswith("space."):
                container = ifcopenshell.util.element.get_container(element)
                current = container
                while current:
                    if current.is_a("IfcSpace"):
                        attr_name = key.split(".", 1)[1]
                        if hasattr(current, attr_name):
                            return getattr(current, attr_name)
                        break
                    current = ifcopenshell.util.element.get_aggregate(current)

            elif key.startswith("storey."):
                container = ifcopenshell.util.element.get_container(element)
                current = container
                while current:
                    if current.is_a("IfcBuildingStorey"):
                        attr_name = key.split(".", 1)[1]
                        if hasattr(current, attr_name):
                            return getattr(current, attr_name)
                        break
                    current = ifcopenshell.util.element.get_aggregate(current)

            elif key.startswith("building."):
                container = ifcopenshell.util.element.get_container(element)
                current = container
                while current:
                    if current.is_a("IfcBuilding"):
                        attr_name = key.split(".", 1)[1]
                        if hasattr(current, attr_name):
                            return getattr(current, attr_name)
                        break
                    current = ifcopenshell.util.element.get_aggregate(current)

            elif key.startswith("site."):
                container = ifcopenshell.util.element.get_container(element)
                current = container
                while current:
                    if current.is_a("IfcSite"):
                        attr_name = key.split(".", 1)[1]
                        if hasattr(current, attr_name):
                            return getattr(current, attr_name)
                        break
                    current = ifcopenshell.util.element.get_aggregate(current)

            # Parent keys
            elif key.startswith("parent."):
                parent = ifcopenshell.util.element.get_aggregate(element)
                if parent:
                    attr_name = key.split(".", 1)[1]
                    if hasattr(parent, attr_name):
                        return getattr(parent, attr_name)

            # Group, system, zone keys
            elif key.startswith(("group.", "system.", "zone.")):
                prefix = key.split(".")[0]
                attr_name = key.split(".", 1)[1]

                if hasattr(element, "HasAssignments"):
                    for assignment in element.HasAssignments:
                        if assignment.is_a("IfcRelAssignsToGroup"):
                            group = assignment.RelatingGroup
                            if (
                                prefix == "group"
                                and group.is_a("IfcGroup")
                                and not group.is_a("IfcSystem")
                                and not group.is_a("IfcZone")
                            ):
                                if hasattr(group, attr_name):
                                    return getattr(group, attr_name)
                            elif prefix == "system" and group.is_a("IfcSystem"):
                                if hasattr(group, attr_name):
                                    return getattr(group, attr_name)
                            elif prefix == "zone" and group.is_a("IfcZone"):
                                if hasattr(group, attr_name):
                                    return getattr(group, attr_name)

            elif key in ("groups.count", "systems.count", "zones.count"):
                prefix = key.split(".")[0]
                count = 0

                if hasattr(element, "HasAssignments"):
                    for assignment in element.HasAssignments:
                        if assignment.is_a("IfcRelAssignsToGroup"):
                            group = assignment.RelatingGroup
                            if (
                                prefix == "groups"
                                and group.is_a("IfcGroup")
                                and not group.is_a("IfcSystem")
                                and not group.is_a("IfcZone")
                            ):
                                count += 1
                            elif prefix == "systems" and group.is_a("IfcSystem"):
                                count += 1
                            elif prefix == "zones" and group.is_a("IfcZone"):
                                count += 1

                return count

            # Classification keys
            elif key.startswith("classification."):
                import re

                match = re.match(r"classification\.(\d+)\.(\w+)", key)
                if match:
                    idx = int(match.group(1))
                    attr_name = match.group(2)
                    classifications = ifcopenshell.util.classification.get_references(element)
                    if classifications and 0 <= idx < len(classifications):
                        classification = classifications[idx]
                        if hasattr(classification, attr_name):
                            return getattr(classification, attr_name)

            elif key == "classification.count":
                classifications = ifcopenshell.util.classification.get_references(element)
                return len(classifications) if classifications else 0

            # Profile keys
            elif key.startswith("profiles."):
                import re

                if key == "profiles.count":
                    material = ifcopenshell.util.element.get_material(element, should_skip_usage=True)
                    if material and material.is_a("IfcMaterialProfileSet") and hasattr(material, "MaterialProfiles"):
                        return len(material.MaterialProfiles)
                    return 0

                match = re.match(r"profiles\.(\d+)\.(\w+)", key)
                if match:
                    idx = int(match.group(1))
                    attr_name = match.group(2)
                    material = ifcopenshell.util.element.get_material(element, should_skip_usage=True)
                    if material and material.is_a("IfcMaterialProfileSet") and hasattr(material, "MaterialProfiles"):
                        if 0 <= idx < len(material.MaterialProfiles):
                            profile_item = material.MaterialProfiles[idx]
                            if hasattr(profile_item, "Profile") and profile_item.Profile:
                                profile = profile_item.Profile
                                if hasattr(profile, attr_name):
                                    return getattr(profile, attr_name)
                return None

            elif key.startswith("profile."):
                attr_name = key.split(".", 1)[1]
                if hasattr(element, "Representation") and element.Representation:
                    for representation in element.Representation.Representations:
                        if hasattr(representation, "Items"):
                            for item in representation.Items:
                                if item.is_a("IfcExtrudedAreaSolid") and hasattr(item, "SweptArea"):
                                    profile = item.SweptArea
                                    if hasattr(profile, attr_name):
                                        return getattr(profile, attr_name)
                return None

            # Style keys
            elif key.startswith("styles."):
                import re

                if key == "styles.count":
                    try:
                        styles = ifcopenshell.util.element.get_styles(element)
                        return len(styles) if styles else 0
                    except:
                        return 0

                match = re.match(r"styles\.(\d+)\.(\w+)", key)
                if match:
                    idx = int(match.group(1))
                    attr_name = match.group(2)
                    try:
                        styles = ifcopenshell.util.element.get_styles(element)
                        if styles and 0 <= idx < len(styles):
                            style = styles[idx]
                            if attr_name == "Color" and style.is_a("IfcSurfaceStyle"):
                                # Extract color from surface style
                                if hasattr(style, "Styles"):
                                    for surface_style_elem in style.Styles:
                                        if surface_style_elem.is_a("IfcSurfaceStyleRendering"):
                                            if hasattr(surface_style_elem, "SurfaceColour"):
                                                color = surface_style_elem.SurfaceColour
                                                return f"RGB({color.Red:.2f}, {color.Green:.2f}, {color.Blue:.2f})"
                            elif hasattr(style, attr_name):
                                return getattr(style, attr_name)
                    except:
                        pass
                return None

            # Coordinate keys
            elif key in ("x", "y", "z"):
                if hasattr(element, "ObjectPlacement") and element.ObjectPlacement:
                    matrix = ifcopenshell.util.placement.get_local_placement(element.ObjectPlacement)
                    if matrix is not None:
                        if key == "x":
                            return matrix[0][3]
                        elif key == "y":
                            return matrix[1][3]
                        elif key == "z":
                            return matrix[2][3]
                return None

            elif key in ("easting", "northing", "elevation"):
                if hasattr(element, "ObjectPlacement") and element.ObjectPlacement:
                    try:
                        matrix = ifcopenshell.util.placement.get_local_placement(element.ObjectPlacement)
                        if matrix is not None:
                            ifc_file = element.wrapped_data.file
                            project = ifc_file.by_type("IfcProject")[0] if ifc_file.by_type("IfcProject") else None

                            if project:
                                for context in project.RepresentationContexts or []:
                                    if context.is_a("IfcGeometricRepresentationContext") and hasattr(
                                        context, "HasCoordinateOperation"
                                    ):
                                        for coord_op in context.HasCoordinateOperation:
                                            if coord_op.is_a("IfcMapConversion"):
                                                if key == "easting":
                                                    return matrix[0][3] + coord_op.Eastings
                                                elif key == "northing":
                                                    return matrix[1][3] + coord_op.Northings
                                                elif key == "elevation":
                                                    return matrix[2][3] + coord_op.OrthogonalHeight
                    except:
                        pass
                return None

            # Property sets / Quantity sets (must be checked last to avoid conflicts)
            elif "." in key:
                parts = key.split(".", 1)
                if len(parts) == 2:
                    pset_name, prop_name = parts
                    psets = ifcopenshell.util.element.get_psets(element, psets_only=True)
                    qsets = ifcopenshell.util.element.get_psets(element, qtos_only=True)
                    all_psets = {**psets, **qsets}

                    if pset_name in all_psets and prop_name in all_psets[pset_name]:
                        return all_psets[pset_name][prop_name]

                    # Check for regex patterns (e.g., /Pset_.*Common/)
                    import re

                    if pset_name.startswith("/") and pset_name.endswith("/"):
                        pattern = pset_name[1:-1]
                        try:
                            regex = re.compile(pattern)
                            for actual_pset_name in all_psets.keys():
                                if regex.match(actual_pset_name):
                                    if prop_name in all_psets[actual_pset_name]:
                                        return all_psets[actual_pset_name][prop_name]
                                    elif prop_name.startswith("/") and prop_name.endswith("/"):
                                        prop_pattern = prop_name[1:-1]
                                        prop_regex = re.compile(prop_pattern)
                                        for actual_prop_name, prop_value in all_psets[actual_pset_name].items():
                                            if prop_regex.match(actual_prop_name):
                                                return prop_value
                        except re.error:
                            pass

        except Exception as e:
            print(f"Error getting value for key '{key}': {e}")

        return None

    @classmethod
    def _get_material_value(cls, element: ifcopenshell.entity_instance, key: str):
        """Extract material values using correct selector syntax"""
        material = ifcopenshell.util.element.get_material(element, should_skip_usage=True)
        if not material:
            return None

        if key == "materials.count":
            if material.is_a("IfcMaterialLayerSetUsage") and material.ForLayerSet:
                layer_set = material.ForLayerSet
                if hasattr(layer_set, "MaterialLayers"):
                    return len(layer_set.MaterialLayers)
            elif material.is_a("IfcMaterialLayerSet") and hasattr(material, "MaterialLayers"):
                return len(material.MaterialLayers)
            elif material.is_a("IfcMaterialProfileSet") and hasattr(material, "MaterialProfiles"):
                return len(material.MaterialProfiles)
            elif material.is_a("IfcMaterialConstituentSet") and hasattr(material, "MaterialConstituents"):
                return len(material.MaterialConstituents)
            elif material.is_a("IfcMaterial"):
                return 1
            return 0

        if key == "material.Name":
            return getattr(material, "Name", None)

        elif key.startswith("material.item."):
            import re

            match = re.match(r"material\.item\.(\d+)\.(\w+)", key)
            if match:
                item_idx = int(match.group(1))
                prop_name = match.group(2)

                items = cls._get_material_items(material)
                if items and 0 <= item_idx < len(items):
                    item = items[item_idx]
                    if prop_name == "Name" and hasattr(item, "Material") and item.Material:
                        return getattr(item.Material, "Name", None)
                    elif prop_name == "LayerThickness" and hasattr(item, "LayerThickness"):
                        return getattr(item, "LayerThickness", None)
                    elif hasattr(item, prop_name):
                        return getattr(item, prop_name, None)

            match = re.match(r"material\.item\.Material\.Name\.(\d+)", key)
            if match:
                item_idx = int(match.group(1))
                items = cls._get_material_items(material)
                if items and 0 <= item_idx < len(items):
                    item = items[item_idx]
                    if hasattr(item, "Material") and item.Material:
                        return getattr(item.Material, "Name", None)

        return None

    @classmethod
    def _get_material_items(cls, material):
        """Get material items (layers, profiles, or constituents) from material"""
        if material.is_a("IfcMaterialLayerSetUsage") and hasattr(material, "ForLayerSet") and material.ForLayerSet:
            if hasattr(material.ForLayerSet, "MaterialLayers"):
                return material.ForLayerSet.MaterialLayers
        elif material.is_a("IfcMaterialLayerSet") and hasattr(material, "MaterialLayers"):
            return material.MaterialLayers
        elif material.is_a("IfcMaterialProfileSet") and hasattr(material, "MaterialProfiles"):
            return material.MaterialProfiles
        elif material.is_a("IfcMaterialConstituentSet") and hasattr(material, "MaterialConstituents"):
            return material.MaterialConstituents
        return None

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
    def get_flattened_keys(cls, available_keys: dict[str, list[tuple[str, str]]]) -> list[tuple[str, str]]:
        """Flatten all keys from all categories into a single list for numbering"""
        all_keys_flat = []
        for cat_name, cat_keys in available_keys.items():
            for cat_key, cat_desc in cat_keys:
                all_keys_flat.append((cat_key, cat_desc))
        return all_keys_flat

    @classmethod
    def get_available_element_value_keys(
        cls, element: ifcopenshell.entity_instance
    ) -> dict[str, list[tuple[str, str]]]:
        """Get all available selector syntax keys for the element"""
        keys = {}

        keys["Basic"] = cls._get_basic_keys(element)

        keys["Attributes"] = cls._get_attribute_keys(element)

        keys["Property Sets"] = cls._get_pset_keys(element)
        keys["Quantity Sets"] = cls._get_qset_keys(element)

        keys["Type"] = cls._get_type_keys(element)
        keys["Spatial"] = cls._get_spatial_keys(element)
        keys["Parent"] = cls._get_parent_keys(element)
        keys["Groups"] = cls._get_group_keys(element)
        keys["Systems"] = cls._get_system_keys(element)
        keys["Zones"] = cls._get_zone_keys(element)

        keys["Material"] = cls._get_material_keys(element)
        keys["Styles"] = cls._get_style_keys(element)

        keys["Classification"] = cls._get_classification_keys(element)

        keys["Profiles"] = cls._get_profile_keys(element)

        keys["Coordinates"] = cls._get_coordinate_keys()

        return keys

    @classmethod
    def _get_basic_keys(cls, element):
        keys = []
        keys.append(("id", f"IFC ID: {element.id()}"))
        keys.append(("class", f"IFC Class: {element.is_a()}"))

        predefined_type = ifcopenshell.util.element.get_predefined_type(element)
        if predefined_type and predefined_type != "NOTDEFINED":
            keys.append(("predefined_type", f"Predefined Type: {predefined_type}"))

        return keys

    @classmethod
    def _get_attribute_keys(cls, element):
        keys = []
        excluded_attrs = {"id", "type", "GlobalId", "OwnerHistory", "ObjectPlacement", "Representation"}

        for attr_name in element.get_info().keys():
            if attr_name not in excluded_attrs:
                attr_value = getattr(element, attr_name, None)
                if attr_value is not None:
                    keys.append((attr_name, f"{attr_name}: {attr_value}"))

        return keys

    @classmethod
    def _get_pset_keys(cls, element):
        keys = []
        psets = ifcopenshell.util.element.get_psets(element, psets_only=True)
        if psets:
            for pset_name, props in psets.items():
                for prop_name, prop_value in props.items():
                    if isinstance(prop_value, (str, int, float, bool)):
                        keys.append((f"{pset_name}.{prop_name}", f"{pset_name}.{prop_name}: {prop_value}"))
        return keys

    @classmethod
    def _get_qset_keys(cls, element):
        keys = []
        qsets = ifcopenshell.util.element.get_psets(element, qtos_only=True)
        if qsets:
            for qset_name, quantities in qsets.items():
                for qty_name, qty_value in quantities.items():
                    if isinstance(qty_value, (str, int, float)):
                        keys.append((f"{qset_name}.{qty_name}", f"{qset_name}.{qty_name}: {qty_value}"))
        return keys

    @classmethod
    def _get_material_keys(cls, element):
        keys = []
        material = ifcopenshell.util.element.get_material(element, should_skip_usage=True)
        if not material:
            return keys

        if hasattr(material, "Name") and material.Name:
            keys.append(("material.Name", f"Material: {material.Name}"))

        material_count = 0
        if material.is_a("IfcMaterialLayerSetUsage") and material.ForLayerSet:
            layer_set = material.ForLayerSet
            if hasattr(layer_set, "MaterialLayers"):
                material_count = len(layer_set.MaterialLayers)
                for i, layer in enumerate(layer_set.MaterialLayers):
                    if layer.Material and layer.Material.Name:
                        keys.append(
                            (f"material.item.Material.Name.{i}", f"Layer {i+1} Material Name: {layer.Material.Name}")
                        )
                    if hasattr(layer, "LayerThickness") and layer.LayerThickness:
                        keys.append(
                            (f"material.item.{i}.LayerThickness", f"Layer {i+1} Thickness: {layer.LayerThickness}")
                        )

        elif material.is_a("IfcMaterialLayerSet") and hasattr(material, "MaterialLayers"):
            material_count = len(material.MaterialLayers)
            for i, layer in enumerate(material.MaterialLayers):
                if layer.Material and layer.Material.Name:
                    keys.append(
                        (f"material.item.Material.Name.{i}", f"Layer {i+1} Material Name: {layer.Material.Name}")
                    )
                if hasattr(layer, "LayerThickness") and layer.LayerThickness:
                    keys.append((f"material.item.{i}.LayerThickness", f"Layer {i+1} Thickness: {layer.LayerThickness}"))

        elif material.is_a("IfcMaterialProfileSet") and hasattr(material, "MaterialProfiles"):
            material_count = len(material.MaterialProfiles)
            for i, profile in enumerate(material.MaterialProfiles):
                if profile.Material and profile.Material.Name:
                    keys.append(
                        (f"material.item.Material.Name.{i}", f"Profile {i+1} Material Name: {profile.Material.Name}")
                    )

        elif material.is_a("IfcMaterialConstituentSet") and hasattr(material, "MaterialConstituents"):
            material_count = len(material.MaterialConstituents)
            for i, constituent in enumerate(material.MaterialConstituents):
                if constituent.Material and constituent.Material.Name:
                    keys.append(
                        (
                            f"material.item.Material.Name.{i}",
                            f"Constituent {i+1} Material Name: {constituent.Material.Name}",
                        )
                    )

        elif material.is_a("IfcMaterial"):
            material_count = 1

        if material_count > 0:
            keys.append(("materials.count", f"Material Count: {material_count}"))

        return keys

    @classmethod
    def _get_style_keys(cls, element):
        """Get presentation styles from the element"""
        keys = []

        styles = ifcopenshell.util.element.get_styles(element)
        if styles:
            keys.append(("styles.count", f"Style Count: {len(styles)}"))
            for i, style in enumerate(styles):
                if hasattr(style, "Name") and style.Name:
                    keys.append((f"styles.{i}.Name", f"Style {i+1} Name: {style.Name}"))
                if style.is_a("IfcSurfaceStyle") and hasattr(style, "Styles"):
                    for surface_style_elem in style.Styles:
                        if surface_style_elem.is_a("IfcSurfaceStyleRendering"):
                            if hasattr(surface_style_elem, "SurfaceColour"):
                                color = surface_style_elem.SurfaceColour
                                if hasattr(color, "Red") and hasattr(color, "Green") and hasattr(color, "Blue"):
                                    rgb = f"RGB({color.Red:.2f}, {color.Green:.2f}, {color.Blue:.2f})"
                                    keys.append((f"styles.{i}.Color", f"Style {i+1} Color: {rgb}"))

        return keys

    @classmethod
    def _get_type_keys(cls, element):
        keys = []

        if hasattr(element, "IsTypedBy") and element.IsTypedBy:
            element_type = element.IsTypedBy[0].RelatingType
            if hasattr(element_type, "Name") and element_type.Name:
                keys.append(("type.Name", f"Type Name: {element_type.Name}"))

        if element.is_a("IfcTypeProduct"):
            occurrence_count = 0
            if hasattr(element, "Types"):
                for rel in element.Types:
                    if hasattr(rel, "RelatedObjects"):
                        occurrence_count += len(rel.RelatedObjects)
            keys.append(("occurrences.count", f"Occurrence Count: {occurrence_count}"))

        elif hasattr(element, "IsTypedBy") and element.IsTypedBy:
            element_type = element.IsTypedBy[0].RelatingType
            occurrence_count = 0
            if hasattr(element_type, "Types"):
                for rel in element_type.Types:
                    if hasattr(rel, "RelatedObjects"):
                        occurrence_count += len(rel.RelatedObjects)
            keys.append(("types.count", f"Type Occurrence Count: {occurrence_count}"))

        return keys

    @classmethod
    def _get_spatial_keys(cls, element):
        keys = []

        container = ifcopenshell.util.element.get_container(element)
        if container and hasattr(container, "Name") and container.Name:
            keys.append(("container.Name", f"Container: {container.Name}"))

        space = None
        current = container
        while current:
            if current.is_a("IfcSpace"):
                space = current
                break
            current = ifcopenshell.util.element.get_aggregate(current)
        if space and hasattr(space, "Name") and space.Name:
            keys.append(("space.Name", f"Space: {space.Name}"))

        storey = None
        current = container
        while current:
            if current.is_a("IfcBuildingStorey"):
                storey = current
                break
            current = ifcopenshell.util.element.get_aggregate(current)
        if storey and hasattr(storey, "Name") and storey.Name:
            keys.append(("storey.Name", f"Storey: {storey.Name}"))

        building = None
        current = container
        while current:
            if current.is_a("IfcBuilding"):
                building = current
                break
            current = ifcopenshell.util.element.get_aggregate(current)
        if building and hasattr(building, "Name") and building.Name:
            keys.append(("building.Name", f"Building: {building.Name}"))

        site = None
        current = container
        while current:
            if current.is_a("IfcSite"):
                site = current
                break
            current = ifcopenshell.util.element.get_aggregate(current)
        if site and hasattr(site, "Name") and site.Name:
            keys.append(("site.Name", f"Site: {site.Name}"))

        return keys

    @classmethod
    def _get_parent_keys(cls, element):
        keys = []
        parent = ifcopenshell.util.element.get_aggregate(element)
        if parent and hasattr(parent, "Name") and parent.Name:
            keys.append((f"parent.name", f"Parent: {parent.Name}"))
        return keys

    @classmethod
    def _get_group_keys(cls, element):
        keys = []
        groups = []
        if hasattr(element, "HasAssignments"):
            for assignment in element.HasAssignments:
                if assignment.is_a("IfcRelAssignsToGroup"):
                    group = assignment.RelatingGroup
                    if group.is_a("IfcGroup") and not group.is_a("IfcSystem") and not group.is_a("IfcZone"):
                        groups.append(group)
                        if group.Name:
                            keys.append((f"group.Name", f"Group: {group.Name}"))

        if groups:
            keys.append(("groups.count", f"Group Count: {len(groups)}"))

        return keys

    @classmethod
    def _get_system_keys(cls, element):
        keys = []
        systems = []
        if hasattr(element, "HasAssignments"):
            for assignment in element.HasAssignments:
                if assignment.is_a("IfcRelAssignsToGroup"):
                    group = assignment.RelatingGroup
                    if group.is_a("IfcSystem"):
                        systems.append(group)
                        if group.Name:
                            keys.append((f"system.Name", f"System: {group.Name}"))

        if systems:
            keys.append(("systems.count", f"System Count: {len(systems)}"))

        return keys

    @classmethod
    def _get_zone_keys(cls, element):
        keys = []
        zones = []
        if hasattr(element, "HasAssignments"):
            for assignment in element.HasAssignments:
                if assignment.is_a("IfcRelAssignsToGroup"):
                    group = assignment.RelatingGroup
                    if group.is_a("IfcZone"):
                        zones.append(group)
                        if group.Name:
                            keys.append((f"zone.Name", f"Zone: {group.Name}"))

        if zones:
            keys.append(("zones.count", f"Zone Count: {len(zones)}"))

        return keys

    @classmethod
    def _get_classification_keys(cls, element):
        keys = []
        classifications = ifcopenshell.util.classification.get_references(element)
        if classifications:
            for i, classification in enumerate(classifications):
                if hasattr(classification, "Name") and classification.Name:
                    keys.append((f"classification.{i}.Name", f"Classification {i+1}: {classification.Name}"))
                if hasattr(classification, "Identification") and classification.Identification:
                    keys.append(
                        (
                            f"classification.{i}.Identification",
                            f"Classification {i+1} ID: {classification.Identification}",
                        )
                    )

            keys.append(("classification.count", f"Classification Count: {len(classifications)}"))

        return keys

    @classmethod
    def _get_coordinate_keys(cls):
        return [
            ("x", "X Coordinate"),
            ("y", "Y Coordinate"),
            ("z", "Z Coordinate"),
            ("easting", "Easting"),
            ("northing", "Northing"),
            ("elevation", "Elevation"),
        ]

    @classmethod
    def _get_profile_keys(cls, element):
        """Get profile definitions from the element"""
        keys = []

        material = ifcopenshell.util.element.get_material(element, should_skip_usage=True)
        if material:
            profiles = []
            if material.is_a("IfcMaterialProfileSet") and hasattr(material, "MaterialProfiles"):
                for profile in material.MaterialProfiles:
                    if hasattr(profile, "Profile") and profile.Profile:
                        profiles.append(profile.Profile)

            if profiles:
                keys.append(("profiles.count", f"Profile Count: {len(profiles)}"))
                for i, profile in enumerate(profiles):
                    if hasattr(profile, "ProfileName") and profile.ProfileName:
                        keys.append((f"profiles.{i}.ProfileName", f"Profile {i+1} Name: {profile.ProfileName}"))
                    if hasattr(profile, "ProfileType") and profile.ProfileType:
                        keys.append((f"profiles.{i}.ProfileType", f"Profile {i+1} Type: {profile.ProfileType}"))

        if hasattr(element, "Representation") and element.Representation:
            for representation in element.Representation.Representations:
                if hasattr(representation, "Items"):
                    for item in representation.Items:
                        if item.is_a("IfcExtrudedAreaSolid") and hasattr(item, "SweptArea"):
                            profile = item.SweptArea
                            if hasattr(profile, "ProfileName") and profile.ProfileName:
                                keys.append(("profile.ProfileName", f"Swept Profile Name: {profile.ProfileName}"))
                            if hasattr(profile, "ProfileType") and profile.ProfileType:
                                keys.append(("profile.ProfileType", f"Swept Profile Type: {profile.ProfileType}"))
                            break

        return keys
