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
        props = context.scene.BIMCostProperties
        props.active_cost_schedule_id = self.cost_schedule

        while len(props.cost_schedule_attributes) > 0:
            props.cost_schedule_attributes.remove(0)

        data = Data.cost_schedules[self.cost_schedule]

        for attribute in IfcStore.get_schema().declaration_by_name("IfcCostSchedule").all_attributes():
            data_type = ifcopenshell.util.attribute.get_primitive_type(attribute)
            if data_type == "entity":
                continue
            new = props.cost_schedule_attributes.add()
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
        return {"FINISHED"}


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
