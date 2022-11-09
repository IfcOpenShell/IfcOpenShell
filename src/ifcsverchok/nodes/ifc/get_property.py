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


class SvIfcGetProperty(bpy.types.Node, SverchCustomTreeNode, ifcsverchok.helper.SvIfcCore):
    bl_idname = "SvIfcGetProperty"
    bl_label = "IFC Get Property"
    entity: StringProperty(name="entity", update=updateNode)
    pset_name: StringProperty(name="pset_name", update=updateNode)
    prop_name: StringProperty(name="prop_name", update=updateNode)

    def sv_init(self, context):
        self.inputs.new("SvStringsSocket", "entity").prop_name = "entity"
        self.inputs.new("SvStringsSocket", "pset_name").prop_name = "pset_name"
        self.inputs.new("SvStringsSocket", "prop_name").prop_name = "prop_name"
        self.outputs.new("SvStringsSocket", "value")

    def process(self):
        self.sv_input_names = ["entity", "pset_name", "prop_name"]
        self.value_out = []
        super().process()
        self.outputs["value"].sv_set(self.value_out)

    def process_ifc(self, entity, pset_name, prop_name):
        try:
            self.value_out.append(ifcopenshell.util.element.get_psets(entity)[pset_name][prop_name])
        except:
            pass


def register():
    bpy.utils.register_class(SvIfcGetProperty)


def unregister():
    bpy.utils.unregister_class(SvIfcGetProperty)
