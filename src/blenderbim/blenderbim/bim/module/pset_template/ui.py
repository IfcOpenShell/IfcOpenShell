import bpy
from bpy.types import Panel
from blenderbim.bim.ifc import IfcStore
from ifcopenshell.api.pset_template.data import Data


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
        row.operator("bim.save_pset_template_file", text="", icon="EXPORT")

        row = layout.row(align=True)

        if props.pset_templates:
            row.prop(props, "pset_templates", text="", icon="COPY_ID")
        else:
            row.label(text="No Pset Templates", icon="COPY_ID")

        if props.active_pset_template_id:
            row.operator("bim.edit_pset_template", text="", icon="CHECKMARK")
            row.operator("bim.disable_editing_pset_template", text="", icon="X")
        else:
            row.operator("bim.add_pset_template", text="", icon="ADD")
            row.operator("bim.enable_editing_pset_template", text="", icon="GREASEPENCIL")
            row.operator("bim.remove_pset_template", text="", icon="X")

        if not Data.is_loaded and props.pset_template_files:
            Data.load(IfcStore.pset_template_file)

        if not Data.pset_templates:
            return

        if props.active_pset_template_id:
            pset_template = Data.pset_templates[int(props.active_pset_template_id)]
            row = layout.row()
            row.prop(props.active_pset_template, "name")
            row = layout.row()
            row.prop(props.active_pset_template, "description")
            row = layout.row()
            row.prop(props.active_pset_template, "template_type")
            row = layout.row()
            row.prop(props.active_pset_template, "applicable_entity")
        else:
            pset_template = Data.pset_templates[int(props.pset_templates)]
            for name, value in pset_template.items():
                if name == "id" or name == "type" or name == "HasPropertyTemplates":
                    continue
                row = layout.row(align=True)
                row.label(text=name)
                row.label(text=str(value))

        row = layout.row(align=True)
        row.label(text="Property Templates", icon="COPY_ID")
        row.operator("bim.add_prop_template", icon="ADD", text="")

        for prop_template_id in pset_template["HasPropertyTemplates"]:
            prop_template = Data.prop_templates[prop_template_id]
            row = layout.row(align=True)

            if props.active_prop_template_id and props.active_prop_template_id == prop_template_id:
                row.prop(props.active_prop_template, "name", text="")
                row.prop(props.active_prop_template, "description", text="")
                row.prop(props.active_prop_template, "primary_measure_type", text="")
            else:
                row.label(text=prop_template["Name"])
                row.label(text=prop_template["PrimaryMeasureType"])

            if props.active_prop_template_id and props.active_prop_template_id == prop_template_id:
                op = row.operator("bim.edit_prop_template", icon="CHECKMARK", text="")
                row.operator("bim.disable_editing_prop_template", icon="X", text="")
            elif props.active_prop_template_id and props.active_prop_template_id != prop_template_id:
                row.operator("bim.remove_prop_template", icon="X", text="").prop_template = prop_template_id
            else:
                op = row.operator("bim.enable_editing_prop_template", icon="GREASEPENCIL", text="")
                op.prop_template = prop_template_id
                row.operator("bim.remove_prop_template", icon="X", text="").prop_template = prop_template_id
