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
import json
import ifcopenshell
import ifcopenshell.api
import blenderbim.bim.helper
import blenderbim.bim.handler
import blenderbim.core.structural as core
import blenderbim.tool as tool
import blenderbim.core.context
from math import degrees
from mathutils import Vector, Matrix
from blenderbim.bim.ifc import IfcStore
from blenderbim.bim.module.structural.prop import purge
from ifcopenshell.api.structural.data import Data
from ifcopenshell.api.context.data import Data as ContextData
from blenderbim.bim.module.structural.data import StructuralData


class Operator:
    def execute(self, context):
        IfcStore.execute_ifc_operator(self, context)
        blenderbim.bim.handler.refresh_ui_data()
        return {"FINISHED"}


class AddStructuralMemberConnection(bpy.types.Operator):
    bl_idname = "bim.add_structural_member_connection"
    bl_label = "Add Structural Member Connection"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        obj = context.active_object
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
    bl_options = {"REGISTER", "UNDO"}
    connects_structural_member: bpy.props.IntProperty()

    def execute(self, context):
        obj = context.active_object
        oprops = obj.BIMObjectProperties
        props = obj.BIMStructuralProperties
        applied_condition_id = Data.connects_structural_members[self.connects_structural_member]["AppliedCondition"]
        props.active_connects_structural_member = self.connects_structural_member
        return {"FINISHED"}


class DisableEditingStructuralConnectionCondition(bpy.types.Operator):
    bl_idname = "bim.disable_editing_structural_connection_condition"
    bl_label = "Disable Editing Structural Connection Condition"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        obj = context.active_object
        props = obj.BIMStructuralProperties
        props.active_connects_structural_member = 0
        return {"FINISHED"}


class RemoveStructuralConnectionCondition(bpy.types.Operator):
    bl_idname = "bim.remove_structural_connection_condition"
    bl_label = "Remove Structural Connection Condition"
    bl_options = {"REGISTER", "UNDO"}
    connects_structural_member: bpy.props.IntProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        file = IfcStore.get_file()
        relation = file.by_id(self.connects_structural_member)
        connection = relation.RelatedStructuralConnection
        ifcopenshell.api.run("structural.remove_structural_connection_condition", file, **{"relation": relation})

        Data.load(IfcStore.get_file(), connection.id())
        return {"FINISHED"}


class AddStructuralBoundaryCondition(bpy.types.Operator):
    bl_idname = "bim.add_structural_boundary_condition"
    bl_label = "Add Structural Boundary Condition"
    bl_options = {"REGISTER", "UNDO"}
    connection: bpy.props.IntProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
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
    bl_options = {"REGISTER", "UNDO"}
    connection: bpy.props.IntProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
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
    bl_options = {"REGISTER", "UNDO"}
    boundary_condition: bpy.props.IntProperty()

    def execute(self, context):
        obj = context.active_object
        props = obj.BIMStructuralProperties
        props.boundary_condition_attributes.clear()

        data = Data.boundary_conditions[self.boundary_condition]

        for attribute in IfcStore.get_schema().declaration_by_name(data["type"]).all_attributes():
            value = data[attribute.name()]
            data_type = ifcopenshell.util.attribute.get_primitive_type(attribute)
            new = props.boundary_condition_attributes.add()
            new.name = attribute.name()
            new.is_null = value is None
            new.is_optional = attribute.optional()
            if isinstance(data_type, tuple) and data_type[0] == "select":
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
    bl_options = {"REGISTER", "UNDO"}
    connection: bpy.props.IntProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
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
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        context.active_object.BIMStructuralProperties.active_boundary_condition = 0
        return {"FINISHED"}


class LoadStructuralAnalysisModels(bpy.types.Operator, Operator):
    bl_idname = "bim.load_structural_analysis_models"
    bl_label = "Load Structural Analysis Models"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.load_structural_analysis_models(tool.Structural)


class DisableStructuralAnalysisModelEditingUI(bpy.types.Operator, Operator):
    bl_idname = "bim.disable_structural_analysis_model_editing_ui"
    bl_label = "Disable Structural Analysis Model Editing UI"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.disable_structural_analysis_model_editing_ui(tool.Structural)


class AddStructuralAnalysisModel(bpy.types.Operator, Operator):
    bl_idname = "bim.add_structural_analysis_model"
    bl_label = "Add Structural Analysis Model"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        model = core.add_structural_analysis_model(tool.Ifc, tool.Structural)
        core.load_structural_analysis_model_attributes(tool.Structural, model=model.id())
        core.enable_editing_structural_analysis_model(tool.Structural, model=model.id())


class EditStructuralAnalysisModel(bpy.types.Operator, Operator):
    bl_idname = "bim.edit_structural_analysis_model"
    bl_label = "Edit Structural Analysis Model"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.edit_structural_analysis_model(tool.Ifc, tool.Structural)


class RemoveStructuralAnalysisModel(bpy.types.Operator, Operator):
    bl_idname = "bim.remove_structural_analysis_model"
    bl_label = "Remove Structural Analysis Model"
    bl_options = {"REGISTER", "UNDO"}
    structural_analysis_model: bpy.props.IntProperty()

    def _execute(self, context):
        core.remove_structural_analysis_model(tool.Ifc, tool.Structural, model=self.structural_analysis_model)


class EnableEditingStructuralAnalysisModel(bpy.types.Operator, Operator):
    bl_idname = "bim.enable_editing_structural_analysis_model"
    bl_label = "Enable Editing Structural Analysis Model"
    bl_options = {"REGISTER", "UNDO"}
    structural_analysis_model: bpy.props.IntProperty()

    def _execute(self, context):
        core.load_structural_analysis_model_attributes(tool.Structural, model=self.structural_analysis_model)
        core.enable_editing_structural_analysis_model(tool.Structural, model=self.structural_analysis_model)


class DisableEditingStructuralAnalysisModel(bpy.types.Operator, Operator):
    bl_idname = "bim.disable_editing_structural_analysis_model"
    bl_label = "Disable Editing Structural Analysis Model"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.disable_editing_structural_analysis_model(tool.Structural)


class AssignStructuralAnalysisModel(bpy.types.Operator, Operator):
    bl_idname = "bim.assign_structural_analysis_model"
    bl_label = "Assign Structural Analysis Model"
    bl_options = {"REGISTER", "UNDO"}
    product: bpy.props.StringProperty()
    structural_analysis_model: bpy.props.IntProperty()

    def _execute(self, context):
        core.assign_structural_analysis_model(
            tool.Ifc, tool.Structural, product=self.product, structural_analysis_model=self.structural_analysis_model
        )


class UnassignStructuralAnalysisModel(bpy.types.Operator, Operator):
    bl_idname = "bim.unassign_structural_analysis_model"
    bl_label = "Unassign Structural Analysis Model"
    bl_options = {"REGISTER", "UNDO"}
    product: bpy.props.StringProperty()
    structural_analysis_model: bpy.props.IntProperty()

    def _execute(self, context):
        core.unassign_structural_analysis_model(
            tool.Ifc, tool.Structural, product=self.product, structural_analysis_model=self.structural_analysis_model
        )


class EnableEditingStructuralItemAxis(bpy.types.Operator):
    bl_idname = "bim.enable_editing_structural_item_axis"
    bl_label = "Enable Editing Structural Item Axis"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        obj = context.active_object
        oprops = obj.BIMObjectProperties
        props = obj.BIMStructuralProperties

        self.file = IfcStore.get_file()
        item = self.file.by_id(oprops.ifc_definition_id)
        z_axis = Vector(item.Axis.DirectionRatios).normalized() @ obj.matrix_world if item.Axis else None
        x_axis = (obj.data.vertices[1].co - obj.data.vertices[0].co).normalized()
        location = obj.data.vertices[0].co
        empty = bpy.data.objects.new("Item Axis", None)
        empty.empty_display_type = "ARROWS"
        if z_axis:
            y_axis = (z_axis.cross(x_axis)).normalized()
            empty.matrix_world = Matrix(
                (
                    (x_axis[0], y_axis[0], z_axis[0], location[0]),
                    (x_axis[1], y_axis[1], z_axis[1], location[1]),
                    (x_axis[2], y_axis[2], z_axis[2], location[2]),
                    (0, 0, 0, 1),
                )
            )
        else:
            empty.location = location
            empty.rotation_mode = "QUATERNION"
            empty.rotation_quaternion = x_axis.to_track_quat("X", "Z")

        props.axis_angle = degrees(empty.rotation_euler[0])
        props.axis_empty = empty
        context.scene.collection.objects.link(empty)

        props.is_editing_axis = True
        return {"FINISHED"}


class DisableEditingStructuralItemAxis(bpy.types.Operator):
    bl_idname = "bim.disable_editing_structural_item_axis"
    bl_label = "Disable Editing Structural Item Axis"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        obj = context.active_object
        props = obj.BIMStructuralProperties
        props.is_editing_axis = False
        if props.axis_empty:
            bpy.data.objects.remove(props.axis_empty)
        return {"FINISHED"}


class EditStructuralItemAxis(bpy.types.Operator):
    bl_idname = "bim.edit_structural_item_axis"
    bl_label = "Edit Structural Item Axis"

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        obj = context.active_object
        oprops = obj.BIMObjectProperties
        props = obj.BIMStructuralProperties
        relative_matrix = props.axis_empty.matrix_world @ obj.matrix_world.inverted()
        z_axis = relative_matrix.col[2][0:3]
        self.file = IfcStore.get_file()
        ifcopenshell.api.run(
            "structural.edit_structural_item_axis",
            self.file,
            structural_item=self.file.by_id(oprops.ifc_definition_id),
            axis=z_axis,
        )
        bpy.ops.bim.disable_editing_structural_item_axis()
        return {"FINISHED"}


class EnableEditingStructuralConnectionCS(bpy.types.Operator):
    bl_idname = "bim.enable_editing_structural_connection_cs"
    bl_label = "Enable Editing Structural Item Connection CS"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        obj = context.active_object
        oprops = obj.BIMObjectProperties
        props = obj.BIMStructuralProperties

        self.file = IfcStore.get_file()
        item = self.file.by_id(oprops.ifc_definition_id)

        location = obj.data.vertices[0].co
        empty = bpy.data.objects.new("Item Connection CS", None)
        empty.empty_display_type = "ARROWS"
        empty.location = location

        if item.ConditionCoordinateSystem is not None:
            z_axis = (
                Vector(item.ConditionCoordinateSystem.Axis.DirectionRatios).normalized() @ obj.matrix_world
                if item.ConditionCoordinateSystem.Axis
                else None
            )
            x_axis = (
                Vector(item.ConditionCoordinateSystem.RefDirection.DirectionRatios).normalized() @ obj.matrix_world
                if item.ConditionCoordinateSystem.RefDirection
                else None
            )

            if z_axis:
                y_axis = (z_axis.cross(x_axis)).normalized()
                x_axis = (y_axis.cross(z_axis)).normalized()
                empty.matrix_world = Matrix(
                    (
                        (x_axis[0], y_axis[0], z_axis[0], location[0]),
                        (x_axis[1], y_axis[1], z_axis[1], location[1]),
                        (x_axis[2], y_axis[2], z_axis[2], location[2]),
                        (0, 0, 0, 1),
                    )
                )

        props.ccs_x_angle = degrees(empty.rotation_euler[0])
        props.ccs_y_angle = degrees(empty.rotation_euler[1])
        props.ccs_z_angle = degrees(empty.rotation_euler[2])
        props.ccs_empty = empty
        context.scene.collection.objects.link(empty)

        props.is_editing_connection_cs = True
        return {"FINISHED"}


class DisableEditingStructuralConnectionCS(bpy.types.Operator):
    bl_idname = "bim.disable_editing_structural_connection_cs"
    bl_label = "Disable Editing Structural Connection CS"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        obj = context.active_object
        props = obj.BIMStructuralProperties
        props.is_editing_connection_cs = False
        if props.ccs_empty:
            bpy.data.objects.remove(props.ccs_empty)
        return {"FINISHED"}


class EditStructuralConnectionCS(bpy.types.Operator):
    bl_idname = "bim.edit_structural_connection_cs"
    bl_label = "Edit Structural Connection CS"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        obj = context.active_object
        oprops = obj.BIMObjectProperties
        props = obj.BIMStructuralProperties
        relative_matrix = props.ccs_empty.matrix_world @ obj.matrix_world.inverted()
        x_axis = relative_matrix.col[0][0:3]
        z_axis = relative_matrix.col[2][0:3]
        self.file = IfcStore.get_file()
        ifcopenshell.api.run(
            "structural.edit_structural_connection_cs",
            self.file,
            structural_item=self.file.by_id(oprops.ifc_definition_id),
            axis=z_axis,
            ref_direction=x_axis,
        )
        bpy.ops.bim.disable_editing_structural_connection_cs()
        return {"FINISHED"}


class AssignStructuralLoadCase(bpy.types.Operator):
    bl_idname = "bim.assign_structural_load_case"
    bl_label = "Assign Structural Load Case"
    work_plan: bpy.props.IntProperty()
    load_case: bpy.props.IntProperty()

    def execute(self, context):
        self.file = IfcStore.get_file()
        ifcopenshell.api.run(
            "aggregate.assign_object",
            self.file,
            **{
                "relating_object": self.file.by_id(self.work_plan),
                "product": self.file.by_id(self.load_case),
            },
        )
        Data.load(IfcStore.get_file())
        return {"FINISHED"}


class UnassignStructuralLoadCase(bpy.types.Operator):
    bl_idname = "bim.unassign_structural_load_case"
    bl_label = "Unassign Structural Load Case"
    work_plan: bpy.props.IntProperty()
    load_case: bpy.props.IntProperty()

    def execute(self, context):
        self.file = IfcStore.get_file()
        ifcopenshell.api.run(
            "aggregate.unassign_object",
            self.file,
            **{
                "relating_object": self.file.by_id(self.work_plan),
                "product": self.file.by_id(self.load_case),
            },
        )
        Data.load(IfcStore.get_file())
        return {"FINISHED"}


class AddStructuralLoadCase(bpy.types.Operator):
    bl_idname = "bim.add_structural_load_case"
    bl_label = "Add Structural Load Case"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        ifcopenshell.api.run("structural.add_structural_load_case", IfcStore.get_file())
        Data.load(IfcStore.get_file())
        return {"FINISHED"}


class EditStructuralLoadCase(bpy.types.Operator):
    bl_idname = "bim.edit_structural_load_case"
    bl_label = "Edit Structural Load Case"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        props = context.scene.BIMStructuralProperties
        attributes = blenderbim.bim.helper.export_attributes(props.load_case_attributes)
        self.file = IfcStore.get_file()
        ifcopenshell.api.run(
            "structural.edit_structural_load_case",
            self.file,
            **{"load_case": self.file.by_id(props.active_load_case_id), "attributes": attributes},
        )
        Data.load(IfcStore.get_file())
        bpy.ops.bim.disable_editing_structural_load_case()
        return {"FINISHED"}


class RemoveStructuralLoadCase(bpy.types.Operator):
    bl_idname = "bim.remove_structural_load_case"
    bl_label = "Remove Structural Load Case"
    bl_options = {"REGISTER", "UNDO"}
    load_case: bpy.props.IntProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        self.file = IfcStore.get_file()
        ifcopenshell.api.run(
            "structural.remove_structural_load_case", self.file, load_case=self.file.by_id(self.load_case)
        )
        Data.load(self.file)
        return {"FINISHED"}


class EnableEditingStructuralLoadCase(bpy.types.Operator):
    bl_idname = "bim.enable_editing_structural_load_case"
    bl_label = "Enable Editing Structural Load Case"
    bl_options = {"REGISTER", "UNDO"}
    load_case: bpy.props.IntProperty()

    def execute(self, context):
        self.props = context.scene.BIMStructuralProperties
        self.props.active_load_case_id = self.load_case
        self.props.load_case_editing_type = "ATTRIBUTES"
        self.props.load_case_attributes.clear()
        data = Data.load_cases[self.load_case]
        blenderbim.bim.helper.import_attributes(
            "IfcStructuralLoadCase", self.props.load_case_attributes, data, self.import_attributes
        )
        return {"FINISHED"}

    def import_attributes(self, name, prop, data):
        if name in ["SelfWeightCoefficients"]:
            return False


class DisableEditingStructuralLoadCase(bpy.types.Operator):
    bl_idname = "bim.disable_editing_structural_load_case"
    bl_label = "Disable Editing Structural Load Case"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        context.scene.BIMStructuralProperties.active_load_case_id = 0
        return {"FINISHED"}


class EnableEditingStructuralLoadCaseGroups(bpy.types.Operator):
    bl_idname = "bim.enable_editing_structural_load_case_groups"
    bl_label = "Enable Editing Structural Load Case Groups"
    bl_options = {"REGISTER", "UNDO"}
    load_case: bpy.props.IntProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        self.props = context.scene.BIMStructuralProperties
        self.props.active_load_case_id = self.load_case
        self.props.load_case_editing_type = "GROUPS"
        return {"FINISHED"}


class AddStructuralLoadGroup(bpy.types.Operator):
    bl_idname = "bim.add_structural_load_group"
    bl_label = "Add Structural Load Group"
    bl_options = {"REGISTER", "UNDO"}
    load_case: bpy.props.IntProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        self.file = IfcStore.get_file()
        load_group = ifcopenshell.api.run("structural.add_structural_load_group", self.file)
        ifcopenshell.api.run(
            "group.assign_group", self.file, products=[load_group], group=self.file.by_id(self.load_case)
        )
        Data.load(IfcStore.get_file())
        return {"FINISHED"}


class RemoveStructuralLoadGroup(bpy.types.Operator):
    bl_idname = "bim.remove_structural_load_group"
    bl_label = "Remove Structural Load Group"
    bl_options = {"REGISTER", "UNDO"}
    load_group: bpy.props.IntProperty()

    def execute(self, context):
        self.file = IfcStore.get_file()
        ifcopenshell.api.run(
            "structural.remove_structural_load_group", self.file, load_group=self.file.by_id(self.load_group)
        )
        Data.load(self.file)
        return {"FINISHED"}


class EnableEditingStructuralLoadGroupActivities(bpy.types.Operator):
    bl_idname = "bim.enable_editing_structural_load_group_activities"
    bl_label = "Enable Editing Structural Load Group Activities"
    bl_options = {"REGISTER", "UNDO"}
    load_group: bpy.props.IntProperty()

    def execute(self, context):
        self.file = IfcStore.get_file()
        self.props = context.scene.BIMStructuralProperties
        self.props.active_load_group_id = self.load_group
        self.props.load_group_editing_type = "ACTIVITY"
        self.load_structural_activities()
        purge()
        return {"FINISHED"}

    def load_structural_activities(self):
        self.props.load_group_activities.clear()
        for activity_id in Data.load_groups[self.load_group]["IsGroupedBy"]:
            activity = Data.structural_activities[activity_id]
            new = self.props.load_group_activities.add()
            new.ifc_definition_id = activity_id
            new.name = self.file.by_id(activity["AssignedToStructuralItem"]).Name or "Unnamed"
            new.applied_load_class = self.file.by_id(activity["AppliedLoad"]).is_a()


class AddStructuralActivity(bpy.types.Operator):
    bl_idname = "bim.add_structural_activity"
    bl_label = "Add Structural Activity"
    bl_options = {"REGISTER", "UNDO"}
    load_group: bpy.props.IntProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        self.props = context.scene.BIMStructuralProperties
        self.file = IfcStore.get_file()
        for obj in context.selected_objects:
            if not obj.BIMObjectProperties.ifc_definition_id:
                continue
            element = self.file.by_id(obj.BIMObjectProperties.ifc_definition_id)
            applied_load_class = self.props.applicable_structural_load_types

            allowed_load_classes = {
                "IfcStructuralPointConnection": [
                    "IfcStructuralLoadTemperature",
                    "IfcStructuralLoadSingleForce",
                    "IfcStructuralLoadSingleDisplacement",
                ],
                "IfcStructuralCurveMember": ["IfcStructuralLoadTemperature", "IfcStructuralLoadLinearForce"],
                "IfcStructuralSurfaceMember": ["IfcStructuralLoadTemperature", "IfcStructuralLoadPlanarForce"],
            }

            applicable_activity_class = {
                "IfcStructuralPointConnection": "IfcStructuralPointAction",
                "IfcStructuralCurveMember": "IfcStructuralLinearAction",
                "IfcStructuralSurfaceMember": "IfcStructuralPlanarAction",
            }

            if applied_load_class not in allowed_load_classes[element.is_a()]:
                continue

            ifc_class = applicable_activity_class[element.is_a()]

            activity = ifcopenshell.api.run(
                "structural.add_structural_activity",
                self.file,
                ifc_class=ifc_class,
                applied_load=self.file.by_id(int(self.props.applicable_structural_loads)),
                structural_member=element,
            )
            ifcopenshell.api.run(
                "group.assign_group", self.file, products=[activity], group=self.file.by_id(self.load_group)
            )
        Data.load(IfcStore.get_file())
        bpy.ops.bim.enable_editing_structural_load_group_activities(load_group=self.load_group)
        return {"FINISHED"}


class LoadStructuralLoads(bpy.types.Operator):
    bl_idname = "bim.load_structural_loads"
    bl_label = "Load Structural Loads"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        self.file = IfcStore.get_file()
        props = context.scene.BIMStructuralProperties
        props.structural_loads.clear()
        if props.filtered_structural_loads:
            names = [structural_load["Name"] or "Unnamed" for _, structural_load in Data.structural_loads.items()]
            for ifc_definition_id, structural_load in Data.structural_loads.items():
                if (
                    names.count(structural_load["Name"] or "Unnamed") > 1
                    and len(self.file.get_inverse(self.file.by_id(ifc_definition_id))) < 2
                ):
                    continue
                new = props.structural_loads.add()
                new.ifc_definition_id = ifc_definition_id
                new.name = structural_load["Name"] or "Unnamed"
                new.number_of_inverse_references = len(self.file.get_inverse(self.file.by_id(ifc_definition_id)))

        else:
            for ifc_definition_id, structural_load in Data.structural_loads.items():
                new = props.structural_loads.add()
                new.ifc_definition_id = ifc_definition_id
                new.name = structural_load["Name"] or "Unnamed"
                new.number_of_inverse_references = len(self.file.get_inverse(self.file.by_id(ifc_definition_id)))
        props.is_editing_loads = True
        bpy.ops.bim.disable_editing_structural_load()
        return {"FINISHED"}


class DisableStructuralLoadEditingUI(bpy.types.Operator):
    bl_idname = "bim.disable_structural_load_editing_ui"
    bl_label = "Disable Structural Load Editing UI"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        context.scene.BIMStructuralProperties.is_editing_loads = False
        return {"FINISHED"}


class AddStructuralLoad(bpy.types.Operator):
    bl_idname = "bim.add_structural_load"
    bl_label = "Add Structural Load"
    bl_options = {"REGISTER", "UNDO"}
    ifc_class: bpy.props.StringProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        result = ifcopenshell.api.run(
            "structural.add_structural_load", IfcStore.get_file(), name="New Load", ifc_class=self.ifc_class
        )
        Data.load(IfcStore.get_file())
        bpy.ops.bim.load_structural_loads()
        bpy.ops.bim.enable_editing_structural_load(structural_load=result.id())
        return {"FINISHED"}


class EnableEditingStructuralLoad(bpy.types.Operator):
    bl_idname = "bim.enable_editing_structural_load"
    bl_label = "Enable Editing Structural Load"
    bl_options = {"REGISTER", "UNDO"}
    structural_load: bpy.props.IntProperty()

    def execute(self, context):
        props = context.scene.BIMStructuralProperties
        props.structural_load_attributes.clear()

        data = Data.structural_loads[self.structural_load]
        blenderbim.bim.helper.import_attributes(data["type"], props.structural_load_attributes, data)
        props.active_structural_load_id = self.structural_load
        return {"FINISHED"}


class DisableEditingStructuralLoad(bpy.types.Operator):
    bl_idname = "bim.disable_editing_structural_load"
    bl_label = "Disable Editing Structural Load"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        context.scene.BIMStructuralProperties.active_structural_load_id = 0
        return {"FINISHED"}


class RemoveStructuralLoad(bpy.types.Operator):
    bl_idname = "bim.remove_structural_load"
    bl_label = "Remove Structural Load"
    bl_options = {"REGISTER", "UNDO"}
    structural_load: bpy.props.IntProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        props = context.scene.BIMStructuralProperties
        self.file = IfcStore.get_file()
        ifcopenshell.api.run(
            "structural.remove_structural_load",
            self.file,
            **{"structural_load": self.file.by_id(self.structural_load)},
        )
        Data.load(IfcStore.get_file())
        bpy.ops.bim.load_structural_loads()
        return {"FINISHED"}


class EditStructuralLoad(bpy.types.Operator):
    bl_idname = "bim.edit_structural_load"
    bl_label = "Edit Structural Load"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        props = context.scene.BIMStructuralProperties
        attributes = blenderbim.bim.helper.export_attributes(props.structural_load_attributes)
        self.file = IfcStore.get_file()
        ifcopenshell.api.run(
            "structural.edit_structural_load",
            self.file,
            **{
                "structural_load": self.file.by_id(props.active_structural_load_id),
                "attributes": attributes,
            },
        )
        Data.load(IfcStore.get_file())
        bpy.ops.bim.load_structural_loads()
        return {"FINISHED"}


class ToggleFilterStructuralLoads(bpy.types.Operator):
    bl_idname = "bim.toggle_filter_structural_loads"
    bl_label = "Toggle Filter Structural Loads"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        props = context.scene.BIMStructuralProperties
        props.filtered_structural_loads = not props.filtered_structural_loads
        bpy.ops.bim.load_structural_loads()
        return {"FINISHED"}


class LoadBoundaryConditions(bpy.types.Operator):
    bl_idname = "bim.load_boundary_conditions"
    bl_label = "Load Boundary Conditions"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        self.file = IfcStore.get_file()
        props = context.scene.BIMStructuralProperties
        props.boundary_conditions.clear()
        if props.filtered_boundary_conditions:
            names = [
                boundary_condition["Name"] or "Unnamed" for _, boundary_condition in Data.boundary_conditions.items()
            ]
            for ifc_definition_id, boundary_condition in Data.boundary_conditions.items():
                if (
                    names.count(boundary_condition["Name"] or "Unnamed") > 1
                    and len(self.file.get_inverse(self.file.by_id(ifc_definition_id))) < 2
                ):
                    continue
                new = props.boundary_conditions.add()
                new.ifc_definition_id = ifc_definition_id
                new.name = boundary_condition["Name"] or "Unnamed"
                new.number_of_inverse_references = len(self.file.get_inverse(self.file.by_id(ifc_definition_id)))

        else:
            for ifc_definition_id, boundary_condition in Data.boundary_conditions.items():
                new = props.boundary_conditions.add()
                new.ifc_definition_id = ifc_definition_id
                new.name = boundary_condition["Name"] or "Unnamed"
                new.number_of_inverse_references = len(self.file.get_inverse(self.file.by_id(ifc_definition_id)))
        props.is_editing_boundary_conditions = True
        bpy.ops.bim.disable_editing_boundary_condition()
        return {"FINISHED"}


class ToggleFilterBoundaryConditions(bpy.types.Operator):
    bl_idname = "bim.toggle_filter_boundary_conditions"
    bl_label = "Toggle Filter Boundary Conditions"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        props = context.scene.BIMStructuralProperties
        props.filtered_boundary_conditions = not props.filtered_boundary_conditions
        bpy.ops.bim.load_boundary_conditions()
        return {"FINISHED"}


class DisableBoundaryConditionEditingUI(bpy.types.Operator):
    bl_idname = "bim.disable_boundary_condition_editing_ui"
    bl_label = "Disable Boundary Condition Editing UI"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        context.scene.BIMStructuralProperties.is_editing_boundary_conditions = False
        return {"FINISHED"}


class AddBoundaryCondition(bpy.types.Operator):
    bl_idname = "bim.add_boundary_condition"
    bl_label = "Add Boundary Condition"
    bl_options = {"REGISTER", "UNDO"}
    ifc_class: bpy.props.StringProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        result = ifcopenshell.api.run(
            "structural.add_structural_boundary_condition",
            IfcStore.get_file(),
            name="New Load",
            ifc_class=self.ifc_class,
        )
        Data.load(IfcStore.get_file())
        bpy.ops.bim.load_boundary_conditions()
        bpy.ops.bim.enable_editing_boundary_condition(boundary_condition=result.id())
        return {"FINISHED"}


class EnableEditingBoundaryCondition(bpy.types.Operator):
    bl_idname = "bim.enable_editing_boundary_condition"
    bl_label = "Enable Editing Boundary Condition"
    bl_options = {"REGISTER", "UNDO"}
    boundary_condition: bpy.props.IntProperty()

    def execute(self, context):
        props = context.scene.BIMStructuralProperties
        props.boundary_condition_attributes.clear()

        data = Data.boundary_conditions[self.boundary_condition]
        # blenderbim.bim.helper.import_attributes(data["type"], props.boundary_condition_attributes, data)
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
        props.active_boundary_condition_id = self.boundary_condition
        return {"FINISHED"}


class DisableEditingBoundaryCondition(bpy.types.Operator):
    bl_idname = "bim.disable_editing_boundary_condition"
    bl_label = "Disable Editing Boundary Condition"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        context.scene.BIMStructuralProperties.active_boundary_condition_id = 0
        return {"FINISHED"}


class RemoveBoundaryCondition(bpy.types.Operator):
    bl_idname = "bim.remove_boundary_condition"
    bl_label = "Remove Boundary Condition"
    bl_options = {"REGISTER", "UNDO"}
    boundary_condition: bpy.props.IntProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        props = context.scene.BIMStructuralProperties
        self.file = IfcStore.get_file()
        ifcopenshell.api.run(
            "structural.remove_structural_boundary_condition",
            self.file,
            **{"boundary_condition": self.file.by_id(self.boundary_condition)},
        )
        Data.load(IfcStore.get_file())
        bpy.ops.bim.load_boundary_conditions()
        return {"FINISHED"}


class EditBoundaryCondition(bpy.types.Operator):
    bl_idname = "bim.edit_boundary_condition"
    bl_label = "Edit Boundary Condition"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        props = context.scene.BIMStructuralProperties
        self.file = IfcStore.get_file()
        # attributes = blenderbim.bim.helper.export_attributes(props.boundary_condition_attributes)
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
            "structural.edit_structural_boundary_condition",
            self.file,
            **{"condition": self.file.by_id(props.active_boundary_condition_id), "attributes": attributes},
        )
        Data.load(IfcStore.get_file())
        bpy.ops.bim.load_boundary_conditions()
        return {"FINISHED"}
