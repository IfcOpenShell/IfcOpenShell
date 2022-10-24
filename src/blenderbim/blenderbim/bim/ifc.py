# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021, 2022 Dion Moult <dion@thinkmoult.com>
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

import os
import bpy
import uuid
import hashlib
import zipfile
import tempfile
import ifcopenshell
import blenderbim.bim.handler
from pathlib import Path


class IfcStore:
    path = ""
    file = None
    schema = None
    cache = None
    cache_path = None
    id_map = {}
    guid_map = {}
    deleted_ids = set()
    edited_objs = set()
    pset_template_path = ""
    pset_template_file = None
    classification_path = ""
    classification_file = None
    library_path = ""
    library_file = None
    element_listeners = set()
    undo_redo_stack_objects = set()
    undo_redo_stack_object_names = {}
    current_transaction = ""
    last_transaction = ""
    history = []
    future = []
    schema_identifiers = ["IFC4", "IFC2X3", "IFC4X3"]

    @staticmethod
    def purge():
        IfcStore.path = ""
        IfcStore.file = None
        IfcStore.schema = None
        IfcStore.cache = None
        IfcStore.cache_path = None
        IfcStore.id_map = {}
        IfcStore.guid_map = {}
        IfcStore.deleted_ids = set()
        IfcStore.edited_objs = set()
        IfcStore.pset_template_path = ""
        IfcStore.pset_template_file = None
        IfcStore.library_path = ""
        IfcStore.library_file = None
        IfcStore.last_transaction = ""
        IfcStore.history = []
        IfcStore.future = []
        IfcStore.schema_identifiers = ["IFC4", "IFC2X3", "IFC4X3"]

    @staticmethod
    def get_file():
        if IfcStore.file is None:
            IfcStore.path = bpy.context.scene.BIMProperties.ifc_file
            if not os.path.isabs(IfcStore.path):
                IfcStore.path = os.path.abspath(os.path.join(bpy.path.abspath("//"), IfcStore.path))
            if IfcStore.path:
                try:
                    IfcStore.load_file(IfcStore.path)
                except:
                    pass
        return IfcStore.file

    @staticmethod
    def get_cache():
        if IfcStore.cache is None and IfcStore.path:
            ifc_key = IfcStore.path + IfcStore.file.wrapped_data.header.file_name.time_stamp
            ifc_hash = hashlib.md5(ifc_key.encode("utf-8")).hexdigest()
            IfcStore.cache_path = os.path.join(bpy.context.scene.BIMProperties.data_dir, "cache", f"{ifc_hash}.h5")
            cache_settings = ifcopenshell.geom.settings()
            cache_settings.set(cache_settings.STRICT_TOLERANCE, True)
            try:
                IfcStore.cache = ifcopenshell.geom.serializers.hdf5(IfcStore.cache_path, cache_settings)
            except:
                return
        return IfcStore.cache

    @staticmethod
    def update_cache():
        if not IfcStore.cache:
            return
        ifc_key = IfcStore.path + IfcStore.file.wrapped_data.header.file_name.time_stamp
        ifc_hash = hashlib.md5(ifc_key.encode("utf-8")).hexdigest()
        new_cache_path = os.path.join(bpy.context.scene.BIMProperties.data_dir, "cache", f"{ifc_hash}.h5")
        IfcStore.cache = None
        os.replace(IfcStore.cache_path, new_cache_path)
        IfcStore.get_cache()

    @staticmethod
    def load_file(path):
        extension = path.split(".")[-1]
        if extension.lower() == "ifczip":
            with tempfile.TemporaryDirectory() as unzipped_path:
                with zipfile.ZipFile(path, "r") as zip_ref:
                    zip_ref.extractall(unzipped_path)
                for filename in Path(unzipped_path).glob("**/*.ifc"):
                    IfcStore.file = ifcopenshell.open(filename)
                    return
        elif extension.lower() == "ifcxml":
            IfcStore.file = ifcopenshell.file(ifcopenshell.ifcopenshell_wrapper.parse_ifcxml(path))
        elif extension.lower() == "ifc":
            IfcStore.file = ifcopenshell.open(path)

    @staticmethod
    def get_schema():
        if IfcStore.file is None:
            IfcStore.schema = ifcopenshell.ifcopenshell_wrapper.schema_by_name(
                bpy.context.scene.BIMProjectProperties.export_schema
            )
        elif IfcStore.schema is None:
            IfcStore.schema = ifcopenshell.ifcopenshell_wrapper.schema_by_name(IfcStore.file.schema)
        return IfcStore.schema

    @staticmethod
    def get_element(id_or_guid):
        if isinstance(id_or_guid, int):
            map_object = IfcStore.id_map
        else:
            map_object = IfcStore.guid_map
        try:
            obj = map_object[id_or_guid]
            obj.name  # In case the object has been deleted, this triggers an exception
        except:
            return
        return obj

    @staticmethod
    def add_element_listener(callback):
        IfcStore.element_listeners.add(callback)

    @staticmethod
    def track_undo_redo_stack_object_map():
        """Keeps track of currently mapped object names, typically during undo and redo

        When any Blender object is stored outside a Blender PointerProperty, such as
        in a regular Python list, there is the likely probability that the object
        will be invalidated when undo or redo occurs. Object invalidation seems to
        occur whenever an object is affected during an operation.

        For example, if an operator deletes a modifier on o1, then o1 will be invalidated.
        """
        for key, value in IfcStore.id_map.items():
            try:
                IfcStore.undo_redo_stack_object_names[key] = value.name
            except:
                continue

    @staticmethod
    def track_undo_redo_stack_selected_objects():
        """Keeps track of selected object names, typically during undo and redo

        When any Blender object is stored outside a Blender PointerProperty, such as
        in a regular Python list, there is the likely probability that the object
        will be invalidated when undo or redo occurs. Object invalidation seems to
        occur for selected objects either pre/post undo/redo event, including
        selected objects for consecutive undo/redos, and all children. This is
        important because selected objects are often deleted from the scene.

        So if I first select o1, then o2, then o3, then press undo, o3 will be
        invalidated. If instead I press undo twice, o3 and o2 will be invalidated.
        """
        if bpy.context.active_object:
            objects = set([o.name for o in bpy.context.selected_objects + [bpy.context.active_object]])
            objects.update([o.name for o in bpy.context.active_object.children])
        else:
            objects = set([o.name for o in bpy.context.selected_objects])
        for obj in bpy.context.selected_objects:
            objects.update([o.name for o in obj.children])
        IfcStore.undo_redo_stack_objects |= objects

    @staticmethod
    def reload_undo_redo_stack_objects():
        """Reloads any invalidated objects after undo or redo

        After an undo or redo operation, objects may have been invalidated in
        our id_map and guid_map. Invalidated objects are typically those that
        have been manipulated or deleted. This checks the cache of mapped and
        selected objects prior to the operation and ensures that if the object
        is invalidated, they are reloaded based on the object name that was
        tracked prior to the undo / redo.
        """
        file = IfcStore.get_file()
        if not file:
            return

        # First, reload objects that were selected or active
        for name in IfcStore.undo_redo_stack_objects:
            obj = bpy.data.objects.get(name)
            if not obj:
                continue
            if not obj.BIMObjectProperties.ifc_definition_id:
                continue
            element = file.by_id(obj.BIMObjectProperties.ifc_definition_id)
            data = {"id": element.id(), "obj": obj.name}
            if hasattr(element, "GlobalId"):
                data["guid"] = element.GlobalId
            IfcStore.commit_link_element(data)

        # Scan for any straggling invalidated objects which were indirectly affected and reload them too.
        for key, value in IfcStore.id_map.items():
            try:
                value.name
            except:
                # TODO not so sure about this obj_name check
                obj_name = IfcStore.undo_redo_stack_object_names.get(key, None)
                if not obj_name:
                    continue
                obj = bpy.data.objects.get(obj_name)
                if not obj or not obj.BIMObjectProperties.ifc_definition_id:
                    continue
                element = file.by_id(obj.BIMObjectProperties.ifc_definition_id)
                data = {"id": element.id(), "obj": obj.name}
                if hasattr(element, "GlobalId"):
                    data["guid"] = element.GlobalId
                IfcStore.commit_link_element(data)

    @staticmethod
    def relink_all_objects():
        if not IfcStore.get_file():
            return
        for obj in bpy.data.objects:
            IfcStore.relink_object(obj)
        for obj in bpy.data.materials:
            IfcStore.relink_object(obj)

    @staticmethod
    def relink_object(obj):
        if not obj:
            return
        if obj.BIMObjectProperties.ifc_definition_id:
            try:
                element = IfcStore.get_file().by_id(obj.BIMObjectProperties.ifc_definition_id)
            except:
                return
            data = {"id": element.id(), "obj": obj.name}
            if hasattr(element, "GlobalId"):
                data["guid"] = element.GlobalId
            IfcStore.commit_link_element(data)
        if hasattr(obj, "BIMMaterialProperties") and obj.BIMMaterialProperties.ifc_style_id:
            try:
                element = IfcStore.get_file().by_id(obj.BIMMaterialProperties.ifc_style_id)
            except:
                return
            data = {"id": element.id(), "obj": obj.name}
            IfcStore.commit_link_element(data)

    @staticmethod
    def delete_element(element):
        IfcStore.deleted_ids.add(element.id())
        if IfcStore.history:
            data = {"id": element.id()}
            IfcStore.history[-1]["operations"].append(
                {"rollback": IfcStore.rollback_delete_element, "commit": IfcStore.commit_delete_element, "data": data}
            )

    @staticmethod
    def rollback_delete_element(data):
        IfcStore.deleted_ids.remove(data["id"])

    @staticmethod
    def commit_delete_element(data):
        IfcStore.deleted_ids.add(data["id"])

    @staticmethod
    def link_element(element, obj):
        existing_obj = IfcStore.id_map.get(element.id(), None)
        if existing_obj == obj:
            return
        elif existing_obj:
            try:
                existing_obj.name
                IfcStore.unlink_element(obj=existing_obj)
            except:
                pass
        IfcStore.id_map[element.id()] = obj
        if hasattr(element, "GlobalId"):
            IfcStore.guid_map[element.GlobalId] = obj

        if element.is_a("IfcSurfaceStyle"):
            obj.BIMMaterialProperties.ifc_style_id = element.id()
        else:
            obj.BIMObjectProperties.ifc_definition_id = element.id()

        blenderbim.bim.handler.subscribe_to(obj, "name", blenderbim.bim.handler.name_callback)

        if isinstance(obj, bpy.types.Material):
            blenderbim.bim.handler.subscribe_to(obj, "diffuse_color", blenderbim.bim.handler.color_callback)
        elif isinstance(obj, bpy.types.Object):
            blenderbim.bim.handler.subscribe_to(obj, "mode", blenderbim.bim.handler.mode_callback)

        for listener in IfcStore.element_listeners:
            listener(element, obj)

        if IfcStore.history:
            data = {"id": element.id(), "guid": getattr(element, "GlobalId", None), "obj": obj.name}
            IfcStore.history[-1]["operations"].append(
                {"rollback": IfcStore.rollback_link_element, "commit": IfcStore.commit_link_element, "data": data}
            )

    @staticmethod
    def rollback_link_element(data):
        del IfcStore.id_map[data["id"]]
        if data["guid"]:
            del IfcStore.guid_map[data["guid"]]

    @staticmethod
    def commit_link_element(data):
        obj = bpy.data.objects.get(data["obj"])
        if not obj:
            obj = bpy.data.materials.get(data["obj"])
        IfcStore.id_map[data["id"]] = obj
        if "guid" in data:
            IfcStore.guid_map[data["guid"]] = obj
        blenderbim.bim.handler.subscribe_to(obj, "mode", blenderbim.bim.handler.mode_callback)
        blenderbim.bim.handler.subscribe_to(obj, "name", blenderbim.bim.handler.name_callback)
        if isinstance(obj, bpy.types.Material):
            blenderbim.bim.handler.subscribe_to(obj, "diffuse_color", blenderbim.bim.handler.color_callback)
        # TODO Listeners are not re-registered. Does this cause nasty problems to debug later on?
        # TODO We're handling id_map and guid_map, but what about edited_objs? This might cause big problems.

    @staticmethod
    def rollback_unlink_element(data):
        if "id" not in data or "obj" not in data:
            return
        obj = bpy.data.objects.get(data["obj"])
        IfcStore.id_map[data["id"]] = obj
        if data["guid"]:
            IfcStore.guid_map[data["guid"]] = obj

    @staticmethod
    def commit_unlink_element(data):
        del IfcStore.id_map[data["id"]]
        if data["guid"]:
            del IfcStore.guid_map[data["guid"]]

    @staticmethod
    def unlink_element(element=None, obj=None):
        if element is None:
            try:
                element = IfcStore.get_file().by_id(obj.BIMObjectProperties.ifc_definition_id)
            except:
                pass

        if obj is None:
            try:
                potential_obj = IfcStore.id_map[element.id()]
                potential_obj.name
                obj = potential_obj
            except:
                pass

        try:
            if element:
                del IfcStore.id_map[element.id()]
            else:
                del IfcStore.id_map[obj.BIMObjectProperties.ifc_definition_id]
        except:
            pass

        try:
            if element and hasattr(element, "GlobalId"):
                del IfcStore.guid_map[element.GlobalId]
        except:
            pass

        if element and element.is_a("IfcSurfaceStyle"):
            obj.BIMMaterialProperties.ifc_style_id = 0
        elif obj:
            obj.BIMObjectProperties.ifc_definition_id = 0

        if IfcStore.history:
            data = {}
            if element:
                data["id"] = element.id()
                data["guid"] = getattr(element, "GlobalId", None)
            if obj:
                data["obj"] = obj.name
            IfcStore.history[-1]["operations"].append(
                {"rollback": IfcStore.rollback_unlink_element, "commit": IfcStore.commit_unlink_element, "data": data}
            )

    @staticmethod
    def execute_ifc_operator(operator, context):
        is_top_level_operator = not bool(IfcStore.current_transaction)

        if is_top_level_operator:
            IfcStore.begin_transaction(operator)
            IfcStore.get_file().begin_transaction()
            # This empty transaction ensures that each operator has at least one transaction
            IfcStore.add_transaction_operation(operator, rollback=lambda data: True, commit=lambda data: True)
        else:
            operator.transaction_key = IfcStore.current_transaction

        result = getattr(operator, "_execute")(context)

        if is_top_level_operator:
            IfcStore.get_file().end_transaction()
            IfcStore.add_transaction_operation(
                operator, rollback=lambda d: IfcStore.get_file().undo(), commit=lambda d: IfcStore.get_file().redo()
            )
            IfcStore.end_transaction(operator)
            blenderbim.bim.handler.refresh_ui_data()

        return result

    @staticmethod
    def begin_transaction(operator):
        IfcStore.undo_redo_stack_objects = set()
        IfcStore.undo_redo_stack_object_names = {}
        IfcStore.current_transaction = str(uuid.uuid4())
        operator.transaction_key = IfcStore.current_transaction

    @staticmethod
    def end_transaction(operator):
        IfcStore.current_transaction = ""
        operator.transaction_key = ""

    @staticmethod
    def add_transaction_operation(operator, rollback=None, commit=None):
        key = getattr(operator, "transaction_key", None)
        data = getattr(operator, "transaction_data", None)
        bpy.context.scene.BIMProperties.last_transaction = key
        IfcStore.last_transaction = key
        rollback = rollback or getattr(operator, "rollback", lambda data: True)
        commit = commit or getattr(operator, "commit", lambda data: True)
        if IfcStore.history and IfcStore.history[-1]["key"] == key:
            IfcStore.history[-1]["operations"].append({"rollback": rollback, "commit": commit, "data": data})
        else:
            IfcStore.history.append(
                {"key": key, "operations": [{"rollback": rollback, "commit": commit, "data": data}]}
            )
        IfcStore.future = []

    @staticmethod
    def undo():
        if not IfcStore.history:
            return
        event = IfcStore.history.pop()
        for transaction in event["operations"][::-1]:
            transaction["rollback"](transaction["data"])
        IfcStore.future.append(event)

    @staticmethod
    def redo():
        if not IfcStore.future:
            return
        event = IfcStore.future.pop()
        for transaction in event["operations"]:
            transaction["commit"](transaction["data"])
        IfcStore.history.append(event)
