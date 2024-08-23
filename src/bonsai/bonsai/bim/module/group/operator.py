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
import ifcopenshell.util.attribute
import ifcopenshell.api
import bonsai.bim.helper
import bonsai.tool as tool
from bonsai.bim.ifc import IfcStore
import json


class LoadGroups(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.load_groups"
    bl_label = "Load Groups"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        self.props = context.scene.BIMGroupProperties
        self.expanded_groups = json.loads(context.scene.ExpandedGroups.json_string)
        self.props.groups.clear()

        for group in tool.Ifc.get().by_type("IfcGroup", include_subtypes=False):
            if not group.HasAssignments:
                self.load_group(group)

        self.props.is_editing = True
        bpy.ops.bim.disable_editing_group()
        return {"FINISHED"}

    def load_group(self, group, tree_depth=0):
        new = self.props.groups.add()
        new.ifc_definition_id = group.id()
        new.name = group.Name or "Unnamed"
        new.tree_depth = tree_depth
        new.has_children = False
        new.is_expanded = group.id() in self.expanded_groups

        for rel in group.IsGroupedBy or []:
            for related_object in rel.RelatedObjects:
                if not related_object.is_a("IfcGroup"):
                    continue
                new.has_children = True
                if not new.is_expanded:
                    return
                self.load_group(related_object, tree_depth=tree_depth + 1)


class ToggleGroup(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.toggle_group"
    bl_label = "Toggle Group"
    bl_options = {"REGISTER", "UNDO"}
    ifc_definition_id: bpy.props.IntProperty()
    index: bpy.props.IntProperty()
    option: bpy.props.StringProperty(name="Expand or Collapse")

    def _execute(self, context):
        expanded_groups = set(json.loads(context.scene.ExpandedGroups.json_string))
        if self.option == "Expand":
            expanded_groups.add(self.ifc_definition_id)
        elif self.ifc_definition_id in expanded_groups:
            expanded_groups.remove(self.ifc_definition_id)
        context.scene.ExpandedGroups.json_string = json.dumps(list(expanded_groups))
        bpy.ops.bim.load_groups()
        return {"FINISHED"}


class DisableGroupEditingUI(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.disable_group_editing_ui"
    bl_label = "Disable Group Editing UI"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        context.scene.BIMGroupProperties.is_editing = False
        context.scene.BIMGroupProperties.active_group_id = 0
        return {"FINISHED"}


class AddGroup(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_group"
    bl_label = "Add New Group"
    bl_options = {"REGISTER", "UNDO"}
    group: bpy.props.IntProperty()

    def _execute(self, context):
        result = ifcopenshell.api.run("group.add_group", tool.Ifc.get())
        if self.group:
            ifcopenshell.api.run(
                "group.assign_group", tool.Ifc.get(), products=[result], group=tool.Ifc.get().by_id(self.group)
            )
        bpy.ops.bim.load_groups()
        return {"FINISHED"}


class EditGroup(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.edit_group"
    bl_label = "Edit Group"
    bl_options = {"REGISTER", "UNDO"}

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
        bpy.ops.bim.load_groups()
        return {"FINISHED"}


class RemoveGroup(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.remove_group"
    bl_label = "Remove Group"
    bl_options = {"REGISTER", "UNDO"}
    group: bpy.props.IntProperty()

    def _execute(self, context):
        props = context.scene.BIMGroupProperties
        self.file = IfcStore.get_file()
        ifcopenshell.api.run("group.remove_group", self.file, **{"group": self.file.by_id(self.group)})
        bpy.ops.bim.load_groups()
        return {"FINISHED"}


class EnableEditingGroup(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.enable_editing_group"
    bl_label = "Enable Editing Group"
    bl_options = {"REGISTER", "UNDO"}
    group: bpy.props.IntProperty()

    def _execute(self, context):
        props = context.scene.BIMGroupProperties
        props.group_attributes.clear()
        bonsai.bim.helper.import_attributes2(tool.Ifc.get().by_id(self.group), props.group_attributes)
        props.active_group_id = self.group
        return {"FINISHED"}


class DisableEditingGroup(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.disable_editing_group"
    bl_label = "Disable Editing Group"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        context.scene.BIMGroupProperties.active_group_id = 0
        return {"FINISHED"}


class AssignGroup(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.assign_group"
    bl_label = "Assign Group"
    bl_options = {"REGISTER", "UNDO"}
    product: bpy.props.StringProperty()
    group: bpy.props.IntProperty()

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
        return {"FINISHED"}


class UnassignGroup(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.unassign_group"
    bl_label = "Unassign Group"
    bl_options = {"REGISTER", "UNDO"}
    product: bpy.props.StringProperty()
    group: bpy.props.IntProperty()

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
                    "products": [self.file.by_id(product.BIMObjectProperties.ifc_definition_id)],
                    "group": self.file.by_id(self.group),
                }
            )
        return {"FINISHED"}


class SelectGroupProducts(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.select_group_products"
    bl_label = "Select Group Products"
    bl_options = {"REGISTER", "UNDO"}
    group: bpy.props.IntProperty()

    def _execute(self, context):
        self.file = IfcStore.get_file()
        for obj in context.visible_objects:
            obj.select_set(False)
            element = tool.Ifc.get_entity(obj)
            if not element:
                continue
            product_groups = [
                r.RelatingGroup.id()
                for r in getattr(element, "HasAssignments", []) or []
                if r.is_a("IfcRelAssignsToGroup")
            ]
            if self.group in product_groups:
                obj.select_set(True)
        return {"FINISHED"}


class SelectGroupElements(bpy.types.Operator):
    bl_idname = "bim.select_group_elements"
    bl_label = "Select Group elements"
    bl_options = {"REGISTER", "UNDO"}
    group: bpy.props.IntProperty()

    @classmethod
    def poll(cls, context):
        return bool(tool.Ifc.get() and context.active_object)

    def execute(self, context):
        elements = tool.Drawing.get_group_elements(tool.Ifc.get().by_id(self.group))
        tool.Spatial.select_products(elements)
        return {"FINISHED"}
