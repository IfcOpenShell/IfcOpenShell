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

import collections.abc
import json
import re
import weakref
from copy import copy
from math import acos, cos, degrees, pi, radians, sin, tan
from typing import ClassVar

import bpy
import ifcopenshell.api.geometry
import ifcopenshell.api.material
import ifcopenshell.api.pset
import ifcopenshell.api.system
import ifcopenshell.util.element
import ifcopenshell.util.placement
import ifcopenshell.util.representation
import ifcopenshell.util.system
import ifcopenshell.util.unit
import numpy as np
from ifcopenshell.util.shape_builder import ShapeBuilder
from mathutils import Matrix, Vector

import bonsai.core.root
import bonsai.tool as tool
from bonsai.bim.module.drawing import gizmos as gizmo
from bonsai.bim.module.drawing.gizmos import DimensionGizmoConfig
from bonsai.bim.module.model import preview_base
from bonsai.bim.module.model.profile import DumbProfileJoiner
from bonsai.bim.parametric_lifecycle import ParametricEditMixinBase
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

            if not all([is_parallel12, is_parallel13, is_parallel21, is_parallel23]):
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

        rel = ifcopenshell.api.material.assign_material(ifc_file, products=[element], type="IfcMaterialProfileSet")
        profile_set = rel.RelatingMaterial
        material_profile = ifcopenshell.api.material.add_profile(ifc_file, profile_set=profile_set, material=material)
        ifcopenshell.api.material.assign_profile(ifc_file, material_profile=material_profile, profile=profile)
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

        ifc_file = tool.Ifc.get()
        segment_obj = tool.Ifc.get_object(segment)
        assert isinstance(segment_obj, bpy.types.Object)
        segment_matrix = segment_obj.matrix_world
        segment_rotation = segment_matrix.to_quaternion()
        fitting_data = self.get_compatible_fitting_type(segment, related_port, "OBSTRUCTION")
        obstruction_type = fitting_data["fitting_type"] if fitting_data else None
        if not obstruction_type:
            obstruction_type = self.create_obstruction_type(segment)

        profile_joiner = DumbProfileJoiner()
        # create obstruction occurrence and setup it's length and port
        # NOTE: at this point we loose current blender objects selection
        bpy.ops.bim.add_occurrence(relating_type_id=obstruction_type.id())
        obstruction_obj = bpy.context.active_object
        assert obstruction_obj
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

        ifcopenshell.api.system.connect_port(
            ifc_file, port1=related_port, port2=obstruction_port, direction="NOTDEFINED"
        )
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
            ifcopenshell.api.geometry.remove_representation(ifc_file, representation=rep)
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
            ifcopenshell.api.geometry.remove_representation(ifc_file, representation=rep)
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
            # Will implicitly remove `mesh`.
            tool.Model.replace_object_ifc_representation(body, obj, rep)
            pset = ifcopenshell.api.pset.add_pset(tool.Ifc.get(), product=transition_type, name="BBIM_Fitting")
            ifcopenshell.api.pset.edit_pset(
                tool.Ifc.get(),
                pset=pset,
                properties={"Data": tool.Ifc.get().createIfcText(json.dumps(transition_data, default=list))},
            )
            tool.System.add_ports(obj, offset_end_port=profile_offset_si)

        # NOTE: at this point we loose current blender objects selection
        # create transition element
        bpy.ops.bim.add_occurrence(relating_type_id=transition_type.id())
        transition_obj = bpy.context.active_object
        assert transition_obj

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
        ifcopenshell.api.system.connect_port(ifc_file, port1=ports[0], port2=start_port, direction="NOTDEFINED")
        ifcopenshell.api.system.connect_port(ifc_file, port1=ports[1], port2=end_port, direction="NOTDEFINED")
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
        name="Bend Inner Radius", description="Bend inner radius in SI units", default=0.2, subtype="DISTANCE", min=0
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
                self.report({"ERROR"}, "Two IFC elements should be selected for the bend.")
                return {"CANCELLED"}

        else:
            self.report({"ERROR"}, "Two IFC elements should be provided for the bend.")
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
            ifcopenshell.api.geometry.remove_representation(ifc_file, representation=rep)
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
            # Will implicitly remove `mesh`.
            tool.Model.replace_object_ifc_representation(body, obj, rep)
            pset = ifcopenshell.api.pset.add_pset(tool.Ifc.get(), product=bend_type, name="BBIM_Fitting")
            ifcopenshell.api.pset.edit_pset(
                tool.Ifc.get(),
                pset=pset,
                properties={"Data": tool.Ifc.get().createIfcText(json.dumps(bend_data, default=list))},
            )
            tool.System.add_ports(obj, end_port_pos=end_port_offset)

        # NOTE: at this point we loose current blender objects selection
        # create transition element
        bpy.ops.bim.add_occurrence(relating_type_id=bend_type.id())
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
        tool.Model.sync_object_ifc_position(fitting_obj)

        # add ports and connect them
        ports = tool.System.get_ports(tool.Ifc.get_entity(fitting_obj))
        start_co = ifcopenshell.util.placement.get_local_placement(start_port.ObjectPlacement)[:, 3]
        port0_co = ifcopenshell.util.placement.get_local_placement(ports[0].ObjectPlacement)[:, 3]
        # We cannot use start_port_match because tool.System.get_ports is unordered
        if not np.allclose(start_co, port0_co):
            start_port, end_port = end_port, start_port
        ifcopenshell.api.system.connect_port(ifc_file, port1=ports[0], port2=start_port, direction="NOTDEFINED")
        ifcopenshell.api.system.connect_port(ifc_file, port1=ports[1], port2=end_port, direction="NOTDEFINED")

        self.report({"INFO"}, f"Success!.. kind of. The angle was {round(bend_data['angle'])}")
        return {"FINISHED"}


def _n_mep_selected(n: int) -> bool:
    selected = tool.Blender.get_selected_objects()
    if len(selected) != n:
        return False
    for selected_obj in selected:
        element = tool.Ifc.get_entity(selected_obj)
        if element is None or not tool.System.is_mep_element(element):
            return False
    return True


def segments_are_parallel(start_object, end_object) -> bool:
    """True iff the two MEP segments' axes are parallel (or collinear)."""
    start_axis = tool.Model.get_flow_segment_axis(start_object)
    end_axis = tool.Model.get_flow_segment_axis(end_object)
    return tool.Cad.are_edges_parallel(start_axis, end_axis)


class MEPJoinSegments(bpy.types.Operator):
    """Dispatcher: join two MEP segments via transition (parallel) or bend
    (non-parallel).

    ``MEPAddTransition`` rejects non-parallel inputs; ``MEPAddBend`` rejects
    parallel inputs (its axis-intersection step is undefined for parallel
    lines). Collapsing them under one click target removes a per-frame
    question the user shouldn't have to answer."""

    bl_idname = "bim.mep_join_segments"
    bl_label = "Join MEP Segments"
    bl_description = "Join the two selected MEP segments — transition if parallel, bend if not"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if not _n_mep_selected(2):
            cls.poll_message_set("Select exactly 2 MEP segments to join.")
            return False
        return True

    def execute(self, context):
        selected = tool.Blender.get_selected_objects()
        active = context.active_object
        if active is None or active not in selected:
            self.report({"ERROR"}, "Active object must be one of the selected MEP segments.")
            return {"CANCELLED"}
        other = next((o for o in selected if o is not active), None)
        if other is None:
            self.report({"ERROR"}, "Two MEP segments must be selected.")
            return {"CANCELLED"}
        if segments_are_parallel(active, other):
            return bpy.ops.bim.mep_add_transition()
        return bpy.ops.bim.enable_bend_preview()


class EnableBendPreview(bpy.types.Operator):
    """Enter bend-preview mode for two selected MEP segments. Populates
    scene.BIMPreviewProperties.bend with segment IFC ids and default
    start_length / end_length / radius; no IFC mutation until finish."""

    bl_idname = "bim.enable_bend_preview"
    bl_label = "Enter Bend Preview"
    bl_description = "Begin tuning bend parameters before committing the bend"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if not _n_mep_selected(2):
            cls.poll_message_set("Select exactly 2 MEP segments to bend.")
            return False
        return True

    def execute(self, context):
        selected = tool.Blender.get_selected_objects()
        active = context.active_object
        if active is None or active not in selected:
            self.report({"ERROR"}, "Active object must be one of the selected MEP segments.")
            return {"CANCELLED"}
        other = next((o for o in selected if o is not active), None)
        if other is None:
            self.report({"ERROR"}, "Two MEP segments must be selected.")
            return {"CANCELLED"}
        active_element = tool.Ifc.get_entity(active)
        other_element = tool.Ifc.get_entity(other)
        if active_element is None or other_element is None:
            self.report({"ERROR"}, "Both selected objects must be IFC elements.")
            return {"CANCELLED"}
        if segments_are_parallel(active, other):
            self.report({"ERROR"}, "Bend preview is for non-parallel segments only.")
            return {"CANCELLED"}

        preview_base.sync_uncommitted_moves([active, other])

        props = preview_base.get_preview_props(context, "bend")
        # Auto-cancel any prior preview so re-clicking join on a different
        # pair doesn't silently commit the previous tuning.
        if props is not None and props.is_active:
            bpy.ops.bim.cancel_bend_preview()

        props.start_segment_id = active_element.id()
        props.end_segment_id = other_element.id()
        props.start_length = 0.1
        props.end_length = 0.1
        props.radius = 0.2
        props.is_active = True
        return {"FINISHED"}


class FinishBendPreview(bpy.types.Operator):
    """Commit the previewed bend with the tuned parameters and exit preview.

    Preview state survives a failed commit so the user can re-tune without
    re-selecting."""

    bl_idname = "bim.finish_bend_preview"
    bl_label = "Apply Bend"
    bl_description = "Commit the bend with the previewed parameters"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        if context.screen is None:
            return {"CANCELLED"}
        props = preview_base.get_preview_props(context, "bend")
        if props is None or not props.is_active:
            return {"CANCELLED"}
        if tool.Ifc.get() is None:
            self.report({"ERROR"}, "No IFC file loaded.")
            return {"CANCELLED"}
        # bpy.ops promotes ``self.report({"ERROR"}) + return CANCELLED`` from
        # the dispatched operator to RuntimeError. Catch it so this operator
        # returns cleanly instead of leaving Blender's operator state
        # half-broken (which would silently disable downstream gizmo polls).
        try:
            result = bpy.ops.bim.mep_add_bend(
                start_segment_id=props.start_segment_id,
                end_segment_id=props.end_segment_id,
                start_length=props.start_length,
                end_length=props.end_length,
                radius=props.radius,
            )
        except RuntimeError as exc:
            self.report({"ERROR"}, str(exc))
            return {"CANCELLED"}
        if "FINISHED" in result:
            preview_base.clear_preview_state(props)
        return result


class CancelBendPreview(bpy.types.Operator):
    """Exit bend preview without committing."""

    bl_idname = "bim.cancel_bend_preview"
    bl_label = "Cancel Bend"
    bl_description = "Discard the previewed bend"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        if context.screen is None:
            return {"CANCELLED"}
        props = preview_base.get_preview_props(context, "bend")
        if props is None or not props.is_active:
            return {"CANCELLED"}
        preview_base.clear_preview_state(props)
        return {"FINISHED"}


def _intersection_past_near(intersection: Vector, near: Vector, far: Vector) -> bool:
    """True iff ``intersection`` lies past ``near`` away from ``far`` — i.e.
    on the bend-corner side of the segment. Used to reject configurations
    where the axes meet INSIDE one of the segments (the bend fitting
    wouldn't physically fit)."""
    base = near - far
    if base.length < 1e-6:
        return False
    return (intersection - near).dot(base.normalized()) > 1e-6


def compute_bend_preview_polylines(
    start_object,
    end_object,
    start_length: float,
    end_length: float,
    radius: float,
    arc_resolution: int = 24,
):
    """Compute the centerline polylines visualising a bend between two MEP
    segments WITHOUT mutating IFC or Blender state.

    Returns a dict with keys:

    - ``"valid"`` (bool) — False for parallel / collinear / degenerate axes
      and for in-segment intersections.
    - ``"leg_a"`` / ``"leg_b"`` — ``(far_endpoint, tangent_point)`` per
      segment, ``None`` when invalid.
    - ``"arc"`` — ``arc_resolution + 1`` points sampling the bend arc.
    - ``"invalid_axes"`` (when invalid + in-segment) — pair of
      ``(far_endpoint, intersection)`` so the decorator can highlight the
      rejected axes in warning colour."""
    from mathutils import Quaternion

    start_axis = tool.Model.get_flow_segment_axis(start_object)
    end_axis = tool.Model.get_flow_segment_axis(end_object)

    intersection = tool.Cad.intersect_edges(start_axis, end_axis)
    if intersection is None:
        return {"valid": False, "leg_a": None, "leg_b": None, "arc": []}
    intersection_point = intersection[0]

    start_near, start_far = tool.Cad.closest_and_furthest_vectors(intersection_point, start_axis)
    end_near, end_far = tool.Cad.closest_and_furthest_vectors(intersection_point, end_axis)

    # The intersection MUST lie outside both segments — past the near-endpoint
    # on the bend-corner side. When it lands inside a segment the tangent
    # points overlap the segment itself and the arc sweeps through a
    # degenerate half-circle.
    invalid_axes = [
        (start_far, intersection_point),
        (end_far, intersection_point),
    ]

    if not _intersection_past_near(intersection_point, start_near, start_far):
        return {
            "valid": False,
            "reason": "intersection_inside_start",
            "leg_a": None,
            "leg_b": None,
            "arc": [],
            "invalid_axes": invalid_axes,
        }
    if not _intersection_past_near(intersection_point, end_near, end_far):
        return {
            "valid": False,
            "reason": "intersection_inside_end",
            "leg_a": None,
            "leg_b": None,
            "arc": [],
            "invalid_axes": invalid_axes,
        }

    dir_into_start = start_near - intersection_point
    dir_into_end = end_near - intersection_point
    if dir_into_start.length < 1e-6 or dir_into_end.length < 1e-6:
        return {"valid": False, "leg_a": None, "leg_b": None, "arc": []}
    dir_into_start.normalize()
    dir_into_end.normalize()

    cos_angle = max(-1.0, min(1.0, dir_into_start.dot(dir_into_end)))
    angle = acos(cos_angle)
    bend_angle = pi - angle
    if bend_angle < 1e-3 or bend_angle > pi - 1e-3:
        return {"valid": False, "leg_a": None, "leg_b": None, "arc": []}

    tangent_offset = radius * tan(bend_angle / 2)
    leg_a_tangent = intersection_point + dir_into_start * tangent_offset
    leg_b_tangent = intersection_point + dir_into_end * tangent_offset

    leg_a_endpoint = leg_a_tangent + dir_into_start * start_length
    leg_b_endpoint = leg_b_tangent + dir_into_end * end_length

    plane_normal = dir_into_start.cross(dir_into_end)
    if plane_normal.length < 1e-6:
        return {"valid": False, "leg_a": None, "leg_b": None, "arc": []}
    plane_normal.normalize()
    perp_to_start = plane_normal.cross(dir_into_start).normalized()
    if perp_to_start.dot(dir_into_end) < 0:
        perp_to_start = -perp_to_start
    arc_center = leg_a_tangent + perp_to_start * radius

    v_a = leg_a_tangent - arc_center
    v_b = leg_b_tangent - arc_center
    sweep_axis = plane_normal if v_a.cross(v_b).dot(plane_normal) > 0 else -plane_normal

    arc_points = []
    for i in range(arc_resolution + 1):
        t = i / arc_resolution
        q = Quaternion(sweep_axis, bend_angle * t)
        arc_points.append(arc_center + (q @ v_a))

    return {
        "valid": True,
        "leg_a": (start_far, leg_a_endpoint),
        "leg_b": (end_far, leg_b_endpoint),
        "arc": arc_points,
    }


def _bend_preview_segments(context):
    """Resolve the two segment objects from the scene-level preview props.

    Re-resolves by IFC id each frame so undo / file reload during preview
    never dangles a stale bpy reference."""
    props = context.scene.BIMPreviewProperties.bend
    ifc_file = tool.Ifc.get()
    if ifc_file is None or not props.is_active:
        return None, None
    try:
        start_element = ifc_file.by_id(props.start_segment_id)
        end_element = ifc_file.by_id(props.end_segment_id)
    except Exception:
        return None, None
    start_obj = tool.Ifc.get_object(start_element) if start_element else None
    end_obj = tool.Ifc.get_object(end_element) if end_element else None
    return start_obj, end_obj


def _gizmo_x_matrix(location: Vector, x_direction: Vector) -> Matrix:
    """Build a 4x4 matrix placing a gizmo at ``location`` with its local +X
    axis aligned to ``x_direction`` in world space. ``BIM_GT_gizmo_dimension``
    draws + drags along local +X by convention."""
    x = x_direction.normalized()
    seed = Vector((0, 0, 1)) if abs(x.z) < 0.9 else Vector((1, 0, 0))
    y = (seed - x * seed.dot(x)).normalized()
    z = x.cross(y)
    mat = Matrix.Identity(4)
    mat[0][:3] = (x.x, y.x, z.x)
    mat[1][:3] = (x.y, y.y, z.y)
    mat[2][:3] = (x.z, y.z, z.z)
    mat.translation = location
    return mat


class GizmoBendPreview(bpy.types.GizmoGroup):
    """Interactive gizmo group for the bend preview flow.

    Three dimension widgets drag start_length / end_length / radius; two
    icon gizmos commit or cancel. When the geometry is degenerate the
    dimensions and validate hide but cancel stays visible so the user
    always has an exit."""

    bl_idname = "OBJECT_GGT_bim_bend_preview"
    bl_label = "Bend Preview Gizmos"
    bl_space_type = "VIEW_3D"
    bl_region_type = "WINDOW"
    bl_options = {"3D", "PERSISTENT"}

    ICON_SCALE: ClassVar[float] = 0.375
    ICON_SPACING_X: ClassVar[float] = 0.4
    ICON_Z_OFFSET: ClassVar[float] = 1.5

    @classmethod
    def poll(cls, context):
        preview = getattr(context.scene, "BIMPreviewProperties", None)
        props = preview.bend if preview is not None else None
        if props is None or not props.is_active:
            return False
        if not tool.Blender.are_viewport_gizmos_enabled():
            return False
        ifc_file = tool.Ifc.get()
        if ifc_file is None:
            return False
        try:
            ifc_file.by_id(props.start_segment_id)
            ifc_file.by_id(props.end_segment_id)
        except (RuntimeError, KeyError):
            return False
        return True

    def setup(self, context):
        prefs = tool.Blender.get_addon_preferences()
        default_color = tuple(prefs.decorations_colour[:3])
        highlight_color = tuple(prefs.decorator_color_selected[:3])

        _props = preview_base.make_props_callback("bend")

        def setup_dimension(attr: str, prop_name: str, invert_delta: bool = False) -> bpy.types.Gizmo:
            gz = self.gizmos.new("BIM_GT_gizmo_dimension")
            gz.move_get_cb = preview_base.make_dim_getter(_props, attr)
            gz.move_set_cb = preview_base.make_dim_setter(_props, attr)
            gz.axis = Vector((1, 0, 0))
            gz.invert_delta = invert_delta
            gz.delta_scale = 1.0
            gz.prop_name = prop_name
            gz.gizmo_group = self
            gz.color = default_color
            gz.color_highlight = highlight_color
            gz.alpha = 1.0
            gz.use_draw_modal = True
            gz.use_draw_scale = False
            gz.text_offset_sign = 1
            gz.text_alignment = gizmo.TextAlignment.CENTER
            gz.show_start_arrow = False
            gz.show_end_arrow = True
            gz.show_extension_lines = False
            gz.text_formatter = None
            return gz

        self.start_dim = setup_dimension("start_length", "Start Length")
        self.end_dim = setup_dimension("end_length", "End Length")
        self.radius_dim = setup_dimension("radius", "Radius")

        from bonsai.bim.module.drawing.gizmos import BaseParametricGizmoGroup

        self.validate_icon = self.gizmos.new("VIEW3D_GT_validate")
        self.validate_icon.use_draw_scale = False
        self.validate_icon.color = BaseParametricGizmoGroup.COLOR_GREEN
        self.validate_icon.color_highlight = highlight_color
        self.validate_icon.target_set_operator("bim.finish_bend_preview")

        self.cancel_icon = self.gizmos.new("VIEW3D_GT_cancel")
        self.cancel_icon.use_draw_scale = False
        self.cancel_icon.color = BaseParametricGizmoGroup.COLOR_RED
        self.cancel_icon.color_highlight = highlight_color
        self.cancel_icon.target_set_operator("bim.cancel_bend_preview")

    def refresh(self, context):
        self._position_gizmos(context)

    def draw_prepare(self, context):
        self._position_gizmos(context)

    def _position_gizmos(self, context):
        """Place gizmos at the bend intersection using the current scene
        props. Cancel stays visible on degenerate geometry so the user
        always has an exit; the other widgets hide when there's no defined
        tangent / arc to anchor them on."""
        start_obj, end_obj = _bend_preview_segments(context)
        if start_obj is None or end_obj is None:
            for gz in (self.start_dim, self.end_dim, self.radius_dim, self.validate_icon, self.cancel_icon):
                gz.hide = True
            return

        props = context.scene.BIMPreviewProperties.bend
        preview = compute_bend_preview_polylines(start_obj, end_obj, props.start_length, props.end_length, props.radius)
        if not preview["valid"]:
            for gz in (self.start_dim, self.end_dim, self.radius_dim, self.validate_icon):
                gz.hide = True
            self.cancel_icon.hide = False
            axes = preview.get("invalid_axes") or []
            if axes:
                intersection_point = axes[0][1]
                billboard_rot = gizmo.get_billboard_rotation(context)
                anchor = intersection_point + Vector((0, 0, self.ICON_Z_OFFSET))
                self.cancel_icon.matrix_basis = gizmo.billboarded_at(anchor, billboard_rot, scale=self.ICON_SCALE)
            return

        for gz in (self.start_dim, self.end_dim, self.radius_dim, self.validate_icon, self.cancel_icon):
            gz.hide = False

        leg_a_far, leg_a_end = preview["leg_a"]
        leg_b_far, leg_b_end = preview["leg_b"]
        toward_bend_a = (
            (leg_a_end - leg_a_far).normalized() if (leg_a_end - leg_a_far).length > 1e-6 else Vector((0, 0, 1))
        )
        toward_bend_b = (
            (leg_b_end - leg_b_far).normalized() if (leg_b_end - leg_b_far).length > 1e-6 else Vector((0, 0, 1))
        )
        leg_a_tangent = leg_a_end + toward_bend_a * props.start_length
        leg_b_tangent = leg_b_end + toward_bend_b * props.end_length

        # axis is set in world space every frame so the drag projection
        # matches the visual regardless of either segment's matrix_world.
        self.start_dim.matrix_basis = _gizmo_x_matrix(leg_a_tangent, -toward_bend_a)
        self.start_dim.axis = -toward_bend_a
        self.start_dim.set_dimension_length(props.start_length)
        self.end_dim.matrix_basis = _gizmo_x_matrix(leg_b_tangent, -toward_bend_b)
        self.end_dim.axis = -toward_bend_b
        self.end_dim.set_dimension_length(props.end_length)

        arc = preview["arc"]
        if len(arc) >= 3:
            mid = len(arc) // 2
            chord_mid = (arc[0] + arc[-1]) * 0.5
            toward_mid = arc[mid] - chord_mid
            if toward_mid.length > 1e-6:
                toward_mid = toward_mid.normalized()
                half_chord = (arc[-1] - arc[0]).length * 0.5
                center_dist = max(0.0, props.radius * props.radius - half_chord * half_chord) ** 0.5
                arc_center = chord_mid - toward_mid * center_dist
                radial_out = arc[mid] - arc_center
                if radial_out.length > 1e-6:
                    radial_out.normalize()
                    inward = -radial_out
                    self.radius_dim.matrix_basis = _gizmo_x_matrix(arc[mid], inward)
                    self.radius_dim.axis = inward
                    self.radius_dim.set_dimension_length(props.radius)
                else:
                    self.radius_dim.hide = True
            else:
                self.radius_dim.hide = True
        else:
            self.radius_dim.hide = True

        billboard_rot = gizmo.get_billboard_rotation(context)
        anchor_base = arc[len(arc) // 2] if arc else (leg_a_end + leg_b_end) * 0.5
        anchor = anchor_base + Vector((0, 0, self.ICON_Z_OFFSET))
        offset_x = billboard_rot @ Vector((self.ICON_SPACING_X, 0.0, 0.0))
        self.validate_icon.matrix_basis = gizmo.billboarded_at(anchor, billboard_rot, scale=self.ICON_SCALE)
        self.cancel_icon.matrix_basis = gizmo.billboarded_at(anchor + offset_x, billboard_rot, scale=self.ICON_SCALE)


# --- MEP segment parametric edit + cursor-anchored operators ---------------


def _segment_world_length(obj: bpy.types.Object) -> float:
    """World-space length of an MEP segment's extrusion axis."""
    start, end = tool.Model.get_flow_segment_axis(obj)
    return (end - start).length


def _preview_segment_via_scale(
    obj: bpy.types.Object,
    props_length: float,
    snap_length: float,
    snap_object_scale_z: float,
) -> None:
    """Scale obj along local Z so the visible segment matches ``props_length``
    without touching IFC.

    Composes correctly with a non-identity pre-edit ``obj.scale.z``: the
    mesh's local-Z extent is ``snap_length / snap_object_scale_z``, so the
    new scale.z is ``props_length / mesh_local_length``."""
    if snap_length < 1e-6 or snap_object_scale_z < 1e-6:
        return
    mesh_local_length = snap_length / snap_object_scale_z
    obj.scale.z = max(props_length, 0.01) / mesh_local_length


def _restore_segment_scale_to(obj: bpy.types.Object, scale_z: float) -> None:
    """Restore obj's local-Z scale. Cancel passes the pre-edit
    ``snap_object_scale_z``; finish passes ``1.0`` because ``set_depth`` has
    already rebuilt the mesh 1:1 with the new IFC length."""
    obj.scale.z = scale_z


def regenerate_pipe_segment_mesh_from_props(obj: bpy.types.Object) -> None:
    """Live-preview hook for ``BIMPipeSegmentProperties.length`` drags."""
    props = tool.Model.get_pipe_segment_props(obj)
    _preview_segment_via_scale(obj, props.length, props.snap_length, props.snap_object_scale_z)
    props.mesh_dirty = True


def regenerate_duct_segment_mesh_from_props(obj: bpy.types.Object) -> None:
    """Live-preview hook for ``BIMDuctSegmentProperties.length`` drags."""
    props = tool.Model.get_duct_segment_props(obj)
    _preview_segment_via_scale(obj, props.length, props.snap_length, props.snap_object_scale_z)
    props.mesh_dirty = True


def _restore_segment_mesh_if_dirty(props, obj: bpy.types.Object) -> None:
    """Restore obj's preview scale to the pre-edit value if dirty.

    Restoring to ``snap_object_scale_z`` (not 1.0) avoids zeroing a user's
    non-identity pre-edit scale."""
    if not props.mesh_dirty:
        return
    _restore_segment_scale_to(obj, props.snap_object_scale_z)
    props.mesh_dirty = False


class _MEPSegmentEditMixin(ParametricEditMixinBase):
    """MEP segment edit lifecycle (length-only).

    Segment editing has no BBIM pset — the length lives in the IFC
    extrusion depth and is rewritten by ``DumbProfileJoiner.set_depth``. The
    ``snap_object_scale_z`` field on the PropertyGroup records pre-edit
    scale so Cancel and no-op Finish restore the segment exactly to its
    pre-edit visual state. Finish dispatches ``bim.regenerate_distribution_element``
    on length-change to re-align adjacent fittings."""

    pset_name = ""  # MEP segments carry no BBIM_<Type> pset.

    @classmethod
    def _enable_one(cls, obj: bpy.types.Object) -> None:
        resolved = cls._resolve(obj)
        if resolved is None:
            return
        _element, props = resolved
        # Commit any pre-edit matrix_world drift before snap_length is captured
        # from _segment_world_length. Otherwise set_depth at Finish would write
        # representation coords relative to a stale ObjectPlacement.
        cls._handle_drift_on_enable(obj)
        current_length = _segment_world_length(obj)
        props.snap_object_scale_z = obj.scale.z
        props.snap_length = current_length
        props.length = current_length
        props.mesh_dirty = False
        props.is_editing = True

    @classmethod
    def _finish_one(cls, obj: bpy.types.Object, context: bpy.types.Context) -> tuple[bool, bool]:
        """Returns ``(resolved, committed)``: ``resolved`` is False when the
        target is no longer this MEP segment type; ``committed`` is True when
        a length change was written through ``set_depth``."""
        resolved = cls._resolve(obj)
        if resolved is None:
            return False, False
        _element, props = resolved
        committed = False
        if props.length != props.snap_length:
            # set_depth rebuilds the representation 1:1 with the new length, so
            # reset scale to 1.0 or any preview stretch would double-apply.
            DumbProfileJoiner().set_depth(obj, props.length)
            _restore_segment_scale_to(obj, 1.0)
            props.mesh_dirty = False
            committed = True
        else:
            _restore_segment_mesh_if_dirty(props, obj)
        cls._handle_drift_on_finish(obj)
        props.is_editing = False
        return True, committed

    @classmethod
    def _cancel_one(cls, obj: bpy.types.Object) -> None:
        resolved = cls._resolve(obj)
        if resolved is None:
            return
        element, props = resolved
        # Disable editing first so the length-restore below doesn't fire one
        # more preview pass.
        props.is_editing = False
        props.length = props.snap_length
        _restore_segment_mesh_if_dirty(props, obj)
        cls._handle_drift_on_cancel(obj, element)

    def _enable_targets(self, context: bpy.types.Context) -> set[str]:
        obj = context.active_object
        if obj is None:
            return {"CANCELLED"}
        # Resolve pre-flight to map a non-matching active object to CANCELLED
        # rather than the silent no-op the per-target classmethod would produce.
        resolved = self._resolve(obj)
        if resolved is None:
            return {"CANCELLED"}
        self._enable_one(obj)
        return {"FINISHED"}

    def _finish_targets(self, context: bpy.types.Context) -> set[str]:
        obj = context.active_object
        if obj is None:
            return {"CANCELLED"}
        resolved_ok, committed = self._finish_one(obj, context)
        if not resolved_ok:
            return {"CANCELLED"}
        if committed:
            # Re-align adjacent fittings + segments to follow the port move;
            # failure here doesn't roll back the length commit (primary intent).
            try:
                bpy.ops.bim.regenerate_distribution_element()
            except Exception as e:
                self.report({"WARNING"}, f"Length committed but auto-regenerate failed: {e}")
        return {"FINISHED"}

    def _cancel_targets(self, context: bpy.types.Context) -> set[str]:
        obj = context.active_object
        if obj is None:
            return {"CANCELLED"}
        self._cancel_one(obj)
        return {"FINISHED"}


class _PipeSegmentEditMixin(_MEPSegmentEditMixin):
    @classmethod
    def _is_element_type(cls, element):
        return tool.Parametric.is_pipe_segment(element)

    @classmethod
    def _get_props(cls, obj: bpy.types.Object):
        return tool.Model.get_pipe_segment_props(obj)


class _DuctSegmentEditMixin(_MEPSegmentEditMixin):
    @classmethod
    def _is_element_type(cls, element):
        return tool.Parametric.is_duct_segment(element)

    @classmethod
    def _get_props(cls, obj: bpy.types.Object):
        return tool.Model.get_duct_segment_props(obj)


EnableEditingPipeSegment, FinishEditingPipeSegment, CancelEditingPipeSegment = tool.Parametric.build_edit_lifecycle(
    "pipe_segment",
    _PipeSegmentEditMixin,
    labels=(
        ("Edit Pipe Segment", ""),
        ("Apply Pipe Segment Edits", ""),
        ("Discard Pipe Segment Edits", ""),
    ),
    module_name=__name__,
)

EnableEditingDuctSegment, FinishEditingDuctSegment, CancelEditingDuctSegment = tool.Parametric.build_edit_lifecycle(
    "duct_segment",
    _DuctSegmentEditMixin,
    labels=(
        ("Edit Duct Segment", ""),
        ("Apply Duct Segment Edits", ""),
        ("Discard Duct Segment Edits", ""),
    ),
    module_name=__name__,
)


def _project_cursor_to_segment_local_z(context, *, is_pipe: bool) -> tuple[bpy.types.Object | None, float | None]:
    """Validate the active object is an MEP segment of the requested kind,
    commit any in-progress parametric edit, and return ``(obj, cursor_local_z)``.

    Returns ``(None, None)`` on precondition failure — callers should treat
    that as ``{"CANCELLED"}``."""
    obj = context.active_object
    if obj is None:
        return None, None
    element = tool.Ifc.get_entity(obj)
    if element is None:
        return None, None
    predicate = tool.Parametric.is_pipe_segment if is_pipe else tool.Parametric.is_duct_segment
    if not predicate(element):
        return None, None

    # Commit any in-progress edit first so the user's drag-state isn't
    # silently discarded — cursor-anchored ops must layer on top of an
    # in-progress edit, not overwrite it.
    props = tool.Model.get_pipe_segment_props(obj) if is_pipe else tool.Model.get_duct_segment_props(obj)
    if props.is_editing:
        with bpy.context.temp_override(active_object=obj, selected_objects=[obj]):
            if is_pipe:
                bpy.ops.bim.finish_editing_pipe_segment()
            else:
                bpy.ops.bim.finish_editing_duct_segment()

    cursor_world = context.scene.cursor.location
    cursor_local = obj.matrix_world.inverted() @ cursor_world
    return obj, cursor_local.z


def _extend_segment_to_cursor(context, *, is_pipe: bool) -> set[str]:
    """Extend or trim the nearest endpoint of the segment to the cursor
    projection."""
    obj, _ = _project_cursor_to_segment_local_z(context, is_pipe=is_pipe)
    if obj is None:
        return {"CANCELLED"}
    DumbProfileJoiner().join_E(obj, context.scene.cursor.location)
    return {"FINISHED"}


class ExtendPipeSegmentToCursor(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.extend_pipe_segment_to_cursor"
    bl_label = "Extend Pipe Segment to Cursor"
    bl_description = (
        "Extend or trim the active pipe segment so its nearest endpoint reaches the 3D cursor's projection "
        "on the segment axis"
    )
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        return _extend_segment_to_cursor(context, is_pipe=True)


class ExtendDuctSegmentToCursor(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.extend_duct_segment_to_cursor"
    bl_label = "Extend Duct Segment to Cursor"
    bl_description = (
        "Extend or trim the active duct segment so its nearest endpoint reaches the 3D cursor's projection "
        "on the segment axis"
    )
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        return _extend_segment_to_cursor(context, is_pipe=False)


def split_mep_segment(obj: bpy.types.Object, cut_local_z: float) -> bpy.types.Object | None:
    """Split an MEP segment at ``cut_local_z`` along its local +Z axis,
    producing two connected segments where there was one.

    Snapshots the downstream end-port connection, duplicates the segment via
    ``bonsai.core.root.copy_class``, positions the new segment so its start
    coincides with the original's new end, calls ``DumbProfileJoiner.set_depth``
    on both halves, then reconnects ports: original-end ↔ new-start, and
    if a downstream connection existed: new-end ↔ snapshotted downstream
    with the preserved direction. Rejects splits within 0.01m of either
    endpoint."""
    from bonsai.tool.system import direction_from_port_pair

    element = tool.Ifc.get_entity(obj)
    if element is None or not tool.System.is_mep_element(element):
        return None

    start_world, end_world = tool.Model.get_flow_segment_axis(obj)
    original_length = (end_world - start_world).length
    if cut_local_z < 0.01 or cut_local_z > original_length - 0.01:
        return None

    segment_data = MEPGenerator().get_segment_data(element)
    end_port = segment_data.get("end_port")
    downstream_port = None
    downstream_direction = "NOTDEFINED"
    if end_port is not None:
        downstream_port = tool.System.get_connected_port(end_port)
        if downstream_port is not None:
            downstream_direction = direction_from_port_pair(end_port, downstream_port)

    new_obj = obj.copy()
    if obj.data is not None:
        new_obj.data = obj.data.copy()
    for collection in obj.users_collection:
        collection.objects.link(new_obj)
    new_element = bonsai.core.root.copy_class(tool.Ifc, tool.Collector, tool.Geometry, tool.Root, obj=new_obj)
    if new_element is None:
        bpy.data.objects.remove(new_obj, do_unlink=True)
        return None

    local_z = obj.matrix_world.to_3x3() @ Vector((0.0, 0.0, 1.0))
    local_z.normalize()
    new_obj.matrix_world.translation = obj.matrix_world.translation + local_z * cut_local_z

    joiner = DumbProfileJoiner()
    joiner.set_depth(obj, cut_local_z)
    joiner.set_depth(new_obj, original_length - cut_local_z)

    gen = MEPGenerator()
    seg1_data = gen.get_segment_data(element)
    seg2_data = gen.get_segment_data(new_element)
    seg1_end = seg1_data.get("end_port")
    seg2_start = seg2_data.get("start_port")
    seg2_end = seg2_data.get("end_port")

    if seg1_end is not None and seg2_start is not None:
        try:
            tool.Ifc.run(
                "system.connect_port",
                port1=seg1_end,
                port2=seg2_start,
                direction="NOTDEFINED",
            )
        except Exception as e:
            print(f"Bonsai: split_mep_segment failed to connect halves at cut: {e}")

    if downstream_port is not None and seg2_end is not None:
        try:
            tool.Ifc.run(
                "system.connect_port",
                port1=seg2_end,
                port2=downstream_port,
                direction=downstream_direction,
            )
        except Exception as e:
            print(f"Bonsai: split_mep_segment failed to restore downstream connection: {e}")

    return new_obj


def _split_segment_at_cursor(operator, context, *, is_pipe: bool) -> set[str]:
    """Split the active MEP segment at the cursor's projection on its axis."""
    obj, cursor_local_z = _project_cursor_to_segment_local_z(context, is_pipe=is_pipe)
    if obj is None or cursor_local_z is None:
        return {"CANCELLED"}
    new_obj = split_mep_segment(obj, cursor_local_z)
    if new_obj is None:
        operator.report(
            {"WARNING"},
            "Split cancelled — cursor projection must lie between segment endpoints (>=0.01 m from each).",
        )
        return {"CANCELLED"}
    return {"FINISHED"}


class SplitPipeSegmentAtCursor(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.split_pipe_segment_at_cursor"
    bl_label = "Split Pipe Segment at Cursor"
    bl_description = (
        "Split the active pipe segment at the 3D cursor's projection on the segment axis, "
        "producing two connected segments"
    )
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        return _split_segment_at_cursor(self, context, is_pipe=True)


class SplitDuctSegmentAtCursor(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.split_duct_segment_at_cursor"
    bl_label = "Split Duct Segment at Cursor"
    bl_description = (
        "Split the active duct segment at the 3D cursor's projection on the segment axis, "
        "producing two connected segments"
    )
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        return _split_segment_at_cursor(self, context, is_pipe=False)


class _MEPSegmentEditionMixin:
    """Shared element-specific scaffolding for the two MEP-segment gizmo
    groups: an extend-to-cursor icon at the cursor's projection on the
    segment axis plus a split icon stacked above it. Cursor-anchored, always
    visible when the parametric gizmo group polls."""

    _extend_operator: str = ""
    _split_operator: str = ""

    CURSOR_STACK_OFFSET: ClassVar[float] = 0.4

    def setup_element_specific_gizmos(self, context):
        default_color, highlight_color = self.get_decoration_colors()
        self.extend_gizmo = self._setup_icon_gizmo(
            "VIEW3D_GT_extend",
            default_color,
            self._extend_operator,
            highlight_color,
        )
        warning_color = gizmo.get_warning_color_from_prefs(tool.Blender.get_addon_preferences())
        self.split_gizmo = self._setup_icon_gizmo(
            "VIEW3D_GT_split",
            default_color,
            self._split_operator,
            warning_color,
        )
        if context.region is not None:
            type(self)._active_instances[context.region.as_pointer()] = weakref.ref(self)

    def _refresh_element_specific(self, context, mw, props):
        if not hasattr(self, "extend_gizmo"):
            return
        cursor_world = context.scene.cursor.location
        cursor_local = mw.inverted() @ cursor_world
        projected_local = Vector((0.0, 0.0, cursor_local.z))
        projected_world = mw @ projected_local
        billboard_rot = self._frame_billboard_rot or gizmo.get_billboard_rotation(context)

        gz = self.extend_gizmo
        gz.hide = self.is_gizmo_hidden_by_modal(gz)
        gz.matrix_basis = gizmo.billboarded_at(projected_world, billboard_rot)
        if gizmo.should_flip_extend_arrow(projected_world, mw.translation, billboard_rot):
            gz.matrix_basis = gz.matrix_basis @ gizmo.EXTEND_FLIP_MIRROR_X

        if hasattr(self, "split_gizmo"):
            split_gz = self.split_gizmo
            obj = context.active_object
            if obj is None or not obj.bound_box:
                split_gz.hide = True
            else:
                # Endpoint-cut threshold matches split_mep_segment's rejection
                # window so the icon never offers an invalid affordance.
                current_length = max(c[2] for c in obj.bound_box)
                in_range = 0.01 < cursor_local.z < (current_length - 0.01)
                if not in_range or self.is_gizmo_hidden_by_modal(split_gz):
                    split_gz.hide = True
                else:
                    split_gz.hide = False
                    offset_world = billboard_rot @ Vector((0.0, self.CURSOR_STACK_OFFSET, 0.0))
                    split_gz.matrix_basis = gizmo.billboarded_at(projected_world + offset_world, billboard_rot)


# Dimension config shared between pipe and duct segments. ``matrix_position``
# routing through ``compose_gizmo_matrix`` rotates the +X line to ``axis`` so
# the dimension renders along the segment's extrusion direction.
_MEP_SEGMENT_LENGTH_DIMENSION = DimensionGizmoConfig(
    attr_name="length",
    axis=(0, 0, 1),
    matrix_position=lambda _props: Vector((0.0, 0.0, 0.0)),
    min_value=0.01,
    show_start_arrow=True,
    show_end_arrow=True,
)


class GizmoPipeSegmentEdition(bpy.types.GizmoGroup, _MEPSegmentEditionMixin, gizmo.BaseParametricGizmoGroup):
    """Parametric-edit gizmo for IfcPipeSegment."""

    bl_idname = "OBJECT_GGT_bim_pipe_segment_edition"
    bl_label = "Pipe Segment Editing Gizmo"
    bl_space_type = "VIEW_3D"
    bl_region_type = "WINDOW"
    bl_options = {"3D", "PERSISTENT"}

    enable_editing_operator = "bim.enable_editing_pipe_segment"
    finish_editing_operator = "bim.finish_editing_pipe_segment"
    cancel_editing_operator = "bim.cancel_editing_pipe_segment"
    cycle_type_operator = ""
    props_getter = tool.Model.get_pipe_segment_props
    gizmo_pref_name = "pipe_segment"
    _extend_operator = "bim.extend_pipe_segment_to_cursor"
    _split_operator = "bim.split_pipe_segment_at_cursor"

    dimension_gizmo_props = [_MEP_SEGMENT_LENGTH_DIMENSION]

    _active_instances: ClassVar["dict[int, weakref.ReferenceType[GizmoPipeSegmentEdition]]"] = {}

    @classmethod
    def is_element_type(cls, element):
        return tool.Parametric.is_pipe_segment(element)


class GizmoDuctSegmentEdition(bpy.types.GizmoGroup, _MEPSegmentEditionMixin, gizmo.BaseParametricGizmoGroup):
    """Parametric-edit gizmo for IfcDuctSegment."""

    bl_idname = "OBJECT_GGT_bim_duct_segment_edition"
    bl_label = "Duct Segment Editing Gizmo"
    bl_space_type = "VIEW_3D"
    bl_region_type = "WINDOW"
    bl_options = {"3D", "PERSISTENT"}

    enable_editing_operator = "bim.enable_editing_duct_segment"
    finish_editing_operator = "bim.finish_editing_duct_segment"
    cancel_editing_operator = "bim.cancel_editing_duct_segment"
    cycle_type_operator = ""
    props_getter = tool.Model.get_duct_segment_props
    gizmo_pref_name = "duct_segment"
    _extend_operator = "bim.extend_duct_segment_to_cursor"
    _split_operator = "bim.split_duct_segment_at_cursor"

    dimension_gizmo_props = [_MEP_SEGMENT_LENGTH_DIMENSION]

    _active_instances: ClassVar["dict[int, weakref.ReferenceType[GizmoDuctSegmentEdition]]"] = {}

    @classmethod
    def is_element_type(cls, element):
        return tool.Parametric.is_duct_segment(element)
