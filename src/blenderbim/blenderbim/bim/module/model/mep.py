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
from math import pi, degrees
from mathutils import Vector, Matrix
import re
from blenderbim.bim.module.model.profile import DumbProfileJoiner

V = lambda *x: Vector([float(i) for i in x])
float_is_zero = lambda f: 0.0001 >= f >= -0.0001


class FitFlowSegments(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.fit_flow_segments"
    bl_label = "Fit Flow Segments"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        selected_objs = []
        selected_profiles = []

        selected_class = None
        for obj in context.selected_objects:
            element = tool.Ifc.get_entity(obj)
            if element and element.is_a("IfcFlowSegment"):
                if selected_class and not element.is_a(selected_class):
                    return  # The user is mixing up ducts and pipes.
                profile = tool.Model.get_flow_segment_profile(element)
                if profile:
                    selected_profiles.append(profile)
                    selected_objs.append(obj)
                    selected_class = element.is_a()

        total_selected_objs = len(selected_objs)
        total_profiles = len(set(selected_profiles))
        fitting_type = None

        if total_selected_objs == 1:
            fitting_type = "OBSTRUCTION"
            bpy.ops.bim.mep_add_obstruction()

        elif total_selected_objs == 2:
            # Shorten the axis by the profile size to allow for fuzzy intersections
            # e.g. if two ducts touch, we want a bend, not a cross.

            axis1 = tool.Model.get_flow_segment_axis(selected_objs[0])
            profile_size = max(selected_objs[0].dimensions.x, selected_objs[0].dimensions.y)
            offset = (axis1[1] - axis1[0]).normalized() * profile_size
            axis1 = (axis1[0] + offset, axis1[1] - offset)

            axis2 = tool.Model.get_flow_segment_axis(selected_objs[1])
            profile_size = max(selected_objs[1].dimensions.x, selected_objs[1].dimensions.y)
            offset = (axis2[1] - axis2[0]).normalized() * profile_size
            axis2 = (axis2[0] + offset, axis2[1] - offset)

            angle = tool.Cad.angle_edges(axis1, axis2, signed=False, degrees=True)
            is_parallel = tool.Cad.is_x(angle, (0, 180), tolerance=0.001)

            if total_profiles == 1:
                if is_parallel:
                    return
                intersect1, intersect2 = tool.Cad.intersect_edges(axis1, axis2)
                is_on_axis1 = tool.Cad.is_point_on_edge(intersect1, axis1)
                is_on_axis2 = tool.Cad.is_point_on_edge(intersect2, axis2)
                if not is_on_axis1 and not is_on_axis2:
                    fitting_type = "BEND"
                elif is_on_axis1 and is_on_axis2:
                    fitting_type = "CROSS"
                else:
                    fitting_type = "TEE"
            elif total_profiles == 2:
                if is_parallel:
                    fitting_type = "TRANSITION"

        elif total_selected_objs == 3:
            if total_profiles > 1:
                return

            axis1 = tool.Model.get_flow_segment_axis(selected_objs[0])
            axis2 = tool.Model.get_flow_segment_axis(selected_objs[1])
            axis3 = tool.Model.get_flow_segment_axis(selected_objs[2])

            angle12 = tool.Cad.angle_edges(axis1, axis2, signed=False, degrees=True)
            angle13 = tool.Cad.angle_edges(axis1, axis3, signed=False, degrees=True)
            angle21 = tool.Cad.angle_edges(axis2, axis1, signed=False, degrees=True)
            angle23 = tool.Cad.angle_edges(axis2, axis3, signed=False, degrees=True)
            is_parallel12 = tool.Cad.is_x(angle12, (0, 180), tolerance=0.001)
            is_parallel13 = tool.Cad.is_x(angle13, (0, 180), tolerance=0.001)
            is_parallel21 = tool.Cad.is_x(angle21, (0, 180), tolerance=0.001)
            is_parallel23 = tool.Cad.is_x(angle23, (0, 180), tolerance=0.001)

            if not all(is_parallel12, is_parallel13, is_parallel21, is_parallel23):
                fitting_type = "WYE"

        if not fitting_type:
            return

        print(fitting_type)


class MEPGenerator:
    def __init__(self, relating_type=None):
        self.relating_type = relating_type

    def setup_ports(self, obj):
        self.file = tool.Ifc.get()
        self.collection = bpy.context.view_layer.active_layer_collection.collection

        element = tool.Ifc.get_entity(obj)
        representation = ifcopenshell.util.representation.get_representation(element, "Model", "Body", "MODEL_VIEW")
        extrusion = tool.Model.get_extrusion(representation)
        si_conversion = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
        length = extrusion.Depth * si_conversion
        end_port_matrix = Matrix.Translation((0, 0, length))

        ports = tool.System.get_ports(element)
        if not ports:
            start_port_matrix = Matrix()
            for mat in [start_port_matrix, end_port_matrix]:
                port = tool.Ifc.run("system.add_port", element=element)
                port.FlowDirection = "NOTDEFINED"
                tool.Ifc.run("geometry.edit_object_placement", product=port, matrix=obj.matrix_world @ mat, is_si=True)
            return

        end_port = self.get_segment_data(element)["end_port"]
        tool.Model.edit_element_placement(end_port, obj.matrix_world @ end_port_matrix)

    def get_segment_data(self, segment):
        ports = tool.System.get_ports(segment)
        segment_object = tool.Ifc.get_object(segment)
        start_point = segment_object.location
        extrusion_depth = segment_object.dimensions.z
        end_point = segment_object.matrix_world @ V(0, 0, extrusion_depth)
        segment_data = {
            "start_point": start_point,
            "end_point": end_point,
            "ports": ports,
            "extrusion_depth": extrusion_depth,
        }

        for port in ports:
            port_local_position = V(*port.ObjectPlacement.RelativePlacement.Location.Coordinates)
            if float_is_zero(port_local_position.length):
                segment_data["start_port"] = port
            else:
                segment_data["end_port"] = port

        return segment_data

    def get_mep_element_class_name(self, element, mep_class_type):
        split_camel_case = lambda x: re.findall("[A-Z][^A-Z]*", x)
        class_name = "".join(split_camel_case(element.is_a())[:2] + [mep_class_type])
        return class_name

    def get_compatible_fitting_type(self, segment, predefined_type):
        """We find compatible fitting only by checking if they were
        already used with that segment type before.

        There lies the problem that it won't be
        able to identify the fittings that were not connected to any segments yet.
        """
        segment_type = ifcopenshell.util.element.get_type(segment)
        if not segment_type:
            return None

        fitting_types = tool.Ifc.get().by_type(self.get_mep_element_class_name(segment, "Fitting"))
        for fitting_type in fitting_types:
            if fitting_type.PredefinedType != predefined_type:
                continue
            fittings = tool.Ifc.get_all_element_occurences(fitting_type)
            if not fittings:
                continue
            fitting = fittings[0]
            elements = set(
                ifcopenshell.util.system.get_connected_to(fitting)
                + ifcopenshell.util.system.get_connected_from(fitting)
            )
            for element in elements:
                if element.IsTypedBy and element.IsTypedBy[0].RelatingType == segment_type:
                    return fitting_type

    def create_obstruction_type(self, segment):
        # code is very similar to "bim.add_type"
        profile_set = ifcopenshell.util.element.get_material(segment, should_skip_usage=True)
        material_profile = profile_set.MaterialProfiles[0]
        profile = material_profile.Profile
        material = material_profile.Material
        ifc_class = self.get_mep_element_class_name(segment, "FittingType")
        ifc_file = tool.Ifc.get()
        body = ifcopenshell.util.representation.get_context(ifc_file, "Model", "Body", "MODEL_VIEW")

        obj = bpy.data.objects.new("Fitting", None)
        element = blenderbim.core.root.assign_class(
            tool.Ifc,
            tool.Collector,
            tool.Root,
            obj=obj,
            ifc_class=ifc_class,
            predefined_type="OBSTRUCTION",
            should_add_representation=True,
            context=body,
            ifc_representation_class=None,
        )

        rel = ifcopenshell.api.run("material.assign_material", ifc_file, product=element, type="IfcMaterialProfileSet")
        profile_set = rel.RelatingMaterial
        material_profile = ifcopenshell.api.run(
            "material.add_profile", ifc_file, profile_set=profile_set, material=material
        )
        ifcopenshell.api.run("material.assign_profile", ifc_file, material_profile=material_profile, profile=profile)
        return element

    def add_obstruction(self, segment, length, at_segment_start=False):
        """
        `segment` is a segment ifc element

        `length` is obstruction length provided in si units

        returns `(None, error_message)` if there was some error in the process
        or returns `(obstruction_element, None)` if everything went fine.
        """

        related_port_name = "start" if at_segment_start else "end"
        segment_data = self.get_segment_data(segment)
        related_port = segment_data[f"{related_port_name}_port"]

        # communicate error cases
        if related_port.ConnectedTo or related_port.ConnectedFrom:
            return None, f"Failed to add obstruction - {related_port_name} port is already connected."
        if length >= segment_data["extrusion_depth"]:
            return None, "Failed to add obstruction - obstruction length is larger than the segment."

        segment_obj = tool.Ifc.get_object(segment)
        segment_matrix = segment_obj.matrix_world
        segment_rotation = segment_matrix.to_quaternion()
        obstruction_type = self.get_compatible_fitting_type(segment, "OBSTRUCTION")
        if not obstruction_type:
            obstruction_type = self.create_obstruction_type(segment)

        profile_joiner = DumbProfileJoiner()
        # create obstruction occurence and setup it's length and port
        # NOTE: at this point we loose current blender objects selection
        bpy.ops.bim.add_constr_type_instance(relating_type_id=obstruction_type.id())
        obstruction_obj = bpy.context.active_object
        obstruction_obj.matrix_world = segment_matrix

        profile_joiner.set_depth(obstruction_obj, length)
        obstruction = tool.Ifc.get_entity(obstruction_obj)
        obstruction_port = tool.Ifc.run("system.add_port", element=obstruction)
        port_local_position = Matrix.Translation((0, 0, length)) if at_segment_start else Matrix()
        tool.Ifc.run(
            "geometry.edit_object_placement",
            product=obstruction_port,
            matrix=segment_matrix @ port_local_position,
            is_si=True,
        )

        # change segment length
        new_segment_length = segment_data["extrusion_depth"] - length
        profile_joiner.set_depth(segment_obj, new_segment_length)

        if at_segment_start:
            segment_obj.location += segment_rotation @ V(0, 0, length)
        else:
            obstruction_obj.location += segment_rotation @ V(0, 0, new_segment_length)

        tool.Ifc.run("system.connect_port", port1=related_port, port2=obstruction_port, direction="NOTDEFINED")
        return obstruction, None


class MEPAddObstruction(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.mep_add_obstruction"
    bl_label = "Add Obstruction"
    bl_description = "Adds obstruction to the MEP segment"
    bl_options = {"REGISTER", "UNDO"}
    length: bpy.props.FloatProperty(
        name="Obstruction Length", description="Obstruction length in SI units", default=0.1, subtype="DISTANCE"
    )
    segment_id: bpy.props.IntProperty(name="Segment Element ID", default=0)

    def _execute(self, context):
        if self.segment_id:
            element = tool.Ifc.get().by_id(self.segment_id)
        else:
            element = tool.Ifc.get_entity(context.active_object)
        if not element:
            return {"CANCELLED"}

        if not element.is_a("IfcFlowSegment"):
            self.report({"ERROR"}, f"Failed to add obstruction - object is not a MEP segment: {element.is_a()}.")
            return {"CANCELLED"}

        # derive obstruction position from the cursor
        cursor_location = bpy.context.scene.cursor.location
        obj = tool.Ifc.get_object(element)
        axis = tool.Model.get_flow_segment_axis(obj)
        # check if cursor is closer to the segment start
        at_segment_start = (axis[0] - cursor_location).length < (axis[1] - cursor_location).length

        obstruction, error_msg = MEPGenerator().add_obstruction(element, self.length, at_segment_start)
        if error_msg:
            self.report({"ERROR"}, error_msg)
            return {"CANCELLED"}

        return {"FINISHED"}
