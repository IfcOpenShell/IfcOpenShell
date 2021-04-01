import bpy
import ifcopenshell.util.attribute
import ifcopenshell.api
from blenderbim.bim.ifc import IfcStore
from ifcopenshell.api.group.data import Data


class LoadGroups(bpy.types.Operator):
    bl_idname = "bim.load_groups"
    bl_label = "Load Groups"

    def execute(self, context):
        props = context.scene.BIMGroupProperties
        while len(props.groups) > 0:
            props.groups.remove(0)
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

    def execute(self, context):
        context.scene.BIMGroupProperties.is_editing = False
        return {"FINISHED"}


class AddGroup(bpy.types.Operator):
    bl_idname = "bim.add_group"
    bl_label = "Add Group"

    def execute(self, context):
        result = ifcopenshell.api.run("group.add_group", IfcStore.get_file())
        Data.load(IfcStore.get_file())
        bpy.ops.bim.load_groups()
        bpy.ops.bim.enable_editing_group(group=result.id())
        return {"FINISHED"}


class EditGroup(bpy.types.Operator):
    bl_idname = "bim.edit_group"
    bl_label = "Edit Group"

    def execute(self, context):
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
    group: bpy.props.IntProperty()

    def execute(self, context):
        props = context.scene.BIMGroupProperties
        self.file = IfcStore.get_file()
        ifcopenshell.api.run("group.remove_group", self.file, **{"group": self.file.by_id(self.group)})
        Data.load(IfcStore.get_file())
        bpy.ops.bim.load_groups()
        return {"FINISHED"}


class EnableEditingGroup(bpy.types.Operator):
    bl_idname = "bim.enable_editing_group"
    bl_label = "Enable Editing Group"
    group: bpy.props.IntProperty()

    def execute(self, context):
        props = context.scene.BIMGroupProperties
        while len(props.group_attributes) > 0:
            props.group_attributes.remove(0)

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

    def execute(self, context):
        context.scene.BIMGroupProperties.active_group_id = 0
        return {"FINISHED"}


class AssignGroup(bpy.types.Operator):
    bl_idname = "bim.assign_group"
    bl_label = "Assign Group"
    product: bpy.props.StringProperty()
    group: bpy.props.IntProperty()

    def execute(self, context):
        product = bpy.data.objects.get(self.product) if self.product else context.active_object
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


class UnassignGroup(bpy.types.Operator):
    bl_idname = "bim.unassign_group"
    bl_label = "Unassign Group"
    product: bpy.props.StringProperty()
    group: bpy.props.IntProperty()

    def execute(self, context):
        product = bpy.data.objects.get(self.product) if self.product else context.active_object
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
