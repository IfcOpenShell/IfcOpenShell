# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of BlenderBIM Add-on.
#
# BlenderBIM Add-on is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# BlenderBIM Add-on is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with BlenderBIM Add-on.  If not, see <http://www.gnu.org/licenses/>.

import blenderbim.tool as tool
from bpy.types import Panel
from blenderbim.bim.helper import draw_attributes, draw_attribute
from blenderbim.bim.module.georeference.data import GeoreferenceData


class BIM_PT_gis(Panel):
    bl_label = "IFC Georeferencing"
    bl_idname = "BIM_PT_gis"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_geometry"

    def draw(self, context):
        self.layout.use_property_split = True
        self.layout.use_property_decorate = False
        props = context.scene.BIMGeoreferenceProperties

        if not GeoreferenceData.is_loaded:
            GeoreferenceData.load()

        if props.is_editing:
            return self.draw_editable_ui(context)
        self.draw_ui(context)

    def draw_editable_ui(self, context):
        props = context.scene.BIMGeoreferenceProperties
        row = self.layout.row(align=True)
        row.label(text="Projected CRS", icon="WORLD")
        row.operator("bim.edit_georeferencing", icon="CHECKMARK", text="")
        row.operator("bim.disable_editing_georeferencing", icon="CANCEL", text="")

        draw_attributes(props.projected_crs, self.layout)

        row = self.layout.row()
        row.label(text="Map Conversion", icon="GRID")

        for attribute in props.map_conversion:
            if attribute.name == "Scale" and hasattr(context.scene, "sun_pos_properties"):
                row = self.layout.row(align=True)
                row.operator("bim.set_ifc_grid_north", text="Set IFC North")
                row.operator("bim.set_blender_grid_north", text="Set Blender North")
            draw_attribute(attribute, self.layout.row())

        row = self.layout.row()
        row.label(text="True North", icon="LIGHT_SUN")
        row = self.layout.row()
        row.prop(props, "has_true_north")
        row = self.layout.row()
        row.prop(props, "true_north_abscissa")
        row = self.layout.row()
        row.prop(props, "true_north_ordinate")
        if hasattr(context.scene, "sun_pos_properties"):
            row = self.layout.row(align=True)
            row.operator("bim.set_ifc_true_north", text="Set IFC North")
            row.operator("bim.set_blender_true_north", text="Set Blender North")

    def draw_ui(self, context):
        props = context.scene.BIMGeoreferenceProperties

        if not GeoreferenceData.data["projected_crs"]:
            row = self.layout.row(align=True)
            row.label(text="Not Georeferenced")
            if tool.Ifc.get_schema != "IFC2X3":
                row.operator("bim.add_georeferencing", icon="ADD", text="")

        if props.has_blender_offset:
            row = self.layout.row()
            row.label(text="Blender Offset", icon="TRACKING_REFINE_FORWARDS")

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
            row = self.layout.row(align=True)
            row.label(text="Derived Grid North")
            row.label(text=GeoreferenceData.data["blender_derived_angle"])

        if GeoreferenceData.data["projected_crs"]:
            row = self.layout.row(align=True)
            row.label(text="Projected CRS", icon="WORLD")
            row.operator("bim.enable_editing_georeferencing", icon="GREASEPENCIL", text="")
            row.operator("bim.remove_georeferencing", icon="X", text="")

        for key, value in GeoreferenceData.data["projected_crs"].items():
            if not value:
                continue
            row = self.layout.row(align=True)
            row.label(text=key)
            row.label(text=str(value))

        if GeoreferenceData.data["map_conversion"]:
            row = self.layout.row(align=True)
            row.label(text="Map Conversion", icon="GRID")

        for key, value in GeoreferenceData.data["map_conversion"].items():
            if value is None:
                continue
            row = self.layout.row(align=True)
            row.label(text=key)
            row.label(text=str(value))
            if key == "XAxisOrdinate":
                row = self.layout.row(align=True)
                row.label(text="Derived Angle")
                row.label(text=GeoreferenceData.data["map_derived_angle"])

        if GeoreferenceData.data["true_north"]:
            row = self.layout.row()
            row.label(text="True North", icon="LIGHT_SUN")
            row = self.layout.row(align=True)
            row.label(text="Vector")
            row.label(text=str(GeoreferenceData.data["true_north"][0:2])[1:-1])
            row = self.layout.row(align=True)
            row.label(text="Derived Angle")
            row.label(text=GeoreferenceData.data["true_derived_angle"])


class BIM_PT_gis_utilities(Panel):
    bl_idname = "BIM_PT_gis_utilities"
    bl_label = "Georeferencing Utilities"
    bl_options = {"DEFAULT_CLOSED"}
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
