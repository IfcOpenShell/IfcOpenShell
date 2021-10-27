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
import blenderbim.bim.handler
import blenderbim.tool as tool
import blenderbim.core.misc as core
from blenderbim.bim.ifc import IfcStore
from mathutils import Vector, Matrix, Euler


class Operator:
    def execute(self, context):
        IfcStore.execute_ifc_operator(self, context)
        blenderbim.bim.handler.refresh_ui_data()
        return {"FINISHED"}


class SetOverrideColour(bpy.types.Operator):
    bl_idname = "bim.set_override_colour"
    bl_label = "Set Override Colour"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.selected_objects

    def execute(self, context):
        for obj in context.selected_objects:
            obj.color = context.scene.BIMMiscProperties.override_colour
        area = next(area for area in context.screen.areas if area.type == "VIEW_3D")
        area.spaces[0].shading.color_type = "OBJECT"
        return {"FINISHED"}


class SetViewportShadowFromSun(bpy.types.Operator):
    bl_idname = "bim.set_viewport_shadow_from_sun"
    bl_label = "Set Viewport Shadow from Sun"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        # Does this belong in the drawing module? Perhaps.
        # The vector used for the light direction is a bit funny
        mat = Matrix(((-1.0, 0.0, 0.0, 0.0), (0.0, 0, 1.0, 0.0), (-0.0, -1.0, 0, 0.0), (0.0, 0.0, 0.0, 1.0)))
        context.scene.display.light_direction = mat.inverted() @ (
            context.active_object.matrix_world.to_quaternion() @ Vector((0, 0, -1))
        )
        return {"FINISHED"}


class SnapSpacesTogether(bpy.types.Operator):
    bl_idname = "bim.snap_spaces_together"
    bl_label = "Snap Spaces Together"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.selected_objects

    def execute(self, context):
        threshold = 0.5
        processed_polygons = set()
        selected_mesh_objects = [o for o in context.selected_objects if o.type == "MESH"]
        for obj in selected_mesh_objects:
            for polygon in obj.data.polygons:
                center = obj.matrix_world @ polygon.center
                distance = None
                for obj2 in selected_mesh_objects:
                    if obj2 == obj:
                        continue
                    result = obj2.ray_cast(obj2.matrix_world.inverted() @ center, polygon.normal, distance=threshold)
                    if not result[0]:
                        continue
                    hit = obj2.matrix_world @ result[1]
                    distance = (hit - center).length / 2
                    if distance < 0.01:
                        distance = None
                        break

                    if (obj2.name, result[3]) in processed_polygons:
                        distance *= 2
                        continue

                    offset = polygon.normal * distance * -1
                    processed_polygons.add((obj2.name, result[3]))
                    for v in obj2.data.polygons[result[3]].vertices:
                        obj2.data.vertices[v].co += offset
                    break
                if distance:
                    offset = polygon.normal * distance
                    processed_polygons.add((obj.name, polygon.index))
                    for v in polygon.vertices:
                        obj.data.vertices[v].co += offset
        return {"FINISHED"}


class ResizeToStorey(bpy.types.Operator, Operator):
    bl_idname = "bim.resize_to_storey"
    bl_label = "Resize To Storey"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.selected_objects and tool.Ifc.get()

    def _execute(self, context):
        for obj in context.selected_objects:
            core.resize_to_storey(tool.Misc, obj=obj)


class SplitAlongEdge(bpy.types.Operator, Operator):
    bl_idname = "bim.split_along_edge"
    bl_label = "Split Along Edge"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.selected_objects and tool.Ifc.get()

    def _execute(self, context):
        core.split_along_edge(tool.Misc, cutter=context.active_object, objs=context.selected_objects)
