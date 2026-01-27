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
import ifcsverchok.helper as helper
import sverchok.core.sockets
from ifcsverchok.nodes.ifc.shape_builder.representation import ShapeBuilder
from sverchok.node_tree import SverchCustomTreeNode


class SvSbMesh(bpy.types.Node, SverchCustomTreeNode, helper.SvIfcCore):
    bl_idname = "SvSbMesh"
    bl_label = "IFC Mesh"

    def sv_init(self, context):
        helper.create_socket(self.inputs, "Vers", socket_type=sverchok.core.sockets.SvVerticesSocket)
        helper.create_socket(self.inputs, "Pols")
        helper.create_socket(self.outputs, "Representation Item", data_type="list[list[ifcopenshell.entity_instance]]")

    def process(self):
        ifc_file = helper.get_file()

        vertices: list[[list[float]]] = helper.get_socket_value(self.inputs, "Vers", value_type="CONTAINER")
        polygons: list[[list[int]]] = helper.get_socket_value(self.inputs, "Pols", value_type="CONTAINER")

        builder = ShapeBuilder(ifc_file)
        mesh = builder.mesh(vertices, polygons)
        helper.set_socket_value(self.outputs, "Representation Item", mesh)


def register():
    bpy.utils.register_class(SvSbMesh)


def unregister():
    bpy.utils.unregister_class(SvSbMesh)
