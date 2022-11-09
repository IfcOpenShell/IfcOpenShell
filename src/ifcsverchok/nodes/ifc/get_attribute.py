# IfcSverchok - IFC Sverchok extension
# Copyright (C) 2020, 2021, 2022 Dion Moult <dion@thinkmoult.com>
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
import ifcopenshell.util.element
import ifcsverchok.helper
from bpy.props import StringProperty
from sverchok.node_tree import SverchCustomTreeNode
from sverchok.data_structure import updateNode


class SvIfcGetAttribute(bpy.types.Node, SverchCustomTreeNode, ifcsverchok.helper.SvIfcCore):
    bl_idname = "SvIfcGetAttribute"
    bl_label = "IFC Get Attribute"
    entity: StringProperty(name="entity", update=updateNode)
    attribute_name: StringProperty(name="attribute_name", update=updateNode)

    def sv_init(self, context):
        self.inputs.new("SvStringsSocket", "entity").prop_name = "entity"
        self.inputs.new("SvStringsSocket", "attribute_name").prop_name = "attribute_name"
        self.outputs.new("SvStringsSocket", "value")

    def process(self):
        self.value_out = []
        entity_nested_inputs = self.inputs["entity"].sv_get()
        attribute_name = self.inputs["attribute_name"].sv_get()[0][0]
        for entities in entity_nested_inputs:
            if hasattr(entities, "__iter__"):
                for entity in entities:
                    self.process_ifc(entity, attribute_name)
            else:
                self.process_ifc(entities, attribute_name)
        self.outputs["value"].sv_set(self.value_out)

    def process_ifc(self, entity, attribute_name):
        try:
            if attribute_name.isnumeric():
                self.value_out.append(entity[int(attribute_name)])
            else:
                self.value_out.append(entity.get_info()[attribute_name])
        except:
            pass


def register():
    bpy.utils.register_class(SvIfcGetAttribute)


def unregister():
    bpy.utils.unregister_class(SvIfcGetAttribute)
