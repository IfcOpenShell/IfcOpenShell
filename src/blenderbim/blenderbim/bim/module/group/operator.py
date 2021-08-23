
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
from blenderbim.bim.ifc import IfcStore
from ifcopenshell.api.group.data import Data


class LoadGroups(bpy.types.Operator):
    bl_idname = "bim.load_groups"
    bl_label = "Load Groups"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        props = context.scene.BIMGroupProperties
        props.groups.clear()
        for ifc_definition_id, group in Data.groups.items():
            new = props.groups.add()
            new.ifc_definition_id = ifc_definition_id
            new.name = group["Name"]
        props.is_editing = True
        bpy.ops.bim.disable_editing_group()
        return {"FINISHED"}


class DisableGroupEditingUI(bpy.types.Operator):
    bl_idname = "bim.disable_group_editing_ui"
    bl_label = "Disable Group Editing UI"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        context.scene.BIMGroupProperties.is_editing = False
        return {"FINISHED"}


class AddGroup(bpy.types.Operator):
    bl_idname = "bim.add_group"
    bl_label = "Add Group"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        result = ifcopenshell.api.run("group.add_group", IfcStore.get_file())
        Data.load(IfcStore.get_file())
        bpy.ops.bim.load_groups()
        bpy.ops.bim.enable_editing_group(group=result.id())
        return {"FINISHED"}


class EditGroup(bpy.types.Operator):
    bl_idname = "bim.edit_group"
    bl_label = "Edit Group"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        props = context.scene.BIMGroupProperties
        attributes = {}
        for attribute in props.group_attributes:
            if attribute.is_null:
                attributes[attribute.name] = None
            else:
                attributes[attribute.name] = attribute.string_value
        self.file = IfcStore.get_file()
        ifcopenshell.api.run(
            "group.edit_group", self.file, **{"group": self.file.by_id(props.active_group_id), "attributes": attributes}
        )
        Data.load(IfcStore.get_file())
        bpy.ops.bim.load_groups()
        return {"FINISHED"}


class RemoveGroup(bpy.types.Operator):
    bl_idname = "bim.remove_group"
    bl_label = "Remove Group"
    bl_options = {"REGISTER", "UNDO"}
    group: bpy.props.IntProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        props = context.scene.BIMGroupProperties
        self.file = IfcStore.get_file()
        ifcopenshell.api.run("group.remove_group", self.file, **{"group": self.file.by_id(self.group)})
        Data.load(IfcStore.get_file())
        bpy.ops.bim.load_groups()
        return {"FINISHED"}


class EnableEditingGroup(bpy.types.Operator):
    bl_idname = "bim.enable_editing_group"
    bl_label = "Enable Editing Group"
    bl_options = {"REGISTER", "UNDO"}
    group: bpy.props.IntProperty()

    def execute(self, context):
        props = context.scene.BIMGroupProperties
        props.group_attributes.clear()

        data = Data.groups[self.group]

        for attribute in IfcStore.get_schema().declaration_by_name("IfcGroup").all_attributes():
            data_type = ifcopenshell.util.attribute.get_primitive_type(attribute)
            if data_type == "entity":
                continue
            new = props.group_attributes.add()
            new.name = attribute.name()
            new.is_null = data[attribute.name()] is None
            new.is_optional = attribute.optional()
            new.string_value = "" if new.is_null else data[attribute.name()]
        props.active_group_id = self.group
        return {"FINISHED"}


class DisableEditingGroup(bpy.types.Operator):
    bl_idname = "bim.disable_editing_group"
    bl_label = "Disable Editing Group"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        context.scene.BIMGroupProperties.active_group_id = 0
        return {"FINISHED"}


class AssignGroupToMany(bpy.types.Operator):
    bl_idname = "bim.assign_group_to_many"
    bl_label = "Assign Group to Selected Objects"
    bl_options = {"REGISTER", "UNDO"}
    group: bpy.props.IntProperty()

    @classmethod
    def poll(cls, context):
        return context.selected_objects

    def execute(self, context):        
        for obj in (o for o in context.selected_objects if o.BIMObjectProperties.ifc_definition_id):
            bpy.ops.bim.assign_group(product=obj.name, group=self.group)
        return {"FINISHED"}


class AssignGroup(bpy.types.Operator):
    bl_idname = "bim.assign_group"
    bl_label = "Assign Group"
    bl_options = {"REGISTER", "UNDO"}
    product: bpy.props.StringProperty()
    group: bpy.props.IntProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        product = bpy.data.objects.get(self.product, context.active_object)
        self.file = IfcStore.get_file()
        ifcopenshell.api.run(
            "group.assign_group",
            self.file,
            **{
                "product": self.file.by_id(product.BIMObjectProperties.ifc_definition_id),
                "group": self.file.by_id(self.group),
            }
        )
        Data.load(IfcStore.get_file())
        return {"FINISHED"}


class UnassignGroupFromMany(bpy.types.Operator):
    bl_idname = "bim.unassign_group_from_many"
    bl_label = "Unassign Group from Selected Objects"
    bl_options = {"REGISTER", "UNDO"}
    group: bpy.props.IntProperty()

    @classmethod
    def poll(cls, context):
        return context.selected_objects

    def execute(self, context):        
        for obj in (o for o in context.selected_objects if o.BIMObjectProperties.ifc_definition_id):
            bpy.ops.bim.unassign_group(product=obj.name, group=self.group)
        return {"FINISHED"}


class UnassignGroup(bpy.types.Operator):
    bl_idname = "bim.unassign_group"
    bl_label = "Unassign Group"
    bl_options = {"REGISTER", "UNDO"}
    product: bpy.props.StringProperty()
    group: bpy.props.IntProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        product = bpy.data.objects.get(self.product, context.active_object)
        self.file = IfcStore.get_file()
        ifcopenshell.api.run(
            "group.unassign_group",
            self.file,
            **{
                "product": self.file.by_id(product.BIMObjectProperties.ifc_definition_id),
                "group": self.file.by_id(self.group),
            }
        )
        Data.load(IfcStore.get_file())
        return {"FINISHED"}


class SelectGroupProducts(bpy.types.Operator):
    bl_idname = "bim.select_group_products"
    bl_label = "Select Group Products"
    bl_options = {"REGISTER", "UNDO"}
    group: bpy.props.IntProperty()

    def execute(self, context):
        self.file = IfcStore.get_file()
        for obj in context.visible_objects:
            obj.select_set(False)
            if not obj.BIMObjectProperties.ifc_definition_id:
                continue
            product_groups = Data.products.get(obj.BIMObjectProperties.ifc_definition_id, [])
            if self.group in product_groups:
                obj.select_set(True)
        return {"FINISHED"}
