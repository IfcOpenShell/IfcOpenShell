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
import copy
import math
import bmesh
import ifcopenshell
import ifcopenshell.api
import ifcopenshell.util.unit
import ifcopenshell.util.element
import ifcopenshell.util.representation
import mathutils.geometry
import blenderbim.bim.handler
import blenderbim.core.type
import blenderbim.core.root
import blenderbim.core.geometry
import blenderbim.tool as tool
from blenderbim.bim.ifc import IfcStore
from ifcopenshell.api.pset.data import Data as PsetData
from ifcopenshell.api.material.data import Data as MaterialData
from math import pi, sin, cos, degrees, radians
from mathutils import Vector, Matrix


def element_listener(element, obj):
    blenderbim.bim.handler.subscribe_to(obj, "mode", mode_callback)


def mode_callback(obj, data):
    for obj in set(bpy.context.selected_objects + [bpy.context.active_object]):
        if (
            not obj.data
            or not isinstance(obj.data, (bpy.types.Mesh, bpy.types.Curve, bpy.types.TextCurve))
            or not obj.BIMObjectProperties.ifc_definition_id
            or not bpy.context.scene.BIMProjectProperties.is_authoring
        ):
            return
        product = IfcStore.get_file().by_id(obj.BIMObjectProperties.ifc_definition_id)
        parametric = ifcopenshell.util.element.get_psets(product).get("EPset_Parametric")
        if not parametric or parametric["Engine"] != "BlenderBIM.DumbLayer2":
            return
        if obj.mode == "EDIT":
            IfcStore.edited_objs.add(obj)
            bm = bmesh.from_edit_mesh(obj.data)
            bmesh.ops.dissolve_limit(bm, angle_limit=pi / 180 * 1, verts=bm.verts, edges=bm.edges)
            bmesh.update_edit_mesh(obj.data)
            bm.free()
        else:
            new_origin = obj.matrix_world @ Vector(obj.bound_box[0])
            obj.data.transform(
                Matrix.Translation(
                    (obj.matrix_world.inverted().to_quaternion() @ (obj.matrix_world.translation - new_origin))
                )
            )
            obj.matrix_world.translation = new_origin


class JoinWall(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.join_wall"
    bl_label = "Join Wall"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = """ Trim/Extend the selected walls to the last selected wall:
    'T' mode: Trim/Extend to a selected wall, slab, or 3D target
    'L' mode: Butt join two selected walls
    'V' mode: Mitre join two selected wall
    '' (empty) mode: Unjoin selected walls
    """
    join_type: bpy.props.StringProperty()

    @classmethod
    def poll(cls, context):
        return context.selected_objects

    def _execute(self, context):
        selected_objs = [o for o in context.selected_objects if o.BIMObjectProperties.ifc_definition_id]
        joiner = DumbWallJoiner()
        if not self.join_type:
            for obj in selected_objs:
                joiner.unjoin(obj)
            return {"FINISHED"}
        if not context.active_object:
            return {"FINISHED"}
        if len(selected_objs) == 1:
            joiner.join_E(context.active_object, context.scene.cursor.location)
            return {"FINISHED"}
        if len(selected_objs) == 2:
            if self.join_type == "L":
                joiner.join_L([o for o in selected_objs if o != context.active_object][0], context.active_object)
            elif self.join_type == "V":
                joiner.join_V([o for o in selected_objs if o != context.active_object][0], context.active_object)
        if len(selected_objs) < 2:
            return {"FINISHED"}
        if self.join_type == "T":
            elements = [tool.Ifc.get_entity(o) for o in context.selected_objects]
            targets = [e for e in elements if e and e.is_a() in ("IfcSlab", "IfcSlabStandardCase", "IfcRoof")]
            if targets:
                target = tool.Ifc.get_object(targets[0])
                for element in elements:
                    if element.is_a("IfcWall"):
                        joiner.join_Z(tool.Ifc.get_object(element), target)
            else:
                for obj in selected_objs:
                    if obj == context.active_object:
                        continue
                    joiner.join_T(obj, context.active_object)
        return {"FINISHED"}


class AlignWall(bpy.types.Operator):
    bl_idname = "bim.align_wall"
    bl_label = "Align Wall"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = """ Align the selected walls to the last selected wall:
    'Ext.': align to the EXTERIOR face
    'C/L': align to wall CENTERLINE
    'Int.': align to the INTERIOR face"""
    align_type: bpy.props.StringProperty()

    @classmethod
    def poll(cls, context):
        selected_valid_objects = [o for o in context.selected_objects if o.data and hasattr(o.data, "transform")]
        return context.active_object and len(selected_valid_objects) > 1

    def execute(self, context):
        selected_objects = [o for o in context.selected_objects if o.data and hasattr(o.data, "transform")]
        for obj in selected_objects:
            if obj == context.active_object:
                continue
            aligner = DumbWallAligner(obj, context.active_object)
            if self.align_type == "CENTERLINE":
                aligner.align_centerline()
            elif self.align_type == "EXTERIOR":
                aligner.align_first_layer()
            elif self.align_type == "INTERIOR":
                aligner.align_last_layer()
            IfcStore.edited_objs.add(obj)
        return {"FINISHED"}


class FlipWall(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.flip_wall"
    bl_label = "Flip Wall"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Switch the origin from the min XY corner to the max XY corner, and rotates the origin by 180"

    @classmethod
    def poll(cls, context):
        return context.selected_objects

    def _execute(self, context):
        selected_objs = [o for o in context.selected_objects if o.data and hasattr(o.data, "transform")]
        joiner = DumbWallJoiner()
        for obj in selected_objs:
            joiner.flip(obj)
        return {"FINISHED"}


class SplitWall(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.split_wall"
    bl_label = "Split Wall"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = (
        "Split selected wall into two walls in correspondence of Blender cursor. The cursor must be in the wall volume"
    )

    @classmethod
    def poll(cls, context):
        return context.selected_objects

    def _execute(self, context):
        selected_objs = [o for o in context.selected_objects if o.data and hasattr(o.data, "transform")]
        for obj in selected_objs:
            DumbWallJoiner().split(obj, context.scene.cursor.location)
        return {"FINISHED"}


class MergeWall(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.merge_wall"
    bl_label = "Merge Wall"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.selected_objects

    def _execute(self, context):
        selected_objs = [o for o in context.selected_objects if o.data and hasattr(o.data, "transform")]
        if len(selected_objs) == 2:
            DumbWallJoiner().merge([o for o in selected_objs if o != context.active_object][0], context.active_object)
        return {"FINISHED"}


class RecalculateWall(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.recalculate_wall"
    bl_label = "Recalculate Wall"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.selected_objects

    def _execute(self, context):
        DumbWallRecalculator().recalculate(context.selected_objects)
        return {"FINISHED"}


class ChangeExtrusionDepth(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.change_extrusion_depth"
    bl_label = "Change Extrusion Depth"
    bl_options = {"REGISTER", "UNDO"}
    depth: bpy.props.FloatProperty()

    @classmethod
    def poll(cls, context):
        return context.selected_objects

    def _execute(self, context):
        wall_objs = []
        for obj in context.selected_objects:
            element = tool.Ifc.get_entity(obj)
            if not element:
                return
            representation = ifcopenshell.util.representation.get_representation(element, "Model", "Body", "MODEL_VIEW")
            if not representation:
                return
            extrusion = tool.Model.get_extrusion(representation)
            if not extrusion:
                return
            x, y, z = extrusion.ExtrudedDirection.DirectionRatios
            x_angle = Vector((0, 1)).angle_signed(Vector((y, z)))
            extrusion.Depth = self.depth * (1 / cos(x_angle))
            if element.is_a("IfcWall"):
                for rel in element.ConnectedFrom:
                    if rel.is_a() == "IfcRelConnectsElements":
                        ifcopenshell.api.run(
                            "geometry.disconnect_element",
                            tool.Ifc.get(),
                            relating_element=rel.RelatingElement,
                            related_element=element,
                        )
                wall_objs.append(obj)
        if wall_objs:
            DumbWallRecalculator().recalculate(wall_objs)
        return {"FINISHED"}


class ChangeExtrusionXAngle(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.change_extrusion_x_angle"
    bl_label = "Change Extrusion X Angle"
    bl_options = {"REGISTER", "UNDO"}
    x_angle: bpy.props.FloatProperty()

    @classmethod
    def poll(cls, context):
        return context.selected_objects

    def _execute(self, context):
        wall_objs = []
        other_objs = []
        x_angle = radians(self.x_angle)
        unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
        for obj in context.selected_objects:
            element = tool.Ifc.get_entity(obj)
            if not element:
                return
            representation = ifcopenshell.util.representation.get_representation(element, "Model", "Body", "MODEL_VIEW")
            if not representation:
                return
            extrusion = tool.Model.get_extrusion(representation)
            if not extrusion:
                return
            x, y, z = extrusion.ExtrudedDirection.DirectionRatios
            existing_x_angle = Vector((0, 1)).angle_signed(Vector((y, z)))
            perpendicular_depth = extrusion.Depth / (1 / cos(existing_x_angle))
            extrusion.Depth = perpendicular_depth * (1 / cos(x_angle))
            extrusion.ExtrudedDirection.DirectionRatios = (0.0, sin(x_angle), cos(x_angle))
            if element.is_a("IfcWall"):
                wall_objs.append(obj)
            else:
                blenderbim.core.geometry.switch_representation(
                    tool.Geometry,
                    obj=obj,
                    representation=representation,
                    should_reload=True,
                    is_global=True,
                    should_sync_changes_first=False,
                )

                euler = obj.matrix_world.to_euler()
                euler.x = x_angle
                new_matrix = euler.to_matrix().to_4x4()
                new_matrix.col[3] = obj.matrix_world.col[3]
                obj.matrix_world = new_matrix
        if wall_objs:
            DumbWallRecalculator().recalculate(wall_objs)
        return {"FINISHED"}


class ChangeLayerLength(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.change_layer_length"
    bl_label = "Change Layer Length"
    bl_options = {"REGISTER", "UNDO"}
    length: bpy.props.FloatProperty()

    @classmethod
    def poll(cls, context):
        return context.selected_objects

    def _execute(self, context):
        joiner = DumbWallJoiner()
        for obj in context.selected_objects:
            joiner.set_length(obj, self.length)
        return {"FINISHED"}


def recalculate_dumb_wall_origin(wall, new_origin=None):
    if new_origin is None:
        new_origin = wall.matrix_world @ Vector(wall.bound_box[0])
    if (wall.matrix_world.translation - new_origin).length < 0.001:
        return
    wall.data.transform(
        Matrix.Translation(
            (wall.matrix_world.inverted().to_quaternion() @ (wall.matrix_world.translation - new_origin))
        )
    )
    wall.matrix_world.translation = new_origin
    for child in wall.children:
        child.matrix_parent_inverse = wall.matrix_world.inverted()


class DumbWallFlipper:
    def __init__(self, wall):
        self.wall = wall

    def flip(self):
        if (
            self.wall.matrix_world.translation - self.wall.matrix_world @ Vector(self.wall.bound_box[0])
        ).length < 0.001:
            recalculate_dumb_wall_origin(self.wall, self.wall.matrix_world @ Vector(self.wall.bound_box[7]))
            self.rotate_wall_180()
            bpy.context.view_layer.update()
            for child in self.wall.children:
                child.matrix_parent_inverse = self.wall.matrix_world.inverted()
        else:
            recalculate_dumb_wall_origin(self.wall)

    def rotate_wall_180(self):
        flip_matrix = Matrix.Rotation(pi, 4, "Z")
        self.wall.data.transform(flip_matrix)
        self.wall.rotation_euler.rotate(flip_matrix)


class DumbWallAligner:
    # An alignment shifts the origin of all walls to the closest point on the
    # local X axis of the reference wall. In addition, the Z rotation is copied.
    # Z translations are ignored for alignment.
    def __init__(self, wall, reference_wall):
        self.wall = wall
        self.reference_wall = reference_wall

    def align_centerline(self):
        recalculate_dumb_wall_origin(self.wall)
        recalculate_dumb_wall_origin(self.reference_wall)
        self.align_rotation()

        width = (Vector(self.wall.bound_box[3]) - Vector(self.wall.bound_box[0])).y
        reference_width = (Vector(self.reference_wall.bound_box[3]) - Vector(self.reference_wall.bound_box[0])).y

        if self.is_rotation_flipped():
            offset = self.wall.matrix_world.to_quaternion() @ Vector((0, -(reference_width / 2) - (width / 2), 0))
        else:
            offset = self.wall.matrix_world.to_quaternion() @ Vector((0, (reference_width / 2) - (width / 2), 0))

        self.align(
            self.reference_wall.matrix_world @ Vector(self.reference_wall.bound_box[0]),
            self.reference_wall.matrix_world @ Vector(self.reference_wall.bound_box[4]),
            offset,
        )

    def align_last_layer(self):
        recalculate_dumb_wall_origin(self.wall)
        recalculate_dumb_wall_origin(self.reference_wall)
        self.align_rotation()

        if self.is_rotation_flipped():
            DumbWallFlipper(self.wall).flip()
            bpy.context.view_layer.update()
        start = self.reference_wall.matrix_world @ Vector(self.reference_wall.bound_box[3])
        end = self.reference_wall.matrix_world @ Vector(self.reference_wall.bound_box[7])

        wall_width = (Vector(self.wall.bound_box[3]) - Vector(self.wall.bound_box[0])).y

        offset = self.wall.matrix_world.to_quaternion() @ Vector((0, -wall_width, 0))
        self.align(start, end, offset)

    def align_first_layer(self):
        recalculate_dumb_wall_origin(self.wall)
        recalculate_dumb_wall_origin(self.reference_wall)
        self.align_rotation()

        if self.is_rotation_flipped():
            DumbWallFlipper(self.wall).flip()
            bpy.context.view_layer.update()

        start = self.reference_wall.matrix_world @ Vector(self.reference_wall.bound_box[0])
        end = self.reference_wall.matrix_world @ Vector(self.reference_wall.bound_box[4])

        self.align(start, end)

    def align(self, start, end, offset=None):
        if offset is None:
            offset = Vector((0, 0, 0))
        point, distance = mathutils.geometry.intersect_point_line(self.wall.matrix_world.translation, start, end)
        new_origin = point + offset
        self.wall.matrix_world.translation[0] = new_origin[0]
        self.wall.matrix_world.translation[1] = new_origin[1]

    def align_rotation(self):
        reference = (self.reference_wall.matrix_world.to_quaternion() @ Vector((1, 0, 0))).to_2d()
        wall = (self.wall.matrix_world.to_quaternion() @ Vector((1, 0, 0))).to_2d()
        angle = reference.angle_signed(wall)
        if round(degrees(angle) % 360) in (0, 180):
            return
        elif angle > (pi / 2):
            self.wall.rotation_euler[2] -= pi - angle
        else:
            self.wall.rotation_euler[2] += angle
        bpy.context.view_layer.update()

    def is_rotation_flipped(self):
        reference = (self.reference_wall.matrix_world.to_quaternion() @ Vector((1, 0, 0))).to_2d()
        wall = (self.wall.matrix_world.to_quaternion() @ Vector((1, 0, 0))).to_2d()
        angle = reference.angle_signed(wall)
        return round(degrees(angle) % 360) == 180


class DumbWallRecalculator:
    def recalculate(self, walls):
        queue = set()
        for wall in walls:
            element = tool.Ifc.get_entity(wall)
            queue.add((element, wall))
            for rel in getattr(element, "ConnectedTo", []):
                queue.add((rel.RelatedElement, tool.Ifc.get_object(rel.RelatedElement)))
            for rel in getattr(element, "ConnectedFrom", []):
                queue.add((rel.RelatingElement, tool.Ifc.get_object(rel.RelatingElement)))
        joiner = DumbWallJoiner()
        for element, wall in queue:
            if element.is_a("IfcWall") and wall:
                joiner.recreate_wall(element, wall)


class DumbWallGenerator:
    def __init__(self, relating_type):
        self.relating_type = relating_type
        self.unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())

    def generate(self, link_to_scene=True):
        self.file = IfcStore.get_file()
        self.layers = tool.Model.get_material_layer_parameters(self.relating_type)
        if not self.layers["thickness"]:
            return

        self.body_context = ifcopenshell.util.representation.get_context(tool.Ifc.get(), "Model", "Body", "MODEL_VIEW")
        self.axis_context = ifcopenshell.util.representation.get_context(tool.Ifc.get(), "Plan", "Axis", "GRAPH_VIEW")

        props = bpy.context.scene.BIMModelProperties
        self.collection = bpy.context.view_layer.active_layer_collection.collection
        self.collection_obj = bpy.data.objects.get(self.collection.name)
        self.width = self.layers["thickness"]
        self.height = props.extrusion_depth * self.unit_scale
        self.length = props.length * self.unit_scale
        self.rotation = 0.0
        self.location = Vector((0, 0, 0))
        self.x_angle = 0 if tool.Cad.is_x(props.x_angle, 0, tolerance=0.001) else radians(props.x_angle)

        if self.has_sketch():
            return  # For now
            return self.derive_from_sketch()
        return self.derive_from_cursor(link_to_scene)

    def has_sketch(self):
        return (
            bpy.context.scene.grease_pencil
            and len(bpy.context.scene.grease_pencil.layers) == 1
            and bpy.context.scene.grease_pencil.layers[0].active_frame.strokes
        )

    def derive_from_sketch(self):
        objs = []
        strokes = []
        layer = bpy.context.scene.grease_pencil.layers[0]

        for stroke in layer.active_frame.strokes:
            if len(stroke.points) == 1:
                continue
            data = self.create_wall_from_2_points((stroke.points[0].co, stroke.points[-1].co))
            if data:
                strokes.append(data)
                objs.append(data["obj"])

        if len(objs) < 2:
            return objs

        l_joins = set()
        for stroke in strokes:
            if not stroke["obj"]:
                continue
            for stroke2 in strokes:
                if stroke2 == stroke or not stroke2["obj"]:
                    continue
                if self.has_nearby_ends(stroke, stroke2):
                    wall_join = "-JOIN-".join(sorted([stroke["obj"].name, stroke2["obj"].name]))
                    if wall_join not in l_joins:
                        l_joins.add(wall_join)
                        DumbWallJoiner(stroke["obj"], stroke2["obj"]).join_L()
                elif self.has_end_near_stroke(stroke, stroke2):
                    DumbWallJoiner(stroke["obj"], stroke2["obj"]).join_T()
        bpy.context.scene.grease_pencil.layers.remove(layer)
        return objs

    def create_wall_from_2_points(self, coords):
        direction = coords[1] - coords[0]
        length = direction.length
        if length < 0.1:
            return
        data = {"coords": coords}

        # Round to nearest 50mm (yes, metric for now)
        self.length = 0.05 * round(length / 0.05)
        self.rotation = math.atan2(direction[1], direction[0])
        # Round to nearest 5 degrees
        nearest_degree = (math.pi / 180) * 5
        self.rotation = nearest_degree * round(self.rotation / nearest_degree)
        self.location = coords[0]
        data["obj"] = self.create_wall()
        return data

    def has_end_near_stroke(self, stroke, stroke2):
        point, distance = mathutils.geometry.intersect_point_line(stroke["coords"][0], *stroke2["coords"])
        if distance > 0 and distance < 1 and self.is_near(point, stroke["coords"][0]):
            return True
        point, distance = mathutils.geometry.intersect_point_line(stroke["coords"][1], *stroke2["coords"])
        if distance > 0 and distance < 1 and self.is_near(point, stroke["coords"][1]):
            return True

    def has_nearby_ends(self, stroke, stroke2):
        return (
            self.is_near(stroke["coords"][0], stroke2["coords"][0])
            or self.is_near(stroke["coords"][0], stroke2["coords"][1])
            or self.is_near(stroke["coords"][1], stroke2["coords"][0])
            or self.is_near(stroke["coords"][1], stroke2["coords"][1])
        )

    def is_near(self, point1, point2):
        return (point1 - point2).length < 0.1

    def derive_from_cursor(self, link_to_scene):
        self.location = bpy.context.scene.cursor.location
        if self.collection:
            for sibling_obj in self.collection.objects:
                if not isinstance(sibling_obj.data, bpy.types.Mesh):
                    continue
                if "IfcWall" not in sibling_obj.name:
                    continue
                local_location = sibling_obj.matrix_world.inverted() @ self.location
                try:
                    raycast = sibling_obj.closest_point_on_mesh(local_location, distance=0.01)
                except:
                    # If the mesh has no faces
                    raycast = [None]
                if not raycast[0]:
                    continue
                for face in sibling_obj.data.polygons:
                    if (
                        abs(face.normal.y) >= 0.75
                        and abs(mathutils.geometry.distance_point_to_plane(local_location, face.center, face.normal))
                        < 0.01
                    ):
                        # Rotate the wall in the direction of the face normal
                        normal = (sibling_obj.matrix_world.to_quaternion() @ face.normal).normalized()
                        self.rotation = math.atan2(normal[1], normal[0])
                        break
        return self.create_wall(link_to_scene)

    def create_wall(self, link_to_scene):
        props = bpy.context.scene.BIMModelProperties
        ifc_class = self.get_relating_type_class(self.relating_type)
        mesh = bpy.data.meshes.new("Dummy")
        obj = bpy.data.objects.new(tool.Model.generate_occurrence_name(self.relating_type, ifc_class), mesh)
        if link_to_scene:
            matrix_world = Matrix.Rotation(self.rotation, 4, "Z")
            matrix_world.col[3] = self.location.to_4d()
            if self.collection_obj and self.collection_obj.BIMObjectProperties.ifc_definition_id:
                matrix_world[2][3] = self.collection_obj.location[2] + (props.rl1 * self.unit_scale)
            obj.matrix_world = matrix_world
            bpy.context.view_layer.update()
            self.collection.objects.link(obj)

        element = blenderbim.core.root.assign_class(
            tool.Ifc,
            tool.Collector,
            tool.Root,
            obj=obj,
            ifc_class=ifc_class,
            should_add_representation=False,
            context=self.body_context,
        )
        ifcopenshell.api.run("type.assign_type", self.file, related_object=element, relating_type=self.relating_type)
        if self.axis_context:
            representation = ifcopenshell.api.run(
                "geometry.add_axis_representation",
                tool.Ifc.get(),
                context=self.axis_context,
                axis=[(0.0, 0.0), (self.length, 0.0)],
            )
            ifcopenshell.api.run(
                "geometry.assign_representation", tool.Ifc.get(), product=element, representation=representation
            )
        blenderbim.core.geometry.edit_object_placement(tool.Ifc, tool.Geometry, tool.Surveyor, obj=obj)
        representation = ifcopenshell.api.run(
            "geometry.add_wall_representation",
            tool.Ifc.get(),
            context=self.body_context,
            thickness=self.layers["thickness"],
            offset=self.layers["offset"],
            length=self.length,
            height=self.height,
            x_angle=self.x_angle,
        )
        ifcopenshell.api.run(
            "geometry.assign_representation", tool.Ifc.get(), product=element, representation=representation
        )
        blenderbim.core.geometry.switch_representation(
            tool.Geometry,
            obj=obj,
            representation=representation,
            should_reload=True,
            is_global=True,
            should_sync_changes_first=False,
        )
        pset = ifcopenshell.api.run("pset.add_pset", self.file, product=element, name="EPset_Parametric")
        ifcopenshell.api.run("pset.edit_pset", self.file, pset=pset, properties={"Engine": "BlenderBIM.DumbLayer2"})
        MaterialData.load(self.file)
        obj.select_set(True)
        return obj

    def get_relating_type_class(self, relating_type):
        classes = ifcopenshell.util.type.get_applicable_entities(relating_type.is_a(), tool.Ifc.get().schema)
        return [c for c in classes if "StandardCase" not in c][0]


def calculate_quantities(usecase_path, ifc_file, settings):
    unit_scale = ifcopenshell.util.unit.calculate_unit_scale(ifc_file)
    obj = settings["blender_object"]
    product = ifc_file.by_id(obj.BIMObjectProperties.ifc_definition_id)
    parametric = ifcopenshell.util.element.get_psets(product).get("EPset_Parametric")
    if not parametric or "Engine" not in parametric or parametric["Engine"] != "BlenderBIM.DumbLayer2":
        return
    qto = ifcopenshell.api.run(
        "pset.add_qto", ifc_file, should_run_listeners=False, product=product, name="Qto_WallBaseQuantities"
    )
    length = obj.dimensions[0] / unit_scale
    width = obj.dimensions[1] / unit_scale
    height = obj.dimensions[2] / unit_scale

    bm_gross = bmesh.new()
    bm_gross.from_mesh(obj.data)
    bm_gross.faces.ensure_lookup_table()

    bm_net = bmesh.new()
    depsgraph = bpy.context.evaluated_depsgraph_get()
    evaluated_mesh = obj.evaluated_get(depsgraph).data
    bm_net.from_mesh(evaluated_mesh)
    bm_net.faces.ensure_lookup_table()

    gross_footprint_area = sum([f.calc_area() for f in bm_gross.faces if f.normal.z < -0.9])
    net_footprint_area = sum([f.calc_area() for f in bm_net.faces if f.normal.z < -0.9])
    gross_side_area = sum([f.calc_area() for f in bm_gross.faces if f.normal.y > 0.9])
    net_side_area = sum([f.calc_area() for f in bm_net.faces if f.normal.y > 0.9])
    gross_volume = bm_gross.calc_volume()
    net_volume = bm_net.calc_volume()
    bm_gross.free()
    bm_net.free()

    ifcopenshell.api.run(
        "pset.edit_qto",
        ifc_file,
        should_run_listeners=False,
        qto=qto,
        properties={
            "Length": round(length, 2),
            "Width": round(width, 2),
            "Height": round(height, 2),
            "GrossFootprintArea": round(gross_footprint_area, 2),
            "NetFootprintArea": round(net_footprint_area, 2),
            "GrossSideArea": round(gross_side_area, 2),
            "NetSideArea": round(net_side_area, 2),
            "GrossVolume": round(gross_volume, 2),
            "NetVolume": round(net_volume, 2),
        },
    )
    PsetData.load(ifc_file, obj.BIMObjectProperties.ifc_definition_id)


class DumbWallPlaner:
    def regenerate_from_layer(self, usecase_path, ifc_file, settings):
        if settings["attributes"].get("LayerThickness") is None:
            return
        walls = []
        layer = settings["layer"]
        for layer_set in layer.ToMaterialLayerSet:
            total_thickness = sum([l.LayerThickness for l in layer_set.MaterialLayers])
            if not total_thickness:
                continue
            for inverse in ifc_file.get_inverse(layer_set):
                if not inverse.is_a("IfcMaterialLayerSetUsage") or inverse.LayerSetDirection != "AXIS2":
                    continue
                if ifc_file.schema == "IFC2X3":
                    for rel in ifc_file.get_inverse(inverse):
                        if not rel.is_a("IfcRelAssociatesMaterial"):
                            continue
                        walls.extend([tool.Ifc.get_object(e) for e in rel.RelatedObjects])
                else:
                    for rel in inverse.AssociatedTo:
                        walls.extend([tool.Ifc.get_object(e) for e in rel.RelatedObjects])
        DumbWallRecalculator().recalculate([w for w in set(walls) if w])

    def regenerate_from_type(self, usecase_path, ifc_file, settings):
        obj = tool.Ifc.get_object(settings["related_object"])
        if not obj or not obj.data or not obj.data.BIMMeshProperties.ifc_definition_id:
            return
        self.unit_scale = ifcopenshell.util.unit.calculate_unit_scale(ifc_file)
        new_material = ifcopenshell.util.element.get_material(settings["relating_type"])
        if not new_material or not new_material.is_a("IfcMaterialLayerSet"):
            return
        material = ifcopenshell.util.element.get_material(settings["related_object"])
        if material and material.is_a("IfcMaterialLayerSetUsage") and material.LayerSetDirection == "AXIS2":
            DumbWallRecalculator().recalculate([obj])


class DumbWallJoiner:
    def __init__(self):
        self.unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
        self.axis_context = ifcopenshell.util.representation.get_context(tool.Ifc.get(), "Plan", "Axis", "GRAPH_VIEW")
        self.body_context = ifcopenshell.util.representation.get_context(tool.Ifc.get(), "Model", "Body", "MODEL_VIEW")

    def unjoin(self, wall1):
        element1 = tool.Ifc.get_entity(wall1)
        if not element1:
            return

        ifcopenshell.api.run("geometry.disconnect_path", tool.Ifc.get(), element=element1, connection_type="ATSTART")
        ifcopenshell.api.run("geometry.disconnect_path", tool.Ifc.get(), element=element1, connection_type="ATEND")

        axis1 = tool.Model.get_wall_axis(wall1)
        axis = copy.deepcopy(axis1["reference"])
        body = copy.deepcopy(axis1["reference"])
        self.recreate_wall(element1, wall1, axis, body)

    def split(self, wall1, target):
        element1 = tool.Ifc.get_entity(wall1)
        if not element1:
            return
        axis1 = tool.Model.get_wall_axis(wall1)
        axis2 = copy.deepcopy(axis1)
        intersect, connection = mathutils.geometry.intersect_point_line(target.to_2d(), *axis1["reference"])
        if connection < 0 or connection > 1 or tool.Cad.is_x(connection, (0, 1)):
            return
        connection = "ATEND" if connection > 0.5 else "ATSTART"

        wall2 = self.duplicate_wall(wall1)
        MaterialData.load(tool.Ifc.get())
        element2 = tool.Ifc.get_entity(wall2)

        ifcopenshell.api.run("geometry.disconnect_path", tool.Ifc.get(), element=element1, connection_type="ATEND")
        ifcopenshell.api.run("geometry.disconnect_path", tool.Ifc.get(), element=element2, connection_type="ATSTART")

        axis1["reference"][1] = intersect
        axis2["reference"][0] = intersect
        self.recreate_wall(element1, wall1, axis1["reference"], axis1["reference"])
        self.recreate_wall(element2, wall2, axis2["reference"], axis2["reference"])

    def flip(self, wall1):
        if tool.Ifc.is_moved(wall1):
            blenderbim.core.geometry.edit_object_placement(tool.Ifc, tool.Geometry, tool.Surveyor, obj=wall1)

        element1 = tool.Ifc.get_entity(wall1)
        if not element1:
            return

        for rel in element1.ConnectedTo:
            if rel.RelatingConnectionType in ["ATSTART", "ATEND"]:
                rel.RelatingConnectionType = "ATSTART" if rel.RelatingConnectionType == "ATEND" else "ATEND"
        for rel in element1.ConnectedFrom:
            if rel.RelatedConnectionType in ["ATSTART", "ATEND"]:
                rel.RelatedConnectionType = "ATSTART" if rel.RelatedConnectionType == "ATEND" else "ATEND"

        layers1 = tool.Model.get_material_layer_parameters(element1)
        axis1 = tool.Model.get_wall_axis(wall1, layers1)
        axis1["reference"][0], axis1["reference"][1] = axis1["reference"][1], axis1["reference"][0]

        flip_matrix = Matrix.Rotation(pi, 4, "Z")
        wall1.matrix_world = wall1.matrix_world @ flip_matrix
        wall1.matrix_world[0][3], wall1.matrix_world[1][3] = axis1["reference"][0]
        bpy.context.view_layer.update()

        # The wall should flip, but all openings and fills should stay and shift to the opposite axis
        opening_matrixes = {}
        filling_matrixes = {}
        for opening in [r.RelatedOpeningElement for r in element1.HasOpenings]:
            opening_matrix = Matrix(ifcopenshell.util.placement.get_local_placement(opening.ObjectPlacement).tolist())
            location = opening_matrix.col[3].to_3d()
            location_on_base = tool.Cad.point_on_edge(location, axis1["base"])
            location_on_side = tool.Cad.point_on_edge(location, axis1["side"])
            if (location_on_base - location).length < (location_on_side - location).length:
                axis_offset = location_on_side - location_on_base
                offset_from_axis = location_on_base - location
                opening_matrix.col[3] = (location_on_base - axis_offset - offset_from_axis).to_4d()
            else:
                axis_offset = location_on_side - location_on_base
                offset_from_axis = location_on_side - location
                opening_matrix.col[3] = (location_on_side - axis_offset - offset_from_axis).to_4d()
            opening_matrixes[opening] = opening_matrix

            for filling in [r.RelatedBuildingElement for r in opening.HasFillings]:
                filling_obj = tool.Ifc.get_object(filling)
                filling_matrix = filling_obj.matrix_world.copy()

                location = filling_matrix.col[3].to_3d()
                location_on_base = tool.Cad.point_on_edge(location, axis1["base"])
                location_on_side = tool.Cad.point_on_edge(location, axis1["side"])
                if (location_on_base - location).length < (location_on_side - location).length:
                    axis_offset = location_on_side - location_on_base
                    offset_from_axis = location_on_base - location
                    filling_matrix.col[3] = (location_on_base - axis_offset - offset_from_axis).to_4d()
                else:
                    axis_offset = location_on_side - location_on_base
                    offset_from_axis = location_on_side - location
                    filling_matrix.col[3] = (location_on_side - axis_offset - offset_from_axis).to_4d()
                filling_matrixes[filling] = filling_matrix

        self.recreate_wall(element1, wall1, axis1["reference"], axis1["reference"])
        DumbWallRecalculator().recalculate([wall1])

        for opening in [r.RelatedOpeningElement for r in element1.HasOpenings]:
            opening_matrix = opening_matrixes[opening]
            ifcopenshell.api.run(
                "geometry.edit_object_placement", tool.Ifc.get(), product=opening, matrix=opening_matrix
            )
            for filling in [r.RelatedBuildingElement for r in opening.HasFillings]:
                filling_matrix = filling_matrixes[filling]
                filling_obj = tool.Ifc.get_object(filling)
                filling_obj.matrix_world = filling_matrix

        if filling_matrixes:
            bpy.context.view_layer.update()

        body = ifcopenshell.util.representation.get_representation(element1, "Model", "Body", "MODEL_VIEW")
        blenderbim.core.geometry.switch_representation(
            tool.Geometry,
            obj=wall1,
            representation=body,
            should_reload=True,
            is_global=True,
            should_sync_changes_first=False,
        )

    def merge(self, wall1, wall2):
        element1 = tool.Ifc.get_entity(wall1)
        element2 = tool.Ifc.get_entity(wall2)
        axis1 = tool.Model.get_wall_axis(wall1)
        axis2 = tool.Model.get_wall_axis(wall2)

        angle = tool.Cad.angle_edges(axis1["reference"], axis2["reference"], signed=False, degrees=True)
        if not tool.Cad.is_x(angle, 0, tolerance=0.001):
            return

        intersect1, connection1 = mathutils.geometry.intersect_point_line(axis2["reference"][0], *axis1["reference"])
        if not tool.Cad.is_x((intersect1 - axis2["reference"][0]).length, 0):
            return

        intersect2, connection2 = mathutils.geometry.intersect_point_line(axis2["reference"][1], *axis1["reference"])
        if not tool.Cad.is_x((intersect2 - axis2["reference"][1]).length, 0):
            return

        changed_connections = set()

        if connection1 < 0:
            changed_connections.add("ATSTART")
            axis1["reference"][0] = intersect2 if connection2 < connection1 else intersect1
        elif connection1 > 1:
            changed_connections.add("ATEND")
            axis1["reference"][1] = intersect2 if connection2 > connection1 else intersect1

        for connection in changed_connections:
            ifcopenshell.api.run(
                "geometry.disconnect_path", tool.Ifc.get(), element=element1, connection_type=connection
            )

        for rel in element2.ConnectedTo:
            if rel.RelatingConnectionType in changed_connections:
                other = tool.Ifc.get_object(rel.RelatedElement)
                ifcopenshell.api.run(
                    "geometry.connect_path",
                    tool.Ifc.get(),
                    relating_element=element1,
                    related_element=rel.RelatedElement,
                    relating_connection=rel.RelatingConnectionType,
                    related_connection=rel.RelatedConnectionType,
                )

        for rel in element2.ConnectedFrom:
            if rel.RelatedConnectionType in changed_connections:
                ifcopenshell.api.run(
                    "geometry.connect_path",
                    tool.Ifc.get(),
                    relating_element=rel.RelatingElement,
                    related_element=element1,
                    relating_connection=rel.RelatingConnectionType,
                    related_connection=rel.RelatedConnectionType,
                )

        self.recreate_wall(element1, wall1, axis1["reference"], axis1["reference"])
        bpy.data.objects.remove(wall2)

    def duplicate_wall(self, wall1):
        wall2 = wall1.copy()
        wall2.data = wall2.data.copy()
        wall1.users_collection[0].objects.link(wall2)
        blenderbim.core.root.copy_class(tool.Ifc, tool.Collector, tool.Geometry, tool.Root, obj=wall2)
        return wall2

    def join_Z(self, wall1, slab2):
        element1 = tool.Ifc.get_entity(wall1)
        element2 = tool.Ifc.get_entity(slab2)

        ifcopenshell.api.run(
            "geometry.connect_element",
            tool.Ifc.get(),
            relating_element=element2,
            related_element=element1,
            description="TOP",
        )

        self.recreate_wall(element1, wall1)

    def join_L(self, wall1, wall2):
        element1 = tool.Ifc.get_entity(wall1)
        element2 = tool.Ifc.get_entity(wall2)
        axis1 = tool.Model.get_wall_axis(wall1)
        axis2 = tool.Model.get_wall_axis(wall2)
        intersect = tool.Cad.intersect_edges(axis1["reference"], axis2["reference"])
        if intersect:
            intersect, _ = intersect
        else:
            return
        wall1_end = "ATEND" if tool.Cad.edge_percent(intersect, axis1["reference"]) > 0.5 else "ATSTART"
        wall2_end = "ATEND" if tool.Cad.edge_percent(intersect, axis2["reference"]) > 0.5 else "ATSTART"

        ifcopenshell.api.run(
            "geometry.connect_path",
            tool.Ifc.get(),
            relating_element=element1,
            related_element=element2,
            relating_connection=wall1_end,
            related_connection=wall2_end,
            description="BUTT",
        )

        self.recreate_wall(element1, wall1, axis1["reference"], axis1["reference"])
        self.recreate_wall(element2, wall2, axis2["reference"], axis2["reference"])

    def join_E(self, wall1, target):
        element1 = tool.Ifc.get_entity(wall1)
        if not element1:
            return

        axis1 = tool.Model.get_wall_axis(wall1)
        intersect, connection = mathutils.geometry.intersect_point_line(target.to_2d(), *axis1["reference"])
        connection = "ATEND" if connection > 0.5 else "ATSTART"

        ifcopenshell.api.run("geometry.disconnect_path", tool.Ifc.get(), element=element1, connection_type=connection)

        axis = copy.deepcopy(axis1["reference"])
        body = copy.deepcopy(axis1["reference"])
        axis[1 if connection == "ATEND" else 0] = intersect
        body[1 if connection == "ATEND" else 0] = intersect

        self.recreate_wall(element1, wall1, axis, body)

    def set_length(self, wall1, length):
        element1 = tool.Ifc.get_entity(wall1)
        if not element1:
            return

        ifcopenshell.api.run("geometry.disconnect_path", tool.Ifc.get(), element=element1, connection_type="ATEND")

        axis1 = tool.Model.get_wall_axis(wall1)
        axis = copy.deepcopy(axis1["reference"])
        body = copy.deepcopy(axis1["reference"])
        unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
        si_length = unit_scale * length
        end = (wall1.matrix_world @ Vector((si_length, 0, 0))).to_2d()
        axis[1] = end
        body[1] = end
        self.recreate_wall(element1, wall1, axis, body)

    def join_T(self, wall1, wall2):
        element1 = tool.Ifc.get_entity(wall1)
        element2 = tool.Ifc.get_entity(wall2)
        axis1 = tool.Model.get_wall_axis(wall1)
        axis2 = tool.Model.get_wall_axis(wall2)
        intersect = tool.Cad.intersect_edges(axis1["reference"], axis2["reference"])
        if intersect:
            intersect, _ = intersect
        else:
            return
        connection = "ATEND" if tool.Cad.edge_percent(intersect, axis1["reference"]) > 0.5 else "ATSTART"

        ifcopenshell.api.run(
            "geometry.connect_path",
            tool.Ifc.get(),
            related_element=element1,
            relating_element=element2,
            relating_connection="ATPATH",
            related_connection=connection,
            description="BUTT",
        )

        self.recreate_wall(element1, wall1, axis1["reference"], axis1["reference"])

    def join_V(self, wall1, wall2):
        element1 = tool.Ifc.get_entity(wall1)
        element2 = tool.Ifc.get_entity(wall2)
        axis1 = tool.Model.get_wall_axis(wall1)
        axis2 = tool.Model.get_wall_axis(wall2)
        intersect = tool.Cad.intersect_edges(axis1["reference"], axis2["reference"])
        if intersect:
            intersect, _ = intersect
        else:
            return
        wall1_end = "ATEND" if tool.Cad.edge_percent(intersect, axis1["reference"]) > 0.5 else "ATSTART"
        wall2_end = "ATEND" if tool.Cad.edge_percent(intersect, axis2["reference"]) > 0.5 else "ATSTART"

        ifcopenshell.api.run(
            "geometry.connect_path",
            tool.Ifc.get(),
            relating_element=element1,
            related_element=element2,
            relating_connection=wall1_end,
            related_connection=wall2_end,
            description="MITRE",
        )

        self.recreate_wall(element1, wall1, axis1["reference"], axis1["reference"])
        self.recreate_wall(element2, wall2, axis2["reference"], axis2["reference"])

    def recreate_wall(self, element, obj, axis=None, body=None):
        if axis is None or body is None:
            axis = body = tool.Model.get_wall_axis(obj)["reference"]
        self.axis = copy.deepcopy(axis)
        self.body = copy.deepcopy(body)
        extrusion_data = self.get_extrusion_data(tool.Ifc.get().by_id(obj.data.BIMMeshProperties.ifc_definition_id))
        height = extrusion_data["height"]
        x_angle = extrusion_data["x_angle"]
        self.clippings = []
        layers = tool.Model.get_material_layer_parameters(element)

        for rel in element.ConnectedTo:
            if rel.is_a("IfcRelConnectsPathElements"):
                connection = rel.RelatingConnectionType
                other = tool.Ifc.get_object(rel.RelatedElement)
                if connection not in ["ATPATH", "NOTDEFINED"]:
                    self.join(
                        obj, other, connection, rel.RelatedConnectionType, is_relating=True, description=rel.Description
                    )
        for rel in element.ConnectedFrom:
            if rel.is_a("IfcRelConnectsPathElements"):
                connection = rel.RelatedConnectionType
                other = tool.Ifc.get_object(rel.RelatingElement)
                if connection not in ["ATPATH", "NOTDEFINED"]:
                    self.join(
                        obj,
                        other,
                        connection,
                        rel.RelatingConnectionType,
                        is_relating=False,
                        description=rel.Description,
                    )

        previous_matrix = obj.matrix_world.copy()
        previous_origin = previous_matrix.col[3].to_2d()
        obj.matrix_world[0][3], obj.matrix_world[1][3] = self.body[0]
        bpy.context.view_layer.update()

        for rel in element.ConnectedFrom:
            if rel.is_a() == "IfcRelConnectsElements":
                height = self.clip(obj, tool.Ifc.get_object(rel.RelatingElement))

        new_matrix = copy.deepcopy(obj.matrix_world)
        new_matrix.invert()

        for clipping in self.clippings:
            if clipping["operand_type"] == "IfcHalfSpaceSolid":
                clipping["matrix"] = new_matrix @ clipping["matrix"]

        length = (self.body[1] - self.body[0]).length

        if self.axis_context:
            axis = [(new_matrix @ a.to_3d()).to_2d() for a in self.axis]
            new_axis = ifcopenshell.api.run(
                "geometry.add_axis_representation", tool.Ifc.get(), context=self.axis_context, axis=axis
            )
            old_axis = ifcopenshell.util.representation.get_representation(element, "Plan", "Axis", "GRAPH_VIEW")
            if old_axis:
                for inverse in tool.Ifc.get().get_inverse(old_axis):
                    ifcopenshell.util.element.replace_attribute(inverse, old_axis, new_axis)
                blenderbim.core.geometry.remove_representation(
                    tool.Ifc, tool.Geometry, obj=obj, representation=old_axis
                )
            else:
                ifcopenshell.api.run(
                    "geometry.assign_representation", tool.Ifc.get(), product=element, representation=new_axis
                )

        new_body = ifcopenshell.api.run(
            "geometry.add_wall_representation",
            tool.Ifc.get(),
            context=self.body_context,
            length=length,
            height=height,
            x_angle=x_angle,
            offset=layers["offset"],
            thickness=layers["thickness"],
            clippings=self.clippings,
            booleans=tool.Model.get_manual_booleans(element),
        )

        old_body = ifcopenshell.util.representation.get_representation(element, "Model", "Body", "MODEL_VIEW")
        if old_body:
            for inverse in tool.Ifc.get().get_inverse(old_body):
                ifcopenshell.util.element.replace_attribute(inverse, old_body, new_body)
            obj.data.BIMMeshProperties.ifc_definition_id = int(new_body.id())
            obj.data.name = f"{self.body_context.id()}/{new_body.id()}"
            blenderbim.core.geometry.remove_representation(tool.Ifc, tool.Geometry, obj=obj, representation=old_body)
        else:
            ifcopenshell.api.run(
                "geometry.assign_representation", tool.Ifc.get(), product=element, representation=new_body
            )

        if tool.Ifc.is_moved(obj):
            # Openings should move with the host overall ...
            # ... except their position should stay the same along the local X axis of the wall
            for opening in [r.RelatedOpeningElement for r in element.HasOpenings]:
                percent = tool.Cad.edge_percent(
                    self.body[0], (previous_origin, (previous_matrix @ Vector((1, 0, 0))).to_2d())
                )
                is_x_offset_increased = True if percent < 0 else False

                change_in_x = (self.body[0] - previous_origin).length / self.unit_scale
                coordinates = list(opening.ObjectPlacement.RelativePlacement.Location.Coordinates)
                if is_x_offset_increased:
                    coordinates[0] += change_in_x
                else:
                    coordinates[0] -= change_in_x
                opening.ObjectPlacement.RelativePlacement.Location.Coordinates = coordinates
            blenderbim.core.geometry.edit_object_placement(tool.Ifc, tool.Geometry, tool.Surveyor, obj=obj)

        blenderbim.core.geometry.switch_representation(
            tool.Geometry,
            obj=obj,
            representation=new_body,
            should_reload=True,
            is_global=True,
            should_sync_changes_first=False,
        )
        tool.Geometry.record_object_materials(obj)

    def create_matrix(self, p, x, y, z):
        return Matrix(
            (
                (x[0], y[0], z[0], p[0]),
                (x[1], y[1], z[1], p[1]),
                (x[2], y[2], z[2], p[2]),
                (0.0, 0.0, 0.0, 1.0),
            )
        )

    def get_extrusion_data(self, representation):
        results = {"item": None, "height": 3.0, "x_angle": 0, "is_sloped": False, "direction": Vector((0, 0, 1))}
        item = representation.Items[0]
        while True:
            if item.is_a("IfcExtrudedAreaSolid"):
                results["item"] = item
                x, y, z = item.ExtrudedDirection.DirectionRatios
                if not tool.Cad.is_x(x, 0) or not tool.Cad.is_x(y, 0) or not tool.Cad.is_x(z, 1):
                    results["direction"] = Vector(item.ExtrudedDirection.DirectionRatios)
                    results["x_angle"] = Vector((0, 1)).angle_signed(Vector((y, z)))
                    results["is_sloped"] = True
                results["height"] = (item.Depth * self.unit_scale) / (1 / cos(results["x_angle"]))
                break
            elif item.is_a("IfcBooleanClippingResult"):
                item = item.FirstOperand
            else:
                break
        return results

    def join(self, wall1, wall2, connection1, connection2, is_relating=True, description="BUTT"):
        element1 = tool.Ifc.get_entity(wall1)
        element2 = tool.Ifc.get_entity(wall2)
        layers1 = tool.Model.get_material_layer_parameters(element1)
        layers2 = tool.Model.get_material_layer_parameters(element2)
        axis1 = tool.Model.get_wall_axis(wall1, layers1)
        axis2 = tool.Model.get_wall_axis(wall2, layers2)
        body1 = ifcopenshell.util.representation.get_representation(element1, "Model", "Body", "MODEL_VIEW")
        body2 = ifcopenshell.util.representation.get_representation(element2, "Model", "Body", "MODEL_VIEW")
        extrusion1 = self.get_extrusion_data(body1)
        extrusion2 = self.get_extrusion_data(body2)
        direction1 = (wall1.matrix_world.to_quaternion() @ extrusion1["direction"]).normalized()
        direction2 = (wall2.matrix_world.to_quaternion() @ extrusion2["direction"]).normalized()
        height1 = extrusion1["height"] * self.unit_scale
        height2 = extrusion2["height"] * self.unit_scale
        depth1 = direction1 * height1
        depth2 = direction2 * height2
        normal1 = (axis1["base"][1] - axis1["base"][0]).to_3d().normalized().cross(direction1)
        normal2 = (axis2["base"][1] - axis2["base"][0]).to_3d().normalized().cross(direction2)

        angle = tool.Cad.angle_edges(axis1["reference"], axis2["reference"], signed=True, degrees=True)
        if tool.Cad.is_x(abs(angle), (0, 180), tolerance=0.001):
            return False

        # Work out axis line
        intersect = tool.Cad.intersect_edges(axis1["reference"], axis2["reference"])
        if intersect:
            intersect, _ = intersect
        else:
            return False

        proposed_axis = [self.axis[0], intersect] if connection1 == "ATEND" else [intersect, self.axis[1]]

        if tool.Cad.is_x(tool.Cad.angle_edges(self.axis, proposed_axis, degrees=True), 180, tolerance=0.001):
            # The user has moved the wall into an invalid position that cannot connect at the desired end
            return False

        self.axis[1 if connection1 == "ATEND" else 0] = intersect

        # Work out body

        # Bottom and top plane point
        bp1 = wall1.matrix_world @ Vector(wall1.bound_box[0])
        bp2 = wall2.matrix_world @ Vector(wall2.bound_box[0])
        tp1 = wall1.matrix_world @ Vector(wall1.bound_box[1])

        # Axis lines on bottom, for reference, base, and side axes
        bra1 = (Vector((*axis1["reference"][0], bp1[2])), Vector((*axis1["reference"][1], bp1[2])))
        bba1 = (Vector((*axis1["base"][0], bp1[2])), Vector((*axis1["base"][1], bp1[2])))
        bsa1 = (Vector((*axis1["side"][0], bp1[2])), Vector((*axis1["side"][1], bp1[2])))
        bba2 = (Vector((*axis2["base"][0], bp2[2])), Vector((*axis2["base"][1], bp2[2])))
        bsa2 = (Vector((*axis2["side"][0], bp2[2])), Vector((*axis2["side"][1], bp2[2])))

        # Intersecting the walls sides defined by planes gives 4 lines of intersection
        # Line point, and line direction
        lp1, ld1 = mathutils.geometry.intersect_plane_plane(bba1[0], normal1, bba2[0], normal2)
        lp2, ld2 = mathutils.geometry.intersect_plane_plane(bba1[0], normal1, bsa2[0], normal2)
        lp3, ld3 = mathutils.geometry.intersect_plane_plane(bsa1[0], normal1, bba2[0], normal2)
        lp4, ld4 = mathutils.geometry.intersect_plane_plane(bsa1[0], normal1, bsa2[0], normal2)

        # Intersecting the 4 lines gives the 8 possible verts of intersection
        # 4 on bottom, and 4 on top. 4 on our base line, 4 on our side line.
        bb1 = mathutils.geometry.intersect_line_plane(lp1, lp1 + ld1, bp1, Vector((0, 0, 1)))
        bb2 = mathutils.geometry.intersect_line_plane(lp2, lp2 + ld2, bp1, Vector((0, 0, 1)))
        bs1 = mathutils.geometry.intersect_line_plane(lp3, lp3 + ld3, bp1, Vector((0, 0, 1)))
        bs2 = mathutils.geometry.intersect_line_plane(lp4, lp4 + ld4, bp1, Vector((0, 0, 1)))
        tb1 = mathutils.geometry.intersect_line_plane(lp1, lp1 + ld1, tp1, Vector((0, 0, 1)))
        tb2 = mathutils.geometry.intersect_line_plane(lp2, lp2 + ld2, tp1, Vector((0, 0, 1)))
        ts1 = mathutils.geometry.intersect_line_plane(lp3, lp3 + ld3, tp1, Vector((0, 0, 1)))
        ts2 = mathutils.geometry.intersect_line_plane(lp4, lp4 + ld4, tp1, Vector((0, 0, 1)))

        # Let's distinguish the 8 points by whether they are nearer or further away from the other end
        # These 8 points will be used to find the final body position and clippings.
        i = 0 if connection1 == "ATEND" else 1
        j = 1 if connection1 == "ATEND" else 0
        bbn = tool.Cad.closest_vector(axis1["base"][i].to_3d(), (bb1, bb2))
        bbf = bb2 if bbn == bb1 else bb1
        bsn = tool.Cad.closest_vector(axis1["side"][i].to_3d(), (bs1, bs2))
        bsf = bs2 if bsn == bs1 else bs1
        tbn = tool.Cad.closest_vector(axis1["base"][i].to_3d(), (tb1, tb2))
        tbf = tb2 if tbn == tb1 else tb1
        tsn = tool.Cad.closest_vector(axis1["side"][i].to_3d(), (ts1, ts2))
        tsf = ts2 if tsn == ts1 else ts1

        if description == "MITRE":
            # Mitre joints are an unofficial convention
            bsf_ = tool.Cad.point_on_edge(bsf, bba1)
            tbf_ = tool.Cad.point_on_edge(tbf, bba1)
            tsf_ = tool.Cad.point_on_edge(tsf, bba1)
            new_body = tool.Cad.furthest_vector(bba1[i], (bbf, bsf_)).copy()
            new_body = tool.Cad.furthest_vector(bba1[i], (new_body, tbf_)).copy()
            new_body = tool.Cad.furthest_vector(bba1[i], (new_body, tsf_)).copy()
            self.body[j] = tool.Cad.point_on_edge(new_body, bra1).to_2d()

            if connection1 == connection2:
                if (connection1 == "ATEND" and angle > 0) or (connection1 != "ATEND" and angle < 0):
                    pt = bbf.to_2d().to_3d()
                    x_axis = bsn - bbf
                    y_axis = tbf - bbf
                else:
                    pt = bbn.to_2d().to_3d()
                    x_axis = bsf - bbn
                    y_axis = tbn - bbn
            else:
                if (connection1 == "ATEND" and angle < 0) or (connection1 != "ATEND" and angle > 0):
                    pt = bbf.to_2d().to_3d()
                    x_axis = bsn - bbf
                    y_axis = tbf - bbf
                else:
                    pt = bbn.to_2d().to_3d()
                    x_axis = bsf - bbn
                    y_axis = tbn - bbn

            if connection1 != "ATEND":
                y_axis *= -1
            z_axis = x_axis.cross(y_axis)
            y_axis = z_axis.cross(x_axis)

            self.clippings.append(
                {
                    "type": "IfcBooleanClippingResult",
                    "operand_type": "IfcHalfSpaceSolid",
                    "matrix": self.create_matrix(pt, x_axis, y_axis, z_axis),
                }
            )
        else:
            # This is the standard L and T joints described by IFC
            if (
                tool.Cad.is_x(abs(angle), (90, 270), tolerance=0.001)
                and not extrusion1["is_sloped"]
                and not extrusion2["is_sloped"]
            ):
                if is_relating:
                    self.body[j] = tool.Cad.point_on_edge(bbf, bra1).to_2d()
                else:
                    self.body[j] = tool.Cad.point_on_edge(bbn, bra1).to_2d()
                return True

            bsf_ = tool.Cad.point_on_edge(bsf, bba1)
            tbf_ = tool.Cad.point_on_edge(tbf, bba1)
            tsf_ = tool.Cad.point_on_edge(tsf, bba1)
            new_body = tool.Cad.furthest_vector(bba1[i], (bbf, bsf_)).copy()
            new_body = tool.Cad.furthest_vector(bba1[i], (new_body, tbf_)).copy()
            new_body = tool.Cad.furthest_vector(bba1[i], (new_body, tsf_)).copy()
            self.body[j] = tool.Cad.point_on_edge(new_body, bra1).to_2d()

            if is_relating:
                pt = bbf.to_2d().to_3d()
                x_axis = bsf - bbf
                y_axis = tbf - bbf
            else:
                pt = bbn.to_2d().to_3d()
                x_axis = bsn - bbn
                y_axis = tbn - bbn
            if connection1 != "ATEND":
                y_axis *= -1
            z_axis = x_axis.cross(y_axis)
            y_axis = z_axis.cross(x_axis)

            self.clippings.append(
                {
                    "type": "IfcBooleanClippingResult",
                    "operand_type": "IfcHalfSpaceSolid",
                    "matrix": self.create_matrix(pt, x_axis, y_axis, z_axis),
                }
            )

        return True

    def clip(self, wall1, slab2):
        element1 = tool.Ifc.get_entity(wall1)
        element2 = tool.Ifc.get_entity(slab2)

        layers1 = tool.Model.get_material_layer_parameters(element1)
        axis1 = tool.Model.get_wall_axis(wall1, layers1)

        bases = [axis1["base"][0].to_3d(), axis1["base"][1].to_3d(), axis1["side"][0].to_3d(), axis1["side"][1].to_3d()]

        extrusion = self.get_extrusion_data(tool.Ifc.get().by_id(wall1.data.BIMMeshProperties.ifc_definition_id))
        d = wall1.matrix_world.to_quaternion() @ extrusion["direction"]

        slab_pt = slab2.matrix_world @ Vector((0, 0, 0))
        slab_dir = slab2.matrix_world.to_quaternion() @ Vector((0, 0, -1))

        tops = [mathutils.geometry.intersect_line_plane(b, b + d, slab_pt, slab_dir) for b in bases]

        i_bottom = None
        i_top = None
        for i, co in enumerate(tops):
            if i_top is None or co[2] > i_top[2]:
                i_top = co
                i_bottom = bases[i]

        quaternion = slab2.matrix_world.to_quaternion()
        x_axis = quaternion @ Vector((1, 0, 0))
        y_axis = quaternion @ Vector((0, 1, 0))
        z_axis = quaternion @ Vector((0, 0, 1))
        self.clippings.append(
            {
                "type": "IfcBooleanClippingResult",
                "operand_type": "IfcHalfSpaceSolid",
                "matrix": self.create_matrix(i_top, x_axis, y_axis, z_axis),
            }
        )

        return (i_top - i_bottom).length
