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
import ifcopenshell.api
import bonsai.tool as tool
import bonsai.core.root
from bpy.types import Operator
from bpy.props import FloatProperty, IntProperty
from mathutils import Vector


def add_object(self, context):
    obj = bpy.data.objects.new("Grid", None)
    obj.name = "Grid"

    bonsai.core.root.assign_class(
        tool.Ifc, tool.Collector, tool.Root, obj=obj, ifc_class="IfcGrid", should_add_representation=False
    )
    grid = tool.Ifc.get_entity(obj)

    for i in range(0, self.total_u):
        verts = [
            Vector((-2, i * self.u_spacing, 0)),
            Vector((((self.total_v - 1) * self.v_spacing) + 2, i * self.u_spacing, 0)),
        ]
        edges = [[0, 1]]
        faces = []
        mesh = bpy.data.meshes.new(name="Grid Axis")
        mesh.from_pydata(verts, edges, faces)
        tag = chr(ord("A") + i)
        obj = bpy.data.objects.new(f"IfcGridAxis/{tag}", mesh)

        result = ifcopenshell.api.run(
            "grid.create_grid_axis", tool.Ifc.get(), axis_tag=tag, uvw_axes="UAxes", grid=grid
        )
        tool.Ifc.link(result, obj)
        ifcopenshell.api.run("grid.create_axis_curve", tool.Ifc.get(), axis_curve=obj, grid_axis=result)
        tool.Collector.assign(obj)

    for i in range(0, self.total_v):
        verts = [
            Vector((i * self.v_spacing, -2, 0)),
            Vector((i * self.v_spacing, ((self.total_u - 1) * self.u_spacing) + 2, 0)),
        ]
        edges = [[0, 1]]
        faces = []
        mesh = bpy.data.meshes.new(name="Grid Axis")
        mesh.from_pydata(verts, edges, faces)
        tag = str(i + 1).zfill(2)
        obj = bpy.data.objects.new(f"IfcGridAxis/{tag}", mesh)

        result = ifcopenshell.api.run(
            "grid.create_grid_axis", tool.Ifc.get(), axis_tag=tag, uvw_axes="VAxes", grid=grid
        )
        tool.Ifc.link(result, obj)
        ifcopenshell.api.run("grid.create_axis_curve", tool.Ifc.get(), axis_curve=obj, grid_axis=result)
        tool.Collector.assign(obj)

    tool.Root.reload_grid_decorator()


class BIM_OT_add_object(Operator, tool.Ifc.Operator):
    bl_idname = "mesh.add_grid"
    bl_label = "Grid"
    bl_options = {"REGISTER", "UNDO"}

    u_spacing: FloatProperty(name="U Spacing", default=10)
    total_u: IntProperty(name="Number of U Grids", default=3)
    v_spacing: FloatProperty(name="V Spacing", default=10)
    total_v: IntProperty(name="Number of V Grids", default=3)

    @classmethod
    def poll(cls, context):
        return tool.Ifc.get() and context.mode == "OBJECT"

    def _execute(self, context):
        add_object(self, context)
        return {"FINISHED"}
