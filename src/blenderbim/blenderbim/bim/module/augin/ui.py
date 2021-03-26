import bpy.types


class BIM_PT_augin(bpy.types.Panel):
    bl_label = "Augin"
    bl_idname = "BIM_PT_augin"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True

        scene = context.scene
        props = scene.AuginProperties

        if not props.token:
            row = layout.row()
            row.prop(props, "username")
            row = layout.row()
            row.prop(props, "password")
            row = layout.row()
            row.operator("bim.augin_login")
            return

        row = layout.row()
        row.label(text="Logged in as " + props.username)

        if not bpy.context.scene.BIMProperties.ifc_file:
            row = layout.row()
            row.label(text="No IFC Found")
            return

        if props.is_success:
            row = layout.row()
            row.label(text="Upload Successful")
            row = layout.row()
            row.operator("bim.augin_reset")
        else:
            row = layout.row()
            row.prop(props, "project_name")
            row = layout.row()
            row.operator("bim.augin_create_new_model")
