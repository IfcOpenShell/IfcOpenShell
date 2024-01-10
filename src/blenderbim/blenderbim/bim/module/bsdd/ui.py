# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2023 Dion Moult <dion@thinkmoult.com>
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
from blenderbim.bim.ifc import IfcStore


class BIM_PT_bsdd(Panel):
    bl_label = "buildingSMART Data Dictionary"
    bl_idname = "BIM_PT_bsdd"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_tab_project_setup"

    def draw(self, context):
        props = context.scene.BIMBSDDProperties
        row = self.layout.row(align=True)
        row.prop(props, "load_preview_domains")
        if len(props.domains):
            row.operator("bim.load_bsdd_domains", text="", icon="FILE_REFRESH")

        if props.active_domain:
            row = self.layout.row()
            row.label(text="Active: " + props.active_domain, icon="URL")
        else:
            row = self.layout.row()
            row.label(text="No Active bSDD Domain", icon="ERROR")

        if len(props.domains):
            self.layout.template_list(
                "BIM_UL_bsdd_domains",
                "",
                props,
                "domains",
                props,
                "active_domain_index",
            )
        else:
            row = self.layout.row()
            row.operator("bim.load_bsdd_domains")


class BIM_UL_bsdd_domains(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if item:
            row = layout.row(align=True)
            if item.status != "Active":
                row.label(text=f"{item.name} ({item.organization_name_owner}) - {item.status}", icon="ERROR")
            else:
                row.label(text=f"{item.name} ({item.organization_name_owner})")
            op = row.operator("bim.set_active_bsdd_domain", text="", icon="RESTRICT_SELECT_OFF")
            op.name = item.name
            op.uri = item.uri


class BIM_UL_bsdd_classifications(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if item:
            row = layout.row(align=True)
            row.label(text=item.reference_code)
            row.label(text=item.name)
