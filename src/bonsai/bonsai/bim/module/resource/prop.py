# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2021, 2022, 2023 Dion Moult, Yassine Oualid <dion@thinkmoult.com>
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
import ifcopenshell.api
import ifcopenshell.api.resource
import ifcopenshell.util.resource
import bonsai.tool as tool
import bonsai.bim.module.pset.data
import bonsai.bim.module.resource.data
import bonsai.bim.module.sequence.data
from bonsai.bim.prop import Attribute, ISODuration
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
from typing import TYPE_CHECKING, Literal, get_args

quantitytypes_enum: dict[str, tool.Blender.BLENDER_ENUM_ITEMS] = {}


def setup_quantity_types_enum() -> None:
    resources = ifcopenshell.util.resource.RESOURCES_TO_QUANTITIES
    for resource, quantities in resources.items():
        quantitytypes_enum[resource] = [(q, q, "") for q in quantities]


setup_quantity_types_enum()


def updateResourceName(self: "Resource", context: object) -> None:
    props = tool.Resource.get_resource_props()
    if not props.is_resource_update_enabled:
        return
    ifc_file = tool.Ifc.get()
    ifcopenshell.api.resource.edit_resource(
        ifc_file,
        resource=ifc_file.by_id(self.ifc_definition_id),
        attributes={"Name": self.name},
    )
    if props.active_resource_id == self.ifc_definition_id:
        attribute = props.resource_attributes["Name"]
        attribute.string_value = self.name
    bonsai.bim.module.resource.data.refresh()
    tool.Sequence.refresh_task_resources()


def get_quantity_types(self: "BIMResourceProperties", context: object) -> tool.Blender.BLENDER_ENUM_ITEMS:
    return quantitytypes_enum[self.active_resource_class]


def update_active_resource_index(self: "BIMResourceProperties", context: object) -> None:
    bonsai.bim.module.pset.data.refresh()
    if self.should_show_resource_tools:
        tool.Resource.load_productivity_data()


def updateResourceUsage(self: "Resource", context: object) -> None:
    props = tool.Resource.get_resource_props()
    if not props.is_resource_update_enabled:
        return
    if not self.schedule_usage:
        return
    resource = tool.Ifc.get().by_id(self.ifc_definition_id)
    if resource.Usage and resource.Usage.ScheduleUsage == self.schedule_usage:
        return
    tool.Resource.run_edit_resource_time(resource, attributes={"ScheduleUsage": self.schedule_usage})
    tool.Sequence.load_task_properties()
    tool.Resource.load_resource_properties()
    tool.Sequence.refresh_task_resources()
    bonsai.bim.module.resource.data.refresh()
    bonsai.bim.module.sequence.data.refresh()
    bonsai.bim.module.pset.data.refresh()


class Resource(PropertyGroup):
    name: StringProperty(name="Name", update=updateResourceName)
    ifc_definition_id: IntProperty(name="IFC Definition ID")
    schedule_usage: FloatProperty(name="Schedule Usage", update=updateResourceUsage)
    has_children: BoolProperty(name="Has Children")
    is_expanded: BoolProperty(name="Is Expanded")
    level_index: IntProperty(name="Level Index")

    if TYPE_CHECKING:
        name: str
        ifc_definition_id: int
        schedule_usage: float
        has_children: bool
        is_expanded: bool
        level_index: int


# Separate from BIMResourceProperties - see BIMTaskTreeProperties note.
class BIMResourceTreeProperties(PropertyGroup):
    resources: CollectionProperty(name="Resources", type=Resource)

    if TYPE_CHECKING:
        resources: bpy.types.bpy_prop_collection_idprop[Resource]


EditingResourceType = Literal["ATTRIBUTES", "USAGE", "COSTS", "QUANTITY"]
CostType = Literal["FIXED", "SUM", "CATEGORY"]


class BIMResourceProperties(PropertyGroup):
    resource_attributes: CollectionProperty(name="Resource Attributes", type=Attribute)
    is_editing: BoolProperty(name="Is Editing")
    active_resource_index: IntProperty(name="Active Resource Index", update=update_active_resource_index)
    active_resource_id: IntProperty(name="Active Resource Id")
    active_resource_class: StringProperty(name="Active Resource Type")
    contracted_resources: StringProperty(name="Contracted Resources", default="[]")
    is_resource_update_enabled: BoolProperty(name="Is Resource Update Enabled", default=True)
    is_loaded: BoolProperty(name="Is Editing")
    active_resource_time_id: IntProperty(name="Active Resource Usage Id")
    resource_time_attributes: CollectionProperty(name="Resource Usage Attributes", type=Attribute)
    editing_resource_type: EnumProperty(
        name="Editing Resource Type", items=[(i, i, "") for i in get_args(EditingResourceType)]
    )
    cost_types: EnumProperty(
        items=[
            ("FIXED", "Fixed", "The cost value is a fixed number"),
            ("SUM", "Sum", "The cost value is automatically derived from the sum of all nested cost items"),
            ("CATEGORY", "Category", "The cost value represents a single category"),
        ],
        name="Cost Types",
    )
    cost_category: StringProperty(name="Cost Category")
    active_cost_value_id: IntProperty(name="Active Resource Cost Value Id")
    cost_value_editing_type: StringProperty(name="Cost Value Editing Type")
    cost_value_attributes: CollectionProperty(name="Cost Value Attributes", type=Attribute)
    cost_value_formula: StringProperty(name="Cost Value Formula")
    quantity_types: EnumProperty(items=get_quantity_types, name="Quantity Types")
    is_editing_quantity: BoolProperty(name="Is Editing Quantity")
    quantity_attributes: CollectionProperty(name="Quantity Attributes", type=Attribute)
    should_show_resource_tools: BoolProperty(name="Edit Productivity", update=update_active_resource_index)

    if TYPE_CHECKING:
        resource_attributes: bpy.types.bpy_prop_collection_idprop[Attribute]
        is_editing: bool
        active_resource_index: int
        active_resource_id: int
        active_resource_class: str
        contracted_resources: str
        is_resource_update_enabled: bool
        is_loaded: bool
        active_resource_time_id: int
        resource_time_attributes: bpy.types.bpy_prop_collection_idprop[Attribute]
        editing_resource_type: EditingResourceType
        cost_types: CostType
        cost_category: str
        active_cost_value_id: int
        cost_value_editing_type: str
        cost_value_attributes: bpy.types.bpy_prop_collection_idprop[Attribute]
        cost_value_formula: str
        quantity_types: str
        is_editing_quantity: bool
        quantity_attributes: bpy.types.bpy_prop_collection_idprop[Attribute]
        should_show_resource_tools: bool

    @property
    def tree(self) -> "BIMResourceTreeProperties":
        assert bpy.context.scene
        tprops = bpy.context.scene.BIMResourceTreeProperties  # pyright: ignore[reportAttributeAccessIssue]
        assert isinstance(tprops, BIMResourceTreeProperties)
        return tprops

    @property
    def productivity(self) -> "BIMResourceProductivity":
        assert bpy.context.scene
        productivity = bpy.context.scene.BIMResourceProductivity
        assert isinstance(productivity, BIMResourceProductivity)
        return productivity

    @property
    def active_resource(self) -> Resource | None:
        return tool.Blender.get_active_uilist_element(self.tree.resources, self.active_resource_index)


class BIMResourceProductivity(PropertyGroup):
    ifc_definition_id: IntProperty(name="IFC Definition ID")
    quantity_consumed: CollectionProperty(name="Duration", type=ISODuration)
    quantity_produced: FloatProperty(name="Quantity Produced")
    quantity_produced_name: StringProperty(name="Quantity Produced Name")

    if TYPE_CHECKING:
        ifc_definition_id: int
        quantity_consumed: bpy.types.bpy_prop_collection_idprop[ISODuration]
        quantity_produced: float
        quantity_produced_name: str
