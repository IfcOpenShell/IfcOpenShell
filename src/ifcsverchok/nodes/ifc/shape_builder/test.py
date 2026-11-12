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
import ifcsverchok.helper
import ifcsverchok.helper as helper
from sverchok.node_tree import SverchCustomTreeNode


class SvIfcSbTest(bpy.types.Node, SverchCustomTreeNode, ifcsverchok.helper.SvIfcCore):
    bl_idname = "SvIfcSbTest"
    bl_label = "IFC Test"

    def sv_init(self, context):
        helper.create_socket(
            self.inputs,
            "Input",
        )
        helper.create_socket(
            self.outputs,
            "Output",
            description="Extruded Profile",
        )

    def process(self):
        print("test!")
        self.sv_input_names = ["Input"]
        super().process()

    def process_ifc(self, input_value: float) -> None:
        self.outputs["Output"].sv_set([[input_value]])


def register():
    bpy.utils.register_class(SvIfcSbTest)


def unregister():
    bpy.utils.unregister_class(SvIfcSbTest)
