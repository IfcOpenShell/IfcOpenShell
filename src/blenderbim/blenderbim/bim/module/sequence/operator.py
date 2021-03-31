import bpy
import ifcopenshell.api
from blenderbim.bim.ifc import IfcStore
from ifcopenshell.api.sequence.data import Data


class AddWorkPlan(bpy.types.Operator):
    bl_idname = "bim.add_work_plan"
    bl_label = "Add Work Plan"

    def execute(self, context):
        ifcopenshell.api.run("sequence.add_work_plan", IfcStore.get_file())
        Data.load(IfcStore.get_file())
        return {"FINISHED"}


class RemoveWorkPlan(bpy.types.Operator):
    bl_idname = "bim.remove_work_plan"
    bl_label = "Remove Work Plan"
    work_plan: bpy.props.IntProperty()

    def execute(self, context):
        ifcopenshell.api.run(
            "sequence.remove_work_plan", IfcStore.get_file(), work_plan=IfcStore.get_file().by_id(self.work_plan)
        )
        Data.load(IfcStore.get_file())
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
