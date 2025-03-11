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

from __future__ import annotations
import bpy
import bonsai.bim.helper
import bonsai.tool as tool
from bonsai.bim.helper import prop_with_search, draw_attributes
from bpy.types import Panel, UIList
from bonsai.bim.module.system.data import SystemData, ZonesData, ActiveObjectZonesData, ObjectSystemData, PortData
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bonsai.bim.module.system.prop import BIMSystemProperties, System, BIMZoneProperties, Zone


FLOW_DIRECTION_TO_ICON = {
    "SOURCE": "FORWARD",
    "SINK": "BACK",
    "SOURCEANDSINK": "ARROW_LEFTRIGHT",
    "NOTDEFINED": "CHECKBOX_DEHLT",
}

SYSTEM_ICONS = {
    "IfcSystem": "EXTERNAL_DRIVE",
    "IfcDistributionSystem": "NETWORK_DRIVE",
    "IfcDistributionCircuit": "DRIVER",
    "IfcBuildingSystem": "MOD_BUILD",
    "IfcBuiltSystem": "MOD_BUILD",
    "IfcZone": "CUBE",
}
SYSTEM_ICONS["IfcElectricalCircuit"] = SYSTEM_ICONS["IfcDistributionCircuit"]


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
        return tool.Ifc.get()

    def draw(self, context):
        if not SystemData.is_loaded:
            SystemData.load()
        if not ObjectSystemData.is_loaded:
            ObjectSystemData.load()

        self.props = tool.System.get_system_props()
        active_system_item = self.props.active_system_ui_item
        row = self.layout.row(align=True)
        row.prop(self.props, "should_draw_decorations")

        row = self.layout.row()
        if active_system := tool.System.get_active_system():
            row.label(text=f"Active system:")
            tool.System.draw_system_ui(self.layout, active_system.id(), active_system.Name, active_system.is_a())
        else:
            row.label(text="No active system is selected")

        if ObjectSystemData.data["systems"]:
            row = self.layout.row()
            row.label(text="Active object systems:")
            for system in ObjectSystemData.data["systems"]:
                tool.System.draw_system_ui(self.layout, system["id"], system["name"], system["ifc_class"])
        else:
            self.layout.label(text="No System associated with active object")

        row = self.layout.row(align=True)
        row.label(text="{} Systems Found in Project".format(SystemData.data["total_systems"]), icon="OUTLINER")
        if self.props.is_editing:
            row.operator("bim.disable_system_editing_ui", text="", icon="CANCEL")

            row = self.layout.row(align=True)
            prop_with_search(row, self.props, "system_class", text="")
            row.operator("bim.add_system", text="", icon="ADD")
            if active_system_item:
                system_id = active_system_item.ifc_definition_id
                op = row.operator("bim.select_system_products", text="", icon="RESTRICT_SELECT_OFF")
                op.system = system_id
                row.operator("bim.assign_system", text="", icon="KEYFRAME_HLT").system = system_id
                row.operator("bim.unassign_system", text="", icon="KEYFRAME").system = system_id
                if self.props.edited_system_id == system_id:
                    row.operator("bim.edit_system", text="", icon="CHECKMARK")
                    row.operator("bim.disable_editing_system", text="", icon="CANCEL")
                else:
                    op = row.operator("bim.enable_editing_system", text="", icon="GREASEPENCIL")
                    op.system = system_id
                    op = row.operator("bim.remove_system", text="", icon="X")
                    op.system = system_id
        else:
            row.operator("bim.load_systems", text="", icon="IMPORT")

        if self.props.is_editing:
            self.layout.template_list(
                "BIM_UL_systems",
                "",
                self.props,
                "systems",
                self.props,
                "active_system_index",
            )

        if self.props.edited_system_id:
            self.draw_editable_ui(context)

    def draw_editable_ui(self, context: bpy.types.Context) -> None:
        draw_attributes(self.props.system_attributes, self.layout)


class BIM_PT_ports(Panel):
    bl_label = "Ports"
    bl_idname = "BIM_PT_ports"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"
    bl_order = 1
    bl_parent_id = "BIM_PT_tab_services"

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

        self.props = tool.System.get_system_props()

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
            port, port_obj_name, connected_obj_name = port_data
            flow_direction_icon = FLOW_DIRECTION_TO_ICON[port.FlowDirection or "NOTDEFINED"]
            if port_obj_name:
                cols[0].label(text="", icon=flow_direction_icon)
                cols[1].operator("bim.select_entity", text="", icon="RESTRICT_SELECT_OFF").ifc_id = port.id()
                cols[2].label(text=port_obj_name)
            else:
                cols[0].label(text="", icon=flow_direction_icon)
                cols[1].label(text="", icon="HIDE_ON")
                cols[2].label(text="Port is hidden")

            if connected_obj_name:
                connected_obj = bpy.data.objects[connected_obj_name]
                cols[3].operator("bim.disconnect_port", text="", icon="UNLINKED").element_id = port.id()
                ifc_id = tool.Blender.get_ifc_definition_id(connected_obj)
                cols[4].operator("bim.select_entity", text="", icon="RESTRICT_SELECT_OFF").ifc_id = ifc_id
                cols[5].label(text=connected_obj_name)
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
    bl_parent_id = "BIM_PT_tab_services"

    @classmethod
    def poll(cls, context):
        if not context.active_object:
            return False
        element = tool.Ifc.get_entity(context.active_object)
        if not element or not element.is_a("IfcPort"):
            return False
        return True

    def draw(self, context):
        self.props = tool.System.get_system_props()

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
        relating_object_name = PortData.data["port_relating_object_name"]
        relating_object = bpy.data.objects[relating_object_name]
        row.label(text="Port located on:")
        row.label(text=relating_object_name)
        ifc_id = tool.Blender.get_ifc_definition_id(relating_object)
        row.operator("bim.select_entity", text="", icon="RESTRICT_SELECT_OFF").ifc_id = ifc_id

        # object connected to the port
        row = layout.row(align=True)
        connected_object_name = PortData.data["port_connected_object_name"]
        if connected_object_name:
            connected_object = bpy.data.objects[connected_object_name]
            row.label(text="Port connected to:")
            row.label(text=connected_object_name)
            ifc_id = tool.Blender.get_ifc_definition_id(connected_object)
            row.operator("bim.select_entity", text="", icon="RESTRICT_SELECT_OFF").ifc_id = ifc_id
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


class BIM_PT_flow_controls(Panel):
    bl_label = "Flow Controls"
    bl_idname = "BIM_PT_flow_controls"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"
    bl_order = 1
    bl_parent_id = "BIM_PT_tab_services"

    @classmethod
    def poll(cls, context):
        if not context.active_object:
            return False
        element = tool.Ifc.get_entity(context.active_object)
        if not element or not (
            element.is_a("IfcDistributionControlElement") or element.is_a("IfcDistributionFlowElement")
        ):
            return False
        return True

    def draw(self, context):
        if not ObjectSystemData.is_loaded:
            ObjectSystemData.load()

        def display_element(control_id: int, flow_element_id: int, displayed_object_name: str) -> None:
            displayed_object = bpy.data.objects[displayed_object_name]
            row = self.layout.row(align=True)
            op = row.operator("bim.assign_unassign_flow_control", text="", icon="X")
            op.flow_control = control_id
            op.flow_element = flow_element_id
            op.assign = False
            ifc_id = tool.Blender.get_ifc_definition_id(displayed_object)
            row.operator("bim.select_entity", text="", icon="RESTRICT_SELECT_OFF").ifc_id = ifc_id
            row.label(text=f"{displayed_object_name}")

        element = tool.Ifc.get_entity(context.active_object)
        flow_controls_data = ObjectSystemData.data["flow_controls_data"]
        if flow_controls_data["type"] == "IfcDistributionFlowElement":
            controls = flow_controls_data["controls"]
            row = self.layout.row(align=True)
            if controls:
                row.label(text="Controls assigned to the element:")
            else:
                row.label(text="No controls assigned to the flow element")
            row.operator("bim.assign_unassign_flow_control", text="", icon="ADD").assign = True
            if controls:
                for control_data in controls:
                    control, control_obj_name = control_data
                    display_element(control.id(), element.id(), control_obj_name)
        else:
            flow_element, flow_element_obj_name = flow_controls_data["flow_element"]
            row = self.layout.row(align=True)
            if flow_element:
                row.label(text="Flow element controlled by the flow control:")
                display_element(element.id(), flow_element.id(), flow_element_obj_name)
            else:
                row.label(text="No flow element controlled by the flow control")
                row.operator("bim.assign_unassign_flow_control", text="", icon="ADD").assign = True


class BIM_PT_zones(Panel):
    bl_label = "Zones"
    bl_idname = "BIM_PT_zones"
    bl_options = {"HIDE_HEADER"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_tab_zones"

    @classmethod
    def poll(cls, context):
        return tool.Ifc.get()

    def draw(self, context):
        if not ZonesData.is_loaded:
            ZonesData.load()
        self.props = tool.System.get_zone_props()

        row = self.layout.row(align=True)
        row.label(text="{} Zones Found".format(ZonesData.data["total_zones"]), icon="SEQ_STRIP_META")
        if not self.props.is_loaded:
            row.operator("bim.load_zones", text="", icon="IMPORT")
            return

        row.operator("bim.unload_zones", text="", icon="CANCEL")

        row = self.layout.row(align=True)
        row.alignment = "RIGHT"
        row.operator("bim.add_zone", text="", icon="ADD")
        if self.props.zones and self.props.active_zone_index < len(self.props.zones):
            ifc_definition_id = self.props.zones[self.props.active_zone_index].ifc_definition_id
            row.operator("bim.enable_editing_zone", text="", icon="GREASEPENCIL").zone = ifc_definition_id
            row.operator("bim.select_system_products", text="", icon="RESTRICT_SELECT_OFF").system = ifc_definition_id
            row.operator("bim.assign_system", text="", icon="KEYFRAME_HLT").system = ifc_definition_id
            row.operator("bim.unassign_system", text="", icon="KEYFRAME").system = ifc_definition_id
            row.operator("bim.remove_zone", text="", icon="X").zone = ifc_definition_id

        self.layout.template_list("BIM_UL_zones", "", self.props, "zones", self.props, "active_zone_index")

        if self.props.is_editing:
            bonsai.bim.helper.draw_attributes(self.props.attributes, self.layout)
            row = self.layout.row(align=True)
            row.operator("bim.edit_zone", icon="CHECKMARK")
            row.operator("bim.disable_editing_zone", icon="CANCEL", text="")


class BIM_PT_active_object_zones(Panel):
    bl_label = "Active Object Zones"
    bl_idname = "BIM_PT_active_object_zones"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_tab_zones"

    @classmethod
    def poll(cls, context):
        return tool.Ifc.get() and context.active_object and tool.Ifc.get_entity(context.active_object)

    def draw(self, context):
        if not ActiveObjectZonesData.is_loaded:
            ActiveObjectZonesData.load()
        self.props = tool.System.get_zone_props()

        for zone in ActiveObjectZonesData.data["zones"]:
            tool.System.draw_system_ui(self.layout, zone["id"], zone["Name"], "IfcZone")

        if not ActiveObjectZonesData.data["zones"]:
            row = self.layout.row()
            row.label(text="Active Object Has No Zones")


class BIM_UL_systems(UIList):
    def draw_item(
        self,
        context,
        layout: bpy.types.UILayout,
        data: BIMSystemProperties,
        item: System,
        icon,
        active_data,
        active_propname,
    ):
        if item:
            row = layout.row(align=True)
            system_id = item.ifc_definition_id
            if data.edited_system_id == system_id:
                row.label(text="", icon="GREASEPENCIL")
            row.prop(item, "name", text="", icon=SYSTEM_ICONS[item.ifc_class], emboss=False)


class BIM_UL_zones(UIList):
    def draw_item(
        self,
        context,
        layout: bpy.types.UILayout,
        data: BIMZoneProperties,
        item: Zone,
        icon,
        active_data,
        active_propname,
    ):
        if item:
            row = layout.row(align=True)
            row.prop(item, "name", text="", emboss=False)
