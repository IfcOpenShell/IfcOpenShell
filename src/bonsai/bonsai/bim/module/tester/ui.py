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

from __future__ import annotations

from typing import TYPE_CHECKING

from bonsai.bim.ui import draw_multiline_text

import bpy
from bpy.types import Panel, UIList
import bonsai.tool as tool
from bonsai.bim.module.tester.data import TesterData

if TYPE_CHECKING:
    from bonsai.bim.module.tester.prop import (
        FailedEntities,
        IfcTesterProperties,
        Specification,
    )


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

        assert self.layout
        self.layout.use_property_split = True
        props = tool.Tester.get_tester_props()

        if tool.Ifc.get():
            row = self.layout.row()
            row.prop(props, "should_load_from_memory")

        row = self.layout.row()
        row.prop(props, "generate_html_report")
        row = self.layout.row()
        row.prop(props, "generate_ods_report")
        row = self.layout.row()
        row.prop(props, "flag")
        row = self.layout.row()
        row.prop(props, "hide_skipped_specs")
        if not tool.Ifc.get() or not props.should_load_from_memory:
            row = self.layout.row(align=True)
            props.ifc_files.layout_file_select(row, "*.ifc;*.ifczip;*.ifcxml", "IFC File(s)")

        row = self.layout.row(align=True)
        props.specs.layout_file_select(row, "*.ids;*.xml", "IDS File(s)")

        row = self.layout.row()
        row.operator("bim.execute_ifc_tester")

        self.layout.separator()

        # IfcTester Webapp controls
        if props.webapp_is_running:
            row = self.layout.row()
            row.label(text=f"Webapp: {props.webapp_server_port} | Server: {props.websocket_server_port}")

            row = self.layout.row(align=True)
            row.operator("bim.stop_ifc_tester_webapp")
            row.operator("bim.open_ifc_tester_webapp", icon="URL", text="")
        else:
            row = self.layout.row()
            row.operator("bim.start_ifc_tester_webapp")

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

    def draw_editable_ui(self, context: bpy.types.Context) -> None:
        props = tool.Tester.get_tester_props()
        specification = TesterData.data["specification"]
        is_skipped = specification["total_checks"] == 0 and specification["cardinality"] == "optional"
        if props.hide_skipped_specs and is_skipped:
            return

        n_requirements = len(specification["requirements"])

        assert self.layout
        row = self.layout.row()
        row.label(
            text=f'Passed: {specification["total_checks_pass"]}/{specification["total_checks"]} ({specification["percent_checks_pass"]}%)'
        )
        row = self.layout.row()
        if specification.get("instructions"):
            row.label(text="Instructions:")
            box = self.layout.box()
            column = box.column(align=True)
            draw_multiline_text(column, specification.get("instructions"), context=context)

        row = self.layout.row()
        row.label(text=f"Requirements ({n_requirements}):")
        if props.flag:
            op = row.operator("bim.color_specification", text="", icon="COLOR")
            op.spec_index = props.active_specification_index
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

        if (
            props.old_index == props.active_specification_index
            and props.n_entities > 0
            and len(props.failed_entities) > 0
        ):

            requirement = specification["requirements"][props.active_requirement_index]
            metadata = requirement.get("metadata")
            if metadata and metadata.get("@instructions"):
                row = self.layout.row()
                row.label(text="Instructions:")
                box = self.layout.box()
                column = box.column(align=True)
                draw_multiline_text(column, metadata.get("@instructions"), context=context)

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
    def draw_item(
        self,
        context: bpy.types.Context,
        layout: bpy.types.UILayout,
        data: IfcTesterProperties,
        item: Specification,
        icon,
        active_data,
        active_propname,
    ) -> None:
        if item:
            row = layout.split(factor=0.3, align=True)
            row.label(text=item.name, icon="CHECKMARK" if item.status else "CANCEL")
            row.label(text=item.description)

    def filter_items(self, context: bpy.types.Context, data: IfcTesterProperties, propname: str):
        items = getattr(data, propname)
        filter_flags = [self.bitflag_filter_item] * len(items)

        props = tool.Tester.get_tester_props()
        if props.hide_skipped_specs:
            for idx, item in enumerate(items):
                report = tool.Tester.report[idx]
                if report["total_checks"] != 0:
                    filter_flags[idx] |= self.bitflag_filter_item
                else:
                    filter_flags[idx] &= ~self.bitflag_filter_item

        filter_name = self.filter_name
        if filter_name:
            name_filtered = bpy.types.UI_UL_list.filter_items_by_name(
                filter_name,
                self.bitflag_filter_item,
                items,
                "name",
            )
            if len(name_filtered) == len(filter_flags):
                for idx, flag in enumerate(name_filtered):
                    if flag == 0:
                        filter_flags[idx] &= ~self.bitflag_filter_item

        return filter_flags, []


class BIM_UL_tester_failed_entities(UIList):
    def draw_item(
        self,
        context: bpy.types.Context,
        layout: bpy.types.UILayout,
        data: IfcTesterProperties,
        item: FailedEntities,
        icon,
        active_data,
        active_propname,
    ) -> None:
        if item:
            row = layout.row(align=True)
            row.label(text=item.element)
            row.label(text=item.reason)
            if data.should_load_from_memory:
                op = row.operator("bim.select_entity", text="", icon="RESTRICT_SELECT_OFF")
                op.ifc_id = item.ifc_id
