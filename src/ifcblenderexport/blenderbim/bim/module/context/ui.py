from bpy.types import Panel
from blenderbim.bim.module.context.data import Data
from blenderbim.bim.ifc import IfcStore


class BIM_PT_context(Panel):
    bl_label = "IFC Geometric Representation Contexts"
    bl_idname = "BIM_PT_context"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"

    @classmethod
    def poll(cls, context):
        return IfcStore.get_file()

    def draw(self, context):
        if not Data.is_loaded:
            Data.load()

        props = context.scene.BIMProperties

        row = self.layout.row(align=True)
        row.prop(props, "available_contexts", text="")
        row.prop(props, "available_subcontexts", text="")
        row.prop(props, "available_target_views", text="")
        row.operator("bim.add_subcontext", icon="ADD", text="")

        for ifc_definition_id, context in Data.contexts.items():
            box = self.layout.box()
            row = box.row(align=True)
            row.label(text=context["ContextType"])
            row.operator("bim.remove_subcontext", icon="X", text="").ifc_definition_id = ifc_definition_id
            for ifc_definition_id2, subcontext in context["HasSubContexts"].items():
                row = box.row(align=True)
                row.label(text=subcontext["ContextType"])
                row.label(text=subcontext["ContextIdentifier"])
                row.label(text=subcontext["TargetView"])
                row.operator("bim.remove_subcontext", icon="X", text="").ifc_definition_id = ifc_definition_id2
