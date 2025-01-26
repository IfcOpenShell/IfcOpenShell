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
import numpy as np
import ifcopenshell
import ifcopenshell.util.geolocation
import ifcopenshell.util.placement
import ifcopenshell.util.unit
import bonsai.tool as tool
import bonsai.core.misc as core
import bonsai.core.geometry as core_geometry
import bonsai.core.root
from mathutils import Vector, Matrix, Euler


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


class ResizeToStorey(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.resize_to_storey"
    bl_label = "Resize To Storey"
    bl_description = (
        "Change object's origin to the bottom, move object to it's storey elevation and scale object to storey height.\n"
        "Storey height is based on the provided number of storeys above object's storey.\n"
        "If object's storey is the last storey, operator will have no effect"
    )
    bl_options = {"REGISTER", "UNDO"}
    total_storeys: bpy.props.IntProperty()

    @classmethod
    def poll(cls, context):
        return context.selected_objects and tool.Ifc.get()

    def _execute(self, context):
        for obj in context.selected_objects:
            if not (element := tool.Ifc.get_entity(obj)):
                continue
            if element.HasOpenings:
                self.report({"ERROR"}, f"Object '{obj.name}', scaling is not supported.")
                continue
            core.resize_to_storey(tool.Misc, tool.Ifc, obj=obj, total_storeys=self.total_storeys)


class SplitAlongEdge(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.split_along_edge"
    bl_label = "Split Along Edge"
    bl_description = (
        "Active object is considered to be a cutting object."
        "Will unassign element from a type if type has a representation."
    )
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.selected_objects and tool.Ifc.get()

    def _execute(self, context):
        cutter = context.active_object
        objs = [o for o in context.selected_objects if o != cutter]

        objs_to_cut = []
        # Splitting only works on meshes
        for obj in objs:
            # You cannot split meshes if the representation is mapped.
            element = tool.Ifc.get_entity(obj)
            if not element:
                continue

            relating_type = tool.Root.get_element_type(element)
            if relating_type and tool.Root.does_type_have_representations(relating_type):
                bpy.ops.bim.unassign_type(related_object=obj.name)

            # refresh representation
            representation = tool.Geometry.get_active_representation(obj)

            # skip empty objects that might get in the way
            if not representation:
                continue

            core_geometry.switch_representation(
                tool.Ifc,
                tool.Geometry,
                obj=obj,
                representation=representation,
                should_reload=True,
                is_global=True,
                should_sync_changes_first=False,
                apply_openings=False,
            )

            if not tool.Geometry.is_meshlike(representation):
                bpy.ops.bim.update_representation(obj=obj.name, ifc_representation_class="IfcTessellatedFaceSet")

            objs_to_cut.append(obj)

        new_objs = tool.Misc.split_objects_with_cutter(objs_to_cut, cutter)
        for obj in new_objs:
            bonsai.core.root.copy_class(tool.Ifc, tool.Collector, tool.Geometry, tool.Root, obj=obj)
            bpy.ops.bim.update_representation(obj=obj.name)
        for obj in objs_to_cut:
            bpy.ops.bim.update_representation(obj=obj.name)

            representation = tool.Geometry.get_active_representation(obj)
            core_geometry.switch_representation(
                tool.Ifc,
                tool.Geometry,
                obj=obj,
                representation=representation,
                should_reload=True,
                is_global=True,
                should_sync_changes_first=False,
                apply_openings=True,
            )

        self.report({"INFO"}, f"Splitting finished, {len(new_objs)} new objects created.")


class GetConnectedSystemElements(bpy.types.Operator, tool.Ifc.Operator):
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


class DrawSystemArrows(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.draw_system_arrows"
    bl_label = "Draw System Arrows"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.selected_objects and tool.Ifc.get()

    def _execute(self, context):
        sinks = []
        sources = []

        for obj in bpy.context.selected_objects:
            if not obj.BIMObjectProperties.ifc_definition_id:
                continue

            element = tool.Ifc.get_entity(obj)
            sources_current = []
            sinks_current = []

            for port in tool.System.get_ports(element):
                local_placement = ifcopenshell.util.placement.get_local_placement(port.ObjectPlacement)
                m = self.get_absolute_matrix(local_placement)
                if port.FlowDirection == "SOURCE":
                    sources_current.append(m)
                elif port.FlowDirection == "SINK":
                    sinks_current.append(m)
                else:
                    sources_current.append(m)
                    sinks_current.append(m)

                if sinks_current or sources_current:
                    sinks.append(sinks_current)
                    sources.append(sources_current)

        if not sinks:
            self.report({"INFO"}, "No sinks/sources found for selected objects.")
            return {"FINISHED"}

        unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
        curve = bpy.data.objects.new("System Arrows", bpy.data.curves.new("System Arrows", "CURVE"))
        curve.data.dimensions = "3D"
        curve.show_in_front = True
        context.scene.collection.objects.link(curve)

        for i in range(len(sinks)):
            for sink in sinks[i]:
                for source in sources[i]:
                    polyline = curve.data.splines.new("POLY")
                    polyline.points.add(1)
                    polyline.points[0].co = (Matrix(sink).translation * unit_scale).to_4d()
                    polyline.points[1].co = (Matrix(source).translation * unit_scale).to_4d()
        tool.Blender.select_and_activate_single_object(context, curve)

    def get_absolute_matrix(self, matrix):
        props = bpy.context.scene.BIMGeoreferenceProperties
        if props.has_blender_offset:
            matrix = np.array(
                ifcopenshell.util.geolocation.global2local(
                    matrix,
                    float(props.blender_offset_x),
                    float(props.blender_offset_y),
                    float(props.blender_offset_z),
                    float(props.blender_x_axis_abscissa),
                    float(props.blender_x_axis_ordinate),
                )
            )
        return matrix
