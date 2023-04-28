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
import math
import json
import functools
import ifcopenshell
import ifcopenshell.util.element
from ifcopenshell.util.doc import get_entity_doc, get_predefined_type_doc
import blenderbim.tool as tool


def refresh():
    AuthoringData.is_loaded = False
    ArrayData.is_loaded = False
    StairData.is_loaded = False
    SverchokData.is_loaded = False
    WindowData.is_loaded = False
    DoorData.is_loaded = False
    RailingData.is_loaded = False
    RoofData.is_loaded = False


class AuthoringData:
    data = {}
    type_thumbnails = {}
    types_per_page = 9
    is_loaded = False

    @classmethod
    def load(cls):
        cls.is_loaded = True
        cls.props = bpy.context.scene.BIMModelProperties
        cls.data["ifc_classes"] = cls.ifc_classes()
        cls.data["relating_type_id"] = cls.relating_type_id()
        cls.data["type_class"] = cls.type_class()
        cls.data["type_predefined_type"] = cls.type_predefined_type()
        cls.data["total_types"] = cls.total_types()
        cls.data["total_pages"] = cls.total_pages()
        cls.data["next_page"] = cls.next_page()
        cls.data["prev_page"] = cls.prev_page()
        cls.data["paginated_relating_types"] = cls.paginated_relating_types()
        cls.data["type_thumbnail"] = cls.type_thumbnail()
        cls.data["is_voidable_element"] = cls.is_voidable_element()
        cls.data["has_visible_openings"] = cls.has_visible_openings()
        cls.data["active_class"] = cls.active_class()
        cls.data["active_material_usage"] = cls.active_material_usage()
        cls.data["active_representation_type"] = cls.active_representation_type()

    @classmethod
    def type_class(cls):
        declaration = tool.Ifc.schema().declaration_by_name("IfcElementType")
        declarations = ifcopenshell.util.schema.get_subtypes(declaration)
        names = [d.name() for d in declarations]

        declaration = tool.Ifc.schema().declaration_by_name("IfcSpatialElementType")
        declarations = ifcopenshell.util.schema.get_subtypes(declaration)
        names.extend([d.name() for d in declarations])

        if tool.Ifc.get_schema() in ("IFC2X3", "IFC4"):
            names.extend(("IfcDoorStyle", "IfcWindowStyle"))

        version = tool.Ifc.get_schema()
        return [(c, c, get_entity_doc(version, c).get("description", "")) for c in sorted(names)]

    @classmethod
    def type_predefined_type(cls):
        results = []
        declaration = tool.Ifc().schema().declaration_by_name(cls.props.type_class)
        version = tool.Ifc.get_schema()
        for attribute in declaration.attributes():
            if attribute.name() == "PredefinedType":
                results.extend(
                    [
                        (e, e, get_predefined_type_doc(version, cls.props.type_class, e))
                        for e in attribute.type_of_attribute().declared_type().enumeration_items()
                    ]
                )
                break
        return results

    @classmethod
    def type_thumbnail(cls):
        if not cls.data["relating_type_id"]:
            return 0
        element = tool.Ifc.get().by_id(int(cls.props.relating_type_id))
        return cls.type_thumbnails.get(element.id(), None) or 0

    @classmethod
    def total_types(cls):
        type_class = cls.props.type_class
        return len(tool.Ifc.get().by_type(type_class)) if type_class else 0

    @classmethod
    def total_pages(cls):
        type_class = cls.props.type_class
        total_types = len(tool.Ifc.get().by_type(type_class)) if type_class else 0
        return math.ceil(total_types / cls.types_per_page)

    @classmethod
    def next_page(cls):
        if cls.props.type_page < cls.total_pages():
            return cls.props.type_page + 1

    @classmethod
    def prev_page(cls):
        if cls.props.type_page > 1:
            return cls.props.type_page - 1

    @classmethod
    def paginated_relating_types(cls):
        type_class = cls.props.type_class
        if not type_class:
            return []
        results = []
        elements = sorted(tool.Ifc.get().by_type(type_class), key=lambda e: e.Name or "Unnamed")
        elements = elements[(cls.props.type_page - 1) * cls.types_per_page : cls.props.type_page * cls.types_per_page]
        for element in elements:
            predefined_type = ifcopenshell.util.element.get_predefined_type(element)
            if predefined_type == "NOTDEFINED":
                predefined_type = None
            results.append(
                {
                    "id": element.id(),
                    "ifc_class": element.is_a(),
                    "name": element.Name or "Unnamed",
                    "description": element.Description or "No Description",
                    "predefined_type": predefined_type,
                    "icon_id": cls.type_thumbnails.get(element.id(), None) or 0,
                }
            )
        return results

    @classmethod
    def is_voidable_element(cls):
        element = tool.Ifc.get_entity(bpy.context.active_object)
        return element and element.is_a("IfcElement") and not element.is_a("IfcOpeningElement")

    @classmethod
    def has_visible_openings(cls):
        element = tool.Ifc.get_entity(bpy.context.active_object)
        if element and element.is_a("IfcElement") and not element.is_a("IfcOpeningElement"):
            for opening in [r.RelatedOpeningElement for r in element.HasOpenings]:
                if tool.Ifc.get_object(opening):
                    return True
        return False

    @classmethod
    def active_class(cls):
        element = tool.Ifc.get_entity(bpy.context.active_object)
        if element:
            return element.is_a()

    @classmethod
    def active_material_usage(cls):
        element = tool.Ifc.get_entity(bpy.context.active_object)
        if element:
            return tool.Model.get_usage_type(element)

    @classmethod
    def active_representation_type(cls):
        if bpy.context.active_object:
            representation = tool.Geometry.get_active_representation(bpy.context.active_object)
            if representation:
                return representation.RepresentationType

    @classmethod
    def ifc_classes(cls):
        results = []
        classes = {
            e.is_a() for e in (tool.Ifc.get().by_type("IfcElementType") + tool.Ifc.get().by_type("IfcSpaceType"))
        }

        if tool.Ifc.get_schema() in ("IFC2X3", "IFC4"):
            classes.update(
                {e.is_a() for e in (tool.Ifc.get().by_type("IfcDoorStyle") + tool.Ifc.get().by_type("IfcWindowStyle"))}
            )
        results.extend([(c, c, "") for c in sorted(classes)])
        return results

    @classmethod
    def relating_type_id(cls):
        ifc_classes = cls.data["ifc_classes"]
        if not ifc_classes:
            return []
        results = []
        ifc_class = cls.props.ifc_class
        if not ifc_class and ifc_classes:
            ifc_class = ifc_classes[0][0]
        if ifc_class:
            elements = sorted(tool.Ifc.get().by_type(ifc_class), key=lambda s: s.Name or "Unnamed")
            results.extend(elements)
            return [
                (str(e.id()), e.Name or "Unnamed", e.Description or "")
                for e in results
            ]
        return []


class ArrayData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.is_loaded = True
        cls.data = {"parameters": cls.parameters()}

    @classmethod
    def parameters(cls):
        element = tool.Ifc.get_entity(bpy.context.active_object)
        if element:
            psets = ifcopenshell.util.element.get_psets(element)
            parameters = psets.get("BBIM_Array", None)
            if parameters:
                try:
                    parent = tool.Ifc.get().by_guid(parameters["Parent"])
                    parameters["has_parent"] = True
                    parameters["parent_name"] = parent.Name or "Unnamed"
                    parameters["data_dict"] = json.loads(parameters.get("Data", "[]") or "[]")
                except:
                    parameters["has_parent"] = False
                return parameters


class StairData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.is_loaded = True
        cls.data = {"parameters": cls.parameters()}

    @classmethod
    def parameters(cls):
        element = tool.Ifc.get_entity(bpy.context.active_object)
        if element:
            psets = ifcopenshell.util.element.get_psets(element)
            parameters = psets.get("BBIM_Stair", None)
            if parameters:
                parameters["data_dict"] = json.loads(parameters.get("Data", "[]") or "[]")
                return parameters


class SverchokData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.is_loaded = True
        cls.data = {"parameters": cls.parameters(), "has_sverchok": cls.has_sverchok()}

    @classmethod
    def parameters(cls):
        element = tool.Ifc.get_entity(bpy.context.active_object)
        if element:
            psets = ifcopenshell.util.element.get_psets(element)
            parameters = psets.get("BBIM_Sverchok", None)
            if parameters:
                parameters["data_dict"] = json.loads(parameters.get("Data", "[]") or "[]")
                return parameters

    @classmethod
    def has_sverchok(cls):
        try:
            import sverchok

            return True
        except:
            return False


class WindowData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.is_loaded = True
        cls.data = {"parameters": cls.parameters()}

    @classmethod
    def parameters(cls):
        element = tool.Ifc.get_entity(bpy.context.active_object)
        if element:
            psets = ifcopenshell.util.element.get_psets(element)
            parameters = psets.get("BBIM_Window", None)
            if parameters:
                parameters["data_dict"] = json.loads(parameters.get("Data", "[]") or "[]")
                return parameters


class DoorData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.is_loaded = True
        cls.data = {"parameters": cls.parameters()}

    @classmethod
    def parameters(cls):
        element = tool.Ifc.get_entity(bpy.context.active_object)
        if element:
            psets = ifcopenshell.util.element.get_psets(element)
            parameters = psets.get("BBIM_Door", None)
            if parameters:
                parameters["data_dict"] = json.loads(parameters.get("Data", "[]") or "[]")
                return parameters


class RailingData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.is_loaded = True
        cls.data = {"parameters": cls.parameters()}

    @classmethod
    def parameters(cls):
        element = tool.Ifc.get_entity(bpy.context.active_object)
        if element:
            psets = ifcopenshell.util.element.get_psets(element)
            parameters = psets.get("BBIM_Railing", None)
            if parameters:
                parameters["data_dict"] = json.loads(parameters.get("Data", "[]") or "[]")
                return parameters


class RoofData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.is_loaded = True
        cls.data = {"parameters": cls.parameters()}

    @classmethod
    def parameters(cls):
        element = tool.Ifc.get_entity(bpy.context.active_object)
        if element:
            psets = ifcopenshell.util.element.get_psets(element)
            parameters = psets.get("BBIM_Roof", None)
            if parameters:
                parameters["data_dict"] = json.loads(parameters.get("Data", "[]") or "[]")
                return parameters
