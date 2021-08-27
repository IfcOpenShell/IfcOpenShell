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

import os
import bpy
import json
import time
import ifcopenshell.api
import blenderbim.bim.helper
from blenderbim.bim.module.cost.prop import purge
from blenderbim.bim.ifc import IfcStore
from bpy_extras.io_utils import ImportHelper
from ifcopenshell.api.cost.data import Data
from ifcopenshell.api.unit.data import Data as UnitData
from ifcopenshell.api.resource.data import Data as ResourceData


class AddCostSchedule(bpy.types.Operator):
    bl_idname = "bim.add_cost_schedule"
    bl_label = "Add Cost Schedule"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        ifcopenshell.api.run("cost.add_cost_schedule", IfcStore.get_file())
        Data.load(IfcStore.get_file())
        return {"FINISHED"}


class EditCostSchedule(bpy.types.Operator):
    bl_idname = "bim.edit_cost_schedule"
    bl_label = "Edit Cost Schedule"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        props = context.scene.BIMCostProperties
        attributes = blenderbim.bim.helper.export_attributes(props.cost_schedule_attributes)
        self.file = IfcStore.get_file()
        ifcopenshell.api.run(
            "cost.edit_cost_schedule",
            self.file,
            **{"cost_schedule": self.file.by_id(props.active_cost_schedule_id), "attributes": attributes},
        )
        Data.load(IfcStore.get_file())
        purge()
        bpy.ops.bim.disable_editing_cost_schedule()
        return {"FINISHED"}


class RemoveCostSchedule(bpy.types.Operator):
    bl_idname = "bim.remove_cost_schedule"
    bl_label = "Remove Cost Schedule"
    bl_options = {"REGISTER", "UNDO"}
    cost_schedule: bpy.props.IntProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        ifcopenshell.api.run(
            "cost.remove_cost_schedule",
            IfcStore.get_file(),
            cost_schedule=IfcStore.get_file().by_id(self.cost_schedule),
        )
        Data.load(IfcStore.get_file())
        return {"FINISHED"}


class EnableEditingCostSchedule(bpy.types.Operator):
    bl_idname = "bim.enable_editing_cost_schedule"
    bl_label = "Enable Editing Cost Schedule"
    bl_options = {"REGISTER", "UNDO"}
    cost_schedule: bpy.props.IntProperty()

    def execute(self, context):
        self.props = context.scene.BIMCostProperties
        self.props.active_cost_schedule_id = self.cost_schedule
        self.props.cost_schedule_attributes.clear()
        self.enable_editing_cost_schedule()
        self.props.is_editing = "COST_SCHEDULE"
        return {"FINISHED"}

    def enable_editing_cost_schedule(self):
        data = Data.cost_schedules[self.cost_schedule]
        blenderbim.bim.helper.import_attributes(
            "IfcCostSchedule", self.props.cost_schedule_attributes, data, self.import_attributes
        )

    def import_attributes(self, name, prop, data):
        if name in ["SubmittedOn", "UpdateDate"]:
            prop.string_value = "" if prop.is_null else data[name].isoformat()
            return True


class EnableEditingCostItems(bpy.types.Operator):
    bl_idname = "bim.enable_editing_cost_items"
    bl_label = "Enable Editing Cost Items"
    bl_options = {"REGISTER", "UNDO"}
    cost_schedule: bpy.props.IntProperty()

    def execute(self, context):
        if context.preferences.addons["blenderbim"].preferences.should_play_chaching_sound:
            self.play_chaching_sound()  # lol
        self.props = context.scene.BIMCostProperties
        self.props.is_cost_update_enabled = False
        self.props.active_cost_schedule_id = self.cost_schedule
        self.props.cost_items.clear()

        self.contracted_cost_items = json.loads(self.props.contracted_cost_items)
        for related_object_id in Data.cost_schedules[self.cost_schedule]["Controls"]:
            self.create_new_cost_item_li(related_object_id, 0)
        self.props.is_editing = "COST_ITEMS"
        self.props.is_cost_update_enabled = True
        return {"FINISHED"}

    def play_chaching_sound(self):
        # TODO: make pitch higher as costs rise
        try:
            import aud

            device = aud.Device()
            # chaching.mp3 is by Lucish_ CC-BY-3.0 https://freesound.org/people/Lucish_/sounds/554841/
            sound = aud.Sound(os.path.join(context.scene.BIMProperties.data_dir, "chaching.mp3"))
            handle = device.play(sound)
            sound_buffered = aud.Sound.buffer(sound)
            handle_buffered = device.play(sound_buffered)
            handle.stop()
            handle_buffered.stop()
        except:
            pass  # ah well

    def create_new_cost_item_li(self, related_object_id, level_index):
        cost_item = Data.cost_items[related_object_id]
        new = self.props.cost_items.add()
        new.ifc_definition_id = related_object_id
        new.name = cost_item["Name"] or "Unnamed"
        new.identification = cost_item["Identification"] or "XXX"
        new.is_expanded = related_object_id not in self.contracted_cost_items
        new.level_index = level_index
        if cost_item["IsNestedBy"]:
            new.has_children = True
            if new.is_expanded:
                for related_object_id in cost_item["IsNestedBy"]:
                    self.create_new_cost_item_li(related_object_id, level_index + 1)


class DisableEditingCostSchedule(bpy.types.Operator):
    bl_idname = "bim.disable_editing_cost_schedule"
    bl_label = "Disable Editing Cost Schedule"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        context.scene.BIMCostProperties.active_cost_schedule_id = 0
        return {"FINISHED"}


class AddSummaryCostItem(bpy.types.Operator):
    bl_idname = "bim.add_summary_cost_item"
    bl_label = "Add Cost Item"
    bl_options = {"REGISTER", "UNDO"}
    cost_schedule: bpy.props.IntProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        props = context.scene.BIMCostProperties
        self.file = IfcStore.get_file()
        ifcopenshell.api.run("cost.add_cost_item", self.file, **{"cost_schedule": self.file.by_id(self.cost_schedule)})
        Data.load(self.file)
        bpy.ops.bim.enable_editing_cost_items(cost_schedule=self.cost_schedule)
        return {"FINISHED"}


class AddCostItem(bpy.types.Operator):
    bl_idname = "bim.add_cost_item"
    bl_label = "Add Cost Item"
    bl_options = {"REGISTER", "UNDO"}
    cost_item: bpy.props.IntProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        props = context.scene.BIMCostProperties
        self.file = IfcStore.get_file()
        ifcopenshell.api.run("cost.add_cost_item", self.file, **{"cost_item": self.file.by_id(self.cost_item)})
        Data.load(self.file)
        bpy.ops.bim.enable_editing_cost_items(cost_schedule=props.active_cost_schedule_id)
        return {"FINISHED"}


class ExpandCostItem(bpy.types.Operator):
    bl_idname = "bim.expand_cost_item"
    bl_label = "Expand Cost Item"
    bl_options = {"REGISTER", "UNDO"}
    cost_item: bpy.props.IntProperty()

    def execute(self, context):
        props = context.scene.BIMCostProperties
        self.file = IfcStore.get_file()
        contracted_cost_items = json.loads(props.contracted_cost_items)
        contracted_cost_items.remove(self.cost_item)
        props.contracted_cost_items = json.dumps(contracted_cost_items)
        bpy.ops.bim.enable_editing_cost_items(cost_schedule=props.active_cost_schedule_id)
        return {"FINISHED"}


class ContractCostItem(bpy.types.Operator):
    bl_idname = "bim.contract_cost_item"
    bl_label = "Contract Cost Item"
    bl_options = {"REGISTER", "UNDO"}
    cost_item: bpy.props.IntProperty()

    def execute(self, context):
        props = context.scene.BIMCostProperties
        self.file = IfcStore.get_file()
        contracted_cost_items = json.loads(props.contracted_cost_items)
        contracted_cost_items.append(self.cost_item)
        props.contracted_cost_items = json.dumps(contracted_cost_items)
        bpy.ops.bim.enable_editing_cost_items(cost_schedule=props.active_cost_schedule_id)
        return {"FINISHED"}


class RemoveCostItem(bpy.types.Operator):
    bl_idname = "bim.remove_cost_item"
    bl_label = "Remove Cost item"
    bl_options = {"REGISTER", "UNDO"}
    cost_item: bpy.props.IntProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        props = context.scene.BIMCostProperties
        self.file = IfcStore.get_file()
        ifcopenshell.api.run(
            "cost.remove_cost_item",
            self.file,
            cost_item=self.file.by_id(self.cost_item),
        )
        contracted_cost_items = json.loads(props.contracted_cost_items)
        if props.active_cost_item_index in contracted_cost_items:
            contracted_cost_items.remove(props.active_cost_item_index)
        props.contracted_cost_items = json.dumps(contracted_cost_items)
        Data.load(self.file)
        bpy.ops.bim.enable_editing_cost_items(cost_schedule=props.active_cost_schedule_id)
        return {"FINISHED"}


class EnableEditingCostItem(bpy.types.Operator):
    bl_idname = "bim.enable_editing_cost_item"
    bl_label = "Enable Editing Cost Item"
    bl_options = {"REGISTER", "UNDO"}
    cost_item: bpy.props.IntProperty()

    def execute(self, context):
        props = context.scene.BIMCostProperties
        props.cost_item_attributes.clear()

        data = Data.cost_items[self.cost_item]
        blenderbim.bim.helper.import_attributes("IfcCostItem", props.cost_item_attributes, data)
        props.active_cost_item_id = self.cost_item
        props.cost_item_editing_type = "ATTRIBUTES"
        return {"FINISHED"}


class DisableEditingCostItem(bpy.types.Operator):
    bl_idname = "bim.disable_editing_cost_item"
    bl_label = "Disable Editing Cost Item"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        context.scene.BIMCostProperties.active_cost_item_id = 0
        return {"FINISHED"}


class EditCostItem(bpy.types.Operator):
    bl_idname = "bim.edit_cost_item"
    bl_label = "Edit Cost Item"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        props = context.scene.BIMCostProperties
        attributes = blenderbim.bim.helper.export_attributes(props.cost_item_attributes)
        self.file = IfcStore.get_file()
        ifcopenshell.api.run(
            "cost.edit_cost_item",
            self.file,
            **{"cost_item": self.file.by_id(props.active_cost_item_id), "attributes": attributes},
        )
        Data.load(IfcStore.get_file())
        bpy.ops.bim.disable_editing_cost_item()
        bpy.ops.bim.enable_editing_cost_items(cost_schedule=props.active_cost_schedule_id)
        return {"FINISHED"}


class AssignCostItemType(bpy.types.Operator):
    bl_idname = "bim.assign_cost_item_type"
    bl_label = "Assign Cost Item Type Product"
    bl_options = {"REGISTER", "UNDO"}
    cost_item: bpy.props.IntProperty()
    prop_name: bpy.props.StringProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        self.file = IfcStore.get_file()
        cost_item = self.file.by_id(self.cost_item)
        for obj in context.selected_objects:
            if not obj.BIMObjectProperties.ifc_definition_id:
                continue
            product = self.file.by_id(obj.BIMObjectProperties.ifc_definition_id)
            if product.is_a("IfcTypeProduct"):
                ifcopenshell.api.run(
                    "control.assign_control", self.file, relating_control=cost_item, related_object=product
                )
        Data.load(self.file)
        bpy.ops.bim.load_cost_item_types()
        return {"FINISHED"}


class UnassignCostItemType(bpy.types.Operator):
    bl_idname = "bim.unassign_cost_item_type"
    bl_label = "Unassign Cost Item Type"
    bl_options = {"REGISTER", "UNDO"}
    cost_item: bpy.props.IntProperty()
    related_object: bpy.props.IntProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        self.file = IfcStore.get_file()
        cost_item = self.file.by_id(self.cost_item)
        if self.related_object:
            products = [self.file.by_id(self.related_object)]
        else:
            for obj in context.selected_objects:
                if not obj.BIMObjectProperties.ifc_definition_id:
                    continue
                product = self.file.by_id(obj.BIMObjectProperties.ifc_definition_id)
                if product.is_a("IfcTypeProduct"):
                    products.append(product)
        for product in products:
            ifcopenshell.api.run(
                "control.unassign_control", self.file, relating_control=cost_item, related_object=product
            )
        Data.load(self.file)
        bpy.ops.bim.load_cost_item_types()
        return {"FINISHED"}


class AssignCostItemQuantity(bpy.types.Operator):
    bl_idname = "bim.assign_cost_item_quantity"
    bl_label = "Assign Cost Item Quantity"
    bl_options = {"REGISTER", "UNDO"}
    cost_item: bpy.props.IntProperty()
    related_object_type: bpy.props.StringProperty()
    prop_name: bpy.props.StringProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        self.file = IfcStore.get_file()
        if self.related_object_type == "PRODUCT":
            products = [
                self.file.by_id(o.BIMObjectProperties.ifc_definition_id)
                for o in context.selected_objects
                if o.BIMObjectProperties.ifc_definition_id
            ]
        elif self.related_object_type == "PROCESS":
            products = [
                self.file.by_id(
                    context.scene.BIMTaskTreeProperties.tasks[
                        context.scene.BIMWorkScheduleProperties.active_task_index
                    ].ifc_definition_id
                )
            ]
        elif self.related_object_type == "RESOURCE":
            products = [
                self.file.by_id(
                    context.scene.BIMResourceTreeProperties.resources[
                        context.scene.BIMResourceProperties.active_resource_index
                    ].ifc_definition_id
                )
            ]
        ifcopenshell.api.run(
            "cost.assign_cost_item_quantity",
            self.file,
            cost_item=self.file.by_id(self.cost_item),
            products=products,
            prop_name=self.prop_name,
        )
        Data.load(self.file)
        bpy.ops.bim.load_cost_item_quantities()
        return {"FINISHED"}


class UnassignCostItemQuantity(bpy.types.Operator):
    bl_idname = "bim.unassign_cost_item_quantity"
    bl_label = "Unassign Cost Item Quantity"
    bl_options = {"REGISTER", "UNDO"}
    cost_item: bpy.props.IntProperty()
    related_object: bpy.props.IntProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        self.file = IfcStore.get_file()
        if self.related_object:
            products = [self.file.by_id(self.related_object)]
        else:
            products = [
                self.file.by_id(o.BIMObjectProperties.ifc_definition_id)
                for o in context.selected_objects
                if o.BIMObjectProperties.ifc_definition_id
            ]
        ifcopenshell.api.run(
            "cost.unassign_cost_item_quantity",
            self.file,
            cost_item=self.file.by_id(self.cost_item),
            products=products,
        )
        Data.load(self.file)
        bpy.ops.bim.load_cost_item_quantities()
        return {"FINISHED"}


class EnableEditingCostItemQuantities(bpy.types.Operator):
    bl_idname = "bim.enable_editing_cost_item_quantities"
    bl_label = "Enable Editing Cost Item Quantities"
    bl_options = {"REGISTER", "UNDO"}
    cost_item: bpy.props.IntProperty()

    def execute(self, context):
        props = context.scene.BIMCostProperties
        props.active_cost_item_id = self.cost_item
        props.cost_item_editing_type = "QUANTITIES"
        purge()
        return {"FINISHED"}


class EnableEditingCostItemValues(bpy.types.Operator):
    bl_idname = "bim.enable_editing_cost_item_values"
    bl_label = "Enable Editing Cost Item Values"
    bl_options = {"REGISTER", "UNDO"}
    cost_item: bpy.props.IntProperty()

    def execute(self, context):
        props = context.scene.BIMCostProperties
        props.active_cost_item_id = self.cost_item
        props.cost_item_editing_type = "VALUES"
        bpy.ops.bim.disable_editing_cost_item_value()
        return {"FINISHED"}


class AddCostItemQuantity(bpy.types.Operator):
    bl_idname = "bim.add_cost_item_quantity"
    bl_label = "Add Cost Item Quantity"
    bl_options = {"REGISTER", "UNDO"}
    cost_item: bpy.props.IntProperty()
    ifc_class: bpy.props.StringProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        self.file = IfcStore.get_file()
        self.props = context.scene.BIMCostProperties
        self.add_manual_quantity()
        Data.load(self.file)
        return {"FINISHED"}

    def add_manual_quantity(self):
        ifcopenshell.api.run(
            "cost.add_cost_item_quantity",
            self.file,
            cost_item=self.file.by_id(self.cost_item),
            ifc_class=self.ifc_class,
        )


class RemoveCostItemQuantity(bpy.types.Operator):
    bl_idname = "bim.remove_cost_item_quantity"
    bl_label = "Remove Cost Item Quantity"
    bl_options = {"REGISTER", "UNDO"}
    cost_item: bpy.props.IntProperty()
    physical_quantity: bpy.props.IntProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        self.file = IfcStore.get_file()
        ifcopenshell.api.run(
            "cost.remove_cost_item_quantity",
            self.file,
            cost_item=self.file.by_id(self.cost_item),
            physical_quantity=self.file.by_id(self.physical_quantity),
        )
        Data.load(self.file)
        return {"FINISHED"}


class EnableEditingCostItemQuantity(bpy.types.Operator):
    bl_idname = "bim.enable_editing_cost_item_quantity"
    bl_label = "Enable Editing Cost Item Quantity"
    bl_options = {"REGISTER", "UNDO"}
    physical_quantity: bpy.props.IntProperty()

    def execute(self, context):
        self.props = context.scene.BIMCostProperties
        self.props.quantity_attributes.clear()
        self.props.active_cost_item_quantity_id = self.physical_quantity
        data = Data.physical_quantities[self.physical_quantity]
        blenderbim.bim.helper.import_attributes(data["type"], self.props.quantity_attributes, data)
        return {"FINISHED"}


class DisableEditingCostItemQuantity(bpy.types.Operator):
    bl_idname = "bim.disable_editing_cost_item_quantity"
    bl_label = "Disable Editing Cost Item Quantity"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        props = context.scene.BIMCostProperties
        props.active_cost_item_quantity_id = 0
        return {"FINISHED"}


class EditCostItemQuantity(bpy.types.Operator):
    bl_idname = "bim.edit_cost_item_quantity"
    bl_label = "Edit Cost Item Quantity"
    bl_options = {"REGISTER", "UNDO"}
    physical_quantity: bpy.props.IntProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        props = context.scene.BIMCostProperties
        attributes = blenderbim.bim.helper.export_attributes(props.quantity_attributes)
        self.file = IfcStore.get_file()
        ifcopenshell.api.run(
            "cost.edit_cost_item_quantity",
            self.file,
            **{"physical_quantity": self.file.by_id(self.physical_quantity), "attributes": attributes},
        )
        Data.load(IfcStore.get_file())
        bpy.ops.bim.disable_editing_cost_item_quantity()
        return {"FINISHED"}


class AddCostValue(bpy.types.Operator):
    bl_idname = "bim.add_cost_value"
    bl_label = "Add Cost Value"
    bl_options = {"REGISTER", "UNDO"}
    parent: bpy.props.IntProperty()
    cost_type: bpy.props.StringProperty()
    cost_category: bpy.props.StringProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        self.file = IfcStore.get_file()
        parent = self.file.by_id(self.parent)
        if self.cost_type == "FIXED":
            category = None
            attributes = {"AppliedValue": 0.0}
        elif self.cost_type == "SUM":
            category = "*"
            attributes = {"Category": category}
        elif self.cost_type == "CATEGORY":
            category = self.cost_category
            attributes = {"Category": category}
        value = ifcopenshell.api.run("cost.add_cost_value", self.file, parent=parent)
        ifcopenshell.api.run("cost.edit_cost_value", self.file, cost_value=value, attributes=attributes)
        if parent.is_a("IfcConstructionResource"):
            ResourceData.load(self.file)
        else:
            Data.load(self.file)
        return {"FINISHED"}


class RemoveCostItemValue(bpy.types.Operator):
    bl_idname = "bim.remove_cost_value"
    bl_label = "Add Cost Item Value"
    bl_options = {"REGISTER", "UNDO"}
    parent: bpy.props.IntProperty()
    cost_value: bpy.props.IntProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        self.file = IfcStore.get_file()
        parent = self.file.by_id(self.parent)
        ifcopenshell.api.run(
            "cost.remove_cost_value",
            self.file,
            parent=parent,
            cost_value=self.file.by_id(self.cost_value),
        )
        if parent.is_a("IfcConstructionResource"):
            ResourceData.load(self.file)
        else:
            Data.load(self.file)
        return {"FINISHED"}


class EnableEditingCostItemValue(bpy.types.Operator):
    bl_idname = "bim.enable_editing_cost_item_value"
    bl_label = "Enable Editing Cost Item Value"
    bl_options = {"REGISTER", "UNDO"}
    cost_value: bpy.props.IntProperty()

    def execute(self, context):
        self.props = context.scene.BIMCostProperties
        self.props.cost_value_attributes.clear()
        self.props.active_cost_value_id = self.cost_value
        self.props.cost_value_editing_type = "ATTRIBUTES"
        data = Data.cost_values[self.cost_value]

        blenderbim.bim.helper.import_attributes(
            data["type"],
            self.props.cost_value_attributes,
            data,
            lambda name, prop, data: self.import_attributes(name, prop, data, context),
        )
        return {"FINISHED"}

    def import_attributes(self, name, prop, data, context):
        if name == "AppliedValue":
            # TODO: for now, only support simple IfcValues (which are effectively IfcMonetaryMeasure)
            prop = self.props.cost_value_attributes.add()
            prop.data_type = "float"
            prop.name = "AppliedValue"
            prop.is_optional = True
            prop.float_value = 0.0 if prop.is_null else data[name]
            return True
        if (
            name == "UnitBasis"
            and Data.cost_schedules[context.scene.BIMCostProperties.active_cost_schedule_id]["PredefinedType"]
            == "SCHEDULEOFRATES"
        ):
            prop = self.props.cost_value_attributes.add()
            prop.name = "UnitBasisValue"
            prop.data_type = "float"
            prop.is_null = data["UnitBasis"] is None
            prop.is_optional = True
            if data["UnitBasis"]:
                prop.float_value = data["UnitBasis"]["ValueComponent"] or 0
            else:
                prop.float_value = 0

            prop = self.props.cost_value_attributes.add()
            prop.name = "UnitBasisUnit"
            prop.data_type = "enum"
            prop.is_null = prop.is_optional = False
            units = {}
            for unit_id, unit in UnitData.units.items():
                if unit.get("UnitType", None) in [
                    "AREAUNIT",
                    "LENGTHUNIT",
                    "TIMEUNIT",
                    "VOLUMEUNIT",
                    "MASSUNIT",
                    "USERDEFINED",
                ]:
                    if unit["type"] == "IfcContextDependentUnit":
                        units[unit_id] = f"{unit['UnitType']} / {unit['Name']}"
                    else:
                        name = unit["Name"]
                        if unit.get("Prefix", None):
                            name = f"(unit['Prefix']) {name}"
                        units[unit_id] = f"{unit['UnitType']} / {name}"
            prop.enum_items = json.dumps(units)
            if data["UnitBasis"] and data["UnitBasis"]["UnitComponent"]:
                prop.enum_value = str(data["UnitBasis"]["UnitComponent"])
            return True


class DisableEditingCostItemValue(bpy.types.Operator):
    bl_idname = "bim.disable_editing_cost_item_value"
    bl_label = "Disable Editing Cost Item Value"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        props = context.scene.BIMCostProperties
        props.active_cost_value_id = 0
        props.cost_value_editing_type = ""
        return {"FINISHED"}


class EnableEditingCostItemValueFormula(bpy.types.Operator):
    bl_idname = "bim.enable_editing_cost_item_value_formula"
    bl_label = "Enable Editing Cost Item Value Formula"
    bl_options = {"REGISTER", "UNDO"}
    cost_value: bpy.props.IntProperty()

    def execute(self, context):
        self.props = context.scene.BIMCostProperties
        self.props.cost_value_attributes.clear()
        self.props.active_cost_value_id = self.cost_value
        self.props.cost_value_editing_type = "FORMULA"
        self.props.cost_value_formula = Data.cost_values[self.cost_value]["Formula"]
        return {"FINISHED"}


class EditCostItemValueFormula(bpy.types.Operator):
    bl_idname = "bim.edit_cost_value_formula"
    bl_label = "Edit Cost Value Formula"
    bl_options = {"REGISTER", "UNDO"}
    cost_value: bpy.props.IntProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        props = context.scene.BIMCostProperties
        self.file = IfcStore.get_file()
        ifcopenshell.api.run(
            "cost.edit_cost_value_formula",
            self.file,
            **{"cost_value": self.file.by_id(self.cost_value), "formula": props.cost_value_formula},
        )
        Data.load(IfcStore.get_file())
        bpy.ops.bim.disable_editing_cost_item_value()
        return {"FINISHED"}


class EditCostItemValue(bpy.types.Operator):
    bl_idname = "bim.edit_cost_value"
    bl_label = "Edit Cost Value"
    bl_options = {"REGISTER", "UNDO"}
    cost_value: bpy.props.IntProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        props = context.scene.BIMCostProperties
        attributes = blenderbim.bim.helper.export_attributes(
            props.cost_value_attributes, lambda attributes, prop: self.export_attributes(attributes, prop, context)
        )
        self.file = IfcStore.get_file()
        ifcopenshell.api.run(
            "cost.edit_cost_value",
            self.file,
            **{"cost_value": self.file.by_id(self.cost_value), "attributes": attributes},
        )
        Data.load(IfcStore.get_file())
        bpy.ops.bim.disable_editing_cost_item_value()
        return {"FINISHED"}

    def export_attributes(self, attributes, prop, context):
        if prop.name == "UnitBasisValue":
            if prop.is_null:
                attributes["UnitBasis"] = None
                return True
            attributes["UnitBasis"] = {
                "ValueComponent": prop.float_value or 1,
                "UnitComponent": IfcStore.get_file().by_id(
                    int(context.scene.BIMCostProperties.cost_value_attributes.get("UnitBasisUnit").enum_value)
                ),
            }
            return True
        if prop.name == "UnitBasisUnit":
            return True


class CopyCostItemValues(bpy.types.Operator):
    bl_idname = "bim.copy_cost_item_values"
    bl_label = "Copy Cost Item Values"
    bl_options = {"REGISTER", "UNDO"}
    source: bpy.props.IntProperty()
    destination: bpy.props.IntProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        self.file = IfcStore.get_file()
        ifcopenshell.api.run(
            "cost.copy_cost_item_values",
            self.file,
            **{"source": self.file.by_id(self.source), "destination": self.file.by_id(self.destination)},
        )
        Data.load(IfcStore.get_file())
        return {"FINISHED"}


class SelectCostItemProducts(bpy.types.Operator):
    bl_idname = "bim.select_cost_item_products"
    bl_label = "Select Cost Item Products"
    bl_options = {"REGISTER", "UNDO"}
    cost_item: bpy.props.IntProperty()

    def execute(self, context):
        self.file = IfcStore.get_file()
        related_products = Data.cost_items[self.cost_item]["Controls"].keys()
        for obj in context.visible_objects:
            obj.select_set(False)
            if obj.BIMObjectProperties.ifc_definition_id in related_products:
                obj.select_set(True)
        return {"FINISHED"}


class SelectCostScheduleProducts(bpy.types.Operator):
    bl_idname = "bim.select_cost_schedule_products"
    bl_label = "Select Cost Schedule Products"
    bl_options = {"REGISTER", "UNDO"}
    cost_schedule: bpy.props.IntProperty()

    def execute(self, context):
        self.file = IfcStore.get_file()
        self.related_products = []
        for cost_item_id in Data.cost_schedules[self.cost_schedule]["Controls"]:
            self.get_related_products(Data.cost_items[cost_item_id])
        self.related_products = set(self.related_products)
        for obj in context.visible_objects:
            obj.select_set(False)
            if obj.BIMObjectProperties.ifc_definition_id in self.related_products:
                obj.select_set(True)
        return {"FINISHED"}

    def get_related_products(self, cost_item):
        self.related_products.extend(cost_item["Controls"].keys())
        for child_id in cost_item["IsNestedBy"]:
            self.get_related_products(Data.cost_items[child_id])


class ImportCostScheduleCsv(bpy.types.Operator, ImportHelper):
    bl_idname = "import_cost_schedule_csv.bim"
    bl_label = "Import Cost Schedule CSV"
    bl_options = {"REGISTER", "UNDO"}
    filename_ext = ".csv"
    filter_glob: bpy.props.StringProperty(default="*.csv", options={"HIDDEN"})
    is_schedule_of_rates: bpy.props.BoolProperty(name="Is Schedule Of Rates", default=False)

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        from ifc5d.csv2ifc import Csv2Ifc

        self.file = IfcStore.get_file()
        start = time.time()
        csv2ifc = Csv2Ifc()
        csv2ifc.csv = self.filepath
        csv2ifc.file = self.file
        csv2ifc.is_schedule_of_rates = self.is_schedule_of_rates
        csv2ifc.execute()
        Data.load(IfcStore.get_file())
        UnitData.load(IfcStore.get_file())
        purge()
        print("Import finished in {:.2f} seconds".format(time.time() - start))
        return {"FINISHED"}


class AddCostColumn(bpy.types.Operator):
    bl_idname = "bim.add_cost_column"
    bl_label = "Add Cost Column"
    bl_options = {"REGISTER", "UNDO"}
    name: bpy.props.StringProperty()

    def execute(self, context):
        self.props = context.scene.BIMCostProperties
        new = self.props.columns.add()
        new.name = self.name
        Data.set_categories([c.name for c in self.props.columns])
        Data.load(IfcStore.get_file())
        return {"FINISHED"}


class RemoveCostColumn(bpy.types.Operator):
    bl_idname = "bim.remove_cost_column"
    bl_label = "Remove Cost Column"
    bl_options = {"REGISTER", "UNDO"}
    name: bpy.props.StringProperty()

    def execute(self, context):
        self.props = context.scene.BIMCostProperties
        self.props.columns.remove(self.props.columns.find(self.name))
        Data.set_categories([c.name for c in self.props.columns])
        Data.load(IfcStore.get_file())
        return {"FINISHED"}


class LoadCostItemQuantities(bpy.types.Operator):
    bl_idname = "bim.load_cost_item_quantities"
    bl_label = "Load Cost Item Quantities"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        self.props = context.scene.BIMCostProperties
        self.file = IfcStore.get_file()
        self.props.cost_item_products.clear()
        self.props.cost_item_processes.clear()
        self.props.cost_item_resources.clear()
        ifc_definition_id = self.props.cost_items[self.props.active_cost_item_index].ifc_definition_id
        for control_id, quantity_ids in Data.cost_items[ifc_definition_id]["Controls"].items():
            related_object = self.file.by_id(control_id)
            if related_object.is_a("IfcProduct"):
                new = self.props.cost_item_products.add()
            elif related_object.is_a("IfcProcess"):
                new = self.props.cost_item_processes.add()
            elif related_object.is_a("IfcResource"):
                new = self.props.cost_item_resources.add()
            new.ifc_definition_id = control_id
            new.name = related_object.Name or "Unnamed"
            total_quantity = 0
            for quantity_id in quantity_ids:
                total_quantity += self.file.by_id(quantity_id)[3]
            new.total_quantity = total_quantity
        return {"FINISHED"}


class LoadCostItemTypes(bpy.types.Operator):
    bl_idname = "bim.load_cost_item_types"
    bl_label = "Load Cost Item Types"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        self.props = context.scene.BIMCostProperties
        self.file = IfcStore.get_file()
        self.props.cost_item_type_products.clear()
        # TODO implement process and resource types
        # self.props.cost_item_processes.clear()
        # self.props.cost_item_resources.clear()
        ifc_definition_id = self.props.cost_items[self.props.active_cost_item_index].ifc_definition_id
        for control_id, quantity_ids in Data.cost_items[ifc_definition_id]["Controls"].items():
            related_object = self.file.by_id(control_id)
            if related_object.is_a("IfcTypeProduct"):
                new = self.props.cost_item_type_products.add()
            # TODO implement process and resource types
            # elif related_object.is_a("IfcProcess"):
            #    new = self.props.cost_item_processes.add()
            # elif related_object.is_a("IfcResource"):
            #    new = self.props.cost_item_resources.add()
            new.ifc_definition_id = control_id
            new.name = related_object.Name or "Unnamed"
        return {"FINISHED"}


class AssignCostValue(bpy.types.Operator):
    bl_idname = "bim.assign_cost_value"
    bl_label = "Assign Cost Value"
    bl_options = {"REGISTER", "UNDO"}
    cost_item: bpy.props.IntProperty()
    cost_rate: bpy.props.IntProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        self.file = IfcStore.get_file()
        ifcopenshell.api.run(
            "cost.assign_cost_value",
            self.file,
            cost_item=self.file.by_id(self.cost_item),
            cost_rate=self.file.by_id(self.cost_rate),
        )
        Data.load(self.file)
        return {"FINISHED"}


class LoadScheduleOfRates(bpy.types.Operator):
    bl_idname = "bim.load_schedule_of_rates"
    bl_label = "Load Schedule of Rates"
    bl_options = {"REGISTER", "UNDO"}
    cost_schedule: bpy.props.IntProperty()

    def execute(self, context):
        self.props = context.scene.BIMCostProperties
        self.props.is_cost_update_enabled = False
        self.props.cost_item_rates.clear()
        self.contracted_cost_item_rates = json.loads(self.props.contracted_cost_item_rates)
        for related_object_id in Data.cost_schedules[self.cost_schedule]["Controls"]:
            self.create_new_cost_item_li(related_object_id, 0)
        self.props.is_cost_update_enabled = True
        return {"FINISHED"}

    def create_new_cost_item_li(self, related_object_id, level_index):
        cost_item = Data.cost_items[related_object_id]
        new = self.props.cost_item_rates.add()
        new.ifc_definition_id = related_object_id
        new.name = cost_item["Name"] or "Unnamed"
        new.identification = cost_item["Identification"] or "XXX"
        new.is_expanded = related_object_id not in self.contracted_cost_item_rates
        new.level_index = level_index
        if cost_item["IsNestedBy"]:
            new.has_children = True
            if new.is_expanded:
                for related_object_id in cost_item["IsNestedBy"]:
                    self.create_new_cost_item_li(related_object_id, level_index + 1)


class ExpandCostItemRate(bpy.types.Operator):
    bl_idname = "bim.expand_cost_item_rate"
    bl_label = "Expand Cost Item Rate"
    bl_options = {"REGISTER", "UNDO"}
    cost_item: bpy.props.IntProperty()

    def execute(self, context):
        props = context.scene.BIMCostProperties
        self.file = IfcStore.get_file()
        contracted_cost_item_rates = json.loads(props.contracted_cost_item_rates)
        contracted_cost_item_rates.remove(self.cost_item)
        props.contracted_cost_item_rates = json.dumps(contracted_cost_item_rates)
        bpy.ops.bim.load_schedule_of_rates(cost_schedule=int(props.schedule_of_rates))
        return {"FINISHED"}


class ContractCostItemRate(bpy.types.Operator):
    bl_idname = "bim.contract_cost_item_rate"
    bl_label = "Contract Cost Item Rate"
    bl_options = {"REGISTER", "UNDO"}
    cost_item: bpy.props.IntProperty()

    def execute(self, context):
        props = context.scene.BIMCostProperties
        self.file = IfcStore.get_file()
        contracted_cost_item_rates = json.loads(props.contracted_cost_item_rates)
        contracted_cost_item_rates.append(self.cost_item)
        props.contracted_cost_item_rates = json.dumps(contracted_cost_item_rates)
        bpy.ops.bim.load_schedule_of_rates(cost_schedule=int(props.schedule_of_rates))
        return {"FINISHED"}
