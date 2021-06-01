import os
import bpy
import json
import ifcopenshell.api
import blenderbim.bim.helper
from blenderbim.bim.module.cost.prop import purge
from blenderbim.bim.ifc import IfcStore
from ifcopenshell.api.cost.data import Data


class AddCostSchedule(bpy.types.Operator):
    bl_idname = "bim.add_cost_schedule"
    bl_label = "Add Cost Schedule"

    def execute(self, context):
        ifcopenshell.api.run("cost.add_cost_schedule", IfcStore.get_file())
        Data.load(IfcStore.get_file())
        return {"FINISHED"}


class EditCostSchedule(bpy.types.Operator):
    bl_idname = "bim.edit_cost_schedule"
    bl_label = "Edit Cost Schedule"

    def execute(self, context):
        props = context.scene.BIMCostProperties
        attributes = blenderbim.bim.helper.export_attributes(props.cost_schedule_attributes)
        self.file = IfcStore.get_file()
        ifcopenshell.api.run(
            "cost.edit_cost_schedule",
            self.file,
            **{"cost_schedule": self.file.by_id(props.active_cost_schedule_id), "attributes": attributes},
        )
        Data.load(IfcStore.get_file())
        bpy.ops.bim.disable_editing_cost_schedule()
        return {"FINISHED"}


class RemoveCostSchedule(bpy.types.Operator):
    bl_idname = "bim.remove_cost_schedule"
    bl_label = "Remove Cost Schedule"
    cost_schedule: bpy.props.IntProperty()

    def execute(self, context):
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
    cost_schedule: bpy.props.IntProperty()

    def execute(self, context):
        self.props = context.scene.BIMCostProperties
        self.props.active_cost_schedule_id = self.cost_schedule
        while len(self.props.cost_schedule_attributes) > 0:
            self.props.cost_schedule_attributes.remove(0)
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
    cost_schedule: bpy.props.IntProperty()

    def execute(self, context):
        if context.preferences.addons["blenderbim"].preferences.should_play_chaching_sound:
            # lol
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
        self.props = context.scene.BIMCostProperties
        self.props.active_cost_schedule_id = self.cost_schedule
        while len(self.props.cost_items) > 0:
            self.props.cost_items.remove(0)

        self.contracted_cost_items = json.loads(self.props.contracted_cost_items)
        for related_object_id in Data.cost_schedules[self.cost_schedule]["Controls"]:
            self.create_new_cost_item_li(related_object_id, 0)
        self.props.is_editing = "COST_ITEMS"
        return {"FINISHED"}

    def create_new_cost_item_li(self, related_object_id, level_index):
        cost_item = Data.cost_items[related_object_id]
        new = self.props.cost_items.add()
        new.ifc_definition_id = related_object_id
        new.name = cost_item["Name"] or "Unnamed"
        new.is_expanded = related_object_id not in self.contracted_cost_items
        new.level_index = level_index
        if cost_item["IsNestedBy"]:
            new.has_children = True
            if new.is_expanded:
                for related_object_id in cost_item["IsNestedBy"]:
                    self.create_new_cost_item_li(related_object_id, level_index + 1)

        return {"FINISHED"}


class DisableEditingCostSchedule(bpy.types.Operator):
    bl_idname = "bim.disable_editing_cost_schedule"
    bl_label = "Disable Editing Cost Schedule"

    def execute(self, context):
        context.scene.BIMCostProperties.active_cost_schedule_id = 0
        return {"FINISHED"}


class AddSummaryCostItem(bpy.types.Operator):
    bl_idname = "bim.add_summary_cost_item"
    bl_label = "Add Cost Item"
    cost_schedule: bpy.props.IntProperty()

    def execute(self, context):
        props = context.scene.BIMCostProperties
        self.file = IfcStore.get_file()
        ifcopenshell.api.run("cost.add_cost_item", self.file, **{"cost_schedule": self.file.by_id(self.cost_schedule)})
        Data.load(self.file)
        bpy.ops.bim.enable_editing_cost_items(cost_schedule=self.cost_schedule)
        return {"FINISHED"}


class AddCostItem(bpy.types.Operator):
    bl_idname = "bim.add_cost_item"
    bl_label = "Add Cost Item"
    cost_item: bpy.props.IntProperty()

    def execute(self, context):
        props = context.scene.BIMCostProperties
        self.file = IfcStore.get_file()
        ifcopenshell.api.run("cost.add_cost_item", self.file, **{"cost_item": self.file.by_id(self.cost_item)})
        Data.load(self.file)
        bpy.ops.bim.enable_editing_cost_items(cost_schedule=props.active_cost_schedule_id)
        return {"FINISHED"}


class ExpandCostItem(bpy.types.Operator):
    bl_idname = "bim.expand_cost_item"
    bl_label = "Expand Cost Item"
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
    cost_item: bpy.props.IntProperty()

    def execute(self, context):
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
    cost_item: bpy.props.IntProperty()

    def execute(self, context):
        props = context.scene.BIMCostProperties
        while len(props.cost_item_attributes) > 0:
            props.cost_item_attributes.remove(0)

        data = Data.cost_items[self.cost_item]
        blenderbim.bim.helper.import_attributes("IfcCostItem", props.cost_item_attributes, data)
        props.active_cost_item_id = self.cost_item
        props.cost_item_editing_type = "ATTRIBUTES"
        return {"FINISHED"}


class DisableEditingCostItem(bpy.types.Operator):
    bl_idname = "bim.disable_editing_cost_item"
    bl_label = "Disable Editing Cost Item"

    def execute(self, context):
        context.scene.BIMCostProperties.active_cost_item_id = 0
        return {"FINISHED"}


class EditCostItem(bpy.types.Operator):
    bl_idname = "bim.edit_cost_item"
    bl_label = "Edit Cost Item"

    def execute(self, context):
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


class AssignCostItemProduct(bpy.types.Operator):
    bl_idname = "bim.assign_cost_item_product"
    bl_label = "Assign Control"
    cost_item: bpy.props.IntProperty()
    related_object: bpy.props.StringProperty()

    def execute(self, context):
        related_objects = (
            [bpy.data.objects.get(self.related_object)] if self.related_object else bpy.context.selected_objects
        )
        self.file = IfcStore.get_file()
        ifcopenshell.api.run(
            "cost.assign_cost_item_product",
            self.file,
            cost_item=self.file.by_id(self.cost_item),
            products=[
                self.file.by_id(o.BIMObjectProperties.ifc_definition_id)
                for o in related_objects
                if o.BIMObjectProperties.ifc_definition_id
            ],
        )
        Data.load(self.file)
        return {"FINISHED"}


class UnassignCostItemProduct(bpy.types.Operator):
    bl_idname = "bim.unassign_cost_item_product"
    bl_label = "Unassign Control"
    cost_item: bpy.props.IntProperty()
    related_object: bpy.props.StringProperty()

    def execute(self, context):
        related_objects = (
            [bpy.data.objects.get(self.related_object)] if self.related_object else bpy.context.selected_objects
        )
        self.file = IfcStore.get_file()
        ifcopenshell.api.run(
            "cost.unassign_cost_item_product",
            self.file,
            cost_item=self.file.by_id(self.cost_item),
            products=[
                self.file.by_id(o.BIMObjectProperties.ifc_definition_id)
                for o in related_objects
                if o.BIMObjectProperties.ifc_definition_id
            ],
        )
        Data.load(self.file)
        return {"FINISHED"}


class EnableEditingCostItemQuantities(bpy.types.Operator):
    bl_idname = "bim.enable_editing_cost_item_quantities"
    bl_label = "Enable Editing Cost Item Quantities"
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
    cost_item: bpy.props.IntProperty()
    ifc_class: bpy.props.StringProperty()

    def execute(self, context):
        self.file = IfcStore.get_file()
        self.props = context.scene.BIMCostProperties
        if self.props.quantity_types == "QTO":
            self.add_quantities_from_qto_filter()
        else:
            self.add_manual_quantity()
        Data.load(self.file)
        return {"FINISHED"}

    def add_quantities_from_qto_filter(self):
        ifcopenshell.api.run(
            "cost.assign_cost_item_product_quantities",
            self.file,
            cost_item=self.file.by_id(self.cost_item),
            prop_name=self.props.quantity_names,
        )

    def add_manual_quantity(self):
        ifcopenshell.api.run(
            "cost.add_cost_item_quantity",
            self.file,
            cost_item=self.file.by_id(self.cost_item),
            ifc_class=self.ifc_class,
        )


class RemoveCostItemQuantity(bpy.types.Operator):
    bl_idname = "bim.remove_cost_item_quantity"
    bl_label = "Add Cost Item Quantity"
    cost_item: bpy.props.IntProperty()
    physical_quantity: bpy.props.IntProperty()

    def execute(self, context):
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
    physical_quantity: bpy.props.IntProperty()

    def execute(self, context):
        self.props = context.scene.BIMCostProperties
        while len(self.props.quantity_attributes) > 0:
            self.props.quantity_attributes.remove(0)
        self.props.active_cost_item_quantity_id = self.physical_quantity
        data = Data.physical_quantities[self.physical_quantity]
        blenderbim.bim.helper.import_attributes(data["type"], self.props.quantity_attributes, data)
        return {"FINISHED"}


class DisableEditingCostItemQuantity(bpy.types.Operator):
    bl_idname = "bim.disable_editing_cost_item_quantity"
    bl_label = "Disable Editing Cost Item Quantity"

    def execute(self, context):
        props = context.scene.BIMCostProperties
        props.active_cost_item_quantity_id = 0
        return {"FINISHED"}


class EditCostItemQuantity(bpy.types.Operator):
    bl_idname = "bim.edit_cost_item_quantity"
    bl_label = "Edit Cost Item Quantity"
    physical_quantity: bpy.props.IntProperty()

    def execute(self, context):
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
    parent: bpy.props.IntProperty()
    cost_type: bpy.props.StringProperty()
    cost_category: bpy.props.StringProperty()

    def execute(self, context):
        self.file = IfcStore.get_file()
        if self.cost_type == "FIXED":
            category = None
        elif self.cost_type == "SUM":
            category = "*"
        elif self.cost_type == "CATEGORY":
            category = self.cost_category
        value = ifcopenshell.api.run("cost.add_cost_value", self.file, parent=self.file.by_id(self.parent))
        ifcopenshell.api.run("cost.edit_cost_value", self.file, cost_value=value, attributes={"Category": category})
        Data.load(self.file)
        return {"FINISHED"}


class RemoveCostItemValue(bpy.types.Operator):
    bl_idname = "bim.remove_cost_item_value"
    bl_label = "Add Cost Item Value"
    cost_value: bpy.props.IntProperty()

    def execute(self, context):
        self.file = IfcStore.get_file()
        ifcopenshell.api.run("cost.remove_cost_item_value", self.file, cost_value=self.file.by_id(self.cost_value))
        Data.load(self.file)
        return {"FINISHED"}


class EnableEditingCostItemValue(bpy.types.Operator):
    bl_idname = "bim.enable_editing_cost_item_value"
    bl_label = "Enable Editing Cost Item Value"
    cost_value: bpy.props.IntProperty()

    def execute(self, context):
        self.props = context.scene.BIMCostProperties
        while len(self.props.cost_value_attributes) > 0:
            self.props.cost_value_attributes.remove(0)
        self.props.active_cost_item_value_id = self.cost_value
        data = Data.cost_values[self.cost_value]

        blenderbim.bim.helper.import_attributes(
            data["type"], self.props.cost_value_attributes, data, self.import_attributes
        )
        return {"FINISHED"}

    def import_attributes(self, name, prop, data):
        if name == "AppliedValue":
            # TODO: for now, only support simple values
            prop.data_type = "float"
            prop.float_value = 0.0 if prop.is_null else data[name]
            return True


class DisableEditingCostItemValue(bpy.types.Operator):
    bl_idname = "bim.disable_editing_cost_item_value"
    bl_label = "Disable Editing Cost Item Value"

    def execute(self, context):
        props = context.scene.BIMCostProperties
        props.active_cost_item_value_id = 0
        return {"FINISHED"}


class EditCostValue(bpy.types.Operator):
    bl_idname = "bim.edit_cost_value"
    bl_label = "Edit Cost Item Value"
    cost_value: bpy.props.IntProperty()

    def execute(self, context):
        props = context.scene.BIMCostProperties
        attributes = blenderbim.bim.helper.export_attributes(props.cost_value_attributes)
        self.file = IfcStore.get_file()
        ifcopenshell.api.run(
            "cost.edit_cost_value",
            self.file,
            **{"cost_value": self.file.by_id(self.cost_value), "attributes": attributes},
        )
        Data.load(IfcStore.get_file())
        bpy.ops.bim.disable_editing_cost_item_value()
        return {"FINISHED"}


class CopyCostItemValues(bpy.types.Operator):
    bl_idname = "bim.copy_cost_item_values"
    bl_label = "Copy Cost Item Values"
    source: bpy.props.IntProperty()
    destination: bpy.props.IntProperty()

    def execute(self, context):
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
    cost_item: bpy.props.IntProperty()

    def execute(self, context):
        self.file = IfcStore.get_file()
        related_products = Data.cost_items[self.cost_item]["Controls"]
        for obj in bpy.context.visible_objects:
            obj.select_set(False)
            if obj.BIMObjectProperties.ifc_definition_id in related_products:
                obj.select_set(True)
        return {"FINISHED"}


class SelectCostScheduleProducts(bpy.types.Operator):
    bl_idname = "bim.select_cost_schedule_products"
    bl_label = "Select Cost Schedule Products"
    cost_schedule: bpy.props.IntProperty()

    def execute(self, context):
        self.file = IfcStore.get_file()
        self.related_products = []
        for cost_item_id in Data.cost_schedules[self.cost_schedule]["Controls"]:
            self.get_related_products(Data.cost_items[cost_item_id])
        self.related_products = set(self.related_products)
        for obj in bpy.context.visible_objects:
            obj.select_set(False)
            if obj.BIMObjectProperties.ifc_definition_id in self.related_products:
                obj.select_set(True)
        return {"FINISHED"}

    def get_related_products(self, cost_item):
        self.related_products.extend(cost_item["Controls"])
        for child_id in cost_item["IsNestedBy"]:
            self.get_related_products(Data.cost_items[child_id])
