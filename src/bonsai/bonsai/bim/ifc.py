# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021, 2022 Dion Moult <dion@thinkmoult.com>
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

from __future__ import annotations
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
import bonsai
import bonsai.bim.handler
import bonsai.tool as tool
from pathlib import Path
from bonsai.tool.brick import BrickStore
from typing import Set, Union, Optional, TypedDict, Callable, NotRequired


IFC_CONNECTED_TYPE = Union[bpy.types.Material, bpy.types.Object]


class OperationData(TypedDict):
    id: int
    guid: NotRequired[str]
    obj: str


class EditObjectOperationData(TypedDict):
    obj: str


class Operation(TypedDict):
    rollback: Callable
    commit: Callable
    data: Union[OperationData, EditObjectOperationData, None]


class TransactionStep(TypedDict):
    key: str
    operations: list[Operation]


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
    history: list[TransactionStep] = []
    future: list[TransactionStep] = []
    schema_identifiers = ["IFC4", "IFC2X3", "IFC4X3_ADD2"]
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
        IfcStore.schema_identifiers = ["IFC4", "IFC2X3", "IFC4X3_ADD2"]
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
            os.makedirs(bpy.context.scene.BIMProperties.cache_dir, exist_ok=True)
            IfcStore.cache_path = os.path.join(bpy.context.scene.BIMProperties.cache_dir, f"{ifc_hash}.h5")
            cache_path = Path(IfcStore.cache_path)
            cache_settings = ifcopenshell.geom.settings()
            serializer_settings = ifcopenshell.geom.serializer_settings()
            cache_preexists = cache_path.exists()
            try:
                IfcStore.cache = ifcopenshell.geom.serializers.hdf5(
                    IfcStore.cache_path, cache_settings, serializer_settings
                )
                if cache_preexists:
                    print(f"Successfully loaded existing cache: {cache_path.name}.")
                else:
                    print("New cache was created.")
            except Exception as e:
                if cache_preexists:
                    print(f"Failed to create a cache from existing file '{cache_path.name}': {str(e)}.")
                else:
                    print(f"Failed to create a cache: {str(e)}.")
                    # No point to trying again the same operation.
                    return

                os.remove(IfcStore.cache_path)
                try:
                    IfcStore.cache = ifcopenshell.geom.serializers.hdf5(
                        IfcStore.cache_path, cache_settings, serializer_settings
                    )
                    print("New cache was created.")
                except Exception as e:
                    print(f"Failed to create a cache: {str(e)}.")
                    return
        return IfcStore.cache

    @staticmethod
    def update_cache():
        if not IfcStore.cache:
            return
        assert IfcStore.cache_path
        assert IfcStore.file
        ifc_key = IfcStore.path + IfcStore.file.wrapped_data.header.file_name.time_stamp
        ifc_hash = hashlib.md5(ifc_key.encode("utf-8")).hexdigest()
        new_cache_path = os.path.join(bpy.context.scene.BIMProperties.cache_dir, f"{ifc_hash}.h5")
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
    def get_schema() -> ifcopenshell.ifcopenshell_wrapper.schema_definition:
        if IfcStore.file is None:
            IfcStore.schema = ifcopenshell.ifcopenshell_wrapper.schema_by_name(
                bpy.context.scene.BIMProjectProperties.export_schema
            )
        elif IfcStore.schema is None:
            IfcStore.schema = ifcopenshell.ifcopenshell_wrapper.schema_by_name(IfcStore.file.schema_identifier)
        return IfcStore.schema

    @staticmethod
    def get_element(id_or_guid: Union[int, str]) -> Union[IFC_CONNECTED_TYPE, None]:
        if isinstance(id_or_guid, int):
            obj = IfcStore.id_map.get(id_or_guid)
        else:
            obj = IfcStore.guid_map.get(id_or_guid)
        if obj is None:
            return None
        if not tool.Blender.is_valid_data_block(obj):
            return None
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
        element = tool.Ifc.get_entity(obj)
        if not element:
            return
        data = OperationData(id=element.id(), obj=obj.name)
        if hasattr(element, "GlobalId"):
            data["guid"] = element.GlobalId
        IfcStore.commit_link_element(data)

    @staticmethod
    def link_element(
        element: ifcopenshell.entity_instance, obj: Union[IFC_CONNECTED_TYPE, tool.Geometry.TYPES_WITH_MESH_PROPERTIES]
    ) -> None:
        # Please use tool.Ifc.link() instead of this method. We want to
        # refactor this class and deprecate usage of IfcStore in favour of
        # tools.
        if not isinstance(obj, (bpy.types.Object, bpy.types.Material)):
            obj.BIMMeshProperties.ifc_definition_id = element.id()
            return

        existing_obj = IfcStore.id_map.get(element.id(), None)
        if existing_obj == obj:
            return
        # TODO: When does this occur?
        elif existing_obj and tool.Blender.is_valid_data_block(existing_obj):
            IfcStore.unlink_element(obj=existing_obj)

        IfcStore.id_map[element.id()] = obj
        if global_id := getattr(element, "GlobalId", None):
            IfcStore.guid_map[global_id] = obj

        if element.is_a("IfcSurfaceStyle"):
            obj.BIMStyleProperties.ifc_definition_id = element.id()
        else:
            obj.BIMObjectProperties.ifc_definition_id = element.id()

        tool.Ifc.setup_listeners(obj)

        if IfcStore.history:
            data = OperationData(id=element.id(), obj=obj.name)
            if global_id:
                data["guid"] = global_id
            IfcStore.history[-1]["operations"].append(
                Operation(rollback=IfcStore.rollback_link_element, commit=IfcStore.commit_link_element, data=data)
            )

    @staticmethod
    def get_object_by_name(name: str) -> Union[IFC_CONNECTED_TYPE, None]:
        obj = bpy.data.objects.get(name)
        if not obj:
            obj = bpy.data.materials.get(name)
        return obj

    @staticmethod
    def rollback_link_element(data: OperationData) -> None:
        del IfcStore.id_map[data["id"]]
        if "guid" in data:
            del IfcStore.guid_map[data["guid"]]
        obj = IfcStore.get_object_by_name(data["obj"])
        if obj is None:
            # obj was just created during this step and didn't existed before.
            return
        bpy.msgbus.clear_by_owner(obj)

    @staticmethod
    def commit_link_element(data: OperationData) -> None:
        obj = IfcStore.get_object_by_name(data["obj"])
        IfcStore.id_map[data["id"]] = obj
        if "guid" in data:
            IfcStore.guid_map[data["guid"]] = obj
        tool.Ifc.setup_listeners(obj)

    @staticmethod
    def history_edit_object(obj: bpy.types.Object, *, finish_editing: bool) -> None:
        if not IfcStore.history:
            return

        commit, rollback = IfcStore.commit_edit_object, IfcStore.rollback_edit_object
        if finish_editing:
            commit, rollback = rollback, commit

        data = EditObjectOperationData(obj=obj.name)
        IfcStore.history[-1]["operations"].append(Operation(rollback=rollback, commit=commit, data=data))

    @staticmethod
    def commit_edit_object(data: EditObjectOperationData) -> None:
        obj = bpy.data.objects[data["obj"]]
        IfcStore.edited_objs.add(obj)

    @staticmethod
    def rollback_edit_object(data: EditObjectOperationData) -> None:
        obj = bpy.data.objects[data["obj"]]
        IfcStore.edited_objs.discard(obj)

    @staticmethod
    def rollback_unlink_element(data: OperationData) -> None:
        if "id" not in data or "obj" not in data:
            return
        obj = IfcStore.get_object_by_name(data["obj"])
        IfcStore.id_map[data["id"]] = obj
        if "guid" in data:
            IfcStore.guid_map[data["guid"]] = obj
        tool.Ifc.setup_listeners(obj)

    @staticmethod
    def commit_unlink_element(data: OperationData) -> None:
        del IfcStore.id_map[data["id"]]
        if "guid" in data:
            del IfcStore.guid_map[data["guid"]]
        obj = IfcStore.get_object_by_name(data["obj"])
        # obj might be removed after unlink.
        if not obj:
            bpy.msgbus.clear_by_owner(obj)

    @staticmethod
    def unlink_element(
        element: Optional[ifcopenshell.entity_instance] = None, obj: Optional[IFC_CONNECTED_TYPE] = None
    ) -> None:
        """Unlink IFC `element` or Blender `obj`.

        If element is provided then it will be unlinked from the related Blender object.
        Blender object's IFC information is also will be purged.

        If Blender object is provided  then all IFC information will be purged from this object.
        Method won't be searching for related IFC elements as Blender object might come from
        different Blender session and there might be an ids/guids clash.

        Only one argument must be provided and other should be omitted as they have different meaning.
        :raises TypeError: If both arguments or no arguments provided.

        """
        if not bool(element) ^ bool(obj):
            raise TypeError("Only one argument must be provided - element or obj.")

        if obj:
            IfcStore.purge_blender_ifc_data(obj)
            return

        assert element  # Type checker.
        if obj is None:
            try:
                potential_obj = IfcStore.id_map[element.id()]
                if tool.Blender.is_valid_data_block(potential_obj):
                    obj = potential_obj
                    IfcStore.purge_blender_ifc_data(obj)
            except:
                pass

        try:
            del IfcStore.id_map[element.id()]
        except:
            pass

        if global_id := getattr(element, "GlobalId", None):
            try:
                del IfcStore.guid_map[global_id]
            except:
                pass

        if IfcStore.history:
            data = OperationData(id=element.id())
            if global_id:
                data["guid"] = global_id
            if obj:
                data["obj"] = obj.name
            IfcStore.history[-1]["operations"].append(
                Operation(rollback=IfcStore.rollback_unlink_element, commit=IfcStore.commit_unlink_element, data=data)
            )

    @staticmethod
    def purge_blender_ifc_data(obj: IFC_CONNECTED_TYPE) -> None:
        if isinstance(obj, bpy.types.Material):
            obj.BIMStyleProperties.ifc_definition_id = 0
        else:  # bpy.types.Object
            obj.BIMObjectProperties.ifc_definition_id = 0
        # NOTE: in theory this will also remove listeners added by other addons
        # though never had a report when this would be a problem.
        bpy.msgbus.clear_by_owner(obj)

    @staticmethod
    def execute_ifc_operator(operator: tool.Ifc.Operator, context: bpy.types.Context, is_invoke=False) -> set[str]:
        bonsai.last_actions.append({"type": "operator", "name": operator.bl_idname})
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

        def end_top_level_operator() -> None:
            if is_top_level_operator:
                if tool.Ifc.get():
                    tool.Ifc.get().end_transaction()
                    IfcStore.add_transaction_operation(
                        operator, rollback=lambda d: tool.Ifc.get().undo(), commit=lambda d: tool.Ifc.get().redo()
                    )
                if BrickStore.graph is not None:  # `if BrickStore.graph` by itself takes ages.
                    BrickStore.end_transaction()
                IfcStore.end_transaction(operator)
                bonsai.bim.handler.refresh_ui_data()

        try:
            if is_invoke:
                result = getattr(operator, "_invoke")(context, None)
            else:
                result = getattr(operator, "_execute")(context)
        except:
            bonsai.last_error = traceback.format_exc()
            # Try to ensure undo will work since Blender undo does work in case of errors.
            # As error come unexpectedly, it's important that user might have a chance to save the file
            # before they got the error and not to lose the work they've done.
            #
            # Also, some users won't stop seeing the error,
            # so we need to try to ensure that undo for further operations will work.
            end_top_level_operator()
            raise

        end_top_level_operator()
        return result

    @staticmethod
    def begin_transaction(operator: tool.Ifc.Operator) -> None:
        IfcStore.current_transaction = str(uuid.uuid4())
        operator.transaction_key = IfcStore.current_transaction

    @staticmethod
    def end_transaction(operator: tool.Ifc.Operator) -> None:
        IfcStore.current_transaction = ""
        operator.transaction_key = ""

    @staticmethod
    def add_transaction_operation(
        operator: tool.Ifc.Operator, rollback: Optional[Callable] = None, commit: Optional[Callable] = None
    ) -> None:
        key = getattr(operator, "transaction_key", None)
        data = getattr(operator, "transaction_data", None)
        bpy.context.scene.BIMProperties.last_transaction = key
        IfcStore.last_transaction = key
        rollback = rollback or getattr(operator, "rollback", lambda data: True)
        commit = commit or getattr(operator, "commit", lambda data: True)
        if IfcStore.history and IfcStore.history[-1]["key"] == key:
            IfcStore.history[-1]["operations"].append(Operation(rollback=rollback, commit=commit, data=data))
        else:
            IfcStore.history.append(
                TransactionStep(key=key, operations=[Operation(rollback=rollback, commit=commit, data=data)])
            )
        IfcStore.future = []

    @staticmethod
    def undo(until_key: str = None) -> None:
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
    def redo(until_key: str = None) -> None:
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
