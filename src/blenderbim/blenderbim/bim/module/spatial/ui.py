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
from blenderbim.bim.module.spatial.data import SpatialData, SpatialDecompositionData
import blenderbim.tool as tool


class BIM_PT_spatial(Panel):
    bl_label = "Spatial Container"
    bl_idname = "BIM_PT_spatial"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"
    bl_parent_id = "BIM_PT_tab_object_metadata"

    @classmethod
    def poll(cls, context):
        if not SpatialData.is_loaded:
            SpatialData.load()
        return SpatialData.data["poll"]

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
            self.layout.prop(osprops, "relating_container_object")
        else:
            row = self.layout.row(align=True)
            if SpatialData.data["label"]:
                row.label(text=SpatialData.data["label"])
                row.operator("bim.select_container", icon="OBJECT_DATA", text="")
                row.operator("bim.select_similar_container", icon="RESTRICT_SELECT_OFF", text="")
                row.operator("bim.enable_editing_container", icon="GREASEPENCIL", text="")
                if SpatialData.data["is_directly_contained"]:
                    row.operator("bim.remove_container", icon="X", text="")
            else:
                row.label(text="No Spatial Container")
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


class BIM_PT_spatial_decomposition(Panel):
    bl_label = "Spatial Decomposition"
    bl_idname = "BIM_PT_spatial_decomposition"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_tab_spatial_decomposition"
    bl_options = {"HIDE_HEADER"}

    @classmethod
    def poll(cls, context):
        return tool.Ifc.get()

    def draw(self, context):
        if not SpatialDecompositionData.is_loaded:
            SpatialDecompositionData.load()
        self.props = context.scene.BIMSpatialDecompositionProperties

        if self.props.active_container:
            row = self.layout.row(align=True)
            row.label(
                text=f"Active: {self.props.active_container.name}",
                icon="OUTLINER_COLLECTION",
            )
            row.operator("bim.import_spatial_decomposition", icon="FILE_REFRESH", text="")

            if self.props.active_container.ifc_class != "IfcProject":
                row = self.layout.row(align=True)
                row.operator("bim.select_decomposed_elements", icon="HIDE_OFF", text=f"Isolate {self.props.active_container.ifc_class}")
                row.operator("bim.delete_container", icon="X", text="").container = (
                    self.props.active_container.ifc_definition_id
                )

            row = self.layout.row(align=True)
            row.prop(self.props, "subelement_class", text="")
            op = row.operator("bim.add_part_to_object", icon="ADD", text="")
            op.element = self.props.active_container.ifc_definition_id
            op.part_class = self.props.subelement_class
        else:
            row = self.layout.row(align=True)
            row.label(text="Warning: No Active Container", icon="ERROR")
            row.operator("bim.import_spatial_decomposition", icon="FILE_REFRESH", text="")

        self.layout.template_list(
            "BIM_UL_containers_manager",
            "",
            self.props,
            "containers",
            self.props,
            "active_container_index",
            rows=10,
        )

        if not self.props.active_container:
            return

        if not self.props.total_elements:
            row = self.layout.row()
            row.label(text="No Contained Elements", icon="FILE_3D")
            return

        row = self.layout.row(align=True)
        row.label(text=f"{self.props.total_elements} Contained Elements", icon="FILE_3D")
        row.operator("bim.select_decomposed_elements", icon="RESTRICT_SELECT_OFF", text="")

        self.layout.template_list(
            "BIM_UL_elements",
            "",
            self.props,
            "elements",
            self.props,
            "active_element_index",
        )


class BIM_UL_containers_manager(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if item:
            row = layout.row(align=True)
            self.draw_hierarchy(row, item)
            row.prop(item, "name", emboss=False, text="")
            if item.long_name:
                row.prop(item, "long_name", emboss=False, text="")
            col = row.column()
            col.alignment = "RIGHT"
            col.prop(item, "elevation", emboss=False, text="")

    def draw_hierarchy(self, row, item):
        for i in range(0, item.level_index):
            row.label(text="", icon="BLANK1")
        if item.has_children:
            if item.is_expanded:
                row.operator("bim.contract_container", text="", emboss=False, icon="DISCLOSURE_TRI_DOWN").container = (
                    item.ifc_definition_id
                )
            else:
                row.operator("bim.expand_container", text="", emboss=False, icon="DISCLOSURE_TRI_RIGHT").container = (
                    item.ifc_definition_id
                )
        else:
            row.label(text="", icon="BLANK1")
        if item.ifc_class == "IfcProject":
            row.label(text="", icon="FILE")
        elif item.ifc_class == "IfcSite":
            row.label(text="", icon="WORLD")
        elif item.ifc_class == "IfcBuilding":
            row.label(text="", icon="HOME")
        elif item.ifc_class == "IfcBuildingStorey":
            row.label(text="", icon="LINENUMBERS_OFF")
        elif item.ifc_class == "IfcSpace":
            row.label(text="", icon="ANTIALIASED")
        elif "Part" in item.ifc_class:
            row.label(text="", icon="MOD_FLUID")
        else:
            row.label(text="", icon="META_PLANE")


class BIM_UL_elements(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if item:
            row = layout.row(align=True)
            if item.is_class:
                row.label(text="", icon="DISCLOSURE_TRI_DOWN")
                row.label(text=item.name)
                col = row.column()
                col.alignment = "RIGHT"
                col.label(text=str(item.total))
            elif item.is_type:
                row.label(text="", icon="BLANK1")
                row.label(text="", icon="DISCLOSURE_TRI_DOWN")
                row.label(text=item.name)
                col = row.column()
                col.alignment = "RIGHT"
                col.label(text=str(item.total))
