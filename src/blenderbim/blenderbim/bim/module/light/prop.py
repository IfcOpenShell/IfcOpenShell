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
from bpy.props import IntProperty, StringProperty, EnumProperty, BoolProperty
from bpy.types import PropertyGroup

class RadianceExporterProperties(PropertyGroup):

    def update_json_file(self, context):
        if self.json_file:
            self.json_file = bpy.path.abspath(self.json_file)

    def update_output_dir(self, context):
        if self.output_dir:
            self.output_dir = bpy.path.abspath(self.output_dir)

    def update_ifc_file(self, context):
        if self.ifc_file:
            self.ifc_file = bpy.path.abspath(self.ifc_file)


    should_load_from_memory: BoolProperty(
        name="Load from Memory",
        default=False, 
        name="Load from Memory"
    )

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
    output_dir: StringProperty(
        name="Output Directory",
        description="Directory to output Radiance files",
        default="",
        subtype="DIR_PATH",
        update=lambda self, context: self.update_output_dir(context)
    )
    ifc_file: StringProperty(
        name="IFC File",
        description="Path to the IFC file",
        default="",
        subtype="FILE_PATH",
        update=lambda self, context: self.update_ifc_file(context)
    )
    json_file: StringProperty(
        name="JSON File",
        description="Path to the JSON file",
        default="",
        subtype="FILE_PATH",
        update=lambda self, context: self.update_json_file(context)
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