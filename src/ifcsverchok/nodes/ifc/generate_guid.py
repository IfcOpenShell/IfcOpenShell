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
from sverchok.node_tree import SverchCustomTreeNode


class SvIfcGenerateGuid(bpy.types.Node, SverchCustomTreeNode, ifcsverchok.helper.SvIfcCore):
    bl_idname = "SvIfcGenerateGuid"
    bl_label = "IFC Generate Guid"

    def sv_init(self, context):
        self.outputs.new("SvStringsSocket", "guid")

    def process(self):
        self.outputs["guid"].sv_set([[ifcopenshell.guid.new()]])


def register():
    bpy.utils.register_class(SvIfcGenerateGuid)


def unregister():
    bpy.utils.unregister_class(SvIfcGenerateGuid)
