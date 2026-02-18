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
import ifcsverchok.helper
import ifcsverchok.helper as helper
from ifcopenshell.util.shape_builder import ShapeBuilder
from sverchok.node_tree import SverchCustomTreeNode


class SvIfcSbRectangle(bpy.types.Node, SverchCustomTreeNode, ifcsverchok.helper.SvIfcCore):
    bl_idname = "SvIfcSbRectangle"
    bl_label = "IFC Rectangle"

    def sv_init(self, context):
        helper.create_socket(
            self.inputs,
            "Size (2D)",
            data_type="list[list[tuple[float, float]]]",
        )
        helper.create_socket(
            self.outputs,
            "Rectangle",
            description="Rectangle",
            data_type="list[list[ifcopenshell.entity_instance]]",
        )

    def process(self):
        file = helper.get_file()
        builder = ShapeBuilder(file)
        size: tuple[float, ...] = helper.get_socket_value(self.inputs, "Size", value_type="CONTAINER")
        rectangle = builder.rectangle(size=size)
        helper.set_socket_value(self.outputs, "Rectangle", rectangle)


def register():
    bpy.utils.register_class(SvIfcSbRectangle)


def unregister():
    bpy.utils.unregister_class(SvIfcSbRectangle)
