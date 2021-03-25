import bpy
from blenderbim.bim.ifc import IfcStore
from blenderbim.bim.module.sequence.data import Data


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
