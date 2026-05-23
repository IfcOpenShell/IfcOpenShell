# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2024 Bonsai Contributors
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
# along with Bonsai.  If not, see <https://www.gnu.org/licenses/>.

import bpy
from bpy.types import Operator, Panel
from bpy.props import EnumProperty

import bonsai.tool as tool

_SKETCH_ROLE_ITEMS = [
    ("Plan", "Plan", "Default plan view — lines become wall axes, closed polylines become slabs"),
    ("Elevation", "Elevation", "Elevation view — IfcWall polylines define wall height profiles"),
]


class SetSketchRole(Operator):
    """Set the BIM role for the active CAD Sketcher sketch"""

    bl_idname = "bim.set_sketch_role"
    bl_label = "Set Sketch Role"
    bl_options = {"UNDO"}

    role: EnumProperty(name="Role", items=_SKETCH_ROLE_ITEMS)

    @classmethod
    def poll(cls, context):
        return hasattr(context.scene, "sketcher") and context.scene.sketcher.active_sketch is not None

    def execute(self, context):
        context.scene.sketcher.active_sketch.tag = self.role
        return {"FINISHED"}


class BIM_PT_cadsketcher(Panel):
    bl_label = "CAD Sketcher BIM"
    bl_idname = "BIM_PT_cadsketcher"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Bonsai"

    @classmethod
    def poll(cls, context):
        if not hasattr(context.scene, "sketcher"):
            return False
        return context.scene.sketcher.active_sketch is not None

    def draw(self, context):
        layout = self.layout
        sketch = context.scene.sketcher.active_sketch

        row = layout.row()
        row.label(text=sketch.name or "Unnamed Sketch", icon="SNAP_PERPENDICULAR")

        row = layout.row(align=True)
        row.label(text="Role:")
        for role_value, role_label, _ in _SKETCH_ROLE_ITEMS:
            op = row.operator("bim.set_sketch_role", text=role_label, depress=(sketch.tag == role_value))
            op.role = role_value

        layout.separator()
        layout.operator("bim.fetch_cad_sketcher", icon="MOD_LATTICE")
