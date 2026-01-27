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
import ifcopenshell.geom
import ifcopenshell.ifcopenshell_wrapper as W
import ifcopenshell.util.shape
import ifcsverchok.helper as helper
import sverchok.core.sockets
from sverchok.node_tree import SverchCustomTreeNode


class SvSbShapeOutput(bpy.types.Node, SverchCustomTreeNode, helper.SvIfcCore):
    """
    Triggers: Ifc create shape by entity
    Tooltip: Convert IfcShapeRepresentation to geometry data.
    """

    bl_idname = "SvSbShapeOutput"
    bl_label = "IFC Shape Output"

    def sv_init(self, context):
        helper.create_socket(self.inputs, "Representation", data_type="list[list[ifcopenshell.entity_instance]]")
        helper.create_socket(self.outputs, "Vers", socket_type=sverchok.core.sockets.SvVerticesSocket)
        helper.create_socket(self.outputs, "Edgs")
        helper.create_socket(self.outputs, "Pols")

    def process(self):
        entity: ifcopenshell.entity_instance = helper.get_socket_value(self.inputs, "Representation")
        self.create(entity)
        helper.set_socket_value(self.outputs, "Vers", [self.verts], value_type="FINAL_VALUE")
        helper.set_socket_value(self.outputs, "Edgs", [self.edges], value_type="FINAL_VALUE")
        helper.set_socket_value(self.outputs, "Pols", [self.polys], value_type="FINAL_VALUE")

    def create(self, entity: ifcopenshell.entity_instance) -> None:
        assert bpy.context.scene
        settings = ifcopenshell.geom.settings()
        settings.set("dimensionality", ifcopenshell.ifcopenshell_wrapper.CURVES_SURFACES_AND_SOLIDS)
        shape = ifcopenshell.geom.create_shape(settings, entity)
        assert isinstance(shape, W.Triangulation)
        self.verts = ifcopenshell.util.shape.get_vertices(shape).tolist()
        self.edges = ifcopenshell.util.shape.get_edges(shape).tolist()
        self.polys = ifcopenshell.util.shape.get_faces(shape).tolist()


def register():
    bpy.utils.register_class(SvSbShapeOutput)


def unregister():
    bpy.utils.unregister_class(SvSbShapeOutput)
