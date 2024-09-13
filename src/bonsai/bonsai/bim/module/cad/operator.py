# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of Bonsai.
#
# Bonsai is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Bonsai is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Bonsai.  If not, see <http://www.gnu.org/licenses/>.

import bpy
import math
import bmesh
import mathutils
import bpy_extras
import bonsai.tool as tool
from mathutils import Vector, Matrix
from math import pi, radians, sin, cos, sqrt
import ifcopenshell.util.unit


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

        bmesh.ops.remove_doubles(bm, verts=list(set(edges[0].verts) | set(edges[1].verts)), dist=1e-5)
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

        bmesh.ops.remove_doubles(bm, verts=list(set(edges[0].verts) | set(edges[1].verts)), dist=1e-5)
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
        si_conversion = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
        self.radius = self.radius * si_conversion

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

        bm.verts.index_update()
        bm.edges.index_update()
        bmesh.update_edit_mesh(mesh)
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
        axis = region_3d.view_rotation @ Vector((0, 0, 1))
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

        arc = [v for v in bm.verts if v.select]
        if len(arc) != 3:
            return {"CANCELLED"}
        elif len([e for e in bm.edges if e.select]) != 2:
            return {"CANCELLED"}

        sorted_arc = [None, None, None]
        for v1 in arc:
            connections = 0
            for link_edge in v1.link_edges:
                v2 = link_edge.other_vert(v1)
                if v2 in arc:
                    connections += 1
            if connections == 2:  # Midpoint
                sorted_arc[1] = v1
            else:
                sorted_arc[2 if sorted_arc[2] is None else 0] = v1

        points = [tuple(v.co) for v in sorted_arc]
        verts, _ = tool.Cad.create_arc_segments(points, num_verts=(self.resolution * 4) + 1, make_edges=False)

        bm.verts.index_update()
        bm.edges.index_update()

        index_offset = len(bm.verts)
        new_verts = [bm.verts.new(v) for v in verts]
        new_edges = [bm.edges.new((new_verts[i], new_verts[i + 1])) for i in range(len(new_verts) - 1)]

        bm.verts.remove(sorted_arc[1])
        bmesh.ops.remove_doubles(bm, verts=new_verts + [sorted_arc[0], sorted_arc[2]], dist=1e-5)

        bmesh.update_edit_mesh(mesh)
        return {"FINISHED"}


class CadOffset(bpy.types.Operator):
    bl_idname = "bim.cad_offset"
    bl_label = "CAD Offset"
    bl_options = {"REGISTER", "UNDO"}
    distance: bpy.props.FloatProperty(name="Distance", default=0.1)

    @classmethod
    def poll(self, context):
        return context.mode == "EDIT_MESH"

    def draw(self, context):
        layout = self.layout
        for prop in self.__class__.__annotations__.keys():
            layout.prop(self, prop)

    def cancel_message(self, msg):
        self.report({"WARNING"}, msg)
        return {"CANCELLED"}

    def execute(self, context):
        # This is not the same as Mesh Tools or Sverchok. Mesh Tools is based on
        # a 3D "rail" which allows fancy 3D edge offsets, but will get different
        # results to traditional CAD, which expects offsets to occur on a
        # defined 2D workplane. This CAD offset does a pure 2D operation, so it
        # always looks correct from the desired "2D workplane". This also
        # reduces the settings down to one parameter instead of the huge config
        # dialog that Mesh Tools has. Sverchok is 2D based, but has a weird side
        # effect of converting an unclosed loop into a closed loop which is also
        # not what users expect.

        si_conversion = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
        self.distance = self.distance * si_conversion

        bpy.ops.object.mode_set(mode="OBJECT")
        bpy.ops.object.mode_set(mode="EDIT")

        obj = context.active_object
        mw = obj.matrix_world

        bm = bmesh.from_edit_mesh(obj.data)
        bm.verts.ensure_lookup_table()
        bm.edges.ensure_lookup_table()

        edges = [e for e in bm.edges if e.select and not e.hide]

        if len(edges) < 1:
            return self.cancel_message("NO_EDGES")

        verts = set()
        [verts.update(e.verts) for e in edges]

        # Use the viewport angle to determine the offset direction
        for area in bpy.context.screen.areas:
            if area.type == "VIEW_3D":
                # Don't ask me, I don't know.
                # view_matrix = area.spaces.active.region_3d.view_matrix
                x = area.spaces.active.region_3d.view_rotation @ Vector((1, 0, 0))
                y = area.spaces.active.region_3d.view_rotation @ Vector((0, 1, 0))
                z = area.spaces.active.region_3d.view_rotation @ Vector((0, 0, 1))
                wp = Matrix([x, y, z, Vector((0, 0, 0))]).to_4x4().transposed()
                break

        rotation = Matrix.Rotation(pi / 2, 2, "Z")
        rotation_i = Matrix.Rotation(-pi / 2, 2, "Z")

        # Create loops from edges
        loop_edges = set(edges)
        loops = []
        while loop_edges:
            edge = loop_edges.pop()
            loop = [edge]
            has_found_connected_edge = True
            while has_found_connected_edge:
                has_found_connected_edge = False
                for edge in loop_edges.copy():
                    edge_verts = set(edge.verts)
                    if edge_verts & set(loop[0].verts):
                        loop.insert(0, edge)
                        loop_edges.remove(edge)
                        has_found_connected_edge = True
                    elif edge_verts & set(loop[-1].verts):
                        loop.append(edge)
                        loop_edges.remove(edge)
                        has_found_connected_edge = True
            loops.append(loop)

        for loop in loops:
            all_verts = {v.index for e in loop for v in e.verts}
            possible_v1s = []
            is_closed = True
            for edge in loop:
                # If we have an open loop, start at either end instead
                v = edge.verts[0]
                if len(v.link_edges) == 1:
                    possible_v1s.append(v)
                    is_closed = False
                else:
                    for link_edge in v.link_edges:
                        if link_edge.other_vert(v).index not in all_verts:
                            possible_v1s.append(v)
                            is_closed = False
                            break
                v = edge.verts[1]
                if len(v.link_edges) == 1:
                    possible_v1s.append(v)
                    is_closed = False
                else:
                    for link_edge in v.link_edges:
                        if link_edge.other_vert(v).index not in all_verts:
                            possible_v1s.append(v)
                            is_closed = False
                            break

            # Always start at the same vertex, so that when the operator is
            # refreshed with new parameters the axes don't randomly get flipped.
            if is_closed:
                bm.verts.ensure_lookup_table()
                bm.edges.ensure_lookup_table()
                start = bm.verts[min(all_verts)]
            else:
                start = possible_v1s[0] if possible_v1s[0].index < possible_v1s[1].index else possible_v1s[1]

            v1 = start

            new_verts = []
            processed_verts = set()
            # [v0] --> v1 --> v2
            while v1:
                if v1.index in processed_verts:
                    break

                link_verts = []
                if len(v1.link_edges) == 1:
                    v = v1.link_edges[0].other_vert(v1)
                    link_verts.append(v) if v.index in all_verts else None
                else:
                    v = v1.link_edges[0].other_vert(v1)
                    link_verts.append(v) if v.index in all_verts else None
                    v = v1.link_edges[1].other_vert(v1)
                    link_verts.append(v) if v.index in all_verts else None

                if len(link_verts) == 1:
                    v2 = link_verts[0]
                    v0 = None if v2.index not in processed_verts else v2
                    v2 = None if v2.index in processed_verts else v2
                else:
                    v2 = link_verts[0]
                    v0 = link_verts[1]
                    if v2.index in processed_verts:
                        if is_closed and v0.index in processed_verts:
                            v3 = start
                            v0 = v0 if v2 == v3 else v2
                            v2 = v3
                        else:
                            v0, v2 = v2, v0

                normals = []
                v1co = (wp.inverted() @ mw @ v1.co).to_2d()

                if v2:
                    v2co = (wp.inverted() @ mw @ v2.co).to_2d()
                    direction = (v2co - v1co).normalized()
                    local_direction = (rotation @ direction).normalized()
                    normals.append(local_direction)

                if v0:
                    v0co = (wp.inverted() @ mw @ v0.co).to_2d()
                    direction = (v0co - v1co).normalized()
                    local_direction = (rotation_i @ direction).normalized()
                    normals.append(local_direction)

                if len(normals) == 2:
                    # https://stackoverflow.com/a/54042831/9627415
                    new_normal = (normals[0].lerp(normals[1], 0.5)).normalized()
                    offset_length = self.distance / sqrt((1 + normals[0].dot(normals[1])) / 2)
                    offset = mw.inverted().to_quaternion() @ (wp.to_quaternion() @ (new_normal * offset_length).to_3d())
                    new_vert = v1.co + offset
                    new_verts.append(bm.verts.new(new_vert))
                else:
                    normal = (normals[0] * self.distance).to_3d()
                    offset = mw.inverted().to_quaternion() @ (wp.to_quaternion() @ normal)
                    new_vert = v1.co + offset
                    new_verts.append(bm.verts.new(new_vert))

                processed_verts.add(v1.index)

                if v2 in processed_verts:
                    break

                v1 = v2

            [bm.edges.new((new_verts[i], new_verts[i + 1])) for i in range(len(new_verts) - 1)]
            if is_closed:
                bm.edges.new((new_verts[len(new_verts) - 1], new_verts[0]))

        bm.verts.index_update()
        bm.edges.index_update()
        bmesh.update_edit_mesh(obj.data)
        return {"FINISHED"}


class AddIfcCircle(bpy.types.Operator):
    bl_idname = "bim.add_ifccircle"
    bl_label = "Add IfcCircle"
    radius: bpy.props.FloatProperty(name="Radius", default=0.5)

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return bool(obj) and obj.type == "MESH"

    def execute(self, context):
        si_conversion = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
        self.radius = self.radius * si_conversion

        if self.has_selected_existing_circle(context):
            self.change_radius(context)
        else:
            self.create_circle(context)
        return {"FINISHED"}

    def has_selected_existing_circle(self, context):
        obj = context.active_object
        bm = bmesh.from_edit_mesh(obj.data)
        verts = [v for v in bm.verts if v.select and not v.hide]
        if len(verts) != 2:
            return False
        groups = []
        for i, group in enumerate(obj.vertex_groups):
            if "IFCCIRCLE" in group.name:
                groups.append(i)
        bm.verts.layers.deform.verify()
        deform_layer = bm.verts.layers.deform.active
        for group in groups:
            if group in verts[0][deform_layer] and group in verts[1][deform_layer]:
                return True

    def change_radius(self, context):
        obj = context.active_object
        bm = bmesh.from_edit_mesh(obj.data)
        verts = [v for v in bm.verts if v.select and not v.hide]
        center = verts[0].co.lerp(verts[1].co, 0.5)
        verts[0].co = center + ((verts[0].co - center).normalized() * self.radius)
        verts[1].co = center + ((verts[1].co - center).normalized() * self.radius)
        bm.verts.index_update()
        bm.edges.index_update()
        bmesh.update_edit_mesh(obj.data)

    def create_circle(self, context):
        obj = context.active_object
        bpy.ops.object.mode_set(mode="OBJECT")
        # The last group may be the result of a prior run of this operator.
        # I tried looping through all groups but Blender group indices seem to behave unpredictably.
        if len(obj.vertex_groups):
            last_group = obj.vertex_groups[-1]
            verts_in_group = [v for v in obj.data.vertices if last_group.index in [vg.group for vg in v.groups]]
            if "IFCCIRCLE" in last_group.name and len(verts_in_group) != 2:
                obj.vertex_groups.remove(last_group)
        group = obj.vertex_groups.new(name="IFCCIRCLE")
        bpy.ops.object.mode_set(mode="EDIT")

        bm = bmesh.from_edit_mesh(obj.data)

        bm.verts.layers.deform.verify()
        deform_layer = bm.verts.layers.deform.active

        center = obj.matrix_world.inverted() @ context.scene.cursor.location

        v1 = bm.verts.new((center[0], center[1] + self.radius, 0.0))
        v2 = bm.verts.new((center[0], center[1] - self.radius, 0.0))
        bm.verts.index_update()
        bm.edges.new((v1, v2))

        for vert in [v1, v2]:
            vert[deform_layer][group.index] = 1

        bm.verts.index_update()
        bm.edges.index_update()
        bmesh.update_edit_mesh(obj.data)


class AddIfcArcIndexFillet(bpy.types.Operator):
    bl_idname = "bim.add_ifcarcindex_fillet"
    bl_label = "Add Arc Index Fillet"
    bl_options = {"REGISTER", "UNDO"}
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
        si_conversion = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
        self.radius = self.radius * si_conversion

        if self.has_selected_existing_arc(context):
            self.change_radius(context)
        else:
            self.create_arc(context)
        return {"FINISHED"}

    def has_selected_existing_arc(self, context):
        obj = context.active_object
        bm = bmesh.from_edit_mesh(obj.data)
        verts = [v for v in bm.verts if v.select and not v.hide]
        if len(verts) != 3:
            return False
        groups = []
        for i, group in enumerate(obj.vertex_groups):
            if "IFCARCINDEX" in group.name:
                groups.append(i)
        bm.verts.layers.deform.verify()
        deform_layer = bm.verts.layers.deform.active
        for group in groups:
            try:
                if group in verts[0][deform_layer] and group in verts[1][deform_layer]:
                    return True
            except:
                pass  # Potentially fail if the vert has been removed in the previous operation

    def change_radius(self, context):
        obj = context.active_object
        bm = bmesh.from_edit_mesh(obj.data)
        edges = [e for e in bm.edges if e.select and not e.hide]

        mid = list(set(edges[0].verts) & set(edges[1].verts))[0]
        v1 = edges[0].other_vert(mid)
        v2 = edges[1].other_vert(mid)
        center = tool.Cad.get_center_of_arc([v1.co, mid.co, v2.co])

        if len(v1.link_edges) != 2 or len(v2.link_edges) != 2:
            return

        v3 = v1.link_edges[1].other_vert(v1) if mid in v1.link_edges[0].verts else v1.link_edges[0].other_vert(v1)
        v4 = v2.link_edges[1].other_vert(v2) if mid in v2.link_edges[0].verts else v2.link_edges[0].other_vert(v2)
        dir1 = (v3.co - v1.co).normalized()
        dir2 = (v4.co - v2.co).normalized()

        intersect = mathutils.geometry.intersect_line_line(v3.co, v1.co, v4.co, v2.co)[0]

        edge_angle = dir1.angle(dir2)
        slide_distance = self.radius / math.tan(edge_angle / 2)

        v1.co = intersect + (dir1 * slide_distance)
        v2.co = intersect + (dir2 * slide_distance)

        normal = mathutils.geometry.normal([v1.co, intersect, v2.co])
        center = mathutils.geometry.intersect_line_line(
            v1.co, v1.co + normal.cross(dir1), v2.co, v2.co + normal.cross(dir2)
        )[0]

        mid.co = center + ((v1.co.lerp(v2.co, 0.5) - center).normalized() * self.radius)

        bm.verts.index_update()
        bm.edges.index_update()
        bmesh.update_edit_mesh(obj.data)

    def create_arc(self, context):
        obj = bpy.context.active_object

        bpy.ops.object.mode_set(mode="OBJECT")
        # The last group may be the result of a prior run of this operator.
        # I tried looping through all groups but Blender group indices seem to behave unpredictably.
        if len(obj.vertex_groups):
            last_group = obj.vertex_groups[-1]
            verts_in_group = [v for v in obj.data.vertices if last_group.index in [vg.group for vg in v.groups]]
            if "IFCARCINDEX" in last_group.name and len(verts_in_group) != 3:
                obj.vertex_groups.remove(last_group)
        group = obj.vertex_groups.new(name="IFCARCINDEX")
        bpy.ops.object.mode_set(mode="EDIT")

        bm = bmesh.from_edit_mesh(obj.data)

        bm.verts.layers.deform.verify()
        deform_layer = bm.verts.layers.deform.active

        selected_edges = [e for e in bm.edges if e.select]
        if len(selected_edges) != 2:
            return {"CANCELLED"}

        # Assume the user has selected two edges sharing a vert, but merge verts
        # just in case the vertex is coincident but not shared.
        all_verts = list(set(selected_edges[0].verts) | set(selected_edges[1].verts))

        bmesh.ops.remove_doubles(bm, verts=all_verts, dist=1e-4)

        # Calculate the distance to slide each edge to make space for the fillet arc
        shared_vert = list(set(selected_edges[0].verts) & set(selected_edges[1].verts))[0]
        v1 = selected_edges[0].other_vert(shared_vert)
        v2 = selected_edges[1].other_vert(shared_vert)
        dir1 = (v1.co - shared_vert.co).normalized()
        dir2 = (v2.co - shared_vert.co).normalized()
        edge_angle = dir1.angle(dir2)
        slide_distance = self.radius / math.tan(edge_angle / 2)

        angle = math.pi - edge_angle
        fillet_v1co = shared_vert.co + (dir1 * slide_distance)
        fillet_v2co = shared_vert.co + (dir2 * slide_distance)

        normal = mathutils.geometry.normal([v1.co, shared_vert.co, v2.co])

        center = mathutils.geometry.intersect_line_line(
            fillet_v1co, fillet_v1co + normal.cross(dir1), fillet_v2co, fillet_v2co + normal.cross(dir2)
        )[0]

        fillet_v1 = bm.verts.new(fillet_v1co)
        fillet_v2 = bm.verts.new(fillet_v2co)

        midpointco = center + ((fillet_v1co.lerp(fillet_v2.co, 0.5) - center).normalized() * self.radius)
        midpoint = bm.verts.new(midpointco)

        bm.edges.new((v1, fillet_v1))
        bm.edges.new((v2, fillet_v2))
        bm.edges.new((fillet_v1, midpoint))
        bm.edges.new((fillet_v2, midpoint))

        bmesh.ops.delete(bm, geom=[shared_vert], context="VERTS")

        for vert in [fillet_v1, midpoint, fillet_v2]:
            vert[deform_layer][group.index] = 1

        bm.verts.index_update()
        bm.edges.index_update()
        bmesh.update_edit_mesh(obj.data)


class AlignViewToProfile(bpy.types.Operator):
    bl_idname = "bim.align_view_to_profile"
    bl_label = "Align View To Profile"
    #            __ ___
    #          .'. -- . '.
    #         /U)  __   (O|
    #        /.'  ()()   '.\._
    #      .',/;,_.--._.;;) . '--..__
    #     /  ,///|.__.|.\\\  \ '.  '.''---..___
    #    /'._ '' ||  ||  '' _'\  :   \   '   . '.
    #   /        ||  ||        '.,    )   )   :  \
    #  :'-.__ _  ||  ||   _ __.' _\_ .'  '   '   ,)
    #  (          '  |'        ( __= ___..-._ ( (.\\
    # ('\      .___ ___.      /'.___=          \.\.\
    #  \\\-..____________..-'///

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return bool(obj) and obj.type == "MESH"

    def execute(self, context):
        bpy.ops.object.mode_set(mode="OBJECT")
        bpy.ops.view3d.view_axis(type="TOP", align_active=True)
        region_3d = bpy.context.area.spaces.active.region_3d
        region_3d.view_perspective = "ORTHO"
        bpy.ops.object.mode_set(mode="EDIT")
        return {"FINISHED"}


class AddRectangle(bpy.types.Operator):
    bl_idname = "bim.add_rectangle"
    bl_label = "Add Rectangle"
    x: bpy.props.FloatProperty(name="X", default=1)
    y: bpy.props.FloatProperty(name="Y", default=1)

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return bool(obj) and obj.type == "MESH"

    def execute(self, context):
        si_conversion = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
        self.x = self.x * si_conversion
        self.y = self.y * si_conversion

        obj = context.active_object
        bm = bmesh.from_edit_mesh(obj.data)
        cursor = obj.matrix_world.inverted() @ context.scene.cursor.location
        new_verts = [
            bm.verts.new((cursor[0], cursor[1], 0.0)),
            bm.verts.new((cursor[0] + self.x, cursor[1], 0.0)),
            bm.verts.new((cursor[0] + self.x, cursor[1] + self.y, 0.0)),
            bm.verts.new((cursor[0], cursor[1] + self.y, 0.0)),
        ]
        [bm.edges.new((new_verts[i], new_verts[i + 1])) for i in range(len(new_verts) - 1)]
        bm.edges.new((new_verts[len(new_verts) - 1], new_verts[0]))

        bm.verts.index_update()
        bm.edges.index_update()
        bmesh.update_edit_mesh(obj.data)
        return {"FINISHED"}
