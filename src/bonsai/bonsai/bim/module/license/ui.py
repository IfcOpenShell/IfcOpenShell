# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2026 Dion Moult <dion@thinkmoult.com>
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

# AI-assisted development tool was used in writing this file.

from __future__ import annotations

import bpy
from bpy.types import Panel

import bonsai.tool as tool
from bonsai.bim.module.license.data import ObjectLicenseData, ProjectLicenseData


def _draw_license_fields(layout: bpy.types.UILayout, props) -> None:
    layout.prop(props, "spdx_license_identifier")
    layout.prop(props, "copyright_notice")
    layout.prop(props, "attribution_text")
    layout.prop(props, "source_url")


def _draw_license_display(layout: bpy.types.UILayout, pset: dict) -> None:
    spdx = pset.get("SpdxLicenseIdentifier") or ""
    notice = pset.get("CopyrightNotice") or ""
    attribution = pset.get("AttributionText") or ""
    source = pset.get("SourceUrl") or ""
    if spdx:
        row = layout.row()
        row.label(text=spdx, icon="COPYDOWN")
    if notice:
        row = layout.row()
        row.label(text=notice, icon="USER")
    if attribution:
        row = layout.row()
        row.label(text=attribution, icon="INFO")
    if source:
        row = layout.row(align=True)
        row.label(text="Source", icon="URL")
        row.operator("bim.open_uri", text=source, icon="LINKED").uri = source


class BIM_PT_project_license(Panel):
    bl_label = "License"
    bl_idname = "BIM_PT_project_license"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_tab_project_setup"

    @classmethod
    def poll(cls, context):
        return tool.Ifc.get()

    def draw(self, context):
        if not ProjectLicenseData.is_loaded:
            ProjectLicenseData.load()

        layout = self.layout
        props = context.scene.BIMLicenseProperties  # type: ignore[attr-defined]
        pset = ProjectLicenseData.data["license"]

        if props.is_editing:
            _draw_license_fields(layout, props)
            row = layout.row(align=True)
            row.operator("bim.edit_project_license", text="Save", icon="CHECKMARK")
            row.operator("bim.disable_editing_project_license", text="", icon="CANCEL")
        elif pset:
            _draw_license_display(layout, pset)
            row = layout.row(align=True)
            row.operator("bim.enable_editing_project_license", text="Edit", icon="GREASEPENCIL")
            row.operator("bim.remove_project_license", text="", icon="X")
        else:
            row = layout.row()
            row.label(text="No license set", icon="QUESTION")
            row.operator("bim.enable_editing_project_license", text="Set License", icon="ADD")


class BIM_PT_object_license(Panel):
    bl_label = "License"
    bl_idname = "BIM_PT_object_license"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"
    bl_parent_id = "BIM_PT_tab_object_metadata"

    @classmethod
    def poll(cls, context):
        return (obj := tool.Blender.get_active_object()) and tool.Ifc.get_entity(obj)

    def draw(self, context):
        if not ObjectLicenseData.is_loaded:
            ObjectLicenseData.load()

        layout = self.layout
        props = context.scene.BIMLicenseProperties  # type: ignore[attr-defined]
        pset = ObjectLicenseData.data["license"]
        inherited_from = ObjectLicenseData.data["inherited_from"]

        obj = context.active_object
        element = tool.Ifc.get_entity(obj) if obj else None
        has_own_pset = bool(element and tool.License.get_pset(element))

        if props.is_editing:
            _draw_license_fields(layout, props)
            row = layout.row(align=True)
            row.operator("bim.edit_object_license", text="Save", icon="CHECKMARK")
            row.operator("bim.disable_editing_object_license", text="", icon="CANCEL")
        elif pset:
            if inherited_from:
                row = layout.row()
                row.label(text=f"Inherited from: {inherited_from}", icon="LINKED")
            _draw_license_display(layout, pset)
            row = layout.row(align=True)
            row.operator("bim.enable_editing_object_license", text="Override", icon="GREASEPENCIL")
            if has_own_pset:
                row.operator("bim.remove_object_license", text="", icon="X")
        else:
            row = layout.row()
            row.label(text="No license set", icon="QUESTION")
            row.operator("bim.enable_editing_object_license", text="Set License", icon="ADD")
