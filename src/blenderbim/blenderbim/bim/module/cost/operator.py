import bpy
import json
import ifcopenshell.api
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
        attributes = {}
        for attribute in props.cost_schedule_attributes:
            if attribute.is_null:
                attributes[attribute.name] = None
            else:
                if attribute.data_type == "string":
                    attributes[attribute.name] = attribute.string_value
                elif attribute.data_type == "enum":
                    attributes[attribute.name] = attribute.enum_value
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

        for attribute in IfcStore.get_schema().declaration_by_name("IfcCostSchedule").all_attributes():
            data_type = ifcopenshell.util.attribute.get_primitive_type(attribute)
            if data_type == "entity":
                continue
            new = self.props.cost_schedule_attributes.add()
            new.name = attribute.name()
            new.is_null = data[attribute.name()] is None
            new.is_optional = attribute.optional()
            new.data_type = data_type
            if attribute.name() in ["SubmittedOn", "UpdateDate"]:
                new.string_value = "" if new.is_null else data[attribute.name()].isoformat()
            elif data_type == "string":
                new.string_value = "" if new.is_null else data[attribute.name()]
            elif data_type == "enum":
                new.enum_items = json.dumps(ifcopenshell.util.attribute.get_enum_items(attribute))
                if data[attribute.name()]:
                    new.enum_value = data[attribute.name()]


class EnableEditingCostItems(bpy.types.Operator):
    bl_idname = "bim.enable_editing_cost_items"
    bl_label = "Enable Editing Cost Items"
    cost_schedule: bpy.props.IntProperty()

    def execute(self, context):
        self.props = context.scene.BIMCostProperties
        self.props.active_cost_schedule_id = self.cost_schedule
        while len(self.props.cost_items) > 0:
            self.props.cost_items.remove(0)

        self.contracted_cost_items = json.loads(self.props.contracted_cost_items)
        for related_object_id in Data.cost_schedules[self.cost_schedule]["RelatedObjects"]:
            self.create_new_cost_item_li(related_object_id, 0)
        self.props.is_editing = "COST_ITEMS"
        return {"FINISHED"}

    def create_new_cost_item_li(self, related_object_id, level_index):
        cost_item = Data.cost_items[related_object_id]
        new = self.props.cost_items.add()
        new.name = cost_item["Name"] or "Unnamed"
        new.ifc_definition_id = related_object_id
        new.is_expanded = related_object_id not in self.contracted_cost_items
        new.level_index = level_index
        if cost_item["RelatedObjects"]:
            new.has_children = True
            if new.is_expanded:
                for related_object_id in cost_item["RelatedObjects"]:
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

        for attribute in IfcStore.get_schema().declaration_by_name("IfcCostItem").all_attributes():
            data_type = ifcopenshell.util.attribute.get_primitive_type(attribute)
            if data_type == "entity":
                continue
            new = props.cost_item_attributes.add()
            new.name = attribute.name()
            new.is_null = data[attribute.name()] is None
            new.is_optional = attribute.optional()
            new.data_type = data_type
            if data_type == "string":
                new.string_value = "" if new.is_null else data[attribute.name()]
            elif data_type == "boolean":
                new.bool_value = False if new.is_null else data[attribute.name()]
            elif data_type == "integer":
                new.int_value = 0 if new.is_null else data[attribute.name()]
            elif data_type == "enum":
                new.enum_items = json.dumps(ifcopenshell.util.attribute.get_enum_items(attribute))
                if data[attribute.name()]:
                    new.enum_value = data[attribute.name()]
        props.active_cost_item_id = self.cost_item
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
        attributes = {}
        for attribute in props.cost_item_attributes:
            if attribute.is_null:
                attributes[attribute.name] = None
            else:
                if attribute.data_type == "string":
                    attributes[attribute.name] = attribute.string_value
                elif attribute.data_type == "boolean":
                    attributes[attribute.name] = attribute.bool_value
                elif attribute.data_type == "integer":
                    attributes[attribute.name] = attribute.int_value
                elif attribute.data_type == "enum":
                    attributes[attribute.name] = attribute.enum_value
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


class AssignControl(bpy.types.Operator):
    bl_idname = "bim.assign_control"
    bl_label = "Assign Control"
    cost_item: bpy.props.IntProperty()
    related_object: bpy.props.StringProperty()

    def execute(self, context):
        related_objects = (
            [bpy.data.objects.get(self.related_object)] if self.related_object else bpy.context.selected_objects
        )
        for related_object in related_objects:
            self.file = IfcStore.get_file()
            ifcopenshell.api.run(
                "control.assign_control",
                self.file,
                related_object=self.file.by_id(related_object.BIMObjectProperties.ifc_definition_id),
                relating_control=self.file.by_id(self.cost_item),
            )
        Data.load(self.file)
        return {"FINISHED"}


class UnassignControl(bpy.types.Operator):
    bl_idname = "bim.unassign_control"
    bl_label = "Unassign Control"
    cost_item: bpy.props.IntProperty()
    related_object: bpy.props.StringProperty()

    def execute(self, context):
        related_objects = (
            [bpy.data.objects.get(self.related_object)] if self.related_object else bpy.context.selected_objects
        )
        for related_object in related_objects:
            self.file = IfcStore.get_file()
            ifcopenshell.api.run(
                "control.unassign_control",
                self.file,
                related_object=self.file.by_id(related_object.BIMObjectProperties.ifc_definition_id),
                relating_control=self.file.by_id(self.cost_item),
            )
        Data.load(self.file)
        return {"FINISHED"}
