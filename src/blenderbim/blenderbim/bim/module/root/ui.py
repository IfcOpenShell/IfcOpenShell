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
import blenderbim.bim.module.root.prop as root_prop
from bpy.types import Panel
from blenderbim.bim.ifc import IfcStore
from blenderbim.bim.helper import prop_with_search
from blenderbim.bim.module.root.data import IfcClassData


class BIM_PT_class(Panel):
    bl_label = "IFC Class"
    bl_idname = "BIM_PT_class"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"
    bl_parent_id = "BIM_PT_object_metadata"

    @classmethod
    def poll(cls, context):
        if not context.active_object:
            return False
        return IfcStore.get_file()

    def draw(self, context):
        if not IfcClassData.is_loaded:
            IfcClassData.load()
        props = context.active_object.BIMObjectProperties
        if props.ifc_definition_id:
            if not IfcClassData.data["has_entity"]:
                row = self.layout.row(align=True)
                row.label(text="IFC Element Not Found")
                row.operator("bim.unlink_object", icon="UNLINKED", text="")
                return
            if props.is_reassigning_class:
                row = self.layout.row(align=True)
                row.operator("bim.reassign_class", icon="CHECKMARK")
                row.operator("bim.disable_reassign_class", icon="CANCEL", text="")
                self.draw_class_dropdowns(
                    context,
                    root_prop.get_ifc_predefined_types(context.scene.BIMRootProperties, context),
                    is_reassigning_class=True,
                )
            else:
                row = self.layout.row(align=True)
                row.label(text=IfcClassData.data["name"])
                op = row.operator("bim.select_ifc_class", text="", icon="RESTRICT_SELECT_OFF")
                op.ifc_class = IfcClassData.data["ifc_class"]
                row.operator("bim.copy_class", icon="DUPLICATE", text="")
                row.operator("bim.unlink_object", icon="UNLINKED", text="")
                if IfcStore.get_file().by_id(props.ifc_definition_id).is_a("IfcRoot"):
                    row.operator("bim.enable_reassign_class", icon="GREASEPENCIL", text="")
        else:
            ifc_predefined_types = root_prop.get_ifc_predefined_types(context.scene.BIMRootProperties, context)
            self.draw_class_dropdowns(context, ifc_predefined_types)
            row = self.layout.row(align=True)
            op = row.operator("bim.assign_class")
            op.ifc_class = context.scene.BIMRootProperties.ifc_class
            op.predefined_type = context.scene.BIMRootProperties.ifc_predefined_type if ifc_predefined_types else ""
            op.userdefined_type = context.scene.BIMRootProperties.ifc_userdefined_type

    def draw_class_dropdowns(self, context, ifc_predefined_types, is_reassigning_class=False):
        props = context.scene.BIMRootProperties
        layout = self.layout
        if not is_reassigning_class:
            prop_with_search(layout, props, "ifc_product")
        prop_with_search(layout, props, "ifc_class")
        if ifc_predefined_types:
            prop_with_search(layout, props, "ifc_predefined_type")
            if props.ifc_predefined_type == "USERDEFINED":
                row = layout.row()
                row.prop(props, "ifc_userdefined_type")
        if not is_reassigning_class:
            prop_with_search(layout, props, "contexts")
