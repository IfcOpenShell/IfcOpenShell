# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
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

import bonsai.bim.helper
import bonsai.tool as tool
from bpy.types import Panel, UIList
from bonsai.bim.module.library.data import LibrariesData, LibraryReferencesData


class BIM_PT_libraries(Panel):
    bl_label = "Libraries"
    bl_idname = "BIM_PT_libraries"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_tab_project_setup"

    @classmethod
    def poll(cls, context):
        return tool.Ifc.get()

    def draw(self, context):
        if not LibrariesData.is_loaded:
            LibrariesData.load()
        self.props = context.scene.BIMLibraryProperties

        if self.props.editing_mode == "LIBRARY":
            self.draw_editable_library_ui()
        elif self.props.editing_mode == "REFERENCE":
            self.draw_editable_reference_ui()
        elif self.props.editing_mode == "REFERENCES":
            self.draw_editable_references_ui()
        else:
            self.draw_readonly_library_ui()

    def draw_editable_library_ui(self):
        row = self.layout.row(align=True)
        row.operator("bim.edit_library", icon="CHECKMARK")
        row.operator("bim.disable_editing_library", text="", icon="CANCEL")
        bonsai.bim.helper.draw_attributes(self.props.library_attributes, self.layout)

    def draw_editable_references_ui(self):
        row = self.layout.row(align=True)
        row.operator("bim.enable_editing_library", icon="GREASEPENCIL")
        row.operator("bim.disable_editing_library_references", text="", icon="CANCEL")

        for attribute in LibrariesData.data["library_attributes"]:
            row = self.layout.row(align=True)
            row.label(text=attribute["name"])
            row.label(text=attribute["value"])

        row = self.layout.row(align=True)
        row.operator("bim.add_library_reference", icon="ADD")

        self.layout.template_list(
            "BIM_UL_library_references", "", self.props, "references", self.props, "active_reference_index"
        )

        for attribute in LibrariesData.data["reference_attributes"]:
            row = self.layout.row(align=True)
            row.label(text=attribute["name"])
            row.label(text=attribute["value"])

    def draw_editable_reference_ui(self):
        row = self.layout.row(align=True)
        row.operator("bim.edit_library_reference", icon="CHECKMARK")
        row.operator("bim.disable_editing_library_reference", text="", icon="CANCEL")
        bonsai.bim.helper.draw_attributes(self.props.reference_attributes, self.layout)

    def draw_readonly_library_ui(self):
        row = self.layout.row()
        row.operator("bim.add_library", icon="ADD")
        for library in LibrariesData.data["libraries"]:
            row = self.layout.row(align=True)
            row.label(text=library["name"], icon="ASSET_MANAGER")
            row.operator("bim.enable_editing_library_references", text="", icon="OUTLINER").library = library["id"]
            row.operator("bim.remove_library", text="", icon="X").library = library["id"]


class BIM_PT_library_references(Panel):
    bl_label = "Library References"
    bl_idname = "BIM_PT_library_references"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"
    bl_order = 1
    bl_parent_id = "BIM_PT_tab_misc"

    @classmethod
    def poll(cls, context):
        return tool.Ifc.get()

    def draw(self, context):
        if not LibraryReferencesData.is_loaded:
            LibraryReferencesData.load()
        self.props = context.scene.BIMLibraryProperties

        if self.props.editing_mode == "REFERENCES":
            self.layout.template_list(
                "BIM_UL_object_library_references", "", self.props, "references", self.props, "active_reference_index"
            )

        if not LibraryReferencesData.data["references"]:
            row = self.layout.row()
            row.label(text="No References")

        for reference in LibraryReferencesData.data["references"]:
            row = self.layout.row(align=True)
            row.label(text=reference["identification"], icon="ASSET_MANAGER")
            row.label(text=reference["name"])
            row.operator("bim.unassign_library_reference", text="", icon="X").reference = reference["id"]


class BIM_UL_library_references(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if item:
            row = layout.row(align=True)
            row.label(text=item.name)
            op = row.operator("bim.enable_editing_library_reference", text="", icon="GREASEPENCIL")
            op.reference = item.ifc_definition_id
            op = row.operator("bim.remove_library_reference", text="", icon="X")
            op.reference = item.ifc_definition_id


class BIM_UL_object_library_references(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if item:
            row = layout.row(align=True)
            row.label(text=item.name)
            op = row.operator("bim.assign_library_reference", text="", icon="ADD")
            op.reference = item.ifc_definition_id
