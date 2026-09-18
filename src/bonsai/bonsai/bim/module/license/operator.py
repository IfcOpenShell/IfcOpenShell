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

from typing import TYPE_CHECKING

import bpy
from bpy.types import Operator

import bonsai.bim.handler
import bonsai.tool as tool
from bonsai.bim.module.license.data import ObjectLicenseData, ProjectLicenseData

if TYPE_CHECKING:
    from bonsai.bim.module.license.prop import BIMLicenseProperties


def _get_props() -> BIMLicenseProperties:
    assert (scene := bpy.context.scene)
    return scene.BIMLicenseProperties  # type: ignore[attr-defined]


def _populate_props_from_pset(props: BIMLicenseProperties, pset: dict) -> None:
    props.spdx_license_identifier = pset.get("SpdxLicenseIdentifier", "") or ""
    props.copyright_notice = pset.get("CopyrightNotice", "") or ""
    props.attribution_text = pset.get("AttributionText", "") or ""
    props.source_url = pset.get("SourceUrl", "") or ""


# ---------------------------------------------------------------------------
# Project-level license
# ---------------------------------------------------------------------------


class EnableEditingProjectLicense(Operator):
    bl_idname = "bim.enable_editing_project_license"
    bl_label = "Edit Project License"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        props = _get_props()
        existing = ProjectLicenseData.data.get("license")
        if existing:
            _populate_props_from_pset(props, existing)
        props.is_editing = True
        return {"FINISHED"}


class DisableEditingProjectLicense(Operator):
    bl_idname = "bim.disable_editing_project_license"
    bl_label = "Cancel"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        _get_props().is_editing = False
        return {"FINISHED"}


class EditProjectLicense(Operator):
    bl_idname = "bim.edit_project_license"
    bl_label = "Save Project License"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        file = tool.Ifc.get()
        projects = file.by_type("IfcProject")
        if not projects:
            return {"CANCELLED"}
        props = _get_props()
        tool.License.set_license(
            file,
            projects[0],
            spdx_id=props.spdx_license_identifier,
            copyright_notice=props.copyright_notice,
            attribution_text=props.attribution_text,
            source_url=props.source_url,
        )
        props.is_editing = False
        ProjectLicenseData.is_loaded = False
        bonsai.bim.handler.refresh_ui_data()
        return {"FINISHED"}


class RemoveProjectLicense(Operator):
    bl_idname = "bim.remove_project_license"
    bl_label = "Remove Project License"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        file = tool.Ifc.get()
        projects = file.by_type("IfcProject")
        if not projects:
            return {"CANCELLED"}
        tool.License.remove_license(file, projects[0])
        ProjectLicenseData.is_loaded = False
        bonsai.bim.handler.refresh_ui_data()
        return {"FINISHED"}


# ---------------------------------------------------------------------------
# Object-level license
# ---------------------------------------------------------------------------


class EnableEditingObjectLicense(Operator):
    bl_idname = "bim.enable_editing_object_license"
    bl_label = "Edit Object License"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        props = _get_props()
        obj = context.active_object
        if not obj:
            return {"CANCELLED"}
        element = tool.Ifc.get_entity(obj)
        if not element:
            return {"CANCELLED"}
        existing = tool.License.get_pset(element)
        if existing:
            _populate_props_from_pset(props, existing)
        else:
            # Pre-populate from effective (inherited) license as a convenience
            eff, _ = tool.License.get_effective_pset(element)
            if eff:
                _populate_props_from_pset(props, eff)
        props.is_editing = True
        return {"FINISHED"}


class DisableEditingObjectLicense(Operator):
    bl_idname = "bim.disable_editing_object_license"
    bl_label = "Cancel"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        _get_props().is_editing = False
        return {"FINISHED"}


class EditObjectLicense(Operator):
    bl_idname = "bim.edit_object_license"
    bl_label = "Save Object License"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        obj = context.active_object
        if not obj:
            return {"CANCELLED"}
        element = tool.Ifc.get_entity(obj)
        if not element:
            return {"CANCELLED"}
        props = _get_props()
        tool.License.set_license(
            tool.Ifc.get(),
            element,
            spdx_id=props.spdx_license_identifier,
            copyright_notice=props.copyright_notice,
            attribution_text=props.attribution_text,
            source_url=props.source_url,
        )
        props.is_editing = False
        ObjectLicenseData.is_loaded = False
        bonsai.bim.handler.refresh_ui_data()
        return {"FINISHED"}


class RemoveObjectLicense(Operator):
    bl_idname = "bim.remove_object_license"
    bl_label = "Remove Object License"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        obj = context.active_object
        if not obj:
            return {"CANCELLED"}
        element = tool.Ifc.get_entity(obj)
        if not element:
            return {"CANCELLED"}
        tool.License.remove_license(tool.Ifc.get(), element)
        ObjectLicenseData.is_loaded = False
        bonsai.bim.handler.refresh_ui_data()
        return {"FINISHED"}
