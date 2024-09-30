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
import collections
import bmesh
import re
import json
import ifcopenshell
import ifcopenshell.api
import ifcopenshell.util.unit
import ifcopenshell.util.system
import ifcopenshell.util.element
import ifcopenshell.util.representation
import numpy as np
import bonsai.core.type
import bonsai.core.root
import bonsai.core.geometry
import bonsai.tool as tool
from math import pi, degrees, radians, sin, cos, asin, tan
from copy import copy
from mathutils import Vector, Matrix
from ifcopenshell.util.shape_builder import ShapeBuilder
from bonsai.bim.module.model.profile import DumbProfileJoiner
from bonsai.tool.cad import VTX_PRECISION

V = lambda *x: Vector([float(i) for i in x])


class RegenerateDistributionElement(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.regenerate_distribution_element"
    bl_description = (
        "Regenerates the positions and segment lengths of a distribution element and all connected elements.\n"
        "Will try to adjust as less elements as possible, never rotate them. Segments will also try to change their length to fit"
    )
    bl_label = "Regenerate Distribution Element"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        current_element = tool.Ifc.get_entity(bpy.context.active_object)
        processed_elements = set()

        # The goal is to regenerate all recursively connected elements that
        # minimise movement as much as possible.

        # A queue is a list of branches. A branch is a list of elements in
        # sequence, each one connecting to another element. An element in a
        # branch may have a child queue. The queue and child queues are
        # acyclic.

        def extend_branch(element, branch, predecessor=None):
            processed_elements.add(element)
            branch_element = {"element": element, "children": [], "predecessor": predecessor}
            branch.append(branch_element)

            connected = {e for e in ifcopenshell.util.system.get_connected_to(element) if e not in processed_elements}
            connected.update(
                [e for e in ifcopenshell.util.system.get_connected_from(element) if e not in processed_elements]
            )

            for connected_element in connected:
                branch_element["children"].append(extend_branch(connected_element, [], element))

            return branch

        extended_branch = extend_branch(current_element, [])
        queue = extended_branch[0]["children"]

        # import pprint
        # pprint.pprint(queue)

        def get_connected_ports_between(element1, element2):
            ports1 = tool.System.get_ports(element1)
            ports2 = tool.System.get_ports(element2)

            for p in ports1:
                connected_port = tool.System.get_connected_port(p)
                # in IFC2X3 there is no PredefinedType
                if getattr(p, "PredefinedType", None) == "WIRELESS":
                    continue
                if connected_port in ports2:
                    return p, connected_port

            return None, None

        si_conversion = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())

        def process_branch(branch):
            for branch_element in branch:
                element = branch_element["element"]
                print("processing", element)
                predecessor = branch_element["predecessor"]

                # Perform the extend, translate, rotate, etc the element as necessary based on the predecessor.
                # For everything besides segments, only translate. No rotation.

                obj = tool.Ifc.get_object(element)
                obj_pred = tool.Ifc.get_object(predecessor)
                tool.Model.sync_object_ifc_position(obj)
                tool.Model.sync_object_ifc_position(obj_pred)

                port, port_pred = get_connected_ports_between(element, predecessor)
                port_matrix_pred = tool.Model.get_element_matrix(port_pred)

                # Only segments can be extended
                # extension for them takes priority over translation
                if element.is_a("IfcFlowSegment"):
                    DumbProfileJoiner().join_E(obj, port_matrix_pred.translation * si_conversion)
                    context.view_layer.update()  # update since extrusion might involve changing object's location

                port_martix = tool.Model.get_element_matrix(port)
                port_location = port_martix.translation
                port_location_pred = port_matrix_pred.translation
                if not tool.Cad.are_vectors_equal(port_location, port_location_pred):
                    obj.location += (port_location_pred - port_location) * si_conversion
                    context.view_layer.update()  # otherwise tool.Ifc.is_moved won't get triggered
                else:
                    # If the element does not need to be transformed, return early.
                    return

                for child_branch in branch_element["children"]:
                    process_branch(child_branch)

        for branch in queue:
            process_branch(branch)


class FitFlowSegments(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.fit_flow_segments"
    bl_description = "Add a fitting based on currently selected elements and cursor"
    bl_label = "Fit Flow Segments"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        # TODO: need to add ui for parameters:
        # - obstruction cap thickness
        # - start/end thickness and angle for transition
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
                    bpy.ops.bim.mep_add_bend()
                elif is_on_axis1 and is_on_axis2:
                    fitting_type = "CROSS"
                else:
                    fitting_type = "TEE"
            elif total_profiles == 2:
                if is_parallel:
                    fitting_type = "TRANSITION"
                    bpy.ops.bim.mep_add_transition()

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

        segment = tool.Ifc.get_entity(obj)
        representation = ifcopenshell.util.representation.get_representation(segment, "Model", "Body", "MODEL_VIEW")
        extrusion = tool.Model.get_extrusion(representation)
        si_conversion = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
        length = extrusion.Depth * si_conversion
        start_port_matrix = obj.matrix_world @ Matrix()
        end_port_matrix = obj.matrix_world @ Matrix.Translation((0, 0, length))

        ports = tool.System.get_ports(segment)
        if segment.is_a("IfcFlowSegment") and not ports:
            tool.System.add_ports(obj)
            return

        # adjust current segment ports and related flow segments
        segment_data = self.get_segment_data(segment)

        for port_position in ("start_port", "end_port"):
            port = segment_data.get(port_position, None)
            if not port:
                continue

            # no need to correct start port position - it's corrected automatically
            # as DumbProfileJoiner already moved the general segment position in that case
            if port_position == "end_port":
                tool.Model.edit_element_placement(port, end_port_matrix)

            continue

            # NOTE: currently this functionality is moved to bim.regenerate_distribution_element

            connected_port = tool.System.get_connected_port(port)
            if not connected_port:
                continue

            # handle only obstructions for now
            connected_element = tool.System.get_port_relating_element(connected_port)

            def get_predefined_type(element):
                element_type = ifcopenshell.util.element.get_type(element)
                if element_type:
                    return element_type.PredefinedType
                return element.PredefinedType

            connected_obj = tool.Ifc.get_object(connected_element)
            connected_element_length = connected_obj.dimensions.z
            if (segment.is_a("IfcFlowSegment") and get_predefined_type(connected_element) == "OBSTRUCTION") or (
                segment.is_a("IfcFlowFitting") and connected_element.is_a("IfcFlowSegment")
            ):
                if port_position == "start_port":
                    if segment.is_a("IfcFlowFitting"):
                        connected_element_length = (
                            tool.Model.get_flow_segment_axis(connected_obj)[0]
                            - tool.Model.get_flow_segment_axis(obj)[0]
                        ).length

                    connected_port_matrix = start_port_matrix @ Matrix.Translation((0, 0, -connected_element_length))
                else:
                    connected_port_matrix = end_port_matrix
                connected_obj.matrix_world = connected_port_matrix
                if port_position == "start_port" and segment.is_a("IfcFlowFitting"):
                    profile_joiner = DumbProfileJoiner()
                    profile_joiner.set_depth(connected_obj, connected_element_length)

    def get_segment_data(self, segment):
        """returns points data is in world space"""
        ports = tool.System.get_ports(segment)
        segment_object = tool.Ifc.get_object(segment)
        start_point = segment_object.location
        extrusion_depth = segment_object.dimensions.z
        end_point = segment_object.matrix_world @ V(0, 0, extrusion_depth)
        segment_data = {
            "start_point": start_point.copy().freeze(),
            "end_point": end_point.freeze(),
            "ports": ports,
            "extrusion_depth": extrusion_depth,
        }

        for port in ports:
            port_local_position = V(*port.ObjectPlacement.RelativePlacement.Location.Coordinates)
            if tool.Cad.is_x(port_local_position.length, 0.0):
                segment_data["start_port"] = port
            else:
                segment_data["end_port"] = port

        return segment_data

    def get_mep_element_class_name(self, element, mep_class_type):
        split_camel_case = lambda x: re.findall("[A-Z][^A-Z]*", x)
        class_name = "".join(split_camel_case(element.is_a())[:-1] + [mep_class_type])
        return class_name

    def get_compatible_fitting_type(self, segment_or_segments, port_or_ports, predefined_type, bbim_data=None):
        """
        returns a dict of compatible fitting_type and start_port_match flag to correctly place the fitting.

        We find compatible fitting only by checking
        if they were already used with that segment type before
        and fitting's ports should match `port_or_ports` by PredefinedType and SystemType.

        If port from `port_or_ports` has PredefinedType/SystemType == None/NOTDEFINED then
        those parameters won't be taken into account checking compatibility.

        There lies the problem that it won't be
        able to identify the fittings that were not yet connected to any segments yet.


        `bbim_data` is used to find compatible fitting build with BBIM parametrically (BBIM_Fitting pset).
        All data in `bbim_data` supposed to be in project units.
        """

        if not isinstance(segment_or_segments, collections.abc.Iterable):
            segments = [segment_or_segments]
            ports = [port_or_ports]
        else:
            segments = segment_or_segments
            ports = port_or_ports

        ifc_file = tool.Ifc.get()
        si_conversion = ifcopenshell.util.unit.calculate_unit_scale(ifc_file)
        precision = VTX_PRECISION / si_conversion
        angle_precision = degrees(precision)
        start_port_match = True

        segments_data = []
        for segment, port in zip(segments, ports, strict=True):
            segment_type = ifcopenshell.util.element.get_type(segment)
            # if segment doesn't have type we cannot check compatibility by available occurrences
            if segment_type is None:
                return
            segments_data.append((segment_type, port.PredefinedType, port.SystemType))

        def compatible_with_bbim_data(fitting_type):
            nonlocal start_port_match
            start_port_match = True
            if not bbim_data:
                return True
            fitting_type_obj = tool.Ifc.get_object(fitting_type)
            fitting_bbim_data = tool.Model.get_modeling_bbim_pset_data(fitting_type_obj, "BBIM_Fitting")
            if not fitting_bbim_data:
                return False

            fitting_bbim_data = fitting_bbim_data["data_dict"]

            def compare_value(key, second_key=None):
                second_key = second_key or key
                requested_value = bbim_data[key]
                fitting_value = fitting_bbim_data[second_key]

                if isinstance(requested_value, float):
                    compare_precision = angle_precision if key == "angle" else precision
                    compare = tool.Cad.is_x(requested_value, fitting_value, compare_precision)
                elif isinstance(fitting_value, list):
                    compare = tool.Cad.are_vectors_equal(requested_value, Vector(fitting_value), precision)
                return compare

            ignore_keys = []
            if predefined_type == "BEND":
                ignore_keys.extend(("start_length", "end_length"))
                # for bends there is a special case when lengths might not match
                # but fitting is still compatible if we flip it
                # since bend connects segments of the same type
                default_lengths_match = compare_value("start_length") and compare_value("end_length")
                if not default_lengths_match:
                    switched_lengths_match = compare_value("start_length", "end_length") and compare_value(
                        "end_length", "start_length"
                    )
                    if switched_lengths_match:
                        start_port_match = False
                    else:
                        return False

            for key in bbim_data:
                if key in ignore_keys:
                    continue
                if not compare_value(key):
                    return False
            return True

        def are_connected_elements_compatible(segments_data, fitting_data):
            # prevent arguments mutation, not using deepcopy because of the errors with ifc elements
            segments_data = [copy(i) for i in segments_data]
            fitting_data = [copy(i) for i in fitting_data]
            not_defined_values = {"NOTDEFINED", None}

            if len(segments_data) != len(fitting_data):
                return False

            def are_segments_compatible(test_segment_data, base_segment_data):
                segment_type, predefined_type, system_type = test_segment_data
                base_segment_type, base_predefined_type, base_system_type = base_segment_data

                if segment_type != base_segment_type:
                    return False

                if predefined_type not in not_defined_values and predefined_type != base_predefined_type:
                    return False

                if system_type not in not_defined_values and system_type != base_system_type:
                    return False

                return True

            # NOTE: I have a feeling that there are cases where order
            # in which we're checking the segments is important
            # but I couldn't pin it down to exact cases
            for test_segment_data in fitting_data:
                for base_segment_data in segments_data:
                    if not are_segments_compatible(test_segment_data, base_segment_data):
                        continue
                    segments_data.remove(base_segment_data)
                    break

            # all segments were sorted
            return len(segments_data) == 0

        def pack_return_data(fitting_type, ports, segments_data):
            packed_data = {"fitting_type": fitting_type}

            if predefined_type == "OBSTRUCTION":
                return packed_data

            for port in ports:
                port_local_position = V(*port.ObjectPlacement.RelativePlacement.Location.Coordinates)
                if tool.Cad.is_x(port_local_position.length, 0.0):
                    start_port = port
                    break

            connected_port = tool.System.get_connected_port(start_port)
            connected_element = tool.System.get_port_relating_element(connected_port)
            element_type = ifcopenshell.util.element.get_type(connected_element)
            packed_data["start_port_match"] = element_type == segments_data[0][0] and start_port_match

            return packed_data

        fitting_types = tool.Ifc.get().by_type(self.get_mep_element_class_name(segments[0], "FittingType"))
        for fitting_type in fitting_types:
            if fitting_type.PredefinedType != predefined_type:
                continue
            fittings = tool.Ifc.get_all_element_occurrences(fitting_type)
            if not fittings:
                continue

            for fitting in fittings:
                ports = ifcopenshell.util.system.get_ports(fitting)
                fitting_data = []
                skipped_the_occurrence = False
                for port in ports:
                    connected_port = tool.System.get_connected_port(port)

                    # fitting port is not connected to anything
                    if not connected_port:
                        skipped_the_occurrence = True
                        break

                    connected_element = tool.System.get_port_relating_element(connected_port)
                    element_type = ifcopenshell.util.element.get_type(connected_element)

                    # fitting is connected to none type
                    if element_type is None:
                        skipped_the_occurrence = True
                        break

                    fitting_data.append((element_type, port.PredefinedType, port.SystemType))

                # if we skipped the occurrence we still need to check other occurrences
                # otherwise checking 1 occurrence is enough
                if not skipped_the_occurrence:
                    if compatible_with_bbim_data(fitting_type) and are_connected_elements_compatible(
                        segments_data, fitting_data
                    ):
                        return pack_return_data(fitting_type, ports, segments_data)
                    break

    def create_obstruction_type(self, segment):
        # code is very similar to "bim.add_element"
        profile_set = ifcopenshell.util.element.get_material(segment, should_skip_usage=True)
        material_profile = profile_set.MaterialProfiles[0]
        profile = material_profile.Profile
        material = material_profile.Material
        ifc_class = self.get_mep_element_class_name(segment, "FittingType")
        ifc_file = tool.Ifc.get()
        body = ifcopenshell.util.representation.get_context(ifc_file, "Model", "Body", "MODEL_VIEW")

        obj = bpy.data.objects.new("Obstruction", None)
        # TODO: OBSTRUCTION predefined type is available only for IfcDuctFitting and IfcPipeFitting
        element = bonsai.core.root.assign_class(
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

        rel = ifcopenshell.api.run(
            "material.assign_material", ifc_file, products=[element], type="IfcMaterialProfileSet"
        )
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
        fitting_data = self.get_compatible_fitting_type(segment, related_port, "OBSTRUCTION")
        obstruction_type = fitting_data["fitting_type"] if fitting_data else None
        if not obstruction_type:
            obstruction_type = self.create_obstruction_type(segment)

        profile_joiner = DumbProfileJoiner()
        # create obstruction occurrence and setup it's length and port
        # NOTE: at this point we loose current blender objects selection
        bpy.ops.bim.add_constr_type_instance(relating_type_id=obstruction_type.id())
        obstruction_obj = bpy.context.active_object
        obstruction_obj.matrix_world = segment_matrix

        profile_joiner.set_depth(obstruction_obj, length)
        # NOTE: we add ports to the obstruction occurence and not to the type
        # since it's material profile based like segments
        obstruction_port = tool.System.add_ports(
            obstruction_obj,
            add_start_port=not at_segment_start,
            add_end_port=at_segment_start,
        )[0]

        # change segment length
        new_segment_length = segment_data["extrusion_depth"] - length
        profile_joiner.set_depth(segment_obj, new_segment_length)

        if at_segment_start:
            segment_obj.location += segment_rotation @ V(0, 0, length)
        else:
            obstruction_obj.location += segment_rotation @ V(0, 0, new_segment_length)

        tool.Ifc.run("system.connect_port", port1=related_port, port2=obstruction_port, direction="NOTDEFINED")
        obstruction = tool.Ifc.get_entity(obstruction_obj)
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
        at_segment_start = tool.Cad.edge_percent(cursor_location, axis) < 0.5

        obstruction, error_msg = MEPGenerator().add_obstruction(element, self.length, at_segment_start)
        if error_msg:
            self.report({"ERROR"}, error_msg)
            return {"CANCELLED"}

        return {"FINISHED"}


class MEPAddTransition(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.mep_add_transition"
    bl_label = "Add Transition"
    bl_description = "Adds transition between two selected MEP Elements"
    bl_options = {"REGISTER", "UNDO"}
    start_length: bpy.props.FloatProperty(
        name="Start Length", description="Transition start length in SI units", default=0.1, subtype="DISTANCE", min=0
    )
    end_length: bpy.props.FloatProperty(
        name="End Length", description="Transition end length in SI units", default=0.1, subtype="DISTANCE", min=0
    )
    angle: bpy.props.FloatProperty(
        name="Transition Angle", description="Transition angle in degrees", default=pi / 6, subtype="ANGLE", min=0
    )
    start_segment_id: bpy.props.IntProperty(name="Start Segment Element ID", default=0)
    end_segment_id: bpy.props.IntProperty(name="End Segment Element ID", default=0)

    def _execute(self, context):
        start_element, end_element = None, None
        ifc_file = tool.Ifc.get()
        si_conversion = ifcopenshell.util.unit.calculate_unit_scale(ifc_file)

        if self.start_segment_id and self.end_segment_id:
            start_element = ifc_file.by_id(self.start_segment_id)
            end_element = ifc_file.by_id(self.end_segment_id)
            start_object = tool.Ifc.get_object(start_element)
            end_object = tool.Ifc.get_object(end_element)

        elif len(context.selected_objects) == 2:
            start_object = context.active_object
            end_object = next(o for o in context.selected_objects if o != context.active_object)
            start_element = tool.Ifc.get_entity(start_object)
            end_element = tool.Ifc.get_entity(end_object)
            if not start_element or not end_element:
                self.report({"ERROR"}, f"Two IFC elements should be selected for the transition")
                return {"CANCELLED"}

        else:
            self.report({"ERROR"}, f"Two IFC elements should be provided for the transition")
            return {"CANCELLED"}

        # TODO: support IfcFlowTerminal
        def is_mep(element):
            return element.is_a("IfcFlowSegment") or element.is_a("IfcFlowFitting")

        if not is_mep(start_element) or not is_mep(end_element):
            self.report(
                {"ERROR"},
                f"Failed to add transition - some object is not a MEP element: {start_element.is_a()}, {end_element.is_a()}.",
            )
            return {"CANCELLED"}

        start_axis = tool.Model.get_flow_segment_axis(start_object)
        end_axis = tool.Model.get_flow_segment_axis(end_object)
        start_object_rotation = start_object.matrix_world.to_quaternion()
        start_object_z_basis = start_object_rotation.to_matrix().col[2]  # z basis vector
        keep_only_z_axis = lambda p_ws: p_ws.dot(start_object_z_basis) * start_object_z_basis

        if not tool.Cad.are_edges_parallel(start_axis, end_axis):
            self.report({"ERROR"}, f"Failed to add transition - segments are not parallel.")
            return {"CANCELLED"}

        # TODO: support different profiles rotation by local Z
        # check rotation difference
        end_object_rotation = end_object.matrix_world.to_quaternion()
        rotation_difference_z = (
            start_object.matrix_world.to_quaternion().rotation_difference(end_object_rotation).to_euler().z
        )

        def is_multiple_of_pi(value):
            n = round(value / pi)
            return tool.Cad.is_x(abs(value - n * pi), 0)

        if not is_multiple_of_pi(rotation_difference_z):
            self.report(
                {"ERROR"},
                "There is some rotation difference between profiles by local Z axis: "
                f"{round(degrees(rotation_difference_z))} deg, this kind of transition is not yet supported.",
            )
            return {"CANCELLED"}

        # setup start / end points
        start_segment_data = MEPGenerator().get_segment_data(start_element)
        end_segment_data = MEPGenerator().get_segment_data(end_element)
        points_ports_map = {
            start_segment_data["start_point"]: start_segment_data["start_port"],
            start_segment_data["end_point"]: start_segment_data["end_port"],
            end_segment_data["start_point"]: end_segment_data["start_port"],
            end_segment_data["end_point"]: end_segment_data["end_port"],
        }
        # transition points
        (start_point, end_point), (first_segment_start, second_segment_end) = tool.Cad.closest_points(
            (start_segment_data["start_point"], start_segment_data["end_point"]),
            (end_segment_data["start_point"], end_segment_data["end_point"]),
        )
        start_port = points_ports_map[start_point]
        end_port = points_ports_map[end_point]
        start_point_on_origin = start_point == start_segment_data["start_point"]
        start_connection = "ATSTART" if start_point_on_origin else "ATEND"
        start_segment_sign = -1 if start_point_on_origin else 1

        end_point_on_origin = end_point == end_segment_data["start_point"]
        end_connection = "ATSTART" if end_point_on_origin else "ATEND"

        # figure profile offset
        base_transition_dir = keep_only_z_axis(end_point - start_point).normalized()
        flip_profile_offset = base_transition_dir.dot(start_object_z_basis) < 0

        if tool.Cad.are_edges_collinear(start_axis, end_axis):
            profile_offset = V(0, 0)
        else:
            to_start_object_space = start_object_rotation.inverted()
            profile_offset = (
                (to_start_object_space @ end_object.location) - (to_start_object_space @ start_object.location)
            ).xy
            profile_offset = profile_offset / si_conversion
            if flip_profile_offset:
                profile_offset *= V(1, -1)

        # world space profile offset
        profile_offset_si = (profile_offset * si_conversion).to_3d()
        profile_offset_ws = start_object_rotation @ profile_offset_si

        def get_segments_length():
            start_dir = (start_point - first_segment_start).normalized()
            segments_vector = second_segment_end - first_segment_start
            return segments_vector.dot(start_dir)

        entire_length = get_segments_length()

        # can't rely on (end_point-start_point) here because
        # transition might change the segments length and therefore direction will be changed
        segments_dir = (start_point - first_segment_start).normalized()

        # add transition representation
        builder = ShapeBuilder(ifc_file)
        rep, transition_data = builder.mep_transition_shape(
            start_element,
            end_element,
            self.start_length / si_conversion,
            self.end_length / si_conversion,
            angle=degrees(self.angle),
            profile_offset=profile_offset,
        )

        if not rep:
            self.report({"ERROR"}, f"Failed to add transition - this kind of profiles is not yet supported.")
            return {"CANCELLED"}

        full_transition_length = transition_data["full_transition_length"] * si_conversion
        if full_transition_length >= entire_length:
            self.report(
                {"ERROR"},
                f"Failed to add transition - transition length is larger the segments and the distance between them.\n"
                + f"Transition length: {full_transition_length:.2f}m, segments length: {entire_length:.2f}m",
            )
            ifcopenshell.api.run("geometry.remove_representation", ifc_file, representation=rep)
            return {"CANCELLED"}

        # calculate bunch of points to for adjustments
        middle_point = keep_only_z_axis((start_point + end_point) / 2 - start_point) + start_point
        start_segment_extend_point = middle_point - segments_dir * full_transition_length / 2
        end_segment_extend_point = middle_point + segments_dir * full_transition_length / 2 + profile_offset_ws
        transition_dir = keep_only_z_axis(end_segment_extend_point - start_segment_extend_point).normalized()

        # adjust the segments
        DumbProfileJoiner().join_E(start_object, start_segment_extend_point, start_connection)
        DumbProfileJoiner().join_E(end_object, end_segment_extend_point, end_connection)

        # For bbim transitions, there is small convention that:
        # - start_length segment positioned at the start of the transition's Z-axis.
        # - end_length segment positioned at the of it.
        # this is why we sort the lengths in parametric data too
        parametric_data = {
            "start_length": (self.start_length if start_segment_sign == 1 else self.end_length) / si_conversion,
            "end_length": (self.end_length if start_segment_sign == 1 else self.start_length) / si_conversion,
            "profile_offset": profile_offset,
            "angle": degrees(self.angle),
        }

        # find the compatible fitting type
        fitting_data = MEPGenerator().get_compatible_fitting_type(
            [start_element, end_element], [start_port, end_port], "TRANSITION", bbim_data=parametric_data
        )
        transition_type = fitting_data["fitting_type"] if fitting_data else None
        start_port_match = fitting_data["start_port_match"] if fitting_data else True
        if transition_type:
            # TODO: handle the case without creating a representation in the first place?
            ifcopenshell.api.run("geometry.remove_representation", ifc_file, representation=rep)
        else:  # create new fitting type if nothing is compatible
            mesh = bpy.data.meshes.new("Transition")
            obj = bpy.data.objects.new("Transition", mesh)
            transition_type = bonsai.core.root.assign_class(
                tool.Ifc,
                tool.Collector,
                tool.Root,
                obj=obj,
                ifc_class=MEPGenerator().get_mep_element_class_name(start_element, "FittingType"),
                predefined_type="TRANSITION",
                should_add_representation=False,
            )
            body = ifcopenshell.util.representation.get_context(ifc_file, "Model", "Body", "MODEL_VIEW")
            tool.Model.replace_object_ifc_representation(body, obj, rep)
            tool.Blender.remove_data_block(mesh)
            pset = ifcopenshell.api.run("pset.add_pset", tool.Ifc.get(), product=transition_type, name="BBIM_Fitting")
            ifcopenshell.api.run(
                "pset.edit_pset",
                tool.Ifc.get(),
                pset=pset,
                properties={"Data": tool.Ifc.get().createIfcText(json.dumps(transition_data, default=list))},
            )
            tool.System.add_ports(obj, offset_end_port=profile_offset_si)

        # NOTE: at this point we loose current blender objects selection
        # create transition element
        bpy.ops.bim.add_constr_type_instance(relating_type_id=transition_type.id())
        transition_obj = bpy.context.active_object

        # adjust transition segment rotation and location
        # required since we'll base our `transition_obj_dir` on this
        transition_obj.matrix_world = start_object.matrix_world
        context.view_layer.update()

        # depending on transition direction we may need to flip it or attach it's origin to end segment
        # direction can be different depending on:
        # - order of the current segments
        # - order of the segments that were used with the same transition type before
        transition_obj_dir = tool.Cad.get_edge_direction(tool.Model.get_flow_segment_axis(transition_obj))
        direction_match = tool.Cad.are_vectors_equal(transition_dir, transition_obj_dir)
        # if there are no mismatches or everything matches up we don't need to flip the transition
        if start_port_match != direction_match:
            transition_obj.matrix_world = start_object.matrix_world @ Matrix.Rotation(radians(180), 4, "X")
        transition_obj.location = start_segment_extend_point if start_port_match else end_segment_extend_point

        # add ports and connect them
        ports = tool.System.get_ports(tool.Ifc.get_entity(transition_obj))
        if not start_port_match:
            start_port, end_port = end_port, start_port
        tool.Ifc.run("system.connect_port", port1=ports[0], port2=start_port, direction="NOTDEFINED")
        tool.Ifc.run("system.connect_port", port1=ports[1], port2=end_port, direction="NOTDEFINED")
        return {"FINISHED"}


class MEPAddBend(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.mep_add_bend"
    bl_label = "Add Bend"
    bl_description = "Adds a bend between two selected MEP Elements"
    bl_options = {"REGISTER", "UNDO"}
    start_length: bpy.props.FloatProperty(
        name="Start Length", description="Bend start length in SI units", default=0.1, subtype="DISTANCE", min=0
    )
    end_length: bpy.props.FloatProperty(
        name="End Length", description="Bend end length in SI units", default=0.1, subtype="DISTANCE", min=0
    )
    start_segment_id: bpy.props.IntProperty(name="Start Segment Element ID", default=0)
    end_segment_id: bpy.props.IntProperty(name="End Segment Element ID", default=0)
    radius: bpy.props.FloatProperty(
        "Bend Inner Radius", description="Bend inner radius in SI units", default=0.2, subtype="DISTANCE", min=0
    )

    def _execute(self, context):
        start_element, end_element = None, None
        ifc_file = tool.Ifc.get()
        si_conversion = ifcopenshell.util.unit.calculate_unit_scale(ifc_file)

        if self.start_segment_id and self.end_segment_id:
            start_element = ifc_file.by_id(self.start_segment_id)
            end_element = ifc_file.by_id(self.end_segment_id)
            start_object = tool.Ifc.get_object(start_element)
            end_object = tool.Ifc.get_object(end_element)

        elif len(context.selected_objects) == 2:
            start_object = context.active_object
            end_object = next(o for o in context.selected_objects if o != context.active_object)
            start_element = tool.Ifc.get_entity(start_object)
            end_element = tool.Ifc.get_entity(end_object)
            if not start_element or not end_element:
                self.report({"ERROR"}, f"Two IFC elements should be selected for the bend.")
                return {"CANCELLED"}

        else:
            self.report({"ERROR"}, f"Two IFC elements should be provided for the bend.")
            return {"CANCELLED"}

        # check rotation difference
        def rotation_difference_check():
            end_object_rotation = end_object.matrix_world.to_quaternion()
            rotation_difference = (
                start_object.matrix_world.to_quaternion().rotation_difference(end_object_rotation).to_euler()
            )

            def is_multiple_of_pi(value):
                n = round(value / pi)
                return tool.Cad.is_x(abs(value - n * pi), 0)

            if not is_multiple_of_pi(rotation_difference.z):
                error_msg = (
                    "There is some rotation difference between profiles by local Z axis: "
                    f"{round(degrees(rotation_difference.z))} deg, adding a bend is not possible."
                )
                return error_msg

        if error_msg := rotation_difference_check():
            self.report({"ERROR"}, error_msg)
            return {"CANCELLED"}

        # check segments types
        def types_check():
            start_type = ifcopenshell.util.element.get_type(start_element)
            end_type = ifcopenshell.util.element.get_type(end_element)
            if not start_type or not end_type:
                return False
            return start_type == end_type

        if not types_check():
            self.report(
                {"ERROR"},
                "Segments types do not match or one of the segments doesn't have type which is required for a bend.",
            )
            return {"CANCELLED"}

        profile = tool.Model.get_flow_segment_profile(start_element)
        if not profile.is_a("IfcRectangleProfileDef") and not profile.is_a("IfcCircleProfileDef"):
            self.report(
                {"ERROR"},
                "For now Only IfcRectangleProfileDef/IfcCircleProfileDef profiles supported for a bend, "
                f"the segments are {profile.is_a()}",
            )
            return {"CANCELLED"}

        def get_dim(profile):
            if profile.is_a("IfcRectangleProfileDef"):
                return V(profile.XDim / 2, profile.YDim / 2)
            elif profile.is_a("IfcCircleProfileDef"):
                return V(profile.Radius, profile.Radius)
            return None

        # setup start / end points
        start_object_rotation = start_object.matrix_world.to_quaternion().to_matrix()
        start_segment_data = MEPGenerator().get_segment_data(start_element)
        end_segment_data = MEPGenerator().get_segment_data(end_element)
        # use id() to match by the exact vector objects and not by their values
        # since vectors position could match
        points_ports_map = {
            id(start_segment_data["start_point"]): start_segment_data["start_port"],
            id(start_segment_data["end_point"]): start_segment_data["end_port"],
            id(end_segment_data["start_point"]): end_segment_data["start_port"],
            id(end_segment_data["end_point"]): end_segment_data["end_port"],
        }

        get_z_basis = lambda o: tool.Cad.get_basis_vector(o, 2)
        segments_intersection_ws = tool.Cad.intersect_edges(
            (start_object.location, start_object.location + get_z_basis(start_object)),
            (end_object.location, end_object.location + get_z_basis(end_object)),
        )[0]

        start_point, first_segment_start = tool.Cad.closest_and_furthest_vectors(
            segments_intersection_ws, (start_segment_data["start_point"], start_segment_data["end_point"])
        )
        end_point, second_segment_end = tool.Cad.closest_and_furthest_vectors(
            segments_intersection_ws, (end_segment_data["start_point"], end_segment_data["end_point"])
        )

        # start_/end_segment_sign indicate
        # whether segments' z axes are directed towards the bend
        start_port = points_ports_map[id(start_point)]
        end_port = points_ports_map[id(end_point)]
        start_point_on_origin = start_point == start_segment_data["start_point"]
        start_connection = "ATSTART" if start_point_on_origin else "ATEND"
        start_segment_sign = -1 if start_point_on_origin else 1

        end_point_on_origin = end_point == end_segment_data["start_point"]
        end_connection = "ATSTART" if end_point_on_origin else "ATEND"
        end_segment_sign = -1 if end_point_on_origin else 1

        profile_dim = get_dim(profile) * si_conversion

        # TODO: profile offset may need to be flipped (check transition code)
        to_start_object_space = start_object_rotation.inverted()
        ref_point = end_point.copy()
        end_segment_dir = (second_segment_end - end_point).normalized()
        # we prioritize direction between end_point and start_point for bend_vector
        # if those point match we use general end segment direction
        if tool.Cad.is_x((end_point - start_point).length, 0):
            ref_point = end_point + end_segment_dir
        bend_vector = (to_start_object_space @ ref_point) - (to_start_object_space @ start_point)

        z_axis_end_object_local = to_start_object_space @ tool.Cad.get_basis_vector(end_object, 2)

        def check_for_double_bends():
            # The theory is To avoid double bends, the profile offset should occur along only two axes:
            # 1) The local Z-axis of the start segment
            # 2) One of the lateral axes (either X or Y)
            #
            # Double bend required when:
            # - there are 2 or 0 lateral axes involved
            # - offset appear by the non-lateral axis
            #
            # NOTE: some double bends are only possible for square profiles:
            # https://i.imgur.com/ZhdGbEp.png

            lateral_axes = [i for i in range(2) if not tool.Cad.is_x(z_axis_end_object_local[i], 0)]

            if len(lateral_axes) != 1:
                return (
                    None,
                    f"For now only one lateral axis is supported for a bend (double bends not supported). Found lateral axes: {len(lateral_axes)}.",
                )

            non_lateral_axis = 0 if lateral_axes[0] == 1 else 1
            non_lateral_axis_offset = bend_vector[non_lateral_axis]
            if not tool.Cad.is_x(non_lateral_axis_offset, 0):
                return (
                    None,
                    "For now offset by non-lateral axis is not supported for a bend (double bends not supported).\n"
                    f"Detected an offset of {round(non_lateral_axis_offset, 5)} along the local axis {'XY'[non_lateral_axis]} when lateral axis is {'XY'[lateral_axes[0]]}.",
                )

            return lateral_axes[0], None

        lateral_axis, error_msg = check_for_double_bends()
        if error_msg:
            self.report({"ERROR"}, error_msg)
            return {"CANCELLED"}
        non_lateral_axis = 0 if lateral_axis == 1 else 1

        def get_bend_rotation():
            O = V(0, 0, 0)
            edge1 = (get_z_basis(start_object) * start_segment_sign, O)
            edge2 = (get_z_basis(end_object) * end_segment_sign, O)
            angle = pi - tool.Cad.angle_edges(edge1, edge2)
            axis = (edge2[1] - edge2[0]).cross(edge1[1] - edge1[0])
            return angle, axis

        angle, rotation_axis = get_bend_rotation()

        lateral_sign = tool.Cad.sign(bend_vector[lateral_axis])
        radial_offset = V(0, 0, 0)
        ref_point_radius = self.radius + profile_dim[lateral_axis]
        radial_offset[lateral_axis] = ref_point_radius * (1 - cos(angle)) * lateral_sign
        radial_offset.z = ref_point_radius * sin(angle) * start_segment_sign
        end_port_offset = radial_offset + V(0, 0, self.start_length * start_segment_sign)
        end_port_offset += z_axis_end_object_local * (self.end_length * -end_segment_sign)

        def get_segments_extend_points():
            # since tangent segments are equal
            # if drawn for the circle from the same point
            required_offset = ref_point_radius * tan(angle / 2)

            start_segment_extend_point = segments_intersection_ws - start_segment_sign * (
                self.start_length + required_offset
            ) * get_z_basis(start_object)
            end_segment_extend_point = segments_intersection_ws - end_segment_sign * (
                self.end_length + required_offset
            ) * get_z_basis(end_object)

            return start_segment_extend_point, end_segment_extend_point

        def check_new_segment_length(start_point, end_point, extend_point):
            """Check if segment is placed too near to the bend point.

            The idea is that we can either extend segment toward the bend
            but we can shrink it only until it's start.

            If the segment is too near it will return offset to fix the problem,
            otherwise returns `None`.

            """
            base_edge = end_point - start_point
            new_edge = extend_point - start_point
            projection = new_edge.dot(base_edge.normalized())
            if projection < 0 or tool.Cad.is_x(projection, 0):
                return projection
            return None

        # adjust segments to fit the radius and angle
        start_segment_extend_point, end_segment_extend_point = get_segments_extend_points()
        projection = check_new_segment_length(first_segment_start, start_point, start_segment_extend_point)
        if projection is not None:
            self.report(
                {"ERROR"},
                f"Start segment starts too near to the bend, need to offset it atleast by {round(projection, 3)} m.",
            )
            return {"ERROR"}

        projection = check_new_segment_length(second_segment_end, end_point, end_segment_extend_point)
        if projection is not None:
            self.report(
                {"ERROR"},
                f"End segment starts too near to the bend, need to offset it atleast by {round(projection, 3)} m.",
            )
            return {"ERROR"}

        DumbProfileJoiner().join_E(start_object, start_segment_extend_point, start_connection)
        DumbProfileJoiner().join_E(end_object, end_segment_extend_point, end_connection)

        context.view_layer.update()  # update matrices

        builder = ShapeBuilder(ifc_file)
        rep, bend_data = builder.mep_bend_shape(
            start_element,
            self.start_length / si_conversion,
            self.end_length / si_conversion,
            angle,
            self.radius / si_conversion,
            bend_vector / si_conversion,
            flip_z_axis=start_segment_sign == -1,
        )

        parametric_data = {
            "start_length": self.start_length / si_conversion,
            "end_length": self.end_length / si_conversion,
            "radius": self.radius / si_conversion,
            "angle": degrees(angle),
            "main_profile_dimension": profile_dim[lateral_axis] / si_conversion,
        }
        # find the compatible fitting type
        fitting_data = MEPGenerator().get_compatible_fitting_type(
            [start_element, end_element], [start_port, end_port], "BEND", bbim_data=parametric_data
        )
        bend_type = fitting_data["fitting_type"] if fitting_data else None
        start_port_match = fitting_data["start_port_match"] if fitting_data else True

        # use current segments axes if no fitting type found
        lateral_axis_type = lateral_axis
        lateral_sign_type = lateral_sign
        z_sign_type = start_segment_sign
        non_lateral_axis_type = non_lateral_axis
        if bend_type:
            bend_obj = tool.Ifc.get_object(bend_type)
            bbim_data = tool.Model.get_modeling_bbim_pset_data(bend_obj, "BBIM_Fitting")["data_dict"]
            lateral_axis_type, lateral_sign_type = bbim_data["lateral_axis"], bbim_data["lateral_sign"]
            non_lateral_axis_type = 0 if lateral_axis_type == 1 else 1
            z_sign_type = bbim_data.get("z_axis_sign", None)
            # TODO: drop flip_z_axis a bit later
            if z_sign_type is None:
                z_sign_type = -1 if bbim_data["flip_z_axis"] else 1

            # TODO: handle the case without creating a representation in the first place?
            ifcopenshell.api.run("geometry.remove_representation", ifc_file, representation=rep)
        else:  # create new fitting type if nothing is compatible
            mesh = bpy.data.meshes.new("Bend")
            obj = bpy.data.objects.new("Bend", mesh)
            bend_type = bonsai.core.root.assign_class(
                tool.Ifc,
                tool.Collector,
                tool.Root,
                obj=obj,
                ifc_class=MEPGenerator().get_mep_element_class_name(start_element, "FittingType"),
                predefined_type="BEND",
                should_add_representation=False,
            )
            body = ifcopenshell.util.representation.get_context(ifc_file, "Model", "Body", "MODEL_VIEW")
            tool.Model.replace_object_ifc_representation(body, obj, rep)
            tool.Blender.remove_data_block(mesh)
            pset = ifcopenshell.api.run("pset.add_pset", tool.Ifc.get(), product=bend_type, name="BBIM_Fitting")
            ifcopenshell.api.run(
                "pset.edit_pset",
                tool.Ifc.get(),
                pset=pset,
                properties={"Data": tool.Ifc.get().createIfcText(json.dumps(bend_data, default=list))},
            )
            tool.System.add_ports(obj, end_port_pos=end_port_offset)

        # NOTE: at this point we loose current blender objects selection
        # create transition element
        bpy.ops.bim.add_constr_type_instance(relating_type_id=bend_type.id())
        fitting_obj = bpy.context.active_object

        # adjust fitting object rotation and location
        # required since we'll base our `fitting_obj_dir` on this
        fitting_obj.matrix_world = start_object.matrix_world
        context.view_layer.update()

        # depending on bend direction we may need to rotate it to match
        # we just calculate the matrix basises - it's simpler than describing all possible conditions
        def get_fitting_matrix():
            matrix = Matrix.Identity(3)
            start_object_z_basis = tool.Cad.get_basis_vector(start_object, 2)
            start_object_lateral_basis = tool.Cad.get_basis_vector(start_object, lateral_axis)

            def axis_direction(current_axis_sign, type_axis_sign):
                return -1 if current_axis_sign != type_axis_sign else 1

            matrix.col[2] = start_object_z_basis * axis_direction(start_segment_sign, z_sign_type)
            matrix.col[lateral_axis_type] = start_object_lateral_basis * axis_direction(lateral_sign, lateral_sign_type)
            if not start_port_match:
                matrix.col[2] *= -1

            if non_lateral_axis_type == 0:
                non_lateral_axis = matrix.col[lateral_axis_type].cross(matrix.col[2])
            else:
                non_lateral_axis = matrix.col[2].cross(matrix.col[lateral_axis_type])
            matrix.col[non_lateral_axis_type] = non_lateral_axis

            if not start_port_match:
                angle_sign = np.sign(rotation_axis.dot(non_lateral_axis))
                matrix = matrix @ Matrix.Rotation(angle * angle_sign, 3, "XY"[non_lateral_axis_type])

            matrix = matrix.to_4x4()
            matrix.translation = start_segment_extend_point if start_port_match else end_segment_extend_point
            return matrix

        fitting_obj.matrix_world = get_fitting_matrix()

        # add ports and connect them
        ports = tool.System.get_ports(tool.Ifc.get_entity(fitting_obj))
        if not start_port_match:
            start_port, end_port = end_port, start_port
        tool.Ifc.run("system.connect_port", port1=ports[0], port2=start_port, direction="NOTDEFINED")
        tool.Ifc.run("system.connect_port", port1=ports[1], port2=end_port, direction="NOTDEFINED")

        self.report({"INFO"}, f"Success!.. kind of. The angle was {round(bend_data['angle'])}")
        return {"FINISHED"}
