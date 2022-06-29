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
import blenderbim.tool as tool
from blenderbim.bim.ifc import IfcStore


preview_icon_ids = {}


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
        cls.load_ifc_classes()
        cls.load_relating_types()
        cls.load_preview_ifc_types()

    @classmethod
    def load_ifc_classes(cls):
        cls.data["ifc_classes"] = cls.ifc_classes()

    @classmethod
    def load_relating_types(cls):
        cls.data["relating_types"] = cls.relating_types()

    @classmethod
    def load_preview_ifc_types(cls):
        cls.data["preview_ifc_types"] = preview_icon_ids

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
    def ifc_class_entities(cls, ifc_class=None):
        ifc_classes = cls.data["ifc_classes"]
        if not ifc_classes:
            return []
        results = []
        if ifc_class is None:
            ifc_class = bpy.context.scene.BIMModelProperties.ifc_class
        if not ifc_class and ifc_classes:
            ifc_class = ifc_classes[0][0]
        if ifc_class:
            elements = sorted(tool.Ifc.get().by_type(ifc_class), key=lambda s: s.Name)
            results.extend(elements)
            return results
        return []

    @classmethod
    def relating_types(cls, ifc_class=None):
        return [(str(e.id()), e.Name, e.Description or "") for e in cls.ifc_class_entities(ifc_class=ifc_class)]

    @classmethod
    def assetize_relating_type_from_selection(cls):
        props = bpy.context.scene.BIMModelProperties
        ifc_class = props.ifc_class
        relating_type_id = props.relating_type
        ifc_class_occurrences = cls.ifc_class_entities(ifc_class=ifc_class)
        ifc_class_occurrences = [entity for entity in ifc_class_occurrences if entity.id() == int(relating_type_id)]
        if len(ifc_class_occurrences) == 0:
            return
        ifc_class_entity = ifc_class_occurrences[0]
        obj = tool.Ifc.get_object(ifc_class_entity)
        relating_type = ifc_class_entity.Name
        to_be_deleted = False
        if obj.type == 'EMPTY':
            bpy.ops.bim.add_type_instance()
            new_obj = bpy.context.selected_objects[-1]
            if new_obj is not None:
                to_be_deleted = True
                obj = new_obj
        obj.asset_mark()
        obj.asset_generate_preview()
        icon_id = obj.preview.icon_id
        if ifc_class not in cls.data["preview_ifc_types"]:
            cls.data["preview_ifc_types"][ifc_class] = {}
        cls.data["preview_ifc_types"][ifc_class][relating_type] = {"icon_id": icon_id, "object": obj}
        if to_be_deleted:
            for col in obj.users_collection:
                col.objects.unlink(obj)

    @staticmethod
    def ifc_type_info(ifc_class):
        ifc_type_infos = [element for element in bpy.context.scene.IfcTypeInfo if element.ifc_class == ifc_class]
        return None if len(ifc_type_infos) == 0 else ifc_type_infos[0]

    @classmethod
    def new_ifc_type_instance(cls, ifc_class, relating_type_id):
        props = bpy.context.scene.BIMModelProperties
        props.ifc_class = ifc_class
        props.relating_type = str(relating_type_id)
        bpy.ops.bim.add_type_instance()

    @staticmethod
    def relating_type_name_by_id(ifc_class, relating_type_id):
        file = IfcStore.get_file()
        try:
            ifc_class_entity = file.by_id(int(relating_type_id))
        except (RuntimeError, ValueError):
            return None
        return ifc_class_entity.Name if ifc_class_entity.is_a() == ifc_class else None
