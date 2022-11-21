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
import ifcopenshell.api
from blenderbim.bim.ifc import IfcStore
from ifcopenshell.api.resource.data import Data
import blenderbim.bim.module.pset.data
from blenderbim.bim.prop import StrProperty, Attribute
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


quantitytypes_enum = []


def purge():
    global quantitytypes_enum
    quantitytypes_enum = []


def updateResourceName(self, context):
    props = context.scene.BIMResourceProperties
    if not props.is_resource_update_enabled or self.name == "Unnamed":
        return
    self.file = IfcStore.get_file()
    ifcopenshell.api.run(
        "resource.edit_resource",
        self.file,
        **{"resource": self.file.by_id(self.ifc_definition_id), "attributes": {"Name": self.name}},
    )
    Data.load(IfcStore.get_file())
    if props.active_resource_id == self.ifc_definition_id:
        attribute = props.resource_attributes.get("Name")
        attribute.string_value = self.name


def get_quantity_types(self, context):
    global quantitytypes_enum
    if len(quantitytypes_enum) == 0 and IfcStore.get_schema():
        quantitytypes_enum.extend(
            [
                (t.name(), t.name(), "")
                for t in IfcStore.get_schema().declaration_by_name("IfcPhysicalSimpleQuantity").subtypes()
            ]
        )
    return quantitytypes_enum


def update_active_resource_index(self, context):
    blenderbim.bim.module.pset.data.refresh()


class Resource(PropertyGroup):
    name: StringProperty(name="Name", update=updateResourceName)
    ifc_definition_id: IntProperty(name="IFC Definition ID")
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
    contracted_resources: StringProperty(name="Contracted Resources", default="[]")
    is_resource_update_enabled: BoolProperty(name="Is Resource Update Enabled", default=True)
    is_loaded: BoolProperty(name="Is Editing")
    active_resource_time_id: IntProperty(name="Active Resource Usage Id")
    resource_time_attributes: CollectionProperty(name="Resource Usage Attributes", type=Attribute)
    editing_resource_type: StringProperty(name="Editing Resource Type")
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
