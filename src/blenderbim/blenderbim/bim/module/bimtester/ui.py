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

from bpy.types import Panel
from blenderbim.bim.ifc import IfcStore


class BIM_PT_qa(Panel):
    bl_label = "BIMTester"
    bl_idname = "BIM_PT_qa"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_tab_quality_control"

    def draw(self, context):
        self.layout.use_property_split = True

        props = context.scene.BimTesterProperties

        if IfcStore.get_file():
            row = self.layout.row()
            row.prop(props, "should_load_from_memory")

        if not IfcStore.get_file() or not props.should_load_from_memory:
            row = self.layout.row(align=True)
            row.prop(props, "ifc_file")
            row.operator("bim.select_bimtester_ifc_file", icon="FILE_FOLDER", text="")

        row = self.layout.row(align=True)
        row.prop(props, "feature")
        row.operator("bim.select_feature", icon="FILE_FOLDER", text="")

        row = self.layout.row(align=True)
        row.prop(props, "steps")
        row.operator("bim.select_steps", icon="FILE_FOLDER", text="")

        has_ifc_file = (IfcStore.get_file() and props.should_load_from_memory) or (
            props.ifc_file and not props.should_load_from_memory
        )

        row = self.layout.row(align=True)
        row.operator("bim.execute_bim_tester")
        row.operator("bim.bim_tester_purge")

        if props.feature and has_ifc_file:
            self.layout.label(text="Scenario Authoring:")

            row = self.layout.row(align=True)
            row.prop(props, "scenario")

            row = self.layout.row()
            row.prop(props, "qa_reject_element_reason")
            row = self.layout.row()
            row.operator("bim.reject_element")

            row = self.layout.row()
            row.prop(props, "audit_ifc_class")

            row = self.layout.row(align=True)
            row.operator("bim.approve_class")
            row.operator("bim.reject_class")

            row = self.layout.row()
            row.operator("bim.select_audited")
