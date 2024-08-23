# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of Bonsai.
#
# Bonsai is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Bonsai is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Bonsai.  If not, see <http://www.gnu.org/licenses/>.

import bpy
from bpy.types import Panel, UIList
from bonsai.bim.module.spatial.data import SpatialData, SpatialDecompositionData
import bonsai.tool as tool


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

        osprops = context.active_object.BIMObjectSpatialProperties

        if osprops.is_editing:
            if SpatialData.data["default_container"]:
                row = self.layout.row(align=True)
                row.prop(osprops, "container_obj", text="", icon="OUTLINER_COLLECTION")
                row.operator("bim.assign_container", icon="CHECKMARK", text="")
                row.operator("bim.disable_editing_container", icon="CANCEL", text="")

            if SpatialData.data["selected_containers"]:
                row = self.layout.row()
                row.label(text=f"{len(SpatialData.data['selected_containers'])} Selected Containers")
                for name in SpatialData.data["selected_containers"][:3]:
                    row = self.layout.row()
                    row.label(text=name, icon="OUTLINER_COLLECTION")
                if len(SpatialData.data["selected_containers"]) > 3:
                    row = self.layout.row()
                    row.label(text=f"... {len(SpatialData.data['selected_containers']) - 3} More")
                row = self.layout.row(align=True)
                row.operator("bim.reference_structure", icon="LINKED", text="Reference Selected")
                row.operator("bim.dereference_structure", icon="UNLINKED", text="")
                row = self.layout.row()
                row.operator("bim.copy_to_container", icon="COPYDOWN", text="Copy Object To Selected")
            else:
                row = self.layout.row()
                row.label(text="No Selected Containers")
        else:
            row = self.layout.row(align=True)
            if SpatialData.data["label"]:
                row.label(text=SpatialData.data["label"])
                row.operator("bim.select_container", icon="OBJECT_DATA", text="").container = 0
                row.operator("bim.select_similar_container", icon="RESTRICT_SELECT_OFF", text="")
                row.operator("bim.enable_editing_container", icon="GREASEPENCIL", text="")
                if SpatialData.data["is_directly_contained"]:
                    row.operator("bim.remove_container", icon="X", text="")
            else:
                row.label(text="No Spatial Container")
                row.operator("bim.enable_editing_container", icon="GREASEPENCIL", text="")

            if references := SpatialData.data["references"]:
                self.layout.label(text=f"{len(references)} References:")
            else:
                self.layout.label(text="No References Found")

            for reference in references:
                row = self.layout.row()
                row.label(text=reference, icon="LINKED")


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

        if SpatialDecompositionData.data["default_container"]:
            row = self.layout.row(align=True)
            row.label(
                text=f"Default: {SpatialDecompositionData.data['default_container']}",
                icon="OUTLINER_COLLECTION",
            )
        else:
            row = self.layout.row(align=True)
            row.label(text="Warning: No Default Container", icon="ERROR")
        row.operator("bim.import_spatial_decomposition", icon="FILE_REFRESH", text="")

        if self.props.active_container:
            ifc_definition_id = self.props.active_container.ifc_definition_id
            row = self.layout.row(align=True)
            row.prop(self.props, "subelement_class", text="")
            op = row.operator("bim.add_part_to_object", icon="ADD", text="")
            op.element = ifc_definition_id
            op.part_class = self.props.subelement_class

            row = self.layout.row(align=True)
            if self.props.active_container.ifc_class == "IfcProject":
                row.enabled = False
            op = row.operator("bim.set_default_container", icon="OUTLINER_COLLECTION", text="Set Default")
            op.container = ifc_definition_id
            op = row.operator("bim.set_container_visibility", icon="FULLSCREEN_EXIT", text="Isolate")
            op.mode = "ISOLATE"
            op.container = ifc_definition_id
            op = row.operator("bim.set_container_visibility", icon="HIDE_OFF", text="")
            op.mode = "SHOW"
            op.container = ifc_definition_id
            op = row.operator("bim.set_container_visibility", icon="HIDE_ON", text="")
            op.mode = "HIDE"
            op.container = ifc_definition_id
            row.operator("bim.select_container", icon="OBJECT_DATA", text="").container = ifc_definition_id
            op = row.operator("bim.delete_container", icon="X", text="")
            op.container = ifc_definition_id

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
            row = self.layout.row(align=True)
            row.label(text=f"{self.props.active_container.ifc_class} > No Contained Elements", icon="FILE_3D")
            row.prop(self.props, "should_include_children", text="", icon="OUTLINER")
            return

        row = self.layout.row(align=True)
        row.label(
            text=f"{self.props.active_container.ifc_class} > {self.props.total_elements} Contained Elements",
            icon="FILE_3D",
        )
        row.prop(self.props, "should_include_children", text="", icon="OUTLINER")
        op = row.operator("bim.select_decomposed_elements", icon="RESTRICT_SELECT_OFF", text="")
        op.container = ifc_definition_id

        self.layout.template_list(
            "BIM_UL_elements",
            "",
            self.props,
            "elements",
            self.props,
            "active_element_index",
            sort_lock=True,
        )


class BIM_UL_containers_manager(UIList):
    def __init__(self):
        self.use_filter_show = True

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if item:
            row = layout.row(align=True)
            self.draw_hierarchy(row, item)
            icon = {
                "IfcProject": "FILE",
                "IfcSite": "WORLD",
                "IfcBuilding": "HOME",
                "IfcBuildingStorey": "LINENUMBERS_OFF",
                "IfcSpace": "ANTIALIASED",
                "IfcFacilityPart": "MOD_FLUID",
                "IfcBridgePart": "MOD_FLUID",
                "IfcFacilityPartCommon": "MOD_FLUID",
                "IfcMarinePart": "MOD_FLUID",
                "IfcRailwayPart": "MOD_FLUID",
                "IfcRoadPart": "MOD_FLUID",
            }.get(item.ifc_class, "META_PLANE")
            row.prop(item, "name", emboss=False, text="", icon=icon)
            if item.long_name:
                row.prop(item, "long_name", emboss=False, text="")
            col = row.column()
            col.alignment = "RIGHT"
            col.prop(item, "elevation", emboss=False, text="")

    def draw_hierarchy(self, row, item):
        if item.level_index:
            for i in range(0, item.level_index - 1):
                row.label(text="", icon="BLANK1")
            if item.has_children:
                if item.is_expanded:
                    row.operator(
                        "bim.contract_container", text="", emboss=False, icon="DISCLOSURE_TRI_DOWN"
                    ).container = item.ifc_definition_id
                else:
                    row.operator(
                        "bim.expand_container", text="", emboss=False, icon="DISCLOSURE_TRI_RIGHT"
                    ).container = item.ifc_definition_id
            else:
                row.label(text="", icon="BLANK1")

    def draw_filter(self, context, layout):
        row = layout.row()
        row.prop(context.scene.BIMSpatialDecompositionProperties, "container_filter", text="", icon="VIEWZOOM")

    def filter_items(self, context, data, propname):
        items = getattr(data, propname)
        filter_name = context.scene.BIMSpatialDecompositionProperties.container_filter.lower()
        filter_flags = [self.bitflag_filter_item] * len(items)

        for idx, item in enumerate(items):
            if (
                filter_name in item.name.lower()
                or filter_name in item.long_name.lower()
                or filter_name in item.ifc_class.lower()
            ):
                filter_flags[idx] |= self.bitflag_filter_item
            else:
                filter_flags[idx] &= ~self.bitflag_filter_item

        return filter_flags, []

        items = getattr(data, propname)
        filter_name = context.scene.BIMSpatialDecompositionProperties.container_filter
        filtered = bpy.types.UI_UL_list.filter_items_by_name(filter_name, self.bitflag_filter_item, items, "name")
        return filtered, []


class BIM_UL_elements(UIList):
    def __init__(self):
        self.use_filter_show = True

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
                row.label(text=item.name)
                col = row.column()
                col.alignment = "RIGHT"
                col.label(text=str(item.total))

    def draw_filter(self, context, layout):
        row = layout.row()
        row.prop(context.scene.BIMSpatialDecompositionProperties, "element_filter", text="", icon="VIEWZOOM")

    def filter_items(self, context, data, propname):
        items = getattr(data, propname)
        filter_name = context.scene.BIMSpatialDecompositionProperties.element_filter
        filtered = bpy.types.UI_UL_list.filter_items_by_name(filter_name, self.bitflag_filter_item, items, "name")
        return filtered, []

    def get_filter_name(self):
        return self.filter_name
