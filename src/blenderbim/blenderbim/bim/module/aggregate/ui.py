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

from bpy.types import Panel
from blenderbim.bim.module.aggregate.data import AggregateData
from blenderbim.bim.ifc import IfcStore


class BIM_PT_aggregate(Panel):
    bl_label = "IFC Aggregates"
    bl_idname = "BIM_PT_aggregate"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"

    @classmethod
    def poll(cls, context):
        view_setting = context.preferences.addons["blenderbim"].preferences.module_visibility
        return view_setting.aggregate

    @classmethod
    def poll(cls, context):
        view_setting = context.preferences.addons["blenderbim"].preferences.module_visibility
        if not context.active_object:
            return False
        props = context.active_object.BIMObjectProperties
        if not props.ifc_definition_id:
            return False
        if not IfcStore.get_element(props.ifc_definition_id):
            return False
        if not IfcStore.get_file().by_id(props.ifc_definition_id).is_a("IfcObjectDefinition"):
            return False
        return view_setting.aggregate

    def draw(self, context):
        if not AggregateData.is_loaded:
            AggregateData.load()

        props = context.active_object.BIMObjectAggregateProperties

        if props.is_editing:
            row = self.layout.row(align=True)
            row.prop(props, "relating_object", text="")
            if props.relating_object:
                op = row.operator("bim.assign_object", icon="CHECKMARK", text="")
                op.relating_object = props.relating_object.BIMObjectProperties.ifc_definition_id
                op.related_object = context.active_object.BIMObjectProperties.ifc_definition_id
            row.operator("bim.disable_editing_aggregate", icon="CANCEL", text="")
        else:
            row = self.layout.row(align=True)
            if AggregateData.data["has_aggregate"]:
                row.label(text=AggregateData.data["label"])
                row.operator("bim.enable_editing_aggregate", icon="GREASEPENCIL", text="")
                row.operator("bim.add_aggregate", icon="ADD", text="")
                op = row.operator("bim.unassign_object", icon="X", text="")
                op.relating_object = AggregateData.data["relating_object_id"]
                op.related_object = context.active_object.BIMObjectProperties.ifc_definition_id
            else:
                row.label(text="No Aggregate Found")
                row.operator("bim.enable_editing_aggregate", icon="GREASEPENCIL", text="")
                row.operator("bim.add_aggregate", icon="ADD", text="")
