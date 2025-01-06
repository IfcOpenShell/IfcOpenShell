# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2024 Dion Moult <dion@thinkmoult.com>
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
from bpy.types import GizmoGroup
from mathutils import Matrix


class ClippingPlane(GizmoGroup):
    bl_idname = "OBJECT_GGT_bim_clipping_plane"
    bl_label = "Clipping Plane"
    bl_space_type = "VIEW_3D"
    bl_region_type = "WINDOW"
    bl_options = {"3D", "PERSISTENT"}

    @classmethod
    def poll(cls, context):
        obj = context.object
        return (
            context.selected_objects
            and obj
            and obj.name.startswith("ClippingPlane")
            and obj in [sp.obj for sp in context.scene.BIMProjectProperties.clipping_planes]
        )

    def setup(self, context):
        self.obj = None
        self.offset = 0
        self.mw = Matrix()
        self.last_mw = Matrix()

        self.gizmo = self.gizmos.new("GIZMO_GT_arrow_3d")

        def move_get_x():
            return self.offset

        def move_set_x(value):
            self.obj.matrix_world.col[3] = self.mw.col[3] + (self.mw.col[2] * self.offset)
            self.last_mw = self.obj.matrix_world.copy()
            self.offset = value

        self.gizmo.target_set_handler("offset", get=move_get_x, set=move_set_x)

    def refresh(self, context):
        if self.obj != context.object or self.last_mw != context.object.matrix_world:
            self.obj = context.object
            self.offset = 0
            self.mw = context.object.matrix_world.copy()
        obj = context.object
        mw = context.object.matrix_world.normalized()
        mw.col[3] -= mw.col[2] * self.offset
        self.gizmo.matrix_basis = mw
