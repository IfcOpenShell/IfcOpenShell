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
from math import pi, degrees
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
            bpy.ops.bim.dynamically_void_product(obj=obj.name)
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


class JoinWall(bpy.types.Operator):
    bl_idname = "bim.join_wall"
    bl_label = "Join Wall"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = """ Trim/Extend the selected walls to the last selected wall:
    'T' mode: Trim/Extend to the virtual projection
    'L' mode: Chamfer the walls
    'V' mode: Chamfer the walls keeping the angle"""
    join_type: bpy.props.StringProperty()

    @classmethod
    def poll(cls, context):
        return context.selected_objects

    def execute(self, context):
        selected_objs = [o for o in context.selected_objects if o.BIMObjectProperties.ifc_definition_id]
        for obj in selected_objs:
            bpy.ops.bim.dynamically_void_product(obj=obj.name)
        if not self.join_type:
            for obj in selected_objs:
                DumbWallJoiner(obj, obj).unjoin()
            return {"FINISHED"}
        if not context.active_object:
            return {"FINISHED"}
        if len(selected_objs) == 1:
            DumbWallJoiner(context.active_object, target_coordinate=context.scene.cursor.location).extend()
            IfcStore.edited_objs.add(context.active_object)
            return {"FINISHED"}
        if len(selected_objs) < 2:
            return {"FINISHED"}
        for obj in selected_objs:
            if obj == context.active_object:
                continue
            joiner = DumbWallJoiner(obj, context.active_object)
            if self.join_type == "T":
                joiner.join_T()
            elif self.join_type == "L":
                joiner.join_L()
            elif self.join_type == "V":
                joiner.join_V()
            IfcStore.edited_objs.add(obj)
        if self.join_type != "T":
            IfcStore.edited_objs.add(context.active_object)
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


class FlipWall(bpy.types.Operator):
    bl_idname = "bim.flip_wall"
    bl_label = "Flip Wall"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Switch the origin from the min XY corner to the max XY corner, and rotates the origin by 180"

    @classmethod
    def poll(cls, context):
        return context.selected_objects

    def execute(self, context):
        selected_objs = [o for o in context.selected_objects if o.data and hasattr(o.data, "transform")]
        for obj in selected_objs:
            DumbWallFlipper(obj).flip()
            IfcStore.edited_objs.add(obj)
        return {"FINISHED"}


class SplitWall(bpy.types.Operator):
    bl_idname = "bim.split_wall"
    bl_label = "Split Wall"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = (
        "Split selected wall into two walls in correspondence of Blender cursor. The cursor must be in the wall volume"
    )

    @classmethod
    def poll(cls, context):
        return context.selected_objects

    def execute(self, context):
        selected_objs = [o for o in context.selected_objects if o.data and hasattr(o.data, "transform")]
        for obj in selected_objs:
            DumbWallSplitter(obj, context.scene.cursor.location).split()
            IfcStore.edited_objs.add(obj)
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


class DumbWallSplitter:
    def __init__(self, wall, point):
        self.wall = wall
        self.point = point

    def split(self):
        recalculate_dumb_wall_origin(self.wall)
        self.point = self.determine_split_point()
        if not self.point:
            return
        new_wall = self.duplicate_wall()
        self.snap_end_face_to_point(self.wall, "max")
        self.snap_end_face_to_point(new_wall, "min")

    def determine_split_point(self):
        start = self.wall.matrix_world @ Vector(self.wall.bound_box[0])
        end = self.wall.matrix_world @ Vector(self.wall.bound_box[4])
        point, distance = mathutils.geometry.intersect_point_line(self.point, start, end)
        if round(distance, 2) <= 0 or round(distance, 2) >= 1:
            return  # The split point is not on the wall
        return point

    def duplicate_wall(self):
        new = self.wall.copy()
        self.wall.users_collection[0].objects.link(new)
        blenderbim.core.root.copy_class(tool.Ifc, tool.Collector, tool.Geometry, tool.Root, obj=new)
        return new

    def snap_end_face_to_point(self, wall, which_end):
        bm = bmesh.new()
        bm.from_mesh(wall.data)
        bmesh.ops.dissolve_limit(bm, angle_limit=pi / 180 * 1, verts=bm.verts, edges=bm.edges)
        min_face, max_face = self.get_wall_end_faces(wall, bm)
        face = min_face if which_end == "min" else max_face
        local_point = wall.matrix_world.inverted() @ self.point
        for vert in face.verts:
            vert.co.x = local_point.x
        bm.to_mesh(wall.data)
        wall.data.update()
        bm.free()
        IfcStore.edited_objs.add(wall)

    # An end face is a quad that is on one end of the wall or the other. It must
    # have at least one vertex on either extreme X-axis, and a non-insignificant
    # X component of its face normal
    def get_wall_end_faces(self, wall, bm):
        min_face = None
        max_face = None
        min_x = min([v[0] for v in wall.bound_box])
        max_x = max([v[0] for v in wall.bound_box])
        bm.faces.ensure_lookup_table()
        for f in bm.faces:
            for v in f.verts:
                if v.co.x == min_x and abs(f.normal.x) > 0.1:
                    min_face = f
                elif v.co.x == max_x and abs(f.normal.x) > 0.1:
                    max_face = f
            if min_face and max_face:
                break
        return min_face, max_face


class DumbWallFlipper:
    # A flip switches the origin from the min XY corner to the max XY corner, and rotates the origin by 180.
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


class DumbWallJoiner:
    # A dumb wall is a prismatic wall along its local X axis.
    # Given two dumb walls, there are three types of wall joints.
    #  1. T-junction joints
    #  2. L-junction "butt" joints
    #  3. V-junction "mitre" joints
    # The algorithms that handle all joints rely on three fundamental functions.
    #  1. Identify faces at either end of the wall, called "end faces".
    #  2. Given an "end face", identify a side "target face" of the other wall
    #     to project towards.
    #  3. Project the vertices of an "end face" to the "target face".
    # Alternatively, a target coordinate may be provided as an imaginary point for the wall to join to
    def __init__(self, wall1, wall2=None, target_coordinate=None):
        self.wall1 = wall1
        self.wall2 = wall2
        self.target_coordinate = target_coordinate
        self.should_project_to_frontface = True
        self.should_attempt_v_junction_projection = False
        self.initialise_convenience_variables()

    def initialise_convenience_variables(self):
        self.wall1_matrix = self.wall1.matrix_world
        if self.wall2:
            self.wall2_matrix = self.wall2.matrix_world
        self.pos_x = self.wall1_matrix.to_quaternion() @ Vector((1, 0, 0))
        self.neg_x = self.wall1_matrix.to_quaternion() @ Vector((-1, 0, 0))

    # Unjoining a wall geometrically means to flatten the ends of the wall to
    # remove any mitred angle from it.
    def unjoin(self):
        wall1_min_faces, wall1_max_faces = self.get_wall_end_faces(self.wall1)
        min_x = min([v[0] for v in self.wall1.bound_box])
        max_x = max([v[0] for v in self.wall1.bound_box])
        for face in wall1_min_faces:
            for v in face.vertices:
                self.wall1.data.vertices[v].co[0] = min_x
        for face in wall1_max_faces:
            for v in face.vertices:
                self.wall1.data.vertices[v].co[0] = max_x
        self.recalculate_origins()

    # An extension is where a single end of wall1 is projected to an imaginary
    # plane denoted by the target coordinate.
    def extend(self):
        wall1_min_faces, wall1_max_faces = self.get_wall_end_faces(self.wall1)
        ef1_distance = abs(
            mathutils.geometry.distance_point_to_plane(
                self.wall1_matrix @ self.wall1.data.vertices[wall1_min_faces[0].vertices[0]].co,
                self.target_coordinate,
                self.pos_x,
            )
        )
        ef2_distance = abs(
            mathutils.geometry.distance_point_to_plane(
                self.wall1_matrix @ self.wall1.data.vertices[wall1_max_faces[0].vertices[0]].co,
                self.target_coordinate,
                self.neg_x,
            )
        )
        if ef1_distance < ef2_distance:
            self.project_end_faces_to_target(wall1_min_faces)
        else:
            self.project_end_faces_to_target(wall1_max_faces)
        self.recalculate_origins()

    # A T-junction is an ordered operation where a single end of wall1 is joined
    # to wall2 if possible (i.e. walls aren't parallel). Wall2 is not modified.
    # First, wall1 end faces are identified. We attempt to project an end face
    # at both ends to a front face of wall2. We then choose the end face that
    # has the shortest projection distance, and project it.
    def join_T(self):
        self._join_T()
        self.recalculate_origins()

    def _join_T(self):
        wall1_min_faces, wall1_max_faces = self.get_wall_end_faces(self.wall1)
        wall2_end_faces1, wall2_end_faces2 = self.get_wall_end_faces(self.wall2)
        self.wall2_end_faces = wall2_end_faces1 + wall2_end_faces2
        ef1_distance, ef1_target_frontface, ef1_target_backface = self.get_projection_target(wall1_min_faces, 1)
        ef2_distance, ef2_target_frontface, ef2_target_backface = self.get_projection_target(wall1_max_faces, 2)

        # Large distances probably means rounding issues which lead to very long projections
        if ef1_distance and ef1_distance > 50:
            ef1_distance = None
        if ef2_distance and ef2_distance > 50:
            ef2_distance = None

        # Project only the end faces that are closer to their target
        if ef1_distance and ef2_distance is None:
            self.project_end_faces(wall1_min_faces, ef1_target_frontface, ef1_target_backface)
            return (wall1_min_faces, ef1_target_frontface, ef1_target_backface)
        elif ef2_distance and ef1_distance is None:
            self.project_end_faces(wall1_max_faces, ef2_target_frontface, ef2_target_backface)
            return (wall1_max_faces, ef2_target_frontface, ef2_target_backface)
        elif ef1_distance is None and ef2_distance is None:
            return (None, None, None)  # Life is short. BIM is hard.
        elif ef1_distance < ef2_distance:
            self.project_end_faces(wall1_min_faces, ef1_target_frontface, ef1_target_backface)
            return (wall1_min_faces, ef1_target_frontface, ef1_target_backface)
        else:
            self.project_end_faces(wall1_max_faces, ef2_target_frontface, ef2_target_backface)
            return (wall1_max_faces, ef2_target_frontface, ef2_target_backface)

    # An L-junction is ordered operation where a single end of wall1 is joined
    # to the backface of a side of wall2, and then a single end of wall2 is
    # joined back to wall1 as a regular T-junction.
    def join_L(self):
        self.should_project_to_frontface = False
        self._join_T()
        self.swap_walls()
        self.should_project_to_frontface = True
        self._join_T()
        self.recalculate_origins()

    # A V-junction is an unordered operation where wall1 is joined to wall2,
    # then vice versa. First, we do a T-junction from wall1 to wall2, then vice
    # versa. This creates a junction where the inner vertices of the mitre joint
    # touches, but the outer vertices do not. So, we just loop through the end
    # point vertices of each wall, find outer vertices (i.e. vertices that don't
    # touch the other wall), then continue projecting those to the back face of
    # the other wall.
    def join_V(self):
        wall2_end_faces, wall2_target_frontface, wall2_target_backface = self._join_T()
        self.swap_walls()
        wall1_end_faces, wall1_target_frontface, wall1_target_backface = self._join_T()

        for face in wall1_end_faces or []:
            for v in face.vertices:
                global_co = self.wall1_matrix @ self.wall1.data.vertices[v].co
                if self.wall2.closest_point_on_mesh(self.wall2_matrix.inverted() @ global_co, distance=0.001)[0]:
                    continue  # Vertex is already coincident with other wall, do not mitre
                target_face_center = self.wall2_matrix @ wall1_target_backface.center
                target_face_normal = (self.wall2_matrix.to_quaternion() @ wall1_target_backface.normal).normalized()
                self.project_vertex(v, target_face_center, target_face_normal, self.wall1, self.wall1_matrix)

        self.swap_walls()

        for face in wall2_end_faces or []:
            for v in face.vertices:
                global_co = self.wall1_matrix @ self.wall1.data.vertices[v].co
                if self.wall2.closest_point_on_mesh(self.wall2_matrix.inverted() @ global_co, distance=0.001)[0]:
                    continue  # Vertex is already coincident with other wall, do not mitre
                target_face_center = self.wall2_matrix @ wall2_target_backface.center
                target_face_normal = (self.wall2_matrix.to_quaternion() @ wall2_target_backface.normal).normalized()
                self.project_vertex(v, target_face_center, target_face_normal, self.wall1, self.wall1_matrix)
        self.recalculate_origins()

    def recalculate_origins(self):
        bpy.context.view_layer.update()
        recalculate_dumb_wall_origin(self.wall1)
        if self.wall2:
            recalculate_dumb_wall_origin(self.wall2)

    def swap_walls(self):
        self.wall1, self.wall2 = self.wall2, self.wall1
        self.initialise_convenience_variables()

    def project_end_faces(self, end_faces, target_frontface, target_backface):
        target_face = target_frontface if self.should_project_to_frontface else target_backface
        target_face_center = self.wall2_matrix @ target_face.center
        target_face_normal = (self.wall2_matrix.to_quaternion() @ target_face.normal).normalized()

        for end_face in end_faces:
            for v in end_face.vertices:
                self.project_vertex(v, target_face_center, target_face_normal, self.wall1, self.wall1_matrix)

    def project_vertex(self, v, target_face_center, target_face_normal, wall, wall_matrix):
        original_point = wall_matrix @ wall.data.vertices[v].co
        point = mathutils.geometry.intersect_line_plane(
            original_point,
            (original_point) + self.pos_x,
            target_face_center,
            target_face_normal,
        )
        if not point or (point - original_point).length > 50:
            return
        local_point = wall_matrix.inverted() @ point
        wall.data.vertices[v].co = local_point

    def project_end_faces_to_target(self, end_faces):
        for end_face in end_faces:
            for v in end_face.vertices:
                vertex = self.wall1_matrix @ self.wall1.data.vertices[v].co
                self.wall1.data.vertices[v].co = self.wall1_matrix.inverted() @ mathutils.geometry.intersect_line_plane(
                    vertex, vertex + self.pos_x, self.target_coordinate, self.pos_x
                )

    # A projection target face is a side face on the target wall that has a
    # significant local Y component to its normal (i.e. is not pointing up or
    # down or something). In addition, its plane must intersect with the
    # projection vector of an end face. Finally, the projection vector and the
    # normal of the target face must not be acute.
    def get_projection_target(self, end_faces, which_end):
        if not end_faces:
            return (None, None, None)

        # Get a single end face as a sample.
        f1 = end_faces[0]
        f1_center = self.wall1_matrix @ f1.center

        if which_end == 1:
            outwards = self.neg_x
            inwards = self.pos_x
        elif which_end == 2:
            outwards = self.pos_x
            inwards = self.neg_x

        distance = None
        target_frontface = None
        target_backface = None

        for f2 in self.wall2.data.polygons:
            if abs(f2.normal.y) < 0.75:
                continue  # Probably not a side wall
            if f2 in self.wall2_end_faces:
                continue
            # Can we project the end face to the target face?
            f2_center = self.wall2_matrix @ f2.center
            f1_center_offset_x = f1_center + outwards
            f2_normal = (self.wall2_matrix.to_quaternion() @ f2.normal).normalized()
            point = mathutils.geometry.intersect_line_plane(
                f1_center,
                f1_center_offset_x,
                f2_center,
                f2_normal,
            )
            if not point:
                continue  # We can't project to the face at all
            intersection_point, signed_distance = mathutils.geometry.intersect_point_line(
                point, f1_center, f1_center_offset_x
            )
            raycast_direction = outwards if signed_distance > 0 else inwards

            if raycast_direction == outwards and f2_normal.angle(raycast_direction) < math.pi / 2:
                target_backface = f2  # f2 is on the wrong side of the wall
            elif raycast_direction == inwards and f2_normal.angle(raycast_direction) > math.pi / 2:
                target_backface = f2  # f2 is on the wrong side of the wall
            else:
                target_frontface = f2

            distance = (point - f1_center).length

            if distance is not None and target_frontface is not None and target_backface is not None:
                return (distance, target_frontface, target_backface)
        return (None, None, None)

    # An end face is a set of faces that represents either one end of the wall or
    # the other. There is typically only 1 quad or 2 tris for each end.
    # An end face is defined as having at least one vertex on either extreme
    # X-axis, and a non-insignificant X component of its face normal
    def get_wall_end_faces(self, wall):
        min_faces = []
        max_faces = []
        min_x = min([v[0] for v in wall.bound_box])
        max_x = max([v[0] for v in wall.bound_box])
        for f in wall.data.polygons:
            if abs(f.normal.x) < 0.1:
                continue
            end_face_index = self.get_wall_face_end(wall, f, min_x, max_x)
            if end_face_index == 1:
                min_faces.append(f)
            elif end_face_index == 2:
                max_faces.append(f)
        return (min_faces, max_faces)

    # 1 is the leftmost (minimum local X axis) end, and 2 is the rightmost end
    def get_wall_face_end(self, wall, face, min_x, max_x):
        for v in face.vertices:
            if wall.data.vertices[v].co.x == min_x:
                return 1
            if wall.data.vertices[v].co.x == max_x:
                return 2


class DumbWallGenerator:
    def __init__(self, relating_type):
        self.relating_type = relating_type

    def generate(self):
        self.file = IfcStore.get_file()
        unit_scale = ifcopenshell.util.unit.calculate_unit_scale(IfcStore.get_file())
        thicknesses = []
        for rel in self.relating_type.HasAssociations:
            if rel.is_a("IfcRelAssociatesMaterial"):
                material = rel.RelatingMaterial
                if material.is_a("IfcMaterialLayerSet"):
                    thicknesses = [l.LayerThickness for l in material.MaterialLayers]
                    break
        if not sum(thicknesses):
            return

        self.collection = bpy.context.view_layer.active_layer_collection.collection
        self.collection_obj = bpy.data.objects.get(self.collection.name)
        self.width = sum(thicknesses) * unit_scale
        self.height = 3
        self.length = 1
        self.rotation = 0
        self.location = Vector((0, 0, 0))

        if self.has_sketch():
            return self.derive_from_sketch()
        return self.derive_from_cursor()

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
            coords = (stroke.points[0].co, stroke.points[-1].co)
            direction = coords[1] - coords[0]
            length = direction.length
            if length < 0.1:
                continue
            data = {"coords": coords}

            # Round to nearest 50mm (yes, metric for now)
            self.length = 0.05 * round(length / 0.05)
            self.rotation = math.atan2(direction[1], direction[0])
            # Round to nearest 5 degrees
            nearest_degree = (math.pi / 180) * 5
            self.rotation = nearest_degree * round(self.rotation / nearest_degree)
            self.location = coords[0]
            data["obj"] = self.create_wall()
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

    def derive_from_cursor(self):
        self.location = bpy.context.scene.cursor.location
        if self.collection:
            for sibling_obj in self.collection.objects:
                if not isinstance(sibling_obj.data, bpy.types.Mesh):
                    continue
                if "IfcWall" not in sibling_obj.name:
                    continue
                local_location = sibling_obj.matrix_world.inverted() @ self.location
                raycast = sibling_obj.closest_point_on_mesh(local_location, distance=0.01)
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
        return self.create_wall()

    def create_wall(self):
        verts = [
            Vector((0, self.width, 0)),
            Vector((0, 0, 0)),
            Vector((0, self.width, self.height)),
            Vector((0, 0, self.height)),
            Vector((self.length, self.width, 0)),
            Vector((self.length, 0, 0)),
            Vector((self.length, self.width, self.height)),
            Vector((self.length, 0, self.height)),
        ]
        faces = [
            [1, 3, 2, 0],
            [4, 6, 7, 5],
            [1, 0, 4, 5],
            [3, 7, 6, 2],
            [0, 2, 6, 4],
            [1, 5, 7, 3],
        ]
        mesh = bpy.data.meshes.new(name="Wall")
        mesh.from_pydata(verts, [], faces)

        ifc_classes = ifcopenshell.util.type.get_applicable_entities(self.relating_type.is_a(), self.file.schema)
        # Standard cases are deprecated, so let's cull them
        ifc_class = [c for c in ifc_classes if "StandardCase" not in c][0]

        obj = bpy.data.objects.new(tool.Model.generate_occurrence_name(self.relating_type, ifc_class), mesh)
        obj.location = self.location
        obj.rotation_euler[2] = self.rotation
        if self.collection_obj and self.collection_obj.BIMObjectProperties.ifc_definition_id:
            obj.location[2] = self.collection_obj.location[2]
        self.collection.objects.link(obj)

        bpy.ops.bim.assign_class(
            obj=obj.name,
            ifc_class=ifc_class,
            ifc_representation_class="IfcExtrudedAreaSolid/IfcArbitraryClosedProfileDef",
        )

        blenderbim.core.type.assign_type(tool.Ifc, tool.Type, element=tool.Ifc.get_entity(obj), type=self.relating_type)
        element = self.file.by_id(obj.BIMObjectProperties.ifc_definition_id)
        pset = ifcopenshell.api.run("pset.add_pset", self.file, product=element, name="EPset_Parametric")
        ifcopenshell.api.run("pset.edit_pset", self.file, pset=pset, properties={"Engine": "BlenderBIM.DumbLayer2"})
        MaterialData.load(self.file)
        obj.select_set(True)
        return obj


def generate_axis(usecase_path, ifc_file, settings):
    axis_context = ifcopenshell.util.representation.get_context(ifc_file, "Model", "Axis", "GRAPH_VIEW")
    if not axis_context:
        return
    obj = settings["blender_object"]
    product = ifc_file.by_id(obj.BIMObjectProperties.ifc_definition_id)
    parametric = ifcopenshell.util.element.get_psets(product).get("EPset_Parametric")
    if not parametric or parametric["Engine"] != "BlenderBIM.DumbLayer2":
        return
    old_axis = ifcopenshell.util.representation.get_representation(product, "Model", "Axis", "GRAPH_VIEW")
    if settings["context"].ContextType == "Model" and getattr(settings["context"], "ContextIdentifier") == "Body":
        if old_axis:
            blenderbim.core.geometry.remove_representation(tool.Ifc, tool.Geometry, obj=obj, representation=old_axis)

        new_settings = settings.copy()
        new_settings["context"] = axis_context

        mesh = bpy.data.meshes.new("Temporary Axis")
        start = Vector(obj.bound_box[0])
        end = Vector(obj.bound_box[4])
        mesh.from_pydata([start, end], [(0, 1)], [])

        new_settings["geometry"] = mesh
        new_axis = ifcopenshell.api.run(
            "geometry.add_representation", ifc_file, should_run_listeners=False, **new_settings
        )
        ifcopenshell.api.run(
            "geometry.assign_representation",
            ifc_file,
            should_run_listeners=False,
            **{"product": product, "representation": new_axis}
        )
        bpy.data.meshes.remove(mesh)


def calculate_quantities(usecase_path, ifc_file, settings):
    unit_scale = ifcopenshell.util.unit.calculate_unit_scale(ifc_file)
    obj = settings["blender_object"]
    product = ifc_file.by_id(obj.BIMObjectProperties.ifc_definition_id)
    parametric = ifcopenshell.util.element.get_psets(product).get("EPset_Parametric")
    if not parametric or parametric["Engine"] != "BlenderBIM.DumbLayer2":
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
        self.unit_scale = ifcopenshell.util.unit.calculate_unit_scale(ifc_file)
        layer = settings["layer"]
        thickness = settings["attributes"].get("LayerThickness")
        if thickness is None:
            return
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
                        for element in rel.RelatedObjects:
                            self.change_thickness(element, thickness)
                else:
                    for rel in inverse.AssociatedTo:
                        for element in rel.RelatedObjects:
                            self.change_thickness(element, thickness)

    def regenerate_from_type(self, usecase_path, ifc_file, settings):
        self.unit_scale = ifcopenshell.util.unit.calculate_unit_scale(ifc_file)
        new_material = ifcopenshell.util.element.get_material(settings["relating_type"])
        if not new_material or not new_material.is_a("IfcMaterialLayerSet"):
            return
        new_thickness = sum([l.LayerThickness for l in new_material.MaterialLayers])
        material = ifcopenshell.util.element.get_material(settings["related_object"])
        if material and material.is_a("IfcMaterialLayerSetUsage") and material.LayerSetDirection == "AXIS2":
            self.change_thickness(settings["related_object"], new_thickness)

    def change_thickness(self, element, thickness):
        obj = IfcStore.get_element(element.id())
        if not obj:
            return

        delta_thickness = (thickness * self.unit_scale) - obj.dimensions.y
        if round(delta_thickness, 2) == 0:
            return

        bm = bmesh.new()
        bm.from_mesh(obj.data)
        bmesh.ops.dissolve_limit(bm, angle_limit=pi / 180 * 1, verts=bm.verts, edges=bm.edges)

        min_face, max_face = self.get_wall_end_faces(obj, bm)

        verts_to_move = []
        verts_to_move.extend(self.thicken_face(min_face, delta_thickness))
        verts_to_move.extend(self.thicken_face(max_face, delta_thickness))
        for vert_to_move in verts_to_move:
            vert_to_move["vert"].co += vert_to_move["vector"]

        bm.to_mesh(obj.data)
        obj.data.update()
        bm.free()
        IfcStore.edited_objs.add(obj)

    def thicken_face(self, face, delta_thickness):
        slide_magnitude = abs(delta_thickness)
        results = []
        for vert in face.verts:
            slide_vector = None
            for edge in vert.link_edges:
                other_vert = edge.verts[1] if edge.verts[0] == vert else edge.verts[0]
                if delta_thickness > 0:
                    potential_slide_vector = (vert.co - other_vert.co).normalized()
                    if potential_slide_vector.y < 0:
                        continue
                else:
                    potential_slide_vector = (other_vert.co - vert.co).normalized()
                    if potential_slide_vector.y > 0:
                        continue
                if abs(potential_slide_vector.x) > 0.9 or abs(potential_slide_vector.z) > 0.9:
                    continue
                slide_vector = potential_slide_vector
                break
            if not slide_vector:
                continue
            slide_vector *= slide_magnitude / abs(slide_vector.y)
            results.append({"vert": vert, "vector": slide_vector})
        return results

    # An end face is a quad that is on one end of the wall or the other. It must
    # have at least one vertex on either extreme X-axis, and a non-insignificant
    # X component of its face normal
    def get_wall_end_faces(self, wall, bm):
        min_face = None
        max_face = None
        min_x = min([v[0] for v in wall.bound_box])
        max_x = max([v[0] for v in wall.bound_box])
        bm.faces.ensure_lookup_table()
        for f in bm.faces:
            for v in f.verts:
                if v.co.x == min_x and abs(f.normal.x) > 0.1:
                    min_face = f
                elif v.co.x == max_x and abs(f.normal.x) > 0.1:
                    max_face = f
            if min_face and max_face:
                break
        return min_face, max_face
