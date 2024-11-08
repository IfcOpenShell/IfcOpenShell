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
from bonsai.bim.ifc import IfcStore
import bonsai.tool as tool
from bonsai.bim.module.boundary.data import SpaceBoundariesData


class BIM_PT_SceneBoundaries(Panel):
    bl_label = "Space Boundaries"
    bl_id_name = "BIM_PT_scene_boundaries"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_tab_geometry"

    @classmethod
    def poll(cls, context):
        return IfcStore.get_file()

    def draw(self, context):
        row = self.layout.row(align=True)
        row.operator("bim.load_project_space_boundaries")
        row.operator("bim.select_project_space_boundaries", text="", icon="RESTRICT_SELECT_OFF")
        row.operator("bim.colour_by_related_building_element", text="", icon="BRUSH_DATA")


class BIM_PT_Boundary(Panel):
    bl_label = "Space Boundary"
    bl_idname = "BIM_PT_Boundary"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"
    bl_parent_id = "BIM_PT_tab_geometric_relationships"

    @classmethod
    def poll(cls, context):
        if not context.active_object:
            return False
        props = context.active_object.BIMObjectProperties
        if not props.ifc_definition_id:
            return False
        if not IfcStore.get_element(props.ifc_definition_id):
            return False
        entity = IfcStore.get_file().by_id(props.ifc_definition_id)
        return entity.is_a("IfcRelSpaceBoundary")

    def draw(self, context):
        props = context.active_object.BIMObjectProperties
        ifc_file = tool.Ifc.get()
        boundary = ifc_file.by_id(props.ifc_definition_id)
        self.bprops = context.active_object.bim_boundary_properties
        if self.bprops.is_editing:
            row = self.layout.row(align=True)
            row.operator("bim.edit_boundary_attributes", icon="CHECKMARK", text="Save Attributes")
            row.operator("bim.disable_editing_boundary", icon="CANCEL", text="")
            self.draw_relation_editor(boundary, "RelatingSpace", "relating_space")
            self.draw_relation_editor(boundary, "RelatedBuildingElement", "related_building_element")
            self.draw_relation_editor(boundary, "ParentBoundary", "parent_boundary")
            self.draw_relation_editor(boundary, "CorrespondingBoundary", "corresponding_boundary")
        else:
            row = self.layout.row()
            row.operator("bim.enable_editing_boundary", icon="GREASEPENCIL", text="Edit")
            self.draw_relation_data(boundary, "RelatingSpace")
            self.draw_relation_data(boundary, "RelatedBuildingElement")
            self.draw_relation_data(boundary, "ParentBoundary")
            self.draw_relation_data(boundary, "CorrespondingBoundary")
            if hasattr(boundary, "InnerBoundaries"):
                for i, inner_boundary in enumerate(getattr(boundary, "InnerBoundaries", ())):
                    row = self.layout.row(align=True)
                    row.label(text="InnerBoundaries")
                    row.label(text=f"[{i}]")
                    row.label(text=f"{inner_boundary.is_a()}/{inner_boundary.Name}")
        row = self.layout.row()
        row.operator("bim.update_boundary_geometry")

    def draw_relation_data(self, boundary, ifc_attribute: str):
        row = self.layout.row(align=True)
        if hasattr(boundary, ifc_attribute):
            row.label(text=ifc_attribute)
            entity = getattr(boundary, ifc_attribute)
            if entity:
                row.label(text=f"{entity.is_a()}/{entity.Name}")
                op = row.operator("bim.select_global_id", text="", icon="OBJECT_DATA")
                op.global_id = entity.GlobalId
                if ifc_attribute in ("RelatingSpace", "RelatedBuildingElement"):
                    op = row.operator("bim.select_related_element_boundaries", text="", icon="RESTRICT_SELECT_OFF")
                    op.related_element = entity.id()
                    op = row.operator("bim.select_related_element_type_boundaries", text="", icon="ASSET_MANAGER")
                    op.related_element = entity.id()
            else:
                row.label(text="")

    def draw_relation_editor(self, boundary, ifc_attribute: str, blender_property: str):
        if hasattr(boundary, ifc_attribute):
            row = self.layout.row(align=True)
            row.prop(self.bprops, blender_property)


class BIM_PT_SpaceBoundaries(Panel):
    bl_label = "Space Boundaries"
    bl_idname = "BIM_PT_SpaceBoundaries"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"
    bl_order = 1
    bl_parent_id = "BIM_PT_tab_geometric_relationships"

    @classmethod
    def poll(cls, context):
        if not context.active_object:
            return False
        props = context.active_object.BIMObjectProperties
        if not props.ifc_definition_id:
            return False
        if not IfcStore.get_element(props.ifc_definition_id):
            return False
        element = tool.Ifc.get_entity(context.active_object)
        for ifc_class in ("IfcSpace", "IfcExternalSpatialElement"):
            if element.is_a(ifc_class):
                return True
        return False

    def draw(self, context):
        if not SpaceBoundariesData.is_loaded:
            SpaceBoundariesData.load()

        self.props = context.active_object.BIMObjectProperties
        self.ifc_file = tool.Ifc.get()
        row = self.layout.row()
        row.operator("bim.load_space_boundaries")
        row.operator("bim.select_space_boundaries", text="", icon="RESTRICT_SELECT_OFF")
        for boundary in SpaceBoundariesData.data["boundaries"]:
            row = self.layout.row()
            row.label(text=boundary["description"], icon="GHOST_ENABLED")
            op = row.operator("bim.load_boundary", text="", icon="RESTRICT_SELECT_OFF")
            op.boundary_id = boundary["id"]
