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
        cls.load_constr_classes()
        cls.load_constr_types()
        cls.load_constr_types_browser()
        cls.load_preview_constr_types()

    @classmethod
    def load_constr_classes(cls):
        cls.data["constr_classes"] = cls.constr_classes()

    @classmethod
    def load_constr_types(cls):
        cls.data["constr_types_ids"] = cls.constr_types()

    @classmethod
    def load_constr_types_browser(cls):
        cls.data["constr_types_ids_browser"] = cls.constr_types_browser()

    @classmethod
    def load_preview_constr_types(cls):
        cls.data["preview_constr_types"] = preview_icon_ids

    @classmethod
    def constr_classes(cls):
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
    def constr_class_entities(cls, constr_class=None):
        constr_classes = cls.data["constr_classes"]
        if not constr_classes:
            return []
        results = []
        if constr_class is None:
            constr_class = cls.props.constr_class
        if not constr_class and constr_classes:
            constr_class = constr_classes[0][0]
        if constr_class:
            elements = sorted(tool.Ifc.get().by_type(constr_class), key=lambda s: s.Name)
            results.extend(elements)
            return results
        return []

    @classmethod
    def constr_types(cls, constr_class=None):
        return [
            (str(e.id()), e.Name, e.Description or "") for e in cls.constr_class_entities(constr_class=constr_class)
        ]

    @classmethod
    def constr_types_browser(cls):
        return cls.constr_types(constr_class=cls.props.constr_class_browser)

    @staticmethod
    def new_constr_type_info(constr_class):
        constr_type_info = bpy.context.scene.ConstrTypeInfo.add()
        constr_type_info.name = constr_class
        return constr_type_info

    @classmethod
    def assetize_constr_class(cls, constr_class=None):
        if constr_class is None:
            constr_class = cls.props.constr_class
        constr_type_info = cls.constr_type_info(constr_class)
        _ = cls.new_constr_type_info(constr_class) if constr_type_info is None else constr_type_info
        constr_class_occurrences = cls.constr_class_entities(constr_class)
        preview_constr_types = cls.data["preview_constr_types"]
        for constr_class_entity in constr_class_occurrences:

            ### handle asset regeneration when library entity is updated ¿?
            if (constr_class not in preview_constr_types
                    or str(constr_class_entity.id()) not in preview_constr_types[constr_class]):
                obj = tool.Ifc.get_object(constr_class_entity)
                cls.assetize_object(obj, constr_class, constr_class_entity)
        constr_type_info = cls.constr_type_info(constr_class)
        constr_type_info.fully_loaded = True

    @classmethod
    def assetize_object(cls, obj, constr_class, constr_class_entity, from_selection=False):
        constr_type_id = constr_class_entity.id()
        to_be_deleted = False
        if obj.type == 'EMPTY':
            kwargs = {}
            if not from_selection:
                kwargs.update({'constr_class': constr_class, 'constr_type_id': constr_type_id})
            new_obj = cls.new_constr_type(**kwargs)
            if new_obj is not None:
                to_be_deleted = True
                obj = new_obj
        obj.asset_mark()
        obj.asset_generate_preview()
        icon_id = obj.preview.icon_id
        if constr_class not in cls.data["preview_constr_types"]:
            cls.data["preview_constr_types"][constr_class] = {}
        cls.data["preview_constr_types"][constr_class][str(constr_type_id)] = {"icon_id": icon_id, "object": obj}
        if to_be_deleted:
            for col in obj.users_collection:
                col.objects.unlink(obj)

    @classmethod
    def assetize_constr_type_from_selection(cls):
        constr_class_browser = cls.props.constr_class_browser
        constr_type_id_browser = cls.props.constr_type_id_browser
        constr_class_occurrences = cls.constr_class_entities(constr_class=constr_class_browser)
        constr_class_occurrences = [
            entity for entity in constr_class_occurrences if entity.id() == int(constr_type_id_browser)
        ]
        if len(constr_class_occurrences) == 0:
            return False
        constr_class_entity = constr_class_occurrences[0]
        obj = tool.Ifc.get_object(constr_class_entity)
        if obj is None:
            return False
        cls.assetize_object(obj, constr_class_browser, constr_class_entity, from_selection=True)
        return True

    @staticmethod
    def constr_type_info(constr_class):
        constr_type_infos = [element for element in bpy.context.scene.ConstrTypeInfo if element.name == constr_class]
        return None if len(constr_type_infos) == 0 else constr_type_infos[0]

    @classmethod
    def new_constr_type(cls, constr_class=None, constr_type_id=None):
        if constr_class is None:
            bpy.ops.bim.add_constr_type(
                constr_class=cls.props.constr_class_browser, constr_type_id=int(cls.props.constr_type_id_browser)
            )
        else:
            cls.props.constr_class = constr_class
            cls.props.constr_type_id = str(constr_type_id)
            bpy.ops.bim.add_constr_type()
        return bpy.context.selected_objects[-1]

    @staticmethod
    def constr_type_name_by_id(constr_class, constr_type_id):
        file = IfcStore.get_file()
        try:
            constr_class_entity = file.by_id(int(constr_type_id))
        except (RuntimeError, ValueError):
            return None
        return constr_class_entity.Name if constr_class_entity.is_a() == constr_class else None

    @classmethod
    def constr_type_id_by_name(cls, constr_class, constr_type):
        constr_types = [ct[0] for ct in cls.constr_types(constr_class=constr_class) if ct[1] == constr_type]
        return None if len(constr_types) == 0 else constr_types[0]

    @classmethod
    def consolidate_constr_type(cls):
        cls.props.constr_class = cls.props.constr_class_browser
        cls.props.constr_type_id = cls.props.constr_type_id_browser

    @classmethod
    def setup_constr_type_browser(cls):
        cls.props.constr_class_browser = cls.props.constr_class
        cls.props.constr_type_id_browser = cls.props.constr_type_id
