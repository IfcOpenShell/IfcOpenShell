import bpy
import json
import ifcopenshell.api
from blenderbim.bim.ifc import IfcStore
from ifcopenshell.api.resource.data import Data


class LoadResources(bpy.types.Operator):
    bl_idname = "bim.load_resources"
    bl_label = "Load Resources"

    def execute(self, context):
        self.props = context.scene.BIMResourceProperties
        self.tprops = context.scene.BIMResourceTreeProperties
        while len(self.tprops.resources) > 0:
            self.tprops.resources.remove(0)

        self.contracted_resources = json.loads(self.props.contracted_resources)
        for resource_id, data in Data.resources.items():
            if not data["HasContext"]:
                continue
            self.create_new_resource_li(resource_id, 0)
        bpy.ops.bim.load_resource_properties()
        self.props.is_editing = True
        return {"FINISHED"}

    def create_new_resource_li(self, related_object_id, level_index):
        resource = Data.resources[related_object_id]
        new = self.tprops.resources.add()
        new.ifc_definition_id = related_object_id
        new.is_expanded = related_object_id not in self.contracted_resources
        new.level_index = level_index
        if resource["IsNestedBy"]:
            new.has_children = True
            if new.is_expanded:
                for related_object_id in resource["IsNestedBy"]:
                    self.create_new_resource_li(related_object_id, level_index + 1)
        return {"FINISHED"}


class EnableEditingResource(bpy.types.Operator):
    bl_idname = "bim.enable_editing_resource"
    bl_label = "Enable Editing Resource"
    resource: bpy.props.IntProperty()

    def execute(self, context):
        self.props = context.scene.BIMResourceProperties
        self.props.active_resource_id = self.resource
        while len(self.props.resource_attributes) > 0:
            self.props.resource_attributes.remove(0)
        self.enable_editing_resource()
        return {"FINISHED"}

    def enable_editing_resource(self):
        data = Data.resources[self.resource]
        for attribute in IfcStore.get_schema().declaration_by_name(data["type"]).all_attributes():
            data_type = ifcopenshell.util.attribute.get_primitive_type(attribute)
            if data_type == "entity" or isinstance(data_type, tuple):
                continue
            new = self.props.resource_attributes.add()
            new.name = attribute.name()
            new.is_null = data[attribute.name()] is None
            new.is_optional = attribute.optional()
            new.data_type = data_type
            if data_type == "string":
                new.string_value = "" if new.is_null else data[attribute.name()]
            elif data_type == "enum":
                new.enum_items = json.dumps(ifcopenshell.util.attribute.get_enum_items(attribute))
                if data[attribute.name()]:
                    new.enum_value = data[attribute.name()]


class LoadResourceProperties(bpy.types.Operator):
    bl_idname = "bim.load_resource_properties"
    bl_label = "Load Resource Properties"
    resource: bpy.props.IntProperty()

    def execute(self, context):
        self.props = context.scene.BIMResourceProperties
        self.tprops = context.scene.BIMResourceTreeProperties
        self.props.is_resource_update_enabled = False
        for item in self.tprops.resources:
            if self.resource and item.ifc_definition_id != self.resource:
                continue
            resource = Data.resources[item.ifc_definition_id]
            item.name = resource["Name"] or "Unnamed"
        self.props.is_resource_update_enabled = True
        return {"FINISHED"}


class DisableEditingResource(bpy.types.Operator):
    bl_idname = "bim.disable_editing_resource"
    bl_label = "Disable Editing Workplan"

    def execute(self, context):
        context.scene.BIMResourceProperties.active_resource_id = 0
        return {"FINISHED"}


class DisableResourceEditingUI(bpy.types.Operator):
    bl_idname = "bim.disable_resource_editing_ui"
    bl_label = "Disable Resources Editing UI"

    def execute(self, context):
        context.scene.BIMResourceProperties.is_editing = False
        return {"FINISHED"}


class AddResource(bpy.types.Operator):
    bl_idname = "bim.add_resource"
    bl_label = "Add resource"
    ifc_class: bpy.props.StringProperty()
    resource: bpy.props.IntProperty()

    def execute(self, context):
        ifcopenshell.api.run(
            "resource.add_resource",
            IfcStore.get_file(),
            parent_resource=IfcStore.get_file().by_id(self.resource) if self.resource else None,
            ifc_class=self.ifc_class,
        )
        Data.load(IfcStore.get_file())
        bpy.ops.bim.load_resources()
        return {"FINISHED"}


class EditResource(bpy.types.Operator):
    bl_idname = "bim.edit_resource"
    bl_label = "Edit Resource"

    def execute(self, context):
        props = context.scene.BIMResourceProperties
        attributes = {}
        for attribute in props.resource_attributes:
            if attribute.is_null:
                attributes[attribute.name] = None
            else:
                if attribute.data_type == "string":
                    attributes[attribute.name] = attribute.string_value
                elif attribute.data_type == "enum":
                    attributes[attribute.name] = attribute.enum_value
        self.file = IfcStore.get_file()
        ifcopenshell.api.run(
            "resource.edit_resource",
            self.file,
            **{"resource": self.file.by_id(props.active_resource_id), "attributes": attributes},
        )
        Data.load(IfcStore.get_file())
        bpy.ops.bim.load_resource_properties(resource=props.active_resource_id)
        bpy.ops.bim.disable_editing_resource()
        return {"FINISHED"}


class RemoveResource(bpy.types.Operator):
    bl_idname = "bim.remove_resource"
    bl_label = "Remove Resource"
    resource: bpy.props.IntProperty()

    def execute(self, context):
        ifcopenshell.api.run(
            "resource.remove_resource",
            IfcStore.get_file(),
            resource=IfcStore.get_file().by_id(self.resource),
        )
        Data.load(IfcStore.get_file())
        bpy.ops.bim.load_resources()
        return {"FINISHED"}


class ExpandResource(bpy.types.Operator):
    bl_idname = "bim.expand_resource"
    bl_label = "Expand Resource"
    resource: bpy.props.IntProperty()

    def execute(self, context):
        props = context.scene.BIMResourceProperties
        self.file = IfcStore.get_file()
        contracted_resources = json.loads(props.contracted_resources)
        contracted_resources.remove(self.resource)
        props.contracted_resources = json.dumps(contracted_resources)
        Data.load(self.file)
        bpy.ops.bim.load_resources()
        return {"FINISHED"}


class ContractResource(bpy.types.Operator):
    bl_idname = "bim.contract_resource"
    bl_label = "Contract Resource"
    resource: bpy.props.IntProperty()

    def execute(self, context):
        props = context.scene.BIMResourceProperties
        self.file = IfcStore.get_file()
        contracted_resources = json.loads(props.contracted_resources)
        contracted_resources.append(self.resource)
        props.contracted_resources = json.dumps(contracted_resources)
        Data.load(self.file)
        bpy.ops.bim.load_resources()
        return {"FINISHED"}


class AssignResource(bpy.types.Operator):
    bl_idname = "bim.assign_resource"
    bl_label = "Assign Resource"
    resource: bpy.props.IntProperty()
    related_object: bpy.props.StringProperty()

    def execute(self, context):
        related_objects = (
            [bpy.data.objects.get(self.related_object)] if self.related_object else bpy.context.selected_objects
        )
        for related_object in related_objects:
            self.file = IfcStore.get_file()
            ifcopenshell.api.run(
                "resource.assign_resource",
                self.file,
                relating_resource=self.file.by_id(self.resource),
                related_object=self.file.by_id(related_object.BIMObjectProperties.ifc_definition_id),
            )
        Data.load(self.file)
        return {"FINISHED"}


class UnassignResource(bpy.types.Operator):
    bl_idname = "bim.unassign_resource"
    bl_label = "Unassign Resource"
    resource: bpy.props.IntProperty()
    related_object: bpy.props.StringProperty()

    def execute(self, context):
        related_objects = (
            [bpy.data.objects.get(self.related_object)] if self.related_object else bpy.context.selected_objects
        )
        for related_object in related_objects:
            self.file = IfcStore.get_file()
            ifcopenshell.api.run(
                "resource.unassign_resource",
                self.file,
                relating_resource=self.file.by_id(self.resource),
                related_object=self.file.by_id(related_object.BIMObjectProperties.ifc_definition_id),
            )
        Data.load(self.file)
        return {"FINISHED"}
