# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2023 Dion Moult <dion@thinkmoult.com>
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
import bpy
import bonsai.core.tool
import bonsai.tool as tool
import ifcopenshell.util.element
from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
    from bonsai.bim.module.nest.prop import BIMNestProperties, BIMObjectNestProperties


class Nest(bonsai.core.tool.Nest):
    @classmethod
    def get_nest_props(cls) -> BIMNestProperties:
        return bpy.context.scene.BIMNestProperties

    @classmethod
    def get_object_nest_props(cls, obj: bpy.types.Object) -> BIMObjectNestProperties:
        return obj.BIMObjectNestProperties

    @classmethod
    def can_nest(cls, relating_obj, related_obj):
        relating_object = tool.Ifc.get_entity(relating_obj)
        related_object = tool.Ifc.get_entity(related_obj)
        if not relating_object or not related_object:
            return False
        if relating_object.is_a("IfcElement") and related_object.is_a("IfcElement"):
            return True
        return False

    @classmethod
    def disable_editing(cls, obj: bpy.types.Object) -> None:
        props = cls.get_object_nest_props(obj)
        props.is_editing = False

    @classmethod
    def enable_editing(cls, obj: bpy.types.Object) -> None:
        props = cls.get_object_nest_props(obj)
        props.is_editing = True

    @classmethod
    def get_container(cls, element: ifcopenshell.entity_instance) -> Union[ifcopenshell.entity_instance, None]:
        return ifcopenshell.util.element.get_container(element)

    @classmethod
    def get_relating_object(
        cls, related_element: ifcopenshell.entity_instance
    ) -> Union[ifcopenshell.entity_instance, None]:
        return ifcopenshell.util.element.get_nest(related_element)

    @classmethod
    def get_components_recursively(cls, element: ifcopenshell.entity_instance) -> set[ifcopenshell.entity_instance]:
        """Get elements components recursively, resulting set includes `element`."""
        components = set()
        queue = {element}
        while queue:
            element = queue.pop()
            queue.update(new_components := set(ifcopenshell.util.element.get_components(element)))
            components.update(new_components)
        return components

    @classmethod
    def get_nest_mode(cls) -> bool:
        props = cls.get_nest_props()
        return props.in_nest_mode

    @classmethod
    def enable_nest_mode(cls, active_object: bpy.types.Object):
        context = bpy.context
        props = cls.get_nest_props()

        element = tool.Ifc.get_entity(active_object)
        if not element:
            return {"FINISHED"}
        nest = ifcopenshell.util.element.get_nest(element)
        components = ifcopenshell.util.element.get_components(element)
        if not nest and not components:
            return {"FINISHED"}
        if not components:
            components = ifcopenshell.util.element.get_components(nest)
        if components:
            props.editing_nest = tool.Ifc.get_object(nest) if nest else tool.Ifc.get_object(element)
            components_objs = [tool.Ifc.get_object(component) for component in components]
            objs = []
            visible_objects = tool.Raycast.get_visible_objects(context)
            for obj in visible_objects:
                if obj.visible_in_viewport_get(context.space_data):
                    objs.append(obj.original)
            for obj in objs:
                if obj.original not in components_objs:
                    if obj == props.editing_nest:
                        continue
                    not_editing_obj = props.not_editing_objects.add()
                    not_editing_obj.obj = obj.original
                    not_editing_obj.previous_display_type = obj.original.display_type
                    obj.original.display_type = "WIRE"
                else:
                    editing_obj = props.editing_objects.add()
                    editing_obj.obj = obj.original

        props.in_nest_mode = True
        return {"FINISHED"}

    @classmethod
    def disable_nest_mode(cls):
        context = bpy.context
        props = context.scene.BIMNestProperties
        for obj_prop in props.not_editing_objects:
            obj = obj_prop.obj
            obj.original.display_type = obj_prop.previous_display_type
            element = tool.Ifc.get_entity(obj)
            if not element:
                continue

        components = ifcopenshell.util.element.get_components(tool.Ifc.get_entity(props.editing_nest))
        objs = [tool.Ifc.get_object(component) for component in components]
        if context.space_data.local_view:
            bpy.ops.view3d.localview()

        props.in_nest_mode = False
        props.not_editing_objects.clear()
        props.editing_objects.clear()
        props.editing_nest = None
