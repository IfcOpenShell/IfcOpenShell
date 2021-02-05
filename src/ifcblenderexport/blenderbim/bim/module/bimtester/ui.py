from bpy.types import Panel
from blenderbim.bim.ifc import IfcStore


class BIM_PT_qa(Panel):
    bl_label = "BIMTester"
    bl_idname = "BIM_PT_qa"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"

    def draw(self, context):
        self.layout.use_property_split = True

        props = context.scene.BimTesterProperties

        if IfcStore.get_file():
            row = self.layout.row()
            row.prop(props, "should_load_from_memory")

        if not IfcStore.get_file() or not props.should_load_from_memory:
            row = self.layout.row(align=True)
            row.prop(props, "ifc_file")
            row.operator("bim.select_bimtester_ifc_file", icon="FILE_FOLDER", text="")

        row = self.layout.row(align=True)
        row.prop(props, "feature")
        row.operator("bim.select_feature", icon="FILE_FOLDER", text="")

        row = self.layout.row(align=True)
        row.prop(props, "steps")
        row.operator("bim.select_steps", icon="FILE_FOLDER", text="")

        has_ifc_file = (IfcStore.get_file() and props.should_load_from_memory) or (
            props.ifc_file and not props.should_load_from_memory
        )

        row = self.layout.row(align=True)
        row.operator("bim.execute_bim_tester")
        row.operator("bim.bim_tester_purge")

        if props.feature and has_ifc_file:
            self.layout.label(text="Scenario Authoring:")

            row = self.layout.row(align=True)
            row.prop(props, "scenario")

            row = self.layout.row()
            row.prop(props, "qa_reject_element_reason")
            row = self.layout.row()
            row.operator("bim.reject_element")

            row = self.layout.row()
            row.prop(props, "audit_ifc_class")

            row = self.layout.row(align=True)
            row.operator("bim.approve_class")
            row.operator("bim.reject_class")

            row = self.layout.row()
            row.operator("bim.select_audited")
