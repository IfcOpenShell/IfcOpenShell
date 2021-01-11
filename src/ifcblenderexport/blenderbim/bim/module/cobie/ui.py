from bpy.types import Panel
from blenderbim.bim.ifc import IfcStore


class BIM_PT_cobie(Panel):
    bl_label = "IFC COBie"
    bl_idname = "BIM_PT_cobie"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True

        scene = context.scene
        props = scene.BIMProperties

        row = layout.row(align=True)
        row.prop(props, "cobie_ifc_file")
        row.operator("bim.select_cobie_ifc_file", icon="FILE_FOLDER", text="")

        row = layout.row()
        row.prop(props, "cobie_types")
        row = layout.row()
        row.prop(props, "cobie_components")

        row = layout.row(align=True)
        row.prop(props, "cobie_json_file")
        row.operator("bim.select_cobie_json_file", icon="FILE_FOLDER", text="")

        row = layout.row()
        op = row.operator("bim.execute_ifc_cobie", text="CSV")
        op.file_format = "csv"
        op = row.operator("bim.execute_ifc_cobie", text="ODS")
        op.file_format = "ods"
        op = row.operator("bim.execute_ifc_cobie", text="XLSX")
        op.file_format = "xlsx"
