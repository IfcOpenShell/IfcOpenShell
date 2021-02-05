from bpy.types import Panel


class BIM_PT_qto_utilities(Panel):
    bl_idname = "BIM_PT_qto_utilities"
    bl_label = "Quantity Take-off"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "BlenderBIM"

    def draw(self, context):
        layout = self.layout
        props = context.scene.BIMQtoProperties

        row = layout.row()
        row.prop(props, "qto_result", text="Results")

        row = layout.row(align=True)
        row.operator("bim.calculate_edge_lengths")
        row = layout.row(align=True)
        row.operator("bim.calculate_face_areas")
        row = layout.row(align=True)
        row.operator("bim.calculate_object_volumes")
