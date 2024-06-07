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
import json
import bmesh
import ifcopenshell
import ifcopenshell.api
import ifcopenshell.util.representation
import ifcopenshell.util.unit
import blenderbim
import blenderbim.core.root
import blenderbim.tool as tool
from mathutils import Vector
from bmesh.types import BMVert
from bpy.types import Operator
from bpy.props import FloatProperty, IntProperty
from bpy_extras.object_utils import AddObjectHelper, object_data_add


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


def regenerate_stair_mesh(context):
    obj = context.active_object
    props_kwargs = obj.BIMStairProperties.get_props_kwargs()
    vertices, edges, faces = tool.Model.generate_stair_2d_profile(**props_kwargs)

    obj = context.active_object
    bm = bmesh.new()
    bm.verts.index_update()
    bm.edges.index_update()

    new_verts = [bm.verts.new(v) for v in vertices]
    new_edges = [bm.edges.new((new_verts[e[0]], new_verts[e[1]])) for e in edges]
    bm.verts.index_update()
    bm.edges.index_update()

    bmesh.ops.contextual_create(bm, geom=new_edges)

    bm.faces.ensure_lookup_table()
    faces = bm.faces
    extruded = bmesh.ops.extrude_face_region(bm, geom=faces)
    extrusion_vector = Vector((0, 1, 0)) * props_kwargs["width"]
    translate_verts = [v for v in extruded["geom"] if isinstance(v, BMVert)]
    bmesh.ops.translate(bm, vec=extrusion_vector, verts=translate_verts)

    if context.active_object.mode == "EDIT":
        bmesh.update_edit_mesh(obj.data)
    else:
        bm.to_mesh(obj.data)
        bm.free()
    obj.data.update()


def update_stair_representation(obj):
    body = ifcopenshell.util.representation.get_context(tool.Ifc.get(), "Model", "Body", "MODEL_VIEW")
    representation = ifcopenshell.api.run(
        "geometry.add_representation",
        tool.Ifc.get(),
        context=body,
        blender_object=obj,
        geometry=obj.data,
        coordinate_offset=tool.Geometry.get_cartesian_point_coordinate_offset(obj),
        total_items=tool.Geometry.get_total_representation_items(obj),
        should_force_faceted_brep=tool.Geometry.should_force_faceted_brep(),
        should_force_triangulation=tool.Geometry.should_force_triangulation(),
        should_generate_uvs=tool.Geometry.should_generate_uvs(obj),
        ifc_representation_class=None,
        profile_set_usage=None,
    )
    tool.Model.replace_object_ifc_representation(body, obj, representation)
    tool.Ifc.finish_edit(obj)


def update_ifc_stair_props(obj):
    """should be called after new geometry settled
    since it's going to update ifc representation
    """
    element = tool.Ifc.get_entity(obj)
    props = obj.BIMStairProperties
    ifc_file = tool.Ifc.get()

    if tool.Ifc.get_schema() != "IFC2X3":
        element.PredefinedType = "STRAIGHT"
    number_of_risers = props.number_of_treads + 1
    # update IfcStairFlight properties (seems already deprecated but keep it for now)
    # http://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcStairFlight.htm

    si_conversion = ifcopenshell.util.unit.calculate_unit_scale(ifc_file)
    riser_height = props.height / number_of_risers / si_conversion
    tread_length = props.tread_depth / si_conversion
    nosing_length = props.nosing_length / si_conversion

    if element.is_a("IfcStairFlight"):
        if tool.Ifc.get_schema() == "IFC2X3":
            element.NumberOfRiser = number_of_risers
        else:
            element.NumberOfRisers = number_of_risers

        element.NumberOfTreads = props.number_of_treads
        element.RiserHeight = riser_height
        element.TreadLength = tread_length

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
            "RiserHeight": riser_height,
            "TreadLength": tread_length,
            "NosingLength": nosing_length,
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

        if context.active_object is not None:
            spawn_location = context.active_object.location.copy()
            context.active_object.select_set(False)
        else:
            spawn_location = bpy.context.scene.cursor.location.copy()

        mesh = bpy.data.meshes.new("IfcStairFlight")
        obj = bpy.data.objects.new("StairFlight", mesh)
        obj.location = spawn_location
        collection = context.view_layer.active_layer_collection.collection
        collection.objects.link(obj)

        element = blenderbim.core.root.assign_class(
            tool.Ifc,
            tool.Collector,
            tool.Root,
            obj=obj,
            ifc_class="IfcStairFlight",
            should_add_representation=False,
        )
        if tool.Ifc.get_schema() != "IFC2X3":
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

        stair_data = props.get_props_kwargs(convert_to_project_units=True)
        pset = tool.Pset.get_element_pset(element, "BBIM_Stair")
        if not pset:
            pset = ifcopenshell.api.run("pset.add_pset", ifc_file, product=element, name="BBIM_Stair")

        ifcopenshell.api.run(
            "pset.edit_pset",
            ifc_file,
            pset=pset,
            properties={"Data": tool.Ifc.get().createIfcText(json.dumps(stair_data))},
        )
        regenerate_stair_mesh(context)
        update_ifc_stair_props(obj)
        update_stair_representation(obj)


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
        regenerate_stair_mesh(context)

        props.is_editing = False

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
        props.is_editing = False
        regenerate_stair_mesh(context)
        update_stair_representation(obj)

        pset = tool.Pset.get_element_pset(element, "BBIM_Stair")
        data = tool.Ifc.get().createIfcText(json.dumps(data))
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
        props.is_editing = True
        return {"FINISHED"}


class RemoveStair(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.remove_stair"
    bl_label = "Remove Stair"
    bl_options = {"REGISTER"}

    def _execute(self, context):
        obj = context.active_object
        props = obj.BIMStairProperties
        element = tool.Ifc.get_entity(obj)
        obj.BIMStairProperties.is_editing = False

        pset = tool.Pset.get_element_pset(element, "BBIM_Stair")
        ifcopenshell.api.run("pset.remove_pset", tool.Ifc.get(), product=element, pset=pset)

        return {"FINISHED"}
