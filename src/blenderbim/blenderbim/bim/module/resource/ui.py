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

from bpy.types import Panel, UIList
from blenderbim.bim.ifc import IfcStore
from ifcopenshell.api.resource.data import Data
import blenderbim.bim.helper


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
        elif self.props.active_resource_id:
            row.operator("bim.add_resource", text="", icon="ADD").resource = ifc_definition_id
            row.operator("bim.remove_resource", text="", icon="X").resource = ifc_definition_id
        else:
            if resource["type"] in ["IfcLaborResource", "IfcConstructionEquipmentResource"]:
                op = row.operator("bim.calculate_resource_work", text="", icon="TEMP")
                op.resource = ifc_definition_id
                row.operator("bim.enable_editing_resource_time", text="", icon="TIME").resource = ifc_definition_id
            row.operator("bim.enable_editing_resource", text="", icon="GREASEPENCIL").resource = ifc_definition_id
            row.operator("bim.remove_resource", text="", icon="X").resource = ifc_definition_id

    def draw_editable_resource_attributes_ui(self):
        blenderbim.bim.helper.draw_attributes(self.props.resource_attributes, self.layout)

    def draw_editable_resource_time_attributes_ui(self):
        blenderbim.bim.helper.draw_attributes(self.props.resource_time_attributes, self.layout)


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
