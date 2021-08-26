
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
from blenderbim.bim.prop import StrProperty, Attribute
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


class BIMGeoreferenceProperties(PropertyGroup):
    is_editing: BoolProperty(name="Is Editing")
    map_conversion: CollectionProperty(name="Map Conversion", type=Attribute)
    projected_crs: CollectionProperty(name="Projected CRS", type=Attribute)
    coordinate_input: StringProperty(name="Coordinate Input", description="Formatted \"x,y,z\" (without quotes)")
    coordinate_output: StringProperty(name="Coordinate Output", description="Formatted \"x,y,z\" (without quotes)")
    has_blender_offset: BoolProperty(name="Has Blender Offset")
    blender_eastings: StringProperty(name="Blender Eastings", default="0")
    blender_northings: StringProperty(name="Blender Northings", default="0")
    blender_orthogonal_height: StringProperty(name="Blender Orthogonal Height", default="0")
    blender_x_axis_abscissa: StringProperty(name="Blender X Axis Abscissa", default="1")
    blender_x_axis_ordinate: StringProperty(name="Blender X Axis Ordinate", default="0")
    has_true_north: BoolProperty(name="Has True North", default=True)
    true_north_abscissa: StringProperty(name="True North Abscissa")
    true_north_ordinate: StringProperty(name="True North Ordinate")
