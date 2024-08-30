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
from bonsai.bim.ifc import IfcStore, IFC_CONNECTED_TYPE
from typing import Optional, Union, Any, final, Literal


class Ifc(bonsai.core.tool.Ifc):
    OBJECT_TYPE = Literal[
        "Object",
        "Material",
        "MaterialSet",
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
    def get_path(cls) -> str:
        return IfcStore.path

    @classmethod
    def get_schema(cls) -> ifcopenshell.util.schema.IFC_SCHEMA:
        if IfcStore.get_file():
            return IfcStore.get_file().schema

    @classmethod
    def is_edited(cls, obj: bpy.types.Object) -> bool:
        return list(obj.scale) != [1.0, 1.0, 1.0] or obj in IfcStore.edited_objs

    @classmethod
    def is_moved(cls, obj: bpy.types.Object) -> bool:
        element = cls.get_entity(obj)
        if not element or element.is_a("IfcTypeProduct") or element.is_a("IfcProject"):
            return False
        if not obj.BIMObjectProperties.location_checksum:
            return True  # Let's be conservative
        loc_check = np.frombuffer(eval(obj.BIMObjectProperties.location_checksum))
        rot_check = np.frombuffer(eval(obj.BIMObjectProperties.rotation_checksum))
        loc_real = np.array(obj.matrix_world.translation).flatten()
        rot_real = np.array(obj.matrix_world.to_3x3()).flatten()
        if np.allclose(loc_check, loc_real, atol=1e-4) and np.allclose(rot_check, rot_real, atol=1e-2):
            return False
        return True

    @classmethod
    def schema(cls) -> ifcopenshell_wrapper.schema_definition:
        return IfcStore.get_schema()

    @classmethod
    def get_entity(cls, obj: IFC_CONNECTED_TYPE) -> Union[ifcopenshell.entity_instance, None]:
        """Get linked IFC entity based on obj's BIMObjectProperties.ifc_definition_id.

        Return None if object is not linked to IFC or it's linked to non-existent element.
        """
        ifc = IfcStore.get_file()
        if not ifc:
            return

        props = None
        if isinstance(obj, bpy.types.Object):
            props = obj.BIMObjectProperties
        elif isinstance(obj, bpy.types.Material):
            props = obj.BIMStyleProperties

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
    def get_object(cls, element: ifcopenshell.entity_instance) -> IFC_CONNECTED_TYPE:
        return IfcStore.get_element(element.id())

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

            bonsai.bim.handler.subscribe_to(obj, "name", bonsai.bim.handler.name_callback)
            bonsai.bim.handler.subscribe_to(
                obj, "active_material_index", bonsai.bim.handler.active_material_index_callback
            )

        for obj in bpy.data.materials:
            if obj.library:
                continue

            bpy.msgbus.clear_by_owner(obj)

            material = cls.get_entity(obj)
            style = tool.Style.get_style(obj)
            if material:
                IfcStore.id_map[material.id()] = obj
            if style:
                IfcStore.id_map[style.id()] = obj

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
        """Mark object as edited."""
        IfcStore.edited_objs.add(obj)

    @classmethod
    def finish_edit(cls, obj: bpy.types.Object) -> None:
        """Unmark object as edited.

        Method is safe to use on an object that wasn't marked as edited before.
        """
        IfcStore.edited_objs.discard(obj)

    @classmethod
    def resolve_uri(cls, uri: str) -> str:
        if os.path.isabs(uri):
            return uri
        ifc_path = cls.get_path()
        if os.path.isfile(ifc_path):
            ifc_path = os.path.dirname(ifc_path)
        return (uri if not uri else os.path.join(ifc_path, uri)).replace("\\", "/")

    @classmethod
    def get_relative_uri(cls, uri):
        if not os.path.isabs(uri):
            return uri
        ifc_path = cls.get_path()
        if os.path.isfile(ifc_path):
            ifc_path = os.path.dirname(ifc_path)
        return os.path.relpath(uri, ifc_path).replace("\\", "/")

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

        @final
        def execute(self, context):
            IfcStore.execute_ifc_operator(self, context)
            bonsai.bim.handler.refresh_ui_data()
            return {"FINISHED"}

        # NOTE: this class can't inherit from abc.ABC to use abc.abstractmethod
        # because it conflicts with bpy.types.Operator.
        def _execute(self, context: bpy.types.Context) -> None:
            raise NotImplementedError("IFC operator must implement _execute method.")
