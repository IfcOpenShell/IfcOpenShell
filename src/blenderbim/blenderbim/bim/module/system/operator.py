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
import ifcopenshell.api
import blenderbim.tool as tool
import blenderbim.core.system as core
import blenderbim.bim.handler
from blenderbim.bim.ifc import IfcStore


class Operator:
    def execute(self, context):
        IfcStore.execute_ifc_operator(self, context)
        blenderbim.bim.handler.refresh_ui_data()
        return {"FINISHED"}


class LoadSystems(bpy.types.Operator, Operator):
    bl_idname = "bim.load_systems"
    bl_label = "Load Systems"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.load_systems(tool.System)


class DisableSystemEditingUI(bpy.types.Operator, Operator):
    bl_idname = "bim.disable_system_editing_ui"
    bl_label = "Disable System Editing UI"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.disable_system_editing_ui(tool.System)


class AddSystem(bpy.types.Operator, Operator):
    bl_idname = "bim.add_system"
    bl_label = "Add System"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.add_system(tool.Ifc, tool.System, ifc_class=context.scene.BIMSystemProperties.system_class)


class EditSystem(bpy.types.Operator, Operator):
    bl_idname = "bim.edit_system"
    bl_label = "Edit System"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.edit_system(
            tool.Ifc, tool.System, system=tool.Ifc.get().by_id(context.scene.BIMSystemProperties.active_system_id)
        )


class RemoveSystem(bpy.types.Operator, Operator):
    bl_idname = "bim.remove_system"
    bl_label = "Remove System"
    bl_options = {"REGISTER", "UNDO"}
    system: bpy.props.IntProperty()

    def _execute(self, context):
        core.remove_system(tool.Ifc, tool.System, system=tool.Ifc.get().by_id(self.system))


class EnableEditingSystem(bpy.types.Operator, Operator):
    bl_idname = "bim.enable_editing_system"
    bl_label = "Enable Editing System"
    bl_options = {"REGISTER", "UNDO"}
    system: bpy.props.IntProperty()

    def _execute(self, context):
        core.enable_editing_system(tool.System, system=tool.Ifc.get().by_id(self.system))


class DisableEditingSystem(bpy.types.Operator, Operator):
    bl_idname = "bim.disable_editing_system"
    bl_label = "Disable Editing System"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.disable_editing_system(tool.System)


class AssignSystem(bpy.types.Operator, Operator):
    bl_idname = "bim.assign_system"
    bl_label = "Assign System"
    bl_options = {"REGISTER", "UNDO"}
    system: bpy.props.IntProperty()

    def _execute(self, context):
        for obj in context.selected_objects:
            element = tool.Ifc.get_entity(obj)
            if element:
                core.assign_system(tool.Ifc, system=tool.Ifc.get().by_id(self.system), product=element)


class UnassignSystem(bpy.types.Operator, Operator):
    bl_idname = "bim.unassign_system"
    bl_label = "Unassign System"
    bl_options = {"REGISTER", "UNDO"}
    system: bpy.props.IntProperty()

    def _execute(self, context):
        for obj in context.selected_objects:
            element = tool.Ifc.get_entity(obj)
            if element:
                core.unassign_system(tool.Ifc, system=tool.Ifc.get().by_id(self.system), product=element)


class SelectSystemProducts(bpy.types.Operator, Operator):
    bl_idname = "bim.select_system_products"
    bl_label = "Select System Products"
    bl_options = {"REGISTER", "UNDO"}
    system: bpy.props.IntProperty()

    def _execute(self, context):
        core.select_system_products(tool.System, system=tool.Ifc.get().by_id(self.system))


class ShowPorts(bpy.types.Operator, Operator):
    bl_idname = "bim.show_ports"
    bl_label = "Show Ports"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.show_ports(tool.Ifc, tool.System, element=tool.Ifc.get_entity(context.active_object))


class HidePorts(bpy.types.Operator, Operator):
    bl_idname = "bim.hide_ports"
    bl_label = "Hide Ports"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.hide_ports(tool.Ifc, tool.System, element=tool.Ifc.get_entity(context.active_object))


class AddPort(bpy.types.Operator, Operator):
    bl_idname = "bim.add_port"
    bl_label = "Add Port"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.add_port(tool.Ifc, tool.System, element=tool.Ifc.get_entity(context.active_object))


class RemovePort(bpy.types.Operator, Operator):
    bl_idname = "bim.remove_port"
    bl_label = "Remove Port"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.remove_port(tool.Ifc, tool.System, port=tool.Ifc.get_entity(context.active_object))


class ConnectPort(bpy.types.Operator, Operator):
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


class DisconnectPort(bpy.types.Operator, Operator):
    bl_idname = "bim.disconnect_port"
    bl_label = "Disconnect Ports"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.disconnect_port(tool.Ifc, port=tool.Ifc.get_entity(context.active_object))


class SetFlowDirection(bpy.types.Operator, Operator):
    bl_idname = "bim.set_flow_direction"
    bl_label = "Set Flow Direction"
    bl_options = {"REGISTER", "UNDO"}
    direction: bpy.props.StringProperty()

    def _execute(self, context):
        core.set_flow_direction(
            tool.Ifc, tool.System, port=tool.Ifc.get_entity(context.active_object), direction=self.direction
        )
