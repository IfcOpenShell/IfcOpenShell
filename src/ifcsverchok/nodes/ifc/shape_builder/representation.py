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
import ifcopenshell.util.representation
import ifcsverchok.helper
import ifcsverchok.helper as helper
from ifcopenshell.util.shape_builder import ShapeBuilder
from sverchok.node_tree import SverchCustomTreeNode


class SvIfcSbRepresentation(bpy.types.Node, SverchCustomTreeNode, ifcsverchok.helper.SvIfcCore):
    bl_idname = "SvIfcSbRepresentation"
    bl_label = "IFC Representation"

    def sv_init(self, context):
        helper.create_socket(
            self.inputs,
            "Representation Item",
            description="Representation Item",
            data_type="list[list[ifcopenshell.entity_instance]]",
        )
        helper.create_socket(
            self.outputs,
            "Shape Representation",
            description="IfcShapeRepresentation",
            data_type="list[list[ifcopenshell.entity_instance]]",
        )

    def process(self):
        self.file = helper.get_file()
        representation_items: list[ifcopenshell.entity_instance]
        representation_items = helper.get_socket_value(self.inputs, "Representation Item", value_type="FLATTEN")

        builder = ShapeBuilder(self.file)
        context = ifcopenshell.util.representation.get_context(self.file, "Model", "Body", "MODEL_VIEW")
        assert context is not None
        representation = builder.get_representation(context, items=representation_items)
        helper.set_socket_value(self.outputs, "Shape Representation", representation)


def register():
    bpy.utils.register_class(SvIfcSbRepresentation)


def unregister():
    bpy.utils.unregister_class(SvIfcSbRepresentation)
