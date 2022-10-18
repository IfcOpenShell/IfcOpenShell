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
from blenderbim.bim.module.spatial.data import SpatialData


class BIM_PT_spatial(Panel):
    bl_label = "IFC Spatial Container"
    bl_idname = "BIM_PT_spatial"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"
    bl_parent_id = "BIM_PT_object_metadata"

    @classmethod
    def poll(cls, context):
        if not context.active_object:
            return False
        oprops = context.active_object.BIMObjectProperties
        if not oprops.ifc_definition_id:
            return False
        if not IfcStore.get_element(oprops.ifc_definition_id):
            return False
        return True

    def draw(self, context):
        if not SpatialData.is_loaded:
            SpatialData.load()

        props = context.scene.BIMSpatialProperties
        osprops = context.active_object.BIMObjectSpatialProperties

        if osprops.is_editing:
            row = self.layout.row(align=True)
            if SpatialData.data["parent_container_id"]:
                op = row.operator("bim.change_spatial_level", text="", icon="FRAME_PREV")
                op.parent = SpatialData.data["parent_container_id"]
            if props.containers and props.active_container_index < len(props.containers):
                op = row.operator("bim.assign_container", icon="CHECKMARK")
                op.structure = props.containers[props.active_container_index].ifc_definition_id
            row.operator("bim.reference_structure", icon="LINKED", text="")
            row.operator("bim.dereference_structure", icon="UNLINKED", text="")
            row.operator("bim.copy_to_container", icon="COPYDOWN", text="")
            row.operator("bim.disable_editing_container", icon="CANCEL", text="")

            self.layout.template_list("BIM_UL_containers", "", props, "containers", props, "active_container_index")
        else:
            row = self.layout.row(align=True)
            if SpatialData.data["label"]:
                row.label(text=SpatialData.data["label"])
                row.operator("bim.select_container", icon="TRACKER", text="")
                row.operator("bim.select_similar_container", icon="RESTRICT_SELECT_OFF", text="")
                row.operator("bim.enable_editing_container", icon="GREASEPENCIL", text="")
                if SpatialData.data["is_directly_contained"]:
                    row.operator("bim.remove_container", icon="X", text="")
            else:
                row.label(text="This object is not spatially contained")
                row.operator("bim.enable_editing_container", icon="GREASEPENCIL", text="")
            for reference in SpatialData.data["references"]:
                row = self.layout.row()
                row.label(text=reference, icon="LINKED")


class BIM_UL_containers(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if item:
            if item.has_decomposition:
                op = layout.operator("bim.change_spatial_level", text="", icon="DISCLOSURE_TRI_RIGHT", emboss=False)
                op.parent = item.ifc_definition_id
            layout.label(text=item.name)
            layout.label(text=item.long_name)
            layout.prop(
                item,
                "is_selected",
                icon="CHECKBOX_HLT" if item.is_selected else "CHECKBOX_DEHLT",
                text="",
                emboss=False,
            )
