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
        props.is_editing = True
        bpy.ops.bim.disable_editing_resource()
        return {"FINISHED"}

class EnableEditingResource(bpy.types.Operator):
    bl_idname = "bim.enable_editing_resource"
    bl_label = "Enable Editing Resource"
    resource: bpy.props.IntProperty()

    def execute(self, context):
        props = context.scene.BIMResourceProperties
        while len(props.resource_attributes) > 0:
            props.resource_attributes.remove(0)

        data = Data.resources[self.resource]
        for attribute in IfcStore.get_schema().declaration_by_name("IfcConstructionResource").all_attributes():
            data_type = ifcopenshell.util.attribute.get_primitive_type(attribute)
            if data_type == "entity":
                continue
            new = props.resource_attributes.add()
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
        props.active_resource_id = self.resource
        return {"FINISHED"}

class DisableEditingResource(bpy.types.Operator):
    bl_idname = "bim.disable_editing_resource"
    bl_label = "Disable Editing Workplan"

    def execute(self, context):
        context.scene.BIMWorkPlanProperties.active_resource_id = 0
        return {"FINISHED"}

class DisableResourceEditingUI(bpy.types.Operator):
    bl_idname = "bim.disable_resource_editing_ui"
    bl_label = "Disable Resources Editing UI"

    def execute(self, context):
        context.scene.BIMResourceProperties.is_editing = False
        return {"FINISHED"}


class AddSubcontractResource(bpy.types.Operator):
    bl_idname = "bim.add_subcontract_resource"
    bl_label = "Add Subcontract Resource"

    def execute(self, context):
        ifcopenshell.api.run("resource.add_subcontract_resource", IfcStore.get_file())
        Data.load(IfcStore.get_file())
        return {"FINISHED"}


class AddCrewResource(bpy.types.Operator):
    bl_idname = "bim.add_crew_resource"
    bl_label = "Add Crew Resource"

    def execute(self, context):
        ifcopenshell.api.run("resource.add_crew_resource", IfcStore.get_file())
        Data.load(IfcStore.get_file())
        return {"FINISHED"}


class EditResource(bpy.types.Operator):
    bl_idname = "bim.edit_resource"
    bl_label = "Edit Resource"

    def execute(self, context):
        props = context.scene.BIMResourceProperties
        attributes = {}
        for attribute in props.cost_resource_attributes:
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
