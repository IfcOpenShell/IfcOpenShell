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
import shutil
import hashlib
import zipfile
import tempfile
import traceback
import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.ifcopenshell_wrapper
import blenderbim
import blenderbim.bim.handler
import blenderbim.tool as tool
from pathlib import Path
from blenderbim.tool.brick import BrickStore
from typing import Set, Union, Optional


IFC_CONNECTED_TYPE = Union[bpy.types.Material, bpy.types.Object]


class IfcStore:
    path: str = ""
    file: Optional[ifcopenshell.file] = None
    schema: Optional[ifcopenshell.ifcopenshell_wrapper.schema_definition] = None
    cache: Optional[ifcopenshell.ifcopenshell_wrapper.HdfSerializer] = None
    cache_path: Optional[str] = None
    id_map: dict[int, IFC_CONNECTED_TYPE] = {}
    guid_map: dict[str, IFC_CONNECTED_TYPE] = {}
    edited_objs: Set[bpy.types.Object] = set()
    pset_template_path: str = ""
    pset_template_file: Optional[ifcopenshell.file] = None
    classification_path: str = ""
    classification_file: Optional[ifcopenshell.file] = None
    library_path: str = ""
    library_file: Optional[ifcopenshell.file] = None
    current_transaction = ""
    last_transaction = ""
    history = []
    future = []
    schema_identifiers = ["IFC4", "IFC2X3", "IFC4X3"]
    session_files: dict[str, ifcopenshell.file] = {}

    @staticmethod
    def purge():
        IfcStore.path = ""
        IfcStore.file = None
        IfcStore.schema = None
        IfcStore.cache = None
        IfcStore.cache_path = None
        IfcStore.id_map = {}
        IfcStore.guid_map = {}
        IfcStore.edited_objs = set()
        IfcStore.pset_template_path = ""
        IfcStore.pset_template_file = None
        IfcStore.library_path = ""
        IfcStore.library_file = None
        IfcStore.last_transaction = ""
        IfcStore.history = []
        IfcStore.future = []
        IfcStore.schema_identifiers = ["IFC4", "IFC2X3", "IFC4X3"]
        IfcStore.session_files = {}

    @staticmethod
    def get_file():
        if IfcStore.file is None:
            IfcStore.path = bpy.context.scene.BIMProperties.ifc_file
            if not os.path.isabs(IfcStore.path):
                IfcStore.path = os.path.abspath(os.path.join(bpy.path.abspath("//"), IfcStore.path))
            if IfcStore.path:
                try:
                    IfcStore.load_file(IfcStore.path)
                except Exception as e:
                    print(f"Failed to load file {IfcStore.path}. Error details: {e}")
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
                if os.path.exists(IfcStore.cache_path):
                    os.remove(IfcStore.cache_path)
                    try:
                        IfcStore.cache = ifcopenshell.geom.serializers.hdf5(IfcStore.cache_path, cache_settings)
                    except:
                        return
                else:
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
        try:
            shutil.move(IfcStore.cache_path, new_cache_path)
        except PermissionError:
            try:
                shutil.copy2(IfcStore.cache_path, new_cache_path)
            except PermissionError:
                pass  # Well we tried. No cache for you!
        IfcStore.get_cache()

    @staticmethod
    def load_file(path) -> None:
        if not os.path.isfile(path):
            return
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
        elif bpy.context.scene.BIMProjectProperties.should_stream:
            IfcStore.file = ifcopenshell.open(path, should_stream=True)
        else:
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
    def get_element(id_or_guid: Union[int, str]) -> IFC_CONNECTED_TYPE:
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
    def relink_all_objects() -> None:
        if not IfcStore.get_file():
            return
        for obj in bpy.data.objects:
            if obj.library:
                continue
            IfcStore.relink_object(obj)
        for obj in bpy.data.materials:
            if obj.library:
                continue
            IfcStore.relink_object(obj)

    @staticmethod
    def relink_object(obj: IFC_CONNECTED_TYPE) -> None:
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
    def link_element(element: ifcopenshell.entity_instance, obj: IFC_CONNECTED_TYPE) -> None:
        # Please use tool.Ifc.link() instead of this method. We want to
        # refactor this class and deprecate usage of IfcStore in favour of
        # tools.
        if not isinstance(obj, (bpy.types.Object, bpy.types.Material)):
            obj.BIMMeshProperties.ifc_definition_id = element.id()
            return

        existing_obj = IfcStore.id_map.get(element.id(), None)
        if existing_obj == obj:
            return
        elif existing_obj:
            try:
                existing_obj.name
                IfcStore.unlink_element(element=element, obj=existing_obj)
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
            blenderbim.bim.handler.subscribe_to(
                obj, "active_material_index", blenderbim.bim.handler.active_material_index_callback
            )

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
        blenderbim.bim.handler.subscribe_to(obj, "name", blenderbim.bim.handler.name_callback)
        if isinstance(obj, bpy.types.Material):
            blenderbim.bim.handler.subscribe_to(obj, "diffuse_color", blenderbim.bim.handler.color_callback)
        elif isinstance(obj, bpy.types.Object):
            blenderbim.bim.handler.subscribe_to(
                obj, "active_material_index", blenderbim.bim.handler.active_material_index_callback
            )
        # TODO Listeners are not re-registered. Does this cause nasty problems to debug later on?
        # TODO We're handling id_map and guid_map, but what about edited_objs? This might cause big problems.

    @staticmethod
    def rollback_unlink_element(data) -> None:
        if "id" not in data or "obj" not in data:
            return
        obj = bpy.data.objects.get(data["obj"])
        IfcStore.id_map[data["id"]] = obj
        if data["guid"]:
            IfcStore.guid_map[data["guid"]] = obj

    @staticmethod
    def commit_unlink_element(data) -> None:
        del IfcStore.id_map[data["id"]]
        if data["guid"]:
            del IfcStore.guid_map[data["guid"]]

    @staticmethod
    def unlink_element(
        element: Optional[ifcopenshell.entity_instance] = None, obj: Optional[IFC_CONNECTED_TYPE] = None
    ) -> None:
        if element is None:
            try:
                element = tool.Ifc.get_entity(obj)
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
    def execute_ifc_operator(operator: bpy.types.Operator, context: bpy.types.Context, is_invoke=False):
        blenderbim.last_actions.append({"type": "operator", "name": operator.bl_idname})
        bpy.context.scene.BIMProperties.is_dirty = True
        is_top_level_operator = not bool(IfcStore.current_transaction)

        if is_top_level_operator:
            IfcStore.begin_transaction(operator)
            if tool.Ifc.get():
                tool.Ifc.get().begin_transaction()
            if BrickStore.graph is not None:  # `if BrickStore.graph` by itself takes ages.
                BrickStore.begin_transaction()
            # This empty transaction ensures that each operator has at least one transaction
            IfcStore.add_transaction_operation(operator, rollback=lambda data: True, commit=lambda data: True)
        else:
            operator.transaction_key = IfcStore.current_transaction

        try:
            if is_invoke:
                result = getattr(operator, "_invoke")(context, None)
            else:
                result = getattr(operator, "_execute")(context)
        except:
            blenderbim.last_error = traceback.format_exc()
            raise

        if is_top_level_operator:
            if tool.Ifc.get():
                tool.Ifc.get().end_transaction()
                IfcStore.add_transaction_operation(
                    operator, rollback=lambda d: tool.Ifc.get().undo(), commit=lambda d: tool.Ifc.get().redo()
                )
            if BrickStore.graph is not None:  # `if BrickStore.graph` by itself takes ages.
                BrickStore.end_transaction()
            IfcStore.end_transaction(operator)
            blenderbim.bim.handler.refresh_ui_data()

        return result

    @staticmethod
    def begin_transaction(operator: bpy.types.Operator) -> None:
        IfcStore.current_transaction = str(uuid.uuid4())
        operator.transaction_key = IfcStore.current_transaction

    @staticmethod
    def end_transaction(operator: bpy.types.Operator) -> None:
        IfcStore.current_transaction = ""
        operator.transaction_key = ""

    @staticmethod
    def add_transaction_operation(operator: bpy.types.Operator, rollback=None, commit=None) -> None:
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
    def undo(until_key=None) -> None:
        BrickStore.undo()
        if not IfcStore.history:
            return

        while IfcStore.history:
            if IfcStore.history[-1]["key"] == until_key:
                return

            event = IfcStore.history.pop()
            for transaction in event["operations"][::-1]:
                transaction["rollback"](transaction["data"])
            IfcStore.future.append(event)

    @staticmethod
    def redo(until_key=None) -> None:
        BrickStore.redo()

        if not IfcStore.future:
            return

        has_encountered_key = False
        while IfcStore.future:
            if has_encountered_key and IfcStore.future[-1]["key"] != until_key:
                return
            elif IfcStore.future[-1]["key"] == until_key:
                has_encountered_key = True

            event = IfcStore.future.pop()
            for transaction in event["operations"]:
                transaction["commit"](transaction["data"])
            IfcStore.history.append(event)
