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


class BIM_PT_systems(Panel):
    bl_label = "Systems"
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
    bl_parent_id = "BIM_PT_services_object"

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
        row.label(text=f"{PortData.data['total_ports']} Ports Found", icon="PLUGIN")
        row.operator("bim.show_ports", icon="HIDE_OFF", text="")
        row.operator("bim.hide_ports", icon="HIDE_ON", text="")
        row.operator("bim.add_port", icon="ADD", text="")


class BIM_PT_port(Panel):
    bl_label = "Port"
    bl_idname = "BIM_PT_port"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"
    bl_order = 1
    bl_parent_id = "BIM_PT_services_object"

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
        row = self.layout.row(align=True)
        row.operator("bim.connect_port", icon="PLUGIN", text="")
        row.operator("bim.disconnect_port", icon="UNLINKED", text="")
        row.operator("bim.set_flow_direction", icon="FORWARD", text="").direction = "SOURCE"
        row.operator("bim.set_flow_direction", icon="BACK", text="").direction = "SINK"
        row.operator("bim.set_flow_direction", icon="ARROW_LEFTRIGHT", text="").direction = "SOURCEANDSINK"
        row.operator("bim.set_flow_direction", icon="RESTRICT_INSTANCED_ON", text="").direction = "NOTDEFINED"
        row.operator("bim.remove_port", icon="X", text="")


class BIM_UL_systems(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        system_icons = {
            "IfcSystem": "EXTERNAL_DRIVE",
            "IfcDistributionSystem": "NETWORK_DRIVE",
            "IfcDistributionCircuit": "DRIVER",
            "IfcBuildingSystem": "MOD_BUILD",
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
            "IfcZone": "CUBE",
        }
        if item:
            row = layout.row(align=True)
            row.label(text=item.name, icon=system_icons[item.ifc_class])
            row.operator("bim.assign_system", text="", icon="ADD").system = item.ifc_definition_id

class BIM_PT_systems_navigator_main_panel(Panel):
    bl_label = "System Navigator"
    bl_idname = "BIM_PT_systems_navigator_main_panel"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_services"

    @classmethod
    def poll(cls, context):
        return True

    def draw(self, context):
        layout = layout
        #row = layout.row()

class BIM_PT_systems_navigator_sub_panel(Panel):
    bl_parent_id = "BIM_PT_systems_navigator_main_panel"
    bl_label = "Sub panel name assigned by a for loop"
    bl_idname = "Id name assigned by a for loop"
    bl_space_type = BIM_PT_systems_navigator_main_panel.bl_space_type
    bl_region_type = BIM_PT_systems_navigator_main_panel.bl_region_type
    bl_options = {"DEFAULT_CLOSED"}
    ifc_systems = "Assigned by a for loop"
    
    @classmethod
    def poll(cls, context):
        return True

    def draw(self, context):
        for system in ifc_systems:
            layout = layout
            col = layout.column(align=True)
            row = col.row(align=True)
            row.label(text=str(system.Name))
            #info = row.operator(SelectSystemProductsByGuid.bl_idname,icon="INFO")
            info = row.operator(GetIfcSystemInfoByGuid.bl_idname,icon="INFO")
            select = row.operator(SelectSystemProductsByGuid.bl_idname,icon="RESTRICT_SELECT_OFF")
            edit = row.operator(IfcSystemEditingPanel.bl_idname,icon="GREASEPENCIL")
            #edit.ifcSystemColor = (0.3,0.7,0.2,1.0)
            for op in [info, select, edit]:
                op.guid = system.GlobalId


def get_ifc_systems_in_current_file():
    ifcSystemObjectTypeDict = {}
    for ifcSystem in tool.Ifc.get().by_type("IfcSystem"):
        ifcSystemObjectType = ifcSystem.ObjectType
        if ifcSystemObjectType in ifcSystemObjectTypeDict:
            ifcSystemObjectTypeDict[ifcSystemObjectType].append(ifcSystem)
        else:
            ifcSystemObjectTypeDict[ifcSystemObjectType] = [ifcSystem]

    for ifcSystemKey in ifcSystemObjectTypeDict:
        strNumDict = {}
        strOnlyList = []
        for ifcSystemName in ([ifcSystem.Name for ifcSystem in ifcSystemObjectTypeDict[ifcSystemKey]]):
            index = ifcSystemName.rfind(" ")
            if index >= 0:
                num = ifcSystemName[index+1:]
                if num.isdigit():
                    name = ifcSystemName[:index]
                    #print(name, num)
                    if name in strNumDict:
                        strNumDict[name].append(num)
                    else:
                        strNumDict[name] = [num]
                else:
                    strOnlyList.append(ifcSystemName)
        sortedList = []
        for key in sorted(strNumDict.keys()):
            tempNumList = [int(num) for num in sorted(strNumDict[key])]
            for tempNum in sorted(tempNumList):
                sortedList.append(f"{str(key)} {str(tempNum)}")
        sortedIfcSystemName = sortedList+ sorted(strOnlyList)

        tempList = []
        for sortedName in sortedIfcSystemName:
            for ifcSystem in ifcSystemObjectTypeDict[ifcSystemKey]:
                if ifcSystem.Name == sortedName:
                    tempList.append(ifcSystem)
        ifcSystemObjectTypeDict[ifcSystemKey] = tempList
    return (ifcSystemObjectTypeDict)

ifcSystemObjectTypeDict = get_ifc_systems_in_current_file()

def CreatingSubPanels():
    for key in sorted(BIM_PT_systems_navigator_main_panel.ifcSystemObjectTypeDict):
        id = f"BIM_PT_systems_navigator_sub_panel_{key}"
        print(BIM_PT_systems_navigator_main_panel.ifcSystemObjectTypeDict[str(key)])
        panel = type(id,
            (BIM_PT_systems_navigator_sub_panel, Panel, ),
            {"bl_idname" : id,
            "bl_label" : str(key),
            "ifc_systems" : BIM_PT_systems_navigator_main_panel.ifcSystemObjectTypeDict[str(key)],
             "count" : key}
            )
        classes.append(panel)

CreatingSubPanels()

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        try:
            unregister_class(cls)
        except:
            pass

if __name__ == "__main__":
    register()