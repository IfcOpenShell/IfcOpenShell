# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2022 Dion Moult <dion@thinkmoult.com>
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
from bpy.types import Panel, UIList
from bonsai.bim.module.tester.data import TesterData


class BIM_PT_tester(Panel):
    bl_label = "IFC Tester"
    bl_idname = "BIM_PT_tester"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_tab_quality_control"

    def draw(self, context):
        if not TesterData.is_loaded:
            TesterData.load()

        self.layout.use_property_split = True
        props = context.scene.IfcTesterProperties

        if tool.Ifc.get():
            row = self.layout.row()
            row.prop(props, "should_load_from_memory")

        row = self.layout.row()
        row.prop(props, "generate_html_report")
        row = self.layout.row()
        row.prop(props, "generate_ods_report")
        row = self.layout.row()
        row.prop(props, "flag")

        if not tool.Ifc.get() or not props.should_load_from_memory:
            row = self.layout.row(align=True)
            props.ifc_files.layout_file_select(row, "*.ifc;*.ifczip;*.ifcxml", "IFC File(s)")

        row = self.layout.row(align=True)
        props.specs.layout_file_select(row, "*.ids;*.xml", "IDS File(s)")

        row = self.layout.row()
        row.operator("bim.execute_ifc_tester")

        if TesterData.data["has_report"]:
            self.layout.template_list(
                "BIM_UL_tester_specifications",
                "",
                props,
                "specifications",
                props,
                "active_specification_index",
            )

            self.draw_editable_ui(context)
            row = self.layout.row()
            row.operator("bim.export_bcf", text="Export BCF", icon="EXPORT")

    def draw_editable_ui(self, context):
        props = context.scene.IfcTesterProperties
        specification = TesterData.data["specification"]

        n_requirements = len(specification["requirements"])

        row = self.layout.row()
        row.label(
            text=f'Passed: {specification["total_checks_pass"]}/{specification["total_checks"]} ({specification["percent_checks_pass"]}%)'
        )
        row = self.layout.row()
        row.label(text=f"Requirements ({n_requirements}):")
        box = self.layout.box()
        for i, requirement in enumerate(specification["requirements"]):
            row = box.row(align=True)
            row.label(text=requirement["description"], icon="CHECKMARK" if requirement["status"] else "CANCEL")
            if not requirement["status"]:
                op = row.operator("bim.select_requirement", text="", icon="LONGDISPLAY")
                op2 = row.operator("bim.select_failed_entities", text="", icon="RESTRICT_SELECT_OFF")
                op.spec_index = props.active_specification_index
                op.req_index = i
                op2.spec_index = props.active_specification_index
                op2.req_index = i

        if props.old_index == props.active_specification_index and props.n_entities > 0:
            row = self.layout.row()
            row.label(text=f"Failed entities [{props.n_entities}]:")
            self.layout.template_list(
                "BIM_UL_tester_failed_entities",
                "",
                props,
                "failed_entities",
                props,
                "active_failed_entity_index",
            )


class BIM_UL_tester_specifications(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if item:
            row = layout.split(factor=0.3, align=True)
            row.label(text=item.name, icon="CHECKMARK" if item.status else "CANCEL")
            row.label(text=item.description)


class BIM_UL_tester_failed_entities(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        props = context.scene.IfcTesterProperties
        if item:
            row = layout.row(align=True)
            row.label(text=item.element)
            row.label(text=item.reason)
            if props.should_load_from_memory:
                op = row.operator("bim.select_entity", text="", icon="RESTRICT_SELECT_OFF")
                op.ifc_id = item.ifc_id
