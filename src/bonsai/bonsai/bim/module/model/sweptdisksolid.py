# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2026
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
#
# This file was generated with the assistance of an AI coding tool.

from typing import Optional, Union

import bpy
import ifcopenshell
import ifcopenshell.util.representation

import bonsai.core.root
import bonsai.tool as tool


def get_swept_disk_solid_body(
    element: Optional[ifcopenshell.entity_instance],
) -> Union[ifcopenshell.entity_instance, None]:
    """Return the element's Body representation if it's a native swept disk solid, else None."""
    if not element:
        return None
    body = ifcopenshell.util.representation.get_representation(element, "Model", "Body", "MODEL_VIEW")
    if body and tool.Loader.is_native_swept_disk_solid(element, body):
        return body
    return None


class BIM_OT_add_swept_disk_solid(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "mesh.add_swept_disk_solid"
    bl_label = "Swept Disk Solid"
    bl_description = (
        "Add a generic IfcBuildingElementProxy whose Body representation is an "
        "IfcSweptDiskSolid: a circular disk profile swept along a directrix path.\n"
        "Useful for cables, rebar, pipes and similar linear elements.\n"
        "Tab into Edit Mode to edit the directrix path directly (it's a native Blender curve)."
    )
    bl_options = {"REGISTER", "UNDO"}

    radius: bpy.props.FloatProperty(name="Radius", default=0.02, min=0.0001, subtype="DISTANCE")

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        return bool(tool.Ifc.get()) and context.mode == "OBJECT"

    def _execute(self, context: bpy.types.Context) -> set[str]:
        ifc_file = tool.Ifc.get()
        if not ifc_file:
            self.report({"ERROR"}, "You need to start an IFC project first to create a swept disk solid.")
            return {"CANCELLED"}

        body_context = ifcopenshell.util.representation.get_context(ifc_file, "Model", "Body", "MODEL_VIEW")
        if not body_context:
            self.report({"ERROR"}, "No Model/Body/MODEL_VIEW representation context is set up for this project.")
            return {"CANCELLED"}

        if context.active_object is not None:
            spawn_location = context.active_object.location.copy()
            context.active_object.select_set(False)
        else:
            spawn_location = context.scene.cursor.location.copy()

        # A native swept disk solid is loaded as (and, per Loader.create_native_swept_disk_solid,
        # expected to be) a beveled 3D POLY curve: add_representation's create_variable_representation
        # already special-cases a Curve with bevel_depth into IfcSweptDiskSolid, so a plain 2-point
        # directrix is all that's needed here; Blender's own curve Edit Mode (Tab) does the rest.
        curve = bpy.data.curves.new("IfcBuildingElementProxy", type="CURVE")
        curve.dimensions = "3D"
        curve.resolution_u = 2
        curve.bevel_depth = self.radius

        spline = curve.splines.new("POLY")
        spline.points.add(1)
        spline.points[0].co = (-0.5, 0.0, 0.0, 1.0)
        spline.points[1].co = (0.5, 0.0, 0.0, 1.0)

        obj = bpy.data.objects.new("IfcBuildingElementProxy", curve)
        obj.location = spawn_location
        context.scene.collection.objects.link(obj)

        bonsai.core.root.assign_class(
            tool.Ifc,
            tool.Collector,
            tool.Root,
            obj=obj,
            ifc_class="IfcBuildingElementProxy",
            should_add_representation=True,
            context=body_context,
        )

        bpy.ops.object.select_all(action="DESELECT")
        context.view_layer.objects.active = obj
        tool.Blender.select_object(obj)
        return {"FINISHED"}
