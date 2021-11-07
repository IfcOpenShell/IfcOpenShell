from bpy.types import Panel

class BIM_PT_cityjson_converter(Panel):
    bl_label = "IFC CityJSON converter"
    bl_idname = "BIM_PT_ifccityjson"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        props = scene.ifccityjson_properties

        row = layout.row(align=True)
        row.prop(props, "input")
        row = layout.row(align=True)
        row.operator("bim.find_cityjson_lod")
        row = layout.row(align=True)
        row.prop(props, "output")
        row = layout.row(align=True)
        row.prop(props, "name")
        row = layout.row(align=True)
        row.prop(props, "split_lod")
        row = layout.row(align=True)
        row.prop(props, "lod")
        if not props.is_lod_found:
            row.enabled = False
        row = layout.row(align=True)
        row.operator("bim.convert_cityjson2ifc")
