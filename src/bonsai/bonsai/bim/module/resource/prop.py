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
import ifcopenshell.util.resource
from bonsai.bim.ifc import IfcStore
import bonsai.tool as tool
import bonsai.bim.module.pset.data
import bonsai.bim.module.resource.data
import bonsai.bim.module.sequence.data
from bonsai.bim.prop import StrProperty, Attribute
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

quantitytypes_enum = {}


def setup_quantity_types_enum():
    resources = ifcopenshell.util.resource.RESOURCES_TO_QUANTITIES
    for resource, quantities in resources.items():
        quantitytypes_enum[resource] = [(q, q, "") for q in quantities]


setup_quantity_types_enum()


def updateResourceName(self, context):
    props = context.scene.BIMResourceProperties
    if not props.is_resource_update_enabled:
        return
    tool.Ifc.run(
        "resource.edit_resource",
        resource=tool.Ifc.get().by_id(self.ifc_definition_id),
        attributes={"Name": self.name},
    )
    if props.active_resource_id == self.ifc_definition_id:
        attribute = props.resource_attributes.get("Name")
        attribute.string_value = self.name
    bonsai.bim.module.resource.data.refresh()
    tool.Sequence.refresh_task_resources()


def get_quantity_types(self, context):
    return quantitytypes_enum[self.active_resource_class]


def update_active_resource_index(self, context):
    bonsai.bim.module.pset.data.refresh()
    if self.should_show_resource_tools:
        tool.Resource.load_productivity_data()


def updateResourceUsage(self, context):
    if not context.scene.BIMResourceProperties.is_resource_update_enabled:
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


class ISODuration(PropertyGroup):
    name: StringProperty(name="Name")
    years: IntProperty(name="Years", default=0)
    months: IntProperty(name="Months", default=0)
    days: IntProperty(name="Days", default=0)
    hours: IntProperty(name="Hours", default=0)
    minutes: IntProperty(name="Minutes", default=0)
    seconds: IntProperty(name="Seconds", default=0)


class Resource(PropertyGroup):
    name: StringProperty(name="Name", update=updateResourceName)
    ifc_definition_id: IntProperty(name="IFC Definition ID")
    schedule_usage: FloatProperty(name="Schedule Usage", update=updateResourceUsage)
    has_children: BoolProperty(name="Has Children")
    is_expanded: BoolProperty(name="Is Expanded")
    level_index: IntProperty(name="Level Index")


class BIMResourceTreeProperties(PropertyGroup):
    resources: CollectionProperty(name="Resources", type=Resource)


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
        name="Editing Resource Type",
        items=(
            ("ATTRIBUTES", "", ""),
            ("USAGE", "", ""),
            ("COSTS", "", ""),
            ("QUANTITY", "", ""),
        ),
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


class BIMResourceProductivity(PropertyGroup):
    ifc_definition_id: IntProperty(name="IFC Definition ID")
    quantity_consumed: CollectionProperty(name="Duration", type=ISODuration)
    quantity_produced: FloatProperty(name="Quantity Produced")
    quantity_produced_name: StringProperty(name="Quantity Produced Name")
