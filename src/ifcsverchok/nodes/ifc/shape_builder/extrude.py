# IfcSverchok - IFC Sverchok extension
# Copyright (C) 2022 Martina Jakubowska <martina@jakubowska.dk>
#
# This file is part of IfcSverchok.
#
# IfcSverchok is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcSverchok is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with IfcSverchok.  If not, see <http://www.gnu.org/licenses/>.

import bpy
import ifcopenshell
import ifcopenshell.api
import ifcopenshell.api.context
import ifcopenshell.api.root
import ifcopenshell.api.unit
from ifcopenshell.util.shape_builder import ShapeBuilder
from sverchok.node_tree import SverchCustomTreeNode

import ifcsverchok.helper
import ifcsverchok.helper as helper
from ifcsverchok.nodes.ifc.add_pset import flatten_data


class SvIfcSbExtrude(bpy.types.Node, SverchCustomTreeNode, ifcsverchok.helper.SvIfcCore):
    bl_idname = "SvIfcSbExtrude"
    bl_label = "IFC Extrude"

    def sv_init(self, context):
        helper.create_socket(
            self.inputs,
            "Curve",
            description="Curve to extrude",
            data_type="list[list[ifcopenshell.entity_instance]]",
        )
        helper.create_socket(
            self.inputs,
            "Magnitude",
            data_type="list[list[float]]",
        )
        helper.create_socket(
            self.inputs,
            "Position",
            data_type="list[list[tuple[float, float, float]]]",
        )
        helper.create_socket(
            self.outputs,
            "Extruded Profile",
            description="Extruded Profile",
            data_type="list[list[ifcopenshell.entity_instance]]",
        )

    def process(self):
        self.file = helper.get_file()
        curve: ifcopenshell.entity_instance = helper.get_socket_value(self.inputs, "Curve")
        magnitude: float = helper.get_socket_value(self.inputs, "Magnitude")
        position: tuple[float, float, float] = helper.get_socket_value(self.inputs, "Position")
        builder = ShapeBuilder(self.file)
        extrude = builder.extrude(curve, magnitude=magnitude, position=position)
        helper.set_socket_value(self.outputs, "Extruded Profile", extrude)


def register():
    bpy.utils.register_class(SvIfcSbExtrude)


def unregister():
    bpy.utils.unregister_class(SvIfcSbExtrude)
