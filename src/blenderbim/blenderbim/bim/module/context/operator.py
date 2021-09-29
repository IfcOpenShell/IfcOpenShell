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
import ifcopenshell.api
import blenderbim.bim.tool
import blenderbim.core.context
from blenderbim.bim.ifc import IfcStore
from ifcopenshell.api.context.data import Data


class AddSubcontext(bpy.types.Operator):
    bl_idname = "bim.add_subcontext"
    bl_label = "Add Subcontext"
    bl_options = {"REGISTER", "UNDO"}
    context: bpy.props.StringProperty()
    subcontext: bpy.props.StringProperty()
    target_view: bpy.props.StringProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        blenderbim.core.context.AddContext(
            blenderbim.bim.tool.Ifc,
            context=self.context or context.scene.BIMProperties.available_contexts,
            subcontext=self.subcontext or context.scene.BIMProperties.available_subcontexts,
            target_view=self.target_view or context.scene.BIMProperties.available_target_views,
        ).execute()
        Data.load(IfcStore.get_file())
        return {"FINISHED"}


class RemoveSubcontext(bpy.types.Operator):
    bl_idname = "bim.remove_subcontext"
    bl_label = "Remove Context"
    bl_options = {"REGISTER", "UNDO"}
    ifc_definition_id: bpy.props.IntProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        self.file = IfcStore.get_file()
        blenderbim.core.context.RemoveContext(
            blenderbim.bim.tool.Ifc, context=self.file.by_id(self.ifc_definition_id)
        ).execute()
        Data.load(self.file)
        return {"FINISHED"}
