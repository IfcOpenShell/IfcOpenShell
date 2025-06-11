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
import ifcopenshell.api.cost
import bonsai.tool as tool
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
from typing import TYPE_CHECKING, Literal, Union


def get_schedule_of_rates(self: "BIMCostProperties", context: bpy.types.Context) -> tool.Blender.BLENDER_ENUM_ITEMS:
    if not CostItemRatesData.is_loaded:
        CostItemRatesData.load()
    # return CostItemRatesData.data["schedule_of_rates"]
    return CostItemRatesData.data["cost_schedules"]


def update_schedule_of_rates(self: "BIMCostProperties", context: bpy.types.Context) -> None:
    tool.Cost.load_schedule_of_rates_tree(schedule_of_rates=tool.Ifc.get().by_id(int(self.schedule_of_rates)))


def get_quantity_types(self: "BIMCostProperties", context: bpy.types.Context) -> tool.Blender.BLENDER_ENUM_ITEMS:
    if not CostSchedulesData.is_loaded:
        CostSchedulesData.load()
    return CostSchedulesData.data["quantity_types"]


def get_product_quantity_names(
    self: "BIMCostProperties", context: bpy.types.Context
) -> tool.Blender.BLENDER_ENUM_ITEMS:
    if not CostItemQuantitiesData.is_loaded:
        CostItemQuantitiesData.load()
    return CostItemQuantitiesData.data["product_quantity_names"]


def get_process_quantity_names(
    self: "BIMCostProperties", context: bpy.types.Context
) -> tool.Blender.BLENDER_ENUM_ITEMS:
    if not CostItemQuantitiesData.is_loaded:
        CostItemQuantitiesData.load()
    return CostItemQuantitiesData.data["process_quantity_names"]


def get_resource_quantity_names(
    self: "BIMCostProperties", context: bpy.types.Context
) -> tool.Blender.BLENDER_ENUM_ITEMS:
    if not CostItemQuantitiesData.is_loaded:
        CostItemQuantitiesData.load()
    return CostItemQuantitiesData.data["resource_quantity_names"]


def update_active_cost_item_index(self: "BIMCostProperties", context: bpy.types.Context) -> None:
    schedule = tool.Ifc.get().by_id(self.active_cost_schedule_id)
    if schedule.PredefinedType == "SCHEDULEOFRATES":
        tool.Cost.load_cost_item_types()
    else:
        tool.Cost.load_cost_item_quantities()
    CostClassificationsData.load()


def update_cost_item_identification(self: "CostItem", context: bpy.types.Context):
    props = tool.Cost.get_cost_props()
    if not props.is_cost_update_enabled or self.identification == "XXX":
        return
    ifc_file = tool.Ifc.get()
    ifcopenshell.api.cost.edit_cost_item(
        ifc_file,
        cost_item=ifc_file.by_id(self.ifc_definition_id),
        attributes={"Identification": self.identification},
    )
    if props.active_cost_item_id == self.ifc_definition_id:
        attribute = props.cost_item_attributes["Identification"]
        attribute.string_value = self.identification


def update_cost_item_name(self: "CostItem", context: bpy.types.Context) -> None:
    props = tool.Cost.get_cost_props()
    if not props.is_cost_update_enabled or self.name == "Unnamed":
        return
    ifc_file = tool.Ifc.get()
    ifcopenshell.api.cost.edit_cost_item(
        ifc_file,
        cost_item=ifc_file.by_id(self.ifc_definition_id),
        attributes={"Name": self.name},
    )
    if props.active_cost_item_id == self.ifc_definition_id:
        attribute = props.cost_item_attributes["Name"]
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

    if TYPE_CHECKING:
        name: str
        identification: str
        ifc_definition_id: int
        has_children: bool
        is_expanded: bool
        level_index: int


class CostItemQuantity(PropertyGroup):
    name: StringProperty(name="Name")
    ifc_definition_id: IntProperty(name="IFC Definition ID")
    total_quantity: FloatProperty(name="Total Quantity")
    unit_symbol: StringProperty(name="Unit Symbol")
    total_cost_quantity: FloatProperty(name="Total Quantity")

    if TYPE_CHECKING:
        name: str
        ifc_definition_id: int
        total_quantity: float
        unit_symbol: str
        total_cost_quantity: float


class CostSchedulesMapping(PropertyGroup):
    cost_schedule_id: IntProperty(name="cost_schedule_id")
    csv_filepath: StringProperty(name="filepath")

    if TYPE_CHECKING:
        cost_schedule_id: int
        csv_filepath: str


class CostItemType(PropertyGroup):
    name: StringProperty(name="Name")
    ifc_definition_id: IntProperty(name="IFC Definition ID")

    if TYPE_CHECKING:
        name: str
        ifc_definition_id: int


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

    if TYPE_CHECKING:
        schedule_id: int


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
    cost_schedule_files: CollectionProperty(name="Cost Schedule Files", type=CostSchedulesMapping)

    if TYPE_CHECKING:
        cost_schedule_predefined_types: str
        is_cost_update_enabled: bool
        cost_schedule_attributes: bpy.types.bpy_prop_collection_idprop[Attribute]
        is_editing: str
        active_cost_schedule_id: int
        cost_items: bpy.types.bpy_prop_collection_idprop[CostItem]
        active_cost_item_id: int
        cost_item_editing_type: str
        active_cost_item_index: int
        cost_item_attributes: bpy.types.bpy_prop_collection_idprop[Attribute]
        contracted_cost_items: str
        quantity_types: str
        product_quantity_names: str
        process_quantity_names: str
        resource_quantity_names: str
        active_cost_item_quantity_id: int
        quantity_attributes: bpy.types.bpy_prop_collection_idprop[Attribute]
        cost_types: Literal["FIXED", "SUM", "CATEGORY"]
        cost_category: str
        fixed_cost_value: float
        active_cost_value_id: int
        cost_value_editing_type: str
        cost_value_attributes: bpy.types.bpy_prop_collection_idprop[Attribute]
        cost_value_formula: str
        cost_column: str
        should_show_column_ui: bool
        should_show_currency_ui: bool
        columns: bpy.types.bpy_prop_collection_idprop[StrProperty]
        columns_storage: bpy.types.bpy_prop_collection_idprop[ScheduleColumn]
        active_column_index: int
        cost_item_products: bpy.types.bpy_prop_collection_idprop[CostItemQuantity]
        active_cost_item_product_index: int
        cost_item_processes: bpy.types.bpy_prop_collection_idprop[CostItemQuantity]
        active_cost_item_process_index: int
        cost_item_resources: bpy.types.bpy_prop_collection_idprop[CostItemQuantity]
        active_cost_item_resource_index: int
        cost_item_type_products: bpy.types.bpy_prop_collection_idprop[CostItemType]
        active_cost_item_type_product_index: int
        schedule_of_rates: str
        cost_item_rates: bpy.types.bpy_prop_collection_idprop[CostItem]
        active_cost_item_rate_index: int
        contracted_cost_item_rates: str
        product_cost_items: bpy.types.bpy_prop_collection_idprop[CostItemQuantity]
        active_product_cost_item_index: int
        enable_reorder: bool
        show_nested_elements: bool
        show_nested_tasks: bool
        show_nested_resources: bool
        change_cost_item_parent: bool
        show_cost_item_operators: bool
        currency: str
        custom_currency: str
        cost_schedule_files: bpy.types.bpy_prop_collection_idprop[CostSchedulesMapping]

    @property
    def active_cost_item(self) -> Union[CostItem, None]:
        return tool.Blender.get_active_uilist_element(self.cost_items, self.active_cost_item_index)
