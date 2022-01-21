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
from blenderbim.bim.module.system.data import SystemData, ObjectSystemData


class BIM_PT_systems(Panel):
    bl_label = "IFC Systems"
    bl_idname = "BIM_PT_systems"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_services"

    @classmethod
    def poll(cls, context):
        return IfcStore.get_file()

    def draw(self, context):
        if not SystemData.is_loaded:
            SystemData.load()
        self.props = context.scene.BIMSystemProperties

        row = self.layout.row(align=True)
        row.label(text="{} Systems Found".format(SystemData.data["total_systems"]), icon="OUTLINER")
        if self.props.is_editing:
            row.operator("bim.disable_system_editing_ui", text="", icon="CANCEL")

            row = self.layout.row(align=True)
            row.prop(self.props, "system_class", text="")
            row.operator("bim.add_system", text="", icon="ADD")
        else:
            row.operator("bim.load_systems", text="", icon="GREASEPENCIL")

        if self.props.is_editing:
            self.layout.template_list(
                "BIM_UL_systems",
                "",
                self.props,
                "systems",
                self.props,
                "active_system_index",
            )

        if self.props.active_system_id:
            self.draw_editable_ui(context)

    def draw_editable_ui(self, context):
        for attribute in self.props.system_attributes:
            row = self.layout.row(align=True)
            row.prop(attribute, "string_value", text=attribute.name)
            if attribute.is_optional:
                row.prop(attribute, "is_null", icon="RADIOBUT_OFF" if attribute.is_null else "RADIOBUT_ON", text="")


class BIM_PT_object_systems(Panel):
    bl_label = "IFC Systems"
    bl_idname = "BIM_PT_object_systems"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"
    bl_parent_id = "BIM_PT_services_object"

    @classmethod
    def poll(cls, context):
        if not context.active_object:
            return False
        return IfcStore.get_file() and context.active_object.BIMObjectProperties.ifc_definition_id

    def draw(self, context):
        if not ObjectSystemData.is_loaded:
            ObjectSystemData.load()
        self.props = context.scene.BIMSystemProperties
        if self.props.is_editing:
            row = self.layout.row()
            row.alignment = "RIGHT"
            row.operator("bim.disable_system_editing_ui", text="", icon="CANCEL")
            self.layout.template_list(
                "BIM_UL_object_systems",
                "",
                self.props,
                "systems",
                self.props,
                "active_system_index",
            )
        else:
            row = self.layout.row(align=True)
            row.label(text=f"{ObjectSystemData.data['total_systems']} Systems in IFC Project", icon="OUTLINER")
            row.operator("bim.load_systems", text="", icon="GREASEPENCIL")

        system_icons = {
            "IfcSystem": "EXTERNAL_DRIVE",
            "IfcDistributionSystem": "NETWORK_DRIVE",
            "IfcDistributionCircuit": "DRIVER",
            "IfcBuildingSystem": "MOD_BUILD",
        }
        for system in ObjectSystemData.data["systems"]:
            row = self.layout.row(align=True)
            row.label(text=system["name"], icon=system_icons[system["ifc_class"]])
            op = row.operator("bim.select_system_products", text="", icon="RESTRICT_SELECT_OFF")
            op.system = system["id"]
            op = row.operator("bim.unassign_system", text="", icon="X")
            op.system = system["id"]

        if not systems_object:
            self.layout.label(text="No System associated with Active Object")


class BIM_UL_systems(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        system_icons = {
            "IfcSystem": "EXTERNAL_DRIVE",
            "IfcDistributionSystem": "NETWORK_DRIVE",
            "IfcDistributionCircuit": "DRIVER",
            "IfcBuildingSystem": "MOD_BUILD",
        }
        if item:
            row = layout.row(align=True)
            row.label(text=item.name, icon=system_icons[item.ifc_class])
            system_id = item.ifc_definition_id
            if context.scene.BIMSystemProperties.active_system_id == system_id:
                op = row.operator("bim.select_system_products", text="", icon="RESTRICT_SELECT_OFF")
                op.system = system_id
                row.operator("bim.edit_system", text="", icon="CHECKMARK")
                row.operator("bim.disable_editing_system", text="", icon="CANCEL")
            elif context.scene.BIMSystemProperties.active_system_id:
                op = row.operator("bim.select_system_products", text="", icon="RESTRICT_SELECT_OFF")
                op.system = system_id
                op = row.operator("bim.remove_system", text="", icon="X")
                op.system = system_id
            else:
                op = row.operator("bim.select_system_products", text="", icon="RESTRICT_SELECT_OFF")
                op.system = system_id
                op = row.operator("bim.enable_editing_system", text="", icon="GREASEPENCIL")
                op.system = system_id
                op = row.operator("bim.remove_system", text="", icon="X")
                op.system = system_id


class BIM_UL_object_systems(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        system_icons = {
            "IfcSystem": "EXTERNAL_DRIVE",
            "IfcDistributionSystem": "NETWORK_DRIVE",
            "IfcDistributionCircuit": "DRIVER",
            "IfcBuildingSystem": "MOD_BUILD",
        }
        if item:
            row = layout.row(align=True)
            row.label(text=item.name, icon=system_icons[item.ifc_class])
            row.operator("bim.assign_system", text="", icon="ADD").system = item.ifc_definition_id
