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

import bonsai.tool as tool
from bpy.types import Panel
from bonsai.bim.helper import draw_attributes, draw_attribute
from bonsai.bim.module.georeference.data import GeoreferenceData


class BIM_PT_gis(Panel):
    bl_label = "Georeferencing"
    bl_idname = "BIM_PT_gis"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_tab_geometry"

    def draw(self, context):
        self.layout.use_property_split = True
        self.layout.use_property_decorate = False
        props = context.scene.BIMGeoreferenceProperties

        if not GeoreferenceData.is_loaded:
            GeoreferenceData.load()

        if props.is_editing:
            self.draw_editable_ui(context)
        else:
            self.draw_ui(context)

    def draw_editable_ui(self, context):
        props = context.scene.BIMGeoreferenceProperties
        row = self.layout.row(align=True)
        row.label(text="Projected CRS", icon="WORLD")
        row.operator("bim.edit_georeferencing", icon="CHECKMARK", text="")
        row.operator("bim.disable_editing_georeferencing", icon="CANCEL", text="")

        draw_attributes(props.projected_crs, self.layout)

        row = self.layout.row()
        row.label(text="Coordinate Operation", icon="GRID")

        for attribute in props.coordinate_operation:
            if attribute.name == "XAxisAbscissa":
                row = self.layout.row(align=True)
                row.prop(props, "grid_north_angle", text="Angle")
                row.prop(
                    props, "x_axis_is_null", icon="RADIOBUT_OFF" if props.x_axis_is_null else "RADIOBUT_ON", text=""
                )
                row = self.layout.row(align=True)
                row.prop(props, "x_axis_abscissa", text="XAxis Abscissa")
                row.prop(
                    props, "x_axis_is_null", icon="RADIOBUT_OFF" if props.x_axis_is_null else "RADIOBUT_ON", text=""
                )
            elif attribute.name == "XAxisOrdinate":
                row = self.layout.row(align=True)
                row.prop(props, "x_axis_ordinate", text="XAxis Ordinate")
                row.prop(
                    props, "x_axis_is_null", icon="RADIOBUT_OFF" if props.x_axis_is_null else "RADIOBUT_ON", text=""
                )
            else:
                draw_attribute(attribute, self.layout.row())

    def draw_ui(self, context):
        props = context.scene.BIMGeoreferenceProperties

        if tool.Ifc.get_schema() == "IFC2X3":
            row = self.layout.row()
            row.label(text="IFC2X3 Fallback In Use", icon="INFO")

        if not GeoreferenceData.data["projected_crs"]:
            row = self.layout.row(align=True)
            row.label(text="Not Georeferenced", icon="ERROR")
            row = self.layout.row(align=True)
            row.prop(props, "should_visualise", icon="HIDE_OFF")
            row.prop(props, "visualization_scale", text="Size", slider=True)
            if tool.Ifc.get_schema() != "IFC2X3":
                row.prop(props, "coordinate_operation_class", text="")
                row.operator("bim.add_georeferencing", icon="ADD", text="")

        if GeoreferenceData.data["projected_crs"]:
            row = self.layout.row(align=True)
            row.label(text="Projected CRS", icon="WORLD")
            row = self.layout.row(align=True)
            row.prop(props, "should_visualise", icon="HIDE_OFF")
            row.prop(props, "visualization_scale", text="Size", slider=True)
            if tool.Ifc.get_schema() != "IFC2X3":
                row.operator("bim.enable_editing_georeferencing", icon="GREASEPENCIL", text="")
                row.operator("bim.remove_georeferencing", icon="X", text="")

        for key, value in GeoreferenceData.data["projected_crs"].items():
            if not value:
                continue
            row = self.layout.row(align=True)
            row.label(text=key)
            row.label(text=str(value))

        if GeoreferenceData.data["coordinate_operation"]:
            row = self.layout.row(align=True)
            row.label(text="Coordinate Operation", icon="GRID")

        for key, value in GeoreferenceData.data["coordinate_operation"].items():
            if value is None:
                continue
            if key == "type":
                key = "Type"
            row = self.layout.row(align=True)
            if key in ("Eastings", "Northings", "OrthogonalHeight"):
                row.label(text=f"{key} ({GeoreferenceData.data['map_unit_symbol']})")
            else:
                row.label(text=key)
            row.label(text=str(value))
            if key == "XAxisOrdinate":
                row = self.layout.row(align=True)
                row.label(text="*Angle to Grid North")
                row.label(text=GeoreferenceData.data["map_derived_angle"])


class BIM_PT_gis_true_north(Panel):
    bl_idname = "BIM_PT_gis_true_north"
    bl_label = "True North"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_gis"

    def draw(self, context):
        if not GeoreferenceData.is_loaded:
            GeoreferenceData.load()

        self.props = context.scene.BIMGeoreferenceProperties

        if self.props.is_editing_true_north:
            self.draw_editable_ui(context)
        else:
            self.draw_ui()

    def draw_editable_ui(self, context):
        row = self.layout.row()
        row.prop(self.props, "true_north_angle", text="Angle")
        row = self.layout.row()
        row.prop(self.props, "true_north_abscissa", text="Abscissa")
        row = self.layout.row()
        row.prop(self.props, "true_north_ordinate", text="Ordinate")

        row = self.layout.row(align=True)
        row.operator("bim.edit_true_north", icon="CHECKMARK")
        row.operator("bim.disable_editing_true_north", icon="CANCEL", text="")

    def draw_ui(self):
        if GeoreferenceData.data["true_north"]:
            row = self.layout.row(align=True)
            row.label(text="Abscissa")
            row.label(text=str(GeoreferenceData.data["true_north"][0]))
            row = self.layout.row(align=True)
            row.label(text="Ordinate")
            row.label(text=str(GeoreferenceData.data["true_north"][1]))
            row.operator("bim.enable_editing_true_north", icon="GREASEPENCIL", text="")
            row.operator("bim.remove_true_north", icon="X", text="")
            row = self.layout.row(align=True)
            row.label(text="*Angle to True North")
            row.label(text=GeoreferenceData.data["true_derived_angle"])
        else:
            row = self.layout.row(align=True)
            row.label(text="No True North Found", icon="LIGHT_SUN")
            row.operator("bim.enable_editing_true_north", icon="GREASEPENCIL", text="")


class BIM_PT_gis_blender(Panel):
    bl_idname = "BIM_PT_gis_blender"
    bl_label = "Blender Coordinates"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_gis"

    def draw(self, context):
        if not GeoreferenceData.is_loaded:
            GeoreferenceData.load()

        props = context.scene.BIMGeoreferenceProperties

        if props.has_blender_offset:
            row = self.layout.row()
            row.label(text="Temporary Offset Is Active", icon="TRACKING_REFINE_FORWARDS")

        row = self.layout.row(align=True)
        row.label(text=f"Eastings ({GeoreferenceData.data['local_unit_symbol']})")
        row.label(text=props.model_origin.split(",")[0])
        row = self.layout.row(align=True)
        row.label(text=f"Northings ({GeoreferenceData.data['local_unit_symbol']})")
        row.label(text=props.model_origin.split(",")[1])
        row = self.layout.row(align=True)
        row.label(text=f"OrthogonalHeight ({GeoreferenceData.data['local_unit_symbol']})")
        row.label(text=props.model_origin.split(",")[2])
        row = self.layout.row(align=True)
        row.label(text="Angle to Grid North")
        row.label(text=props.model_project_north)


class BIM_PT_gis_wcs(Panel):
    bl_idname = "BIM_PT_gis_wcs"
    bl_label = "World Coordinate System"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_gis"

    def draw(self, context):
        if not GeoreferenceData.is_loaded:
            GeoreferenceData.load()

        props = context.scene.BIMGeoreferenceProperties

        if props.is_editing_wcs:
            self.draw_editable_ui(context)
        else:
            self.draw_ui()

    def draw_ui(self):
        if GeoreferenceData.data["world_coordinate_system"]["has_transformation"]:
            row = self.layout.row(align=True)
            row.label(text="Unrecommended Transformation Found", icon="ERROR")
            row.operator("bim.enable_editing_wcs", icon="GREASEPENCIL", text="")
            row = self.layout.row(align=True)
            row.label(text=f"X ({GeoreferenceData.data['local_unit_symbol']})")
            row.label(text=str(GeoreferenceData.data["world_coordinate_system"]["x"]))
            row = self.layout.row(align=True)
            row.label(text=f"Y ({GeoreferenceData.data['local_unit_symbol']})")
            row.label(text=str(GeoreferenceData.data["world_coordinate_system"]["y"]))
            row = self.layout.row(align=True)
            row.label(text=f"Z ({GeoreferenceData.data['local_unit_symbol']})")
            row.label(text=str(GeoreferenceData.data["world_coordinate_system"]["z"]))
            row = self.layout.row(align=True)
            row.label(text="Rotation")
            row.label(text=str(GeoreferenceData.data["world_coordinate_system"]["rotation"]))
        else:
            row = self.layout.row()
            row.label(text="No WCS Transformation", icon="CHECKMARK")
            row.operator("bim.enable_editing_wcs", icon="GREASEPENCIL", text="")

    def draw_editable_ui(self, context):
        props = context.scene.BIMGeoreferenceProperties

        row = self.layout.row(align=True)
        row.label(text="World Coordinate System", icon="EMPTY_ARROWS")
        row.operator("bim.edit_wcs", icon="CHECKMARK", text="")
        row.operator("bim.disable_editing_wcs", icon="CANCEL", text="")

        row = self.layout.row()
        row.prop(props, "wcs_x")
        row = self.layout.row()
        row.prop(props, "wcs_y")
        row = self.layout.row()
        row.prop(props, "wcs_z")
        row = self.layout.row()
        row.prop(props, "wcs_rotation")


class BIM_PT_gis_calculator(Panel):
    bl_idname = "BIM_PT_gis_calculator"
    bl_label = "Georeferencing Calculator"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_gis"

    def draw(self, context):
        if not GeoreferenceData.is_loaded:
            GeoreferenceData.load()

        props = context.scene.BIMGeoreferenceProperties

        if props.has_blender_offset:
            row = self.layout.row(align=True)
            row.prop(props, "blender_coordinates", text=f"Blender ({GeoreferenceData.data['local_unit_symbol']})")
            row.operator("bim.get_cursor_location", text="", icon="TRACKER")

        row = self.layout.row(align=True)
        row.prop(props, "local_coordinates", text=f"Local ({GeoreferenceData.data['local_unit_symbol']})")
        if not props.has_blender_offset:
            row.operator("bim.get_cursor_location", text="", icon="TRACKER")

        row = self.layout.row()
        row.prop(props, "map_coordinates", text=f"Map ({GeoreferenceData.data['map_unit_symbol']})")
