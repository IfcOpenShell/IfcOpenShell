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

import bpy
import bonsai.tool as tool
from bonsai.bim.module.light.data import SolarData


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
        layout = self.layout
        scene = context.scene

        props = scene.radiance_exporter_properties

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
            col.prop(props, "category")
            if props.category:
                col.prop(props, "subcategory")

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

        row = layout.row()
        layout.label(text="Step 1: Export geometry for simulation")
        row = layout.row()
        row.operator("export_scene.radiance", text="Export Geometry for Simulation")

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

        row = layout.row()
        row.prop(props, "radiance_quality")

        row = layout.row()
        row.prop(props, "radiance_detail")

        row = layout.row()
        row.prop(props, "radiance_variability")

        layout.separator()

        row = layout.row()
        row.prop(props, "output_file_name")

        row = layout.row()
        row.prop(props, "output_file_format")
        layout.separator()

        row = layout.row()
        row.prop(props, "use_hdr")

        if props.use_hdr:
            row = layout.row()
            row.prop(props, "choose_hdr_image")

        row = layout.row()
        layout.label(text="Step 2: Run the simulation")
        row = layout.row()
        row.operator("render_scene.radiance", text="Radiance Render")
        row.enabled = not props.is_exporting


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

        if (sun_position := SolarData.data["sun_position"]) is None:
            self.layout.label(text="Enable 'Sun Position' Add-on To Continue", icon="ERROR")
            return

        props = context.scene.BIMSolarProperties

        if SolarData.data["sites"]:
            row = self.layout.row(align=True)
            row.prop(props, "sites")
            row.operator("bim.import_lat_long", icon="IMPORT", text="")
        else:
            row = self.layout.row(align=True)
            row.label(text="No Sites With Lat/Longs Found", icon="ERROR")

        sun_props = context.scene.sun_pos_properties

        row = self.layout.row()
        row.prop(sun_props, "coordinates", icon="URL")
        row = self.layout.row(align=True)
        row.prop(props, "latitude")
        row.prop(props, "longitude")

        row = self.layout.row(align=True)
        row.prop(props, "true_north")
        if SolarData.data["true_north"] is not None:
            row.operator("bim.import_true_north", icon="IMPORT", text="")

        row = self.layout.row(align=True)
        row.prop(
            props,
            "month",
            text={
                1: "January",
                2: "February",
                3: "March",
                4: "April",
                5: "May",
                6: "June",
                7: "July",
                8: "August",
                9: "September",
                10: "October",
                11: "November",
                12: "December",
            }[props.month],
        )
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
        row.prop(props, "display_shadows", icon="SHADING_RENDERED")
        row.prop(context.scene.display.shading, "shadow_intensity", text="Shadow Intensity")

        row = self.layout.row(align=True)
        row.operator("bim.view_from_sun", icon="LIGHT_HEMI")
