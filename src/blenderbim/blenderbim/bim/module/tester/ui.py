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
import json


class BIM_PT_tester(Panel):
    bl_label = "IFC Tester"
    bl_idname = "BIM_PT_tester"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_tab_quality_control"

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
        row.operator("bim.execute_ifc_tester")

        if self.props.has_report and self.props.should_load_from_memory:
            self.layout.template_list(
                "BIM_UL_tester_specifications",
                "",
                self.props,
                "specifications",
                self.props,
                "active_specification_index",
            )

            self.draw_editable_ui(context)
        
        if self.props.has_report:
            row = self.layout.row()
            row.operator("bim.export_bcf", text="Export BCF", icon="EXPORT")

    def draw_editable_ui(self, context):
        props = context.scene.IfcTesterProperties        
        i = props.active_specification_index
        dic_report = json.loads(props.report)
        
        total_successes = dic_report[i]['total_successes']
        total = dic_report[i]['total']
        percentage = dic_report[i]['percentage']        
        n_requirements = len(dic_report[i]['requirements'])

        row = self.layout.row()
        row.label(text = f"Passed: {total_successes}/{total} ({percentage}%)")
        row = self.layout.row()
        row.label(text = f"Requirements ({n_requirements}):")
        c=0
        box = self.layout.box()        
        for req in dic_report[i]['requirements']:
            row = box.row(align=True)
            row.label(text=f" {c+1}. {req['description']}")
            if req['status']:
                row.label(text="PASS", icon="CHECKMARK")
            else:
                row.label(text="FAIL", icon="CANCEL")
                op = row.operator("bim.select_requirement", text="", icon="LONGDISPLAY")
                op.spec_index = i
                op.req_index = c
            c += 1
        
        if props.old_index == i  and props.n_entities > 0:
            row = self.layout.row()
            row.label(text = f"Failed entities [{props.n_entities}]:")
            self.layout.template_list(
                "BIM_UL_tester_failed_entities",
                "",
                self.props,
                "failed_entities",
                self.props,
                "active_failed_entity_index",
            )
        

        
class BIM_UL_tester_specifications(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if item:
            row = layout.row(align=True)
            row.label(text=item.name, icon="WORDWRAP_ON")
            if item.status:
                row.label(text="PASS")
            else:
                row.label(text="FAIL")

class BIM_UL_tester_failed_entities(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        ifc_file = tool.Ifc.get()
        if item:
            ifc_id = int(item.element[1:item.element.find('=')])
            entity = ifc_file.by_id(ifc_id)
            row = layout.row(align=True)            
            row.label(text=f'{entity.Name} [{entity.is_a()}]')
            row.label(text=item.reason)
            op = row.operator("bim.select_entity", text="", icon="RESTRICT_SELECT_OFF")
            op.ifc_id = entity.id()
            

