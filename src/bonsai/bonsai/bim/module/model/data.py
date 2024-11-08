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

import bpy
import math
import json
import ifcopenshell
import ifcopenshell.util.element
import ifcopenshell.util.schema
from ifcopenshell.util.doc import get_entity_doc, get_predefined_type_doc
import bonsai.tool as tool
from math import degrees
from natsort import natsorted


def refresh():
    AuthoringData.is_loaded = False
    ItemData.is_loaded = False
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
    ifc_element_type = None
    is_loaded = False

    @classmethod
    def load(cls, ifc_element_type=None):
        cls.is_loaded = True
        cls.props = bpy.context.scene.BIMModelProperties
        if ifc_element_type:
            cls.ifc_element_type = None if ifc_element_type == "all" else ifc_element_type
        cls.data["default_container"] = cls.default_container()
        cls.data["ifc_element_type"] = cls.ifc_element_type
        cls.data["ifc_classes"] = cls.ifc_classes()
        cls.data["ifc_class_current"] = cls.ifc_class_current()
        cls.data["relating_type_id"] = cls.relating_type_id()  # only after .ifc_classes()
        cls.data["relating_type_id_current"] = cls.relating_type_id_current()  # only after .ifc_classes()
        cls.data["relating_type_name"] = cls.relating_type_name()  # only after .relating_type_id()
        cls.data["relating_type_description"] = cls.relating_type_description()  # only after .relating_type_id()
        cls.data["predefined_type"] = cls.predefined_type()  # only after .relating_type_id()

        # only after .ifc_classes()
        cls.data["total_types"] = cls.total_types()
        cls.data["total_pages"] = cls.total_pages()
        cls.data["next_page"] = cls.next_page()
        cls.data["prev_page"] = cls.prev_page()
        cls.data["paginated_relating_types"] = cls.paginated_relating_types()

        cls.data["type_thumbnail"] = cls.type_thumbnail()  # only after .relating_type_id()
        cls.data["is_voidable_element"] = cls.is_voidable_element()
        cls.data["has_visible_openings"] = cls.has_visible_openings()
        cls.data["has_visible_boundaries"] = cls.has_visible_boundaries()
        cls.data["active_class"] = cls.active_class()
        cls.data["active_material_usage"] = cls.active_material_usage()
        cls.data["is_representation_item_active"] = cls.is_representation_item_active()
        cls.data["active_representation_type"] = cls.active_representation_type()
        cls.data["boundary_class"] = cls.boundary_class()
        cls.data["selected_material_usages"] = cls.selected_material_usages()

    @classmethod
    def default_container(cls) -> str | None:
        props = bpy.context.scene.BIMSpatialDecompositionProperties
        if props.default_container:
            try:
                return tool.Ifc.get().by_id(props.default_container).Name
            except:
                pass

    @classmethod
    def boundary_class(cls):
        declaration = tool.Ifc.schema().declaration_by_name("IfcRelSpaceBoundary")
        declarations = ifcopenshell.util.schema.get_subtypes(declaration)
        names = [d.name() for d in declarations]
        version = tool.Ifc.get_schema()
        return [(c, c, get_entity_doc(version, c).get("description", "")) for c in sorted(names)]

    @classmethod
    def type_thumbnail(cls):
        if not cls.data["relating_type_id"]:
            return 0
        relating_type_id = tool.Blender.get_enum_safe(cls.props, "relating_type_id")
        if relating_type_id is None:
            return 0
        element = tool.Ifc.get().by_id(int(relating_type_id))
        return cls.type_thumbnails.get(element.id(), None) or 0

    @classmethod
    def total_types(cls):
        ifc_class = cls.data["ifc_class_current"]
        return len(tool.Ifc.get().by_type(ifc_class)) if ifc_class else 0

    @classmethod
    def total_pages(cls):
        ifc_class = cls.data["ifc_class_current"]
        total_types = len(tool.Ifc.get().by_type(ifc_class)) if ifc_class else 0
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
        ifc_class = cls.data["ifc_class_current"]
        if not ifc_class:
            return []
        results = []
        elements = natsorted(tool.Ifc.get().by_type(ifc_class), key=lambda e: e.Name or "Unnamed")
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
        if active_object := tool.Blender.get_active_object():
            element = tool.Ifc.get_entity(active_object)
            return element and element.is_a("IfcElement") and not element.is_a("IfcOpeningElement")

    @classmethod
    def has_visible_openings(cls):
        if active_object := tool.Blender.get_active_object():
            element = tool.Ifc.get_entity(active_object)
            if element and element.is_a("IfcElement") and not element.is_a("IfcOpeningElement"):
                for opening in [r.RelatedOpeningElement for r in element.HasOpenings]:
                    if tool.Ifc.get_object(opening):
                        return True
        return False

    @classmethod
    def has_visible_boundaries(cls):
        if active_object := tool.Blender.get_active_object():
            element = tool.Ifc.get_entity(active_object)
            if element:
                if element.is_a("IfcRelSpaceBoundary"):
                    return True
                for boundary in getattr(element, "BoundedBy", []):
                    if tool.Ifc.get_object(boundary):
                        return True
        return False

    @classmethod
    def active_class(cls):
        if active_object := tool.Blender.get_active_object():
            element = tool.Ifc.get_entity(active_object)
            if element:
                return element.is_a()

    @classmethod
    def active_material_usage(cls):
        if active_object := tool.Blender.get_active_object():
            element = tool.Ifc.get_entity(active_object)
            if element:
                return tool.Model.get_usage_type(element)

    @classmethod
    def is_representation_item_active(cls) -> bool:
        object = bpy.context.active_object
        if not object:
            return False
        return tool.Geometry.is_representation_item(object)

    @classmethod
    def active_representation_type(cls):
        if active_object := tool.Blender.get_active_object():
            representation = tool.Geometry.get_active_representation(active_object)
            if representation and representation.is_a("IfcShapeRepresentation"):
                representation = tool.Geometry.resolve_mapped_representation(representation)
                return representation.RepresentationType

    @classmethod
    def ifc_classes(cls):
        if cls.data["ifc_element_type"]:
            if tool.Ifc.get().by_type(cls.data["ifc_element_type"]):
                return [(cls.data["ifc_element_type"], cls.data["ifc_element_type"], "")]
            return []
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
    def ifc_class_current(cls):
        ifc_classes = cls.data["ifc_classes"]
        if not ifc_classes:
            return []
        ifc_class = tool.Blender.get_enum_safe(cls.props, "ifc_class")
        if not ifc_class and ifc_classes:
            ifc_class = ifc_classes[0][0]
        return ifc_class

    @classmethod
    def relating_type_id(cls):
        results = []
        ifc_class = cls.data["ifc_class_current"]
        if ifc_class:
            elements = natsorted(tool.Ifc.get().by_type(ifc_class), key=lambda s: (s.Name or "Unnamed").lower())
            results.extend(elements)
            return [(str(e.id()), e.Name or "Unnamed", e.Description or "") for e in results]
        return []

    @classmethod 
    def relating_type_id_current(cls):
        relating_type_id = tool.Blender.get_enum_safe(cls.props, "relating_type_id")
        relating_type_id_data = cls.data["relating_type_id"]
        if not relating_type_id and relating_type_id_data:
            relating_type_id = relating_type_id_data[0][0]
        return relating_type_id

    @classmethod
    def relating_type_name(cls):
        if relating_type_id := cls.data["relating_type_id_current"]:
            return tool.Ifc.get().by_id(int(relating_type_id)).Name or "Unnamed"

    @classmethod
    def relating_type_description(cls):
        if relating_type_id := cls.data["relating_type_id_current"]:
            return tool.Ifc.get().by_id(int(relating_type_id)).Description or "No description"

    @classmethod
    def predefined_type(cls):
        relating_type_id = tool.Blender.get_enum_safe(cls.props, "relating_type_id")
        if relating_type_id is None:
            return
        relating_type = tool.Ifc.get().by_id(int(relating_type_id))
        if not hasattr(relating_type, "PredefinedType"):
            return
        predefined_type = relating_type.PredefinedType
        return predefined_type

    @classmethod
    def selected_material_usages(cls):
        selected_usages = {}
        for obj in tool.Blender.get_selected_objects():
            element = tool.Ifc.get_entity(obj)
            if not element:
                continue
            usage = tool.Model.get_usage_type(element)
            if not usage:
                representation = tool.Geometry.get_active_representation(obj)
                # besides IfcRepresentation it could be IfcCurveBoundedPlane
                # if IfcRelSpaceBoundary selected
                if representation and getattr(representation, "RepresentationType", None) == "SweptSolid":
                    usage = "SWEPTSOLID"
                else:
                    continue
            selected_usages.setdefault(usage, []).append(obj)
        return selected_usages


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
        cls.data = {}
        cls.data["pset_data"] = cls.pset_data()
        if not cls.data["pset_data"]:
            return
        cls.data["general_params"] = cls.general_params()
        cls.data["calculated_params"] = cls.calculated_params()

    @classmethod
    def pset_data(cls):
        return tool.Model.get_modeling_bbim_pset_data(bpy.context.active_object, "BBIM_Stair")

    @classmethod
    def general_params(cls):
        props = bpy.context.active_object.BIMStairProperties
        data = cls.data["pset_data"]["data_dict"]
        general_params = {}
        general_props = props.get_props_kwargs(stair_type=data["stair_type"])
        for prop_name in general_props:
            prop_readable_name, prop_value = get_prop_from_data(props, data, prop_name)
            general_params[prop_readable_name] = prop_value
        return general_params

    @classmethod
    def calculated_params(cls):
        return tool.Model.get_active_stair_calculated_params(cls.data["pset_data"]["data_dict"])


class SverchokData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.is_loaded = True
        cls.data = {"pset_data": cls.pset_data(), "has_sverchok": cls.has_sverchok()}

    # NOTE: never used
    @classmethod
    def pset_data(cls):
        return tool.Model.get_modeling_bbim_pset_data(bpy.context.active_object, "BBIM_Sverchok")

    @classmethod
    def has_sverchok(cls):
        try:
            import sverchok

            return True
        except:
            return False


def get_prop_from_data(props, data, prop_name):
    prop_value = data.get(prop_name, tool.Blender.get_blender_prop_default_value(props, prop_name))
    prop_value = round(prop_value, 5) if type(prop_value) is float else prop_value
    prop_readable_name = props.bl_rna.properties[prop_name].name
    return prop_readable_name, prop_value


class WindowData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.is_loaded = True
        cls.data = {}
        cls.data["pset_data"] = cls.pset_data()
        if not cls.data["pset_data"]:
            return
        cls.data["general_params"] = cls.general_params()
        cls.data["lining_params"] = cls.lining_params()
        cls.data["panel_params"] = cls.panel_params()

    @classmethod
    def pset_data(cls):
        return tool.Model.get_modeling_bbim_pset_data(bpy.context.active_object, "BBIM_Window")

    @classmethod
    def general_params(cls):
        props = bpy.context.active_object.BIMWindowProperties
        data = cls.data["pset_data"]["data_dict"]
        general_params = {}
        general_props = props.get_general_kwargs()
        for prop_name in general_props:
            prop_readable_name, prop_value = get_prop_from_data(props, data, prop_name)
            general_params[prop_readable_name] = prop_value
        return general_params

    @classmethod
    def lining_params(cls):
        props = bpy.context.active_object.BIMWindowProperties
        data = cls.data["pset_data"]["data_dict"]
        lining_data = data["lining_properties"]
        lining_params = {}
        lining_props = props.get_lining_kwargs(window_type=data["window_type"])
        for prop_name in lining_props:
            prop_readable_name, prop_value = get_prop_from_data(props, lining_data, prop_name)
            lining_params[prop_readable_name] = prop_value
        return lining_params

    @classmethod
    def panel_params(cls):
        props = bpy.context.active_object.BIMWindowProperties
        panel_data = cls.data["pset_data"]["data_dict"]["panel_properties"]
        panel_params = {}
        panel_props = props.get_panel_kwargs()
        for prop_name in panel_props:
            prop_readable_name, prop_value = get_prop_from_data(props, panel_data, prop_name)
            panel_params[prop_readable_name] = prop_value
        return panel_params


class DoorData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.is_loaded = True
        cls.data = {}
        cls.data["pset_data"] = cls.pset_data()
        if not cls.data["pset_data"]:
            return
        cls.data["general_params"] = cls.general_params()
        cls.data["lining_params"] = cls.lining_params()
        cls.data["panel_params"] = cls.panel_params()

    @classmethod
    def pset_data(cls):
        return tool.Model.get_modeling_bbim_pset_data(bpy.context.active_object, "BBIM_Door")

    @classmethod
    def general_params(cls):
        props = bpy.context.active_object.BIMDoorProperties
        data = cls.data["pset_data"]["data_dict"]
        general_params = {}
        general_props = props.get_general_kwargs()
        for prop_name in general_props:
            prop_readable_name, prop_value = get_prop_from_data(props, data, prop_name)
            general_params[prop_readable_name] = prop_value
        return general_params

    @classmethod
    def lining_params(cls):
        props = bpy.context.active_object.BIMDoorProperties
        data = cls.data["pset_data"]["data_dict"]
        lining_data = data["lining_properties"]
        lining_params = {}
        lining_props = props.get_lining_kwargs(door_type=data["door_type"], lining_data=lining_data)
        for prop_name in lining_props:
            prop_readable_name, prop_value = get_prop_from_data(props, lining_data, prop_name)
            lining_params[prop_readable_name] = prop_value
        return lining_params

    @classmethod
    def panel_params(cls):
        props = bpy.context.active_object.BIMDoorProperties
        data = cls.data["pset_data"]["data_dict"]
        panel_data = cls.data["pset_data"]["data_dict"]["panel_properties"]
        panel_params = {}
        panel_props = props.get_panel_kwargs(lining_data=data["lining_properties"])
        for prop_name in panel_props:
            prop_readable_name, prop_value = get_prop_from_data(props, panel_data, prop_name)
            panel_params[prop_readable_name] = prop_value
        return panel_params


class RailingData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.is_loaded = True
        cls.data = {}
        cls.data["pset_data"] = cls.pset_data()
        if not cls.data["pset_data"]:
            return
        cls.data["general_params"] = cls.general_params()
        cls.data["path_data"] = cls.path_data()

    @classmethod
    def pset_data(cls):
        return tool.Model.get_modeling_bbim_pset_data(bpy.context.active_object, "BBIM_Railing")

    @classmethod
    def general_params(cls):
        props = bpy.context.active_object.BIMRailingProperties
        data = cls.data["pset_data"]["data_dict"]
        general_params = {}
        general_props = props.get_general_kwargs(railing_type=data["railing_type"])
        for prop_name in general_props:
            prop_readable_name, prop_value = get_prop_from_data(props, data, prop_name)
            general_params[prop_readable_name] = prop_value
        return general_params

    @classmethod
    def path_data(cls):
        return cls.data["pset_data"]["data_dict"]["path_data"]


class RoofData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.is_loaded = True
        cls.data = {}
        cls.data["pset_data"] = cls.pset_data()
        if not cls.data["pset_data"]:
            return
        cls.data["general_params"] = cls.general_params()

    @classmethod
    def pset_data(cls):
        return tool.Model.get_modeling_bbim_pset_data(bpy.context.active_object, "BBIM_Roof")

    @classmethod
    def general_params(cls):
        props = bpy.context.active_object.BIMRoofProperties
        data = cls.data["pset_data"]["data_dict"]
        general_params = {}
        general_props = props.get_general_kwargs(generation_method=data["generation_method"])
        for prop_name in general_props:
            prop_readable_name, prop_value = get_prop_from_data(props, data, prop_name)

            if prop_name in ("angle", "rafter_edge_angle"):
                prop_value = round(degrees(prop_value), 2)

            general_params[prop_readable_name] = prop_value
        return general_params


class ItemData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.is_loaded = True
        cls.data = {}
        cls.data["representation_identifier"] = cls.representation_identifier()
        cls.data["representation_type"] = cls.representation_type()

    @classmethod
    def representation_identifier(cls):
        props = bpy.context.scene.BIMGeometryProperties
        rep = tool.Geometry.get_active_representation(props.representation_obj)
        return rep.RepresentationIdentifier

    @classmethod
    def representation_type(cls):
        props = bpy.context.scene.BIMGeometryProperties
        rep = tool.Geometry.get_active_representation(props.representation_obj)
        return rep.RepresentationType
