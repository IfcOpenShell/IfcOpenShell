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
import bmesh
import blenderbim.bim.handler
import ifcopenshell
import ifcopenshell.util.representation
from blenderbim.bim.ifc import IfcStore
from math import pi
from mathutils import Vector
from bpy.types import Operator
from bpy.props import FloatProperty
from bpy_extras.object_utils import AddObjectHelper, object_data_add


def element_listener(element, obj):
    blenderbim.bim.handler.subscribe_to(obj, "mode", mode_callback)


def mode_callback(obj, data):
    for obj in set(bpy.context.selected_objects + [bpy.context.active_object]):
        if (
            obj.mode != "EDIT"
            or not obj.data
            or not isinstance(obj.data, (bpy.types.Mesh, bpy.types.Curve, bpy.types.TextCurve))
            or not obj.BIMObjectProperties.ifc_definition_id
            or not bpy.context.scene.BIMProjectProperties.is_authoring
        ):
            return
        product = IfcStore.get_file().by_id(obj.BIMObjectProperties.ifc_definition_id)
        if not product.is_a("IfcOpeningElement"):
            return
        for rel in product.VoidsElements:
            building_element_obj = IfcStore.get_element(rel.RelatingBuildingElement.id())
            if not building_element_obj:
                continue
            if [m for m in building_element_obj.modifiers if m.type == "BOOLEAN"]:
                continue
            representation = ifcopenshell.util.representation.get_representation(
                rel.RelatingBuildingElement, "Model", "Body", "MODEL_VIEW"
            )
            if not representation:
                continue
            bpy.ops.bim.switch_representation(
                obj=building_element_obj.name,
                should_switch_all_meshes=True,
                should_reload=True,
                ifc_definition_id=representation.id(),
                disable_opening_subtractions=True,
            )
        IfcStore.edited_objs.add(obj)
        bm = bmesh.from_edit_mesh(obj.data)
        bmesh.ops.dissolve_limit(bm, angle_limit=pi / 180 * 1, verts=bm.verts, edges=bm.edges)
        bmesh.update_edit_mesh(obj.data)
        bm.free()


class AddElementOpening(bpy.types.Operator):
    bl_idname = "bim.add_element_opening"
    bl_label = "Add Element Opening"
    bl_options = {"REGISTER", "UNDO"}
    voided_building_element: bpy.props.StringProperty()
    filling_building_element: bpy.props.StringProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        voided_obj = self.get_voided_building_element(context)
        filling_obj = self.get_filling_building_element(context)

        if not voided_obj:
            return {"FINISHED"}

        element = IfcStore.get_file().by_id(voided_obj.BIMObjectProperties.ifc_definition_id)
        local_location = voided_obj.matrix_world.inverted() @ context.scene.cursor.location
        raycast = voided_obj.closest_point_on_mesh(local_location, distance=0.01)
        if not raycast[0]:
            return {"FINISHED"}

        if filling_obj:
            opening = self.generate_opening_from_filling(filling_obj, voided_obj)
        else:
            # The opening shall be based on the smallest bounding dimension of the element
            dimension = min(voided_obj.dimensions)
            bpy.ops.mesh.primitive_cube_add(size=dimension * 2)
            opening = context.selected_objects[0]

            # Place the opening in the middle of the element
            global_location = voided_obj.matrix_world @ raycast[1]
            normal = raycast[2]
            normal.negate()
            global_normal = voided_obj.matrix_world.to_quaternion() @ normal
            opening.location = global_location + (global_normal * (dimension / 2))
            opening.rotation_euler = voided_obj.rotation_euler
            opening.name = "Opening"

        bpy.ops.bim.add_opening(opening=opening.name, obj=voided_obj.name)
        if filling_obj:
            bpy.ops.bim.add_filling(opening=opening.name, obj=filling_obj.name)
        return {"FINISHED"}

    def get_voided_building_element(self, context):
        obj = None
        if self.voided_building_element:
            obj = bpy.data.objects.get(self.voided_building_element)
        else:
            total_selected = len(context.selected_objects)
            if total_selected == 1 or total_selected == 2:
                obj = context.active_object
        if obj and obj.BIMObjectProperties.ifc_definition_id:
            return obj

    def get_filling_building_element(self, context):
        obj = None
        if self.filling_building_element:
            obj = bpy.data.objects.get(self.filling_building_element)
        else:
            total_selected = len(context.selected_objects)
            if total_selected == 2:
                if context.selected_objects[0] == context.active_object:
                    obj = context.selected_objects[1]
                else:
                    obj = context.selected_objects[0]
        if obj and obj.BIMObjectProperties.ifc_definition_id:
            return obj

    def generate_opening_from_filling(self, filling_obj, voided_obj):
        x, y, z = filling_obj.dimensions
        dimension = min(voided_obj.dimensions)
        if dimension == voided_obj.dimensions[0]:
            verts = [
                Vector((-0.1, 0, 0)),
                Vector((-0.1, 0, z)),
                Vector((-0.1, y, 0)),
                Vector((-0.1, y, z)),
                Vector((dimension + 0.1, 0, 0)),
                Vector((dimension + 0.1, 0, z)),
                Vector((dimension + 0.1, y, 0)),
                Vector((dimension + 0.1, y, z)),
            ]
        elif dimension == voided_obj.dimensions[1]:
            verts = [
                Vector((0, -0.1, 0)),
                Vector((0, -0.1, z)),
                Vector((0, dimension + 0.1, 0)),
                Vector((0, dimension + 0.1, z)),
                Vector((x, -0.1, 0)),
                Vector((x, -0.1, z)),
                Vector((x, dimension + 0.1, 0)),
                Vector((x, dimension + 0.1, z)),
            ]
        elif dimension == voided_obj.dimensions[2]:
            verts = [
                Vector((0, 0, -0.1)),
                Vector((0, 0, dimension + 0.1)),
                Vector((0, y, -0.1)),
                Vector((0, y, dimension + 0.1)),
                Vector((x, 0, -0.1)),
                Vector((x, 0, dimension + 0.1)),
                Vector((x, y, -0.1)),
                Vector((x, y, dimension + 0.1)),
            ]
        edges = []
        faces = [
            [0, 1, 3, 2],
            [2, 3, 7, 6],
            [6, 7, 5, 4],
            [4, 5, 1, 0],
            [2, 6, 4, 0],
            [7, 3, 1, 5],
        ]
        mesh = bpy.data.meshes.new(name="Opening")
        mesh.from_pydata(verts, edges, faces)
        obj = bpy.data.objects.new("Opening", mesh)
        obj.matrix_world = filling_obj.matrix_world

        filling_obj.rotation_euler = voided_obj.rotation_euler
        obj.parent = filling_obj
        obj.matrix_parent_inverse = filling_obj.matrix_world.inverted()
        return obj


def add_object(self, context):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=self.size)
    bm.verts.ensure_lookup_table()
    bm.edges.ensure_lookup_table()
    bm.faces.ensure_lookup_table()
    mesh = bpy.data.meshes.new(name="Dumb Opening")
    bm.to_mesh(mesh)
    bm.free()
    obj = object_data_add(context, mesh, operator=self)
    obj.name = "Opening"
    obj.display_type = "WIRE"


class BIM_OT_add_object(Operator, AddObjectHelper):
    bl_idname = "mesh.add_opening"
    bl_label = "Dumb Opening"
    bl_options = {"REGISTER", "UNDO"}

    size: FloatProperty(name="Size", default=2)

    def execute(self, context):
        add_object(self, context)
        return {"FINISHED"}


def add_object_button(self, context):
    self.layout.operator(BIM_OT_add_object.bl_idname, icon="PLUGIN")
