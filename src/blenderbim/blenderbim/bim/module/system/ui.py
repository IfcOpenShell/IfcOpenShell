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
from ifcopenshell.api.system.data import Data


class BIM_PT_systems(Panel):
    bl_label = "IFC Systems"
    bl_idname = "BIM_PT_systems"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"

    @classmethod
    def poll(cls, context):
        view_setting = context.preferences.addons["blenderbim"].preferences.module_visibility
        if not IfcStore.get_file():
            return False
        return view_setting.system

    def draw(self, context):
        if not Data.is_loaded:
            Data.load(IfcStore.get_file())
        self.props = context.scene.BIMSystemProperties

        row = self.layout.row(align=True)
        row.label(text="{} Systems Found".format(len(Data.systems)), icon="OUTLINER")
        if self.props.is_editing:
            row.operator("bim.add_system", text="", icon="ADD")
            row.operator("bim.disable_system_editing_ui", text="", icon="CANCEL")
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

    @classmethod
    def poll(cls, context):
        view_setting = context.preferences.addons["blenderbim"].preferences.module_visibility
        if not context.active_object:
            return False
        if not IfcStore.get_file() and context.active_object.BIMObjectProperties.ifc_definition_id:
            return False
        return view_setting.system

    def draw(self, context):
        if not Data.is_loaded:
            Data.load(IfcStore.get_file())
        self.props = context.scene.BIMSystemProperties
        row = self.layout.row(align=True)
        if self.props.is_adding:
            row.label(text="Adding Systems", icon="OUTLINER")
            row.operator("bim.toggle_assigning_system", text="", icon="CANCEL")
            self.layout.template_list(
                "BIM_UL_object_systems",
                "",
                self.props,
                "systems",
                self.props,
                "active_system_index",
            )
        else:
            row.label(text=f"{len(Data.systems)} Systems in IFC Project", icon="OUTLINER")
            row.operator("bim.toggle_assigning_system", text="", icon="ADD")

        systems_object = Data.products.get(context.active_object.BIMObjectProperties.ifc_definition_id, [])
        for system_id in systems_object:
            row = self.layout.row(align=True)
            row.label(text=Data.systems[system_id].get("Name", "Unnamed"))
            op = row.operator("bim.unassign_system", text="", icon="X")
            op.system = system_id

        if not systems_object:
            self.layout.label(text="No System associated with Active Object")


class BIM_UL_systems(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if item:
            row = layout.row(align=True)
            row.label(text=item.name)
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
        if item:
            row = layout.row(align=True)
            row.label(text=item.name)
            op = row.operator("bim.assign_system", text="", icon="ADD")
            op.system = item.ifc_definition_id
