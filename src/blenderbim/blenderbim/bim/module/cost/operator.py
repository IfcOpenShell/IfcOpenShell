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

        while len(self.props.cost_items) > 0:
            self.props.cost_items.remove(0)

        for related_object_id in Data.cost_schedules[self.cost_schedule]["RelatedObjects"]:
            self.create_new_cost_item_li(related_object_id, 0)
        return {"FINISHED"}

    def create_new_cost_item_li(self, related_object_id, level_index):
        cost_item = Data.cost_items[related_object_id]
        new = self.props.cost_items.add()
        new.name = cost_item["Name"] or "Unnamed"
        new.ifc_definition_id = related_object_id
        new.is_expanded = False
        new.level_index = level_index
        if cost_item["RelatedObjects"]:
            new.has_children = True
            for related_object_id in cost_item["RelatedObjects"]:
                self.create_new_cost_item_li(related_object_id, level_index + 1)


class DisableEditingCostSchedule(bpy.types.Operator):
    bl_idname = "bim.disable_editing_cost_schedule"
    bl_label = "Disable Editing Cost Schedule"

    def execute(self, context):
        props = context.scene.BIMCostProperties
        props.active_cost_schedule_id = 0
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
            **{"cost_schedule": self.file.by_id(props.active_cost_schedule_id), "attributes": attributes}
        )
        Data.load(IfcStore.get_file())
        bpy.ops.bim.disable_editing_cost_schedule()
        return {"FINISHED"}


class AddCostItem(bpy.types.Operator):
    bl_idname = "bim.add_cost_item"
    bl_label = "Add Cost Item"
    cost_schedule: bpy.props.IntProperty()

    def execute(self, context):
        props = context.scene.BIMCostProperties
        self.file = IfcStore.get_file()
        if len(props.cost_items):
            data = {"cost_item": self.file.by_id(props.cost_items[props.active_cost_item_index].ifc_definition_id)}
        else:
            data = {"cost_schedule": self.file.by_id(self.cost_schedule)}
        ifcopenshell.api.run("cost.add_cost_item", self.file, **data)
        Data.load(self.file)
        bpy.ops.bim.enable_editing_cost_schedule(cost_schedule = self.cost_schedule)
        return {"FINISHED"}
