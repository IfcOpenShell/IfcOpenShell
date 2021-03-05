import bpy
import blenderbim.bim.module.group.add_group as add_group
import blenderbim.bim.module.group.edit_group as edit_group
import blenderbim.bim.module.group.remove_group as remove_group
from blenderbim.bim.ifc import IfcStore
from blenderbim.bim.module.group.data import Data


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
        result = add_group.Usecase(IfcStore.get_file()).execute()
        Data.load()
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
        edit_group.Usecase(
            self.file, {"group": self.file.by_id(props.active_group_id), "attributes": attributes}
        ).execute()
        Data.load()
        bpy.ops.bim.load_groups()
        return {"FINISHED"}


class RemoveGroup(bpy.types.Operator):
    bl_idname = "bim.remove_group"
    bl_label = "Remove Group"
    group: bpy.props.IntProperty()

    def execute(self, context):
        props = context.scene.BIMGroupProperties
        self.file = IfcStore.get_file()
        remove_group.Usecase(self.file, {"group": self.file.by_id(self.group)}).execute()
        Data.load()
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
            data_type = str(attribute.type_of_attribute)
            if "<entity" in data_type:
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
