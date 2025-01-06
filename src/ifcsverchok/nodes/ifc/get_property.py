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
from ifcsverchok.ifcstore import SvIfcStore
from bpy.props import StringProperty
from sverchok.node_tree import SverchCustomTreeNode
from sverchok.data_structure import updateNode, flatten_data


class SvIfcGetProperty(bpy.types.Node, SverchCustomTreeNode, ifcsverchok.helper.SvIfcCore):
    bl_idname = "SvIfcGetProperty"
    bl_label = "IFC Get Property"
    entity: StringProperty(name="Entity Ids", update=updateNode)
    pset_name: StringProperty(
        name="Pset Name",
        description='Name of the property set, eg. "Pset_WallCommon".',
        update=updateNode,
    )
    prop_name: StringProperty(
        name="Prop Name",
        description='Name of the property, eg. "IsExternal".',
        update=updateNode,
    )

    def sv_init(self, context):
        self.inputs.new("SvStringsSocket", "entity_ids").prop_name = "entity"
        self.inputs.new("SvStringsSocket", "pset_name").prop_name = "pset_name"
        self.inputs.new("SvStringsSocket", "prop_name").prop_name = "prop_name"
        self.outputs.new("SvStringsSocket", "value")

    def draw_buttons(self, context, layout):
        layout.operator("node.sv_ifc_tooltip", text="", icon="QUESTION", emboss=False).tooltip = (
            "Get the value of a property of an IfcEntity. Can take multiple entity ids."
        )

    def process(self):
        self.sv_input_names = ["entity_ids", "pset_name", "prop_name"]
        entities_ids = flatten_data(self.inputs["entity_ids"].sv_get(), target_level=1)
        pset_name = flatten_data(self.inputs["pset_name"].sv_get(), target_level=1)[0]
        prop_name = flatten_data(self.inputs["prop_name"].sv_get(), target_level=1)[0]
        if not entities_ids[0]:
            return
        self.file = SvIfcStore.get_file()
        try:
            self.entities = [self.file.by_id(int(step_id)) for step_id in entities_ids]
        except Exception as e:
            raise Exception(f"Invalid entity id: {e}")

        self.value_out = []
        for entity in self.entities:
            try:
                self.value_out.append(ifcopenshell.util.element.get_psets(entity)[pset_name][prop_name])
            except:
                pass
        self.outputs["value"].sv_set(self.value_out)


def register():
    bpy.utils.register_class(SvIfcGetProperty)


def unregister():
    bpy.utils.unregister_class(SvIfcGetProperty)
