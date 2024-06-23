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

import bpy
from blenderbim.bim.prop import Attribute
from bpy.types import PropertyGroup
from bpy.props import (
    PointerProperty,
    StringProperty,
    EnumProperty,
    BoolProperty,
    IntProperty,
    FloatProperty,
    FloatVectorProperty,
    CollectionProperty,
)
from blenderbim.bim.module.georeference.data import GeoreferenceData


def get_coordinate_operation_class(self, context):
    if not GeoreferenceData.is_loaded:
        GeoreferenceData.load()
    return GeoreferenceData.data["coordinate_operation_class"]


class BIMGeoreferenceProperties(PropertyGroup):
    coordinate_operation_class: bpy.props.EnumProperty(
        items=get_coordinate_operation_class, name="Coordinate Operation Class"
    )
    is_editing: BoolProperty(name="Is Editing")
    is_editing_wcs: BoolProperty(name="Is Editing WCS")
    coordinate_operation: CollectionProperty(name="Coordinate Operation", type=Attribute)
    projected_crs: CollectionProperty(name="Projected CRS", type=Attribute)
    local_coordinates: StringProperty(
        name="Local Coordinates", description='Formatted "x,y,z" (without quotes)', default="0,0,0"
    )
    map_coordinates: StringProperty(
        name="Map Coordinates", description='Formatted "x,y,z" (without quotes)', default="0,0,0"
    )
    angle_degree_input_x: FloatProperty(name="Angle Degree Input", description="Angle (in degrees) rel to Easting")
    angle_degree_input_y: FloatProperty(name="Angle Degree Input", description="Angle (in degrees) rel to +Y")
    x_axis_abscissa_output: StringProperty(
        name="X Axis Abscissa Ordinate Output",
        description="X axis abscissa and ordinate",
    )
    x_axis_ordinate_output: StringProperty(
        name="X Axis Abscissa Ordinate Output",
        description="X axis abscissa and ordinate",
    )
    y_axis_abscissa_output: StringProperty(
        name="Y Axis Abscissa Ordinate Output",
        description="Y axis abscissa and ordinate",
    )
    y_axis_ordinate_output: StringProperty(
        name="Y Axis Abscissa Ordinate Output",
        description="Y axis abscissa and ordinate",
    )
    host_model_origin: StringProperty(name="Host Model Origin")
    model_origin: StringProperty(name="Model Origin")
    has_blender_offset: BoolProperty(name="Has Blender Offset")
    blender_eastings: StringProperty(name="Blender Eastings", default="0")
    blender_northings: StringProperty(name="Blender Northings", default="0")
    blender_orthogonal_height: StringProperty(name="Blender Orthogonal Height", default="0")
    blender_x_axis_abscissa: StringProperty(name="Blender X Axis Abscissa", default="1")
    blender_x_axis_ordinate: StringProperty(name="Blender X Axis Ordinate", default="0")
    blender_offset_x: StringProperty(name="Blender Offset X", default="0")
    blender_offset_y: StringProperty(name="Blender Offset Y", default="0")
    blender_offset_z: StringProperty(name="Blender Offset Z", default="0")
    has_true_north: BoolProperty(name="Has True North", default=True)
    true_north_abscissa: StringProperty(name="True North Abscissa")
    true_north_ordinate: StringProperty(name="True North Ordinate")
    wcs_x: StringProperty(name="WCS X", default="0")
    wcs_y: StringProperty(name="WCS Y", default="0")
    wcs_z: StringProperty(name="WCS Z", default="0")
    wcs_rotation: StringProperty(name="WCS Rotation", default="0")
