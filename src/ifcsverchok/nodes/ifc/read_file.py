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
import ifcopenshell.guid
import ifcsverchok.helper
from bpy.props import StringProperty
from sverchok.node_tree import SverchCustomTreeNode
from sverchok.data_structure import updateNode


class SvIfcReadFile(bpy.types.Node, SverchCustomTreeNode, ifcsverchok.helper.SvIfcCore):
    bl_idname = "SvIfcReadFile"
    bl_label = "IFC Read File"
    path: StringProperty(name="path", update=updateNode)

    def sv_init(self, context):
        self.inputs.new("SvStringsSocket", "path").prop_name = "path"
        self.outputs.new("SvVerticesSocket", "file")

    def process(self):
        self.sv_input_names = ["path"]
        super().process()

    def process_ifc(self, path: str) -> None:
        guid = ifcopenshell.guid.new()
        ifcsverchok.helper.ifc_files[guid] = ifcopenshell.open(path)
        self.outputs["file"].sv_set([[ifcsverchok.helper.ifc_files[guid]]])


def register():
    bpy.utils.register_class(SvIfcReadFile)


def unregister():
    bpy.utils.unregister_class(SvIfcReadFile)
