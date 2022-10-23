
# IfcSverchok - IFC Sverchok extension
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
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

from os.path import abspath, splitext
import bpy
import ifcopenshell
import ifcsverchok.helper
from ifcsverchok.ifcstore import SvIfcStore
from bpy.props import StringProperty, BoolProperty
from sverchok.node_tree import SverchCustomTreeNode
from sverchok.data_structure import updateNode, flatten_data


class SvIfcWriteFile(bpy.types.Node, SverchCustomTreeNode, ifcsverchok.helper.SvIfcCore):
    """
    Triggers: Ifc write to file
    Tooltip: Write active Sverchok Ifc file to path
    """
    def refresh_node_local(self, context):
        if self.refresh_local:
            self.process()
            self.refresh_local = False

    # out = ""
    refresh_local: BoolProperty(name="Write", description="Write to file", update=refresh_node_local)

    bl_idname = "SvIfcWriteFile"
    bl_label = "IFC Write File"
    path: StringProperty(name="path", description="File path to write to. Can be relative.",  update=updateNode)

    def sv_init(self, context):
        self.inputs.new("SvStringsSocket", "path").prop_name = "path"
        self.outputs.new("SvStringsSocket", "output")
        
    def draw_buttons(self, context, layout):
        row = layout.row(align=True)
        row.operator("node.sv_ifc_tooltip", text="", icon="QUESTION", emboss=False).tooltip = "Writes active Ifc file to path.\n It will overwrite an existing file."
        row.prop(self, 'refresh_local', icon='FILE_REFRESH')

    def process(self):
        path = flatten_data(self.inputs["path"].sv_get(), target_level = 1)[0]
        if not path:
            return
        path = abspath(path)
        file = SvIfcStore.get_file()
        _, ext = splitext(path)
        if not ext:
            raise Exception("Bad path. Provide a path to a file.")
        if self.refresh_local and ext:
            file.write(path)
        self.outputs["output"].sv_set(f"File written successfully to: {path}.")
        


def register():
    bpy.utils.register_class(SvIfcWriteFile)


def unregister():
    bpy.utils.unregister_class(SvIfcWriteFile)
