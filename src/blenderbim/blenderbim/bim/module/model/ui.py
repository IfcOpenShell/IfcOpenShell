from bpy.types import Panel
from blenderbim.bim.ifc import IfcStore


class BIM_PT_authoring(Panel):
    bl_idname = "BIM_PT_authoring"
    bl_label = "Authoring"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "BlenderBIM"

    @classmethod
    def poll(cls, context):
        return IfcStore.get_file()

    def draw(self, context):
        tprops = context.scene.BIMTypeProperties
        col = self.layout.column(align=True)
        col.prop(tprops, "ifc_class", text="", icon="FILE_VOLUME")
        col.prop(tprops, "relating_type", text="", icon="FILE_3D")
        col.operator("bim.add_type_instance", icon="ADD")


class BIM_PT_authoring_architectural(Panel):
    bl_label = "Architectural"
    bl_idname = "BIM_PT_authoring_architectural"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "BlenderBIM"
    bl_parent_id = "BIM_PT_authoring"

    def draw(self, context):
        row = self.layout.row(align=True)
        row.operator("bim.join_wall", icon="MOD_SKIN", text="T").join_type = "T"
        row.operator("bim.join_wall", icon="MOD_SKIN", text="L").join_type = "L"
        row.operator("bim.join_wall", icon="MOD_SKIN", text="V").join_type = "V"
        row.operator("bim.join_wall", icon="X", text="").join_type = ""
        row = self.layout.row(align=True)
        row.operator("bim.align_wall", icon="ANCHOR_TOP", text="Ext.").align_type = "EXTERIOR"
        row.operator("bim.align_wall", icon="ANCHOR_CENTER", text="C/L").align_type = "CENTERLINE"
        row.operator("bim.align_wall", icon="ANCHOR_BOTTOM", text="Int.").align_type = "INTERIOR"
        row = self.layout.row(align=True)
        row.operator("bim.flip_wall", icon="ORIENTATION_NORMAL", text="Flip")
        row.operator("bim.split_wall", icon="MOD_PHYSICS", text="Split")


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
