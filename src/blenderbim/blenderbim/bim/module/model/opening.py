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
import gpu
import bgl
import bmesh
import blenderbim.bim.handler
import ifcopenshell
import ifcopenshell.util.representation
import blenderbim.tool as tool
import blenderbim.core.geometry
from blenderbim.bim.ifc import IfcStore
from math import pi
from mathutils import Vector, Matrix
from bpy.types import Operator
from bpy.types import SpaceView3D
from bpy.props import FloatProperty
from bpy_extras.object_utils import AddObjectHelper, object_data_add
from gpu.types import GPUShader, GPUBatch, GPUIndexBuf, GPUVertBuf, GPUVertFormat
from gpu_extras.batch import batch_for_shader


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


class AddPotentialOpening(Operator, AddObjectHelper):
    bl_idname = "bim.add_potential_opening"
    bl_label = "Add Potential Opening"
    bl_options = {"REGISTER", "UNDO"}
    x: FloatProperty(name="X", default=0.5)
    y: FloatProperty(name="Y", default=0.5)
    z: FloatProperty(name="Z", default=0.5)

    def draw_settings(context, layout, tool):
        row = self.layout.row()
        row.prop(data=self, property="x", label="Size X")
        row = self.layout.row()
        row.prop(data=self, property="y")
        row = self.layout.row()
        row.prop(data=self, property="z")

    def execute(self, context):
        props = context.scene.BIMModelProperties

        new_matrix = None
        if context.selected_objects and context.active_object:
            new_matrix = context.active_object.matrix_world.copy()
            new_matrix.col[3] = context.scene.cursor.location.to_4d().to_4d()

        x = self.x / 2
        y = self.y / 2
        z = self.z / 2
        verts = [
            Vector((-x, -y, -z)),
            Vector((-x, -y, z)),
            Vector((-x, y, -z)),
            Vector((-x, y, z)),
            Vector((x, -y, -z)),
            Vector((x, -y, z)),
            Vector((x, y, -z)),
            Vector((x, y, z)),
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
        obj = object_data_add(context, mesh, operator=self)
        obj.name = "Opening"

        if new_matrix:
            obj.matrix_world = new_matrix

        tool.Model.clear_scene_openings()

        new = props.openings.add()
        new.obj = obj

        DecorationsHandler.install(context)
        return {"FINISHED"}


class AddPotentialHalfSpaceSolid(Operator, AddObjectHelper):
    bl_idname = "bim.add_potential_half_space_solid"
    bl_label = "Add Potential Half Space Solid"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        props = context.scene.BIMModelProperties
        bm = bmesh.new()
        bmesh.ops.create_grid(bm, size=0.5)
        bm.verts.ensure_lookup_table()
        bm.edges.ensure_lookup_table()
        bm.faces.ensure_lookup_table()
        mesh = bpy.data.meshes.new(name="Dumb Opening")
        bm.to_mesh(mesh)
        bm.free()
        obj = object_data_add(context, mesh, operator=self)
        obj.name = "HalfSpaceSolid"

        tool.Model.clear_scene_openings()

        new = props.openings.add()
        new.obj = obj

        DecorationsHandler.install(context)
        return {"FINISHED"}


class AddBoolean(Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_boolean"
    bl_label = "Add Boolean"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        props = context.scene.BIMModelProperties
        if len(context.selected_objects) != 2:
            return {"FINISHED"}
        obj1, obj2 = context.selected_objects
        element1 = tool.Ifc.get_entity(obj1)
        element2 = tool.Ifc.get_entity(obj2)
        if element1 and element2:
            return {"FINISHED"}
        if not element1 and not element2:
            return {"FINISHED"}
        if element2 and not element1:
            obj1, obj2 = obj2, obj1
        if not obj1.data or not hasattr(obj1.data, "BIMMeshProperties"):
            return {"FINISHED"}
        representation = tool.Ifc.get().by_id(obj1.data.BIMMeshProperties.ifc_definition_id)

        ifcopenshell.api.run(
            "geometry.add_boolean",
            tool.Ifc.get(),
            representation=representation,
            operator="DIFFERENCE",
            matrix=obj1.matrix_world.inverted() @ obj2.matrix_world,
        )

        tool.Model.clear_scene_openings()

        blenderbim.core.geometry.switch_representation(
            tool.Geometry,
            obj=obj1,
            representation=representation,
            should_reload=True,
            enable_dynamic_voids=False,
            is_global=True,
            should_sync_changes_first=False,
        )

        tool.Ifc.unlink(obj=obj2)
        bpy.data.objects.remove(obj2)
        return {"FINISHED"}


class ShowBooleans(Operator, tool.Ifc.Operator, AddObjectHelper):
    bl_idname = "bim.show_booleans"
    bl_label = "Show Booleans"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        obj = context.active_object
        if (
            not obj.data
            or not hasattr(obj.data, "BIMMeshProperties")
            or not obj.data.BIMMeshProperties.ifc_definition_id
        ):
            return {"FINISHED"}
        representation = tool.Ifc.get().by_id(obj.data.BIMMeshProperties.ifc_definition_id)
        booleans = []
        for item in representation.Items:
            booleans.extend(self.get_booleans(item))
        for boolean in booleans:
            if boolean.is_a() == "IfcHalfSpaceSolid":
                if boolean.BaseSurface.is_a("IfcPlane"):
                    boolean_obj = self.create_half_space_solid()
                    position = boolean.BaseSurface.Position
                    position = Matrix(ifcopenshell.util.placement.get_axis2placement(position).tolist())
                    boolean_obj.matrix_world = obj.matrix_world @ position
                    boolean_obj.data.BIMMeshProperties.ifc_boolean_id = boolean.id()
                    boolean_obj.data.BIMMeshProperties.obj = obj
        return {"FINISHED"}

    def get_booleans(self, item):
        results = []
        if item.is_a("IfcBooleanResult"):
            results.extend(self.get_booleans(item.FirstOperand))
            results.append(item.SecondOperand)
        return results

    def create_half_space_solid(self):
        props = bpy.context.scene.BIMModelProperties
        bm = bmesh.new()
        bmesh.ops.create_grid(bm, size=0.5)
        bm.verts.ensure_lookup_table()
        bm.edges.ensure_lookup_table()
        bm.faces.ensure_lookup_table()
        mesh = bpy.data.meshes.new(name="Dumb Opening")
        bm.to_mesh(mesh)
        bm.free()
        obj = object_data_add(bpy.context, mesh, operator=self)
        obj.name = "HalfSpaceSolid"

        tool.Model.clear_scene_openings()

        new = props.openings.add()
        new.obj = obj

        DecorationsHandler.install(bpy.context)
        return obj


class HideBooleans(Operator, tool.Ifc.Operator):
    bl_idname = "bim.hide_booleans"
    bl_label = "Hide Booleans"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        props = bpy.context.scene.BIMModelProperties
        for opening in props.openings:
            obj = opening.obj
            if obj.data.BIMMeshProperties.ifc_boolean_id:
                bpy.data.objects.remove(obj)
        return {"FINISHED"}


class RemoveBooleans(Operator, tool.Ifc.Operator, AddObjectHelper):
    bl_idname = "bim.remove_booleans"
    bl_label = "Remove Booleans"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        for obj in context.selected_objects:
            if (
                not obj.data
                or not hasattr(obj.data, "BIMMeshProperties")
                or not obj.data.BIMMeshProperties.ifc_boolean_id
            ):
                continue
            try:
                boolean = tool.Ifc.get().by_id(obj.data.BIMMeshProperties.ifc_boolean_id)
            except:
                continue
            ifcopenshell.api.run("geometry.remove_boolean", tool.Ifc.get(), item=boolean)
            if obj.data.BIMMeshProperties.obj:
                upstream_obj = obj.data.BIMMeshProperties.obj
                element = tool.Ifc.get_entity(upstream_obj)
                body = ifcopenshell.util.representation.get_representation(element, "Model", "Body", "MODEL_VIEW")
                if body:
                    blenderbim.core.geometry.switch_representation(
                        tool.Geometry,
                        obj=upstream_obj,
                        representation=body,
                        should_reload=True,
                        enable_dynamic_voids=False,
                        is_global=True,
                        should_sync_changes_first=False,
                    )
            bpy.data.objects.remove(obj)
        return {"FINISHED"}


class ShowOpenings(Operator, tool.Ifc.Operator):
    bl_idname = "bim.show_openings"
    bl_label = "Show Openings"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        props = bpy.context.scene.BIMModelProperties
        for obj in context.selected_objects:
            element = tool.Ifc.get_entity(obj)
            if not element:
                continue
            openings = tool.Model.load_openings(element, [r.RelatedOpeningElement for r in element.HasOpenings])
            for opening in openings:
                new = props.openings.add()
                new.obj = opening
        DecorationsHandler.install(bpy.context)
        return {"FINISHED"}


class HideOpenings(Operator, tool.Ifc.Operator):
    bl_idname = "bim.hide_openings"
    bl_label = "Hide Openings"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        props = bpy.context.scene.BIMModelProperties
        to_delete = set()
        for obj in context.selected_objects:
            element = tool.Ifc.get_entity(obj)
            if not element:
                continue
            openings = [r.RelatedOpeningElement for r in element.HasOpenings]
            for opening in openings:
                opening_obj = tool.Ifc.get_object(opening)
                if opening_obj:
                    to_delete.add(opening_obj)
        for opening_obj in to_delete:
            tool.Ifc.unlink(element=opening, obj=opening_obj)
            bpy.data.objects.remove(opening_obj)
        tool.Model.clear_scene_openings()
        return {"FINISHED"}


class EditOpenings(Operator, tool.Ifc.Operator):
    bl_idname = "bim.edit_openings"
    bl_label = "Edit Openings"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        props = bpy.context.scene.BIMModelProperties
        for obj in context.selected_objects:
            element = tool.Ifc.get_entity(obj)
            if not element:
                continue
            openings = [r.RelatedOpeningElement for r in element.HasOpenings]
            for opening in openings:
                opening_obj = tool.Ifc.get_object(opening)
                if opening_obj:
                    tool.Geometry.run_geometry_update_representation(obj=opening_obj)
                    tool.Ifc.unlink(element=opening, obj=opening_obj)
                    bpy.data.objects.remove(opening_obj)

            body = ifcopenshell.util.representation.get_representation(element, "Model", "Body", "MODEL_VIEW")
            blenderbim.core.geometry.switch_representation(
                tool.Geometry,
                obj=obj,
                representation=body,
                should_reload=True,
                enable_dynamic_voids=False,
                is_global=True,
                should_sync_changes_first=False,
            )
        return {"FINISHED"}


class DecorationsHandler:
    installed = None

    @classmethod
    def install(cls, context):
        if cls.installed:
            cls.uninstall()
        handler = cls()
        cls.installed = SpaceView3D.draw_handler_add(handler, (context,), "WINDOW", "POST_VIEW")

    @classmethod
    def uninstall(cls):
        try:
            SpaceView3D.draw_handler_remove(cls.installed, "WINDOW")
        except ValueError:
            pass
        cls.installed = None

    def __call__(self, context):
        bgl.glLineWidth(2)
        bgl.glPointSize(6)
        bgl.glEnable(bgl.GL_BLEND)
        bgl.glEnable(bgl.GL_LINE_SMOOTH)

        for opening in context.scene.BIMModelProperties.openings:
            obj = opening.obj

            if not obj:
                continue

            white = (1, 1, 1, 1)
            white_t = (1, 1, 1, 0.1)
            green = (0.545, 0.863, 0, 1)
            red = (1, 0.2, 0.322, 1)
            red_t = (1, 0.2, 0.322, 0.1)
            blue = (0.157, 0.565, 1, 1)
            blue_t = (0.157, 0.565, 1, 0.1)
            grey = (0.2, 0.2, 0.2, 1)

            self.shader = gpu.shader.from_builtin("3D_UNIFORM_COLOR")

            verts = []
            selected_edges = []
            unselected_edges = []
            selected_vertices = []
            unselected_vertices = []

            if obj.mode == "EDIT":
                bm = bmesh.from_edit_mesh(obj.data)

                for vertex in bm.verts:
                    co = tuple(obj.matrix_world @ vertex.co)
                    verts.append(co)
                    if vertex.hide:
                        continue

                    if vertex.select:
                        selected_vertices.append(co)
                    else:
                        unselected_vertices.append(co)

                for edge in bm.edges:
                    edge_indices = [v.index for v in edge.verts]
                    if edge.hide:
                        continue
                    if edge.select:
                        selected_edges.append(edge_indices)
                    else:
                        unselected_edges.append(edge_indices)

                batch = batch_for_shader(self.shader, "LINES", {"pos": verts}, indices=unselected_edges)
                self.shader.bind()
                self.shader.uniform_float("color", white)
                batch.draw(self.shader)

                batch = batch_for_shader(self.shader, "LINES", {"pos": verts}, indices=selected_edges)
                self.shader.uniform_float("color", green)
                batch.draw(self.shader)

                batch = batch_for_shader(self.shader, "POINTS", {"pos": unselected_vertices})
                self.shader.uniform_float("color", white)
                batch.draw(self.shader)

                batch = batch_for_shader(self.shader, "POINTS", {"pos": selected_vertices})
                self.shader.uniform_float("color", green)
                batch.draw(self.shader)
            else:
                bm = bmesh.new()
                bm.from_mesh(obj.data)

                verts = [tuple(obj.matrix_world @ v.co) for v in bm.verts]
                edges = [tuple([v.index for v in e.verts]) for e in bm.edges]

                batch = batch_for_shader(self.shader, "LINES", {"pos": verts}, indices=edges)
                self.shader.bind()
                self.shader.uniform_float("color", green if obj in context.selected_objects else blue)
                batch.draw(self.shader)

            obj.data.calc_loop_triangles()
            tris = [tuple(t.vertices) for t in obj.data.loop_triangles]

            batch = batch_for_shader(self.shader, "TRIS", {"pos": verts}, indices=tris)
            self.shader.bind()
            self.shader.uniform_float("color", blue_t)
            batch.draw(self.shader)

            if "HalfSpaceSolid" in obj.name:
                # Arrow shape
                verts = [
                    tuple(obj.matrix_world @ Vector((0, 0, 0))),
                    tuple(obj.matrix_world @ Vector((0, 0, 0.5))),
                    tuple(obj.matrix_world @ Vector((0.05, 0, 0.45))),
                    tuple(obj.matrix_world @ Vector((-0.05, 0, 0.45))),
                    tuple(obj.matrix_world @ Vector((0, 0.05, 0.45))),
                    tuple(obj.matrix_world @ Vector((0, -0.05, 0.45))),
                ]
                edges = [(0, 1), (1, 2), (1, 3), (1, 4), (1, 5)]
                batch = batch_for_shader(self.shader, "LINES", {"pos": verts}, indices=edges)
                self.shader.bind()
                self.shader.uniform_float("color", green if obj in context.selected_objects else blue)
                batch.draw(self.shader)

            if obj.mode != "EDIT":
                bm.free()
