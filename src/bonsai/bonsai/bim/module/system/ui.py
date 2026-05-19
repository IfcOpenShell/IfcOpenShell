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

from typing import TYPE_CHECKING

import bpy
from bpy.types import Panel, UIList

import bonsai.bim.helper
import bonsai.tool as tool
from bonsai.bim.helper import draw_attributes, prop_with_search
from bonsai.bim.module.system.data import (
    ActiveObjectZonesData,
    ObjectSystemData,
    PortData,
    SystemData,
    ZonesData,
)

if TYPE_CHECKING:
    from bonsai.bim.module.system.prop import (
        BIMSystemProperties,
        BIMZoneProperties,
        System,
        Zone,
    )


FLOW_DIRECTION_TO_ICON = {
    "SOURCE": "FULLSCREEN_ENTER",
    "SINK": "FULLSCREEN_EXIT",
    "SOURCEANDSINK": "CHECKBOX_DEHLT",
    "NOTDEFINED": "QUESTION",
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
        return tool.Ifc.get()

    def draw(self, context):
        if not SystemData.is_loaded:
            SystemData.load()
        if not ObjectSystemData.is_loaded:
            ObjectSystemData.load()

        assert self.layout
        self.props = tool.System.get_system_props()
        active_system_item = self.props.active_system_ui_item
        row = self.layout.row(align=True)
        row.prop(self.props, "should_draw_decorations")

        row = self.layout.row()
        if active_system := SystemData.data["active_system"]:
            row.label(text=f"Active system:")
            tool.System.draw_system_ui(
                self.layout, active_system["id"], active_system["Name"], active_system["ifc_class"]
            )
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
            row.operator("bim.add_system", text="", icon="ADD")
            row.operator("bim.disable_system_editing_ui", text="", icon="CANCEL")

            row = self.layout.row(align=True)
            prop_with_search(row, self.props, "system_class", text="")
            if active_system_item:
                op = row.operator("bim.add_system", text="", icon="ADD")
                op.parent_system_id = active_system_item.ifc_definition_id

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
                "active_group_index",
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
        row.label(text=f"Ports located in: {context.active_object.name} and connected Port/Objects:")

        row = self.layout.row(align=True)
        cols = [row.column(align=True) for i in range(9)]
        cols[3].scale_x = 1.0
        cols[6].scale_x = 1.0
        cols[8].scale_x = 1.33

        for port_data in PortData.data["located_ports_data"]:
            flow_direction_icon = FLOW_DIRECTION_TO_ICON[port_data["FlowDirection"] or "NOTDEFINED"]

            if port_data["connected_obj_name"]:
                cols[0].operator("bim.disconnect_port", text="", icon="UNLINKED").element_id = port_data["id"]
                op = cols[1].operator("bim.cycle_flow_direction", text="", icon=flow_direction_icon, emboss=True)
                op.port_id = port_data["id"]
            else:
                op = cols[0].operator("bim.add_related_port_connection", text="", icon="PLUGIN")
                op.relating_port_id = port_data["id"]
                op = cols[1].operator("bim.cycle_flow_direction", text="", icon=flow_direction_icon, emboss=True)
                op.port_id = port_data["id"]

            if port_data["port_obj_name"]:
                cols[2].operator("bim.select_entity", text="", icon="RESTRICT_SELECT_OFF").ifc_id = port_data["id"]
                cols[3].label(text=port_data["port_obj_name"])
            else:
                cols[2].label(text="", icon="HIDE_ON")
                cols[3].label(text="Port is hidden")

            if port_data["connected_obj_name"]:
                connected_obj = bpy.data.objects[port_data["connected_obj_name"]]

                port = tool.Ifc.get().by_id(port_data["id"])
                connected_port = tool.System.get_connected_port(port)
                if connected_port:
                    connected_port_obj = tool.Ifc.get_object(connected_port)
                    if connected_port_obj:
                        connected_port_flow_dir = FLOW_DIRECTION_TO_ICON[connected_port.FlowDirection or "NOTDEFINED"]
                        op = cols[4].operator(
                            "bim.cycle_flow_direction", text="", icon=connected_port_flow_dir, emboss=True
                        )
                        op.port_id = connected_port.id()
                        cols[5].operator("bim.select_entity", text="", icon="RESTRICT_SELECT_OFF").ifc_id = (
                            connected_port.id()
                        )
                        cols[6].label(text=connected_port_obj.name)
                    else:
                        blank4 = cols[4].column(align=True)
                        blank4.scale_x = 0.1
                        blank4.label(text="", icon="BLANK1")
                        blank5 = cols[5].column(align=True)
                        blank5.scale_x = 0.1
                        blank5.label(text="", icon="BLANK1")
                        cols[6].label(text="Port is hidden")
                else:
                    blank4 = cols[4].column(align=True)
                    blank4.scale_x = 0.1
                    blank4.label(text="", icon="BLANK1")
                    blank5 = cols[5].column(align=True)
                    blank5.scale_x = 0.1
                    blank5.label(text="", icon="BLANK1")
                    cols[6].label(text="")

                ifc_id = tool.Blender.get_ifc_definition_id(connected_obj)
                cols[7].operator("bim.select_entity", text="", icon="RESTRICT_SELECT_OFF").ifc_id = ifc_id
                cols[8].label(text=port_data["connected_obj_name"])
            else:
                blank4 = cols[4].column(align=True)
                blank4.scale_x = 0.1
                blank4.label(text="", icon="BLANK1")
                blank5 = cols[5].column(align=True)
                blank5.scale_x = 0.1
                blank5.label(text="", icon="BLANK1")

                cols[6].label(text="Port is disconnected")

                blank7 = cols[7].column(align=True)
                blank7.scale_x = 0.1
                blank7.label(text="", icon="BLANK1")
                blank8 = cols[8].column(align=True)
                blank8.scale_x = 0.1
                blank8.label(text="", icon="BLANK1")


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
        layout = self.layout
        row = layout.row(align=True)

        if not PortData.is_loaded:
            PortData.load()

        if not PortData.data["is_port"]:
            return

        relating_object_name = PortData.data["port_relating_object_name"]
        row.label(text=f"IfcDistributionPort located in: {relating_object_name}")
        row.operator("bim.remove_port", icon="X", text="")

        element = tool.Ifc.get_entity(context.active_object)

        row = layout.row(align=True)
        cols = [row.column(align=True) for i in range(10)]
        cols[3].scale_x = 1.0
        cols[6].scale_x = 1.0
        cols[8].scale_x = 1.33

        flow_direction_icon = FLOW_DIRECTION_TO_ICON[element.FlowDirection or "NOTDEFINED"]
        connected_port = tool.System.get_connected_port(element)

        if connected_port:
            cols[0].operator("bim.disconnect_port", text="", icon="UNLINKED")
            op = cols[1].operator("bim.cycle_flow_direction", text="", icon=flow_direction_icon, emboss=True)
            op.port_id = element.id()
        else:
            cols[0].operator("bim.connect_port", icon="PLUGIN", text="")
            op = cols[1].operator("bim.cycle_flow_direction", text="", icon=flow_direction_icon, emboss=True)
            op.port_id = element.id()

        cols[2].operator("bim.select_entity", text="", icon="RESTRICT_SELECT_OFF").ifc_id = element.id()
        cols[3].label(text=context.active_object.name)

        if connected_port:
            connected_port_flow_dir = FLOW_DIRECTION_TO_ICON[connected_port.FlowDirection or "NOTDEFINED"]
            op = cols[4].operator("bim.cycle_flow_direction", text="", icon=connected_port_flow_dir, emboss=True)
            op.port_id = connected_port.id()
            cols[5].operator("bim.select_entity", text="", icon="RESTRICT_SELECT_OFF").ifc_id = connected_port.id()
            connected_port_obj = tool.Ifc.get_object(connected_port)
            cols[6].label(text=connected_port_obj.name if connected_port_obj else "Hidden Port")

            connected_object_name = PortData.data["port_connected_object_name"]
            if connected_object_name:
                connected_obj = bpy.data.objects[connected_object_name]
                ifc_id = tool.Blender.get_ifc_definition_id(connected_obj)
                cols[7].operator("bim.select_entity", text="", icon="RESTRICT_SELECT_OFF").ifc_id = ifc_id
                cols[8].label(text=connected_object_name)
            else:
                cols[7].label(text="", icon="BLANK1")
                cols[8].label(text="")
            cols[9].operator("bim.establish_path_direction", text="", icon="CON_FOLLOWPATH").port_id = (
                connected_port.id()
            )
        else:
            cols[4].label(text="", icon="BLANK1")
            cols[5].label(text="", icon="BLANK1")
            cols[6].label(text="Port is disconnected")
            cols[7].label(text="", icon="BLANK1")
            cols[8].label(text="")
            cols[9].label(text="", icon="BLANK1")


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
            row.operator("bim.select_system_products", text="", icon="RESTRICT_SELECT_OFF").system = ifc_definition_id
            row.operator("bim.assign_system", text="", icon="KEYFRAME_HLT").system = ifc_definition_id
            row.operator("bim.unassign_system", text="", icon="KEYFRAME").system = ifc_definition_id
            row.operator("bim.enable_editing_zone", text="", icon="GREASEPENCIL").zone = ifc_definition_id
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
    ) -> None:
        if item:
            row = layout.row(align=True)
            for i in range(0, item.tree_depth):
                row.label(text="", icon="BLANK1")
            system_id = item.ifc_definition_id
            if item.has_children:
                op = row.operator(
                    "bim.toggle_group",
                    text="",
                    icon="TRIA_DOWN" if item.is_expanded else "TRIA_RIGHT",
                    emboss=False,
                )
                op.group_type = "IfcSystem"
                op.ifc_definition_id = item.ifc_definition_id
                op.option = "COLLAPSE" if item.is_expanded else "EXPAND"
            if data.edited_system_id == system_id:
                row.label(text="", icon="GREASEPENCIL")
            row.prop(item, "name", text="", icon=tool.System.SYSTEM_ICONS[item.ifc_class], emboss=False)


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
            if data.is_editing == item.ifc_definition_id:
                row.label(text="", icon="GREASEPENCIL")
            row.prop(item, "name", text="", emboss=False)
