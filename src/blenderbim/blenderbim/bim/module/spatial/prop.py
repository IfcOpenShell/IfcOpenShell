# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
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
from blenderbim.bim.prop import StrProperty, Attribute
from blenderbim.bim.module.spatial.data import SpatialData
from bpy.types import PropertyGroup
from bpy.props import (
    PointerProperty,
    StringProperty,
    EnumProperty,
    BoolProperty,
    IntProperty,
    FloatProperty,
    FloatVectorProperty,
    CollectionProperty,
)
import blenderbim.tool as tool
import blenderbim.core.geometry


def update_elevation(self, context):
    entity = tool.Ifc.get().by_id(self.active_container_id)
    obj = tool.Ifc.get_object(entity)
    if not obj:
        return
    obj.location.z = self.elevation


def update_active_container_index(self, context):
    self.active_container_id = self.containers[self.active_container_index].ifc_definition_id
    self.container_name = self.containers[self.active_container_index].name
    self.elevation = self.containers[self.active_container_index].elevation


def updateContainerName(self, context):
    props = context.scene.BIMSpatialManagerProperties
    if not props.is_container_update_enabled or self.name == "Unnamed":
        return
    tool.Spatial.edit_container_name(tool.Ifc.get().by_id(props.active_container_id), self.name)
    props.container_name = self.name


class SpatialElement(PropertyGroup):
    name: StringProperty(name="Name")
    long_name: StringProperty(name="Long Name")
    has_decomposition: BoolProperty(name="Has Decomposition")
    ifc_definition_id: IntProperty(name="IFC Definition ID")
    is_selected: BoolProperty(name="Is Selected")


class BIMSpatialProperties(PropertyGroup):
    containers: CollectionProperty(name="Containers", type=SpatialElement)
    active_container_index: IntProperty(name="Active Container Index")
    active_container_id: IntProperty(name="Active Container Id")


class BIMObjectSpatialProperties(PropertyGroup):
    is_editing: BoolProperty(name="Is Editing")


class BIMContainer(PropertyGroup):
    name: StringProperty(name="Name", update=updateContainerName)
    elevation: FloatProperty(name="Elevation")
    level_index: IntProperty(name="Level Index")
    has_children: BoolProperty(name="Has Children")
    is_expanded: BoolProperty(name="Is Expanded")
    ifc_definition_id: IntProperty(name="IFC Definition ID")


class BIMSpatialManagerProperties(PropertyGroup):
    containers: CollectionProperty(name="Containers", type=BIMContainer)
    contracted_containers: StringProperty(name="Contracted containers", default="[]")
    expanded_containers: StringProperty(name="Expanded containers", default="[]")
    active_container_index: IntProperty(name="Active Container Index", update=update_active_container_index)
    active_container_id: IntProperty(name="Active Container Id")
    container_name: StringProperty(name="Container Name")
    elevation: FloatProperty(name="Elevation", update=update_elevation)
    is_container_update_enabled: BoolProperty(name="Is Container Update Enabled", default=True)  # TODO:review
