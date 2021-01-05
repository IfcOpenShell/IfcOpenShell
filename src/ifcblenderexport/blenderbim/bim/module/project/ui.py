from bpy.types import Panel
from blenderbim.bim.ifc import IfcStore


class BIM_PT_project(Panel):
    bl_label = "IFC Project"
    bl_idname = "BIM_PT_project"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"

    def draw(self, context):
        self.layout.use_property_decorate = False
        self.layout.use_property_split = True
        self.file = IfcStore.get_file()
        props = context.scene.BIMProperties
        if self.file:
            pass
        else:
            row = self.layout.row()
            row.prop(props, "export_schema")
            row = self.layout.row()
            row.prop(context.scene.unit_settings, "system")
            row = self.layout.row()
            row.prop(context.scene.unit_settings, "length_unit")
            row = self.layout.row()
            row.prop(props, "area_unit", text="Area Unit")
            row = self.layout.row()
            row.prop(props, "volume_unit", text="Volume Unit")
            row = self.layout.row()
            row.operator("bim.create_project")
