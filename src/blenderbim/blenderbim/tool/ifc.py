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

import os
import bpy
import numpy as np
import ifcopenshell.api
import ifcopenshell.util.element
import blenderbim.core.tool
import blenderbim.bim.handler
import blenderbim.tool as tool
from blenderbim.bim.ifc import IfcStore, IFC_CONNECTED_TYPE
from typing import Optional, Union, Any


class Ifc(blenderbim.core.tool.Ifc):
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
    def get_schema(cls) -> str:
        if IfcStore.get_file():
            return IfcStore.get_file().schema

    @classmethod
    def has_changed_shading(cls, obj: bpy.types.Material) -> bool:
        checksum = obj.BIMMaterialProperties.shading_checksum
        return checksum != repr(np.array(obj.diffuse_color).tobytes())

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
    def schema(cls):
        return IfcStore.get_schema()

    @classmethod
    def get_entity(cls, obj: IFC_CONNECTED_TYPE) -> ifcopenshell.entity_instance:
        ifc = IfcStore.get_file()
        props = getattr(obj, "BIMObjectProperties", None)
        if ifc and props and props.ifc_definition_id:
            try:
                return IfcStore.get_file().by_id(props.ifc_definition_id)
            except:
                pass

    @classmethod
    def get_entity_by_id(cls, entity_id) -> Union[ifcopenshell.entity_instance, None]:
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

            blenderbim.bim.handler.subscribe_to(obj, "name", blenderbim.bim.handler.name_callback)
            blenderbim.bim.handler.subscribe_to(
                obj, "active_material_index", blenderbim.bim.handler.active_material_index_callback
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

            blenderbim.bim.handler.subscribe_to(obj, "name", blenderbim.bim.handler.name_callback)
            blenderbim.bim.handler.subscribe_to(obj, "diffuse_color", blenderbim.bim.handler.color_callback)

    @classmethod
    def link(cls, element: ifcopenshell.entity_instance, obj: IFC_CONNECTED_TYPE) -> None:
        IfcStore.link_element(element, obj)

    @classmethod
    def edit(cls, obj: bpy.types.Object) -> None:
        IfcStore.edited_objs.add(obj)

    @classmethod
    def finish_edit(cls, obj: bpy.types.Object) -> None:
        try:
            IfcStore.edited_objs.remove(obj)
        except:
            pass

    @classmethod
    def resolve_uri(cls, uri):
        if os.path.isabs(uri):
            return uri
        ifc_path = cls.get_path()
        if os.path.isfile(ifc_path):
            ifc_path = os.path.dirname(ifc_path)
        return (uri if not uri or os.path.isabs(uri) else os.path.join(ifc_path, uri)).replace("\\", "/")

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
        def execute(self, context):
            IfcStore.execute_ifc_operator(self, context)
            blenderbim.bim.handler.refresh_ui_data()
            return {"FINISHED"}
