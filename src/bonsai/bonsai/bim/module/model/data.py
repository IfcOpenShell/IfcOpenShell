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
from typing import Union, Optional, Any


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
    type_thumbnails: dict[int, int] = {}
    types_per_page = 9
    is_loaded = False

    @classmethod
    def load(cls, ifc_element_type: Optional[str] = None):
        cls.is_loaded = True
        cls.props = tool.Model.get_model_props()
        cls.data["default_container"] = cls.default_container()
        cls.data["ifc_element_type"] = ifc_element_type
        cls.data["ifc_classes"] = cls.ifc_classes()
        cls.data["ifc_class_current"] = cls.ifc_class_current()
        # Make sure .ifc_classes() was run before next lines
        cls.data["type_elements"] = cls.type_elements()
        cls.data["type_elements_filtered"] = cls.type_elements_filtered()
        # After .type_elements().
        cls.data["relating_type_id"] = cls.relating_type_id()
        # Make sure .relating_type_id() was run before next lines
        cls.data["relating_type_data"] = cls.relating_type_data()
        # Make sure .type_elements_filtered() was run before next lines
        cls.data["total_types"] = cls.total_types()
        cls.data["total_pages"] = cls.total_pages()  # Only after .total_types()
        cls.data["next_page"] = cls.next_page()
        cls.data["prev_page"] = cls.prev_page()
        cls.data["paginated_relating_types"] = cls.paginated_relating_types()

        cls.data["materials"] = cls.materials()
        cls.data["is_voidable_element"] = cls.is_voidable_element()
        cls.data["has_visible_openings"] = cls.has_visible_openings()
        cls.data["has_visible_boundaries"] = cls.has_visible_boundaries()
        cls.data["active_class"] = cls.active_class()
        cls.data["active_material_usage"] = cls.active_material_usage()
        cls.data["has_extrusion"] = cls.has_extrusion()
        cls.data["is_representation_item_active"] = cls.is_representation_item_active()
        # After is_representation_item_active.
        cls.data["is_representation_item_swept_solid"] = cls.is_representation_item_swept_solid()

        cls.data["active_representation_type"] = cls.active_representation_type()
        cls.data["boundary_class"] = cls.boundary_class()
        cls.data["selected_material_usages"] = cls.selected_material_usages()

        # Only after .active_material_usage() and .active_class()
        cls.data["is_flippable_element"] = cls.is_flippable_element()
        cls.data["is_regenable_element"] = cls.is_regenable_element()

    @classmethod
    def default_container(cls) -> str | None:
        props = tool.Spatial.get_spatial_props()
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
    def materials(cls):
        results = [("0", "None", "No material")]
        results.extend([(str(m.id()), m.Name or "Unnamed", "") for m in tool.Ifc.get().by_type("IfcMaterial")])
        return results

    @classmethod
    def total_types(cls):
        return len(cls.data["type_elements_filtered"])

    @classmethod
    def total_pages(cls):
        total_types = cls.data["total_types"]
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
    def type_elements(cls):
        ifc_class = cls.data["ifc_class_current"]
        if not ifc_class:
            return []
        elements = list(tool.Ifc.get().by_type(ifc_class))
        return natsorted(elements, key=lambda s: (s.Name or "Unnamed").lower())

    @classmethod
    def type_elements_filtered(cls):
        search_query = cls.props.search_name.lower()

        def filter_element(element: ifcopenshell.entity_instance) -> bool:
            if search_query in (element.Name or "Unnamed").lower():
                return True
            if search_query in (element.Description or "").lower():
                return True
            if search_query in (ifcopenshell.util.element.get_predefined_type(element) or "").lower():
                return True
            return False

        elements = cls.data["type_elements"]
        if cls.props.search_name:
            return [e for e in elements if filter_element(e)]
        return elements

    @classmethod
    def paginated_relating_types(cls):
        results = []
        elements = cls.data["type_elements_filtered"]
        elements = elements[(cls.props.type_page - 1) * cls.types_per_page : cls.props.type_page * cls.types_per_page]
        for element in elements:
            results.append(cls.get_type_data(element))
        return results

    @classmethod
    def get_type_data(cls, element: ifcopenshell.entity_instance) -> dict[str, Any]:
        predefined_type = ifcopenshell.util.element.get_predefined_type(element)
        if predefined_type == "NOTDEFINED":
            predefined_type = None
        data = {
            "id": element.id(),
            "ifc_class": element.is_a(),
            "name": element.Name or "Unnamed",
            "description": element.Description or "No Description",
            "predefined_type": predefined_type,
            "icon_id": cls.type_thumbnails.get(element.id(), 0),
        }
        return data

    @classmethod
    def is_voidable_element(cls):
        if active_object := tool.Blender.get_active_object():
            element = tool.Ifc.get_entity(active_object)
            return element and element.is_a("IfcElement") and not element.is_a("IfcOpeningElement")

    @classmethod
    def is_flippable_element(cls):
        return cls.data["active_material_usage"] in ("LAYER2", "PROFILE") or cls.data["active_class"] in (
            "IfcWindow",
            "IfcWindowStandardCase",
            "IfcDoor",
            "IfcDoorStandardCase",
        )

    @classmethod
    def is_regenable_element(cls):
        if cls.data["active_material_usage"] in ("LAYER2", "PROFILE") and cls.data["active_class"] not in (
            "IfcCableCarrierSegment",
            "IfcCableSegment",
            "IfcDuctSegment",
            "IfcPipeSegment",
        ):
            return True
        if cls.data["active_class"] in ("IfcWindow", "IfcWindowStandardCase", "IfcDoor", "IfcDoorStandardCase"):
            return True
        return False

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
        if (obj := tool.Blender.get_active_object()) and (element := tool.Ifc.get_entity(obj)):
            return element.is_a()

    @classmethod
    def active_material_usage(cls):
        if (obj := tool.Blender.get_active_object()) and (element := tool.Ifc.get_entity(obj)):
            return tool.Model.get_usage_type(element)

    @classmethod
    def has_extrusion(cls) -> bool:
        if not (obj := tool.Blender.get_active_object()) or not (
            representation := tool.Geometry.get_active_representation(obj)
        ):
            return False

        # Skip representation items.
        if not representation.is_a("IfcShapeRepresentation"):
            return False

        return bool(tool.Model.get_extrusion(representation))

    @classmethod
    def is_representation_item_active(cls) -> bool:
        if not (obj := tool.Blender.get_active_object()):
            return False
        return tool.Geometry.is_representation_item(obj)

    @classmethod
    def is_representation_item_swept_solid(cls) -> bool:
        if not cls.data["is_representation_item_active"]:
            return False
        assert (obj := bpy.context.active_object) and (item := tool.Geometry.get_representation_item(obj))
        return item.is_a("IfcSweptAreaSolid")

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
        elements = cls.data["type_elements"]
        return [(str(e.id()), e.Name or "Unnamed", e.Description or "") for e in elements]

    @classmethod
    def relating_type_data(cls) -> dict[str, Any]:
        relating_type_id = tool.Blender.get_enum_safe(cls.props, "relating_type_id")
        relating_type_id_data = cls.data["relating_type_id"]
        if relating_type_id is None:
            if not relating_type_id_data:
                return {}
            relating_type_id = relating_type_id_data[0][0]
        ifc_file = tool.Ifc.get()
        relating_type = ifc_file.by_id(int(relating_type_id))
        return cls.get_type_data(relating_type)

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
        obj = bpy.context.active_object
        assert obj
        props = tool.Model.get_stair_props(obj)
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
        obj = bpy.context.active_object
        assert obj
        props = tool.Model.get_window_props(obj)
        data = cls.data["pset_data"]["data_dict"]
        general_params = {}
        general_props = props.get_general_kwargs()
        for prop_name in general_props:
            prop_readable_name, prop_value = get_prop_from_data(props, data, prop_name)
            general_params[prop_readable_name] = prop_value
        return general_params

    @classmethod
    def lining_params(cls):
        obj = bpy.context.active_object
        assert obj
        props = tool.Model.get_window_props(obj)
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
        obj = bpy.context.active_object
        assert obj
        props = tool.Model.get_window_props(obj)
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
        obj = bpy.context.active_object
        assert obj
        props = tool.Model.get_door_props(obj)
        data = cls.data["pset_data"]["data_dict"]
        general_params = {}
        general_props = props.get_general_kwargs()
        for prop_name in general_props:
            prop_readable_name, prop_value = get_prop_from_data(props, data, prop_name)
            general_params[prop_readable_name] = prop_value
        return general_params

    @classmethod
    def lining_params(cls):
        obj = bpy.context.active_object
        assert obj
        props = tool.Model.get_door_props(obj)
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
        obj = bpy.context.active_object
        assert obj
        props = tool.Model.get_door_props(obj)
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
        obj = bpy.context.active_object
        assert obj
        props = tool.Model.get_railing_props(obj)
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
        cls.data["path_data"] = cls.path_data()

    @classmethod
    def pset_data(cls):
        return tool.Model.get_modeling_bbim_pset_data(bpy.context.active_object, "BBIM_Roof")

    @classmethod
    def general_params(cls):
        obj = bpy.context.active_object
        assert obj
        props = tool.Model.get_roof_props(obj)
        data = cls.data["pset_data"]["data_dict"]
        general_params = {}
        general_props = props.get_general_kwargs(generation_method=data["generation_method"])
        for prop_name in general_props:
            prop_readable_name, prop_value = get_prop_from_data(props, data, prop_name)

            if prop_name in ("angle", "rafter_edge_angle"):
                prop_value = round(degrees(prop_value), 2)

            general_params[prop_readable_name] = prop_value
        return general_params

    @classmethod
    def path_data(cls):
        return cls.data["pset_data"]["data_dict"]["path_data"]


class ItemData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.is_loaded = True
        cls.data = {}
        cls.data["representation_identifier"] = cls.representation_identifier()
        cls.data["representation_type"] = cls.representation_type()
        cls.data["representation_usage"] = cls.representation_usage()
        cls.data["profiles_enum"] = cls.profiles_enum()

    @classmethod
    def representation_identifier(cls):
        props = tool.Geometry.get_geometry_props()
        rep = tool.Geometry.get_active_representation(props.representation_obj)
        return rep.RepresentationIdentifier

    @classmethod
    def representation_type(cls):
        props = tool.Geometry.get_geometry_props()
        rep = tool.Geometry.get_active_representation(props.representation_obj)
        return rep.RepresentationType

    @classmethod
    def representation_usage(cls):
        props = tool.Geometry.get_geometry_props()
        return tool.Model.get_usage_type(tool.Ifc.get_entity(props.representation_obj))

    @classmethod
    def profiles_enum(cls) -> list[Union[tuple[str, str, str], None]]:
        ifc_file = tool.Ifc.get()
        profiles: list[Union[tuple[str, str, str], None]] = []
        profiles.append(
            (
                "-",
                "Use Unnamed Profile",
                "If named profile is currently used, replace it with the unnamed version so it can be edited without affecting original profile.",
            )
        )
        profiles.append(None)

        named_profiles: list[tuple[str, str, str]] = []
        for profile in ifc_file.by_type("IfcProfileDef"):
            if (profile_name := profile.ProfileName) is None:
                continue
            named_profiles.append((str(profile.id()), profile_name, profile.is_a()))
        named_profiles.sort(key=lambda x: x[1])
        profiles.extend(named_profiles)
        return profiles
