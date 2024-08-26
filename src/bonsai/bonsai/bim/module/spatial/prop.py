# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
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

import bpy
from bonsai.bim.prop import StrProperty, Attribute
from bonsai.bim.module.spatial.data import SpatialDecompositionData
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
import bonsai.tool as tool
import ifcopenshell
import ifcopenshell.util.element


def get_subelement_class(self, context):
    if not SpatialDecompositionData.is_loaded:
        SpatialDecompositionData.load()
    return SpatialDecompositionData.data["subelement_class"]


def update_elevation(self, context):
    if ifc_definition_id := self.ifc_definition_id:
        entity = tool.Ifc.get().by_id(ifc_definition_id)
        obj = tool.Ifc.get_object(entity)
        if not obj:
            return
        obj.location.z = self.elevation


def update_name(self, context):
    if ifc_definition_id := self.ifc_definition_id:
        tool.Spatial.edit_container_name(tool.Ifc.get().by_id(ifc_definition_id), self.name)


def update_active_container_index(self, context):
    SpatialDecompositionData.data["subelement_class"] = SpatialDecompositionData.subelement_class()
    tool.Spatial.load_contained_elements()


def update_should_include_children(self, context):
    tool.Spatial.load_contained_elements()


def update_container_obj(self, context):
    if self.container_obj is None or not (obj := context.active_object):
        return
    if not (element := tool.Ifc.get_entity(self.container_obj)):
        self.container_obj = None
        return
    if tool.Spatial.can_contain(element, obj):
        return
    if (
        (container := ifcopenshell.util.element.get_container(element))
        and (container_obj := tool.Ifc.get_object(container))
        and tool.Spatial.can_contain(container, obj)
    ):
        self.container_obj = container_obj
        return
    self.container_obj = None


def poll_container_obj(self, obj):
    return obj is None or tool.Ifc.get_entity(obj)


class BIMObjectSpatialProperties(PropertyGroup):
    is_editing: BoolProperty(name="Is Editing")
    container_obj: PointerProperty(
        type=bpy.types.Object, name="Container", update=update_container_obj, poll=poll_container_obj
    )


class BIMContainer(PropertyGroup):
    name: StringProperty(name="Name", update=update_name)
    ifc_class: StringProperty(name="IFC Class")
    description: StringProperty(name="Description")
    long_name: StringProperty(name="Long Name")
    elevation: FloatProperty(name="Elevation", subtype="DISTANCE", update=update_elevation)
    level_index: IntProperty(name="Level Index")
    has_children: BoolProperty(name="Has Children")
    is_expanded: BoolProperty(name="Is Expanded")
    ifc_definition_id: IntProperty(name="IFC Definition ID")


class Element(PropertyGroup):
    name: StringProperty(name="Name")
    ifc_class: StringProperty(name="Name")
    is_class: BoolProperty(name="Is Class", default=False)
    is_type: BoolProperty(name="Is Type", default=False)
    ifc_definition_id: IntProperty(name="IFC Definition ID")
    total: IntProperty(name="Total")


class BIMSpatialDecompositionProperties(PropertyGroup):
    container_filter: StringProperty(name="Container Filter", default="", options={"TEXTEDIT_UPDATE"})
    containers: CollectionProperty(name="Containers", type=BIMContainer)
    contracted_containers: StringProperty(name="Contracted containers", default="[]")
    expanded_containers: StringProperty(name="Expanded containers", default="[]")
    active_container_index: IntProperty(name="Active Container Index", update=update_active_container_index)
    element_filter: StringProperty(name="Element Filter", default="", options={"TEXTEDIT_UPDATE"})
    elements: CollectionProperty(name="Elements", type=Element)
    active_element_index: IntProperty(name="Active Element Index")
    total_elements: IntProperty(name="Total Elements")
    subelement_class: bpy.props.EnumProperty(items=get_subelement_class, name="Subelement Class")
    default_container: IntProperty(name="Default Container", default=0)
    should_include_children: BoolProperty(
        name="Should Include Children", default=True, update=update_should_include_children
    )

    @property
    def active_container(self):
        if self.containers and self.active_container_index < len(self.containers):
            return self.containers[self.active_container_index]

    @property
    def active_element(self):
        if self.elements and self.active_element_index < len(self.elements):
            return self.elements[self.active_element_index]
