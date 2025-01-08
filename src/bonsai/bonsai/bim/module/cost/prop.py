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
import ifcopenshell.api
import bonsai.tool as tool
from bonsai.bim.ifc import IfcStore
from bonsai.bim.module.classification.data import CostClassificationsData
from bonsai.bim.module.cost.data import CostSchedulesData, CostItemRatesData, CostItemQuantitiesData
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


def get_schedule_of_rates(self, context):
    if not CostItemRatesData.is_loaded:
        CostItemRatesData.load()
    return CostItemRatesData.data["schedule_of_rates"]


def update_schedule_of_rates(self, context):
    tool.Cost.load_schedule_of_rates_tree(schedule_of_rates=tool.Ifc.get().by_id(int(self.schedule_of_rates)))


def get_quantity_types(self, context):
    if not CostSchedulesData.is_loaded:
        CostSchedulesData.load()
    return CostSchedulesData.data["quantity_types"]


def get_product_quantity_names(self, context):
    if not CostItemQuantitiesData.is_loaded:
        CostItemQuantitiesData.load()
    return CostItemQuantitiesData.data["product_quantity_names"]


def get_process_quantity_names(self, context):
    if not CostItemQuantitiesData.is_loaded:
        CostItemQuantitiesData.load()
    return CostItemQuantitiesData.data["process_quantity_names"]


def get_resource_quantity_names(self, context):
    if not CostItemQuantitiesData.is_loaded:
        CostItemQuantitiesData.load()
    return CostItemQuantitiesData.data["resource_quantity_names"]


def update_active_cost_item_index(self, context):
    schedule = tool.Ifc.get().by_id(self.active_cost_schedule_id)
    if schedule.PredefinedType == "SCHEDULEOFRATES":
        tool.Cost.load_cost_item_types()
    else:
        tool.Cost.load_cost_item_quantities()
    CostClassificationsData.load()


def update_cost_item_identification(self, context):
    props = context.scene.BIMCostProperties
    if not props.is_cost_update_enabled or self.identification == "XXX":
        return
    self.file = IfcStore.get_file()
    ifcopenshell.api.run(
        "cost.edit_cost_item",
        self.file,
        **{"cost_item": self.file.by_id(self.ifc_definition_id), "attributes": {"Identification": self.identification}},
    )
    if props.active_cost_item_id == self.ifc_definition_id:
        attribute = props.cost_item_attributes.get("Identification")
        attribute.string_value = self.identification


def update_cost_item_name(self, context):
    props = context.scene.BIMCostProperties
    if not props.is_cost_update_enabled or self.name == "Unnamed":
        return
    self.file = IfcStore.get_file()
    ifcopenshell.api.run(
        "cost.edit_cost_item",
        self.file,
        **{"cost_item": self.file.by_id(self.ifc_definition_id), "attributes": {"Name": self.name}},
    )
    if props.active_cost_item_id == self.ifc_definition_id:
        attribute = props.cost_item_attributes.get("Name")
        attribute.string_value = self.name


def get_schedule_predefined_types(self, context):
    if not CostSchedulesData.is_loaded:
        CostSchedulesData.load()
    return CostSchedulesData.data["predefined_types"]


CURRENCIES_ENUM_ITEMS = (
    ("USD", "USD", "Dollar"),
    ("EUR", "EUR", "Euro"),
    ("GBP", "GBP", "Pound"),
    ("AUD", "AUD", "Australian Dollar"),
    ("CAD", "CAD", "Canadian Dollar"),
    ("CHF", "CHF", "Swiss Franc"),
    ("CNY", "CNY", "Chinese Yuan"),
    ("HKD", "HKD", "Hong Kong Dollar"),
    ("JPY", "JPY", "Japanese Yen"),
    ("NZD", "NZD", "New Zealand Dollar"),
    ("SEK", "SEK", "Swedish Krona"),
    ("KRW", "KRW", "South Korean Won"),
    ("SGD", "SGD", "Singapore Dollar"),
    ("NOK", "NOK", "Norwegian Krone"),
    ("MAD", "MAD", "Moroccan Dirham"),
    ("CUSTOM", "Custom currency", "Custom"),
)


class CostItem(PropertyGroup):
    name: StringProperty(name="Name", update=update_cost_item_name)
    identification: StringProperty(name="Identification", update=update_cost_item_identification)
    ifc_definition_id: IntProperty(name="IFC Definition ID")
    has_children: BoolProperty(name="Has Children")
    is_expanded: BoolProperty(name="Is Expanded")
    level_index: IntProperty(name="Level Index")


class CostItemQuantity(PropertyGroup):
    name: StringProperty(name="Name")
    ifc_definition_id: IntProperty(name="IFC Definition ID")
    total_quantity: FloatProperty(name="Total Quantity")
    unit_symbol: StringProperty(name="Unit Symbol")
    total_cost_quantity: FloatProperty(name="Total Quantity")


class CostItemType(PropertyGroup):
    name: StringProperty(name="Name")
    ifc_definition_id: IntProperty(name="IFC Definition ID")


def update_cost_item_parent(self, context):
    cost_item = tool.Cost.get_highlighted_cost_item()
    tool.Cost.toggle_cost_item_parent_change(cost_item=cost_item)


def update_active_cost_item_elements(self, context):
    bpy.ops.bim.load_cost_item_element_quantities()


def update_active_cost_item_tasks(self, context):
    bpy.ops.bim.load_cost_item_task_quantities()


def update_active_cost_item_resources(self, context):
    bpy.ops.bim.load_cost_item_resource_quantities()


class ScheduleColumn(PropertyGroup):
    schedule_id: IntProperty()


class BIMCostProperties(PropertyGroup):
    cost_schedule_predefined_types: EnumProperty(
        items=get_schedule_predefined_types, name="Predefined Type", default=None
    )
    is_cost_update_enabled: BoolProperty(name="Is Cost Update Enabled", default=True)
    cost_schedule_attributes: CollectionProperty(name="Cost Schedule Attributes", type=Attribute)
    is_editing: StringProperty(name="Is Editing")
    active_cost_schedule_id: IntProperty(name="Active Cost Schedule Id")
    cost_items: CollectionProperty(name="Cost Items", type=CostItem)
    active_cost_item_id: IntProperty(name="Active Cost Id")
    cost_item_editing_type: StringProperty(name="Cost Item Editing Type")
    active_cost_item_index: IntProperty(name="Active Cost Item Index", update=update_active_cost_item_index)
    cost_item_attributes: CollectionProperty(name="Task Attributes", type=Attribute)
    contracted_cost_items: StringProperty(name="Contracted Cost Items", default="[]")
    quantity_types: EnumProperty(items=get_quantity_types, name="Quantity Types")
    product_quantity_names: EnumProperty(items=get_product_quantity_names, name="Product Quantity Names")
    process_quantity_names: EnumProperty(items=get_process_quantity_names, name="Process Quantity Names")
    resource_quantity_names: EnumProperty(items=get_resource_quantity_names, name="Resource Quantity Names")
    active_cost_item_quantity_id: IntProperty(name="Active Cost Item Quantity Id")
    quantity_attributes: CollectionProperty(name="Quantity Attributes", type=Attribute)
    cost_types: EnumProperty(
        items=[
            ("FIXED", "Fixed", "The cost value is a fixed number"),
            ("SUM", "Sum", "The cost value is automatically derived from the sum of all nested cost items"),
            ("CATEGORY", "Category", "The cost value represents a single category"),
        ],
        name="Cost Types",
    )
    cost_category: StringProperty(name="Cost Category")
    fixed_cost_value: FloatProperty(name="Fixed Cost Value")
    active_cost_value_id: IntProperty(name="Active Cost Item Value Id")
    cost_value_editing_type: StringProperty(name="Cost Value Editing Type")
    cost_value_attributes: CollectionProperty(name="Cost Value Attributes", type=Attribute)
    cost_value_formula: StringProperty(name="Cost Value Formula")
    cost_column: StringProperty(name="Cost Column")
    should_show_column_ui: BoolProperty(
        name="Should Show Column UI",
        description="Display UI for adding cost schedule columns, column names represent a category for cost item values",
        default=False,
    )
    should_show_currency_ui: BoolProperty(name="Should Show Currency UI", default=False)
    columns: CollectionProperty(name="Active Schedule Columns", type=StrProperty)
    columns_storage: CollectionProperty(name="Columns", type=ScheduleColumn)
    active_column_index: IntProperty(name="Active Column Index")
    cost_item_products: CollectionProperty(name="Cost Item Products", type=CostItemQuantity)
    active_cost_item_product_index: IntProperty(name="Active Cost Item Product Index")
    cost_item_processes: CollectionProperty(name="Cost Item Processes", type=CostItemQuantity)
    active_cost_item_process_index: IntProperty(name="Active Cost Item Process Index")
    cost_item_resources: CollectionProperty(name="Cost Item Resources", type=CostItemQuantity)
    active_cost_item_resource_index: IntProperty(name="Active Cost Item Resource Index")
    cost_item_type_products: CollectionProperty(name="Cost Item Type Products", type=CostItemType)
    active_cost_item_type_product_index: IntProperty(name="Active Cost Item Type Product Index")
    schedule_of_rates: EnumProperty(
        items=get_schedule_of_rates, name="Schedule Of Rates", update=update_schedule_of_rates
    )
    cost_item_rates: CollectionProperty(name="Cost Item Rates", type=CostItem)
    active_cost_item_rate_index: IntProperty(name="Active Cost Rate Index")
    contracted_cost_item_rates: StringProperty(name="Contracted Cost Item Rates", default="[]")
    product_cost_items: CollectionProperty(name="Product Cost Items", type=CostItemQuantity)
    active_product_cost_item_index: IntProperty(name="Active Product Cost Item Index")
    enable_reorder: BoolProperty(name="Enable Reorder", default=False)
    show_nested_elements: BoolProperty(name="Show Nested Tasks", default=False, update=update_active_cost_item_elements)
    show_nested_tasks: BoolProperty(name="Show Nested Tasks", default=False, update=update_active_cost_item_tasks)
    show_nested_resources: BoolProperty(
        name="Show Nested Tasks", default=False, update=update_active_cost_item_resources
    )
    change_cost_item_parent: BoolProperty(name="Change Cost Item Parent", default=False, update=update_cost_item_parent)
    show_cost_item_operators: BoolProperty(name="Show Cost Item Operators", default=False)
    currency: EnumProperty(items=CURRENCIES_ENUM_ITEMS, name="Currencies")
    custom_currency: StringProperty(
        name="Custom Currency", default="USD", description="Custom Currency in ISO 4217 format"
    )
