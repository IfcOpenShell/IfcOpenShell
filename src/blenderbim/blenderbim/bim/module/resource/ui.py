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

import blenderbim.bim.helper
from bpy.types import Panel, UIList
from blenderbim.bim.ifc import IfcStore
from ifcopenshell.api.resource.data import Data


class BIM_PT_resources(Panel):
    bl_label = "IFC Resources"
    bl_idname = "BIM_PT_resources"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"

    @classmethod
    def poll(cls, context):
        file = IfcStore.get_file()
        return file and hasattr(file, "schema") and file.schema != "IFC2X3"

    def draw(self, context):
        self.props = context.scene.BIMResourceProperties
        self.tprops = context.scene.BIMResourceTreeProperties

        if not Data.is_loaded:
            Data.load(IfcStore.get_file())

        row = self.layout.row(align=True)
        row.label(text=f"{len(Data.resources)} Resources Found")
        if self.props.is_editing:
            row.operator("bim.disable_resource_editing_ui", text="", icon="CANCEL")
        else:
            row.operator("bim.load_resources", text="", icon="GREASEPENCIL")

        if not self.props.is_editing:
            return

        self.draw_resource_operators()
        self.layout.template_list(
            "BIM_UL_resources",
            "",
            self.tprops,
            "resources",
            self.props,
            "active_resource_index",
        )

        if self.props.active_resource_id and self.props.editing_resource_type == "ATTRIBUTES":
            self.draw_editable_resource_attributes_ui()
        elif self.props.active_resource_id and self.props.editing_resource_type == "COSTS":
            self.draw_editable_resource_costs_ui()
        elif self.props.active_resource_id and self.props.editing_resource_type == "USAGE":
            self.draw_editable_resource_time_attributes_ui()

    def draw_resource_operators(self):
        row = self.layout.row(align=True)
        op = row.operator("bim.add_resource", text="Add SubContract", icon="TEXT")
        op.ifc_class = "IfcSubContractResource"
        op.resource = 0
        op = row.operator("bim.add_resource", text="Add Crew", icon="COMMUNITY")
        op.ifc_class = "IfcCrewResource"
        op.resource = 0

        total_resources = len(self.tprops.resources)
        if not total_resources or self.props.active_resource_index >= total_resources:
            return

        ifc_definition_id = self.tprops.resources[self.props.active_resource_index].ifc_definition_id
        resource = Data.resources[ifc_definition_id]

        if resource["type"] != "IfcSubContractResource":
            icon_map = {
                "IfcSubContractResource": "TEXT",
                "IfcConstructionEquipmentResource": "TOOL_SETTINGS",
                "IfcLaborResource": "OUTLINER_OB_ARMATURE",
                "IfcConstructionMaterialResource": "MATERIAL",
                "IfcConstructionProductResource": "PACKAGE",
            }
            row = self.layout.row(align=True)
            for ifc_class, icon in icon_map.items():
                label = ifc_class.replace("Ifc", "").replace("Construction", "").replace("Resource", "")
                op = row.operator("bim.add_resource", text=label, icon=icon)
                op.resource = ifc_definition_id
                op.ifc_class = ifc_class

        row = self.layout.row(align=True)
        row.alignment = "RIGHT"

        if self.props.active_resource_id == ifc_definition_id and self.props.editing_resource_type == "ATTRIBUTES":
            row.operator("bim.edit_resource", text="", icon="CHECKMARK")
            row.operator("bim.disable_editing_resource", text="", icon="CANCEL")
        elif self.props.active_resource_id == ifc_definition_id and self.props.editing_resource_type == "USAGE":
            row.operator("bim.edit_resource_time", text="", icon="CHECKMARK")
            row.operator("bim.disable_editing_resource_time", text="", icon="CANCEL")
        elif self.props.active_resource_id == ifc_definition_id and self.props.editing_resource_type == "COSTS":
            row.operator("bim.disable_editing_resource", text="", icon="CANCEL")
        elif self.props.active_resource_id:
            row.operator("bim.add_resource", text="", icon="ADD").resource = ifc_definition_id
            row.operator("bim.remove_resource", text="", icon="X").resource = ifc_definition_id
        else:
            if resource["type"] in ["IfcLaborResource", "IfcConstructionEquipmentResource"]:
                op = row.operator("bim.calculate_resource_work", text="", icon="TEMP")
                op.resource = ifc_definition_id
                row.operator("bim.enable_editing_resource_time", text="", icon="TIME").resource = ifc_definition_id
            op = row.operator("bim.enable_editing_resource_costs", text="", icon="DISC")
            op.resource = ifc_definition_id
            row.operator("bim.enable_editing_resource", text="", icon="GREASEPENCIL").resource = ifc_definition_id
            row.operator("bim.remove_resource", text="", icon="X").resource = ifc_definition_id

    def draw_editable_resource_attributes_ui(self):
        blenderbim.bim.helper.draw_attributes(self.props.resource_attributes, self.layout)

    def draw_editable_resource_time_attributes_ui(self):
        blenderbim.bim.helper.draw_attributes(self.props.resource_time_attributes, self.layout)

    def draw_editable_resource_costs_ui(self):
        row = self.layout.row(align=True)
        row.prop(self.props, "cost_types", text="")
        if self.props.cost_types == "CATEGORY":
            row.prop(self.props, "cost_category", text="")
        op = row.operator("bim.add_cost_value", text="", icon="ADD")
        op.parent = self.props.active_resource_id
        op.cost_type = self.props.cost_types
        if self.props.cost_types == "CATEGORY":
            op.cost_category = self.props.cost_category

        for cost_value_id in Data.resources[self.props.active_resource_id]["BaseCosts"] or []:
            row = self.layout.row(align=True)
            self.draw_readonly_cost_value_ui(row, cost_value_id)

        if self.props.cost_value_editing_type == "ATTRIBUTES":
            box = self.layout.box()
            self.draw_editable_cost_value_ui(box, Data.cost_values[self.props.active_cost_value_id])

    def draw_readonly_cost_value_ui(self, layout, cost_value_id):
        cost_value = Data.cost_values[cost_value_id]

        if self.props.active_cost_value_id == cost_value_id and self.props.cost_value_editing_type == "FORMULA":
            layout.prop(self.props, "cost_value_formula", text="")
        else:
            cost_value_label = "{0:.2f}".format(cost_value["AppliedValue"])
            cost_value_label += " = " + cost_value["Formula"]
            layout.label(text=cost_value_label, icon="DISC")

        self.draw_cost_value_operator_ui(layout, cost_value_id, self.props.active_resource_id)

    def draw_cost_value_operator_ui(self, layout, cost_value_id, parent_id):
        if self.props.active_cost_value_id and self.props.active_cost_value_id == cost_value_id:
            if self.props.cost_value_editing_type == "ATTRIBUTES":
                op = layout.operator("bim.edit_resource_cost_value", text="", icon="CHECKMARK")
                op.cost_value = cost_value_id
            elif self.props.cost_value_editing_type == "FORMULA":
                op = layout.operator("bim.edit_resource_cost_value_formula", text="", icon="CHECKMARK")
                op.cost_value = cost_value_id
            layout.operator("bim.disable_editing_resource_cost_value", text="", icon="CANCEL")
        elif self.props.active_cost_value_id:
            op = layout.operator("bim.remove_cost_value", text="", icon="X")
            op.parent = parent_id
            op.cost_value = cost_value_id
        else:
            op = layout.operator("bim.enable_editing_resource_cost_value_formula", text="", icon="CON_TRANSLIKE")
            op.cost_value = cost_value_id
            op = layout.operator("bim.enable_editing_resource_cost_value", text="", icon="GREASEPENCIL")
            op.cost_value = cost_value_id
            op = layout.operator("bim.remove_cost_value", text="", icon="X")
            op.parent = parent_id
            op.cost_value = cost_value_id

    def draw_editable_cost_value_ui(self, layout, cost_value):
        blenderbim.bim.helper.draw_attributes(self.props.cost_value_attributes, layout)


class BIM_UL_resources(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        resource = Data.resources[item.ifc_definition_id]
        icon_map = {
            "IfcSubContractResource": "TEXT",
            "IfcCrewResource": "COMMUNITY",
            "IfcConstructionEquipmentResource": "TOOL_SETTINGS",
            "IfcLaborResource": "OUTLINER_OB_ARMATURE",
            "IfcConstructionMaterialResource": "MATERIAL",
            "IfcConstructionProductResource": "PACKAGE",
        }
        if item:
            props = context.scene.BIMResourceProperties
            row = layout.row(align=True)
            for i in range(0, item.level_index):
                row.label(text="", icon="BLANK1")
            if item.has_children:
                if item.is_expanded:
                    row.operator(
                        "bim.contract_resource", text="", emboss=False, icon="DISCLOSURE_TRI_DOWN"
                    ).resource = item.ifc_definition_id
                else:
                    row.operator(
                        "bim.expand_resource", text="", emboss=False, icon="DISCLOSURE_TRI_RIGHT"
                    ).resource = item.ifc_definition_id
            else:
                row.label(text="", icon="DOT")
            row.prop(item, "name", emboss=False, text="", icon=icon_map[resource["type"]])

            if context.active_object:
                oprops = context.active_object.BIMObjectProperties
                row = layout.row(align=True)
                if oprops.ifc_definition_id in Data.resources[item.ifc_definition_id]["ResourceOf"]:
                    op = row.operator("bim.unassign_resource", text="", icon="KEYFRAME_HLT", emboss=False)
                    op.resource = item.ifc_definition_id
                else:
                    op = row.operator("bim.assign_resource", text="", icon="KEYFRAME", emboss=False)
                    op.resource = item.ifc_definition_id
