
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
import ifcopenshell.util.attribute
import ifcopenshell.api
import blenderbim.bim.helper
from blenderbim.bim.ifc import IfcStore
from ifcopenshell.api.system.data import Data


class LoadSystems(bpy.types.Operator):
    bl_idname = "bim.load_systems"
    bl_label = "Load Systems"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        props = context.scene.BIMSystemProperties
        props.systems.clear()
        for ifc_definition_id, system in Data.systems.items():
            new = props.systems.add()
            new.ifc_definition_id = ifc_definition_id
            new.name = system["Name"]
        props.is_editing = True
        bpy.ops.bim.disable_editing_system()
        return {"FINISHED"}


class DisableSystemEditingUI(bpy.types.Operator):
    bl_idname = "bim.disable_system_editing_ui"
    bl_label = "Disable System Editing UI"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        context.scene.BIMSystemProperties.is_editing = False
        context.scene.BIMSystemProperties.active_system_id = 0
        return {"FINISHED"}


class AddSystem(bpy.types.Operator):
    bl_idname = "bim.add_system"
    bl_label = "Add System"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        result = ifcopenshell.api.run("system.add_system", IfcStore.get_file())
        Data.load(IfcStore.get_file())
        bpy.ops.bim.load_systems()
        bpy.ops.bim.enable_editing_system(system=result.id())
        return {"FINISHED"}


class EditSystem(bpy.types.Operator):
    bl_idname = "bim.edit_system"
    bl_label = "Edit System"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        props = context.scene.BIMSystemProperties
        attributes = {}
        for attribute in props.system_attributes:
            if attribute.is_null:
                attributes[attribute.name] = None
            else:
                attributes[attribute.name] = attribute.string_value
        self.file = IfcStore.get_file()
        ifcopenshell.api.run(
            "system.edit_system", self.file, **{"system": self.file.by_id(props.active_system_id), "attributes": attributes}
        )
        Data.load(IfcStore.get_file())
        bpy.ops.bim.load_systems()
        return {"FINISHED"}


class RemoveSystem(bpy.types.Operator):
    bl_idname = "bim.remove_system"
    bl_label = "Remove System"
    bl_options = {"REGISTER", "UNDO"}
    system: bpy.props.IntProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        props = context.scene.BIMSystemProperties
        self.file = IfcStore.get_file()
        ifcopenshell.api.run("system.remove_system", self.file, **{"system": self.file.by_id(self.system)})
        Data.load(IfcStore.get_file())
        bpy.ops.bim.load_systems()
        return {"FINISHED"}


class EnableEditingSystem(bpy.types.Operator):
    bl_idname = "bim.enable_editing_system"
    bl_label = "Enable Editing System"
    bl_options = {"REGISTER", "UNDO"}
    system: bpy.props.IntProperty()

    def execute(self, context):
        props = context.scene.BIMSystemProperties
        props.system_attributes.clear()

        blenderbim.bim.helper.import_attributes("IfcSystem", props.system_attributes, Data.systems[self.system])
        props.active_system_id = self.system
        return {"FINISHED"}


class DisableEditingSystem(bpy.types.Operator):
    bl_idname = "bim.disable_editing_system"
    bl_label = "Disable Editing System"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        context.scene.BIMSystemProperties.active_system_id = 0
        return {"FINISHED"}


class ToggleAssigningSystem(bpy.types.Operator):
    bl_idname = "bim.toggle_assigning_system"
    bl_label = "Toggle Assigning System"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        context.scene.BIMSystemProperties.is_adding = not context.scene.BIMSystemProperties.is_adding
        return {"FINISHED"}


class AssignSystem(bpy.types.Operator):
    bl_idname = "bim.assign_system"
    bl_label = "Assign System"
    bl_options = {"REGISTER", "UNDO"}
    product: bpy.props.StringProperty()
    system: bpy.props.IntProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        self.file = IfcStore.get_file()
        products = [bpy.data.objects.get(self.product)] if self.product else context.selected_objects
        for product in products:
            if not product.BIMObjectProperties.ifc_definition_id:
                continue
            ifcopenshell.api.run(
                "system.assign_system",
                self.file,
                **{
                    "product": self.file.by_id(product.BIMObjectProperties.ifc_definition_id),
                    "system": self.file.by_id(self.system),
                }
            )
        Data.load(self.file)
        return {"FINISHED"}


class UnassignSystem(bpy.types.Operator):
    bl_idname = "bim.unassign_system"
    bl_label = "Unassign System"
    bl_options = {"REGISTER", "UNDO"}
    product: bpy.props.StringProperty()
    system: bpy.props.IntProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        self.file = IfcStore.get_file()
        products = [bpy.data.objects.get(self.product)] if self.product else context.selected_objects
        for product in products:
            props = product.BIMObjectProperties
            if not props.ifc_definition_id:
                continue
            if not (props.ifc_definition_id in Data.products and self.system in Data.products[props.ifc_definition_id]):
                continue
            ifcopenshell.api.run(
                "system.unassign_system",
                self.file,
                **{
                    "product": self.file.by_id(product.BIMObjectProperties.ifc_definition_id),
                    "system": self.file.by_id(self.system),
                }
            )
        Data.load(self.file)
        return {"FINISHED"}


class SelectSystemProducts(bpy.types.Operator):
    bl_idname = "bim.select_system_products"
    bl_label = "Select System Products"
    bl_options = {"REGISTER", "UNDO"}
    system: bpy.props.IntProperty()

    def execute(self, context):
        for obj in context.visible_objects:
            obj.select_set(False)
            if not obj.BIMObjectProperties.ifc_definition_id:
                continue
            product_systems = Data.products.get(obj.BIMObjectProperties.ifc_definition_id, [])
            if self.system in product_systems:
                obj.select_set(True)
        return {"FINISHED"}
