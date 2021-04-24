import bpy
import json
import ifcopenshell.api
from blenderbim.bim.ifc import IfcStore
from ifcopenshell.api.resource.data import Data


class LoadResources(bpy.types.Operator):
    bl_idname = "bim.load_resources"
    bl_label = "Load Work Plans"

    def execute(self, context):
        props = context.scene.BIMResourceProperties
        while len(props.resources) > 0:
            props.resources.remove(0)
        for ifc_definition_id, resource in Data.resources.items():
            new = props.resources.add()
            new.ifc_definition_id = ifc_definition_id
            new.name = resource["Name"] or "Unnamed"
        props.is_loaded = True
        bpy.ops.bim.disable_editing_resource()
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
        self.props.is_editing = "RESOURCE"
        return {"FINISHED"}

    def enable_editing_resource(self):
        data = Data.resources[self.resource]
        for attribute in IfcStore.get_schema().declaration_by_name("IfcCrewResource").all_attributes():
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


class EnableEditingNestedResource(bpy.types.Operator):
    bl_idname = "bim.enable_editing_nested_resources"
    bl_label = "Enable Editing Nested Resource"
    resource: bpy.props.IntProperty()

    def execute(self, context):
        self.props = context.scene.BIMResourceProperties
        self.tprops = context.scene.BIMResourceTreeProperties
        self.props.active_resource_id = self.resource
        while len(self.tprops.nested_resources) > 0:
            self.tprops.nested_resources.remove(0)

        self.contracted_nested_resources = json.loads(self.props.contracted_nested_resources)
        for related_object_id in Data.resources[self.resource]["RelatedObjects"]:
            self.create_new_nested_resource_li(related_object_id, 0)
        bpy.ops.bim.load_nested_resource_properties()
        self.props.is_editing = "NESTED_RESOURCE"
        return {"FINISHED"}

    def create_new_nested_resource_li(self, related_object_id, level_index):
        nested_resource = Data.nested_resources[related_object_id]
        new = self.tprops.nested_resources.add()
        new.ifc_definition_id = related_object_id
        new.is_expanded = related_object_id not in self.contracted_nested_resources
        new.level_index = level_index
        if nested_resource["RelatedObjects"]:
            new.has_children = True
            if new.is_expanded:
                for related_object_id in nested_resource["RelatedObjects"]:
                    self.create_new_nested_resource_li(related_object_id, level_index + 1)
        return {"FINISHED"}


class LoadNestedResourceProperties(bpy.types.Operator):
    bl_idname = "bim.load_nested_resource_properties"
    bl_label = "Load nested_resource Properties"
    nested_resource: bpy.props.IntProperty()

    def execute(self, context):
        self.props = context.scene.BIMResourceProperties
        self.tprops = context.scene.BIMResourceTreeProperties
        self.props.is_nested_resource_update_enabled = False
        for item in self.tprops.nested_resources:
            if self.nested_resource and item.ifc_definition_id != self.nested_resource:
                continue
            nested_resource = Data.nested_resources[item.ifc_definition_id]
            item.name = nested_resource["Name"] or "Unnamed"
        self.props.is_nested_resource_update_enabled = True
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
        context.scene.BIMResourceProperties.is_loaded = False
        return {"FINISHED"}


class AddSubcontractResource(bpy.types.Operator):
    bl_idname = "bim.add_subcontract_resource"
    bl_label = "Add Subcontract Resource"
    resource: bpy.props.IntProperty()

    def execute(self, context):
        if self.resource:
            ifcopenshell.api.run(
            "resource.add_subcontract_resource",
            IfcStore.get_file(),
            resource=IfcStore.get_file().by_id(self.resource)
            )
        else:
            ifcopenshell.api.run("resource.add_subcontract_resource", IfcStore.get_file())
        Data.load(IfcStore.get_file())
        return {"FINISHED"}


class AddCrewResource(bpy.types.Operator):
    bl_idname = "bim.add_crew_resource"
    bl_label = "Add Crew Resource"
    resource: bpy.props.IntProperty()

    def execute(self, context):
        if self.resource:
            ifcopenshell.api.run(
            "resource.add_crew_resource",
            IfcStore.get_file(),
            resource=IfcStore.get_file().by_id(self.resource)
            )
        else:
            ifcopenshell.api.run("resource.add_crew_resource", IfcStore.get_file())
        Data.load(IfcStore.get_file())
        return {"FINISHED"}


class AddEquipementResource(bpy.types.Operator):
    bl_idname = "bim.add_equipment_resource"
    bl_label = "Add Equipement Resource"
    resource: bpy.props.IntProperty()

    def execute(self, context):
        ifcopenshell.api.run(
        "resource.add_equipment_resource",
        IfcStore.get_file(),
        resource=IfcStore.get_file().by_id(self.resource)
        )
        Data.load(IfcStore.get_file())
        return {"FINISHED"}

class AddLaborResource(bpy.types.Operator):
    bl_idname = "bim.add_labor_resource"
    bl_label = "Add Labor Resource"
    resource: bpy.props.IntProperty()

    def execute(self, context):
        ifcopenshell.api.run(
        "resource.add_labor_resource",
        IfcStore.get_file(),
        resource=IfcStore.get_file().by_id(self.resource)
        )
        Data.load(IfcStore.get_file())
        return {"FINISHED"}


class AddMaterialResource(bpy.types.Operator):
    bl_idname = "bim.add_material_resource"
    bl_label = "Add Material Resource"
    resource: bpy.props.IntProperty()

    def execute(self, context):
        ifcopenshell.api.run(
        "resource.add_material_resource",
        IfcStore.get_file(),
        resource=IfcStore.get_file().by_id(self.resource)
        )
        Data.load(IfcStore.get_file())
        return {"FINISHED"}

class AddProductResource(bpy.types.Operator):
    bl_idname = "bim.add_product_resource"
    bl_label = "Add Product Resource"
    resource: bpy.props.IntProperty()

    def execute(self, context):
        ifcopenshell.api.run(
        "resource.add_product_resource",
        IfcStore.get_file(),
        resource=IfcStore.get_file().by_id(self.resource)
        )
        Data.load(IfcStore.get_file())
        return {"FINISHED"}

class EditResource(bpy.types.Operator):
    bl_idname = "bim.edit_resource"
    bl_label = "Edit Resource"

    def execute(self, context):
        props = context.scene.BIMResourceProperties
        attributes = {}
        for attribute in props.nested_resource_attributes:
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
        return {"FINISHED"}
