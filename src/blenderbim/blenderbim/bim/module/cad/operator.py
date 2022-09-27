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
import mathutils
import bpy_extras
import blenderbim.tool as tool

messages = {
    "SHARED_VERTEX": "Shared Vertex, no intersection possible",
    "PARALLEL_EDGES": "Edges Parallel, no intersection possible",
    "NON_PLANAR_EDGES": "Non Planar Edges, no clean intersection point",
}


class CadTrimExtend(bpy.types.Operator):
    bl_idname = "bim.cad_trim_extend"
    bl_label = "CAD Trim / Extend"

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return bool(obj) and obj.type == "MESH"

    def cancel_message(self, msg):
        print(msg)
        self.report({"WARNING"}, msg)
        return {"CANCELLED"}

    def execute(self, context):
        # final attempt to enter unfragmented bm/mesh
        # ghastly, but what can I do? it works with these
        # fails without.
        bpy.ops.object.mode_set(mode="OBJECT")
        bpy.ops.object.mode_set(mode="EDIT")

        obj = context.active_object
        me = obj.data

        bm = bmesh.from_edit_mesh(me)
        bm.verts.ensure_lookup_table()
        bm.edges.ensure_lookup_table()

        edges = [e for e in bm.edges if e.select and not e.hide]

        if len(edges) == 2:
            message = tool.Cad.do_vtx_if_appropriate(bm, edges, mode="T")
            if isinstance(message, set):
                msg = messages.get(message.pop())
                return self.cancel_message(msg)
            bm = message
        else:
            return self.cancel_message("select two edges!")

        bm.verts.index_update()
        bm.edges.index_update()
        bmesh.update_edit_mesh(me, loop_triangles=True)

        return {"FINISHED"}


class CadMitre(bpy.types.Operator):
    bl_idname = "bim.cad_mitre"
    bl_label = "CAD Mitre"

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return bool(obj) and obj.type == "MESH"

    def cancel_message(self, msg):
        print(msg)
        self.report({"WARNING"}, msg)
        return {"CANCELLED"}

    def execute(self, context):
        # final attempt to enter unfragmented bm/mesh
        # ghastly, but what can I do? it works with these
        # fails without.
        bpy.ops.object.mode_set(mode="OBJECT")
        bpy.ops.object.mode_set(mode="EDIT")

        obj = context.active_object
        me = obj.data

        bm = bmesh.from_edit_mesh(me)
        bm.verts.ensure_lookup_table()
        bm.edges.ensure_lookup_table()

        edges = [e for e in bm.edges if e.select and not e.hide]

        if len(edges) == 2:
            message = tool.Cad.do_vtx_if_appropriate(bm, edges, mode="V")
            if isinstance(message, set):
                msg = messages.get(message.pop())
                return self.cancel_message(msg)
            bm = message
        else:
            return self.cancel_message("select two edges!")

        bm.verts.index_update()
        bm.edges.index_update()
        bmesh.update_edit_mesh(me, loop_triangles=True)

        return {"FINISHED"}


class CadFillet(bpy.types.Operator):
    bl_idname = "bim.cad_fillet"
    bl_label = "CAD Fillet"
    bl_options = {"REGISTER", "UNDO"}
    resolution: bpy.props.IntProperty(name="Arc Resolution", min=0, default=1)
    radius: bpy.props.FloatProperty(name="Radius", default=0.1)

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj and obj.type == "MESH" and context.mode == "EDIT_MESH"

    def draw(self, context):
        layout = self.layout
        for prop in self.__class__.__annotations__.keys():
            layout.prop(self, prop)

    def execute(self, context):
        bpy.ops.object.mode_set(mode="OBJECT")
        bpy.ops.object.mode_set(mode="EDIT")

        obj = bpy.context.active_object
        cursor = obj.matrix_world.inverted() @ bpy.context.scene.cursor.location
        mesh = obj.data
        bm = bmesh.from_edit_mesh(mesh)
        selected_edges = [e for e in bm.edges if e.select]
        if len(selected_edges) != 2:
            return {"CANCELLED"}

        # Assume the user has selected two edges sharing a vert, but merge verts
        # just in case the vertex is coincident but not shared.
        all_verts = list(set(selected_edges[0].verts) | set(selected_edges[1].verts))
        bmesh.ops.remove_doubles(bm, verts=all_verts, dist=1e-4)

        # Subdivide one of the edges to give us an extra vert to play with
        # without damaging any faces that already exist.
        cut = bmesh.ops.bisect_edges(bm, edges=[selected_edges[1]], cuts=1)
        bm.edges.index_update()
        bmesh.update_edit_mesh(mesh)

        is_wire = selected_edges[0].is_wire

        # Recover the original intention of the selected edges after our bisect operation
        cut_edges = cut["geom_split"][1:]
        selected_edges = [e for e in bm.edges if e.select and e not in cut_edges]
        if set(selected_edges[0].verts) & set(cut_edges[0].verts):
            selected_edges.append(cut_edges[0])
        elif set(selected_edges[0].verts) & set(cut_edges[1].verts):
            selected_edges.append(cut_edges[1])

        # Calculate the distance to slide each edge to make space for the fillet arc
        shared_vert = list(set(selected_edges[0].verts) & set(selected_edges[1].verts))[0]
        v1 = selected_edges[0].other_vert(shared_vert)
        v2 = selected_edges[1].other_vert(shared_vert)
        dir1 = (v1.co - shared_vert.co).normalized()
        dir2 = (v2.co - shared_vert.co).normalized()
        edge_angle = dir1.angle(dir2)
        slide_distance = self.radius / math.tan(edge_angle / 2)

        angle = math.pi - edge_angle
        fillet_v1 = shared_vert.co + (dir1 * slide_distance)
        fillet_v2 = shared_vert.co + (dir2 * slide_distance)

        normal = mathutils.geometry.normal([v1.co, shared_vert.co, v2.co])

        center = mathutils.geometry.intersect_line_line(
            fillet_v1, fillet_v1 + normal.cross(dir1), fillet_v2, fillet_v2 + normal.cross(dir2)
        )[0]

        v = bm.verts.new(fillet_v1)
        steps = self.resolution * 4 if self.resolution else 1
        spin = bmesh.ops.spin(bm, geom=[v], axis=normal, cent=center, steps=steps, angle=angle)

        bmesh.ops.pointmerge(bm, verts=[shared_vert, v], merge_co=v.co)
        bmesh.ops.pointmerge(bm, verts=[v2, spin["geom_last"][0]], merge_co=spin["geom_last"][0].co)

        # If faces are involved, then the chamfer edge protects existing faces from the newly created fillet.
        # If no faces are involved, we delete the chamfer edge.
        if is_wire:
            chamfer_edge = [e for e in bm.edges if shared_vert in e.verts and v2 in e.verts][0]
            bm.edges.remove(chamfer_edge)

        bmesh.update_edit_mesh(mesh)
        mesh.update()
        bm.free()
        return {"FINISHED"}


class CadArcFrom2Points(bpy.types.Operator):
    bl_idname = "bim.cad_arc_from_2_points"
    bl_label = "CAD Arc from 2 Points"
    bl_options = {"REGISTER", "UNDO"}
    resolution: bpy.props.IntProperty(name="Arc Resolution", min=1, default=1)
    should_flip: bpy.props.BoolProperty(name="Flip", description="Flip arc", default=False)

    def draw(self, context):
        layout = self.layout
        for prop in self.__class__.__annotations__.keys():
            layout.prop(self, prop)

    def execute(self, context):
        bpy.ops.object.mode_set(mode="OBJECT")
        bpy.ops.object.mode_set(mode="EDIT")

        if bpy.context.mode != "EDIT_MESH":
            return {"CANCELLED"}
        obj = bpy.context.active_object
        region = bpy.context.region
        region_3d = bpy.context.area.spaces.active.region_3d
        cursor = bpy.context.scene.cursor.location
        center = bpy_extras.view3d_utils.location_3d_to_region_2d(region, region_3d, cursor)
        if not center:
            return {"CANCELLED"}
        mesh = obj.data
        mw = obj.matrix_world
        bm = bmesh.from_edit_mesh(mesh)
        selected_verts = [v for v in bm.verts if v.select]
        if len(selected_verts) != 2:
            return {"CANCELLED"}
        v1 = bpy_extras.view3d_utils.location_3d_to_region_2d(region, region_3d, mw @ selected_verts[0].co)
        v2 = bpy_extras.view3d_utils.location_3d_to_region_2d(region, region_3d, mw @ selected_verts[1].co)
        l1 = v1 - center
        l2 = v2 - center
        angle = l1.angle_signed(l2)

        if self.should_flip:
            if angle > 0:
                angle = -((math.pi * 2) - angle)
            else:
                angle = (math.pi * 2) + angle

        v = selected_verts[0]
        bm.verts.remove(selected_verts[1])
        axis = region_3d.view_rotation @ mathutils.Vector((0, 0, 1))
        bmesh.ops.spin(
            bm,
            geom=[v],
            axis=mw.inverted().to_quaternion() @ axis,
            cent=mw.inverted() @ cursor,
            steps=self.resolution * 4,
            angle=-angle,
        )
        bmesh.update_edit_mesh(mesh)
        mesh.update()
        return {"FINISHED"}


class CadArcFrom3Points(bpy.types.Operator):
    bl_idname = "bim.cad_arc_from_3_points"
    bl_label = "CAD Arc from 3 Points"
    bl_options = {"REGISTER", "UNDO"}
    resolution: bpy.props.IntProperty(name="Arc Resolution", min=1, default=1)
    only_recalculate_center: bpy.props.BoolProperty(name="Only Recalculate Center", default=False)

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj and obj.type == "MESH" and context.mode == "EDIT_MESH"

    def draw(self, context):
        layout = self.layout
        for prop in self.__class__.__annotations__.keys():
            layout.prop(self, prop)

    def execute(self, context):
        bpy.ops.object.mode_set(mode="OBJECT")
        bpy.ops.object.mode_set(mode="EDIT")

        if bpy.context.mode != "EDIT_MESH":
            return {"CANCELLED"}

        obj = bpy.context.edit_object
        mesh = obj.data
        bm = bmesh.from_edit_mesh(mesh)

        selected_verts = [v for v in bm.verts if v.select]
        if len(selected_verts) != 3:
            return {"CANCELLED"}
        pts = [v.co for v in selected_verts]
        center = tool.Cad.get_center_of_arc(pts, obj)
        if not center:
            return {"CANCELLED"}

        bpy.context.scene.cursor.location = center
        if self.only_recalculate_center:
            return {"FINISHED"}

        center = obj.matrix_world.inverted() @ center

        def get_distance_to_other_points(vert):
            other_verts = [v for v in selected_verts if v != vert]
            total_vector = mathutils.Vector((0, 0, 0))
            for other_vert in other_verts:
                total_vector += other_vert.co - vert.co
            return total_vector.length

        # For three selected points that represent a start, end, and point on an
        # arc, the start and end verts can be identified by being furthest away
        # from the other 2 points.
        arc_end_verts = sorted(selected_verts, key=get_distance_to_other_points)[-2:]
        normal = mathutils.geometry.normal(pts)

        dir1 = (arc_end_verts[0].co - center).normalized()
        dir2 = (arc_end_verts[1].co - center).normalized()

        # Let's get the matrix that represents the coordinate system of the arc.
        # This matrix allows us to get 2D vectors for calculating the signed arc angle.
        z = normal
        x = (arc_end_verts[0].co - center).normalized()
        y = z.cross(x)
        arc_matrix = mathutils.Matrix([x, y, z]).transposed().to_4x4()

        dir1 = ((arc_matrix.inverted() @ arc_end_verts[0].co) - (arc_matrix.inverted() @ center)).normalized()
        dir2 = ((arc_matrix.inverted() @ arc_end_verts[1].co) - (arc_matrix.inverted() @ center)).normalized()
        angle = dir1.xy.angle_signed(dir2.xy)

        v = arc_end_verts[0]
        bmesh.ops.spin(bm, geom=[v], axis=normal, cent=center, steps=self.resolution * 4, angle=-angle)
        bmesh.update_edit_mesh(mesh)
        mesh.update()
        return {"FINISHED"}


class AddIfcCircle(bpy.types.Operator):
    bl_idname = "bim.add_ifccircle"
    bl_label = "Add IfcCircle"

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return bool(obj) and obj.type == "MESH"

    def execute(self, context):
        obj = context.active_object
        bpy.ops.object.mode_set(mode="EDIT")

        bm = bmesh.from_edit_mesh(obj.data)

        center = obj.matrix_world.inverted() @ context.scene.cursor.location
        radius = 0.5

        v1 = bm.verts.new((center[0], center[1] + radius, 0.0))
        v2 = bm.verts.new((center[0], center[1] - radius, 0.0))
        bm.verts.index_update()
        indices = [v1.index, v2.index]
        bm.edges.new((v1, v2))
        bmesh.update_edit_mesh(obj.data)

        bpy.ops.object.mode_set(mode="OBJECT")
        group = obj.vertex_groups.new(name="IFCCIRCLE")
        group.add(indices, 1, "REPLACE")
        bpy.ops.object.mode_set(mode="EDIT")
        return {"FINISHED"}
