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
import ifcsverchok.helper
from bpy.props import StringProperty
from sverchok.node_tree import SverchCustomTreeNode
from sverchok.data_structure import updateNode
from typing import Union


class SvIfcRemove(bpy.types.Node, SverchCustomTreeNode, ifcsverchok.helper.SvIfcCore):
    bl_idname = "SvIfcRemove"
    bl_label = "IFC Remove"
    file: StringProperty(name="file", update=updateNode)
    entity: StringProperty(name="entity", update=updateNode)

    def sv_init(self, context):
        self.inputs.new("SvStringsSocket", "file").prop_name = "file"
        self.inputs.new("SvStringsSocket", "entity").prop_name = "entity"
        self.outputs.new("SvStringsSocket", "file")

    def process(self):
        file: ifcopenshell.file
        file = self.inputs["file"].sv_get()[0][0]
        self.new_file = ifcopenshell.file.from_string(file.wrapped_data.to_string())
        self.remove_entity(self.inputs["entity"].sv_get())
        self.outputs["file"].sv_set([[self.new_file]])

    def remove_entity(
        self,
        entity: Union[
            list[list[ifcopenshell.entity_instance]],
            list[ifcopenshell.entity_instance],
            ifcopenshell.entity_instance,
        ],
    ) -> None:
        if isinstance(entity, (tuple, list)):
            for e in entity:
                self.remove_entity(e)
        else:
            self.new_file.remove(self.new_file.by_id(entity.id()))


def register():
    bpy.utils.register_class(SvIfcRemove)


def unregister():
    bpy.utils.unregister_class(SvIfcRemove)
