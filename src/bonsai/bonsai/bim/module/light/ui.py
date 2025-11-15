# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of Bonsai.
#
# Bonsai is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Bonsai is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Bonsai.  If not, see <http://www.gnu.org/licenses/>.

import calendar
import bpy
import bonsai.tool as tool
from typing import TYPE_CHECKING
from bonsai.bim.module.light.data import SolarData


def get_enum_items(data, prop_name, context=None):
    prop = data.__annotations__[prop_name]
    items = prop.keywords.get("items")
    if items is None:
        return
    if not isinstance(items, (list, tuple)):
        items = items(data, context or bpy.context)
    return items


def prop_with_search(layout, data, prop_name, **kwargs):
    row = layout.row(align=True)
    row.prop(data, prop_name, **kwargs)
    try:
        if len(get_enum_items(data, prop_name)) > 10:
            row.context_pointer_set(name="data", data=data)
            op = row.operator("bim.enum_property_search", text="", icon="VIEWZOOM")
            op.prop_name = prop_name
    except TypeError:
        pass


class BIM_PT_radiance_exporter(bpy.types.Panel):
    """Creates a Panel in the render properties window"""

    bl_label = "Radiance Exporter"
    bl_idname = "BIM_PT_radiance_exporter"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_tab_lighting"

    def draw(self, context):
        assert self.layout
        layout = self.layout
        props = tool.Blender.get_radiance_exporter_props()

        if tool.Ifc.get():
            row = self.layout.row()
            row.prop(props, "should_load_from_memory")

        if not tool.Ifc.get() or not props.should_load_from_memory:
            row = self.layout.row(align=True)
            row.prop(props, "ifc_file")

        row = layout.row()
        row.prop(props, "output_dir")

        row = layout.row()
        layout.label(text="Info: Unmapped materials default to white")
        row = layout.row()
        row.template_list("MATERIAL_UL_radiance_materials", "", props, "materials", props, "active_material_index")
        row.operator("radiance.open_spectraldb", text="", icon="WORLD")  # Globe icon
        if len(props.materials) > 0:
            col = layout.column(align=True)
            prop_with_search(col, props, "category")
            if props.category:
                prop_with_search(col, props, "subcategory")

            if props.active_material_index >= 0 and props.active_material_index < len(props.materials):
                active_material = props.materials[props.active_material_index]
                if active_material.category and active_material.subcategory:
                    layout.label(
                        text=f"Mapped: {active_material.name} to {active_material.category} - {active_material.subcategory}"
                    )
                else:
                    layout.label(text=f"Select category and subcategory for: {active_material.name}")

        row = layout.row()
        row.operator("radiance.import_material_mappings", text="Import Mappings", icon="IMPORT")
        row.operator("radiance.export_material_mappings", text="Export Mappings", icon="EXPORT")
        row = layout.row()
        row.operator("bim.refresh_ifc_materials", text="Refresh IFC Materials")

        layout.separator()

        box = layout.box()
        box.label(text="Camera Settings")
        row = box.row()
        row.prop(props, "use_active_camera")
        if not props.use_active_camera:
            row = box.row()
            row.prop(props, "selected_camera")
            row.operator("radiance.select_camera", text="", icon="EYEDROPPER")

        row = box.row(align=True)
        row.label(text="Resolution")
        row.prop(props, "radiance_resolution_x", text="X")
        row.prop(props, "radiance_resolution_y", text="Y")

        layout.separator()

        box = layout.box()
        box.label(text="Render Settings")

        row = box.row()
        row.prop(props, "radiance_quality")

        row = box.row()
        row.prop(props, "radiance_detail")

        row = box.row()
        row.prop(props, "radiance_variability")

        row = box.row()
        row.prop(props, "output_file_name")

        row = box.row()
        row.prop(props, "output_file_format")
        layout.separator()

        row = box.row()
        row.prop(props, "use_hdr")

        if props.use_hdr:
            row = box.row()
            row.prop(props, "choose_hdr_image")

        layout.separator()

        # Sky Generation Settings
        box = layout.box()
        row = box.row()
        row.prop(props, "use_sun")
        if props.use_sun:
            box.label(text="Sky Generation Settings")
            box.prop(props, "sky_condition")
            row = box.row()
            row.prop(props, "ground_reflectance")
            row = box.row()
            row.prop(props, "turbidity")

        layout.separator()

        # IES Light Fixtures
        box = layout.box()
        box.label(text="IES Light Fixtures")
        row = box.row()
        row.template_list("MATERIAL_UL_ies_lights", "", props, "ies_lights", props, "active_ies_light_index")
        col = row.column(align=True)
        col.operator("radiance.add_ies_light", text="", icon="ADD")

        # Properties panel for selected IES light
        if (
            len(props.ies_lights) > 0
            and props.active_ies_light_index >= 0
            and props.active_ies_light_index < len(props.ies_lights)
        ):
            active_light = props.ies_lights[props.active_ies_light_index]

            box = layout.box()
            box.label(text="Selected Light Properties")

            # Rotation Z
            row = box.row()
            row.prop(active_light, "rotation_z")

            # Lamp Type
            row = box.row()
            row.prop(active_light, "lamp_type")

            # Lamp Color
            row = box.row()
            row.prop(active_light, "lamp_color")

            # Brightness Factor
            row = box.row()
            row.prop(active_light, "multiply_factor")

            # Illum Sphere Radius
            row = box.row()
            row.prop(active_light, "radius")

        layout.separator()

        # Step 1: Export geometry for simulation
        box = layout.box()
        box.label(text="Step 1: Export geometry for simulation")
        row = box.row()
        row.operator("export_scene.radiance", text="Export Geometry for Simulation")

        layout.separator()

        # Step 2: Prepare Radiance scene
        box = layout.box()
        box.label(text="Step 2: Prepare Radiance scene")
        row = box.row()
        row.operator("scene.prepare_radiance", text="Prepare Scene")

        layout.separator()

        # Step 3: Run the simulation
        box = layout.box()
        box.label(text="Step 3: Run the simulation")
        row = box.row()
        row.operator("render_scene.radiance", text="Radiance Render")
        row.enabled = not props.is_exporting

        layout.separator()

        # Step 4: Generate false color image
        box = layout.box()
        box.label(text="Step 4: Generate False Color Image")
        row = box.row()
        row.prop(props, "use_false_color")

        if props.use_false_color:
            row = box.row()
            row.prop(props, "false_color_label")

            row = box.row()
            row.label(text="Scale Factor")
            row.prop(props, "false_color_scale", text="")

            row = box.row()
            row.prop(props, "false_color_contour_lines")

            row = box.row()
            row.label(text="Multiplier")
            row.prop(props, "false_color_multiplier", text="")

            row = box.row()
            row.label(text="Output Name")
            row.prop(props, "false_color_output_name", text="")

            row = box.row()
            row.operator("render_scene.false_color_radiance", text="Generate False Color Image")

        layout.separator()

        # Step 5: Convert to foot-candles
        box = layout.box()
        box.label(text="Step 5: Convert HDR to Foot-Candles")
        row = box.row()
        row.prop(props, "convert_hdr_to_fc")

        if props.convert_hdr_to_fc:
            row = box.row()
            row.label(text="Output Name")
            row.prop(props, "hdr_to_fc_output_name", text="")

            row = box.row()
            row.operator("render_scene.convert_hdr_to_fc", text="Convert to Foot-Candles")


class BIM_PT_solar(bpy.types.Panel):
    """Creates a Panel in the render properties window"""

    bl_label = "Solar Access / Shadow"
    bl_idname = "BIM_PT_solar"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_tab_solar_analysis"
    bl_options = {"HIDE_HEADER"}

    def draw(self, context):
        if not SolarData.is_loaded:
            SolarData.load()

        assert self.layout

        # Props are more reliable as they'll come and go regardless of Data update.
        if (sun_props := tool.Blender.get_sun_props()) is None:
            self.layout.label(text="Enable 'Sun Position' Add-on To Continue", icon="ERROR")
            return

        sun_position = SolarData.data["sun_position"]
        if sun_position is None:
            # There are props, so there must be an addon.
            SolarData.data["sun_position"] = SolarData.sun_position()

        if TYPE_CHECKING:
            import sun_position

        props = tool.Blender.get_solar_props()

        if SolarData.data["sites"]:
            row = self.layout.row(align=True)
            row.prop(props, "sites")
            row.operator("bim.import_lat_long", icon="IMPORT", text="")
        else:
            row = self.layout.row(align=True)
            row.label(text="No Sites With Lat/Longs Found", icon="ERROR")

        row = self.layout.row(align=True)
        row.alignment = "RIGHT"
        row.operator("bim.light_pick_coordinates", icon="URL", text="Pick")

        row = self.layout.row(align=True)
        row.prop(props, "coordinates", icon="URL")
        row = self.layout.row(align=True)
        row.prop(props, "latitude")
        row.prop(props, "longitude")

        row = self.layout.row(align=True)
        row.prop(props, "true_north")
        if SolarData.data["true_north"] is not None:
            row.operator("bim.import_true_north", icon="IMPORT", text="")

        row = self.layout.row()
        row.alignment = "RIGHT"
        row.operator("bim.light_set_time_to_now", icon="TIME", text="Now")

        row = self.layout.row()
        row.prop(props, "year")
        row = self.layout.row(align=True)
        row.prop(props, "month", text=calendar.month_name[props.month])
        row.prop(props, "day")

        row = self.layout.row(align=True)
        row.prop(props, "hour")
        row.prop(props, "minute")

        col = self.layout.column(align=True)
        box = col.box()
        row = box.row()
        row.alignment = "CENTER"
        row.label(text=props.timezone)

        row = col.row(align=True)
        box = row.box()

        local_time = sun_position.sun_calc.format_time(sun_props.time, sun_props.use_daylight_savings)
        utc_time = sun_position.sun_calc.format_time(sun_props.time, sun_props.use_daylight_savings, sun_props.UTC_zone)

        row2 = box.row()
        row2.label(text=f"Local Time: {local_time}")
        row2 = box.row()
        row2.label(text=f"UTC Time: {utc_time}")

        box = row.box()

        sunrise = sun_position.sun_calc.format_hms(sun_props.sunrise_time)
        sunset = sun_position.sun_calc.format_hms(sun_props.sunset_time)

        row2 = box.row()
        row2.label(text=f"Sunrise: {sunrise}")
        row2 = box.row()
        row2.label(text=f"Sunset: {sunset}")

        col = self.layout.column(align=True)
        row = col.row(align=True)
        row.prop(props, "display_sun_path", icon="LIGHT_SUN")
        row.prop(props, "sun_path_size")

        if props.display_sun_path:
            row = col.row()
            row.operator("bim.move_sun_path_to_3d_cursor")

        row = self.layout.row(align=True)
        row.prop(props, "shadow_mode", icon="SHADING_RENDERED", expand=True)

        if props.shadow_mode == "SHADING":
            row = self.layout.row()
            row.prop(context.scene.display.shading, "shadow_intensity", text="Shadow Intensity")
        elif props.shadow_mode == "RENDERING":
            row = self.layout.row()
            sun_props = tool.Blender.get_sun_props()
            assert sun_props
            row.prop(sun_props.sun_object.data, "energy", text="Sun Intensity")

        row = self.layout.row(align=True)
        row.operator("bim.view_from_sun", icon="LIGHT_HEMI")
