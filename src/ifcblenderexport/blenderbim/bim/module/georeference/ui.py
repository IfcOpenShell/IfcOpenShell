from bpy.types import Panel
from ifcopenshell.api.georeference.data import Data
from blenderbim.bim.ifc import IfcStore

class BIM_PT_gis(Panel):
    bl_label = "IFC Georeferencing"
    bl_idname = "BIM_PT_gis"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"

    @classmethod
    def poll(cls, context):
        return IfcStore.get_file()

    def draw(self, context):
        props = context.scene.BIMGeoreferenceProperties
        if not Data.is_loaded:
            Data.load(IfcStore.get_file())

        if props.is_editing:
            return self.draw_editable_ui(context)
        self.draw_ui(context)

    def draw_editable_ui(self, context):
        props = context.scene.BIMGeoreferenceProperties
        row = self.layout.row(align=True)
        row.label(text="Map Conversion", icon="GRID")
        row.operator("bim.edit_georeferencing", icon="CHECKMARK", text="")
        row.operator("bim.disable_editing_georeferencing", icon="X", text="")

        for attribute in props.map_conversion:
            if attribute.name == "XAxisAbscissa" and hasattr(context.scene, "sun_pos_properties"):
                row = self.layout.row(align=True)
                row.operator("bim.get_north_offset", text="Set IFC North")
                row.operator("bim.set_north_offset", text="Set Blender North")
            row = self.layout.row(align=True)
            if attribute.data_type == "string":
                row.prop(attribute, "string_value", text=attribute.name)
            elif attribute.data_type == "integer":
                row.prop(attribute, "int_value", text=attribute.name)
            elif attribute.data_type == "float":
                row.prop(attribute, "float_value", text=attribute.name)
            elif attribute.data_type == "boolean":
                row.prop(attribute, "bool_value", text=attribute.name)
            if attribute.is_optional:
                row.prop(attribute, "is_null", icon="RADIOBUT_OFF" if attribute.is_null else "RADIOBUT_ON", text="")

        row = self.layout.row(align=True)
        row.label(text="Projected CRS", icon="WORLD")

        for attribute in props.projected_crs:
            row = self.layout.row(align=True)
            if attribute.data_type == "string":
                row.prop(attribute, "string_value", text=attribute.name)
            elif attribute.data_type == "integer":
                row.prop(attribute, "int_value", text=attribute.name)
            elif attribute.data_type == "float":
                row.prop(attribute, "float_value", text=attribute.name)
            elif attribute.data_type == "boolean":
                row.prop(attribute, "bool_value", text=attribute.name)
            row.prop(attribute, "is_null", icon="RADIOBUT_OFF" if attribute.is_null else "RADIOBUT_ON", text="")

        row = self.layout.row(align=True)
        row.prop(props, "map_unit_type", text="MapUnit")
        if props.map_unit_type == "IfcSIUnit":
            row.prop(props, "map_unit_si", text="")
        elif props.map_unit_type == "IfcConversionBasedUnit":
            row.prop(props, "map_unit_imperial", text="")
        row.prop(props, "is_map_unit_null", icon="RADIOBUT_OFF" if props.is_map_unit_null else "RADIOBUT_ON", text="")

    def draw_ui(self, context):
        props = context.scene.BIMGeoreferenceProperties

        if not Data.map_conversion and IfcStore.get_file().schema != "IFC2X3":
            row = self.layout.row(align=True)
            row.label(text="Not Georeferenced")
            row.operator("bim.add_georeferencing", icon="ADD", text="")

        if props.has_blender_offset:
            row = self.layout.row()
            row.label(text="Blender Offset", icon="TRACKING_REFINE_FORWARDS")

            row = self.layout.row(align=True)
            row.label(text="Type")
            row.label(text=props.blender_offset_type)
            row = self.layout.row(align=True)
            row.label(text="Eastings")
            row.label(text=props.blender_eastings)
            row = self.layout.row(align=True)
            row.label(text="Northings")
            row.label(text=props.blender_northings)
            row = self.layout.row(align=True)
            row.label(text="OrthogonalHeight")
            row.label(text=props.blender_orthogonal_height)
            row = self.layout.row(align=True)
            row.label(text="XAxisAbscissa")
            row.label(text=props.blender_x_axis_abscissa)
            row = self.layout.row(align=True)
            row.label(text="XAxisOrdinate")
            row.label(text=props.blender_x_axis_ordinate)
        elif IfcStore.get_file().schema == "IFC2X3":
            row = self.layout.row()
            row.label(text="Not Georeferenced")

        if Data.map_conversion:
            row = self.layout.row(align=True)
            row.label(text="Map Conversion", icon="GRID")
            row.operator("bim.enable_editing_georeferencing", icon="GREASEPENCIL", text="")
            row.operator("bim.remove_georeferencing", icon="X", text="")

        for key, value in Data.map_conversion.items():
            if key == "id" or key == "type" or key == "SourceCRS" or key == "TargetCRS" or not value:
                continue
            row = self.layout.row(align=True)
            row.label(text=key)
            row.label(text=str(value))

        if Data.projected_crs:
            row = self.layout.row(align=True)
            row.label(text="Projected CRS", icon="WORLD")

        for key, value in Data.projected_crs.items():
            if key == "id" or key == "type" or not value:
                continue
            if key == "MapUnit":
                unit_value = value.get("Prefix", "") or ""
                unit_value += value["Name"]
                value = unit_value
            row = self.layout.row(align=True)
            row.label(text=key)
            row.label(text=str(value))


class BIM_PT_gis_utilities(Panel):
    bl_idname = "BIM_PT_gis_utilities"
    bl_label = "Georeferencing Utilities"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "BlenderBIM"

    def draw(self, context):
        props = context.scene.BIMGeoreferenceProperties

        row = self.layout.row(align=True)
        row.prop(props, "coordinate_input", text="Input")
        row.operator("bim.get_cursor_location", text="", icon="TRACKER")
        row = self.layout.row(align=True)
        row.prop(props, "coordinate_output", text="Output")
        row.operator("bim.set_cursor_location", text="", icon="TRACKER")

        row = self.layout.row(align=True)
        row.operator("bim.convert_local_to_global", text="Local to Global")
        row.operator("bim.convert_global_to_local", text="Global to Local")
