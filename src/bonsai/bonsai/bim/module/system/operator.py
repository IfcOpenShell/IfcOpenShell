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
import ifcopenshell.api
import bonsai.tool as tool
import bonsai.core.system as core
import bonsai.bim.helper
from bonsai.bim.ifc import IfcStore
from bonsai.bim.module.system.data import PortData
from mathutils import Matrix


class LoadSystems(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.load_systems"
    bl_label = "Load Systems"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.load_systems(tool.System)


class DisableSystemEditingUI(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.disable_system_editing_ui"
    bl_label = "Disable System Editing UI"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.disable_system_editing_ui(tool.System)


class AddSystem(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_system"
    bl_label = "Add System"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.add_system(tool.Ifc, tool.System, ifc_class=context.scene.BIMSystemProperties.system_class)


class EditSystem(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.edit_system"
    bl_label = "Edit System"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.edit_system(
            tool.Ifc, tool.System, system=tool.Ifc.get().by_id(context.scene.BIMSystemProperties.edited_system_id)
        )


class RemoveSystem(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.remove_system"
    bl_label = "Remove System"
    bl_options = {"REGISTER", "UNDO"}
    system: bpy.props.IntProperty()

    def _execute(self, context):
        core.remove_system(tool.Ifc, tool.System, system=tool.Ifc.get().by_id(self.system))


class EnableEditingSystem(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.enable_editing_system"
    bl_label = "Enable Editing System"
    bl_options = {"REGISTER", "UNDO"}
    system: bpy.props.IntProperty()

    def _execute(self, context):
        core.enable_editing_system(tool.System, system=tool.Ifc.get().by_id(self.system))


class DisableEditingSystem(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.disable_editing_system"
    bl_label = "Disable Editing System"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.disable_editing_system(tool.System)


class AssignSystem(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.assign_system"
    bl_label = "Assign System"
    bl_options = {"REGISTER", "UNDO"}
    system: bpy.props.IntProperty()

    def _execute(self, context):
        for obj in context.selected_objects:
            element = tool.Ifc.get_entity(obj)
            if element:
                core.assign_system(tool.Ifc, system=tool.Ifc.get().by_id(self.system), product=element)


class UnassignSystem(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.unassign_system"
    bl_label = "Unassign System"
    bl_options = {"REGISTER", "UNDO"}
    system: bpy.props.IntProperty()

    def _execute(self, context):
        for obj in context.selected_objects:
            element = tool.Ifc.get_entity(obj)
            if element:
                core.unassign_system(tool.Ifc, system=tool.Ifc.get().by_id(self.system), product=element)


class SelectSystemProducts(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.select_system_products"
    bl_label = "Select System Products"
    bl_options = {"REGISTER", "UNDO"}
    system: bpy.props.IntProperty()

    def _execute(self, context):
        core.select_system_products(tool.System, system=tool.Ifc.get().by_id(self.system))


class ShowPorts(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.show_ports"
    bl_label = "Show Ports"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if not PortData.is_loaded:
            PortData.load()
        if PortData.data["total_ports"] == 0:
            cls.poll_message_set("No ports found")
            return False
        return True

    def _execute(self, context):
        core.show_ports(tool.Ifc, tool.System, tool.Spatial, element=tool.Ifc.get_entity(context.active_object))


class HidePorts(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.hide_ports"
    bl_label = "Hide Ports"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return ShowPorts.poll(context)

    def _execute(self, context):
        core.hide_ports(tool.Ifc, tool.System, element=tool.Ifc.get_entity(context.active_object))


class AddPort(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_port"
    bl_description = "Add port at current cursor position"
    bl_label = "Add Port"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.add_port(tool.Ifc, tool.System, element=tool.Ifc.get_entity(context.active_object))


class RemovePort(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.remove_port"
    bl_label = "Remove Port"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.remove_port(tool.Ifc, tool.System, port=tool.Ifc.get_entity(context.active_object))


class ConnectPort(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.connect_port"
    bl_label = "Connect Ports"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return len(context.selected_objects) == 2

    def _execute(self, context):
        obj1 = context.active_object
        obj2 = context.selected_objects[0] if context.selected_objects[1] == obj1 else context.selected_objects[1]
        core.connect_port(tool.Ifc, port1=tool.Ifc.get_entity(obj1), port2=tool.Ifc.get_entity(obj2))


class DisconnectPort(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.disconnect_port"
    bl_label = "Disconnect Ports"
    bl_options = {"REGISTER", "UNDO"}

    element_id: bpy.props.IntProperty(default=0, options={"SKIP_SAVE"})

    def _execute(self, context):
        if self.element_id != 0:
            element = tool.Ifc.get().by_id(self.element_id)
        else:
            element = tool.Ifc.get_entity(context.active_object)
        core.disconnect_port(tool.Ifc, port=element)


class MEPConnectElements(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.mep_connect_elements"
    bl_label = "Connect MEP Elements"
    bl_description = "Connects two selected elements by their closest located ports and adjusts them"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if not len(context.selected_objects) == 2:
            cls.poll_message_set("Need to select 2 objects.")
            return False
        return True

    def _execute(self, context):
        obj1 = context.active_object
        obj2 = next(o for o in context.selected_objects if o != obj1)

        tool.Model.sync_object_ifc_position(obj1)
        tool.Model.sync_object_ifc_position(obj2)

        el1 = tool.Ifc.get_entity(obj1)
        el2 = tool.Ifc.get_entity(obj2)

        connected_elements = ifcopenshell.util.system.get_connected_to(el1)
        connected_elements += ifcopenshell.util.system.get_connected_to(el2)

        if el2 in connected_elements:
            self.report({"ERROR"}, "MEP elements are already connected to each other.")
            return {"CANCELLED"}

        obj1_ports = [p for p in tool.System.get_ports(el1) if not tool.System.get_connected_port(p)]
        obj2_ports = [p for p in tool.System.get_ports(el2) if not tool.System.get_connected_port(p)]

        if not obj1_ports or not obj2_ports:
            self.report({"ERROR"}, "Couldn't find free ports to connect.")
            return {"CANCELLED"}

        ports_distance = dict()
        for port1 in obj1_ports:
            port1_location = tool.Model.get_element_matrix(port1).translation
            for port2 in obj2_ports:
                port2_location = tool.Model.get_element_matrix(port2).translation
                distance = (port1_location - port2_location).length
                ports_distance[(port1, port2)] = distance

        closest_ports = min(ports_distance, key=lambda x: ports_distance[x])
        core.connect_port(tool.Ifc, *closest_ports)
        bpy.ops.bim.regenerate_distribution_element()
        return {"FINISHED"}


class SetFlowDirection(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.set_flow_direction"
    bl_label = "Set Flow Direction"
    bl_options = {"REGISTER", "UNDO"}
    direction: bpy.props.StringProperty()

    @classmethod
    def description(cls, context, operator):
        if not PortData.is_loaded:
            PortData.load()

        port = PortData.data["is_port"]
        if port:
            return f"Set port flow direction to {operator.direction}"
        else:
            return f"Set flow direction to {operator.direction} for active element relatively to the selected"

    @classmethod
    def poll(cls, context):
        if not PortData.is_loaded:
            PortData.load()

        port = PortData.data["is_port"]
        if not port and not len(context.selected_objects) == 2:
            cls.poll_message_set("Need to select port or 2 connected objects.")
            return False
        return True

    def _execute(self, context):
        element = tool.Ifc.get_entity(context.active_object)

        if element.is_a("IfcDistributionPort"):
            second_port = tool.System.get_connected_port(element)
            if not second_port:
                self.report({"ERROR"}, "To set flow direction port has to be connected to another one.")
                return
            core.set_flow_direction(tool.Ifc, tool.System, port=element, direction=self.direction)
            return {"FINISHED"}

        selected_elements = [
            entity
            for entity in (tool.Ifc.get_entity(o) for o in context.selected_objects)
            if entity and tool.System.is_mep_element(element)
        ]

        if len(selected_elements) != 2:
            self.report({"ERROR"}, "To set flow direction selected two connected MEP elements or just 1 port.")
            return {"CANCELLED"}

        other_element = selected_elements[selected_elements[0] == element]
        active_element_ports = tool.System.get_ports(element)
        other_element_ports = tool.System.get_ports(other_element)

        for port in active_element_ports:
            connected_port = tool.System.get_connected_port(port)
            if connected_port in other_element_ports:
                core.set_flow_direction(tool.Ifc, tool.System, port=port, direction=self.direction)
                tool.Blender.update_viewport()
                return {"FINISHED"}

        self.report({"ERROR"}, "Selected elements are not connected to set the flow direction")
        return {"CANCELLED"}


class LoadZones(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.load_zones"
    bl_label = "Load Zones"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        props = bpy.context.scene.BIMZoneProperties
        props.zones.clear()
        for zone in tool.Ifc.get().by_type("IfcZone"):
            new = props.zones.add()
            new.ifc_definition_id = zone.id()
            new.name = zone.Name or "Unnamed"
        props.is_loaded = True
        props.is_editing = 0


class UnloadZones(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.unload_zones"
    bl_label = "Unload Zones"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        props = bpy.context.scene.BIMZoneProperties
        props.is_loaded = False


class AddZone(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_zone"
    bl_label = "Add Zone"
    bl_options = {"REGISTER", "UNDO"}
    name: bpy.props.StringProperty()

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        row = self.layout
        row.prop(self, "name", text="Name")

    def _execute(self, context):
        element = ifcopenshell.api.run("system.add_system", tool.Ifc.get(), ifc_class="IfcZone")
        if self.name:
            element.Name = self.name
        bpy.ops.bim.load_zones()


class EnableEditingZone(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.enable_editing_zone"
    bl_label = "Enable Editing Zone"
    bl_options = {"REGISTER", "UNDO"}
    zone: bpy.props.IntProperty()

    def _execute(self, context):
        props = bpy.context.scene.BIMZoneProperties
        props.attributes.clear()
        bonsai.bim.helper.import_attributes2(tool.Ifc.get().by_id(self.zone), props.attributes)
        props.is_editing = self.zone


class DisableEditingZone(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.disable_editing_zone"
    bl_label = "Disable Editing Zone"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        props = bpy.context.scene.BIMZoneProperties
        props.is_editing = 0


class EditZone(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.edit_zone"
    bl_label = "Edit Zone"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        props = bpy.context.scene.BIMZoneProperties
        zone = tool.Ifc.get().by_id(props.is_editing)
        attributes = bonsai.bim.helper.export_attributes(props.attributes)
        ifcopenshell.api.run("system.edit_system", tool.Ifc.get(), system=zone, attributes=attributes)
        props.is_editing = 0
        bpy.ops.bim.load_zones()


class RemoveZone(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.remove_zone"
    bl_label = "Remove Zone"
    bl_options = {"REGISTER", "UNDO"}
    zone: bpy.props.IntProperty()

    def _execute(self, context):
        ifcopenshell.api.run("system.remove_system", tool.Ifc.get(), system=tool.Ifc.get().by_id(self.zone))
        bpy.ops.bim.load_zones()


class AssignUnassignFlowControl(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.assign_unassign_flow_control"
    bl_label = "Assign/Unassign Flow Control"
    bl_options = {"REGISTER", "UNDO"}
    flow_element: bpy.props.IntProperty(options={"SKIP_SAVE"})
    flow_control: bpy.props.IntProperty(options={"SKIP_SAVE"})
    assign: bpy.props.BoolProperty(name="Assign/Unassign", default=True, options={"SKIP_SAVE"})

    def _execute(self, context):
        ifc_file = tool.Ifc.get()
        flow_element = None
        flow_controls = []
        from_selected_objects = False

        if self.flow_element != 0:
            flow_element = ifc_file.by_id(self.flow_element)
        if self.flow_control != 0:
            flow_controls = [ifc_file.by_id(self.flow_control)]

        # if not provided as arguments tried to get them from
        # the selected objects
        if not flow_element or flow_controls:
            from_selected_objects = True
            for obj in context.selected_objects:
                element = tool.Ifc.get_entity(obj)
                if not element:
                    continue

                if element.is_a("IfcDistributionControlElement") and self.flow_control == 0:
                    flow_controls.append(element)
                elif element.is_a("IfcDistributionFlowElement") and self.flow_element == 0:
                    if flow_element:
                        self.report(
                            {"ERROR"},
                            "More than one flow element selected. Control can be assigned to only 1 flow element.",
                        )
                        return {"CANCELLED"}
                    flow_element = element

        if not flow_element:
            self.report({"ERROR"}, "No flow element selected.")
            return {"CANCELLED"}

        if not flow_controls:
            self.report({"ERROR"}, "No flow controls selected.")
            return {"CANCELLED"}

        for control in flow_controls:
            if self.assign:
                tool.Ifc.run(
                    "system.assign_flow_control", relating_flow_element=flow_element, related_flow_control=control
                )
            else:
                tool.Ifc.run(
                    "system.unassign_flow_control", relating_flow_element=flow_element, related_flow_control=control
                )

        if from_selected_objects:
            self.report(
                {"INFO"}, f"{len(flow_controls)} flow controls were {'assigned' if self.assign else 'unassigned'}."
            )
        return {"FINISHED"}
