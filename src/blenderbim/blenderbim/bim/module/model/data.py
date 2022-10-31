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
from blenderbim.bim.ifc import IfcStore
from blenderbim.bim.module.model.root import ConstrTypeEntityNotFound

def refresh():
    AuthoringData.is_loaded = False
    ArrayData.is_loaded = False


class AuthoringData:
    data = {}
    type_thumbnails = {}
    types_per_page = 9
    is_loaded = False

    @classmethod
    def load(cls):
        cls.is_loaded = True
        cls.props = bpy.context.scene.BIMModelProperties
        cls.load_ifc_classes()
        cls.load_relating_types()
        cls.load_relating_types_browser()
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

    @classmethod
    def type_class(cls):
        declaration = tool.Ifc.schema().declaration_by_name("IfcElementType")
        declarations = ifcopenshell.util.schema.get_subtypes(declaration)
        names = [d.name() for d in declarations]
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
        if not cls.props.relating_type_id:
            return 0
        element = tool.Ifc.get().by_id(int(cls.props.relating_type_id))
        return cls.type_thumbnails.get(element.id(), None) or 0

    @classmethod
    def load_ifc_classes(cls):
        cls.data["ifc_classes"] = cls.ifc_classes()

    @classmethod
    def load_relating_types(cls):
        cls.data["relating_types_ids"] = cls.relating_types()

    @classmethod
    def load_relating_types_browser(cls):
        cls.data["relating_types_ids_browser"] = cls.relating_types_browser()

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
    def ifc_classes(cls):
        results = []
        classes = {
            e.is_a()
            for e in tool.Ifc.get().by_type("IfcElementType")
            + tool.Ifc.get().by_type("IfcDoorStyle")
            + tool.Ifc.get().by_type("IfcWindowStyle")
        }
        results.extend([(c, c, "") for c in sorted(classes)])
        return results

    @classmethod
    def constr_class_entities(cls, ifc_class=None):
        ifc_classes = cls.data["ifc_classes"]
        if not ifc_classes:
            return []
        results = []
        if ifc_class is None:
            ifc_class = cls.props.ifc_class
        if not ifc_class and ifc_classes:
            ifc_class = ifc_classes[0][0]
        if ifc_class:
            elements = sorted(tool.Ifc.get().by_type(ifc_class), key=lambda s: s.Name or "Unnamed")
            results.extend(elements)
            return results
        return []

    @classmethod
    def relating_types(cls, ifc_class=None):
        return [
            (str(e.id()), e.Name or "Unnamed", e.Description or "")
            for e in cls.constr_class_entities(ifc_class=ifc_class)
        ]

    @classmethod
    def relating_types_browser(cls):
        return cls.relating_types(ifc_class=cls.props.ifc_class_browser)

    @classmethod
    def new_constr_class_info(cls, ifc_class):
        if ifc_class not in cls.props.constr_classes:
            cls.props.constr_classes.add().name = ifc_class
        return cls.props.constr_classes[ifc_class]

    @classmethod
    def assetize_constr_class(cls, ifc_class=None):
        selected_ifc_class = cls.props.ifc_class
        selected_relating_type_id = cls.props.relating_type_id
        if ifc_class is None:
            ifc_class = cls.props.ifc_class_browser
        if cls.constr_class_info(ifc_class) is None:
            cls.new_constr_class_info(ifc_class)
        constr_class_occurrences = cls.constr_class_entities(ifc_class)
        constr_classes = cls.props.constr_classes

        for constr_class_entity in constr_class_occurrences:
            if (
                ifc_class not in constr_classes
                or constr_class_entity.Name not in constr_classes[ifc_class].constr_types
            ):
                obj = tool.Ifc.get_object(constr_class_entity)
                cls.assetize_object(obj, ifc_class, constr_class_entity)
        cls.constr_class_info(ifc_class).fully_loaded = True
        cls.props.updating = True
        cls.props.ifc_class = selected_ifc_class
        cls.props.relating_type_id = selected_relating_type_id
        cls.props.updating = False

    @classmethod
    def assetize_object(cls, obj, ifc_class, ifc_class_entity, from_selection=False):
        relating_type_id = ifc_class_entity.id()
        to_be_deleted = False
        if obj.type == "EMPTY":
            kwargs = {}
            if not from_selection:
                kwargs.update({"ifc_class": ifc_class, "relating_type_id": relating_type_id})
            new_obj = cls.new_relating_type(**kwargs)
            if new_obj is not None:
                to_be_deleted = True
                obj = new_obj
                obj.hide_set(True)
        obj.asset_mark()
        obj.asset_generate_preview()
        blender33_or_above = bpy.app.version >= (3, 3, 0)
        interval = 1e-4

        def wait_for_asset_previews_generation(check_interval_seconds=interval):
            if blender33_or_above and bpy.app.is_job_running("RENDER_PREVIEW"):
                return check_interval_seconds
            else:
                if ifc_class not in cls.props.constr_classes:
                    cls.props.constr_classes.add().name = ifc_class
                constr_class_info = cls.props.constr_classes[ifc_class]
                # relating_type = cls.relating_type_name_by_id(ifc_class, relating_type_id)
                if str(relating_type_id) not in constr_class_info.constr_types:
                    constr_class_info.constr_types.add().name = str(relating_type_id)
                relating_type_info = constr_class_info.constr_types[str(relating_type_id)]
                relating_type_info.object = obj
                relating_type_info.icon_id = obj.preview.icon_id

                if to_be_deleted:
                    element = tool.Ifc.get_entity(obj)
                    if element:
                        tool.Ifc.delete(element)
                    tool.Ifc.unlink(obj=obj)
                    for collection in obj.users_collection:
                        collection.objects.unlink(obj)
                return None

        first_interval = 0 if blender33_or_above else interval
        bpy.app.timers.register(wait_for_asset_previews_generation, first_interval=first_interval)

    @classmethod
    def assetize_relating_type_from_selection(cls, browser=False):
        ifc_class = cls.props.ifc_class_browser if browser else cls.props.ifc_class
        relating_type_id = cls.props.relating_type_id_browser if browser else cls.props.relating_type_id
        constr_class_occurrences = cls.constr_class_entities(ifc_class=ifc_class)
        constr_class_occurrences = [
            entity for entity in constr_class_occurrences if entity.id() == int(relating_type_id)
        ]
        if len(constr_class_occurrences) == 0:
            raise ConstrTypeEntityNotFound()
        constr_class_entity = constr_class_occurrences[0]
        if (obj := tool.Ifc.get_object(constr_class_entity)) is None:
            raise ConstrTypeEntityNotFound()
        cls.assetize_object(obj, ifc_class, constr_class_entity, from_selection=True)

    @staticmethod
    def constr_class_info(ifc_class):
        props = bpy.context.scene.BIMModelProperties
        return props.constr_classes[ifc_class] if ifc_class in props.constr_classes else None

    @classmethod
    def new_relating_type(cls, ifc_class=None, relating_type_id=None):
        if ifc_class is None:
            bpy.ops.bim.add_constr_type_instance(
                ifc_class=cls.props.ifc_class, relating_type_id=int(cls.props.relating_type_id), link_to_scene=True
            )
        else:
            cls.props.updating = True
            cls.props.ifc_class = ifc_class
            cls.props.relating_type_id = str(relating_type_id)
            cls.props.updating = False
            bpy.ops.bim.add_constr_type_instance(link_to_scene=True)
        return bpy.context.selected_objects[-1]

    @staticmethod
    def relating_type_name_by_id(ifc_class, relating_type_id):
        file = IfcStore.get_file()
        try:
            constr_class_entity = file.by_id(int(relating_type_id))
        except (RuntimeError, ValueError):
            return None
        return constr_class_entity.Name if constr_class_entity.is_a() == ifc_class else None

    @classmethod
    def relating_type_id_by_name(cls, ifc_class, relating_type):
        relating_types = [ct[0] for ct in cls.relating_types(ifc_class=ifc_class) if ct[1] == relating_type]
        return None if len(relating_types) == 0 else relating_types[0]


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
                    parameters["data"] = json.loads(parameters.get("Data", "[]") or "[]")
                except:
                    parameters["has_parent"] = False
                return parameters
