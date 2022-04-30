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
import blenderbim.tool as tool

messages = {
    "SHARED_VERTEX": "Shared Vertex, no intersection possible",
    "PARALLEL_EDGES": "Edges Parallel, no intersection possible",
    "NON_PLANAR_EDGES": "Non Planar Edges, no clean intersection point",
}


class CadTrimExtend(bpy.types.Operator):
    """Weld intersecting edges, project converging edges towards their intersection"""

    bl_idname = "bim.cad_trim_extend"
    bl_label = "CAD Trim / Extend"
    join_type: bpy.props.StringProperty()

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
            message = tool.Cad.do_vtx_if_appropriate(bm, edges)
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
