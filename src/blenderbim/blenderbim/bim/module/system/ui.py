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

from blenderbim.bim.helper import prop_with_search
import blenderbim.tool as tool
from bpy.types import Panel, UIList
from blenderbim.bim.ifc import IfcStore
from blenderbim.bim.module.system.data import SystemData, ObjectSystemData, PortData


FLOW_DIRECTION_TO_ICON = {
    "SOURCE": "REMOVE",
    "SINK": "ADD",
    "SOURCEANDSINK": "ARROW_LEFTRIGHT",
    "NOTDEFINED": "CHECKBOX_DEHLT",
}


class BIM_PT_systems(Panel):
    bl_label = "Systems"
    bl_idname = "BIM_PT_systems"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_tab_services"

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
            prop_with_search(row, self.props, "system_class", text="")
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
    bl_label = "Systems"
    bl_idname = "BIM_PT_object_systems"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"
    bl_order = 1
    bl_parent_id = "BIM_PT_tab_services_object"

    @classmethod
    def poll(cls, context):
        if not context.active_object:
            return False
        return IfcStore.get_file() and context.active_object.BIMObjectProperties.ifc_definition_id

    def draw(self, context):
        if not ObjectSystemData.is_loaded:
            ObjectSystemData.load()
        self.props = context.scene.BIMSystemProperties

        row = self.layout.row(align=True)
        row.prop(self.props, "should_draw_decorations")

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
            "IfcBuiltSystem": "MOD_BUILD",
            "IfcZone": "CUBE",
        }
        for system in ObjectSystemData.data["systems"]:
            row = self.layout.row(align=True)
            row.label(text=system["name"], icon=system_icons[system["ifc_class"]])
            op = row.operator("bim.select_system_products", text="", icon="RESTRICT_SELECT_OFF")
            op.system = system["id"]
            op = row.operator("bim.unassign_system", text="", icon="X")
            op.system = system["id"]

        if not ObjectSystemData.data["systems"]:
            self.layout.label(text="No System associated with Active Object")


class BIM_PT_ports(Panel):
    bl_label = "Ports"
    bl_idname = "BIM_PT_ports"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"
    bl_order = 1
    bl_parent_id = "BIM_PT_tab_services_object"

    @classmethod
    def poll(cls, context):
        if not context.active_object:
            return False
        element = tool.Ifc.get_entity(context.active_object)
        if not element:
            return False
        if not element.is_a("IfcDistributionElement") and not element.is_a("IfcDistributionElementType"):
            return False
        return True

    def draw(self, context):
        if not PortData.is_loaded:
            PortData.load()
        self.props = context.scene.BIMSystemProperties

        row = self.layout.row(align=True)
        total_ports = PortData.data["total_ports"]
        row.label(text=f"{total_ports} Ports Found", icon="PLUGIN")
        row.operator("bim.mep_connect_elements", text="", icon="PLUGIN")
        row.operator("bim.show_ports", icon="HIDE_OFF", text="")
        row.operator("bim.hide_ports", icon="HIDE_ON", text="")
        row.operator("bim.add_port", icon="ADD", text="")

        if total_ports == 0:
            return

        row = self.layout.row(align=True)
        row.label(text="Change Flow Direction:")

        current_flow_direction = PortData.data["selected_objects_flow_direction"]
        for flow_direction in FLOW_DIRECTION_TO_ICON.keys():
            row.operator(
                "bim.set_flow_direction",
                icon=FLOW_DIRECTION_TO_ICON[flow_direction],
                depress=flow_direction == current_flow_direction,
                text="",
            ).direction = flow_direction
        row.enabled = len(context.selected_objects) == 2

        row = self.layout.row(align=True)
        row.label(text="Ports located on object and connected objects:")
        row = self.layout.row(align=True)
        cols = [row.column(align=True) for i in range(6)]

        for i, port_data in enumerate(PortData.data["located_ports_data"]):
            port, port_obj, connected_obj = port_data
            flow_direction_icon = FLOW_DIRECTION_TO_ICON[port.FlowDirection or "NOTDEFINED"]
            if port_obj:
                cols[0].label(text="", icon=flow_direction_icon)
                cols[1].operator("bim.select_entity", text="", icon="RESTRICT_SELECT_OFF").ifc_id = port.id()
                cols[2].label(text=port_obj.name)
            else:
                cols[0].label(text="", icon=flow_direction_icon)
                cols[1].label(text="", icon="HIDE_ON")
                cols[2].label(text="Port is hidden")

            if connected_obj:
                cols[3].operator("bim.disconnect_port", text="", icon="UNLINKED").element_id = port.id()
                cols[4].operator(
                    "bim.select_entity", text="", icon="RESTRICT_SELECT_OFF"
                ).ifc_id = connected_obj.BIMObjectProperties.ifc_definition_id
                cols[5].label(text=f"{connected_obj.name}")
            else:
                cols[3].label(text="", icon="UNLINKED")
                cols[4].label(text="", icon="BLANK1")
                cols[5].label(text="Port is disconnected")


class BIM_PT_port(Panel):
    bl_label = "Port"
    bl_idname = "BIM_PT_port"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"
    bl_order = 1
    bl_parent_id = "BIM_PT_tab_services_object"

    @classmethod
    def poll(cls, context):
        if not context.active_object:
            return False
        element = tool.Ifc.get_entity(context.active_object)
        if not element or not element.is_a("IfcPort"):
            return False
        return True

    def draw(self, context):
        self.props = context.scene.BIMSystemProperties

        layout = self.layout
        row = layout.row(align=True)
        row.label(text="IfcDistributionPort")
        row.operator("bim.connect_port", icon="PLUGIN", text="")
        row.operator("bim.disconnect_port", icon="UNLINKED", text="")
        row.operator("bim.remove_port", icon="X", text="")

        if not PortData.is_loaded:
            PortData.load()

        if not PortData.data["is_port"]:
            return

        element = tool.Ifc.get_entity(context.active_object)
        current_flow_direction = str(element.FlowDirection)
        row = layout.row(align=True)
        row.label(text="Flow Direction:")
        row.label(text=current_flow_direction)

        # port located on
        row = layout.row(align=True)
        relating_object = PortData.data["port_relating_object"]
        row.label(text="Port located on:")
        row.label(text=relating_object.name)
        row.operator(
            "bim.select_entity", text="", icon="RESTRICT_SELECT_OFF"
        ).ifc_id = relating_object.BIMObjectProperties.ifc_definition_id

        # object connected to the port
        row = layout.row(align=True)
        connected_object = PortData.data["port_connected_object"]
        if connected_object:
            row.label(text="Port connected to:")
            row.label(text=connected_object.name)
            row.operator(
                "bim.select_entity", text="", icon="RESTRICT_SELECT_OFF"
            ).ifc_id = connected_object.BIMObjectProperties.ifc_definition_id
        else:
            row.label(text="Port is not connected to any element")

        row = layout.row(align=True)
        row.label(text="Change Flow Direction:")
        for flow_direction in FLOW_DIRECTION_TO_ICON.keys():
            row.operator(
                "bim.set_flow_direction",
                icon=FLOW_DIRECTION_TO_ICON[flow_direction],
                depress=flow_direction == current_flow_direction,
                text="",
            ).direction = flow_direction


class BIM_UL_systems(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        system_icons = {
            "IfcSystem": "EXTERNAL_DRIVE",
            "IfcDistributionSystem": "NETWORK_DRIVE",
            "IfcDistributionCircuit": "DRIVER",
            "IfcBuildingSystem": "MOD_BUILD",
            "IfcBuiltSystem": "MOD_BUILD",
            "IfcZone": "CUBE",
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
            "IfcBuiltSystem": "MOD_BUILD",
            "IfcZone": "CUBE",
        }
        if item:
            row = layout.row(align=True)
            row.label(text=item.name, icon=system_icons[item.ifc_class])
            row.operator("bim.assign_system", text="", icon="ADD").system = item.ifc_definition_id
