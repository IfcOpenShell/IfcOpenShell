import bpy
from bpy.types import Panel
from blenderbim.bim.module.geometry.data import Data


class BIM_PT_representations(Panel):
    bl_label = "IFC Representations"
    bl_idname = "BIM_PT_representations"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"

    def draw(self, context):
        layout = self.layout
        props = context.active_object.BIMObjectProperties

        if props.ifc_definition_id not in Data.products:
            Data.load(props.ifc_definition_id)

        representations = Data.products[props.ifc_definition_id]["Representations"]
        if not representations:
            layout.label(text="No representations found")

        row = layout.row(align=True)
        row.prop(bpy.context.scene.BIMProperties, "contexts", text="")
        row.operator("bim.add_representation", icon="ADD", text="")

        for ifc_definition_id, representation in representations.items():
            row = self.layout.row(align=True)
            row.label(text=representation["ContextOfItems"]["ContextType"])
            row.label(text=representation["ContextOfItems"]["ContextIdentifier"])
            row.label(text=representation["ContextOfItems"]["TargetView"])
            row.label(text=representation["RepresentationType"])
            row.operator("bim.switch_representation", icon="OUTLINER_DATA_MESH", text="").ifc_definition_id = ifc_definition_id
            row.operator("bim.remove_representation", icon="X", text="").ifc_definition_id = ifc_definition_id

