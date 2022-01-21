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
import numpy as np
import ifcopenshell
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
    total_storeys: bpy.props.IntProperty()

    @classmethod
    def poll(cls, context):
        return context.selected_objects and tool.Ifc.get()

    def _execute(self, context):
        for obj in context.selected_objects:
            core.resize_to_storey(tool.Misc, obj=obj, total_storeys=self.total_storeys)


class SplitAlongEdge(bpy.types.Operator, Operator):
    bl_idname = "bim.split_along_edge"
    bl_label = "Split Along Edge"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.selected_objects and tool.Ifc.get()

    def _execute(self, context):
        core.split_along_edge(tool.Misc, cutter=context.active_object, objs=context.selected_objects)


class GetConnectedSystemElements(bpy.types.Operator, Operator):
    bl_idname = "bim.get_connected_system_elements"
    bl_label = "Get Connected System Elements"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.selected_objects and tool.Ifc.get()

    def _execute(self, context):
        # Just dumped here for now before the system module gets properly planned
        def pprint_element(e):
            return "{} ({})".format(e.Name, e.GlobalId)

        start = tool.Ifc.get_entity(bpy.context.active_object)

        connected_elements = []

        # Note: this code is for IFC2X3. IFC4 has a different approach.
        print("Investigating element:", pprint_element(start))
        for rel in start.HasPorts:
            for rel2 in rel.RelatingPort.ConnectedTo:
                print(
                    "{} is connected as via {} ({}) TO {} ({}), contained in {}".format(
                        pprint_element(start),
                        rel.RelatingPort.FlowDirection,
                        rel.RelatingPort.GlobalId,
                        rel2.RelatedPort.FlowDirection,
                        rel2.RelatedPort.GlobalId,
                        [pprint_element(r.RelatedElement) for r in rel2.RelatedPort.ContainedIn],
                    )
                )
                connected_elements.extend([r.RelatedElement for r in rel2.RelatedPort.ContainedIn])
            for rel2 in rel.RelatingPort.ConnectedFrom:
                print(
                    "{} is connected as via {} ({}) FROM {} ({}), contained in {}".format(
                        pprint_element(start),
                        rel.RelatingPort.FlowDirection,
                        rel.RelatingPort.GlobalId,
                        rel2.RelatingPort.FlowDirection,
                        rel2.RelatingPort.GlobalId,
                        [pprint_element(r.RelatedElement) for r in rel2.RelatingPort.ContainedIn],
                    )
                )
                connected_elements.extend([r.RelatedElement for r in rel2.RelatingPort.ContainedIn])

        for element in connected_elements:
            obj = tool.Ifc.get_object(element)
            if obj:
                obj.select_set(True)


class DrawSystemArrows(bpy.types.Operator, Operator):
    bl_idname = "bim.draw_system_arrows"
    bl_label = "Draw System Arrows"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.selected_objects and tool.Ifc.get()

    def _execute(self, context):
        unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
        curve = bpy.data.objects.new("System Arrows", bpy.data.curves.new("System Arrows", "CURVE"))
        curve.data.dimensions = "3D"
        context.scene.collection.objects.link(curve)
        for obj in bpy.context.selected_objects:
            if not obj.BIMObjectProperties.ifc_definition_id:
                continue
            element = tool.Ifc.get_entity(obj)
            sources = []
            sinks = []
            for rel in getattr(element, "HasPorts", []) or []:
                if rel.RelatingPort.FlowDirection == "SOURCE":
                    sources.append(
                        self.get_absolute_matrix(
                            ifcopenshell.util.placement.get_local_placement(rel.RelatingPort.ObjectPlacement)
                        )
                    )
                elif rel.RelatingPort.FlowDirection == "SINK":
                    sinks.append(
                        self.get_absolute_matrix(
                            ifcopenshell.util.placement.get_local_placement(rel.RelatingPort.ObjectPlacement)
                        )
                    )
                else:
                    sources.append(
                        self.get_absolute_matrix(
                            ifcopenshell.util.placement.get_local_placement(rel.RelatingPort.ObjectPlacement)
                        )
                    )
                    sinks.append(
                        self.get_absolute_matrix(
                            ifcopenshell.util.placement.get_local_placement(rel.RelatingPort.ObjectPlacement)
                        )
                    )
            for sink in sinks:
                for source in sources:
                    polyline = curve.data.splines.new("POLY")
                    polyline.points.add(1)
                    polyline.points[0].co = (Matrix(sink).translation * unit_scale).to_4d()
                    polyline.points[1].co = (Matrix(source).translation * unit_scale).to_4d()

    def get_absolute_matrix(self, matrix):
        props = bpy.context.scene.BIMGeoreferenceProperties
        if props.has_blender_offset:
            matrix = np.array(
                ifcopenshell.util.geolocation.global2local(
                    matrix,
                    float(props.blender_eastings),
                    float(props.blender_northings),
                    float(props.blender_orthogonal_height),
                    float(props.blender_x_axis_abscissa),
                    float(props.blender_x_axis_ordinate),
                )
            )
        return matrix
