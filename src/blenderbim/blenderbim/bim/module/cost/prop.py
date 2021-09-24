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
from ifcopenshell.api.cost.data import Data
from ifcopenshell.api.pset.data import Data as PsetData
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
productquantitynames_enum = []
productquantitynames_count = []
processquantitynames_enum = []
processquantitynames_id = 0
resourcequantitynames_enum = []
resourcequantitynames_id = 0
scheduleofrates_enum = []


def purge():
    global quantitytypes_enum
    global productquantitynames_enum
    global productquantitynames_count
    global processquantitynames_enum
    global processquantitynames_id
    global resourcequantitynames_enum
    global resourcequantitynames_id
    global scheduleofrates_enum
    quantitytypes_enum = []
    productquantitynames_enum = []
    productquantitynames_count = []
    processquantitynames_enum = []
    processquantitynames_id = 0
    resourcequantitynames_enum = []
    resourcequantitynames_id = 0
    scheduleofrates_enum = []


def get_schedule_of_rates(self, context):
    global scheduleofrates_enum
    if len(scheduleofrates_enum) == 0:
        scheduleofrates_enum.extend(
            (str(ifc_definition_id), schedule["Name"] or "Unnamed", "")
            for ifc_definition_id, schedule in Data.cost_schedules.items()
            if schedule["PredefinedType"] == "SCHEDULEOFRATES"
        )
    return scheduleofrates_enum


def update_schedule_of_rates(self, context):
    bpy.ops.bim.load_schedule_of_rates(cost_schedule=int(self.schedule_of_rates))


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


def get_product_quantity_names(self, context):
    global productquantitynames_enum
    global productquantitynames_count
    ifc_file = IfcStore.get_file()
    total_selected_objects = len(context.selected_objects)
    if total_selected_objects != productquantitynames_count or total_selected_objects == 1:
        productquantitynames_enum = []
        productquantitynames_count = total_selected_objects
        names = set()
        for obj in context.selected_objects:
            element_id = obj.BIMObjectProperties.ifc_definition_id
            if not element_id:
                continue
            potential_names = set()
            if element_id not in PsetData.products:
                PsetData.load(ifc_file, element_id)
            for qto_id in PsetData.products[element_id]["qtos"]:
                qto = PsetData.qtos[qto_id]
                [potential_names.add(PsetData.properties[p]["Name"]) for p in qto["Properties"]]
            names = names.intersection(potential_names) if names else potential_names
        productquantitynames_enum.extend([(n, n, "") for n in names])
    return productquantitynames_enum


def get_process_quantity_names(self, context):
    global processquantitynames_enum
    global processquantitynames_id
    ifc_file = IfcStore.get_file()
    active_task_index = context.scene.BIMWorkScheduleProperties.active_task_index
    total_tasks = len(context.scene.BIMTaskTreeProperties.tasks)
    if not total_tasks or active_task_index >= total_tasks:
        return []
    ifc_definition_id = context.scene.BIMTaskTreeProperties.tasks[active_task_index].ifc_definition_id
    if processquantitynames_id != ifc_definition_id:
        processquantitynames_enum = []
        processquantitynames_id = ifc_definition_id
        names = set()
        if ifc_definition_id not in PsetData.products:
            PsetData.load(ifc_file, ifc_definition_id)
        for qto_id in PsetData.products[ifc_definition_id]["qtos"]:
            qto = PsetData.qtos[qto_id]
            [names.add(PsetData.properties[p]["Name"]) for p in qto["Properties"]]
        processquantitynames_enum.extend([(n, n, "") for n in names])
    return processquantitynames_enum


def get_resource_quantity_names(self, context):
    global resourcequantitynames_enum
    global resourcequantitynames_id
    ifc_file = IfcStore.get_file()
    active_resource_index = context.scene.BIMResourceProperties.active_resource_index
    total_resources = len(context.scene.BIMResourceTreeProperties.resources)
    if not total_resources or active_resource_index >= total_resources:
        return []
    ifc_definition_id = context.scene.BIMResourceTreeProperties.resources[active_resource_index].ifc_definition_id
    if resourcequantitynames_id != ifc_definition_id:
        resourcequantitynames_enum = []
        resourcequantitynames_id = ifc_definition_id
        names = set()
        if ifc_definition_id not in PsetData.products:
            PsetData.load(ifc_file, ifc_definition_id)
        for qto_id in PsetData.products[ifc_definition_id]["qtos"]:
            qto = PsetData.qtos[qto_id]
            [names.add(PsetData.properties[p]["Name"]) for p in qto["Properties"]]
        resourcequantitynames_enum.extend([(n, n, "") for n in names])
    return resourcequantitynames_enum


def update_active_cost_item_index(self, context):
    if Data.cost_schedules[self.active_cost_schedule_id]["PredefinedType"] == "SCHEDULEOFRATES":
        bpy.ops.bim.load_cost_item_types()
    else:
        bpy.ops.bim.load_cost_item_quantities()


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
    Data.load(self.file)
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
    Data.load(IfcStore.get_file())
    if props.active_cost_item_id == self.ifc_definition_id:
        attribute = props.cost_item_attributes.get("Name")
        attribute.string_value = self.name


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


class CostItemType(PropertyGroup):
    name: StringProperty(name="Name")
    ifc_definition_id: IntProperty(name="IFC Definition ID")


class BIMCostProperties(PropertyGroup):
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
    active_cost_value_id: IntProperty(name="Active Cost Item Value Id")
    cost_value_editing_type: StringProperty(name="Cost Value Editing Type")
    cost_value_attributes: CollectionProperty(name="Cost Value Attributes", type=Attribute)
    cost_value_formula: StringProperty(name="Cost Value Formula")
    cost_column: StringProperty(name="Cost Column")
    should_show_column_ui: BoolProperty(name="Should Show Column UI", default=False)
    columns: CollectionProperty(name="Columns", type=StrProperty)
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
