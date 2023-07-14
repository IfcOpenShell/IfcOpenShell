# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2022 Dion Moult <dion@thinkmoult.com>
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

import blenderbim.tool as tool
from bpy.types import Panel, UIList


class BIM_PT_tester(Panel):
    bl_label = "IFC Tester"
    bl_idname = "BIM_PT_tester"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_quality_control"

    def draw(self, context):
        self.layout.use_property_split = True

        self.props = context.scene.IfcTesterProperties

        if tool.Ifc.get():
            row = self.layout.row()
            row.prop(self.props, "should_load_from_memory")

        if not tool.Ifc.get() or not self.props.should_load_from_memory:
            row = self.layout.row(align=True)
            row.prop(self.props, "ifc_file")
            row.operator("bim.select_ifctester_ifc_file", icon="FILE_FOLDER", text="")

        row = self.layout.row(align=True)
        row.prop(self.props, "specs")
        row.operator("bim.select_specs", icon="FILE_FOLDER", text="")

        row = self.layout.row()
        result = row.operator("bim.execute_ifc_tester")

        if self.props.has_report:
            self.layout.template_list(
                "BIM_UL_tester",
                "",
                self.props,
                "specifications",
                self.props,
                "active_specification_index",
            )

            self.draw_editable_ui(context)

    def draw_editable_ui(self, context):
        props = context.scene.IfcTesterProperties
        row = self.layout.row()
        row.label(text="Failed entities: " + str(props.entities))
        

        
class BIM_UL_tester(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        props = context.scene.IfcTesterProperties
        if item:
            icon = "MOD_MESHDEFORM"
            row = layout.row(align=True)
            row.label(text=item.name or "Unnamed", icon=icon)
            if item.status:
                row.label(text="PASS")
            else:
                row.label(text="FAIL")
            op = row.operator("bim.select_specification", text="", icon="VIEWZOOM")
            op.spec = item.failed_entities