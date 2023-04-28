# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2022 Dion Moult <dion@thinkmoult.com>
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
import bpy
import ifcopenshell.express
import blenderbim.core.tool
from blenderbim.bim.ifc import IfcStore


class Debug(blenderbim.core.tool.Debug):
    @classmethod
    def add_schema_identifier(cls, schema):
        IfcStore.schema_identifiers.append(schema.schema_name)

    @classmethod
    def load_express(cls, filename):
        schema = ifcopenshell.express.parse(filename)
        ifcopenshell.register_schema(schema)
        return schema

    @classmethod
    def purge_hdf5_cache(cls):
        cache_dir = os.path.join(bpy.context.scene.BIMProperties.data_dir, "cache")
        filelist = [f for f in os.listdir(cache_dir) if f.endswith(".h5")]
        for f in filelist:
            os.remove(os.path.join(cache_dir, f))

    @classmethod
    def debug_geometry(cls, verts=[], edges=[], name="Debug"):
        mesh = bpy.data.meshes.new("Debug")
        mesh.from_pydata(verts, edges, [])
        obj = bpy.data.objects.new(name, mesh)
        bpy.context.scene.collection.objects.link(obj)
        return obj
