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
import bmesh
import pprint

material_volumes = {}

for obj in bpy.context.selected_objects:
    if not obj.data or not isinstance(obj.data, bpy.types.Mesh):
        continue
    material_polygons = {}
    for polygon in obj.data.polygons:
        material_polygons.setdefault(polygon.material_index, []).append(polygon.vertices)
    verts = [v.co for v in obj.data.vertices]
    for index, polygons in material_polygons.items():
        mesh = bpy.data.meshes.new("Temporary Mesh")
        mesh.from_pydata(verts, [], polygons)
        bm = bmesh.new()
        bm.from_mesh(mesh)
        material_name = obj.data.materials[index].name
        material_volumes.setdefault(material_name, 0)
        material_volumes[material_name] += bm.calc_volume()
        bm.free()
        bpy.data.meshes.remove(mesh)

pprint.pprint(material_volumes)
