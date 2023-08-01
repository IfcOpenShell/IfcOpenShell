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
            # TODO: what are the best default directions here?
            for mat, flow_direction in zip([start_port_matrix, end_port_matrix], ("SINK", "SOURCE")):
                port = tool.Ifc.run("system.add_port", element=element)
                port.FlowDirection = flow_direction
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

        # TODO: what's best default direction here?
        tool.Ifc.run("system.connect_port", port1=related_port, port2=obstruction_port, direction="SOURCE")
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
    at_segment_start: bpy.props.BoolProperty(
        name="At Segment Start",
        description="Whether to add obstruction at the segment start or at the end",
        default=False,
    )

    def _execute(self, context):
        if self.segment_id:
            element = tool.Ifc.get().by_id(self.segment_id)
        else:
            element = tool.Ifc.get_entity(context.active_object)
        if not element:
            return {"CANCELLED"}

        obstruction, error_msg = MEPGenerator().add_obstruction(element, self.length, self.at_segment_start)
        if error_msg:
            self.report({"ERROR"}, error_msg)
            return {"CANCELLED"}

        return {"FINISHED"}
