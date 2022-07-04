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

import bpy
from bpy.types import Panel
from blenderbim.bim.ifc import IfcStore
from blenderbim.bim.ui import prop_with_search
from blenderbim.bim.module.pset_template.prop import (
    getPsetTemplates,
)
from ifcopenshell.api.pset_template.data import Data


class BIM_PT_pset_template(Panel):
    bl_label = "IFC Property Set Templates"
    bl_idname = "BIM_PT_pset_template"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_project_setup"

    def draw(self, context):
        layout = self.layout
        props = context.scene.BIMPsetTemplateProperties
        
        row = layout.row(align=True)
        prop_with_search(row, props, "pset_template_files", text="")
        row.operator("bim.save_pset_template_file", text="", icon="EXPORT")
        row.operator("bim.add_pset_file",icon="ADD",text="")
        row.operator("bim.refresh_psettemplates", icon="FILE_REFRESH", text="")
        
        row = layout.row(align=True)

        if bool(getPsetTemplates(props, context)):
            prop_with_search(row, props, "pset_templates", text="", icon="COPY_ID")
        else:
            row.label(text="No Pset Templates", icon="COPY_ID")

        if props.active_pset_template_id:
            row.operator("bim.edit_pset_template", text="", icon="CHECKMARK")
            row.operator("bim.disable_editing_pset_template", text="", icon="CANCEL")
        else:
            row.operator("bim.add_pset_template", text="", icon="ADD")
            row.operator("bim.enable_editing_pset_template", text="", icon="GREASEPENCIL")
            row.operator("bim.remove_pset_template", text="", icon="X")

        if not Data.is_loaded and props.pset_template_files:
            Data.load(IfcStore.pset_template_file)

        if not Data.pset_templates:
            return

        if props.active_pset_template_id:
            pset_template = Data.pset_templates[int(props.active_pset_template_id)]
            row = layout.row()
            row.prop(props.active_pset_template, "name")
            row = layout.row()
            row.prop(props.active_pset_template, "description")
            prop_with_search(layout, props.active_pset_template, "template_type")
            row = layout.row()
            row.prop(props.active_pset_template, "applicable_entity")
        else:    
            pset_template = Data.pset_templates[int(props.pset_templates)]
            for name, value in pset_template.items():
                if name == "id" or name == "type" or name == "HasPropertyTemplates":
                    continue
                row = layout.row(align=True)
                row.label(text=name)
                row.label(text=str(value))

        row = layout.row(align=True)
        row.label(text="Property Templates", icon="COPY_ID")
        row.operator("bim.add_prop_template", icon="ADD", text="")
        
        row = layout.row()
        row.label(text="Name | Description | PrimaryMeasureType | TemplateType")

        for prop_template_id in pset_template["HasPropertyTemplates"]:
            prop_template = Data.prop_templates[prop_template_id]
            row = layout.row(align=True)

            if props.active_prop_template_id and props.active_prop_template_id == prop_template_id:
                row.prop(props.active_prop_template, "name", text="")
                row.prop(props.active_prop_template, "description", text="")
                prop_with_search(row, props.active_prop_template, "primary_measure_type", text="")
                row.prop(props.active_prop_template, "template_type", text="")
                
                if props.active_prop_template.template_type == "P_ENUMERATEDVALUE":
                    row = layout.row(align=True)
                    split = row.split(factor=0.2)
                    c=split.column()
                    c.label(text="Enumerations:",)
                    
                    c=split.column()
                    box = c.box()
                    grid = box.column_flow(columns=4)
                    value_name = props.active_prop_template.get_value_name()
                    r = grid.row()
                    r.operator("bim.add_prop_enum", text="Add Enum")
                    for k,v in enumerate(props.active_prop_template.enum_values):
                        r = grid.row(align=True)                 
                        r.prop(v, value_name, text="")
                        op = r.operator("bim.delete_prop_enum", icon="X", text="")
                        op.index = k
                    
                    
            else:
                row.label(text=prop_template["Name"])
                row.label(text=prop_template["Description"])
                row.label(text=prop_template["PrimaryMeasureType"])
                row.label(text=prop_template["TemplateType"])

            if props.active_prop_template_id and props.active_prop_template_id == prop_template_id:
                op = row.operator("bim.edit_prop_template", icon="CHECKMARK", text="")
                row.operator("bim.disable_editing_prop_template", icon="CANCEL", text="")
            elif props.active_prop_template_id and props.active_prop_template_id != prop_template_id:
                row.operator("bim.remove_prop_template", icon="X", text="").prop_template = prop_template_id
            else:
                op = row.operator("bim.enable_editing_prop_template", icon="GREASEPENCIL", text="")
                op.prop_template = prop_template_id
                row.operator("bim.remove_prop_template", icon="X", text="").prop_template = prop_template_id
