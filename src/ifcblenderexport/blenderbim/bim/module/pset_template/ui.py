import bpy
from bpy.types import Panel


class BIM_PT_pset_template(Panel):
    bl_label = "IFC Property Set Templates"
    bl_idname = "BIM_PT_pset_template"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout
        props = context.scene.BIMPsetTemplateProperties

        row = layout.row(align=True)
        row.prop(props, "pset_template_files", text="")

        row = layout.row(align=True)
        row.prop(props, "property_set_templates", text="")
        row.operator("bim.add_property_set_template", text="", icon="ADD")
        row.operator("bim.remove_property_set_template", text="", icon="PANEL_CLOSE")
        row.operator("bim.edit_property_set_template", text="", icon="IMPORT")
        row.operator("bim.save_property_set_template", text="", icon="EXPORT")

        row = layout.row(align=True)
        row.prop(props.active_property_set_template, "name")
        row = layout.row(align=True)
        row.prop(props.active_property_set_template, "description")
        row = layout.row(align=True)
        row.prop(props.active_property_set_template, "template_type")
        row = layout.row(align=True)
        row.prop(props.active_property_set_template, "applicable_entity")

        layout.label(text="Property Templates:")

        row = layout.row(align=True)
        row.operator("bim.add_property_template")

        for index, template in enumerate(props.property_templates):
            row = layout.row(align=True)
            row.prop(template, "name", text="")
            row.prop(template, "description", text="")
            row.prop(template, "primary_measure_type", text="")
            row.operator("bim.remove_property_template", icon="X", text="").index = index

