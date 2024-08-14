# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2023 Dion Moult <dion@thinkmoult.com>
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

import bonsai.tool as tool
from bpy.types import Panel
from bonsai.bim.ifc import IfcStore
from bonsai.bim.module.fm.data import FMData


class BIM_PT_fm(Panel):
    bl_label = "Facility Management"
    bl_idname = "BIM_PT_fm"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_tab_handover"

    def draw(self, context):
        if not FMData.is_loaded:
            FMData.load()

        layout = self.layout
        layout.use_property_split = True

        scene = context.scene
        props = scene.BIMFMProperties

        if IfcStore.get_file():
            row = layout.row()
            row.prop(props, "should_load_from_memory")

        if not IfcStore.get_file() or not props.should_load_from_memory:
            row = layout.row()
            props.ifc_files.layout_file_select(row, "*.ifc;*.ifczip;*.ifcxml", "IFC File(s)")

        row = layout.row()
        row.prop(props, "engine")
        row = layout.row()
        row.prop(props, "format")

        row = layout.row()
        op = row.operator("bim.execute_ifcfm", text="Convert To Spreadsheet")

        row = layout.row(align=True)
        row.label(text=f"{len(props.spreadsheet_files)} Spreadsheets Selected")
        row.operator("bim.select_fm_spreadsheet_files", icon="FILE_FOLDER", text="")

        row = layout.row()
        op = row.operator("bim.execute_ifcfm_federate", text="Merge Spreadsheets")
