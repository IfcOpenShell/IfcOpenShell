import bpy
import blenderbim.bim.module.context.add_context as add_context
import blenderbim.bim.module.context.remove_context as remove_context
from blenderbim.bim.ifc import IfcStore
from blenderbim.bim.module.context.data import Data


class AddSubcontext(bpy.types.Operator):
    bl_idname = "bim.add_subcontext"
    bl_label = "Add Subcontext"
    context: bpy.props.StringProperty()
    subcontext: bpy.props.StringProperty()
    target_view: bpy.props.StringProperty()

    def execute(self, context):
        self.file = IfcStore.get_file()
        add_context.Usecase(
            self.file,
            {
                "context": self.context or bpy.context.scene.BIMProperties.available_contexts,
                "subcontext": self.subcontext or bpy.context.scene.BIMProperties.available_subcontexts,
                "target_view": self.target_view or bpy.context.scene.BIMProperties.available_target_views,
            },
        ).execute()
        Data.load()
        return {"FINISHED"}


class RemoveSubcontext(bpy.types.Operator):
    bl_idname = "bim.remove_subcontext"
    bl_label = "Remove Context"
    ifc_definition_id: bpy.props.IntProperty()

    def execute(self, context):
        self.file = IfcStore.get_file()
        usecase = remove_context.Usecase(self.file, {"context": self.file.by_id(self.ifc_definition_id)})
        usecase.execute()
        Data.load()
        return {"FINISHED"}
