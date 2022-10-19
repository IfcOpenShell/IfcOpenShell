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
import logging
import blenderbim.bim.handler
import ifcopenshell
import ifcopenshell.util.representation
import blenderbim.tool as tool
import blenderbim.core.geometry
import blenderbim.bim.import_ifc as import_ifc
from blenderbim.bim.ifc import IfcStore
from math import pi
from mathutils import Vector, Matrix
from bpy.types import Operator
from bpy.types import SpaceView3D
from bpy.props import FloatProperty
from bpy_extras.object_utils import AddObjectHelper, object_data_add
from gpu.types import GPUShader, GPUBatch, GPUIndexBuf, GPUVertBuf, GPUVertFormat
from gpu_extras.batch import batch_for_shader


class AddFilledOpening(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_filled_opening"
    bl_label = "Add Filled Opening"
    bl_options = {"REGISTER", "UNDO"}
    voided_obj: bpy.props.StringProperty()
    filling_obj: bpy.props.StringProperty()

    def _execute(self, context):
        props = context.scene.BIMModelProperties
        unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())

        voided_obj = bpy.data.objects.get(self.voided_obj)
        filling_obj = bpy.data.objects.get(self.filling_obj)
        filling = tool.Ifc.get_entity(filling_obj)

        if not voided_obj or not filling_obj:
            return {"FINISHED"}

        element = tool.Ifc.get_entity(voided_obj)
        target = context.scene.cursor.location
        raycast = voided_obj.closest_point_on_mesh(voided_obj.matrix_world.inverted() @ target, distance=0.01)
        if not raycast[0]:
            target = filling_obj.matrix_world.col[3].to_3d().copy()
            raycast = voided_obj.closest_point_on_mesh(voided_obj.matrix_world.inverted() @ target, distance=0.5)
            if not raycast[0]:
                return {"FINISHED"}

        # In this prototype, we assume openings are only added to axis-based elements
        layers = tool.Model.get_material_layer_parameters(element)
        axis = tool.Model.get_wall_axis(voided_obj, layers=layers)["base"]

        new_matrix = voided_obj.matrix_world.copy()
        new_matrix.col[3] = tool.Cad.point_on_edge(target, axis).to_4d()
        if not filling.is_a("IfcDoor"):
            container = ifcopenshell.util.element.get_container(element)
            if container:
                container_obj = tool.Ifc.get_object(container)
                if container_obj:
                    new_matrix[2][3] = container_obj.matrix_world[2][3] + (props.rl2 * unit_scale)
        filling_obj.matrix_world = new_matrix
        bpy.context.view_layer.update()

        opening_obj = self.generate_opening_from_filling(filling, filling_obj, voided_obj)

        # Still prototyping, for now duplicating code from bpy.ops.bim.add_opening
        if tool.Ifc.is_moved(voided_obj):
            blenderbim.core.geometry.edit_object_placement(tool.Ifc, tool.Geometry, tool.Surveyor, obj=voided_obj)

        has_visible_openings = False
        for opening in [r.RelatedOpeningElement for r in element.HasOpenings]:
            if tool.Ifc.get_object(opening):
                has_visible_openings = True
                break

        body_context = ifcopenshell.util.representation.get_context(IfcStore.get_file(), "Model", "Body")
        opening = blenderbim.core.root.assign_class(
            tool.Ifc,
            tool.Collector,
            tool.Root,
            obj=opening_obj,
            ifc_class="IfcOpeningElement",
            should_add_representation=True,
            context=body_context,
        )
        ifcopenshell.api.run("void.add_opening", tool.Ifc.get(), opening=opening, element=element)

        representation = tool.Ifc.get().by_id(voided_obj.data.BIMMeshProperties.ifc_definition_id)
        blenderbim.core.geometry.switch_representation(
            tool.Geometry,
            obj=voided_obj,
            representation=representation,
            should_reload=True,
            is_global=True,
            should_sync_changes_first=False,
        )

        bpy.ops.bim.add_filling(opening=opening_obj.name, obj=filling_obj.name)

        if not has_visible_openings:
            tool.Ifc.unlink(obj=opening_obj)
            bpy.data.objects.remove(opening_obj)
        return {"FINISHED"}

    def generate_opening_from_filling(self, filling, filling_obj, voided_obj):
        profile = ifcopenshell.util.representation.get_representation(filling, "Model", "Profile", "ELEVATION_VIEW")
        if profile:
            return self.generate_opening_from_filling_profile(filling_obj, voided_obj, profile)
        return self.generate_opening_from_filling_box(filling_obj, voided_obj)

    def generate_opening_from_filling_profile(self, filling_obj, voided_obj, profile):
        settings = ifcopenshell.geom.settings()
        settings.set(settings.INCLUDE_CURVES, True)
        shape = ifcopenshell.geom.create_shape(settings, profile)
        verts = shape.verts
        edges = shape.edges
        grouped_verts = [[verts[i], verts[i + 1], verts[i + 2]] for i in range(0, len(verts), 3)]
        grouped_edges = [[edges[i], edges[i + 1]] for i in range(0, len(edges), 2)]

        bm = bmesh.new()
        bm.verts.index_update()
        bm.edges.index_update()
        new_verts = [bm.verts.new(v) for v in grouped_verts]
        new_edges = [bm.edges.new((new_verts[e[0]], new_verts[e[1]])) for e in grouped_edges]

        bm.verts.index_update()
        bm.edges.index_update()

        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
        bmesh.ops.triangle_fill(bm, edges=bm.edges)
        bmesh.ops.dissolve_limit(bm, angle_limit=pi, verts=bm.verts, edges=bm.edges)

        bmesh.ops.translate(bm, vec=[0., -0.1, 0.], verts=bm.verts)
        extrusion = bmesh.ops.extrude_face_region(bm, geom=bm.faces)
        extruded_verts = [g for g in extrusion["geom"] if isinstance(g, bmesh.types.BMVert)]
        bmesh.ops.translate(bm, vec=[0., voided_obj.dimensions[1] + 0.1 + 0.1, 0.], verts=extruded_verts)

        mesh = bpy.data.meshes.new(name="Opening")
        bm.to_mesh(mesh)
        bm.free()

        obj = bpy.data.objects.new("Opening", mesh)
        obj.matrix_world = filling_obj.matrix_world
        return obj

    def generate_opening_from_filling_box(self, filling_obj, voided_obj):
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
        return obj


class RecalculateFill(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.recalculate_fill"
    bl_label = "Recalculate Fill"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.selected_objects

    def _execute(self, context):
        for obj in context.selected_objects:
            element = tool.Ifc.get_entity(obj)
            if not element or not element.FillsVoids:
                continue
            openings = [r.RelatingOpeningElement for r in element.FillsVoids or []]
            building_elements = []
            for opening in openings:
                building_elements.extend([r.RelatingBuildingElement for r in opening.VoidsElements or []])
            for building_element in building_elements:
                building_obj = tool.Ifc.get_object(building_element)
                if tool.Ifc.is_moved(building_obj):
                    blenderbim.core.geometry.edit_object_placement(tool.Ifc, tool.Geometry, tool.Surveyor, obj=building_obj)
            for opening in openings:
                blenderbim.core.geometry.edit_object_placement(tool.Ifc, tool.Geometry, tool.Surveyor, obj=obj)
                ifcopenshell.api.run(
                    "geometry.edit_object_placement", tool.Ifc.get(), product=opening, matrix=obj.matrix_world
                )
            for building_element in building_elements:
                building_obj = tool.Ifc.get_object(building_element)
                body = ifcopenshell.util.representation.get_representation(
                    building_element, "Model", "Body", "MODEL_VIEW"
                )
                if body:
                    blenderbim.core.geometry.switch_representation(
                        tool.Geometry,
                        obj=building_obj,
                        representation=body,
                        should_reload=True,
                        is_global=True,
                        should_sync_changes_first=False,
                    )
        return {"FINISHED"}


class FlipFill(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.flip_fill"
    bl_label = "Flip Fill"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.selected_objects

    def _execute(self, context):
        for obj in context.selected_objects:
            element = tool.Ifc.get_entity(obj)
            if not element or not element.FillsVoids:
                continue

            flip_matrix = Matrix.Rotation(pi, 4, "Z")

            bottom_left = obj.matrix_world @ Vector(obj.bound_box[0])
            top_right = obj.matrix_world @ Vector(obj.bound_box[6])
            center = obj.matrix_world.col[3].to_3d().copy()
            center_offset = center - bottom_left
            flipped_center = top_right - center_offset

            obj.matrix_world = obj.matrix_world @ flip_matrix
            obj.matrix_world.col[3][0] = flipped_center[0]
            obj.matrix_world.col[3][1] = flipped_center[1]
            bpy.context.view_layer.update()
        return {"FINISHED"}


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
            new_matrix.col[3] = context.scene.cursor.location.to_4d()

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

        if not obj2.data or len(obj2.data.polygons) <= 4: # It takes 4 faces to create a closed solid
            mesh_data = {"type": "IfcHalfSpaceSolid", "matrix": obj1.matrix_world.inverted() @ obj2.matrix_world}
        elif obj2.data:
            mesh_data = {"type": "Mesh", "blender_obj": obj1, "blender_void": obj2}

        ifcopenshell.api.run(
            "geometry.add_boolean",
            tool.Ifc.get(),
            representation=representation,
            operator="DIFFERENCE",
            **mesh_data
        )

        tool.Model.clear_scene_openings()

        blenderbim.core.geometry.switch_representation(
            tool.Geometry,
            obj=obj1,
            representation=representation,
            should_reload=True,
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

        props = bpy.context.scene.BIMModelProperties
        tool.Model.clear_scene_openings()

        for boolean in booleans:
            boolean_obj = None

            if boolean.is_a() == "IfcHalfSpaceSolid":
                if boolean.BaseSurface.is_a("IfcPlane"):
                    boolean_obj = self.create_half_space_solid()
                    position = boolean.BaseSurface.Position
                    position = Matrix(ifcopenshell.util.placement.get_axis2placement(position).tolist())
                    boolean_obj.matrix_world = obj.matrix_world @ position
            else:
                settings = ifcopenshell.geom.settings()
                logger = logging.getLogger("ImportIFC")
                ifc_import_settings = import_ifc.IfcImportSettings.factory(context, IfcStore.path, logger)
                shape = ifcopenshell.geom.create_shape(settings, boolean)
                if shape:
                    ifc_importer = import_ifc.IfcImporter(ifc_import_settings)
                    ifc_importer.file = tool.Ifc.get()
                    mesh = ifc_importer.create_mesh(boolean, shape)
                else:
                    mesh = None
                boolean_obj = object_data_add(bpy.context, mesh, operator=self)
                boolean_obj.name = "BooleanMesh"
                boolean_obj.matrix_world = obj.matrix_world

            if boolean_obj:
                boolean_obj.data.BIMMeshProperties.ifc_boolean_id = boolean.id()
                boolean_obj.data.BIMMeshProperties.obj = obj
                new = props.openings.add()
                new.obj = boolean_obj

        if booleans:
            DecorationsHandler.install(bpy.context)
        return {"FINISHED"}

    def get_booleans(self, item):
        results = []
        if item.is_a("IfcBooleanResult"):
            results.extend(self.get_booleans(item.FirstOperand))
            results.append(item.SecondOperand)
        return results

    def create_half_space_solid(self):
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
        return obj


class HideBooleans(Operator, tool.Ifc.Operator):
    bl_idname = "bim.hide_booleans"
    bl_label = "Hide Booleans"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        props = bpy.context.scene.BIMModelProperties
        for opening in props.openings:
            obj = opening.obj
            if obj and obj.data.BIMMeshProperties.ifc_boolean_id:
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
            if tool.Ifc.is_moved(obj):
                blenderbim.core.geometry.edit_object_placement(tool.Ifc, tool.Geometry, tool.Surveyor, obj=obj)
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
                    if tool.Ifc.is_edited(opening_obj):
                        tool.Geometry.run_geometry_update_representation(obj=opening_obj)
                    elif tool.Ifc.is_moved(opening_obj):
                        blenderbim.core.geometry.edit_object_placement(
                            tool.Ifc, tool.Geometry, tool.Surveyor, obj=opening_obj
                        )
                    tool.Ifc.unlink(element=opening, obj=opening_obj)
                    bpy.data.objects.remove(opening_obj)

            body = ifcopenshell.util.representation.get_representation(element, "Model", "Body", "MODEL_VIEW")
            blenderbim.core.geometry.switch_representation(
                tool.Geometry,
                obj=obj,
                representation=body,
                should_reload=True,
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
