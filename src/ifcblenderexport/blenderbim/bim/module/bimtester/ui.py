import bpy
from bpy.types import Panel


class BIM_PT_qa(Panel):
    bl_label = "BIMTester Quality Auditing"
    bl_idname = "BIM_PT_qa"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True

        scene = context.scene
        bimtester_properties = bpy.context.scene.BimTesterProperties

        layout.label(text="Gherkin Setup:")

        row = layout.row(align=True)
        row.prop(bimtester_properties, "features_dir")
        row.operator("bim.select_features_dir", icon="FILE_FOLDER", text="")

        if bimtester_properties.features_dir:
            row = layout.row(align=True)
            row.prop(bimtester_properties, "features_file")

            row = layout.row(align=True)
            row.prop(bimtester_properties, "scenario")
        else:
            return

        if str(context.scene.BimTesterProperties.features_file) != '': # To handle the error when no .feature file exists in the folder
            row = layout.row()
            row.operator("bim.execute_bim_tester")

            row = layout.row()
            row.operator("bim.bim_tester_purge")

            layout.label(text="Quality Auditing:")

            row = layout.row()
            row.prop(bimtester_properties, "qa_reject_element_reason")
            row = layout.row()
            row.operator("bim.reject_element")

            row = layout.row()
            row.prop(bimtester_properties, "audit_ifc_class")

            row = layout.row(align=True)
            row.operator("bim.approve_class")
            row.operator("bim.reject_class")

            row = layout.row()
            row.operator("bim.select_audited")
