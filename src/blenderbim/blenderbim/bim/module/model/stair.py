# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021, 2022 Dion Moult <dion@thinkmoult.com>, @Andrej730
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
from bpy.types import Operator
from bpy.props import FloatProperty, IntProperty, BoolProperty
from bpy_extras.object_utils import AddObjectHelper, object_data_add
from mathutils import Vector

import bmesh
from bmesh.types import BMVert

from mathutils import Vector
from pprint import pprint


def add_dumb_stair_object(self, context):
    if self.number_of_treads <= 0:
        self.number_of_treads = 1
    verts = [
        Vector((0, 0, 0)),
        Vector((0, self.tread_length, 0)),
        Vector((self.width, self.tread_length, 0)),
        Vector((self.width, 0, 0)),
    ]
    edges = []
    faces = [[0, 1, 2, 3]]

    mesh = bpy.data.meshes.new(name="Dumb Stair")
    mesh.from_pydata(verts, edges, faces)
    obj = object_data_add(context, mesh, operator=self)
    modifier = obj.modifiers.new("Stair Width", "SOLIDIFY")
    modifier.use_even_offset = True
    modifier.offset = 1
    modifier.thickness = self.tread_depth
    modifier = obj.modifiers.new("Stair Treads", "ARRAY")
    modifier.relative_offset_displace[0] = 0
    modifier.relative_offset_displace[1] = 1
    modifier.use_constant_offset = True
    modifier.constant_offset_displace[0] = 0
    modifier.constant_offset_displace[1] = 0
    modifier.constant_offset_displace[2] = self.height / self.number_of_treads
    modifier.count = self.number_of_treads
    self.riser_height = self.height / self.number_of_treads
    self.length = self.number_of_treads * self.tread_length
    obj.name = "Stair"


class BIM_OT_add_object(Operator, AddObjectHelper):
    bl_idname = "mesh.add_stair"
    bl_label = "Dumb Stair"
    bl_options = {"REGISTER", "UNDO"}

    width: FloatProperty(name="Width", default=1.1)
    height: FloatProperty(name="Height", default=1)
    tread_depth: FloatProperty(name="Tread Depth", default=0.2)
    number_of_treads: IntProperty(name="Number of Treads (Goings)", default=6)
    tread_length: FloatProperty(name="Tread Length (Going)", default=0.25)
    riser_height: FloatProperty(name="*Calculated* Riser Height")
    length: FloatProperty(name="*Calculated* Length")

    def execute(self, context):
        add_dumb_stair_object(self, context)
        return {"FINISHED"}


def create_stair(
    operator,
    context,
    width=1.2,
    height=1.0,
    number_of_treads=6,
    tread_depth=0.25,
    tread_run=0.3,
    # tread_rise = None, # 0.167
    base_slab_depth=0.25,
    top_slab_depth=0.25,
    has_top_nib=False,
    stair_type="CONCRETE",
    extrude=True,
):

    vertices = []
    edges = []

    # 2d profile generation
    tread_rise = height / number_of_treads
    length = tread_run * number_of_treads

    for i in range(number_of_treads):
        vertices.extend([
            Vector((tread_run*i, 0, tread_rise*i)),
            Vector((tread_run*i, 0, tread_rise*(i+1)))
        ])
        cur_vertex = i * 2
        if i != 0:
            edges.append((cur_vertex - 1, cur_vertex))
        edges.append((cur_vertex, cur_vertex + 1))

    vertices.append(Vector((tread_run * number_of_treads, 0, tread_rise * number_of_treads)))
    edges.append((number_of_treads * 2, number_of_treads * 2 - 1))

    td_vector = Vector((vertices[2][2], 0, -vertices[2][0])).normalized() * tread_depth

    k = tread_rise / tread_run
    s0 = vertices[0] + td_vector
    b = s0.z - k * s0.x  # comes from y = kx + b
    # you could use td_vector as depth_vector
    # but then stair won't be perpendicular to the X+
    # b is kind of vertical tread_depth (along Z+)
    depth_vector = Vector((0, 0, b))

    # top nib
    if has_top_nib:
        vertices.append( vertices[number_of_treads * 2] + Vector((0, 0, -top_slab_depth)) )
        vertices.append( vertices[number_of_treads * 2] + Vector(((-top_slab_depth - b) / k, 0, -top_slab_depth)) )
        last_vertex_i = len(vertices) - 1
        edges.append( (number_of_treads * 2, last_vertex_i - 1) )
        edges.append( (last_vertex_i - 1, last_vertex_i) )
    else:
        vertices.append(vertices[number_of_treads * 2] + depth_vector)
        last_vertex_i = len(vertices) - 1
        edges.append((number_of_treads * 2, last_vertex_i))

    top_nib_end = len(vertices) - 1

    # bottom nib
    if abs(b) <= base_slab_depth:
        vertices.append(vertices[0] + depth_vector)
        edges.append((0, len(vertices) - 1))
        bottom_nib_end = len(vertices) - 1
    else:
        vertices.append(vertices[0] + Vector(((-base_slab_depth - b) / k, 0, -base_slab_depth)))
        vertices.append(vertices[0] + Vector((0, 0, -base_slab_depth)))
        last_vertex_i = len(vertices) - 1
        edges.append( (0, last_vertex_i) )
        edges.append( (last_vertex_i - 1, last_vertex_i) )
        bottom_nib_end = len(vertices) - 2

    edges.append( (bottom_nib_end, top_nib_end) )
    faces = [list(range(len(vertices)))]
    # profile generation finished

    obj = context.object
    bm = bmesh.new()
    bm.verts.index_update()
    bm.edges.index_update()

    new_verts = [bm.verts.new(v) for v in vertices]
    new_edges = [bm.edges.new( (new_verts[e[0]], new_verts[e[1]]) ) for e in edges]
    bm.verts.index_update()
    bm.edges.index_update()

    bmesh.ops.contextual_create(bm, geom=new_edges)

    if extrude:
        bm.faces.ensure_lookup_table()
        faces = [bm.faces[0]]
        extruded = bmesh.ops.extrude_face_region(bm, geom=faces)
        extrusion_vector = Vector((0, 1, 0)) * width
        translate_verts = [v for v in extruded["geom"] if isinstance(v, BMVert)]
        bmesh.ops.translate(bm, vec=extrusion_vector, verts=translate_verts)

    # set origin
    prev_cursor_location = bpy.context.scene.cursor.location.copy()
    bpy.context.scene.cursor.location = vertices[0]
    bpy.ops.object.origin_set(type="ORIGIN_CURSOR", center="MEDIAN")
    bpy.context.scene.cursor.location = prev_cursor_location

    if context.object.mode == "EDIT":
        bmesh.update_edit_mesh(obj.data)
    else:
        bm.to_mesh(obj.data)
        bm.free()

    return (obj, tread_rise, length)


def add_object_stair(self, context):
    if context.object is None:
        self.report({"ERROR"}, "Select object that will be transformed to a stair.")
        return

    mesh, tread_rise, length = create_stair(
        operator=self,
        context=context,
        stair_type="CONCRETE",
        width=self.width,
        height=self.height,
        number_of_treads=self.number_of_treads,
        tread_depth=self.tread_depth,
        tread_run=self.tread_run,
        base_slab_depth=self.base_slab_depth,
        top_slab_depth=self.top_slab_depth,
        has_top_nib=self.has_top_nib,
    )
    self.tread_rise = tread_rise
    self.length = length


class BIM_OT_add_clever_stair(Operator):
    bl_idname = "mesh.add_clever_stair"
    bl_label = "Clever Stair"
    bl_options = {"REGISTER", "UNDO"}

    width: FloatProperty(name="Width", default=1.2, soft_min=0.01)
    height: FloatProperty(name="Height", default=1.0, soft_min=0.01)
    number_of_treads: IntProperty(name="Number of Treads (Goings)", default=6, soft_min=1)
    tread_depth: FloatProperty(name="Tread Depth", default=0.25, soft_min=0.01)
    tread_run: FloatProperty(name="Tread Run", default=0.3, soft_min=0.01)
    base_slab_depth: FloatProperty(name="Base slab depth", default=0.25, soft_min=0)
    top_slab_depth: FloatProperty(name="Top slab depth", default=0.25, soft_min=0)
    has_top_nib: BoolProperty(name="Has top nib", default=True)

    tread_rise: FloatProperty(name="*Calculated* Tread Rise")
    length: FloatProperty(name="*Calculated* Length")

    def execute(self, context):
        add_object_stair(self, context)
        return {"FINISHED"}


def add_object_button(self, context):
    self.layout.operator(BIM_OT_add_object.bl_idname, icon="PLUGIN")
    self.layout.operator(BIM_OT_add_clever_stair.bl_idname, icon="PLUGIN")
