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
import ifcopenshell.util.element


def refresh():
    SpatialData.is_loaded = False


class SpatialData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.data = {
            "is_editing": bpy.context.active_object.BIMObjectSpatialProperties.is_editing,
            "parent_container_id": cls.get_parent_container_id(),
            "container_id": cls.get_container_id(),
            "container_list_settings": cls.get_container_list_settings(),
            "is_contained": cls.is_contained(),
            "is_directly_contained": cls.is_directly_contained(),
            "label": cls.get_label(),
        }
        cls.is_loaded = True

    @classmethod
    def get_parent_container_id(cls):
        container_id = bpy.context.scene.BIMSpatialProperties.active_container_id
        if not container_id:
            return
        container = tool.Ifc.get().by_id(container_id)
        if container.is_a("IfcProject"):
            return
        return container.Decomposes[0].RelatingObject.id()

    @classmethod
    def get_container_id(cls):
        props = bpy.context.scene.BIMSpatialProperties
        try:
            return props.containers[props.active_container_index].ifc_definition_id
        except:
            return 0

    @classmethod
    def get_container_list_settings(cls):
        props = bpy.context.scene.BIMSpatialProperties
        return ["", props, "containers", props, "active_container_id"]

    @classmethod
    def is_contained(cls):
        return ifcopenshell.util.element.get_container(tool.Ifc.get_entity(bpy.context.active_object))

    @classmethod
    def get_label(cls):
        container = ifcopenshell.util.element.get_container(tool.Ifc.get_entity(bpy.context.active_object))
        if container:
            label = f"{container.is_a()}/{container.Name or ''}"
            if not cls.is_directly_contained():
                label += "*"
            return label

    @classmethod
    def is_directly_contained(cls):
        return bool(getattr(tool.Ifc.get_entity(bpy.context.active_object), "ContainedInStructure"))
