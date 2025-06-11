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
from ifcopenshell.file import UndoSystemError
from pathlib import Path
from bonsai.tool.brick import BrickStore
from typing import Union, Optional, TypedDict, NotRequired, Literal
from collections.abc import Callable


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
    edited_objs: set[bpy.types.Object] = set()
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
            props = tool.Blender.get_bim_props()
            IfcStore.set_path(props.ifc_file)
            if IfcStore.path:
                try:
                    IfcStore.load_file(IfcStore.path)
                except Exception as e:
                    print(f"Failed to load file {IfcStore.path}. Error details: {e}")
        return IfcStore.file

    @staticmethod
    def set_path(value):
        IfcStore.path = value
        # Interpret relative paths as relative to .blend file.
        if IfcStore.path and not os.path.isabs(IfcStore.path):
            IfcStore.path = os.path.abspath(os.path.join(bpy.path.abspath("//"), IfcStore.path))

    @staticmethod
    def get_cache():
        if IfcStore.cache is None and IfcStore.path:
            props = tool.Blender.get_bim_props()
            ifc_key = IfcStore.path + IfcStore.file.wrapped_data.header.file_name.time_stamp
            ifc_hash = hashlib.md5(ifc_key.encode("utf-8")).hexdigest()
            os.makedirs(props.cache_dir, exist_ok=True)
            IfcStore.cache_path = os.path.join(props.cache_dir, f"{ifc_hash}.h5")
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
        props = tool.Blender.get_bim_props()
        new_cache_path = os.path.join(props.cache_dir, f"{ifc_hash}.h5")
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
        props = tool.Project.get_project_props()
        if extension.lower() == "ifczip":
            with tempfile.TemporaryDirectory() as unzipped_path:
                with zipfile.ZipFile(path, "r") as zip_ref:
                    zip_ref.extractall(unzipped_path)
                for filename in Path(unzipped_path).glob("**/*.ifc"):
                    IfcStore.file = ifcopenshell.open(filename)
                    return
        elif extension.lower() == "ifcxml":
            IfcStore.file = ifcopenshell.file(ifcopenshell.ifcopenshell_wrapper.parse_ifcxml(path))
        elif props.should_stream:
            IfcStore.file = ifcopenshell.open(path, should_stream=True)
        else:
            IfcStore.file = ifcopenshell.open(path)

    @staticmethod
    def get_schema() -> ifcopenshell.ifcopenshell_wrapper.schema_definition:
        if IfcStore.file is None:
            props = tool.Project.get_project_props()
            IfcStore.schema = ifcopenshell.ifcopenshell_wrapper.schema_by_name(props.export_schema)
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
            tool.Geometry.get_mesh_props(obj).ifc_definition_id = element.id()
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
            props = tool.Style.get_material_style_props(obj)
            props.ifc_definition_id = element.id()
        else:
            props = tool.Blender.get_object_bim_props(obj)
            props.ifc_definition_id = element.id()

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
            props = tool.Style.get_material_style_props(obj)
            props.ifc_definition_id = 0
        else:  # bpy.types.Object
            props = tool.Blender.get_object_bim_props(obj)
            props.ifc_definition_id = 0

    @staticmethod
    def get_ifc_file_undo_callback(callback_type: Literal["UNDO", "REDO"]):
        def callback(_) -> None:
            try:
                if callback_type == "UNDO":
                    tool.Ifc.get().undo()
                else:
                    tool.Ifc.get().redo()
            except Exception as e:
                # Persistent callbacks errors are not visible from UI and we set `last_error`
                # to make it visible.
                error_msg = ""
                # In theory it should always be UndoSystemError, but just to be safe.
                if isinstance(e, UndoSystemError):
                    error_msg += "Undo transaction operations:\n"
                    transaction = e.transaction
                    for operation in transaction.operations:
                        error_msg += f"- {str(operation)}\n"
                    # Show it in system console too, not just in last message.
                    print(error_msg)
                error_msg += traceback.format_exc()
                bonsai.last_error = error_msg
                raise

        return callback

    @staticmethod
    def execute_ifc_operator(
        operator: tool.Ifc.Operator,
        context: bpy.types.Context,
        event=None,
        method: Literal["EXECUTE", "INVOKE", "MODAL"] = "EXECUTE",
    ) -> set[str]:
        bonsai.last_actions.append({"type": "operator", "name": operator.bl_idname})
        props = tool.Blender.get_bim_props()
        props.is_dirty = True
        # Modals don't nest, and Blender handles the loop that continuously calls modal()
        is_top_level_operator = not bool(IfcStore.current_transaction) or (method == "MODAL")

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
                        operator,
                        rollback=IfcStore.get_ifc_file_undo_callback("UNDO"),
                        commit=IfcStore.get_ifc_file_undo_callback("REDO"),
                    )
                if BrickStore.graph is not None:  # `if BrickStore.graph` by itself takes ages.
                    BrickStore.end_transaction()
                IfcStore.end_transaction(operator)
                bonsai.bim.handler.refresh_ui_data()

        try:
            if method == "EXECUTE":
                result = getattr(operator, "_execute")(context)
            elif method == "INVOKE":
                result = getattr(operator, "_invoke")(context, event)
            elif method == "MODAL":
                result = getattr(operator, "_modal")(context, event)
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

        if method == "MODAL":
            if result == {"FINISHED"}:
                end_top_level_operator()
            elif result == {"CANCELLED"}:
                # Please read the docs: https://docs.blender.org/api/current/bpy.types.Operator.html
                # > "when an operator returns {'CANCELLED'}, no undo step will be created".
                # This means that if your modal edits IFC data, then the user
                # cancels it, Blender's undo history will not be in sync with
                # Bonsai / IfcOpenShell's undo history. Instead of hoping for
                # Bonsai devs to remember to handle the "cancel" state (i.e.
                # detect escape keypress) and return {"FINISHED"}, we instead
                # always enforce an undo step.
                bpy.ops.ed.undo_push(message=f"Cancel {operator.bl_idname}")
                end_top_level_operator()
        else:
            end_top_level_operator()
        return result

    @staticmethod
    def begin_transaction(operator: tool.Ifc.Operator) -> None:
        IfcStore.current_transaction = str(uuid.uuid4()) + operator.__class__.__name__
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
        props = tool.Blender.get_bim_props()
        props.last_transaction = key
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
