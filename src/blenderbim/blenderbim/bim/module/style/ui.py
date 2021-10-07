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

import blenderbim.bim.helper
from bpy.types import Panel
from blenderbim.bim.ifc import IfcStore
from blenderbim.bim.module.style.data import StyleAttributesData


class BIM_PT_style(Panel):
    bl_label = "IFC Style"
    bl_idname = "BIM_PT_style"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "material"

    @classmethod
    def poll(cls, context):
        return (
            IfcStore.get_file()
            and context.active_object is not None
            and context.active_object.active_material is not None
        )

    def draw(self, context):
        props = context.active_object.active_material.BIMMaterialProperties
        row = self.layout.row(align=True)
        if props.ifc_style_id:
            row.operator("bim.update_style_colours", icon="GREASEPENCIL")
            row.operator("bim.unlink_style", icon="UNLINKED", text="")
            row.operator("bim.remove_style", icon="X", text="")
        else:
            row.operator("bim.add_style", icon="ADD")


class BIM_PT_style_attributes(Panel):
    bl_label = "IFC Style Attributes"
    bl_idname = "BIM_PT_style_attributes"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "material"

    @classmethod
    def poll(cls, context):
        if not IfcStore.get_file():
            return False
        try:
            return bool(context.active_object.active_material.BIMMaterialProperties.ifc_style_id)
        except:
            return False

    def draw(self, context):
        if not StyleAttributesData.is_loaded:
            StyleAttributesData.load()

        obj = context.active_object.active_material
        mprops = obj.BIMMaterialProperties
        props = obj.BIMStyleProperties
        if props.is_editing:
            row = self.layout.row(align=True)
            row.operator("bim.edit_style", icon="CHECKMARK")
            row.operator("bim.disable_editing_style", icon="CANCEL", text="")
            blenderbim.bim.helper.draw_attributes(props.attributes, self.layout)
        else:
            row = self.layout.row()
            row.operator("bim.enable_editing_style", icon="GREASEPENCIL", text="Edit")

            row = self.layout.row(align=True)
            row.label(text="STEP ID")
            row.label(text=str(mprops.ifc_style_id))

            for attribute in StyleAttributesData.data["attributes"]:
                row = self.layout.row(align=True)
                row.label(text=attribute["name"])
                row.label(text=attribute["value"])
