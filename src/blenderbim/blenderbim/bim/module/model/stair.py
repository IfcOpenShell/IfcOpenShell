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

import bmesh
from bmesh.types import BMVert

import ifcopenshell
import blenderbim
import blenderbim.tool as tool
from blenderbim.bim.module.model.prop import BIMStairProperties


from mathutils import Vector
from pprint import pprint
import json


def add_dumb_stair_object(self, context):
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
    number_of_treads: IntProperty(name="Number of Treads (Goings)", default=6, soft_min=1)
    tread_length: FloatProperty(name="Tread Length (Going)", default=0.25)
    riser_height: FloatProperty(name="*Calculated* Riser Height")
    length: FloatProperty(name="*Calculated* Length")

    def execute(self, context):
        add_dumb_stair_object(self, context)
        return {"FINISHED"}


def generate_stair_2d_profile(
    number_of_treads,
    height,
    width,
    tread_run,
    tread_depth,
    stair_type,
    # CONCRETE STAIR ARGUMENTS
    has_top_nib=None,
    top_slab_depth=None,
    base_slab_depth=None,
):
    vertices = []
    edges = []
    faces = []

    number_of_risers = number_of_treads + 1
    tread_rise = height / number_of_risers
    length = tread_run * number_of_risers

    if stair_type == "WOOD/STEEL":
        for i in range(number_of_risers):
            v1 = Vector(((i + 1) * tread_run, 0, (i + 1) * tread_rise))
            v0 = v1 - Vector((tread_run, 0, 0))
            v2 = v1 - Vector((0, 0, tread_depth))
            v3 = v0 - Vector((0, 0, tread_depth))
            vertices.extend([v0, v1, v2, v3])

            cur_vertex = i * 4
            edges.extend([
                (cur_vertex, cur_vertex+1),
                (cur_vertex+1, cur_vertex+2),
                (cur_vertex+2, cur_vertex+3),
                (cur_vertex+3, cur_vertex),
            ])
            faces.append(list(range(4 * i, 4 * i + 1)))

        return (vertices, edges, faces)
    elif stair_type == "CONCRETE":
        for i in range(number_of_risers):
            vertices.extend([
                Vector((tread_run*i, 0, tread_rise*i)),
                Vector((tread_run*i, 0, tread_rise*(i+1)))
            ])
            cur_vertex = i * 2
            if i != 0:
                edges.append((cur_vertex - 1, cur_vertex))
            edges.append((cur_vertex, cur_vertex + 1))

        vertices.append(Vector((tread_run * number_of_risers, 0, tread_rise * number_of_risers)))
        edges.append((number_of_risers * 2, number_of_risers * 2 - 1))

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
            vertices.append( vertices[number_of_risers * 2] + Vector((0, 0, -top_slab_depth)) )
            vertices.append( vertices[number_of_risers * 2] + Vector(((-top_slab_depth - b) / k, 0, -top_slab_depth)) )
            last_vertex_i = len(vertices) - 1
            edges.append( (number_of_risers * 2, last_vertex_i - 1) )
            edges.append( (last_vertex_i - 1, last_vertex_i) )
        else:
            vertices.append(vertices[number_of_risers * 2] + depth_vector)
            last_vertex_i = len(vertices) - 1
            edges.append((number_of_risers * 2, last_vertex_i))

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

        return (vertices, edges, faces)


def update_stair_modifier(context):
    obj = context.active_object
    props = obj.BIMStairProperties

    props_kwargs = props.get_props_kwargs()
    vertices, edges, faces = generate_stair_2d_profile(**props_kwargs)

    obj = context.object
    bm = bmesh.new()
    bm.verts.index_update()
    bm.edges.index_update()

    new_verts = [bm.verts.new(v) for v in vertices]
    new_edges = [bm.edges.new( (new_verts[e[0]], new_verts[e[1]]) ) for e in edges]
    bm.verts.index_update()
    bm.edges.index_update()

    bmesh.ops.contextual_create(bm, geom=new_edges)

    bm.faces.ensure_lookup_table()
    faces = bm.faces
    extruded = bmesh.ops.extrude_face_region(bm, geom=faces)
    extrusion_vector = Vector((0, 1, 0)) * props.width
    translate_verts = [v for v in extruded["geom"] if isinstance(v, BMVert)]
    bmesh.ops.translate(bm, vec=extrusion_vector, verts=translate_verts)

    if context.object.mode == "EDIT":
        bmesh.update_edit_mesh(obj.data)
    else:
        bm.to_mesh(obj.data)
        bm.free()
    obj.data.update()


class BIM_OT_add_clever_stair(Operator):
    bl_idname = "mesh.add_clever_stair"
    bl_label = "Clever Stair"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        ifcfile = tool.Ifc.get()
        if not ifcfile:
            self.report({"ERROR"}, "You need to start IFC project first to create a stair.")
            return {"CANCELLED"}

        if context.object is not None:
            spawn_location = context.object.location.copy()
            context.object.select_set(False)
        else:
            spawn_location = bpy.context.scene.cursor.location.copy()

        mesh = bpy.data.meshes.new("StairFlight")
        obj = bpy.data.objects.new("StairFlight", mesh)
        bpy.context.scene.collection.objects.link(obj)
        obj.location = spawn_location
        body_context = ifcopenshell.util.representation.get_context(ifcfile, "Model", "Body", "MODEL_VIEW")
        element = blenderbim.core.root.assign_class(
            tool.Ifc,
            tool.Collector,
            tool.Root,
            obj=obj,
            ifc_class="IfcStairFlight",
            should_add_representation=True,
            context=body_context,
        )
        bpy.context.view_layer.objects.active = None
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        bpy.ops.bim.add_stair()
        return {"FINISHED"}


# UI operators
class AddStair(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_stair"
    bl_label = "Add Stair"
    bl_options = {"REGISTER"}

    def _execute(self, context):
        obj = context.active_object
        element = tool.Ifc.get_entity(obj)

        if not element.is_a("IfcStairFlight"):
            self.report({"ERROR"}, "Object has to be IfcStairFlight type to add a stair.")
            return {"CANCELLED"}

        props = obj.BIMStairProperties

        stair_data = props.get_props_kwargs()
        psets = ifcopenshell.util.element.get_psets(element)
        pset = psets.get("BBIM_Stair", None)

        if pset:
            pset = tool.Ifc.get().by_id(pset["id"])
        else:
            pset = ifcopenshell.api.run("pset.add_pset", tool.Ifc.get(), product=element, name="BBIM_Stair")

        ifcopenshell.api.run(
            "pset.edit_pset",
            tool.Ifc.get(),
            pset=pset,
            properties={"Data": json.dumps(stair_data)},
        )
        update_stair_modifier(context)

        # update IfcStairFlight properties
        element.NumberOfRisers = props.number_of_treads + 1
        element.NumberOfTreads = props.number_of_treads
        element.RiserHeight = props.height / element.NumberOfRisers
        element.TreadLength = props.tread_depth
        element.PredefinedType = "STRAIGHT"
        return {"FINISHED"}


class CancelEditingStair(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.cancel_editing_stair"
    bl_label = "Cancel editing Stair"
    bl_options = {"REGISTER"}

    def _execute(self, context):
        obj = context.active_object
        element = tool.Ifc.get_entity(obj)
        psets = ifcopenshell.util.element.get_psets(element)
        data = json.loads(psets["BBIM_Stair"]["Data"])
        props = obj.BIMStairProperties
        # restore previous settings since editing was canceled
        for prop_name in data:
            setattr(props, prop_name, data[prop_name])
        update_stair_modifier(context)

        props.is_editing = -1

        return {"FINISHED"}


class FinishEditingStair(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.finish_editing_stair"
    bl_label = "Finish editing stair"
    bl_options = {"REGISTER"}

    def _execute(self, context):
        obj = context.active_object
        element = tool.Ifc.get_entity(obj)
        props = obj.BIMStairProperties

        psets = ifcopenshell.util.element.get_psets(element)
        pset = psets["BBIM_Stair"]
        data = props.get_props_kwargs()

        props.is_editing = -1

        update_stair_modifier(context)

        pset = tool.Ifc.get().by_id(pset["id"])
        data = json.dumps(data)
        ifcopenshell.api.run("pset.edit_pset", tool.Ifc.get(), pset=pset, properties={"Data": data})

        # update IfcStairFlight properties
        if element.is_a("IfcStairFlight"):
            element.NumberOfRisers = props.number_of_treads + 1
            element.NumberOfTreads = props.number_of_treads
            element.RiserHeight = props.height / element.NumberOfRisers
            element.TreadLength = props.tread_depth
            element.PredefinedType = "STRAIGHT"
        return {"FINISHED"}


class EnableEditingStair(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.enable_editing_stair"
    bl_label = "Enable Editing Stair"
    bl_options = {"REGISTER"}

    def _execute(self, context):
        obj = context.active_object
        props = obj.BIMStairProperties
        element = tool.Ifc.get_entity(obj)
        pset = ifcopenshell.util.element.get_psets(element)
        data = json.loads(pset["BBIM_Stair"]["Data"])
        # required since we could load pset from .ifc and BIMStairProperties won't be set
        for prop_name in data:
            setattr(props, prop_name, data[prop_name])

        props.is_editing = 1


class RemoveStair(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.remove_stair"
    bl_label = "Remove Stair"
    bl_options = {"REGISTER"}

    def _execute(self, context):
        obj = context.active_object
        element = tool.Ifc.get_entity(obj)
        obj.BIMStairProperties.is_editing = -1

        pset = ifcopenshell.util.element.get_psets(element)
        pset = tool.Ifc.get().by_id(pset["BBIM_Stair"]["id"])
        ifcopenshell.api.run("pset.remove_pset", tool.Ifc.get(), pset=pset)

        return {"FINISHED"}


def add_object_button(self, context):
    self.layout.operator(BIM_OT_add_object.bl_idname, icon="PLUGIN")
    self.layout.operator(BIM_OT_add_clever_stair.bl_idname, icon="PLUGIN")
