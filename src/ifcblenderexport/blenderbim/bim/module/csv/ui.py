from bpy.types import Panel
from blenderbim.bim.ifc import IfcStore


class BIM_PT_ifccsv(Panel):
    bl_label = "IFC CSV Import/Export"
    bl_idname = "BIM_PT_ifccsv"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout

        scene = context.scene
        props = scene.CsvProperties

        if IfcStore.get_file():       
            row = layout.row()
            row.prop(props, "should_load_from_memory")
          
        if not IfcStore.get_file() or not props.should_load_from_memory:
            row = layout.row(align=True)
            row.prop(props, "csv_ifc_file")
            row.operator("bim.import_ifccsv", icon="FILE_FOLDER", text="")
            row = layout.row(align=True)
            row.prop(props, "ifc_selector")
            row.operator("bim.eyedrop_ifccsv", icon="EYEDROPPER", text="")

        row = layout.row()
        row.label(text="Add IFC attributes to filter", icon="FILE_BLANK")
        row.operator("bim.add_csv_attribute")

        for index, attribute in enumerate(props.csv_attributes):
            row = layout.row(align=True)
            row.prop(attribute, "name", text="")
            row.operator("bim.remove_csv_attribute", icon="X", text="").index = index

        row = layout.row(align=True)
        row.prop(props, "csv_delimiter")

        if(props.csv_delimiter == 'CUSTOM'):
            row = layout.row(align=True)
            row.prop(props, "csv_custom_delimiter")

        row = layout.row(align=True)
        row.operator("bim.export_ifccsv", icon="EXPORT")
        row.operator("bim.import_ifccsv", icon="IMPORT")

