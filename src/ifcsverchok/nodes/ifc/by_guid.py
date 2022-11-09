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


class SvIfcByGuid(bpy.types.Node, SverchCustomTreeNode, ifcsverchok.helper.SvIfcCore):
    bl_idname = "SvIfcByGuid"
    bl_label = "IFC By Guid"
    file: StringProperty(name="file", update=updateNode)
    guid: StringProperty(name="guid", update=updateNode)

    def sv_init(self, context):
        self.inputs.new("SvStringsSocket", "file").prop_name = "file"
        self.inputs.new("SvStringsSocket", "guid").prop_name = "guid"
        self.outputs.new("SvStringsSocket", "entity")

    def process(self):
        self.sv_input_names = ["file", "guid"]
        super().process()

    def process_ifc(self, file, guid):
        self.outputs["entity"].sv_set([[file.by_guid(guid)]])


def register():
    bpy.utils.register_class(SvIfcByGuid)


def unregister():
    bpy.utils.unregister_class(SvIfcByGuid)
