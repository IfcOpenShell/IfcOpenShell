import bpy
import blenderbim.bim.ifc
import blenderbim.bim.module.context.add_context as add_context
import blenderbim.bim.module.context.remove_context as remove_context
from blenderbim.bim.module.context.data import Data

class AddSubcontext(bpy.types.Operator):
    bl_idname = "bim.add_subcontext"
    bl_label = "Add Subcontext"

    def execute(self, context):
        self.file = blenderbim.bim.ifc.IfcStore.get_file()
        usecase = add_context.Usecase(self.file, {
            "context": bpy.context.scene.BIMProperties.available_contexts,
            "subcontext": bpy.context.scene.BIMProperties.available_subcontexts,
            "target_view": bpy.context.scene.BIMProperties.available_target_views,
        })
        result = usecase.execute()

        Data.load()
        return {"FINISHED"}


class RemoveSubcontext(bpy.types.Operator):
    bl_idname = "bim.remove_subcontext"
    bl_label = "Remove Context"
    ifc_definition_id: bpy.props.IntProperty()

    def execute(self, context):
        self.file = blenderbim.bim.ifc.IfcStore.get_file()
        usecase = remove_context.Usecase(self.file, {
            "context": self.file.by_id(self.ifc_definition_id)
        })
        usecase.execute()

        Data.load()
        return {"FINISHED"}
