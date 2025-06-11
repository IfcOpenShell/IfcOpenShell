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

from __future__ import annotations
import os
import bpy
import numpy as np
import ifcopenshell.api
import ifcopenshell.ifcopenshell_wrapper as ifcopenshell_wrapper
import ifcopenshell.util.element
import ifcopenshell.util.schema
import bonsai.core.tool
import bonsai.bim.handler
import bonsai.tool as tool
from pathlib import Path
from bonsai.bim.ifc import IfcStore, IFC_CONNECTED_TYPE
from typing import Optional, Union, Any, final, Literal, TYPE_CHECKING

if TYPE_CHECKING:
    from bpy.stub_internal import rna_enums


class Ifc(bonsai.core.tool.Ifc):
    OBJECT_TYPE = Literal[
        "Object",
        "Material",
        "MaterialSetItem",
        "Task",
        "Cost",
        "Resource",
        "Profile",
        "WorkSchedule",
        "Group",
    ]

    @classmethod
    def run(cls, command: str, **kwargs) -> Any:
        return ifcopenshell.api.run(command, IfcStore.get_file(), **kwargs)

    @classmethod
    def set(cls, ifc: ifcopenshell.file) -> None:
        IfcStore.file = ifc

    @classmethod
    def get(cls) -> ifcopenshell.file:
        return IfcStore.get_file()

    @classmethod
    def set_path(cls, value: str) -> None:
        bim_props = tool.Blender.get_bim_props()
        bim_props.ifc_file = value
        IfcStore.set_path(value)

    @classmethod
    def get_path(cls) -> str:
        """Get absolute filepath to the IFC file, return empty string if file is not saved."""
        return IfcStore.path

    @classmethod
    def get_schema(cls) -> ifcopenshell.util.schema.IFC_SCHEMA:
        if IfcStore.get_file():
            return IfcStore.get_file().schema

    @classmethod
    def clear_history(cls) -> None:
        IfcStore.last_transaction = ""
        IfcStore.history = []
        IfcStore.future = []

    @classmethod
    def is_edited(cls, obj: bpy.types.Object, *, ignore_scale: bool = False) -> bool:
        return (not ignore_scale and tool.Geometry.is_scaled(obj)) or obj in IfcStore.edited_objs

    @classmethod
    def is_moved(cls, obj: bpy.types.Object, ifc_only: bool = True) -> bool:
        if ifc_only:
            element = cls.get_entity(obj)
            if not element and not tool.Geometry.is_representation_item(obj):
                return False
            if element and (element.is_a("IfcTypeProduct") or element.is_a("IfcProject")):
                return False
        oprops = tool.Blender.get_object_bim_props(obj)
        if not oprops.location_checksum:
            return True  # Let's be conservative
        loc_check = np.frombuffer(eval(oprops.location_checksum))
        loc_real = np.array(obj.matrix_world.translation).flatten()
        if not np.allclose(loc_check, loc_real, atol=1e-4):  # 0.1 mm
            return True
        rot_check = np.frombuffer(eval(oprops.rotation_checksum)).reshape(3, 3)
        rot_real = np.array(obj.matrix_world.to_3x3())
        rot_dot = np.dot(rot_check, rot_real.T)
        angle_rad = np.arccos(np.clip((np.trace(rot_dot) - 1) / 2, -1, 1))
        if angle_rad > 0.0017453292519943296:  # 0.1 degrees
            return True
        return False

    @classmethod
    def schema(cls) -> ifcopenshell_wrapper.schema_definition:
        return IfcStore.get_schema()

    @classmethod
    def get_entity(
        cls, obj: Union[IFC_CONNECTED_TYPE, tool.Geometry.TYPES_WITH_MESH_PROPERTIES]
    ) -> Union[ifcopenshell.entity_instance, None]:
        """Get linked IFC entity based on obj's ifc_definition_id.

        Return None if object is not linked to IFC or it's linked to non-existent element.
        """
        ifc = IfcStore.get_file()
        if not ifc or not obj:
            return

        props = None
        if isinstance(obj, bpy.types.Object):
            props = tool.Blender.get_object_bim_props(obj)
        elif isinstance(obj, bpy.types.Material):
            props = tool.Style.get_material_style_props(obj)
        else:
            props = tool.Geometry.get_mesh_props(obj)

        if props and (ifc_definition_id := props.ifc_definition_id):
            try:
                return ifc.by_id(ifc_definition_id)
            except RuntimeError:
                pass

    @classmethod
    def get_entity_by_id(cls, entity_id: int) -> Union[ifcopenshell.entity_instance, None]:
        """useful to check whether entity_id is still exists in IFC"""
        ifc_file = tool.Ifc.get()
        try:
            return ifc_file.by_id(entity_id)
        except RuntimeError:
            return None

    @classmethod
    def get_object(cls, element: ifcopenshell.entity_instance) -> Union[IFC_CONNECTED_TYPE, None]:
        return IfcStore.get_element(element.id())

    @classmethod
    def get_object_by_identifier(cls, id_or_guid: Union[int, str]) -> Union[IFC_CONNECTED_TYPE, None]:
        return IfcStore.get_element(id_or_guid)

    @classmethod
    def rebuild_element_maps(cls) -> None:
        """Rebuilds the id_map and guid_map

        When any Blender object is stored outside a Blender PointerProperty,
        such as in a regular Python list, there is the likely probability that
        the object will be invalidated when undo or redo occurs. Object
        invalidation seems to occur whenever an object is affected during an
        operation, or selected, or has a related modifier, and so on ... to
        cover all bases, this completely rebuilds the element maps.
        """

        IfcStore.id_map = {}
        IfcStore.guid_map = {}

        if not cls.get():
            return

        for obj in bpy.data.objects:
            if obj.library:
                continue

            bpy.msgbus.clear_by_owner(obj)

            element = cls.get_entity(obj)
            if not element:
                continue
            IfcStore.id_map[element.id()] = obj
            global_id = getattr(element, "GlobalId", None)
            if global_id:
                IfcStore.guid_map[global_id] = obj

            cls.setup_listeners(obj)

        for obj in bpy.data.materials:
            if obj.library:
                continue

            bpy.msgbus.clear_by_owner(obj)

            style = cls.get_entity(obj)
            if not style:
                continue

            IfcStore.id_map[style.id()] = obj
            cls.setup_listeners(obj)

        IfcStore.edited_objs = set()
        edited_objs = tool.Project.get_project_props().edited_objs
        for i in range(len(edited_objs))[::-1]:
            obj = edited_objs[i].obj
            if obj:
                IfcStore.edited_objs.add(obj)
            else:
                # Object was removed.
                edited_objs.remove(i)

    @classmethod
    def setup_listeners(cls, obj: IFC_CONNECTED_TYPE) -> None:
        if isinstance(obj, bpy.types.Object):
            bonsai.bim.handler.subscribe_to(
                obj, "active_material_index", bonsai.bim.handler.active_material_index_callback
            )
        bonsai.bim.handler.subscribe_to(obj, "name", bonsai.bim.handler.name_callback)

    @classmethod
    def link(
        cls,
        element: ifcopenshell.entity_instance,
        obj: Union[IFC_CONNECTED_TYPE, tool.Geometry.TYPES_WITH_MESH_PROPERTIES],
    ) -> None:
        IfcStore.link_element(element, obj)

    @classmethod
    def edit(cls, obj: bpy.types.Object) -> None:
        """Mark object as edited.

        Marking object as edited is an optimization mechanism - instead of saving
        changed geometry to IFC, we mark it as changed and then it's saved later
        (typically during project save or switch_representation(should_sync_changes_first=True)).

        Other caveat of using edited objects is that it won't have an effect for objects with openings,
        since we can't deduce non-openings representation from edited representation with openings.

        So, it's preferable not to use edited objects if object can have an opening. It's still can be used for spaces.
        """
        if obj in IfcStore.edited_objs:
            return
        edited_objs = tool.Project.get_project_props().edited_objs
        edited_objs.add().obj = obj
        IfcStore.edited_objs.add(obj)
        IfcStore.history_edit_object(obj, finish_editing=False)

    @classmethod
    def finish_edit(cls, obj: bpy.types.Object) -> None:
        """Unmark object as edited.

        Method is safe to use on an object that wasn't marked as edited before.
        """
        if obj not in IfcStore.edited_objs:
            return
        edited_objs = tool.Project.get_project_props().edited_objs
        edited_objs.remove(next(i for i, o in enumerate(edited_objs) if o.obj == obj))
        IfcStore.edited_objs.discard(obj)
        IfcStore.history_edit_object(obj, finish_editing=True)

    @classmethod
    def normalize_path(cls, path: Union[Path, str]) -> str:
        # Do not use `Path.resolve` as it will resolve symlinks too.
        return Path(os.path.normpath(path)).as_posix()

    @classmethod
    def resolve_uri(cls, uri: str | Path) -> str:
        """Get absolute path based on the active IFC file."""
        uri = Path(uri)
        if uri.is_absolute():
            return cls.normalize_path(uri)
        ifc_path = Path(cls.get_path())
        if ifc_path.is_file():
            ifc_path = ifc_path.parent
        if not str(uri):
            # TODO: When does it occur and why we return empty path in this case?
            return str(uri)
        return cls.normalize_path(ifc_path / uri)

    @classmethod
    def get_uri(cls, uri: str | Path, use_relative_path: bool) -> str:
        """Get path relative to the active IFC file, if ``use_relative_path`` is ``True``.

        ``use_relative_path`` is ``False``:
        - return ``uri`` as-is if it's absolute
        - raise ``ValueError`` if ``uri`` is relative (this condition indicates deeper code error)
        """
        uri = Path(uri)
        if not use_relative_path:
            if not uri.is_absolute():
                raise ValueError(f"Unexpected relative path in get_uri: '{uri}'.")
            return cls.normalize_path(uri)
        if not uri.is_absolute() or not (ifc_path := cls.get_path()):
            return cls.normalize_path(uri)
        ifc_path = Path(ifc_path)
        if uri.drive != ifc_path.drive:
            return cls.normalize_path(uri)
        if ifc_path.is_file():
            ifc_path = ifc_path.parent
        # Use `os.path.relpath` as it does support creating '..' paths.
        return cls.normalize_path(Path(os.path.relpath(uri, ifc_path)))

    @classmethod
    def unlink(
        cls, element: Optional[ifcopenshell.entity_instance] = None, obj: Optional[IFC_CONNECTED_TYPE] = None
    ) -> None:
        """See IfcStore.unlink_element doc for details."""
        IfcStore.unlink_element(element, obj)

    @classmethod
    def get_all_element_occurrences(cls, element: ifcopenshell.entity_instance) -> list[ifcopenshell.entity_instance]:
        if element.is_a("IfcElementType"):
            element_type = element
            occurrences = ifcopenshell.util.element.get_types(element_type)
        else:
            element_type = ifcopenshell.util.element.get_type(element)
            if element_type:
                occurrences = ifcopenshell.util.element.get_types(element_type)
            else:
                occurrences = [element]
        return occurrences

    class Operator:
        """IFC Operator class.

        Operators that edit any IFC data should inherit from this class
        and implement `_execute` method.

        `execute` method is already reserved by this class to keep track of the
        IFC changes for Undo system.
        """

        transaction_key = ""
        transaction_data: Union[Any, None] = None

        @final
        def execute(self, context) -> set[rna_enums.OperatorReturnItems]:
            IfcStore.execute_ifc_operator(self, context)
            return {"FINISHED"}

        # NOTE: this class can't inherit from abc.ABC to use abc.abstractmethod
        # because it conflicts with bpy.types.Operator.
        def _execute(self, context: bpy.types.Context) -> Union[None, set[rna_enums.OperatorReturnItems]]:
            raise NotImplementedError("IFC operator must implement _execute method.")
