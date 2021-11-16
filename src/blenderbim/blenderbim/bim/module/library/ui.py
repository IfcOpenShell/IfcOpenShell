# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
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
import blenderbim.tool as tool
from bpy.types import Panel, UIList
from blenderbim.bim.module.library.data import LibrariesData


class BIM_PT_libraries(Panel):
    bl_label = "IFC Libraries"
    bl_idname = "BIM_PT_libraries"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"

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
        blenderbim.bim.helper.draw_attributes(self.props.library_attributes, self.layout)

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
        blenderbim.bim.helper.draw_attributes(self.props.reference_attributes, self.layout)

    def draw_readonly_library_ui(self):
        row = self.layout.row()
        row.operator("bim.add_library", icon="ADD")
        for library in LibrariesData.data["libraries"]:
            row = self.layout.row(align=True)
            row.label(text=library["name"])
            row.operator("bim.enable_editing_library_references", text="", icon="OUTLINER").library = library["id"]
            row.operator("bim.remove_library", text="", icon="X").library = library["id"]


class BIM_UL_library_references(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if item:
            row = layout.row(align=True)
            row.label(text=item.name)
            op = row.operator("bim.enable_editing_library_reference", text="", icon="GREASEPENCIL")
            op.reference = item.ifc_definition_id
            op = row.operator("bim.remove_library_reference", text="", icon="X")
            op.reference = item.ifc_definition_id
