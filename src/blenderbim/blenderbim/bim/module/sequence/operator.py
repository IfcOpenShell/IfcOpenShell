import bpy
import json
import ifcopenshell.api
from blenderbim.bim.ifc import IfcStore
from ifcopenshell.api.sequence.data import Data


class LoadWorkPlans(bpy.types.Operator):
    bl_idname = "bim.load_work_plans"
    bl_label = "Load Work Plans"

    def execute(self, context):
        props = context.scene.BIMWorkPlanProperties
        while len(props.work_plans) > 0:
            props.work_plans.remove(0)
        for ifc_definition_id, work_plan in Data.work_plans.items():
            new = props.work_plans.add()
            new.ifc_definition_id = ifc_definition_id
            new.name = work_plan["Name"]  or "Unnamed"
        props.is_editing = True
        bpy.ops.bim.disable_editing_work_plan()
        return {"FINISHED"}

class DisableWorkPlanEditingUI(bpy.types.Operator):
    bl_idname = "bim.disable_work_plan_editing_ui"
    bl_label = "Disable WorkPlan Editing UI"

    def execute(self, context):
        context.scene.BIMWorkPlanProperties.is_editing = False
        return {"FINISHED"}


class AddWorkPlan(bpy.types.Operator):
    bl_idname = "bim.add_work_plan"
    bl_label = "Add Work Plan"

    def execute(self, context):
        ifcopenshell.api.run("sequence.add_work_plan", IfcStore.get_file())
        Data.load(IfcStore.get_file())
        bpy.ops.bim.load_work_plans()
        return {"FINISHED"}


class EditWorkPlan(bpy.types.Operator):
    bl_idname = "bim.edit_work_plan"
    bl_label = "Edit Work Plan"

    def execute(self, context):
        props = context.scene.BIMWorkPlanProperties
        attributes = {}
        for attribute in props.work_plan_attributes:
            if attribute.is_null:
                attributes[attribute.name] = None
            else:
                if attribute.data_type == "string":
                    attributes[attribute.name] = attribute.string_value
                elif attribute.data_type == "enum":
                    attributes[attribute.name] = attribute.enum_value
        self.file = IfcStore.get_file()
        ifcopenshell.api.run(
            "sequence.edit_work_plan", self.file, **{"work_plan": self.file.by_id(props.active_work_plan_id), "attributes": attributes}
        )
        Data.load(IfcStore.get_file())
        bpy.ops.bim.load_work_plans()
        return {"FINISHED"}

class RemoveWorkPlan(bpy.types.Operator):
    bl_idname = "bim.remove_work_plan"
    bl_label = "Remove Work Plan"
    work_plan: bpy.props.IntProperty()

    def execute(self, context):
        props = context.scene.BIMWorkPlanProperties
        self.file = IfcStore.get_file()
        ifcopenshell.api.run("sequence.remove_work_plan", self.file, **{"work_plan": self.file.by_id(self.work_plan)})
        Data.load(IfcStore.get_file())
        bpy.ops.bim.load_work_plans()
        return {"FINISHED"}

class EnableEditingWorkPlan(bpy.types.Operator):
    bl_idname = "bim.enable_editing_work_plan"
    bl_label = "Enable Editing Work Plan"
    work_plan: bpy.props.IntProperty()

    def execute(self, context):
        props = context.scene.BIMWorkPlanProperties
        while len(props.work_plan_attributes) > 0:
            props.work_plan_attributes.remove(0)

        data = Data.work_plans[self.work_plan]

        for attribute in IfcStore.get_schema().declaration_by_name("IfcWorkPlan").all_attributes():
            data_type = ifcopenshell.util.attribute.get_primitive_type(attribute)
            if data_type == "entity":
                continue
            new = props.work_plan_attributes.add()
            new.name = attribute.name()
            new.is_null = data[attribute.name()] is None
            new.is_optional = attribute.optional()
            new.data_type = data_type
            if data_type == "string":
                new.string_value = "" if new.is_null else data[attribute.name()]
            elif data_type == "enum":
                new.enum_items = json.dumps(ifcopenshell.util.attribute.get_enum_items(attribute))
                if data[attribute.name()]:
                    new.enum_value = data[attribute.name()]
        props.active_work_plan_id = self.work_plan
        return {"FINISHED"}

class DisableEditingWorkPlan(bpy.types.Operator):
    bl_idname = "bim.disable_editing_work_plan"
    bl_label = "Disable Editing Work Plan"

    def execute(self, context):
        context.scene.BIMWorkPlanProperties.active_work_plan_id = 0
        return {"FINISHED"}
        return {"FINISHED"}


class LoadTasks(bpy.types.Operator):
    bl_idname = "bim.load_tasks"
    bl_label = "Load Tasks"

    def execute(self, context):
        props = context.scene.BIMTaskProperties
        while len(props.tasks) > 0:
            props.tasks.remove(0)
        for ifc_definition_id, task in Data.tasks.items():
            new = props.tasks.add()
            new.ifc_definition_id = ifc_definition_id
            new.name = task["Name"]
            new.identification = task["Identification"]
        props.is_editing = True
        return {"FINISHED"}


class DisableTaskEditingUI(bpy.types.Operator):
    bl_idname = "bim.disable_task_editing_ui"
    bl_label = "Disable Task Editing UI"

    def execute(self, context):
        context.scene.BIMTaskProperties.is_editing = False
        return {"FINISHED"}
