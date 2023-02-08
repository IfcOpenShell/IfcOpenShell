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
import blenderbim.tool as tool
from blenderbim.bim.ifc import IfcStore
from bpy_extras.io_utils import ImportHelper
import blenderbim.tool as tool
import blenderbim.core.cost as core


class AddCostSchedule(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_cost_schedule"
    bl_label = "Add Cost Schedule"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Add a new cost schedule"

    def _execute(self, context):
        core.add_cost_schedule(tool.Ifc)


class EditCostSchedule(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.edit_cost_schedule"
    bl_label = "Edit Cost Schedule"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.edit_cost_schedule(
            tool.Ifc,
            tool.Cost,
            cost_schedule=tool.Ifc.get().by_id(context.scene.BIMCostProperties.active_cost_schedule_id),
        )


class RemoveCostSchedule(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.remove_cost_schedule"
    bl_label = "Remove Cost Schedule"
    bl_options = {"REGISTER", "UNDO"}
    cost_schedule: bpy.props.IntProperty()

    def _execute(self, context):
        core.remove_cost_schedule(tool.Ifc, cost_schedule=tool.Ifc.get().by_id(self.cost_schedule))


class EnableEditingCostSchedule(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.enable_editing_cost_schedule_attributes"
    bl_label = "Enable Editing Cost Schedule"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Enable editing cost schedule"
    cost_schedule: bpy.props.IntProperty()

    def _execute(self, context):
        core.enable_editing_cost_schedule_attributes(tool.Cost, cost_schedule=tool.Ifc.get().by_id(self.cost_schedule))


class EnableEditingCostItems(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.enable_editing_cost_items"
    bl_label = "Enable Editing Cost Items"
    bl_options = {"REGISTER", "UNDO"}
    cost_schedule: bpy.props.IntProperty()

    def _execute(self, context):
        core.enable_editing_cost_items(tool.Cost, cost_schedule=tool.Ifc.get().by_id(self.cost_schedule))


class DisableEditingCostSchedule(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.disable_editing_cost_schedule"
    bl_label = "Disable Editing Cost Schedule"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.disable_editing_cost_schedule(tool.Cost)


class AddSummaryCostItem(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_summary_cost_item"
    bl_label = "Add Cost Item"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Add a summary cost item"
    cost_schedule: bpy.props.IntProperty()

    def _execute(self, context):
        core.add_summary_cost_item(tool.Ifc, tool.Cost, cost_schedule=tool.Ifc.get().by_id(self.cost_schedule))


class AddCostItem(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_cost_item"
    bl_label = "Add Cost Item"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Add a new cost item"
    cost_item: bpy.props.IntProperty()

    def _execute(self, context):
        core.add_cost_item(tool.Ifc, tool.Cost, cost_item=tool.Ifc.get().by_id(self.cost_item))


class ExpandCostItem(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.expand_cost_item"
    bl_label = "Expand Cost Item"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Expand this cost item"
    cost_item: bpy.props.IntProperty()

    def _execute(self, context):
        core.expand_cost_item(tool.Cost, cost_item=tool.Ifc.get().by_id(self.cost_item))


class ExpandCostItems(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.expand_cost_items"
    bl_label = "Expand Cost Items"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Expand all cost items"
    cost_items: bpy.props.StringProperty()

    def _execute(self, context):
        core.expand_cost_items(tool.Cost)


class ContractCostItem(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.contract_cost_item"
    bl_label = "Contract Cost Item"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Contract a cost item"
    cost_item: bpy.props.IntProperty()

    def _execute(self, context):
        core.contract_cost_item(tool.Cost, cost_item=tool.Ifc.get().by_id(self.cost_item))


class RemoveCostItem(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.remove_cost_item"
    bl_label = "Remove Cost item"
    bl_options = {"REGISTER", "UNDO"}
    cost_item: bpy.props.IntProperty()

    def _execute(self, context):
        core.remove_cost_item(tool.Ifc, tool.Cost, cost_item=tool.Ifc.get().by_id(self.cost_item))


class EnableEditingCostItem(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.enable_editing_cost_item_attributes"
    bl_label = "Enable Editing Cost Item"
    bl_options = {"REGISTER", "UNDO"}
    cost_item: bpy.props.IntProperty()

    def _execute(self, context):
        core.enable_editing_cost_item_attributes(tool.Cost, cost_item=tool.Ifc.get().by_id(self.cost_item))


class DisableEditingCostItem(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.disable_editing_cost_item"
    bl_label = "Disable Editing Cost Item"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.disable_editing_cost_item(tool.Cost)


class EditCostItem(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.edit_cost_item"
    bl_label = "Edit Cost Item"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.edit_cost_item(tool.Ifc, tool.Cost)
        return {"FINISHED"}


class AssignCostItemType(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.assign_cost_item_type"
    bl_label = "Assign Cost Item Type Product"
    bl_options = {"REGISTER", "UNDO"}
    cost_item: bpy.props.IntProperty()
    prop_name: bpy.props.StringProperty()

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
        bpy.ops.bim.load_cost_item_types()
        return {"FINISHED"}


class UnassignCostItemType(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.unassign_cost_item_type"
    bl_label = "Unassign Cost Item Type"
    bl_options = {"REGISTER", "UNDO"}
    cost_item: bpy.props.IntProperty()
    related_object: bpy.props.IntProperty()

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
        bpy.ops.bim.load_cost_item_types()
        return {"FINISHED"}


class AssignCostItemQuantity(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.assign_cost_item_quantity"
    bl_label = "Assign Cost Item Quantity"
    bl_options = {"REGISTER", "UNDO"}
    cost_item: bpy.props.IntProperty()
    related_object_type: bpy.props.StringProperty()
    prop_name: bpy.props.StringProperty()

    def _execute(self, context):
        if self.related_object_type == "PRODUCT":
            products = [
                tool.Ifc.get().by_id(o.BIMObjectProperties.ifc_definition_id)
                for o in context.selected_objects
                if o.BIMObjectProperties.ifc_definition_id
            ]
        elif self.related_object_type == "PROCESS":
            products = [
                tool.Ifc.get().by_id(
                    context.scene.BIMTaskTreeProperties.tasks[
                        context.scene.BIMWorkScheduleProperties.active_task_index
                    ].ifc_definition_id
                )
            ]
        elif self.related_object_type == "RESOURCE":
            products = [
                tool.Ifc.get().by_id(
                    context.scene.BIMResourceTreeProperties.resources[
                        context.scene.BIMResourceProperties.active_resource_index
                    ].ifc_definition_id
                )
            ]
        ifcopenshell.api.run(
            "cost.assign_cost_item_quantity",
            tool.Ifc.get(),
            cost_item=tool.Ifc.get().by_id(self.cost_item),
            products=products,
            prop_name=self.prop_name,
        )
        bpy.ops.bim.load_cost_item_quantities()
        return {"FINISHED"}


class UnassignCostItemQuantity(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.unassign_cost_item_quantity"
    bl_label = "Unassign Cost Item Quantity"
    bl_options = {"REGISTER", "UNDO"}
    cost_item: bpy.props.IntProperty()
    related_object: bpy.props.IntProperty()

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
        bpy.ops.bim.load_cost_item_quantities()
        return {"FINISHED"}


class EnableEditingCostItemQuantities(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.enable_editing_cost_item_quantities"
    bl_label = "Enable Editing Cost Item Quantities"
    bl_options = {"REGISTER", "UNDO"}
    cost_item: bpy.props.IntProperty()

    def _execute(self, context):
        props = context.scene.BIMCostProperties
        props.active_cost_item_id = self.cost_item
        props.cost_item_editing_type = "QUANTITIES"
        return {"FINISHED"}


class EnableEditingCostItemValues(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.enable_editing_cost_item_values"
    bl_label = "Enable Editing Cost Item Values"
    bl_options = {"REGISTER", "UNDO"}
    cost_item: bpy.props.IntProperty()

    def _execute(self, context):
        props = context.scene.BIMCostProperties
        props.active_cost_item_id = self.cost_item
        props.cost_item_editing_type = "VALUES"
        bpy.ops.bim.disable_editing_cost_item_value()
        return {"FINISHED"}


class AddCostItemQuantity(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_cost_item_quantity"
    bl_label = "Add Cost Item Quantity"
    bl_options = {"REGISTER", "UNDO"}
    cost_item: bpy.props.IntProperty()
    ifc_class: bpy.props.StringProperty()

    def _execute(self, context):
        self.file = IfcStore.get_file()
        self.props = context.scene.BIMCostProperties
        self.add_manual_quantity()
        return {"FINISHED"}

    def add_manual_quantity(self):
        ifcopenshell.api.run(
            "cost.add_cost_item_quantity",
            self.file,
            cost_item=self.file.by_id(self.cost_item),
            ifc_class=self.ifc_class,
        )


class RemoveCostItemQuantity(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.remove_cost_item_quantity"
    bl_label = "Remove Cost Item Quantity"
    bl_options = {"REGISTER", "UNDO"}
    cost_item: bpy.props.IntProperty()
    physical_quantity: bpy.props.IntProperty()

    def _execute(self, context):
        self.file = IfcStore.get_file()
        ifcopenshell.api.run(
            "cost.remove_cost_item_quantity",
            self.file,
            cost_item=self.file.by_id(self.cost_item),
            physical_quantity=self.file.by_id(self.physical_quantity),
        )
        return {"FINISHED"}


class EnableEditingCostItemQuantity(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.enable_editing_cost_item_quantity"
    bl_label = "Enable Editing Cost Item Quantity"
    bl_options = {"REGISTER", "UNDO"}
    physical_quantity: bpy.props.IntProperty()

    def _execute(self, context):
        self.props = context.scene.BIMCostProperties
        self.props.quantity_attributes.clear()
        self.props.active_cost_item_quantity_id = self.physical_quantity
        blenderbim.bim.helper.import_attributes2(
            tool.Ifc.get().by_id(self.physical_quantity), self.props.quantity_attributes
        )
        return {"FINISHED"}


class DisableEditingCostItemQuantity(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.disable_editing_cost_item_quantity"
    bl_label = "Disable Editing Cost Item Quantity"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        props = context.scene.BIMCostProperties
        props.active_cost_item_quantity_id = 0
        return {"FINISHED"}


class EditCostItemQuantity(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.edit_cost_item_quantity"
    bl_label = "Edit Cost Item Quantity"
    bl_options = {"REGISTER", "UNDO"}
    physical_quantity: bpy.props.IntProperty()

    def _execute(self, context):
        props = context.scene.BIMCostProperties
        attributes = blenderbim.bim.helper.export_attributes(props.quantity_attributes)
        self.file = IfcStore.get_file()
        ifcopenshell.api.run(
            "cost.edit_cost_item_quantity",
            self.file,
            **{"physical_quantity": self.file.by_id(self.physical_quantity), "attributes": attributes},
        )
        bpy.ops.bim.disable_editing_cost_item_quantity()
        return {"FINISHED"}


class AddCostValue(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_cost_value"
    bl_label = "Add Cost Value"
    bl_options = {"REGISTER", "UNDO"}
    parent: bpy.props.IntProperty()
    cost_type: bpy.props.StringProperty()
    cost_category: bpy.props.StringProperty()

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
        return {"FINISHED"}


class RemoveCostItemValue(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.remove_cost_value"
    bl_label = "Add Cost Item Value"
    bl_options = {"REGISTER", "UNDO"}
    parent: bpy.props.IntProperty()
    cost_value: bpy.props.IntProperty()

    def _execute(self, context):
        self.file = IfcStore.get_file()
        parent = self.file.by_id(self.parent)
        ifcopenshell.api.run(
            "cost.remove_cost_value",
            self.file,
            parent=parent,
            cost_value=self.file.by_id(self.cost_value),
        )
        return {"FINISHED"}


class EnableEditingCostItemValue(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.enable_editing_cost_item_value"
    bl_label = "Enable Editing Cost Item Value"
    bl_options = {"REGISTER", "UNDO"}
    cost_value: bpy.props.IntProperty()

    def _execute(self, context):
        self.props = context.scene.BIMCostProperties
        self.props.cost_value_attributes.clear()
        self.props.active_cost_value_id = self.cost_value
        self.props.cost_value_editing_type = "ATTRIBUTES"
        schedule = tool.Ifc.get().by_id(context.scene.BIMCostProperties.active_cost_schedule_id)
        is_rates = schedule.PredefinedType == "SCHEDULEOFRATES"
        cost_value = tool.Ifc.get().by_id(self.cost_value)
        callback = lambda name, prop, data: self.import_attributes(name, prop, data, cost_value, is_rates)
        blenderbim.bim.helper.import_attributes2(cost_value, self.props.cost_value_attributes, callback=callback)
        return {"FINISHED"}

    def import_attributes(self, name, prop, data, cost_value, is_rates):
        if name == "AppliedValue":
            # TODO: for now, only support simple IfcValues (which are effectively IfcMonetaryMeasure)
            prop = self.props.cost_value_attributes.add()
            prop.data_type = "float"
            prop.name = "AppliedValue"
            prop.is_optional = True
            prop.float_value = (
                0.0
                if prop.is_null
                else ifcopenshell.util.cost.calculate_applied_value(
                    tool.Ifc.get().by_id(self.props.active_cost_item_id), cost_value
                )
            )
            return True
        if name == "UnitBasis" and is_rates:
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
            for unit in tool.Ifc.get().by_type("IfcNamedUnit"):
                if unit.get("UnitType", None) in [
                    "AREAUNIT",
                    "LENGTHUNIT",
                    "TIMEUNIT",
                    "VOLUMEUNIT",
                    "MASSUNIT",
                    "USERDEFINED",
                ]:
                    if unit.is_a("IfcContextDependentUnit"):
                        units[unit.id()] = f"{unit.UnitType} / {unit.Name}"
                    else:
                        name = unit.Name
                        if unit.get("Prefix", None):
                            name = f"{unit.Prefix} {name}"
                        units[unit.id()] = f"{unit.UnitType} / {name}"
            prop.enum_items = json.dumps(units)
            if data["UnitBasis"] and data["UnitBasis"]["UnitComponent"]:
                prop.enum_value = str(data["UnitBasis"]["UnitComponent"])
            return True


class DisableEditingCostItemValue(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.disable_editing_cost_item_value"
    bl_label = "Disable Editing Cost Item Value"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        props = context.scene.BIMCostProperties
        props.active_cost_value_id = 0
        props.cost_value_editing_type = ""
        return {"FINISHED"}


class EnableEditingCostItemValueFormula(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.enable_editing_cost_item_value_formula"
    bl_label = "Enable Editing Cost Item Value Formula"
    bl_options = {"REGISTER", "UNDO"}
    cost_value: bpy.props.IntProperty()

    def _execute(self, context):
        self.props = context.scene.BIMCostProperties
        self.props.cost_value_attributes.clear()
        self.props.active_cost_value_id = self.cost_value
        self.props.cost_value_editing_type = "FORMULA"
        self.props.cost_value_formula = ifcopenshell.util.cost.serialise_cost_value(
            tool.Ifc.get().by_id(self.cost_value)
        )
        return {"FINISHED"}


class EditCostItemValueFormula(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.edit_cost_value_formula"
    bl_label = "Edit Cost Value Formula"
    bl_options = {"REGISTER", "UNDO"}
    cost_value: bpy.props.IntProperty()

    def _execute(self, context):
        props = context.scene.BIMCostProperties
        self.file = IfcStore.get_file()
        ifcopenshell.api.run(
            "cost.edit_cost_value_formula",
            self.file,
            **{"cost_value": self.file.by_id(self.cost_value), "formula": props.cost_value_formula},
        )
        bpy.ops.bim.disable_editing_cost_item_value()
        return {"FINISHED"}


class EditCostItemValue(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.edit_cost_value"
    bl_label = "Edit Cost Value"
    bl_options = {"REGISTER", "UNDO"}
    cost_value: bpy.props.IntProperty()

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


class CopyCostItemValues(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.copy_cost_item_values"
    bl_label = "Copy Cost Item Values"
    bl_options = {"REGISTER", "UNDO"}
    source: bpy.props.IntProperty()
    destination: bpy.props.IntProperty()

    def _execute(self, context):
        self.file = IfcStore.get_file()
        ifcopenshell.api.run(
            "cost.copy_cost_item_values",
            self.file,
            **{"source": self.file.by_id(self.source), "destination": self.file.by_id(self.destination)},
        )
        return {"FINISHED"}


class SelectCostItemProducts(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.select_cost_item_products"
    bl_label = "Select Cost Item Products"
    bl_options = {"REGISTER", "UNDO"}
    cost_item: bpy.props.IntProperty()

    def _execute(self, context):
        related_objects = []
        [related_objects.extend(r.RelatedObjects) for r in tool.Ifc.get().by_id(self.cost_item).Controls or []]
        related_objects = set([r.id() for r in related_objects])
        for obj in context.visible_objects:
            obj.select_set(False)
            if obj.BIMObjectProperties.ifc_definition_id in related_objects:
                obj.select_set(True)
        return {"FINISHED"}


class SelectCostScheduleProducts(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.select_cost_schedule_products"
    bl_label = "Select Cost Schedule Products"
    bl_options = {"REGISTER", "UNDO"}
    cost_schedule: bpy.props.IntProperty()

    def _execute(self, context):
        self.file = IfcStore.get_file()
        self.related_products = []
        for cost_item in tool.Ifc.get().by_id(self.cost_schedule).Controls or []:
            self.get_related_products(cost_item)
        self.related_products = set(self.related_products)
        for obj in context.visible_objects:
            obj.select_set(False)
            if obj.BIMObjectProperties.ifc_definition_id in self.related_products:
                obj.select_set(True)
        return {"FINISHED"}

    def get_related_products(self, cost_item):
        [self.related_products.extend(r.RelatedObjects) for r in cost_item.Controls or []]
        for rel in cost_item.IsNestedBy or []:
            for sub_cost_item in rel.RelatedObjects:
                self.get_related_products(sub_cost_item)


class ImportCostScheduleCsv(bpy.types.Operator, ImportHelper, tool.Ifc.Operator):
    bl_idname = "import_cost_schedule_csv.bim"
    bl_label = "Import Cost Schedule CSV"
    bl_options = {"REGISTER", "UNDO"}
    filename_ext = ".csv"
    filter_glob: bpy.props.StringProperty(default="*.csv", options={"HIDDEN"})
    is_schedule_of_rates: bpy.props.BoolProperty(name="Is Schedule Of Rates", default=False)

    def _execute(self, context):
        from ifc5d.csv2ifc import Csv2Ifc

        self.file = IfcStore.get_file()
        start = time.time()
        csv2ifc = Csv2Ifc()
        csv2ifc.csv = self.filepath
        csv2ifc.file = self.file
        csv2ifc.is_schedule_of_rates = self.is_schedule_of_rates
        csv2ifc.execute()
        print("Import finished in {:.2f} seconds".format(time.time() - start))
        return {"FINISHED"}


class AddCostColumn(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_cost_column"
    bl_label = "Add Cost Column"
    bl_options = {"REGISTER", "UNDO"}
    name: bpy.props.StringProperty()

    def _execute(self, context):
        self.props = context.scene.BIMCostProperties
        new = self.props.columns.add()
        new.name = self.name
        return {"FINISHED"}


class RemoveCostColumn(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.remove_cost_column"
    bl_label = "Remove Cost Column"
    bl_options = {"REGISTER", "UNDO"}
    name: bpy.props.StringProperty()

    def _execute(self, context):
        self.props = context.scene.BIMCostProperties
        self.props.columns.remove(self.props.columns.find(self.name))
        return {"FINISHED"}


class LoadCostItemQuantities(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.load_cost_item_quantities"
    bl_label = "Load Cost Item Quantities"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        self.props = context.scene.BIMCostProperties
        self.file = IfcStore.get_file()
        self.props.cost_item_products.clear()
        self.props.cost_item_processes.clear()
        self.props.cost_item_resources.clear()
        if self.props.active_cost_item_index < len(self.props.cost_items):
            ifc_definition_id = self.props.cost_items[self.props.active_cost_item_index].ifc_definition_id
            cost_item = tool.Ifc.get().by_id(ifc_definition_id)
            # for control_id, quantity_ids in cost_item.Controls.items() or {}:
            for rel in cost_item.Controls or []:
                # control_id, quantity_ids
                for related_object in rel.RelatedObjects:
                    if related_object.is_a("IfcProduct"):
                        new = self.props.cost_item_products.add()
                    elif related_object.is_a("IfcProcess"):
                        new = self.props.cost_item_processes.add()
                    elif related_object.is_a("IfcResource"):
                        new = self.props.cost_item_resources.add()
                    new.ifc_definition_id = related_object.id()
                    new.name = related_object.Name or "Unnamed"
                    total_quantity = 0
                    qtos = ifcopenshell.util.element.get_psets(related_object, qtos_only=True)
                    for qset_name, quantities in qtos.items():
                        qto = tool.Ifc.get().by_id(quantities["id"])
                        for quantity in qto.Quantities:
                            if quantity in cost_item.CostQuantities:
                                total_quantity += quantity[3]
                    new.total_quantity = total_quantity
        return {"FINISHED"}


class LoadCostItemTypes(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.load_cost_item_types"
    bl_label = "Load Cost Item Types"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        self.props = context.scene.BIMCostProperties
        self.file = IfcStore.get_file()
        self.props.cost_item_type_products.clear()
        # TODO implement process and resource types
        # self.props.cost_item_processes.clear()
        # self.props.cost_item_resources.clear()
        ifc_definition_id = self.props.cost_items[self.props.active_cost_item_index].ifc_definition_id
        cost_item = tool.Ifc.get().by_id(ifc_definition_id)
        for rel in cost_item.Controls or []:
            for related_object in rel.RelatedObjects:
                if related_object.is_a("IfcTypeProduct"):
                    new = self.props.cost_item_type_products.add()
                # TODO implement process and resource types
                # elif related_object.is_a("IfcProcess"):
                #    new = self.props.cost_item_processes.add()
                # elif related_object.is_a("IfcResource"):
                #    new = self.props.cost_item_resources.add()
                new.ifc_definition_id = related_object.id()
                new.name = related_object.Name or "Unnamed"
        return {"FINISHED"}


class AssignCostValue(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.assign_cost_value"
    bl_label = "Assign Cost Value"
    bl_options = {"REGISTER", "UNDO"}
    cost_item: bpy.props.IntProperty()
    cost_rate: bpy.props.IntProperty()

    def _execute(self, context):
        self.file = IfcStore.get_file()
        ifcopenshell.api.run(
            "cost.assign_cost_value",
            self.file,
            cost_item=self.file.by_id(self.cost_item),
            cost_rate=self.file.by_id(self.cost_rate),
        )
        return {"FINISHED"}


class LoadScheduleOfRates(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.load_schedule_of_rates"
    bl_label = "Load Schedule of Rates"
    bl_options = {"REGISTER", "UNDO"}
    cost_schedule: bpy.props.IntProperty()

    def _execute(self, context):
        self.props = context.scene.BIMCostProperties
        self.props.is_cost_update_enabled = False
        self.props.cost_item_rates.clear()
        self.contracted_cost_item_rates = json.loads(self.props.contracted_cost_item_rates)
        for rel in tool.Ifc.get().by_id(self.cost_schedule).Controls or []:
            for cost_item in rel.RelatedObjects:
                self.create_new_cost_item_li(cost_item, 0)
        self.props.is_cost_update_enabled = True
        return {"FINISHED"}

    def create_new_cost_item_li(self, cost_item, level_index):
        new = self.props.cost_item_rates.add()
        new.ifc_definition_id = cost_item.id()
        new.name = cost_item.Name or "Unnamed"
        new.identification = cost_item.Identification or "XXX"
        new.is_expanded = cost_item.id() not in self.contracted_cost_item_rates
        new.level_index = level_index
        if cost_item.IsNestedBy:
            new.has_children = True
            if new.is_expanded:
                for rel in cost_item.IsNestedBy:
                    for sub_cost_item in rel.RelatedObjects:
                        self.create_new_cost_item_li(sub_cost_item, level_index + 1)


class ExpandCostItemRate(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.expand_cost_item_rate"
    bl_label = "Expand Cost Item Rate"
    bl_options = {"REGISTER", "UNDO"}
    cost_item: bpy.props.IntProperty()

    def _execute(self, context):
        props = context.scene.BIMCostProperties
        self.file = IfcStore.get_file()
        contracted_cost_item_rates = json.loads(props.contracted_cost_item_rates)
        contracted_cost_item_rates.remove(self.cost_item)
        props.contracted_cost_item_rates = json.dumps(contracted_cost_item_rates)
        bpy.ops.bim.load_schedule_of_rates(cost_schedule=int(props.schedule_of_rates))
        return {"FINISHED"}


class ContractCostItemRate(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.contract_cost_item_rate"
    bl_label = "Contract Cost Item Rate"
    bl_options = {"REGISTER", "UNDO"}
    cost_item: bpy.props.IntProperty()

    def _execute(self, context):
        props = context.scene.BIMCostProperties
        self.file = IfcStore.get_file()
        contracted_cost_item_rates = json.loads(props.contracted_cost_item_rates)
        contracted_cost_item_rates.append(self.cost_item)
        props.contracted_cost_item_rates = json.dumps(contracted_cost_item_rates)
        bpy.ops.bim.load_schedule_of_rates(cost_schedule=int(props.schedule_of_rates))
        return {"FINISHED"}


class CalculateCostItemResourceValue(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.calculate_cost_item_resource_value"
    bl_label = "Calculate Cost Item Resource Value"
    bl_options = {"REGISTER", "UNDO"}
    cost_item: bpy.props.IntProperty()

    def _execute(self, context):
        self.file = IfcStore.get_file()
        ifcopenshell.api.run(
            "cost.calculate_cost_item_resource_value", self.file, cost_item=self.file.by_id(self.cost_item)
        )
        return {"FINISHED"}
