import bpy
import ifcopenshell.api
from blenderbim.bim.ifc import IfcStore
from ifcopenshell.api.context.data import Data


class AddSubcontext(bpy.types.Operator):
    bl_idname = "bim.add_subcontext"
    bl_label = "Add Subcontext"
    context: bpy.props.StringProperty()
    subcontext: bpy.props.StringProperty()
    target_view: bpy.props.StringProperty()

    def execute(self, context):
        self.file = IfcStore.get_file()
        ifcopenshell.api.run(
            "context.add_context",
            self.file,
            **{
                "context": self.context or bpy.context.scene.BIMProperties.available_contexts,
                "subcontext": self.subcontext or bpy.context.scene.BIMProperties.available_subcontexts,
                "target_view": self.target_view or bpy.context.scene.BIMProperties.available_target_views,
            },
        )
        Data.load(IfcStore.get_file())
        return {"FINISHED"}


class RemoveSubcontext(bpy.types.Operator):
    bl_idname = "bim.remove_subcontext"
    bl_label = "Remove Context"
    ifc_definition_id: bpy.props.IntProperty()

    def execute(self, context):
        self.file = IfcStore.get_file()
        ifcopenshell.api.run(
            "context.remove_context", self.file, **{"context": self.file.by_id(self.ifc_definition_id)}
        )
        Data.load(IfcStore.get_file())
        return {"FINISHED"}
