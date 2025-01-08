# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
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

import bpy
from bpy.types import Panel
from bonsai.bim.helper import prop_with_search
from bonsai.bim.module.pset_template.data import PsetTemplatesData


class BIM_PT_pset_template(Panel):
    bl_label = "Property Set Templates"
    bl_idname = "BIM_PT_pset_template"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_tab_project_setup"

    def draw(self, context):
        if not PsetTemplatesData.is_loaded:
            PsetTemplatesData.load()

        self.props = context.scene.BIMPsetTemplateProperties

        row = self.layout.row(align=True)
        if PsetTemplatesData.data["pset_template_files"]:
            prop_with_search(row, self.props, "pset_template_files", text="", icon="FILE")
        else:
            row.label(text="No Pset Template Files", icon="FILE")
        row.operator("bim.add_pset_template_file", icon="ADD", text="")
        if PsetTemplatesData.data["pset_template_files"]:
            row.operator("bim.remove_pset_template_file", icon="X", text="")

        row = self.layout.row(align=True)

        if PsetTemplatesData.data["pset_templates"]:
            prop_with_search(row, self.props, "pset_templates", text="", icon="COPY_ID")
        else:
            row.label(text="No Pset Templates", icon="COPY_ID")

        if self.props.active_pset_template_id:
            row.operator("bim.edit_pset_template", text="", icon="CHECKMARK")
            row.operator("bim.disable_editing_pset_template", text="", icon="CANCEL")
        else:
            row.operator("bim.add_pset_template", text="", icon="ADD")
            row.operator("bim.enable_editing_pset_template", text="", icon="GREASEPENCIL")
            if PsetTemplatesData.data["pset_templates"]:
                row.operator("bim.remove_pset_template", text="", icon="X")

        if PsetTemplatesData.data["pset_template"]:
            self.draw_pset_template()

    def draw_pset_template(self):
        if self.props.active_pset_template_id:
            row = self.layout.row()
            row.prop(self.props.active_pset_template, "name")
            row = self.layout.row()
            row.prop(self.props.active_pset_template, "description")
            prop_with_search(self.layout, self.props.active_pset_template, "template_type")
            row = self.layout.row()
            row.prop(self.props.active_pset_template, "applicable_entity")
        else:
            for name, value in PsetTemplatesData.data["pset_template"].items():
                row = self.layout.row(align=True)
                row.label(text=name)
                row.label(text=str(value))

        row = self.layout.row(align=True)
        row.label(text="Property Templates", icon="COPY_ID")
        row.operator("bim.add_prop_template", icon="ADD", text="")

        for prop_template in PsetTemplatesData.data["prop_templates"]:
            row = self.layout.row(align=True)

            if self.props.active_prop_template_id and self.props.active_prop_template_id == prop_template["id"]:
                active_prop_template = self.props.active_prop_template
                row.prop(self.props.active_prop_template, "name", text="")
                row.prop(self.props.active_prop_template, "description", text="")
                # Quantities don't use primary measure type.
                if active_prop_template.template_type.startswith("P_"):
                    prop_with_search(row, self.props.active_prop_template, "primary_measure_type", text="")
                row.prop(self.props.active_prop_template, "template_type", text="")

                if self.props.active_prop_template.template_type == "P_ENUMERATEDVALUE":
                    row = self.layout.row(align=True)
                    split = row.split(factor=0.2)
                    c = split.column()
                    c.label(
                        text="Enumerations:",
                    )

                    c = split.column()
                    box = c.box()
                    grid = box.column_flow(columns=4)
                    value_name = self.props.active_prop_template.get_value_name()
                    r = grid.row()
                    r.operator("bim.add_prop_enum", text="Add Enum")
                    for k, v in enumerate(self.props.active_prop_template.enum_values):
                        r = grid.row(align=True)
                        r.prop(v, value_name, text="")
                        op = r.operator("bim.delete_prop_enum", icon="X", text="")
                        op.index = k

            else:
                row.label(text=prop_template["Name"])
                row.label(text=prop_template["Description"])
                row.label(text=prop_template["PrimaryMeasureType"])
                row.label(text=prop_template["TemplateType"])

            if self.props.active_prop_template_id and self.props.active_prop_template_id == prop_template["id"]:
                op = row.operator("bim.edit_prop_template", icon="CHECKMARK", text="")
                row.operator("bim.disable_editing_prop_template", icon="CANCEL", text="")
            elif self.props.active_prop_template_id and self.props.active_prop_template_id != prop_template["id"]:
                row.operator("bim.remove_prop_template", icon="X", text="").prop_template = prop_template["id"]
            else:
                op = row.operator("bim.enable_editing_prop_template", icon="GREASEPENCIL", text="")
                op.prop_template = prop_template["id"]
                row.operator("bim.remove_prop_template", icon="X", text="").prop_template = prop_template["id"]
