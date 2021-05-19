from bpy.types import Panel
from blenderbim.bim.ifc import IfcStore


class BIM_PT_authoring(Panel):
    bl_idname = "BIM_PT_authoring"
    bl_label = "Authoring"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "BlenderBIM"

    def draw(self, context):
        tprops = context.scene.BIMTypeProperties
        col = self.layout.column(align=True)
        col.prop(tprops, "ifc_class", text="", icon="FILE_VOLUME")
        col.prop(tprops, "relating_type", text="", icon="FILE_3D")
        col.operator("bim.add_type_instance", icon="ADD")


class BIM_PT_misc_utilities(Panel):
    bl_idname = "BIM_PT_misc_utilities"
    bl_label = "Miscellaneous"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "BlenderBIM"

    def draw(self, context):
        layout = self.layout
        props = context.scene.BIMProperties

        row = layout.row()
        row.prop(props, "override_colour", text="")
        row = layout.row(align=True)
        row.operator("bim.set_override_colour")
        row = layout.row(align=True)
        row.operator("bim.set_viewport_shadow_from_sun")
        row = layout.row(align=True)
        row.operator("bim.snap_spaces_together")
