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

from math import pi
from typing import TYPE_CHECKING

import bpy
import ifcopenshell.api.attribute
import ifcopenshell.api.system
import ifcopenshell.util.element
import ifcopenshell.util.system
from mathutils import Quaternion, Vector

import bonsai.bim.helper
import bonsai.core.system as core
import bonsai.tool as tool
from bonsai.bim.module.system.data import PortData, SystemData
from bonsai.tool.system import direction_from_port_pair


class LoadSystems(bpy.types.Operator):
    bl_idname = "bim.load_systems"
    bl_label = "Load Systems"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        core.load_systems(tool.System)
        return {"FINISHED"}


class DisableSystemEditingUI(bpy.types.Operator):
    bl_idname = "bim.disable_system_editing_ui"
    bl_label = "Disable System Editing UI"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        core.disable_system_editing_ui(tool.System)
        return {"FINISHED"}


class AddSystem(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_system"
    bl_label = "Add System"
    bl_options = {"REGISTER", "UNDO"}

    parent_system_id: bpy.props.IntProperty()

    if TYPE_CHECKING:
        parent_system_id: int

    @classmethod
    def description(cls, context, properties) -> str:
        if properties.parent_system_id:
            return "Add new subsystem to the active system."
        return "Add new IfcSystem."

    def _execute(self, context):
        props = tool.System.get_system_props()
        ifc_file = tool.Ifc.get()
        parent_system = None if self.parent_system_id == 0 else ifc_file.by_id(self.parent_system_id)
        core.add_system(tool.Ifc, tool.Group, tool.System, ifc_class=props.system_class, parent_system=parent_system)


class EditSystem(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.edit_system"
    bl_label = "Edit System"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        props = tool.System.get_system_props()
        core.edit_system(tool.Ifc, tool.System, system=tool.Ifc.get().by_id(props.edited_system_id))


class RemoveSystem(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.remove_system"
    bl_label = "Remove System"
    bl_options = {"REGISTER", "UNDO"}
    system: bpy.props.IntProperty()

    def _execute(self, context):
        core.remove_system(tool.Ifc, tool.Group, tool.System, system=tool.Ifc.get().by_id(self.system))


class EnableEditingSystem(bpy.types.Operator):
    bl_idname = "bim.enable_editing_system"
    bl_label = "Enable Editing System"
    bl_options = {"REGISTER", "UNDO"}
    system: bpy.props.IntProperty()

    def execute(self, context):
        core.enable_editing_system(tool.System, system=tool.Ifc.get().by_id(self.system))
        return {"FINISHED"}


class DisableEditingSystem(bpy.types.Operator):
    bl_idname = "bim.disable_editing_system"
    bl_label = "Disable Editing System"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        core.disable_editing_system(tool.System)
        return {"FINISHED"}


class AssignSystem(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.assign_system"
    bl_label = "Assign System"
    bl_description = "Assign system to the selected objects.\n\nIf object is not assignable to this type of system, it will be skiped."
    bl_options = {"REGISTER", "UNDO"}
    system: bpy.props.IntProperty()

    @classmethod
    def poll(cls, context):
        if not context.selected_objects:
            cls.poll_message_set("No objects selected.")
            return False
        return True

    def _execute(self, context):
        elements = [e for o in context.selected_objects if (e := tool.Ifc.get_entity(o))]
        if not elements:
            self.report({"ERROR"}, "No IFC elements selected.")
            return {"CANCELLED"}
        system = tool.Ifc.get().by_id(self.system)
        assignable_elements = [e for e in elements if ifcopenshell.util.system.is_assignable(e, system)]
        if not assignable_elements:
            supported_elements_str = ", ".join(ifcopenshell.util.system.group_types[system.is_a()])
            self.report(
                {"ERROR"},
                f"No elements assignable to {system.is_a()} is selected.\n"
                f"Assignable elements types are: {supported_elements_str}.",
            )
            return {"CANCELLED"}
        core.assign_system(tool.Ifc, system=system, products=assignable_elements)
        self.report({"INFO"}, f"System assigned to {len(assignable_elements)} elements.")
        return {"FINISHED"}


class UnassignSystem(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.unassign_system"
    bl_label = "Unassign System"
    bl_description = "Unassign system from the selected objects."
    bl_options = {"REGISTER", "UNDO"}
    system: bpy.props.IntProperty()

    @classmethod
    def poll(cls, context):
        if not context.selected_objects:
            cls.poll_message_set("No objects selected.")
            return False
        return True

    def _execute(self, context):
        elements = [e for o in context.selected_objects if (e := tool.Ifc.get_entity(o))]
        if not elements:
            self.report({"ERROR"}, "No IFC elements selected.")
            return {"CANCELLED"}
        system = tool.Ifc.get().by_id(self.system)
        core.unassign_system(tool.Ifc, system=system, products=elements)
        self.report({"INFO"}, f"System unassigned from {len(elements)} elements.")
        return {"FINISHED"}


class SelectSystemProducts(bpy.types.Operator):
    bl_idname = "bim.select_system_products"
    bl_label = "Select System Products And Set Active System"
    bl_options = {"REGISTER", "UNDO"}
    system: bpy.props.IntProperty()

    def execute(self, context):
        core.select_system_products(tool.System, system=tool.Ifc.get().by_id(self.system))
        SystemData.data["active_system"] = SystemData.active_system()
        return {"FINISHED"}


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
        # Ifc.Operator - as operator will sync object's position with IFC.
        element = tool.Ifc.get_entity(context.active_object)
        core.show_ports(tool.Ifc, tool.System, tool.Spatial, element=element)

        for port in tool.System.get_ports(element):
            connected_port = tool.System.get_connected_port(port)
            if connected_port:
                connected_port_obj = tool.Ifc.get_object(connected_port)
                if not connected_port_obj:
                    parent_element = tool.System.get_port_relating_element(connected_port)
                    core.show_ports(tool.Ifc, tool.System, tool.Spatial, element=parent_element)


class HidePorts(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.hide_ports"
    bl_label = "Hide Ports"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return ShowPorts.poll(context)

    def _execute(self, context):
        # Ifc.Operator - as operator will sync object and ports positions with IFC.
        core.hide_ports(tool.Ifc, tool.System, element=tool.Ifc.get_entity(context.active_object))


class AddPort(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_port"
    bl_description = "Add USERDEFINED port at current cursor position"
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
        direction = tool.Ifc.get_entity(obj1).FlowDirection or "NOTDEFINED"
        core.connect_port(
            tool.Ifc, port1=tool.Ifc.get_entity(obj1), port2=tool.Ifc.get_entity(obj2), direction=direction
        )


class AddRelatedPortConnection(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_related_port_connection"
    bl_label = "Connect Port"
    bl_options = {"REGISTER", "UNDO"}

    relating_port_id: bpy.props.IntProperty()

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        props = tool.System.get_system_props()
        self.layout.prop(props, "related_port", text="Select Port")

    def _execute(self, context):
        props = tool.System.get_system_props()

        if not props.related_port or props.related_port == "NONE":
            return {"CANCELLED"}

        port_obj = bpy.data.objects.get(props.related_port)
        related_port = tool.Ifc.get_entity(port_obj)
        relating_port = tool.Ifc.get().by_id(self.relating_port_id)

        direction = relating_port.FlowDirection or "NOTDEFINED"
        core.connect_port(tool.Ifc, port1=relating_port, port2=related_port, direction=direction)
        PortData.is_loaded = False

        return {"FINISHED"}


class DisconnectPort(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.disconnect_port"
    bl_label = "Disconnect Ports"
    bl_options = {"REGISTER", "UNDO"}

    element_id: bpy.props.IntProperty(default=0, options={"SKIP_SAVE"})

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

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
    obj1_guid: bpy.props.StringProperty(name="Object 1 GlobalId")
    obj2_guid: bpy.props.StringProperty(name="Object 2 GlobalId")

    def _execute(self, context):
        if self.obj1_guid and self.obj2_guid:
            ifc_file = tool.Ifc.get()
            try:
                el1_lookup = ifc_file.by_guid(self.obj1_guid)
                el2_lookup = ifc_file.by_guid(self.obj2_guid)
            except RuntimeError:
                self.report({"ERROR"}, "Could not resolve MEP elements from supplied GlobalIds.")
                return {"CANCELLED"}
            obj1 = tool.Ifc.get_object(el1_lookup)
            obj2 = tool.Ifc.get_object(el2_lookup)
            if not obj1 or not obj2:
                self.report({"ERROR"}, "Supplied MEP elements have no Blender object bound.")
                return {"CANCELLED"}
        else:
            if not context.selected_objects or len(context.selected_objects) != 2:
                self.report({"ERROR"}, "Need to select 2 objects.")
                return {"CANCELLED"}
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
        direction = closest_ports[0].FlowDirection or "NOTDEFINED"
        core.connect_port(tool.Ifc, *closest_ports, direction=direction)
        bpy.ops.bim.regenerate_distribution_element()
        return {"FINISHED"}


class MEPConnectPorts(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.mep_connect_ports"
    bl_label = "Connect Ports With Segment"
    bl_description = (
        "Connect two selected free ports with a new flow segment.\n"
        "A transition fitting is inserted when the joined segment profiles differ.\n"
        "The segment type is taken from a port's flow segment, "
        "or from the active relating type when neither port belongs to one"
    )
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if len(context.selected_objects) != 2:
            cls.poll_message_set("Select two port objects")
            return False
        return True

    @staticmethod
    def get_profiled_segment_type(element):
        if element is None:
            return None
        element_type = ifcopenshell.util.element.get_type(element)
        if element_type and element_type.is_a("IfcFlowSegmentType"):
            material = ifcopenshell.util.element.get_material(element_type)
            if material and material.is_a("IfcMaterialProfileSet"):
                return element_type
        return None

    @staticmethod
    def profiles_match(profile1, profile2):
        if profile1 is None or profile2 is None:
            return True
        if profile1 == profile2:
            return True
        if profile1.is_a() != profile2.is_a():
            return False
        if profile1.is_a("IfcCircleProfileDef"):
            return tool.Cad.is_x(profile1.Radius, profile2.Radius)
        if profile1.is_a("IfcRectangleProfileDef"):
            return tool.Cad.is_x(profile1.XDim, profile2.XDim) and tool.Cad.is_x(profile1.YDim, profile2.YDim)
        return True

    def _execute(self, context):
        # Lazy imports to avoid a circular dependency at addon load.
        from bonsai.bim.module.model.mep import MEPGenerator
        from bonsai.bim.module.model.profile import DumbProfileGenerator

        obj1 = context.active_object
        obj2 = next((o for o in context.selected_objects if o != obj1), None)
        port1 = tool.Ifc.get_entity(obj1) if obj1 else None
        port2 = tool.Ifc.get_entity(obj2) if obj2 else None
        if not port1 or not port2 or not port1.is_a("IfcDistributionPort") or not port2.is_a("IfcDistributionPort"):
            self.report({"ERROR"}, "Select exactly two ports (use Show Ports on MEP elements first).")
            return {"CANCELLED"}
        if tool.System.get_connected_port(port1) or tool.System.get_connected_port(port2):
            self.report({"ERROR"}, "Both ports need to be free to connect them.")
            return {"CANCELLED"}

        element1 = tool.System.get_port_relating_element(port1)
        element2 = tool.System.get_port_relating_element(port2)
        if element1 == element2:
            self.report({"ERROR"}, "Both ports belong to the same element.")
            return {"CANCELLED"}

        tool.Model.sync_object_ifc_position(obj1)
        tool.Model.sync_object_ifc_position(obj2)
        p1 = obj1.matrix_world.translation.copy()
        p2 = obj2.matrix_world.translation.copy()

        if (p2 - p1).length < 1e-5:
            direction = direction_from_port_pair(port1, port2)
            core.connect_port(tool.Ifc, port1=port1, port2=port2, direction=direction)
            PortData.is_loaded = False
            return {"FINISHED"}

        relating_type = self.get_profiled_segment_type(element1)
        if not relating_type and (relating_type := self.get_profiled_segment_type(element2)):
            obj1, obj2 = obj2, obj1
            port1, port2 = port2, port1
            element1, element2 = element2, element1
            p1, p2 = p2, p1
        if not relating_type:
            props = tool.Model.get_model_props()
            if props.relating_type_id:
                candidate = tool.Ifc.get().by_id(int(props.relating_type_id))
                if candidate.is_a("IfcFlowSegmentType"):
                    material = ifcopenshell.util.element.get_material(candidate)
                    if material and material.is_a("IfcMaterialProfileSet"):
                        relating_type = candidate
        if not relating_type:
            self.report(
                {"ERROR"},
                "No flow segment type with a profile found on either port. "
                "Select a pipe or duct type in the Add tool first.",
            )
            return {"CANCELLED"}

        data = DumbProfileGenerator(relating_type).generate(coords=(p1, p2))
        if not data or not data.get("obj"):
            self.report({"ERROR"}, "Failed to generate a connecting segment.")
            return {"CANCELLED"}
        segment_obj = data["obj"]
        segment = tool.Ifc.get_entity(segment_obj)

        # When the run continues a parallel segment, match its roll so a transition can be fitted.
        element2_obj = tool.Ifc.get_object(element2)
        direction_vec = (p2 - p1).normalized()
        if element2 is not None and element2.is_a("IfcFlowSegment") and element2_obj:
            element2_quat = element2_obj.matrix_world.to_quaternion()
            element2_axis = element2_quat @ Vector((0.0, 0.0, 1.0))
            dot = element2_axis.dot(direction_vec)
            if abs(abs(dot) - 1) < 1e-4:
                quat = element2_quat if dot > 0 else element2_quat @ Quaternion((1.0, 0.0, 0.0), pi)
                matrix = quat.to_matrix().to_4x4()
                matrix.translation = p1
                segment_obj.matrix_world = matrix
                bpy.context.view_layer.update()
                tool.System.run_geometry_edit_object_placement(segment_obj)

        MEPGenerator(relating_type).setup_ports(segment_obj)
        segment_data = MEPGenerator.get_segment_data(segment)
        start_port = segment_data.get("start_port")
        end_port = segment_data.get("end_port")
        if not start_port or not end_port:
            self.report({"ERROR"}, "Generated segment is missing ports.")
            return {"CANCELLED"}

        core.connect_port(
            tool.Ifc, port1=start_port, port2=port1, direction=direction_from_port_pair(start_port, port1)
        )

        profile1 = tool.Model.get_flow_segment_profile(segment)
        profile2 = (
            tool.Model.get_flow_segment_profile(element2)
            if element2 is not None and element2.is_a("IfcFlowSegment")
            else None
        )
        if profile2 is not None and not self.profiles_match(profile1, profile2) and element2_obj:
            axes_parallel = tool.Cad.are_edges_parallel(
                tool.Model.get_flow_segment_axis(segment_obj), tool.Model.get_flow_segment_axis(element2_obj)
            )
            if axes_parallel:
                try:
                    result = bpy.ops.bim.mep_add_transition(start_segment_id=segment.id(), end_segment_id=element2.id())
                except RuntimeError:
                    result = {"CANCELLED"}
                if "FINISHED" in result:
                    PortData.is_loaded = False
                    return {"FINISHED"}
            self.report(
                {"INFO"}, "Segment profiles differ but no transition could be fitted; ports connected directly."
            )

        core.connect_port(tool.Ifc, port1=end_port, port2=port2, direction=direction_from_port_pair(end_port, port2))
        PortData.is_loaded = False
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


class CycleFlowDirection(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.cycle_flow_direction"
    bl_label = "Cycle Flow Direction"
    bl_options = {"REGISTER", "UNDO"}
    port_id: bpy.props.IntProperty()

    @classmethod
    def description(cls, context, operator):
        port = tool.Ifc.get().by_id(operator.port_id)
        if port and port.is_a("IfcDistributionPort"):
            current_direction = port.FlowDirection or "NOTDEFINED"
            return f"Current flow direction: {current_direction}. Click to cycle: SOURCE → SINK → SOURCEANDSINK → NOTDEFINED"
        return "Cycle through flow directions: SOURCE → SINK → SOURCEANDSINK → NOTDEFINED → SOURCE..."

    def _execute(self, context):
        ifc_file = tool.Ifc.get()
        port = tool.Ifc.get().by_id(self.port_id)
        if not port or not port.is_a("IfcDistributionPort"):
            return {"CANCELLED"}

        current_direction = port.FlowDirection or "NOTDEFINED"

        flow_cycle_map = {
            "SOURCE": "SINK",
            "SINK": "SOURCEANDSINK",
            "SOURCEANDSINK": "NOTDEFINED",
            "NOTDEFINED": "SOURCE",
        }
        next_direction = flow_cycle_map.get(current_direction, "SOURCE")

        ifcopenshell.api.attribute.edit_attributes(ifc_file, product=port, attributes={"FlowDirection": next_direction})

        connected_port = tool.System.get_connected_port(port)
        if connected_port:
            connected_direction_map = {
                "SOURCE": "SINK",
                "SINK": "SOURCE",
                "SOURCEANDSINK": "SOURCEANDSINK",
                "NOTDEFINED": "NOTDEFINED",
            }
            connected_direction = connected_direction_map.get(next_direction, "NOTDEFINED")
            ifcopenshell.api.attribute.edit_attributes(
                ifc_file, product=connected_port, attributes={"FlowDirection": connected_direction}
            )

        PortData.is_loaded = False

        return {"FINISHED"}


class EstablishPathDirection(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.establish_path_direction"
    bl_label = "Establish Path Direction"
    bl_description = "Propagates flow direction through connected flow segments with two ports"
    bl_options = {"REGISTER", "UNDO"}
    port_id: bpy.props.IntProperty()

    def _execute(self, context):
        connected_port = tool.Ifc.get().by_id(self.port_id)

        if not connected_port or not connected_port.is_a("IfcDistributionPort"):
            self.report({"ERROR"}, "Invalid port specified.")
            return {"CANCELLED"}

        direction_map = {
            "SOURCE": "SINK",
            "SINK": "SOURCE",
            "SOURCEANDSINK": "SOURCEANDSINK",
            "NOTDEFINED": "NOTDEFINED",
        }
        next_element = tool.System.get_port_relating_element(connected_port)
        ports = tool.System.get_ports(next_element)
        segments_processed = 0
        while len(ports) == 2:
            if ports[0].id() == connected_port.id():
                other_port = ports[1]
            else:
                other_port = ports[0]

            new_direction = direction_map.get(connected_port.FlowDirection, "NOTDEFINED")
            other_port.FlowDirection = new_direction
            segments_processed += 1

            connected_port = tool.System.get_connected_port(other_port)
            if not connected_port:
                break
            connected_port.FlowDirection = direction_map.get(other_port.FlowDirection, "NOTDEFINED")
            next_element = tool.System.get_port_relating_element(connected_port)

            if not next_element.is_a("IfcFlowSegment"):
                print(f"DEBUG: next_element is not IfcFlowSegment, stopping")
                break

            ports = tool.System.get_ports(next_element)

        self.report({"INFO"}, f"Established path direction through {segments_processed} flow segment(s).")
        return {"FINISHED"}


class LoadZones(bpy.types.Operator):
    bl_idname = "bim.load_zones"
    bl_label = "Load Zones"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        props = tool.System.get_zone_props()
        props.zones.clear()
        for zone in tool.Ifc.get().by_type("IfcZone"):
            new = props.zones.add()
            new.ifc_definition_id = zone.id()
            new["name"] = zone.Name or "Unnamed"
        props.is_loaded = True
        props.is_editing = 0
        return {"FINISHED"}


class UnloadZones(bpy.types.Operator):
    bl_idname = "bim.unload_zones"
    bl_label = "Unload Zones"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        props = tool.System.get_zone_props()
        props.is_loaded = False
        return {"FINISHED"}


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
        element = ifcopenshell.api.system.add_system(tool.Ifc.get(), ifc_class="IfcZone")
        if self.name:
            element.Name = self.name
        bpy.ops.bim.load_zones()


class EnableEditingZone(bpy.types.Operator):
    bl_idname = "bim.enable_editing_zone"
    bl_label = "Enable Editing Zone"
    bl_options = {"REGISTER", "UNDO"}
    zone: bpy.props.IntProperty()

    def execute(self, context):
        props = tool.System.get_zone_props()
        props.attributes.clear()
        bonsai.bim.helper.import_attributes(tool.Ifc.get().by_id(self.zone), props.attributes)
        props.is_editing = self.zone
        return {"FINISHED"}


class DisableEditingZone(bpy.types.Operator):
    bl_idname = "bim.disable_editing_zone"
    bl_label = "Disable Editing Zone"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        props = tool.System.get_zone_props()
        props.is_editing = 0
        return {"FINISHED"}


class EditZone(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.edit_zone"
    bl_label = "Edit Zone"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        props = tool.System.get_zone_props()
        zone = tool.Ifc.get().by_id(props.is_editing)
        attributes = bonsai.bim.helper.export_attributes(props.attributes)
        ifcopenshell.api.system.edit_system(tool.Ifc.get(), system=zone, attributes=attributes)
        props.is_editing = 0
        bpy.ops.bim.load_zones()


class RemoveZone(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.remove_zone"
    bl_label = "Remove Zone"
    bl_options = {"REGISTER", "UNDO"}
    zone: bpy.props.IntProperty()

    def _execute(self, context):
        ifcopenshell.api.system.remove_system(tool.Ifc.get(), system=tool.Ifc.get().by_id(self.zone))
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
                ifcopenshell.api.system.assign_flow_control(
                    ifc_file, relating_flow_element=flow_element, related_flow_control=control
                )
            else:
                ifcopenshell.api.system.unassign_flow_control(
                    ifc_file, relating_flow_element=flow_element, related_flow_control=control
                )

        if from_selected_objects:
            self.report(
                {"INFO"}, f"{len(flow_controls)} flow controls were {'assigned' if self.assign else 'unassigned'}."
            )
        return {"FINISHED"}
