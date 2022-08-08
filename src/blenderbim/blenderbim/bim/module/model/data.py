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

import functools
import bpy
import blenderbim.tool as tool
from blenderbim.bim.ifc import IfcStore


preview_icon_ids = {}
attempts = 0


def refresh():
    AuthoringData.is_loaded = False


class AuthoringData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.is_loaded = True
        if not hasattr(cls, "data"):
            cls.data = {}
        cls.props = bpy.context.scene.BIMModelProperties
        cls.load_ifc_classes()
        cls.load_relating_types()
        cls.load_relating_types_browser()
        cls.load_preview_constr_types()

    @classmethod
    def load_ifc_classes(cls):
        cls.data["ifc_classes"] = cls.ifc_classes()

    @classmethod
    def load_relating_types(cls):
        cls.data["relating_types_ids"] = cls.relating_types()

    @classmethod
    def load_relating_types_browser(cls):
        cls.data["relating_types_browser_ids"] = cls.relating_types_browser()

    @classmethod
    def load_preview_constr_types(cls):
        cls.data["preview_constr_types"] = preview_icon_ids

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
            elements = sorted(tool.Ifc.get().by_type(ifc_class), key=lambda s: s.Name)
            results.extend(elements)
            return results
        return []

    @classmethod
    def relating_types(cls, ifc_class=None):
        return [(str(e.id()), e.Name, e.Description or "") for e in cls.constr_class_entities(ifc_class=ifc_class)]

    @classmethod
    def relating_types_browser(cls):
        return cls.relating_types(ifc_class=cls.props.ifc_class_browser)

    @staticmethod
    def new_relating_type_info(ifc_class):
        relating_type_info = bpy.context.scene.ConstrTypeInfo.add()
        relating_type_info.name = ifc_class
        return relating_type_info

    @classmethod
    def assetize_constr_class(cls, ifc_class=None):
        if ifc_class is None:
            ifc_class = cls.props.ifc_class
        relating_type_info = cls.relating_type_info(ifc_class)
        _ = cls.new_relating_type_info(ifc_class) if relating_type_info is None else relating_type_info
        constr_class_occurrences = cls.constr_class_entities(ifc_class)
        preview_constr_types = cls.data["preview_constr_types"]
        for constr_class_entity in constr_class_occurrences:

            ### handle asset regeneration when library entity is updated ¿?
            if (
                ifc_class not in preview_constr_types
                or str(constr_class_entity.id()) not in preview_constr_types[ifc_class]
            ):
                obj = tool.Ifc.get_object(constr_class_entity)
                cls.assetize_object(obj, ifc_class, constr_class_entity)
        relating_type_info = cls.relating_type_info(ifc_class)
        relating_type_info.fully_loaded = True

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
        obj.asset_mark()
        obj.asset_generate_preview()
        icon_id = obj.preview.icon_id
        if ifc_class not in cls.data["preview_constr_types"]:
            cls.data["preview_constr_types"][ifc_class] = {}
        cls.data["preview_constr_types"][ifc_class][str(relating_type_id)] = {"icon_id": icon_id, "object": obj}
        if to_be_deleted:
            for col in obj.users_collection:
                col.objects.unlink(obj)

    @classmethod
    def assetize_relating_type_from_selection(cls, browser=False):
        ifc_class = cls.props.ifc_class_browser if browser else cls.props.ifc_class
        relating_type_id = cls.props.relating_type_id_browser if browser else cls.props.relating_type_id
        constr_class_occurrences = cls.constr_class_entities(ifc_class=ifc_class)
        constr_class_occurrences = [
            entity for entity in constr_class_occurrences if entity.id() == int(relating_type_id)
        ]
        if len(constr_class_occurrences) == 0:
            return False
        constr_class_entity = constr_class_occurrences[0]
        obj = tool.Ifc.get_object(constr_class_entity)
        if obj is None:
            return False
        cls.assetize_object(obj, ifc_class, constr_class_entity, from_selection=True)
        return True

    @staticmethod
    def relating_type_info(ifc_class):
        relating_type_infos = [element for element in bpy.context.scene.ConstrTypeInfo if element.name == ifc_class]
        return None if len(relating_type_infos) == 0 else relating_type_infos[0]

    @classmethod
    def new_relating_type(cls, ifc_class=None, relating_type_id=None):
        if ifc_class is None:
            bpy.ops.bim.add_constr_type_instance(
                ifc_class=cls.props.ifc_class, relating_type_id=int(cls.props.relating_type_id)
            )
        else:
            cls.props.updating = True
            cls.props.ifc_class = ifc_class
            cls.props.relating_type_id = str(relating_type_id)
            cls.props.updating = False
            bpy.ops.bim.add_constr_type_instance()
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
