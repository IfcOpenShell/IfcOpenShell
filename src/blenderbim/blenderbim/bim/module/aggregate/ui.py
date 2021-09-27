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
from ifcopenshell.api.aggregate.data import Data
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
        if not context.active_object:
            return False
        props = context.active_object.BIMObjectProperties
        if not props.ifc_definition_id:
            return False
        if not IfcStore.get_element(props.ifc_definition_id):
            return False
        if not IfcStore.get_file().by_id(props.ifc_definition_id).is_a("IfcObjectDefinition"):
            return False
        if props.ifc_definition_id not in Data.products:
            Data.load(IfcStore.get_file(), props.ifc_definition_id)
        if not Data.products[props.ifc_definition_id]:
            return False
        return True

    def draw(self, context):
        props = context.active_object.BIMObjectProperties
        if not props.ifc_definition_id:
            return
        if props.ifc_definition_id not in Data.products:
            Data.load(IfcStore.get_file(), props.ifc_definition_id)

        if props.is_editing_aggregate:
            row = self.layout.row(align=True)
            row.prop(props, "relating_object", text="")
            if props.relating_object:
                row.operator(
                    "bim.assign_object", icon="CHECKMARK", text=""
                ).relating_object = props.relating_object.name
            row.operator("bim.disable_editing_aggregate", icon="CANCEL", text="")
        else:
            row = self.layout.row(align=True)
            name = "{}/{}".format(
                Data.products[props.ifc_definition_id]["type"], Data.products[props.ifc_definition_id]["Name"]
            )
            if name == "None/None":
                name = "No Aggregate Found"
            row.label(text=name)
            row.operator("bim.enable_editing_aggregate", icon="GREASEPENCIL", text="")
            row.operator("bim.add_aggregate", icon="ADD", text="")
