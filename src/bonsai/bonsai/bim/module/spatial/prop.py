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
from bonsai.bim.prop import ObjProperty
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
import bonsai.bim.handler
import bonsai.core.geometry
import ifcopenshell
import ifcopenshell.util.element
import ifcopenshell.util.unit


def get_subelement_class(self, context):
    if not SpatialDecompositionData.is_loaded:
        SpatialDecompositionData.load()
    return SpatialDecompositionData.data["subelement_class"]


def update_elevation(self, context):
    try:
        elevation = float(self.elevation)
        if self.elevation != str(elevation):
            self.elevation = str(elevation)
            return
    except:
        elevation = 0
    if ifc_definition_id := self.ifc_definition_id:
        entity = tool.Ifc.get().by_id(ifc_definition_id)
        if obj := tool.Ifc.get_object(entity):
            unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
            obj.matrix_world[2][3] = elevation * unit_scale
            bonsai.core.geometry.edit_object_placement(tool.Ifc, tool.Geometry, tool.Surveyor, obj)


def update_name(self: "BIMContainer", context: bpy.types.Context) -> None:
    if ifc_definition_id := self.ifc_definition_id:
        tool.Ifc.get_object(tool.Ifc.get().by_id(ifc_definition_id)).name = self.name


def update_active_container_index(self: "BIMSpatialDecompositionProperties", context: bpy.types.Context) -> None:
    SpatialDecompositionData.data["subelement_class"] = SpatialDecompositionData.subelement_class()
    if tool.Blender.get_enum_safe(self, "subelement_class") is None:
        self.subelement_class = SpatialDecompositionData.data["subelement_class"][0][0]
    tool.Spatial.load_contained_elements()


def update_should_include_children(self: "BIMSpatialDecompositionProperties", context: bpy.types.Context) -> None:
    tool.Spatial.load_contained_elements()


def update_element_mode(self: "BIMSpatialDecompositionProperties", context: bpy.types.Context) -> None:
    tool.Spatial.load_contained_elements()


def update_grid_is_locked(self, context):
    if not tool.Ifc.get():
        return
    if tool.Ifc.get().schema in ("IFC2X3", "IFC4"):
        elements = tool.Ifc.get().by_type("IfcGrid") + tool.Ifc.get().by_type("IfcGridAxis")
    else:
        elements = tool.Ifc.get().by_type("IfcPositioningElement")
    for element in elements:
        if obj := tool.Ifc.get_object(element):
            if self.is_locked:
                tool.Geometry.lock_object(obj)
            else:
                tool.Geometry.unlock_object(obj)
    # Need to update ViewportData.mode.
    bonsai.bim.handler.refresh_ui_data()


def update_spatial_is_locked(self, context):
    if not tool.Ifc.get():
        return
    if tool.Ifc.get().schema == "IFC2X3":
        elements = tool.Ifc.get().by_type("IfcSpatialStructureElement")
    else:
        elements = tool.Ifc.get().by_type("IfcSpatialElement")
    for element in elements:
        if obj := tool.Ifc.get_object(element):
            if self.is_locked:
                tool.Geometry.lock_object(obj)
                obj.hide_select = True
            else:
                tool.Geometry.unlock_object(obj)
                obj.hide_select = False
    # Need to update ViewportData.mode.
    bonsai.bim.handler.refresh_ui_data()


def update_spatial_is_visible(self: "BIMSpatialDecompositionProperties", context: bpy.types.Context) -> None:
    bpy.ops.bim.toggle_spatial_elements(is_visible=self.is_visible)


def update_grid_is_visible(self: "BIMGridProperties", context: bpy.types.Context) -> None:
    bpy.ops.bim.toggle_grids(is_visible=self.is_visible)


def poll_container_obj(self: "BIMObjectSpatialProperties", container_obj: bpy.types.Object) -> bool:
    obj = self.id_data
    if (
        (container := tool.Ifc.get_entity(container_obj))
        and (tool.Ifc.get_entity(obj))
        and tool.Spatial.can_contain(container, obj)
    ):
        return True
    return False


class BIMObjectSpatialProperties(PropertyGroup):
    is_editing: BoolProperty(name="Is Editing")
    container_obj: PointerProperty(type=bpy.types.Object, name="Container", poll=poll_container_obj)


class BIMContainer(PropertyGroup):
    name: StringProperty(name="Name", update=update_name)
    ifc_class: StringProperty(name="IFC Class")
    description: StringProperty(name="Description")
    long_name: StringProperty(name="Long Name")
    elevation: StringProperty(name="Elevation", update=update_elevation)
    level_index: IntProperty(name="Level Index")
    has_children: BoolProperty(name="Has Children")
    is_expanded: BoolProperty(name="Is Expanded")
    ifc_definition_id: IntProperty(name="IFC Definition ID")


class Element(PropertyGroup):
    name: StringProperty(name="Name")
    ifc_class: StringProperty(name="Name", description="Type or element IFC class, empty if 'type' is 'CLASS'")
    identification: StringProperty(name="Identification", description="Identification if 'type' is 'CLASSIFICATION'")
    ifc_definition_id: IntProperty(
        name="IFC Definition ID",
        description="ID of the element type / occurrence. 0 if 'type' is 'CLASS' or if it's 'TYPE' but it represents untyped elements",
    )
    level: IntProperty(name="Level", default=0)
    has_children: BoolProperty(name="Has Children", default=False)
    total: IntProperty(name="Total")
    is_expanded: BoolProperty(name="Is Expanded", default=False)
    type: EnumProperty(
        name="Element Type",
        items=(
            ("CLASS", "CLASS", "CLASS"),
            ("TYPE", "TYPE", "TYPE"),
            ("CLASSIFICATION", "CLASSIFICATION", "CLASSIFICATION"),
            ("OCCURRENCE", "OCCURRENCE", "OCCURRENCE"),
        ),
    )


class BIMSpatialDecompositionProperties(PropertyGroup):
    is_locked: BoolProperty(
        name="Is Locked",
        description="Prevent all spatial elements from being edited, removed, duplicated",
        default=True,
        update=update_spatial_is_locked,
    )
    is_visible: BoolProperty(
        name="Is Visible",
        description="Show or hide spatial elements, such as buildings, sites, etc",
        default=True,
        update=update_spatial_is_visible,
    )
    container_filter: StringProperty(name="Container Filter", default="", options={"TEXTEDIT_UPDATE"})
    containers: CollectionProperty(name="Containers", type=BIMContainer)
    contracted_containers: StringProperty(name="Contracted containers", default="[]")
    active_container_index: IntProperty(name="Active Container Index", update=update_active_container_index)
    element_filter: StringProperty(name="Element Filter", default="", options={"TEXTEDIT_UPDATE"})
    elements: CollectionProperty(name="Elements", type=Element)
    expanded_elements: StringProperty(name="Expanded Elements", default="{}")
    active_element_index: IntProperty(name="Active Element Index")
    total_elements: IntProperty(name="Total Elements")
    element_mode: EnumProperty(
        name="Element Mode",
        items=(
            ("TYPE", "Class > Type > Occurrence", "Show a breakdown by IfcClass, relating type, and occurrence"),
            ("DECOMPOSITION", "Element Decomposition", "Show a breakdown by element decomposition"),
            ("CLASSIFICATION", "Element Classification", "Show a breakdown by element classification"),
        ),
        update=update_element_mode,
    )
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


class BIMGridProperties(PropertyGroup):
    is_locked: BoolProperty(
        name="Is Locked",
        description="Prevent all grids and grid axes from being edited, removed, duplicated",
        default=True,
        update=update_grid_is_locked,
    )
    is_visible: BoolProperty(
        name="Is Visible",
        description="Show or hide grids and grid axes",
        default=True,
        update=update_grid_is_visible,
    )
    grid_axes: CollectionProperty(name="Grid Axes", type=ObjProperty)
