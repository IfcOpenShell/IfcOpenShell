# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of BlenderBIM Add-on.
#
# BlenderBIM Add-on is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# BlenderBIM Add-on is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with BlenderBIM Add-on.  If not, see <http://www.gnu.org/licenses/>.

import bpy
import blenderbim.tool as tool
import blenderbim.core.context as core
import blenderbim.bim.module.context.data
from blenderbim.bim.ifc import IfcStore
from ifcopenshell.api.context.data import Data


class Operator:
    def execute(self, context):
        IfcStore.execute_ifc_operator(self, context)
        blenderbim.bim.module.context.data.ContextData.is_loaded = False
        return {"FINISHED"}


class AddSubcontext(bpy.types.Operator, Operator):
    bl_idname = "bim.add_subcontext"
    bl_label = "Add Subcontext"
    bl_options = {"REGISTER", "UNDO"}
    context: bpy.props.StringProperty()
    subcontext: bpy.props.StringProperty()
    target_view: bpy.props.StringProperty()

    def _execute(self, context):
        core.add_context(tool.Ifc, context=self.context, subcontext=self.subcontext, target_view=self.target_view)


class RemoveSubcontext(bpy.types.Operator, Operator):
    bl_idname = "bim.remove_subcontext"
    bl_label = "Remove Context"
    bl_options = {"REGISTER", "UNDO"}
    context: bpy.props.IntProperty()

    def _execute(self, context):
        core.remove_context(tool.Ifc, context=tool.Ifc.get().by_id(self.context))
