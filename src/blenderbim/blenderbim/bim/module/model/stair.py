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
from bpy.props import FloatProperty, IntProperty
from bpy_extras.object_utils import AddObjectHelper, object_data_add

import bmesh
from bmesh.types import BMVert

import ifcopenshell
from ifcopenshell.util.shape_builder import V, ShapeBuilder
import blenderbim
import blenderbim.tool as tool

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
    stair_type,
    # WOOD/STEEL CONCRETE STAIR ARGUMENTS
    tread_depth=None,
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
        builder = ShapeBuilder(None)
        tread_shape = builder.get_rectangle_coords(
            size=V(tread_run, 0, tread_depth),
            position=V(0, 0, -(tread_depth-tread_rise))
        )
        tread_offset = V(tread_run, 0, tread_rise)

        for i in range(number_of_risers):
            cur_trade_shape = [v + tread_offset * i for v in tread_shape]
            vertices.extend(cur_trade_shape)

            cur_vertex = i * 4
            edges.extend([
                (cur_vertex, cur_vertex+1),
                (cur_vertex+1, cur_vertex+2),
                (cur_vertex+2, cur_vertex+3),
                (cur_vertex+3, cur_vertex),
            ])
            faces.append(list(range(cur_vertex, cur_vertex + 1)))

        return (vertices, edges, faces)

    elif stair_type == "GENERIC":
        vertices.append(Vector([0, 0, 0]))

        tread_verts = [
            Vector([0, 0, tread_rise]),
            Vector([tread_run, 0, tread_rise])
        ]
        tread_offset = Vector([tread_run, 0, tread_rise])

        for i in range(number_of_risers):
            current_tread_verts = [v + tread_offset * i for v in tread_verts]
            last_vert_i = len(vertices) - 1
            edges.extend([
                (last_vert_i, last_vert_i + 1),
                (last_vert_i + 1, last_vert_i + 2)
            ])
            vertices.extend(current_tread_verts)

        last_vert_i = len(vertices)
        vertices.append(vertices[-1] * V(1,0,0))
        edges.extend([
            (last_vert_i - 1, last_vert_i),
            (last_vert_i, 0)
        ])

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
    props_kwargs = obj.BIMStairProperties.get_props_kwargs()
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
    extrusion_vector = Vector((0, 1, 0)) * props_kwargs["width"]
    translate_verts = [v for v in extruded["geom"] if isinstance(v, BMVert)]
    bmesh.ops.translate(bm, vec=extrusion_vector, verts=translate_verts)

    if context.object.mode == "EDIT":
        bmesh.update_edit_mesh(obj.data)
    else:
        bm.to_mesh(obj.data)
        bm.free()
    obj.data.update()


def update_ifc_stair_props(obj):
    """should be called after new geometry settled
    since it's going to update ifc representation
    """
    element = tool.Ifc.get_entity(obj)
    props = obj.BIMStairProperties
    ifc_file = tool.Ifc.get()

    element.PredefinedType = "STRAIGHT"
    number_of_risers = props.number_of_treads + 1
    # update IfcStairFlight properties (seems already deprecated but keep it for now)
    # http://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcStairFlight.htm
    if element.is_a("IfcStairFlight"):
        element.NumberOfRisers = number_of_risers
        element.NumberOfTreads = props.number_of_treads
        element.RiserHeight = props.height / number_of_risers
        element.TreadLength = props.tread_depth

    # update pset with ifc properties
    pset_common = tool.Pset.get_element_pset(element, "Pset_StairFlightCommon")
    if not pset_common:
        pset_common = ifcopenshell.api.run("pset.add_pset", ifc_file, product=element, name="Pset_StairFlightCommon")

    ifcopenshell.api.run(
        "pset.edit_pset",
        ifc_file,
        pset=pset_common,
        properties={
            "NumberOfRiser": number_of_risers,
            "NumberOfTreads": props.number_of_treads,
            "RiserHeight": props.height / number_of_risers,
            "TreadLength": props.tread_depth,
        },
    )
    tool.Ifc.edit(obj)

    # update related annotation objects
    def get_elements_from_product(product):
        elements = []
        for rel in product.ReferencedBy:
            if not rel.is_a("IfcRelAssignsToProduct"):
                continue
            elements.extend(rel.RelatedObjects)
        return elements

    stair_obj = obj
    for rel_element in get_elements_from_product(element):
        if not rel_element.is_a("IfcAnnotation") or rel_element.ObjectType != "STAIR_ARROW":
            continue
        if annotation_obj := tool.Ifc.get_object(rel_element):
            tool.Drawing.setup_annotation_object(annotation_obj, "STAIR_ARROW", stair_obj)


class BIM_OT_add_clever_stair(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "mesh.add_clever_stair"
    bl_label = "Clever Stair"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        ifc_file = tool.Ifc.get()
        if not ifc_file:
            self.report({"ERROR"}, "You need to start IFC project first to create a stair.")
            return {"CANCELLED"}

        if context.object is not None:
            spawn_location = context.object.location.copy()
            context.object.select_set(False)
        else:
            spawn_location = bpy.context.scene.cursor.location.copy()

        mesh = bpy.data.meshes.new("IfcStairFlight")
        obj = bpy.data.objects.new("StairFlight", mesh)
        obj.location = spawn_location
        body_context = ifcopenshell.util.representation.get_context(ifc_file, "Model", "Body", "MODEL_VIEW")
        element = blenderbim.core.root.assign_class(
            tool.Ifc,
            tool.Collector,
            tool.Root,
            obj=obj,
            ifc_class="IfcStairFlight",
            should_add_representation=True,
            context=body_context,
        )
        element.PredefinedType = "STRAIGHT"

        bpy.ops.object.select_all(action="DESELECT")
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
        props = obj.BIMStairProperties
        ifc_file = tool.Ifc.get()

        if element.is_a() not in ("IfcStairFlight", "IfcStairFlightType"):
            self.report({"ERROR"}, "Object has to be IfcStairFlight/IfcStairFlightType to add a stair.")
            return {"CANCELLED"}

        stair_data = props.get_props_kwargs(convert_to_project_units=True)
        pset = tool.Pset.get_element_pset(element, "BBIM_Stair")
        if not pset:
            pset = ifcopenshell.api.run("pset.add_pset", ifc_file, product=element, name="BBIM_Stair")

        ifcopenshell.api.run(
            "pset.edit_pset",
            ifc_file,
            pset=pset,
            properties={"Data": json.dumps(stair_data)},
        )
        update_stair_modifier(context)
        update_ifc_stair_props(obj)


class CancelEditingStair(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.cancel_editing_stair"
    bl_label = "Cancel Editing Stair"
    bl_options = {"REGISTER"}

    def _execute(self, context):
        obj = context.active_object
        element = tool.Ifc.get_entity(obj)
        data = json.loads(ifcopenshell.util.element.get_pset(element, "BBIM_Stair", "Data"))
        props = obj.BIMStairProperties
        # restore previous settings since editing was canceled
        props.set_props_kwargs_from_ifc_data(data)
        update_stair_modifier(context)

        props.is_editing = -1

        return {"FINISHED"}


class FinishEditingStair(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.finish_editing_stair"
    bl_label = "Finish Editing Stair"
    bl_options = {"REGISTER"}

    def _execute(self, context):
        obj = context.active_object
        element = tool.Ifc.get_entity(obj)
        props = obj.BIMStairProperties

        data = props.get_props_kwargs(convert_to_project_units=True)
        props.is_editing = -1
        update_stair_modifier(context)

        pset = tool.Pset.get_element_pset(element, "BBIM_Stair")
        data = json.dumps(data)
        ifcopenshell.api.run("pset.edit_pset", tool.Ifc.get(), pset=pset, properties={"Data": data})

        # update IfcStairFlight properties
        update_ifc_stair_props(obj)
        return {"FINISHED"}


class EnableEditingStair(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.enable_editing_stair"
    bl_label = "Enable Editing Stair"
    bl_options = {"REGISTER"}

    def _execute(self, context):
        obj = context.active_object
        props = obj.BIMStairProperties
        element = tool.Ifc.get_entity(obj)
        data = json.loads(ifcopenshell.util.element.get_pset(element, "BBIM_Stair", "Data"))
        # required since we could load pset from .ifc and BIMStairProperties won't be set
        props.set_props_kwargs_from_ifc_data(data)
        props.is_editing = 1
        return {"FINISHED"}


class RemoveStair(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.remove_stair"
    bl_label = "Remove Stair"
    bl_options = {"REGISTER"}

    def _execute(self, context):
        obj = context.active_object
        props = obj.BIMStairProperties
        element = tool.Ifc.get_entity(obj)
        obj.BIMStairProperties.is_editing = -1

        pset = tool.Pset.get_element_pset(element, "BBIM_Stair")
        ifcopenshell.api.run("pset.remove_pset", tool.Ifc.get(), pset=pset)
        props.stair_added_previously = True

        return {"FINISHED"}


def add_object_button(self, context):
    self.layout.operator(BIM_OT_add_object.bl_idname, icon="PLUGIN")
    self.layout.operator(BIM_OT_add_clever_stair.bl_idname, icon="PLUGIN")
