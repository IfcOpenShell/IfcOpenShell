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

import os
import pyradiance as pr
import bpy

from pathlib import Path
from typing import Union, Optional, Sequence
import json
import ifcopenshell
import ifcopenshell.geom
import multiprocessing

class ExportRadiance(bpy.types.Operator):
    """Exports and renders the scene with Radiance using rad"""
    bl_idname = "export_scene.radiance"
    bl_label = "Export and Render"
    bl_description = "Export the scene to Radiance and render it"

    def execute(self, context):
        return {'FINISHED'}


    def getResolution(self, context):
        scene = context.scene
        props = scene.radiance_exporter_properties
        resolution_x = props.radiance_resolution_x
        resolution_y = props.radiance_resolution_y
        return resolution_x, resolution_y

def save_obj2mesh_output(inp: Union[bytes, str, Path], output_file: str, **kwargs):
    output_bytes = pr.obj2mesh(inp, **kwargs)
    with open(output_file, 'wb') as f:
        f.write(output_bytes)