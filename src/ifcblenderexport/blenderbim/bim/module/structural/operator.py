import bpy
import json
import blenderbim.bim.module.structural.add_structural_boundary_condition as add_structural_boundary_condition
import blenderbim.bim.module.structural.edit_structural_boundary_condition as edit_structural_boundary_condition
import blenderbim.bim.module.structural.remove_structural_boundary_condition as remove_structural_boundary_condition
import blenderbim.bim.module.structural.add_structural_analysis_model as add_structural_analysis_model
import blenderbim.bim.module.structural.edit_structural_analysis_model as edit_structural_analysis_model
import blenderbim.bim.module.structural.remove_structural_analysis_model as remove_structural_analysis_model
import blenderbim.bim.module.structural.assign_structural_analysis_model as assign_structural_analysis_model
import blenderbim.bim.module.structural.unassign_structural_analysis_model as unassign_structural_analysis_model
from blenderbim.bim.ifc import IfcStore
from blenderbim.bim.module.structural.data import Data


class AddStructuralBoundaryCondition(bpy.types.Operator):
    bl_idname = "bim.add_structural_boundary_condition"
    bl_label = "Add Structural Boundary Condition"

    def execute(self, context):
        obj = context.active_object
        file = IfcStore.get_file()
        connection = file.by_id(obj.BIMObjectProperties.ifc_definition_id)
        add_structural_boundary_condition.Usecase(file, {"connection": connection}).execute()
        Data.load(connection.id())
        return {"FINISHED"}


class RemoveStructuralBoundaryCondition(bpy.types.Operator):
    bl_idname = "bim.remove_structural_boundary_condition"
    bl_label = "Enable Editing Structural Boundary Condition"

    def execute(self, context):
        obj = context.active_object
        file = IfcStore.get_file()
        connection = file.by_id(obj.BIMObjectProperties.ifc_definition_id)
        remove_structural_boundary_condition.Usecase(file, {"connection": connection}).execute()
        Data.load(connection.id())
        return {"FINISHED"}


class EnableEditingStructuralBoundaryCondition(bpy.types.Operator):
    bl_idname = "bim.enable_editing_structural_boundary_condition"
    bl_label = "Enable Editing Structural Boundary Condition"

    def execute(self, context):
        obj = context.active_object
        oprops = obj.BIMObjectProperties
        props = obj.BIMStructuralProperties
        while len(props.boundary_condition_attributes) > 0:
            props.boundary_condition_attributes.remove(0)

        data = Data.boundary_conditions[oprops.ifc_definition_id]

        for attribute in IfcStore.get_schema().declaration_by_name(data["type"]).all_attributes():
            value = data[attribute.name()]
            data_type = ifcopenshell.util.attribute.get_primitive_type(attribute)
            new = props.boundary_condition_attributes.add()
            new.name = attribute.name()
            new.is_null = value is None
            new.is_optional = attribute.optional()
            if data_type == "select":
                enum_items = [s.name() for s in ifcopenshell.get_select_items(attribute)]
                new.enum_items = json.dumps(enum_items)
            if isinstance(value, bool):
                new.bool_value = False if new.is_null else data[attribute.name()]
                new.data_type = "bool"
                new.enum_value = "IfcBoolean"
            elif isinstance(value, float):
                new.float_value = 0.0 if new.is_null else data[attribute.name()]
                new.data_type = "float"
                new.enum_value = [i for i in enum_items if i != "IfcBoolean"][0]
            elif data_type == "string":
                new.string_value = "" if new.is_null else data[attribute.name()]

        props.is_editing_boundary_condition = True
        return {"FINISHED"}


class EditStructuralBoundaryCondition(bpy.types.Operator):
    bl_idname = "bim.edit_structural_boundary_condition"
    bl_label = "Edit Structural Boundary Condition"

    def execute(self, context):
        obj = context.active_object
        oprops = obj.BIMObjectProperties
        props = obj.BIMStructuralProperties

        file = IfcStore.get_file()
        connection = file.by_id(obj.BIMObjectProperties.ifc_definition_id)
        condition = connection.AppliedCondition

        attributes = {}
        for attribute in props.boundary_condition_attributes:
            if attribute.is_null:
                attributes[attribute.name] = {"value": None, "type": "null"}
            elif attribute.data_type == "string":
                attributes[attribute.name] = {"value": attribute.string_value, "type": "string"}
            elif attribute.enum_value == "IfcBoolean":
                attributes[attribute.name] = {"value": attribute.bool_value, "type": attribute.enum_value}
            else:
                attributes[attribute.name] = {"value": attribute.float_value, "type": attribute.enum_value}

        edit_structural_boundary_condition.Usecase(file, {"condition": condition, "attributes": attributes}).execute()
        Data.load(connection.id())
        bpy.ops.bim.disable_editing_structural_boundary_condition()
        return {"FINISHED"}


class DisableEditingStructuralBoundaryCondition(bpy.types.Operator):
    bl_idname = "bim.disable_editing_structural_boundary_condition"
    bl_label = "Disable Editing Structural Boundary Condition"

    def execute(self, context):
        context.active_object.BIMStructuralProperties.is_editing_boundary_condition = False
        return {"FINISHED"}


class LoadStructuralAnalysisModels(bpy.types.Operator):
    bl_idname = "bim.load_structural_analysis_models"
    bl_label = "Load Structural Analysis Models"

    def execute(self, context):
        props = context.scene.BIMStructuralProperties
        while len(props.structural_analysis_models) > 0:
            props.structural_analysis_models.remove(0)
        for ifc_definition_id, structural_analysis_model in Data.structural_analysis_models.items():
            new = props.structural_analysis_models.add()
            new.ifc_definition_id = ifc_definition_id
            new.name = structural_analysis_model["Name"]
        props.is_editing = True
        bpy.ops.bim.disable_editing_structural_analysis_model()
        return {"FINISHED"}


class DisableStructuralAnalysisModelEditingUI(bpy.types.Operator):
    bl_idname = "bim.disable_structural_analysis_model_editing_ui"
    bl_label = "Disable Structural Analysis Model Editing UI"

    def execute(self, context):
        context.scene.BIMStructuralProperties.is_editing = False
        return {"FINISHED"}


class AddStructuralAnalysisModel(bpy.types.Operator):
    bl_idname = "bim.add_structural_analysis_model"
    bl_label = "Add Structural Analysis Model"

    def execute(self, context):
        result = add_structural_analysis_model.Usecase(IfcStore.get_file()).execute()
        Data.load()
        bpy.ops.bim.load_structural_analysis_models()
        bpy.ops.bim.enable_editing_structural_analysis_model(structural_analysis_model=result.id())
        return {"FINISHED"}


class EditStructuralAnalysisModel(bpy.types.Operator):
    bl_idname = "bim.edit_structural_analysis_model"
    bl_label = "Edit Structural Analysis Model"

    def execute(self, context):
        props = context.scene.BIMStructuralProperties
        attributes = {}
        for attribute in props.structural_analysis_model_attributes:
            if attribute.is_null:
                attributes[attribute.name] = None
            else:
                if attribute.data_type == "string":
                    attributes[attribute.name] = attribute.string_value
                elif attribute.data_type == "enum":
                    attributes[attribute.name] = attribute.enum_value
        self.file = IfcStore.get_file()
        edit_structural_analysis_model.Usecase(
            self.file, {"structural_analysis_model": self.file.by_id(props.active_structural_analysis_model_id), "attributes": attributes}
        ).execute()
        Data.load()
        bpy.ops.bim.load_structural_analysis_models()
        return {"FINISHED"}


class RemoveStructuralAnalysisModel(bpy.types.Operator):
    bl_idname = "bim.remove_structural_analysis_model"
    bl_label = "Remove Structural Analysis Model"
    structural_analysis_model: bpy.props.IntProperty()

    def execute(self, context):
        props = context.scene.BIMStructuralProperties
        self.file = IfcStore.get_file()
        remove_structural_analysis_model.Usecase(self.file, {"structural_analysis_model": self.file.by_id(self.structural_analysis_model)}).execute()
        Data.load()
        bpy.ops.bim.load_structural_analysis_models()
        return {"FINISHED"}


class EnableEditingStructuralAnalysisModel(bpy.types.Operator):
    bl_idname = "bim.enable_editing_structural_analysis_model"
    bl_label = "Enable Editing Structural Analysis Model"
    structural_analysis_model: bpy.props.IntProperty()

    def execute(self, context):
        props = context.scene.BIMStructuralProperties
        while len(props.structural_analysis_model_attributes) > 0:
            props.structural_analysis_model_attributes.remove(0)

        data = Data.structural_analysis_models[self.structural_analysis_model]

        for attribute in IfcStore.get_schema().declaration_by_name("IfcStructuralAnalysisModel").all_attributes():
            data_type = str(attribute.type_of_attribute)
            if "<entity" in data_type:
                continue
            new = props.structural_analysis_model_attributes.add()
            new.name = attribute.name()
            new.is_null = data[attribute.name()] is None
            new.is_optional = attribute.optional()
            if attribute.name() == "PredefinedType":
                new.enum_items = json.dumps(attribute.type_of_attribute().declared_type().enumeration_items())
                new.data_type = "enum"
                if data[attribute.name()]:
                    new.enum_value = data[attribute.name()]
            else:
                new.string_value = "" if new.is_null else data[attribute.name()]
                new.data_type = "string"
        props.active_structural_analysis_model_id = self.structural_analysis_model
        return {"FINISHED"}


class DisableEditingStructuralAnalysisModel(bpy.types.Operator):
    bl_idname = "bim.disable_editing_structural_analysis_model"
    bl_label = "Disable Editing Structural Analysis Model"

    def execute(self, context):
        context.scene.BIMStructuralProperties.active_structural_analysis_model_id = 0
        return {"FINISHED"}


class AssignStructuralAnalysisModel(bpy.types.Operator):
    bl_idname = "bim.assign_structural_analysis_model"
    bl_label = "Assign Structural Analysis Model"
    product: bpy.props.StringProperty()
    structural_analysis_model: bpy.props.IntProperty()

    def execute(self, context):
        product = bpy.data.objects.get(self.product) if self.product else context.active_object
        self.file = IfcStore.get_file()
        assign_structural_analysis_model.Usecase(self.file, {
            "product": self.file.by_id(product.BIMObjectProperties.ifc_definition_id),
            "structural_analysis_model": self.file.by_id(self.structural_analysis_model)
        }).execute()
        Data.load()
        return {"FINISHED"}


class UnassignStructuralAnalysisModel(bpy.types.Operator):
    bl_idname = "bim.unassign_structural_analysis_model"
    bl_label = "Unassign Structural Analysis Model"
    product: bpy.props.StringProperty()
    structural_analysis_model: bpy.props.IntProperty()

    def execute(self, context):
        product = bpy.data.objects.get(self.product) if self.product else context.active_object
        self.file = IfcStore.get_file()
        unassign_structural_analysis_model.Usecase(self.file, {
            "product": self.file.by_id(product.BIMObjectProperties.ifc_definition_id),
            "structural_analysis_model": self.file.by_id(self.structural_analysis_model)
        }).execute()
        Data.load()
        return {"FINISHED"}
