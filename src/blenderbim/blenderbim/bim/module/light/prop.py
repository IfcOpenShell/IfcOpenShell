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
from bpy.props import IntProperty, StringProperty, EnumProperty
from bpy.types import PropertyGroup

class RadianceExporterProperties(PropertyGroup):
    radiance_resolution_x: IntProperty(
        name="X",
        description="Horizontal resolution of the output image",
        default=1920,
        min=1
    )
    radiance_resolution_y: IntProperty(
        name="Y",
        description="Vertical resolution of the output image",
        default=1080,
        min=1
    )
    ifc_file_name: StringProperty(
        name="IFC File Name",
        description="Name of the IFC file to use (without .ifc extension)",
        default="AC20-FZK-Haus"
    )
    radiance_quality: EnumProperty(
        name="Quality",
        description="Radiance rendering quality",
        items=[
            ('LOW', "Low", "Low quality"),
            ('MEDIUM', "Medium", "Medium quality"),
            ('HIGH', "High", "High quality")
        ],
        default='MEDIUM'
    )
    radiance_detail: EnumProperty(
        name="Detail",
        description="Radiance rendering detail",
        items=[
            ('LOW', "Low", "Low detail"),
            ('MEDIUM', "Medium", "Medium detail"),
            ('HIGH', "High", "High detail")
        ],
        default='MEDIUM'
    )
    radiance_variability: EnumProperty(
        name="Variability",
        description="Radiance rendering variability",
        items=[
            ('LOW', "Low", "Low variability"),
            ('MEDIUM', "Medium", "Medium variability"),
            ('HIGH', "High", "High variability")
        ],
        default='MEDIUM'
    )