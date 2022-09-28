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
from blenderbim.bim.module.model.root import ConstrTypeEntityNotFound


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
        obj.asset_mark()
        obj.asset_generate_preview()

        def wait_for_asset_previews_generation(check_interval_seconds=0.001):
            if bpy.app.is_job_running("RENDER_PREVIEW"):
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

        bpy.app.timers.register(wait_for_asset_previews_generation)

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
