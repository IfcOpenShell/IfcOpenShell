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
from typing import TYPE_CHECKING

import bpy

import bonsai.tool as tool
from bonsai.bim.helper import prop_with_search
from bonsai.bim.module.light.data import SolarData


# ---------------------------------------------------------------------------
# Root panel (replaces the old "Radiance Exporter" nested panel)
# ---------------------------------------------------------------------------

class BIM_PT_radiance_exporter(bpy.types.Panel):
    bl_label = "Radiance Exporter"
    bl_idname = "BIM_PT_radiance_exporter"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_tab_lighting"
    bl_options = {"HIDE_HEADER"}

    def draw(self, context):
        pass


# ---------------------------------------------------------------------------
# 1. Scene Setup
# ---------------------------------------------------------------------------

class BIM_PT_radiance_scene_setup(bpy.types.Panel):
    bl_label = "Scene Setup"
    bl_idname = "BIM_PT_radiance_scene_setup"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_radiance_exporter"

    def draw(self, context):
        layout = self.layout
        props = tool.Blender.get_radiance_exporter_props()

        row = layout.row()
        row.prop(props, "output_dir")

        layout.separator()

        row = layout.row()
        row.prop(props, "use_active_camera")
        if not props.use_active_camera:
            row = layout.row()
            row.prop(props, "selected_camera")

        row = layout.row(align=True)
        row.label(text="Resolution")
        row.prop(props, "radiance_resolution_x", text="X")
        row.prop(props, "radiance_resolution_y", text="Y")


# ---------------------------------------------------------------------------
# 2. Materials
# ---------------------------------------------------------------------------

class BIM_PT_radiance_materials(bpy.types.Panel):
    bl_label = "Materials"
    bl_idname = "BIM_PT_radiance_materials"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_radiance_exporter"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        props = tool.Blender.get_radiance_exporter_props()

        layout.label(text="Unmapped materials default to white", icon="INFO")

        row = layout.row()
        row.template_list("MATERIAL_UL_radiance_materials", "", props, "materials", props, "active_material_index")
        row.operator("radiance.open_spectraldb", text="", icon="WORLD")

        if len(props.materials) > 0:
            col = layout.column(align=True)
            prop_with_search(col, props, "category")
            if props.category:
                prop_with_search(col, props, "subcategory")

            if 0 <= props.active_material_index < len(props.materials):
                active_material = props.materials[props.active_material_index]
                if active_material.category and active_material.subcategory:
                    layout.label(
                        text=f"Mapped: {active_material.name} -> {active_material.category} - {active_material.subcategory}"
                    )
                else:
                    layout.label(text=f"Select category and subcategory for: {active_material.name}")

        row = layout.row()
        row.operator("radiance.import_material_mappings", text="Import Mappings", icon="IMPORT")
        row.operator("radiance.export_material_mappings", text="Export Mappings", icon="EXPORT")
        row = layout.row()
        row.operator("bim.refresh_ifc_materials", text="Refresh IFC Materials")


# ---------------------------------------------------------------------------
# 3. Lighting (Environment + IES)
# ---------------------------------------------------------------------------

class BIM_PT_radiance_lighting(bpy.types.Panel):
    bl_label = "Lighting"
    bl_idname = "BIM_PT_radiance_lighting"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_radiance_exporter"

    def draw(self, context):
        layout = self.layout
        props = tool.Blender.get_radiance_exporter_props()

        # Environment
        box = layout.box()
        box.label(text="Environment", icon="WORLD")
        row = box.row()
        row.prop(props, "use_hdr")
        row = box.row()
        row.prop(props, "use_sun")
        if props.use_sun:
            box.prop(props, "sky_condition")
            row = box.row()
            row.prop(props, "ground_reflectance")
            row = box.row()
            row.prop(props, "turbidity")

        layout.separator()

        # IES Light Fixtures
        box = layout.box()
        box.label(text="IES Light Fixtures", icon="LIGHT_POINT")
        row = box.row()
        row.template_list("MATERIAL_UL_ies_lights", "", props, "ies_lights", props, "active_ies_light_index")
        col = row.column(align=True)
        col.operator("radiance.add_ies_light", text="", icon="ADD")

        if (
            len(props.ies_lights) > 0
            and 0 <= props.active_ies_light_index < len(props.ies_lights)
        ):
            active_light = props.ies_lights[props.active_ies_light_index]

            col = box.column(align=True)

            row = col.row()
            row.prop(active_light, "use_collection", text="Target Collection", icon="OUTLINER_COLLECTION")

            row = col.row()
            if active_light.use_collection:
                row.prop(active_light, "target_collection", text="Collection")
                if active_light.target_collection:
                    empties = [o for o in active_light.target_collection.all_objects if o.type == "EMPTY"]
                    row = col.row()
                    row.label(text=f"{len(empties)} empty object(s) in collection", icon="INFO")
            else:
                row.prop(active_light, "target_object", text="Object")

            row = col.row()
            row.label(text="Rotation Z")
            row.prop(active_light, "rotation_z", text="")

            row = col.row()
            row.prop(active_light, "lamp_color")

            split = col.split(factor=0.5)
            split.prop(active_light, "multiply_factor")
            split.prop(active_light, "radius")


# ---------------------------------------------------------------------------
# 4. Render Settings
# ---------------------------------------------------------------------------

class BIM_PT_radiance_render_settings(bpy.types.Panel):
    bl_label = "Render Settings"
    bl_idname = "BIM_PT_radiance_render_settings"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_radiance_exporter"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        props = tool.Blender.get_radiance_exporter_props()

        row = layout.row()
        row.prop(props, "radiance_quality")

        row = layout.row()
        row.prop(props, "radiance_detail")

        row = layout.row()
        row.prop(props, "radiance_variability")

        row = layout.row()
        row.prop(props, "ambient_bounces")

        layout.separator()

        row = layout.row()
        row.prop(props, "output_file_name")

        row = layout.row()
        row.prop(props, "output_file_format")


# ---------------------------------------------------------------------------
# 5. Pipeline (Steps 1-4 + Cleanup)
# ---------------------------------------------------------------------------

class BIM_PT_radiance_pipeline(bpy.types.Panel):
    bl_label = "Pipeline"
    bl_idname = "BIM_PT_radiance_pipeline"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_radiance_exporter"

    def draw(self, context):
        layout = self.layout
        props = tool.Blender.get_radiance_exporter_props()

        # Step 1
        box = layout.box()
        row = box.row()
        row.label(text="Step 1: Export Geometry")
        row = box.row()
        if props.is_exporting:
            row.label(text="Exporting...", icon="SORTTIME")
        else:
            row.operator("export_scene.radiance", text="Export Geometry")

        # Step 2
        box = layout.box()
        row = box.row()
        row.label(text="Step 2: Prepare Scene")
        row = box.row()
        if props.is_preparing:
            row.label(text="Preparing scene...", icon="SORTTIME")
        else:
            row.operator("scene.prepare_radiance", text="Prepare Scene")

        # Step 3
        box = layout.box()
        row = box.row()
        row.label(text="Step 3: Render")
        row = box.row()
        if props.is_rendering:
            row.label(text="Rendering...", icon="RENDER_STILL")
        else:
            row.operator("render_scene.radiance", text="Radiance Render")

        # Step 4: False Color
        box = layout.box()
        row = box.row()
        row.label(text="Step 4: False Color Analysis")

        row = box.row()
        row.prop(props, "radiance_bin_dir")

        row = box.row()
        row.prop(props, "false_color_label")

        split = box.split(factor=0.5)
        split.prop(props, "false_color_scale")
        split.prop(props, "false_color_steps")

        row = box.row()
        row.label(text="Output Name")
        row.prop(props, "false_color_output_name", text="")

        row = box.row()
        row.prop(props, "false_color_contour_lines")

        if props.false_color_contour_lines:
            row = box.row()
            row.prop(props, "false_color_contour_mode")

        row = box.row()
        row.operator("render_scene.false_color_radiance", text="Generate False Color Image")

        layout.separator()

        # Cleanup
        row = layout.row()
        row.operator("radiance.cleanup_files", text="Cleanup Generated Files", icon="TRASH")


# ---------------------------------------------------------------------------
# Solar Panel (unchanged)
# ---------------------------------------------------------------------------

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
            if sun_props.sun_object is not None and sun_props.sun_object.data is not None:
                row.prop(sun_props.sun_object.data, "energy", text="Sun Intensity")
            else:
                row.label(text="Sun object not found. Toggle shadow mode to recreate.", icon="ERROR")

        row = self.layout.row(align=True)
        row.operator("bim.view_from_sun", icon="LIGHT_HEMI")
