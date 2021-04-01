import bpy
import json
import ifcopenshell
import ifcopenshell.api
from blenderbim.bim.ifc import IfcStore
from ifcopenshell.api.structural.data import Data


class AddStructuralMemberConnection(bpy.types.Operator):
    bl_idname = "bim.add_structural_member_connection"
    bl_label = "Add Structural Member Connection"

    def execute(self, context):
        obj = bpy.context.active_object
        oprops = obj.BIMObjectProperties
        props = obj.BIMStructuralProperties
        file = IfcStore.get_file()
        related_structural_connection = file.by_id(oprops.ifc_definition_id)
        relating_structural_member = file.by_id(props.relating_structural_member.BIMObjectProperties.ifc_definition_id)
        if not relating_structural_member.is_a("IfcStructuralMember"):
            return {"FINISHED"}
        ifcopenshell.api.run(
            "structural.add_structural_member_connection",
            file,
            relating_structural_member=relating_structural_member,
            related_structural_connection=related_structural_connection,
        )
        props.relating_structural_member = None
        Data.load(IfcStore.get_file(), related_structural_connection.id())
        return {"FINISHED"}


class EnableEditingStructuralConnectionCondition(bpy.types.Operator):
    bl_idname = "bim.enable_editing_structural_connection_condition"
    bl_label = "Enable Editing Structural Connection Condition"
    connects_structural_member: bpy.props.IntProperty()

    def execute(self, context):
        obj = bpy.context.active_object
        oprops = obj.BIMObjectProperties
        props = obj.BIMStructuralProperties
        applied_condition_id = Data.connects_structural_members[self.connects_structural_member]["AppliedCondition"]
        props.active_connects_structural_member = self.connects_structural_member
        return {"FINISHED"}


class DisableEditingStructuralConnectionCondition(bpy.types.Operator):
    bl_idname = "bim.disable_editing_structural_connection_condition"
    bl_label = "Disable Editing Structural Connection Condition"

    def execute(self, context):
        obj = bpy.context.active_object
        props = obj.BIMStructuralProperties
        props.active_connects_structural_member = 0
        return {"FINISHED"}


class RemoveStructuralConnectionCondition(bpy.types.Operator):
    bl_idname = "bim.remove_structural_connection_condition"
    bl_label = "Remove Structural Connection Condition"
    connects_structural_member: bpy.props.IntProperty()

    def execute(self, context):
        file = IfcStore.get_file()
        relation = file.by_id(self.connects_structural_member)
        connection = relation.RelatedStructuralConnection
        ifcopenshell.api.run("structural.remove_structural_connection_condition", file, **{"relation": relation})

        Data.load(IfcStore.get_file(), connection.id())
        return {"FINISHED"}


class AddStructuralBoundaryCondition(bpy.types.Operator):
    bl_idname = "bim.add_structural_boundary_condition"
    bl_label = "Add Structural Boundary Condition"
    connection: bpy.props.IntProperty()

    def execute(self, context):
        file = IfcStore.get_file()
        connection = file.by_id(self.connection)
        ifcopenshell.api.run("structural.add_structural_boundary_condition", file, **{"connection": connection})
        if connection.is_a("IfcRelConnectsStructuralMember"):
            Data.load(IfcStore.get_file(), connection.RelatedStructuralConnection.id())
        else:
            Data.load(IfcStore.get_file(), connection.id())
        return {"FINISHED"}


class RemoveStructuralBoundaryCondition(bpy.types.Operator):
    bl_idname = "bim.remove_structural_boundary_condition"
    bl_label = "Remove Structural Boundary Condition"
    connection: bpy.props.IntProperty()

    def execute(self, context):
        file = IfcStore.get_file()
        connection = file.by_id(self.connection)
        ifcopenshell.api.run("structural.remove_structural_boundary_condition", file, **{"connection": connection})
        if connection.is_a("IfcRelConnectsStructuralMember"):
            Data.load(IfcStore.get_file(), connection.RelatedStructuralConnection.id())
        else:
            Data.load(IfcStore.get_file(), connection.id())
        return {"FINISHED"}


class EnableEditingStructuralBoundaryCondition(bpy.types.Operator):
    bl_idname = "bim.enable_editing_structural_boundary_condition"
    bl_label = "Enable Editing Structural Boundary Condition"
    boundary_condition: bpy.props.IntProperty()

    def execute(self, context):
        obj = context.active_object
        props = obj.BIMStructuralProperties
        while len(props.boundary_condition_attributes) > 0:
            props.boundary_condition_attributes.remove(0)

        data = Data.boundary_conditions[self.boundary_condition]

        for attribute in IfcStore.get_schema().declaration_by_name(data["type"]).all_attributes():
            value = data[attribute.name()]
            data_type = ifcopenshell.util.attribute.get_primitive_type(attribute)
            new = props.boundary_condition_attributes.add()
            new.name = attribute.name()
            new.is_null = value is None
            new.is_optional = attribute.optional()
            if data_type == "select":
                enum_items = [s.name() for s in ifcopenshell.util.attribute.get_select_items(attribute)]
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
                new.data_type = "string"

        props.active_boundary_condition = self.boundary_condition
        return {"FINISHED"}


class EditStructuralBoundaryCondition(bpy.types.Operator):
    bl_idname = "bim.edit_structural_boundary_condition"
    bl_label = "Edit Structural Boundary Condition"
    connection: bpy.props.IntProperty()

    def execute(self, context):
        obj = context.active_object
        props = obj.BIMStructuralProperties

        file = IfcStore.get_file()
        connection = file.by_id(self.connection)
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

        ifcopenshell.api.run(
            "structural.edit_structural_boundary_condition", file, **{"condition": condition, "attributes": attributes}
        )
        if connection.is_a("IfcRelConnectsStructuralMember"):
            Data.load(IfcStore.get_file(), connection.RelatedStructuralConnection.id())
        else:
            Data.load(IfcStore.get_file(), connection.id())
        bpy.ops.bim.disable_editing_structural_boundary_condition()
        return {"FINISHED"}


class DisableEditingStructuralBoundaryCondition(bpy.types.Operator):
    bl_idname = "bim.disable_editing_structural_boundary_condition"
    bl_label = "Disable Editing Structural Boundary Condition"

    def execute(self, context):
        context.active_object.BIMStructuralProperties.active_boundary_condition = 0
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
        result = ifcopenshell.api.run("structural.add_structural_analysis_model", IfcStore.get_file())
        Data.load(IfcStore.get_file())
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
        ifcopenshell.api.run(
            "structural.edit_structural_analysis_model",
            self.file,
            **{
                "structural_analysis_model": self.file.by_id(props.active_structural_analysis_model_id),
                "attributes": attributes,
            }
        )
        Data.load(IfcStore.get_file())
        bpy.ops.bim.load_structural_analysis_models()
        return {"FINISHED"}


class RemoveStructuralAnalysisModel(bpy.types.Operator):
    bl_idname = "bim.remove_structural_analysis_model"
    bl_label = "Remove Structural Analysis Model"
    structural_analysis_model: bpy.props.IntProperty()

    def execute(self, context):
        props = context.scene.BIMStructuralProperties
        self.file = IfcStore.get_file()
        ifcopenshell.api.run(
            "structural.remove_structural_analysis_model",
            self.file,
            **{"structural_analysis_model": self.file.by_id(self.structural_analysis_model)}
        )
        Data.load(IfcStore.get_file())
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
        ifcopenshell.api.run(
            "structural.assign_structural_analysis_model",
            self.file,
            **{
                "product": self.file.by_id(product.BIMObjectProperties.ifc_definition_id),
                "structural_analysis_model": self.file.by_id(self.structural_analysis_model),
            }
        )
        Data.load(IfcStore.get_file())
        return {"FINISHED"}


class UnassignStructuralAnalysisModel(bpy.types.Operator):
    bl_idname = "bim.unassign_structural_analysis_model"
    bl_label = "Unassign Structural Analysis Model"
    product: bpy.props.StringProperty()
    structural_analysis_model: bpy.props.IntProperty()

    def execute(self, context):
        product = bpy.data.objects.get(self.product) if self.product else context.active_object
        self.file = IfcStore.get_file()
        ifcopenshell.api.run(
            "structural.unassign_structural_analysis_model",
            self.file,
            **{
                "product": self.file.by_id(product.BIMObjectProperties.ifc_definition_id),
                "structural_analysis_model": self.file.by_id(self.structural_analysis_model),
            }
        )
        Data.load(IfcStore.get_file())
        return {"FINISHED"}
