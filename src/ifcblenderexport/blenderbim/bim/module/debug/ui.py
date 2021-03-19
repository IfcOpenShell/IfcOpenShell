import bpy
from bpy.types import Panel


class BIM_PT_debug(Panel):
    bl_label = "IFC Debug"
    bl_idname = "BIM_PT_debug"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout

        props = context.scene.BIMDebugProperties

        row = self.layout.row(align=True)
        row.prop(context.scene.BIMProperties, "ifc_file", text="")
        row.operator("bim.validate_ifc_file", icon="CHECKMARK", text="")
        row.operator("bim.select_ifc_file", icon="FILE_FOLDER", text="")

        row = layout.row()
        row.operator("bim.create_all_shapes")

        row = layout.row()
        row.operator("bim.profile_import_ifc")

        row = layout.row()
        row.prop(props, "step_id", text="")
        row = layout.row()
        row.operator("bim.create_shape_from_step_id")

        row = layout.row()
        row.prop(props, "number_of_polygons", text="")
        row = layout.row()
        row.operator("bim.select_high_polygon_meshes")

        layout.label(text="Inspector:")

        row = layout.row(align=True)
        if len(props.step_id_breadcrumb) >= 2:
            row.operator("bim.rewind_inspector", icon="FRAME_PREV", text="")
        row.prop(props, "active_step_id", text="")
        row = layout.row(align=True)
        row.operator("bim.inspect_from_step_id").step_id = bpy.context.scene.BIMDebugProperties.active_step_id
        row.operator("bim.inspect_from_object")

        if props.attributes:
            layout.label(text="Direct attributes:")

        for index, attribute in enumerate(props.attributes):
            row = layout.row(align=True)
            row.prop(attribute, "name", text="")
            row.prop(attribute, "string_value", text="")
            if attribute.int_value:
                row.operator(
                    "bim.inspect_from_step_id", icon="DISCLOSURE_TRI_RIGHT", text=""
                ).step_id = attribute.int_value

        if props.inverse_attributes:
            layout.label(text="Inverse attributes:")

        for index, attribute in enumerate(props.inverse_attributes):
            row = layout.row(align=True)
            row.prop(attribute, "name", text="")
            row.prop(attribute, "string_value", text="")
            if attribute.int_value:
                row.operator(
                    "bim.inspect_from_step_id", icon="DISCLOSURE_TRI_RIGHT", text=""
                ).step_id = attribute.int_value

        if props.inverse_references:
            layout.label(text="Inverse references:")

        for index, attribute in enumerate(props.inverse_references):
            row = layout.row(align=True)
            row.prop(attribute, "string_value", text="")
            if attribute.int_value:
                row.operator(
                    "bim.inspect_from_step_id", icon="DISCLOSURE_TRI_RIGHT", text=""
                ).step_id = attribute.int_value
