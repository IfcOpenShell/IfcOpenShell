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
import mathutils.geometry
import blenderbim.bim.handler
import blenderbim.core.type
import blenderbim.core.root
import blenderbim.core.geometry
import blenderbim.tool as tool
from math import pi, degrees, radians
from copy import copy
from mathutils import Vector, Matrix
from ifcopenshell.util.shape_builder import ShapeBuilder
from blenderbim.bim.module.model.profile import DumbProfileJoiner

V = lambda *x: Vector([float(i) for i in x])


class RegenerateDistributionElement(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.regenerate_distribution_element"
    bl_description = (
        "Regenerates the positions and segment lengths of a distribution element and all connected elements."
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

            if len(connected) == 1:
                extend_branch(list(connected)[0], branch, element)
            else:
                for connected_element in connected:
                    branch_element["children"].append(extend_branch(connected_element, [], element))

            return branch

        queue = extend_branch(current_element, [])[0]["children"]

        # import pprint
        # pprint.pprint(queue)

        def process_branch(branch):
            for branch_element in branch:
                element = branch_element["element"]
                print("processing", element)
                predecessor = branch_element["predecessor"]
                if False:  # If the element does not need to be transformed, return early.
                    return
                # Perform the extend, translate, rotate, etc the element as necessary based on the predecessor.
                # For segments, prioritise extensions instead of translations.
                # For everything else, only translate. No rotation.
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

    def get_compatible_fitting_type(self, segment_or_segments, port_or_ports, predefined_type):
        """
        returns a dict of compatible fitting_type and start_port_match flag to correctly place the fitting.

        We find compatible fitting only by checking
        if they were already used with that segment type before
        and fitting's ports should match `port_or_ports` by PredefinedType and SystemType.

        If port from `port_or_ports` has PredefinedType/SystemType == None/NOTDEFINED then
        those parameters won't be taken into account checking compatibility.

        There lies the problem that it won't be
        able to identify the fittings that were not yet connected to any segments yet.
        """
        if not isinstance(segment_or_segments, collections.abc.Iterable):
            segments = [segment_or_segments]
            ports = [port_or_ports]
        else:
            segments = segment_or_segments
            ports = port_or_ports

        segments_data = []
        for segment, port in zip(segments, ports, strict=True):
            segment_type = ifcopenshell.util.element.get_type(segment)
            # if segment doesn't have type we cannot check compatibility by available occurences
            if segment_type is None:
                return
            segments_data.append((segment_type, port.PredefinedType, port.SystemType))

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
            # but I couldn't pin it down exact cases
            for test_segment_data in fitting_data[:]:
                for base_segment_data in segments_data:
                    if not are_segments_compatible(test_segment_data, base_segment_data):
                        continue
                    segments_data.remove(test_segment_data)

            # all segments were sorted
            return len(segments_data) == 0

        def pack_return_data(fitting_type, ports, segments_data):
            for port in ports:
                port_local_position = V(*port.ObjectPlacement.RelativePlacement.Location.Coordinates)
                if tool.Cad.is_x(port_local_position.length, 0.0):
                    start_port = port
                    break
            connected_port = tool.System.get_connected_port(start_port)
            connected_element = tool.System.get_port_relating_element(connected_port)
            element_type = ifcopenshell.util.element.get_type(connected_element)
            return {"fitting_type": fitting_type, "start_port_match": element_type == segments_data[0][0]}

        fitting_types = tool.Ifc.get().by_type(self.get_mep_element_class_name(segments[0], "FittingType"))
        for fitting_type in fitting_types:
            if fitting_type.PredefinedType != predefined_type:
                continue
            fittings = tool.Ifc.get_all_element_occurences(fitting_type)
            if not fittings:
                continue
            fitting = fittings[0]

            ports = ifcopenshell.util.system.get_ports(fitting)
            fitting_data = []
            fitting_connected_to_none_type = False
            for port in ports:
                connected_port = tool.System.get_connected_port(port)
                connected_element = tool.System.get_port_relating_element(connected_port)
                element_type = ifcopenshell.util.element.get_type(connected_element)
                if element_type is None:
                    fitting_connected_to_none_type = True
                    break
                fitting_data.append((element_type, port.PredefinedType, port.SystemType))

            if fitting_connected_to_none_type:
                continue

            if are_connected_elements_compatible(segments_data, fitting_data):
                return pack_return_data(fitting_type, ports, segments_data)

    def create_obstruction_type(self, segment):
        # code is very similar to "bim.add_type"
        profile_set = ifcopenshell.util.element.get_material(segment, should_skip_usage=True)
        material_profile = profile_set.MaterialProfiles[0]
        profile = material_profile.Profile
        material = material_profile.Material
        ifc_class = self.get_mep_element_class_name(segment, "FittingType")
        ifc_file = tool.Ifc.get()
        body = ifcopenshell.util.representation.get_context(ifc_file, "Model", "Body", "MODEL_VIEW")

        obj = bpy.data.objects.new("Obstruction", None)
        # TODO: OBSTRUCTION predefined type is available only for IfcDuctFitting and IfcPipeFitting
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
        fitting_data = self.get_compatible_fitting_type(segment, related_port, "OBSTRUCTION")
        obstruction_type = fitting_data["fitting_type"] if fitting_data else None
        if not obstruction_type:
            obstruction_type = self.create_obstruction_type(segment)

        profile_joiner = DumbProfileJoiner()
        # create obstruction occurence and setup it's length and port
        # NOTE: at this point we loose current blender objects selection
        bpy.ops.bim.add_constr_type_instance(relating_type_id=obstruction_type.id())
        obstruction_obj = bpy.context.active_object
        obstruction_obj.matrix_world = segment_matrix

        profile_joiner.set_depth(obstruction_obj, length)
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
    bl_description = (
        "Adds transition between two MEP elements. Elements are either provided by ID or selected in Blender"
    )
    bl_options = {"REGISTER", "UNDO"}
    start_length: bpy.props.FloatProperty(
        name="Start Length", description="Transition start length in SI units", default=0.1, subtype="DISTANCE"
    )
    end_length: bpy.props.FloatProperty(
        name="End Length", description="Transition end length in SI units", default=0.1, subtype="DISTANCE"
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

        # TODO: support cases when segments are partially or completely overlapping each other
        if not tool.Cad.are_edges_collinear(start_axis, end_axis):
            self.report({"ERROR"}, f"Failed to add transition - non collinear segments are not yet supported.")
            return {"CANCELLED"}

        start_segment_data = MEPGenerator().get_segment_data(start_element)
        end_segment_data = MEPGenerator().get_segment_data(end_element)
        end_port = end_segment_data["start_port"]
        start_port = start_segment_data["end_port"]

        points_ports_map = {
            start_segment_data["start_point"]: start_segment_data["start_port"],
            start_segment_data["end_point"]: start_segment_data["end_port"],
            end_segment_data["start_point"]: end_segment_data["start_port"],
            end_segment_data["end_point"]: end_segment_data["end_port"],
        }

        start_point, end_point = tool.Cad.closest_points(
            (start_segment_data["start_point"], start_segment_data["end_point"]),
            (end_segment_data["start_point"], end_segment_data["end_point"]),
        )
        transition_dir = (end_point - start_point).normalized()
        start_port = points_ports_map[start_point]
        end_port = points_ports_map[end_point]

        # add transition representation
        builder = ShapeBuilder(ifc_file)
        rep, transition_data = builder.mep_transition_shape(
            start_element, end_element, self.start_length / si_conversion, self.end_length / si_conversion
        )

        if not rep:
            self.report({"ERROR"}, f"Failed to add transition - this kind of profiles is not yet supported.")
            return {"CANCELLED"}

        middle_point = (start_point + end_point) / 2
        full_transition_length = transition_data["full_transition_length"] * si_conversion
        start_segment_extend_point = middle_point - transition_dir * full_transition_length / 2
        end_segment_extend_point = middle_point + transition_dir * full_transition_length / 2
        DumbProfileJoiner().join_E(start_object, start_segment_extend_point)
        DumbProfileJoiner().join_E(end_object, end_segment_extend_point)

        fitting_data = MEPGenerator().get_compatible_fitting_type(
            [start_element, end_element], [start_port, end_port], "TRANSITION"
        )

        transition_type = fitting_data["fitting_type"] if fitting_data else None
        start_port_match = fitting_data["start_port_match"] if fitting_data else True

        if not transition_type:
            mesh = bpy.data.meshes.new("Transition")
            obj = bpy.data.objects.new("Transition", mesh)
            transition_type = blenderbim.core.root.assign_class(
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
            pset = ifcopenshell.api.run("pset.add_pset", tool.Ifc.get(), product=transition_type, name="BBIM_Fitting")
            ifcopenshell.api.run(
                "pset.edit_pset",
                tool.Ifc.get(),
                pset=pset,
                properties={"Data": json.dumps(transition_data, default=list)},
            )

        # NOTE: at this point we loose current blender objects selection
        bpy.ops.bim.add_constr_type_instance(relating_type_id=transition_type.id())
        transition_obj = bpy.context.active_object

        # adjust transition segment rotation and location
        transition_obj.matrix_world = start_object.matrix_world
        context.view_layer.update()
        transition_obj_dir = tool.Cad.get_edge_direction(tool.Model.get_flow_segment_axis(transition_obj))
        direction_match = tool.Cad.are_vectors_equal(transition_obj_dir, transition_dir)

        # if there are no mismatches or everything matches up we don't need to flip the transition
        if start_port_match != direction_match:
            transition_obj.matrix_world = start_object.matrix_world @ Matrix.Rotation(radians(180), 4, "X")
        transition_obj.location = start_segment_extend_point if start_port_match else end_segment_extend_point

        # add ports and connect them
        ports = tool.System.add_ports(transition_obj)
        if not start_port_match:
            start_port, end_port = end_port, start_port
        tool.Ifc.run("system.connect_port", port1=ports[0], port2=start_port, direction="NOTDEFINED")
        tool.Ifc.run("system.connect_port", port1=ports[1], port2=end_port, direction="NOTDEFINED")

        return {"FINISHED"}
