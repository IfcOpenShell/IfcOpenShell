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
import blenderbim.tool as tool
from blenderbim.bim.ifc import IfcStore
from ifcopenshell.api.group.data import Data
from ifcopenshell.util.selector import Selector
import json


class LoadGroups(bpy.types.Operator):
    bl_idname = "bim.load_groups"
    bl_label = "Load Groups"
    bl_options = {"REGISTER", "UNDO"}
    is_refresh: bpy.props.BoolProperty(default=False)

    def execute(self, context):
        self.props = context.scene.BIMGroupProperties
        self.expanded_groups = json.loads(context.scene.ExpandedGroups.json_string)
        self.props.groups.clear()
        self.ifc = IfcStore.get_file()
        if not self.is_refresh:
            context.scene.ExpandedGroups.json_string = "{}"

        for ifc_definition_id, group in Data.groups.items():
            if not group["HasAssignments"]:
                new = self.props.groups.add()
                new.ifc_definition_id = ifc_definition_id
                new.name = group["Name"]
                new.selection_query = group["Description"].split("*selector*")[1] if group["Description"] else ""
                new.tree_depth = 0

                if group["IsGroupedBy"]:
                    #  assumes 1:1 cardinality, will need to be updated to reflect IFC4 changes
                    # where the cardinality is 0:? - vulevukusej
                    sub_groups = [g for g in group["IsGroupedBy"][0].RelatedObjects if g.is_a("IfcGroup")]
                    new.has_children = True if len(sub_groups) != 0 else False

                if self.is_refresh:
                    self.recursively_load_sub_groups(ifc_definition_id, new)

        self.props.is_editing = True
        bpy.ops.bim.disable_editing_group()
        Data.load(IfcStore.get_file())
        return {"FINISHED"}

    def recursively_load_sub_groups(self, ifc_definition_id, parent):
        sub_groups = [
            k for k, v in Data.products.items() if self.ifc.by_id(k).is_a("IfcGroup") and ifc_definition_id in v
        ]
        if str(ifc_definition_id) not in self.expanded_groups or sub_groups == []:
            return
        else:
            parent.is_expanded = True
            parent.has_children = True
            for group in sub_groups:
                new = self.props.groups.add()
                new.ifc_definition_id = group
                new.name = Data.groups[group]["Name"]
                new.selection_query = (
                    Data.groups[group]["Description"].split("*selector*")[1]
                    if Data.groups[group]["Description"]
                    else ""
                )
                new.has_children = True if len(Data.groups[group]["IsGroupedBy"]) != 0 else False
                new.tree_depth = parent.tree_depth + 1
                self.recursively_load_sub_groups(new.ifc_definition_id, new)


class ToggleGroup(bpy.types.Operator):
    bl_idname = "bim.toggle_group"
    bl_label = "Toggle Group"
    bl_options = {"REGISTER", "UNDO"}
    ifc_definition_id: bpy.props.IntProperty()
    index: bpy.props.IntProperty()
    option: bpy.props.StringProperty(name="Expand or Collapse")

    def execute(self, context):
        context.scene.BIMGroupProperties.groups[self.index].is_expanded = True if self.option == "Expand" else False
        json_string = json.loads(context.scene.ExpandedGroups.json_string)
        if self.option == "Expand":
            json_string.setdefault(str(self.ifc_definition_id), None)
        else:
            json_string.pop(str(self.ifc_definition_id), None)
        context.scene.ExpandedGroups.json_string = json.dumps(json_string)
        bpy.ops.bim.load_groups(is_refresh=True)
        return {"FINISHED"}


class DisableGroupEditingUI(bpy.types.Operator):
    bl_idname = "bim.disable_group_editing_ui"
    bl_label = "Disable Group Editing UI"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        context.scene.BIMGroupProperties.is_editing = False
        context.scene.BIMGroupProperties.active_group_id = 0
        return {"FINISHED"}


class AddGroup(bpy.types.Operator):
    bl_idname = "bim.add_group"
    bl_label = "Add New Group"
    bl_options = {"REGISTER", "UNDO"}
    group: bpy.props.IntProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        result = ifcopenshell.api.run("group.add_group", tool.Ifc.get())
        if self.group:
            ifcopenshell.api.run(
                "group.assign_group", tool.Ifc.get(), products=[result], group=tool.Ifc.get().by_id(self.group)
            )
        Data.load(tool.Ifc.get())
        bpy.ops.bim.load_groups(is_refresh=True)
        return {"FINISHED"}


class EditGroup(bpy.types.Operator):
    bl_idname = "bim.edit_group"
    bl_label = "Edit Group"
    bl_options = {"REGISTER", "UNDO"}
    copy_from_selector: bpy.props.BoolProperty(name="Copy from Selector", default=False)

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

        if self.copy_from_selector:
            attributes["Description"] = context.scene.IFCSelector.selection_query

        self.file = IfcStore.get_file()
        ifcopenshell.api.run(
            "group.edit_group", self.file, **{"group": self.file.by_id(props.active_group_id), "attributes": attributes}
        )
        Data.load(IfcStore.get_file())
        bpy.ops.bim.load_groups(is_refresh=True)
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
        bpy.ops.bim.load_groups(is_refresh=True)
        return {"FINISHED"}


class EnableEditingGroup(bpy.types.Operator):
    bl_idname = "bim.enable_editing_group"
    bl_label = "Enable Editing Group"
    bl_options = {"REGISTER", "UNDO"}
    group: bpy.props.IntProperty()

    def execute(self, context):
        props = context.scene.BIMGroupProperties
        props.group_attributes.clear()
        blenderbim.bim.helper.import_attributes("IfcGroup", props.group_attributes, Data.groups[self.group])
        props.active_group_id = self.group
        return {"FINISHED"}


class DisableEditingGroup(bpy.types.Operator):
    bl_idname = "bim.disable_editing_group"
    bl_label = "Disable Editing Group"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        context.scene.BIMGroupProperties.active_group_id = 0
        return {"FINISHED"}


class ToggleAssigningGroup(bpy.types.Operator):
    bl_idname = "bim.toggle_assigning_group"
    bl_label = "Toggle Assigning Group"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        context.scene.BIMGroupProperties.is_adding = not context.scene.BIMGroupProperties.is_adding
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
        self.file = IfcStore.get_file()
        products = [bpy.data.objects.get(self.product)] if self.product else context.selected_objects
        for product in products:
            if not product.BIMObjectProperties.ifc_definition_id:
                continue
            ifcopenshell.api.run(
                "group.assign_group",
                self.file,
                products=[self.file.by_id(product.BIMObjectProperties.ifc_definition_id)],
                group=self.file.by_id(self.group),
            )
        Data.load(self.file)
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
        self.file = IfcStore.get_file()
        products = [bpy.data.objects.get(self.product)] if self.product else context.selected_objects
        for product in products:
            if not product.BIMObjectProperties.ifc_definition_id:
                continue
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


class UpdateGroup(bpy.types.Operator):
    bl_idname = "bim.update_group"
    bl_label = "Update Group"
    bl_options = {"REGISTER", "UNDO"}
    query: bpy.props.StringProperty()
    group_id: bpy.props.IntProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        self.file = IfcStore.get_file()
        group = self.file.by_id(self.group_id)
        query = self.query

        new_products = Selector.parse(self.file, query)
        ifcopenshell.api.run(
            "group.update_group_products",
            self.file,
            **{
                "group": group,
                "products": new_products,
            }
        )
        Data.load(IfcStore.get_file())
        bpy.ops.bim.load_groups(is_refresh=True)
        return {"FINISHED"}
