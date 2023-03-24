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
import numpy as np
import ifcopenshell
import ifcopenshell.util.shape_builder
import ifcopenshell.util.representation
import blenderbim.tool as tool
import blenderbim.core.geometry
import blenderbim.bim.import_ifc as import_ifc
import blenderbim.bim.handler
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
        FilledOpeningGenerator().generate(bpy.data.objects.get(self.filling_obj), bpy.data.objects.get(self.voided_obj))
        return {"FINISHED"}


class FilledOpeningGenerator:
    def generate(self, filling_obj, voided_obj, target=None):
        props = bpy.context.scene.BIMModelProperties
        unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())

        filling = tool.Ifc.get_entity(filling_obj)
        element = tool.Ifc.get_entity(voided_obj)

        if not voided_obj or not filling_obj:
            return

        if filling.FillsVoids:
            ifcopenshell.api.run(
                "void.remove_opening", tool.Ifc.get(), opening=filling.FillsVoids[0].RelatingOpeningElement
            )

        if target is None:
            target = bpy.context.scene.cursor.location

        # Sometimes, the voided_obj may be an aggregate, which won't have any representation.
        if voided_obj.data:
            raycast = voided_obj.closest_point_on_mesh(voided_obj.matrix_world.inverted() @ target, distance=0.01)
            if not raycast[0]:
                target = filling_obj.matrix_world.col[3].to_3d().copy()
                raycast = voided_obj.closest_point_on_mesh(voided_obj.matrix_world.inverted() @ target, distance=0.5)
                if not raycast[0]:
                    return

            # In this prototype, we assume openings are only added to axis-based elements
            layers = tool.Model.get_material_layer_parameters(element)
            axis = tool.Model.get_wall_axis(voided_obj, layers=layers)["base"]

            new_matrix = voided_obj.matrix_world.copy()
            new_matrix.col[3] = tool.Cad.point_on_edge(target, axis).to_4d()

            if filling.is_a("IfcDoor"):
                new_matrix[2][3] = voided_obj.matrix_world[2][3]
            else:
                new_matrix[2][3] = voided_obj.matrix_world[2][3] + (props.rl2 * unit_scale)

            filling_obj.matrix_world = new_matrix
            bpy.context.view_layer.update()

        if tool.Ifc.is_moved(voided_obj):
            blenderbim.core.geometry.edit_object_placement(tool.Ifc, tool.Geometry, tool.Surveyor, obj=voided_obj)

        existing_opening_occurrence = self.get_existing_opening_occurrence_if_any(filling)

        if existing_opening_occurrence:
            opening = ifcopenshell.api.run(
                "root.create_entity",
                tool.Ifc.get(),
                ifc_class="IfcOpeningElement",
                predefined_type="OPENING",
                name="Opening",
            )
            ifcopenshell.api.run(
                "geometry.edit_object_placement", tool.Ifc.get(), product=opening, matrix=filling_obj.matrix_world
            )

            representation = ifcopenshell.util.representation.get_representation(
                existing_opening_occurrence, "Model", "Body", "MODEL_VIEW"
            )
            representation = ifcopenshell.util.representation.resolve_representation(representation)
            mapped_representation = ifcopenshell.api.run(
                "geometry.map_representation", tool.Ifc.get(), representation=representation
            )
            ifcopenshell.api.run(
                "geometry.assign_representation", tool.Ifc.get(), product=opening, representation=mapped_representation
            )
        else:
            representation = self.generate_opening_from_filling(filling, filling_obj, voided_obj)
            opening = ifcopenshell.api.run(
                "root.create_entity", tool.Ifc.get(), ifc_class="IfcOpeningElement", predefined_type="OPENING"
            )

            matrix = np.array(filling_obj.matrix_world)
            ifcopenshell.api.run(
                "geometry.edit_object_placement", tool.Ifc.get(), product=opening, matrix=matrix, is_si=True
            )
            mapped_representation = ifcopenshell.api.run(
                "geometry.map_representation", tool.Ifc.get(), representation=representation
            )
            ifcopenshell.api.run(
                "geometry.assign_representation", tool.Ifc.get(), product=opening, representation=mapped_representation
            )

        ifcopenshell.api.run("void.add_opening", tool.Ifc.get(), opening=opening, element=element)
        ifcopenshell.api.run("void.add_filling", tool.Ifc.get(), opening=opening, element=filling)

        voided_objs = [voided_obj]
        # Openings affect all subelements of an aggregate
        for subelement in ifcopenshell.util.element.get_decomposition(element):
            subobj = tool.Ifc.get_object(subelement)
            if subobj:
                voided_objs.append(subobj)

        for voided_obj in voided_objs:
            if voided_obj.data:
                representation = tool.Ifc.get().by_id(voided_obj.data.BIMMeshProperties.ifc_definition_id)
                blenderbim.core.geometry.switch_representation(
                    tool.Ifc,
                    tool.Geometry,
                    obj=voided_obj,
                    representation=representation,
                    should_reload=True,
                    is_global=True,
                    should_sync_changes_first=False,
                )

    def regenerate_from_type(self, usecase_path, ifc_file, settings):
        filling = settings["related_object"]
        if not getattr(filling, "FillsVoids", None):
            return

        opening = filling.FillsVoids[0].RelatingOpeningElement
        voided_obj = tool.Ifc.get_object(opening.VoidsElements[0].RelatingBuildingElement)

        opening_rep = ifcopenshell.util.representation.get_representation(opening, "Model", "Body", "MODEL_VIEW")
        ifcopenshell.api.run(
            "geometry.unassign_representation", tool.Ifc.get(), product=opening, representation=opening_rep
        )
        ifcopenshell.api.run("geometry.remove_representation", tool.Ifc.get(), representation=opening_rep)

        existing_opening_occurrence = self.get_existing_opening_occurrence_if_any(filling)

        if existing_opening_occurrence:
            representation = ifcopenshell.util.representation.get_representation(
                existing_opening_occurrence, "Model", "Body", "MODEL_VIEW"
            )
            representation = ifcopenshell.util.representation.resolve_representation(representation)
            mapped_representation = ifcopenshell.api.run(
                "geometry.map_representation", tool.Ifc.get(), representation=representation
            )
            ifcopenshell.api.run(
                "geometry.assign_representation", tool.Ifc.get(), product=opening, representation=mapped_representation
            )
        else:
            opening_obj = tool.Ifc.get_object(opening)
            if opening_obj:
                tool.Ifc.unlink(obj=opening_obj)
                bpy.data.objects.remove(opening_obj)

            filling_obj = tool.Ifc.get_object(filling)
            representation = self.generate_opening_from_filling(filling, filling_obj, voided_obj)
            mapped_representation = ifcopenshell.api.run(
                "geometry.map_representation", tool.Ifc.get(), representation=representation
            )
            ifcopenshell.api.run(
                "geometry.assign_representation", tool.Ifc.get(), product=opening, representation=mapped_representation
            )

        representation = tool.Ifc.get().by_id(voided_obj.data.BIMMeshProperties.ifc_definition_id)
        blenderbim.core.geometry.switch_representation(
            tool.Ifc,
            tool.Geometry,
            obj=voided_obj,
            representation=representation,
            should_reload=True,
            is_global=True,
            should_sync_changes_first=False,
        )

    def generate_opening_from_filling(self, filling, filling_obj, voided_obj):
        thickness = voided_obj.dimensions[1] + 0.1 + 0.1
        unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
        shape_builder = ifcopenshell.util.shape_builder.ShapeBuilder(tool.Ifc.get())

        profile = None
        filling_type = ifcopenshell.util.element.get_type(filling)
        if filling_type:
            profile = ifcopenshell.util.representation.get_representation(
                filling_type, "Model", "Profile", "ELEVATION_VIEW"
            )
            filling_obj = tool.Ifc.get_object(filling_type)
        context = ifcopenshell.util.representation.get_context(tool.Ifc.get(), "Model", "Body", "MODEL_VIEW")

        if profile:
            extrusion = shape_builder.extrude(
                ifcopenshell.util.representation.resolve_representation(profile).Items[0],
                magnitude=thickness / unit_scale,
                position=Vector([0.0, -0.1 / unit_scale, 0.0]),
                extrusion_vector=Vector([0.0, 1.0, 0.0]),
            )
            return shape_builder.get_representation(context, [extrusion])

        x, y, z = filling_obj.dimensions
        opening_position = Vector([0.0, -0.1 / unit_scale, 0.0])
        opening_size = Vector([x, 0, z]) / unit_scale

        # Windows and doors can have a casing that overlaps the wall
        # but shouldn't affect the size of the opening.
        # So we shouldn't use object dimensions in that case. More: #2784
        # Just keeping it for windows and doors for now to be safe
        x_redefined, z_redefined = False, False
        if filling.is_a() in ["IfcWindow", "IfcDoor"]:
            if filling.OverallWidth:
                opening_size.x = filling.OverallWidth
                x_redefined = True
            if filling.OverallHeight:
                opening_size.z = filling.OverallHeight
                z_redefined = True

        # making sure if min_x or min_z != 0 to shift the opening accordingly
        # to prevent something like #2784
        if not x_redefined:
            opening_position.x = min(v[0] for v in filling_obj.bound_box)

        if not z_redefined:
            opening_position.z = min(v[2] for v in filling_obj.bound_box)

        extrusion = shape_builder.extrude(
            shape_builder.rectangle(size=opening_size),
            magnitude=thickness / unit_scale,
            position=opening_position,
            extrusion_vector=Vector([0.0, 1.0, 0.0]),
        )

        return shape_builder.get_representation(context, [extrusion])

    def has_visible_openings(self, element):
        for opening in [r.RelatedOpeningElement for r in element.HasOpenings]:
            if tool.Ifc.get_object(opening):
                return True
        return False

    def get_existing_opening_occurrence_if_any(self, filling):
        filling_type = ifcopenshell.util.element.get_type(filling)
        if filling_type:
            filling_occurrences = ifcopenshell.util.element.get_types(filling_type)
            for filling_occurrence in filling_occurrences:
                if filling_occurrence != filling and filling_occurrence.FillsVoids:
                    return filling_occurrence.FillsVoids[0].RelatingOpeningElement


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
                    blenderbim.core.geometry.edit_object_placement(
                        tool.Ifc, tool.Geometry, tool.Surveyor, obj=building_obj
                    )
            for opening in openings:
                blenderbim.core.geometry.edit_object_placement(tool.Ifc, tool.Geometry, tool.Surveyor, obj=obj)
                ifcopenshell.api.run(
                    "geometry.edit_object_placement", tool.Ifc.get(), product=opening, matrix=obj.matrix_world
                )

            decomposed_building_elements = set()
            for building_element in building_elements:
                decomposed_building_elements.add(building_element)
                decomposed_building_elements.update(ifcopenshell.util.element.get_decomposition(building_element))

            for building_element in decomposed_building_elements:
                building_obj = tool.Ifc.get_object(building_element)
                if building_obj and building_obj.data:
                    body = ifcopenshell.util.representation.get_representation(
                        building_element, "Model", "Body", "MODEL_VIEW"
                    )
                    if body:
                        blenderbim.core.geometry.switch_representation(
                            tool.Ifc,
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

        if not obj2.data or len(obj2.data.polygons) <= 4:  # It takes 4 faces to create a closed solid
            mesh_data = {"type": "IfcHalfSpaceSolid", "matrix": obj1.matrix_world.inverted() @ obj2.matrix_world}
        elif obj2.data:
            mesh_data = {"type": "Mesh", "blender_obj": obj1, "blender_void": obj2}

        ifcopenshell.api.run(
            "geometry.add_boolean", tool.Ifc.get(), representation=representation, operator="DIFFERENCE", **mesh_data
        )

        tool.Model.clear_scene_openings()

        blenderbim.core.geometry.switch_representation(
            tool.Ifc,
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
        unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
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
                    position[0][3] *= unit_scale
                    position[1][3] *= unit_scale
                    position[2][3] *= unit_scale
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
                        tool.Ifc,
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
            openings = tool.Model.load_openings(
                element,
                [
                    r.RelatedOpeningElement
                    for r in element.HasOpenings
                    if not tool.Ifc.get_object(r.RelatedOpeningElement)
                ],
            )
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
        building_objs = set()
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
                        building_objs.add(obj)
                        building_objs.update(self.get_all_building_objects_of_similar_openings(opening))
                    elif tool.Ifc.is_moved(opening_obj):
                        blenderbim.core.geometry.edit_object_placement(
                            tool.Ifc, tool.Geometry, tool.Surveyor, obj=opening_obj
                        )
                        building_objs.add(obj)
                    tool.Ifc.unlink(element=opening, obj=opening_obj)
                    bpy.data.objects.remove(opening_obj)

        decomposed_building_objs = set()
        for obj in building_objs:
            decomposed_building_objs.add(obj)
            for subelement in ifcopenshell.util.element.get_decomposition(tool.Ifc.get_entity(obj)):
                subobj = tool.Ifc.get_object(subelement)
                if subobj:
                    decomposed_building_objs.add(subobj)

        for obj in decomposed_building_objs:
            if obj.data:
                element = tool.Ifc.get_entity(obj)
                body = ifcopenshell.util.representation.get_representation(element, "Model", "Body", "MODEL_VIEW")
                blenderbim.core.geometry.switch_representation(
                    tool.Ifc,
                    tool.Geometry,
                    obj=obj,
                    representation=body,
                    should_reload=True,
                    is_global=True,
                    should_sync_changes_first=False,
                )
        return {"FINISHED"}

    def get_all_building_objects_of_similar_openings(self, opening):
        if not opening.HasFillings:
            return []
        results = set()
        for rel in opening.HasFillings:
            filling_type = ifcopenshell.util.element.get_type(rel.RelatedBuildingElement)
            if not filling_type:
                continue
            for occurrence in ifcopenshell.util.element.get_types(filling_type):
                for rel2 in occurrence.FillsVoids:
                    for rel3 in rel2.RelatingOpeningElement.VoidsElements:
                        obj = tool.Ifc.get_object(rel3.RelatingBuildingElement)
                        if obj:
                            results.add(obj)
        return results


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
