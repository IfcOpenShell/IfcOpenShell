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
import blenderbim.core.aggregate as core
import blenderbim.bim.handler
from blenderbim.bim.ifc import IfcStore


class Operator:
    def execute(self, context):
        IfcStore.execute_ifc_operator(self, context)
        blenderbim.bim.handler.refresh_ui_data()
        return {"FINISHED"}


class AssignObject(bpy.types.Operator, Operator):
    bl_idname = "bim.assign_object"
    bl_label = "Assign Object"
    bl_options = {"REGISTER", "UNDO"}
    relating_object: bpy.props.IntProperty()
    related_object: bpy.props.IntProperty()

    def _execute(self, context):
        core.assign_object(
            tool.Ifc,
            tool.Aggregator,
            tool.Collector,
            relating_obj=tool.Ifc.get_object(tool.Ifc.get().by_id(self.relating_object)),
            related_obj=tool.Ifc.get_object(tool.Ifc.get().by_id(self.related_object)),
        )


class EnableEditingAggregate(bpy.types.Operator, Operator):
    bl_idname = "bim.enable_editing_aggregate"
    bl_label = "Enable Editing Aggregate"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.enable_editing_aggregate(tool.Aggregator, obj=context.active_object)


class DisableEditingAggregate(bpy.types.Operator, Operator):
    bl_idname = "bim.disable_editing_aggregate"
    bl_label = "Disable Editing Aggregate"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.disable_editing_aggregate(tool.Aggregator, obj=context.active_object)


class AddAggregate(bpy.types.Operator):
    bl_idname = "bim.add_aggregate"
    bl_label = "Add Aggregate"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        obj = bpy.data.objects.get(self.obj) if self.obj else context.active_object
        aggregate_collection = bpy.data.collections.new("IfcElementAssembly/Assembly")
        context.scene.collection.children.link(aggregate_collection)
        aggregate = bpy.data.objects.new("Assembly", None)
        aggregate_collection.objects.link(aggregate)
        bpy.ops.bim.assign_class(obj=aggregate.name, ifc_class="IfcElementAssembly")
        bpy.ops.bim.assign_object(related_object=obj.name, relating_object=aggregate.name)
        return {"FINISHED"}
