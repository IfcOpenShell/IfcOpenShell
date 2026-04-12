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

from typing import TYPE_CHECKING, Literal

import bpy
import ifcopenshell
import ifcsverchok.helper
import ifcsverchok.helper as helper
from ifcopenshell.util.shape_builder import ShapeBuilder
from sverchok.core.sockets import SvVerticesSocket
from sverchok.data_structure import updateNode
from sverchok.node_tree import SverchCustomTreeNode


class SvIfcSbExtrude(bpy.types.Node, SverchCustomTreeNode, ifcsverchok.helper.SvIfcCore):
    bl_idname = "SvIfcSbExtrude"
    bl_label = "IFC Extrude"

    extrude_axis: bpy.props.EnumProperty(
        default="Z",
        items=[
            ("X", "X", "Interpret curve as in XY plane and extrude along X+."),
            ("Y", "Y", "Interpret curve as in XZ plane and extrude along Y+."),
            ("Z", "Z", "Interpret curve as in XY plane and extrude along Z+."),
        ],
        name="Extrude Axis",
        update=updateNode,
    )

    if TYPE_CHECKING:
        extrude_axis: Literal["X", "Y", "Z"]

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
            socket_type=SvVerticesSocket,
        )
        helper.create_socket(
            self.outputs,
            "Extruded Profile",
            description="Extruded Profile",
            data_type="list[list[ifcopenshell.entity_instance]]",
        )

    def draw_buttons(self, context, layout):
        layout.prop(self, "extrude_axis")

    def process(self):
        self.file = helper.get_file()
        curve: ifcopenshell.entity_instance = helper.get_socket_value(self.inputs, "Curve")
        magnitude: float = helper.get_socket_value(self.inputs, "Magnitude")
        position: tuple[float, float, float] = helper.get_socket_value(self.inputs, "Position")
        builder = ShapeBuilder(self.file)
        axis_kargs = builder.extrude_kwargs(self.extrude_axis)
        extrude = builder.extrude(curve, magnitude=magnitude, position=position, **axis_kargs)
        helper.set_socket_value(self.outputs, "Extruded Profile", extrude)


def register():
    bpy.utils.register_class(SvIfcSbExtrude)


def unregister():
    bpy.utils.unregister_class(SvIfcSbExtrude)
