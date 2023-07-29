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


class MepGenerator:
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
            for mat, flow_direction in zip([start_port_matrix, end_port_matrix], ("SINK", "SOURCE")):
                port = tool.Ifc.run("system.add_port", element=element)
                port.FlowDirection = flow_direction
                tool.Ifc.run("geometry.edit_object_placement", product=port, matrix=obj.matrix_world @ mat, is_si=True)
            return

        # TODO: better way to find the port to be moved
        end_port = next((p for p in ports if p.FlowDirection == "SOURCE"), None)
        if not end_port:
            return
        tool.Model.edit_element_placement(end_port, obj.matrix_world @ end_port_matrix)
