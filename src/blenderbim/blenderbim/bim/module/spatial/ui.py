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

from bpy.types import Panel, UIList
from blenderbim.bim.ifc import IfcStore
from ifcopenshell.api.spatial.data import Data


class BIM_PT_spatial(Panel):
    bl_label = "IFC Spatial Container"
    bl_idname = "BIM_PT_spatial"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"

    @classmethod
    def poll(cls, context):
        if not context.active_object:
            return False
        oprops = context.active_object.BIMObjectProperties
        if not oprops.ifc_definition_id:
            return False
        if not IfcStore.get_element(oprops.ifc_definition_id):
            return False
        if oprops.ifc_definition_id not in Data.products:
            Data.load(IfcStore.get_file(), oprops.ifc_definition_id)
        if not Data.products[oprops.ifc_definition_id]:
            return False
        return True

    def draw(self, context):
        oprops = context.active_object.BIMObjectProperties
        sprops = context.scene.BIMSpatialProperties
        props = context.active_object.BIMObjectSpatialProperties
        if not oprops.ifc_definition_id:
            return
        if oprops.ifc_definition_id not in Data.products:
            Data.load(IfcStore.get_file(), oprops.ifc_definition_id)

        if props.is_editing:
            row = self.layout.row(align=True)
            if sprops.active_decomposes_parent_id:
                op = row.operator("bim.change_spatial_level", text="", icon="FRAME_PREV")
                op.parent_id = sprops.active_decomposes_parent_id
            row.operator("bim.assign_container", icon="CHECKMARK")
            row.operator("bim.copy_to_container", icon="COPYDOWN", text="")
            row.operator("bim.disable_editing_container", icon="CANCEL", text="")

            self.layout.template_list(
                "BIM_UL_spatial_elements", "", sprops, "spatial_elements", sprops, "active_spatial_element_index"
            )
        else:
            row = self.layout.row(align=True)
            name = "{}/{}".format(
                Data.products[oprops.ifc_definition_id]["type"], Data.products[oprops.ifc_definition_id]["Name"]
            )
            if name == "None/None":
                name = "This object is not spatially contained"
            row.label(text=name)
            row.operator("bim.enable_editing_container", icon="GREASEPENCIL", text="")
            row.operator("bim.remove_container", icon="X", text="")


class BIM_UL_spatial_elements(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if item:
            if item.has_decomposition:
                op = layout.operator("bim.change_spatial_level", text="", icon="DISCLOSURE_TRI_RIGHT", emboss=False)
                op.parent_id = item.ifc_definition_id
            layout.label(text=item.name)
            layout.label(text=item.long_name)
            layout.prop(
                item,
                "is_selected",
                icon="CHECKBOX_HLT" if item.is_selected else "CHECKBOX_DEHLT",
                text="",
                emboss=False,
            )
