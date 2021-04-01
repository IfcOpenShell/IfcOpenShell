import bpy
from bpy.types import Panel


class BIM_PT_search(Panel):
    bl_label = "IFC Search"
    bl_idname = "BIM_PT_search"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"

    def draw(self, context):
        props = context.scene.BIMSearchProperties

        row = self.layout.row()
        row.prop(props, "should_use_regex")
        row = self.layout.row()
        row.prop(props, "should_ignorecase")

        row = self.layout.row(align=True)
        row.operator("bim.reset_object_colours", icon="BRUSH_DATA")

        row = self.layout.row(align=True)
        row.prop(props, "global_id", text="", icon="TRACKER")
        row.operator("bim.select_global_id", text="", icon="VIEWZOOM")

        row = self.layout.row(align=True)
        row.prop(props, "ifc_class", text="", icon="OBJECT_DATA")
        row.operator("bim.select_ifc_class", text="", icon="VIEWZOOM")
        row.operator("bim.colour_by_class", text="", icon="BRUSH_DATA")

        row = self.layout.row(align=True)
        row.prop(props, "search_attribute_name", text="", icon="PROPERTIES")
        row.prop(props, "search_attribute_value", text="")
        row.operator("bim.select_attribute", text="", icon="VIEWZOOM")
        row.operator("bim.colour_by_attribute", text="", icon="BRUSH_DATA")

        row = self.layout.row(align=True)
        row.prop(props, "search_pset_name", text="", icon="COPY_ID")
        row.prop(props, "search_prop_name", text="")
        row.prop(props, "search_pset_value", text="")
        row.operator("bim.select_pset", text="", icon="VIEWZOOM")
        row.operator("bim.colour_by_pset", text="", icon="BRUSH_DATA")
