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

from math import degrees
from typing import TYPE_CHECKING, Literal, Union

import bpy
import ifcopenshell.api.group
import ifcopenshell.api.structural
import ifcopenshell.util.unit
from mathutils import Matrix, Vector

import bonsai.bim.helper
import bonsai.core.structural as core
import bonsai.tool as tool
from bonsai.bim.module.structural.data import StructuralAnalysisModelsData, StructuralLoadCasesData
from bonsai.bim.module.structural.decorator import LoadsDecorator


class ShowLoads(bpy.types.Operator):
    """Draw decorations to show structural actions in 3d view"""

    bl_idname = "bim.show_loads"
    bl_label = "Show Loads in 3D View"
    bl_options = {"REGISTER", "UNDO"}

    def modal(self, context, event):
        assert context.screen
        if event.type == "F5":
            LoadsDecorator.update()
            tool.Blender.update_all_viewports(context)
        if event.type == "ESC":
            LoadsDecorator.uninstall()
            tool.Blender.update_all_viewports(context)
            return {"FINISHED"}
        return {"PASS_THROUGH"}

    def invoke(self, context, event):
        assert context.window and context.window_manager and context.screen
        collection = bpy.data.collections.get("IfcStructuralItem")
        if collection is None:
            self.report({"ERROR"}, "No IfcStructuralItems found.")
            return {"CANCELLED"}

        collection.hide_viewport = False
        context.window.cursor_modal_set("WAIT")
        try:
            LoadsDecorator.install(context)
        except Exception as exc:
            context.window.cursor_modal_restore()
            raise exc
        context.window.cursor_modal_restore()
        context.window_manager.modal_handler_add(self)
        tool.Blender.update_all_viewports(context)

        return {"RUNNING_MODAL"}


class AddStructuralMemberConnection(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_structural_member_connection"
    bl_label = "Add Structural Member Connection"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        obj = context.active_object
        assert obj
        oprops = tool.Blender.get_object_bim_props(obj)
        props = tool.Structural.get_object_structural_props(obj)
        file = tool.Ifc.get()
        related_structural_connection = file.by_id(oprops.ifc_definition_id)
        assert props.relating_structural_member
        relating_structural_member = tool.Ifc.get_entity(props.relating_structural_member)
        assert relating_structural_member
        if not relating_structural_member.is_a("IfcStructuralMember"):
            return {"FINISHED"}
        ifcopenshell.api.structural.add_structural_member_connection(
            file,
            relating_structural_member=relating_structural_member,
            related_structural_connection=related_structural_connection,
        )
        props.relating_structural_member = None
        return {"FINISHED"}


class EnableEditingStructuralConnectionCondition(bpy.types.Operator):
    bl_idname = "bim.enable_editing_structural_connection_condition"
    bl_label = "Enable Editing Structural Connection Condition"
    bl_options = {"REGISTER", "UNDO"}
    connects_structural_member: bpy.props.IntProperty()

    def execute(self, context):
        obj = context.active_object
        assert obj
        props = tool.Structural.get_object_structural_props(obj)
        props.active_connects_structural_member = self.connects_structural_member
        return {"FINISHED"}


class DisableEditingStructuralConnectionCondition(bpy.types.Operator):
    bl_idname = "bim.disable_editing_structural_connection_condition"
    bl_label = "Disable Editing Structural Connection Condition"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        obj = context.active_object
        assert obj
        props = tool.Structural.get_object_structural_props(obj)
        props.active_connects_structural_member = 0
        return {"FINISHED"}


class RemoveStructuralConnectionCondition(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.remove_structural_connection_condition"
    bl_label = "Remove Structural Connection Condition"
    bl_options = {"REGISTER", "UNDO"}
    connects_structural_member: bpy.props.IntProperty()

    def _execute(self, context):
        file = tool.Ifc.get()
        relation = file.by_id(self.connects_structural_member)
        connection = relation.RelatedStructuralConnection
        ifcopenshell.api.structural.remove_structural_connection_condition(file, relation=relation)
        return {"FINISHED"}


class AddStructuralBoundaryCondition(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_structural_boundary_condition"
    bl_label = "Add Structural Boundary Condition"
    bl_options = {"REGISTER", "UNDO"}
    connection: bpy.props.IntProperty()

    def _execute(self, context):
        file = tool.Ifc.get()
        connection = file.by_id(self.connection)
        ifcopenshell.api.structural.add_structural_boundary_condition(file, connection=connection)
        return {"FINISHED"}


class RemoveStructuralBoundaryCondition(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.remove_structural_boundary_condition"
    bl_label = "Remove Structural Boundary Condition"
    bl_options = {"REGISTER", "UNDO"}
    connection: bpy.props.IntProperty()

    def _execute(self, context):
        file = tool.Ifc.get()
        connection = file.by_id(self.connection)
        ifcopenshell.api.structural.remove_structural_boundary_condition(file, connection=connection)
        return {"FINISHED"}


class EnableEditingStructuralBoundaryCondition(bpy.types.Operator):
    bl_idname = "bim.enable_editing_structural_boundary_condition"
    bl_label = "Enable Editing Structural Boundary Condition"
    bl_options = {"REGISTER", "UNDO"}
    boundary_condition: bpy.props.IntProperty()

    if TYPE_CHECKING:
        boundary_condition: int

    def execute(self, context):
        obj = context.active_object
        assert obj
        props = tool.Structural.get_object_structural_props(obj)
        condition = tool.Ifc.get().by_id(self.boundary_condition)
        tool.Structural.import_boundary_condition_attributes(condition, props)
        props.active_boundary_condition = self.boundary_condition
        return {"FINISHED"}


class EditStructuralBoundaryCondition(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.edit_structural_boundary_condition"
    bl_label = "Edit Structural Boundary Condition"
    bl_options = {"REGISTER", "UNDO"}
    connection: bpy.props.IntProperty()

    if TYPE_CHECKING:
        connection: int

    def _execute(self, context):
        obj = context.active_object
        assert obj
        props = tool.Structural.get_object_structural_props(obj)

        file = tool.Ifc.get()
        connection = file.by_id(self.connection)
        condition = connection.AppliedCondition

        tool.Structural.export_and_apply_boundary_condition_attributes(condition, props)
        bpy.ops.bim.disable_editing_structural_boundary_condition()
        return {"FINISHED"}


class DisableEditingStructuralBoundaryCondition(bpy.types.Operator):
    bl_idname = "bim.disable_editing_structural_boundary_condition"
    bl_label = "Disable Editing Structural Boundary Condition"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        obj = context.active_object
        assert obj
        props = tool.Structural.get_object_structural_props(obj)
        props.active_boundary_condition = 0
        return {"FINISHED"}


class LoadStructuralAnalysisModels(bpy.types.Operator):
    bl_idname = "bim.load_structural_analysis_models"
    bl_label = "Load Structural Analysis Models"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        core.load_structural_analysis_models(tool.Structural)
        return {"FINISHED"}


class DisableStructuralAnalysisModelEditingUI(bpy.types.Operator):
    bl_idname = "bim.disable_structural_analysis_model_editing_ui"
    bl_label = "Disable Structural Analysis Model Editing UI"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        core.disable_structural_analysis_model_editing_ui(tool.Structural)
        return {"FINISHED"}


class AddStructuralAnalysisModel(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_structural_analysis_model"
    bl_label = "Add Structural Analysis Model"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        model = core.add_structural_analysis_model(tool.Ifc, tool.Structural)
        core.load_structural_analysis_model_attributes(tool.Structural, model=model.id())
        core.enable_editing_structural_analysis_model(tool.Structural, model=model.id())


class SetCurrentStructuralAnalysisModel(bpy.types.Operator):
    bl_idname = "bim.set_current_structural_analysis_model"
    bl_label = "Set Current Structural Analysis Model"
    bl_description = "New structural items and load cases are assigned to the current model"
    bl_options = {"REGISTER", "UNDO"}
    structural_analysis_model: bpy.props.IntProperty()

    def execute(self, context):
        tool.Structural.set_current_structural_analysis_model(tool.Ifc.get().by_id(self.structural_analysis_model))
        StructuralAnalysisModelsData.is_loaded = False
        StructuralLoadCasesData.is_loaded = False
        return {"FINISHED"}


class EditStructuralAnalysisModel(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.edit_structural_analysis_model"
    bl_label = "Edit Structural Analysis Model"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.edit_structural_analysis_model(tool.Ifc, tool.Structural)


class RemoveStructuralAnalysisModel(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.remove_structural_analysis_model"
    bl_label = "Remove Structural Analysis Model"
    bl_options = {"REGISTER", "UNDO"}
    structural_analysis_model: bpy.props.IntProperty()

    def _execute(self, context):
        core.remove_structural_analysis_model(tool.Ifc, tool.Structural, model=self.structural_analysis_model)


class EnableEditingStructuralAnalysisModel(bpy.types.Operator):
    bl_idname = "bim.enable_editing_structural_analysis_model"
    bl_label = "Enable Editing Structural Analysis Model"
    bl_options = {"REGISTER", "UNDO"}
    structural_analysis_model: bpy.props.IntProperty()

    def execute(self, context):
        core.load_structural_analysis_model_attributes(tool.Structural, model=self.structural_analysis_model)
        core.enable_editing_structural_analysis_model(tool.Structural, model=self.structural_analysis_model)
        return {"FINISHED"}


class DisableEditingStructuralAnalysisModel(bpy.types.Operator):
    bl_idname = "bim.disable_editing_structural_analysis_model"
    bl_label = "Disable Editing Structural Analysis Model"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        core.disable_editing_structural_analysis_model(tool.Structural)
        return {"FINISHED"}


class AssignStructuralAnalysisModel(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.assign_structural_analysis_model"
    bl_label = "Assign Structural Analysis Model"
    bl_description = "Assign structual analysis model to the selected objects."
    bl_options = {"REGISTER", "UNDO"}
    structural_analysis_model: bpy.props.IntProperty()

    def _execute(self, context):
        ifc_file = tool.Ifc.get()
        structural_analysis_model = ifc_file.by_id(self.structural_analysis_model)
        products = [element for o in tool.Blender.get_selected_objects() if (element := tool.Ifc.get_entity(o))]
        core.assign_structural_analysis_model(
            tool.Ifc, products=products, structural_analysis_model=structural_analysis_model
        )


class UnassignStructuralAnalysisModel(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.unassign_structural_analysis_model"
    bl_label = "Unassign Structural Analysis Model"
    bl_description = "Unassign structual analysis model from the selected objects."
    bl_options = {"REGISTER", "UNDO"}
    structural_analysis_model: bpy.props.IntProperty()

    def _execute(self, context):
        ifc_file = tool.Ifc.get()
        structural_analysis_model = ifc_file.by_id(self.structural_analysis_model)
        products = [element for o in tool.Blender.get_selected_objects() if (element := tool.Ifc.get_entity(o))]
        core.unassign_structural_analysis_model(
            tool.Ifc, products=products, structural_analysis_model=structural_analysis_model
        )


class EnableEditingStructuralItemAxis(bpy.types.Operator):
    bl_idname = "bim.enable_editing_structural_item_axis"
    bl_label = "Enable Editing Structural Item Axis"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        obj = context.active_object
        assert obj
        oprops = tool.Blender.get_object_bim_props(obj)
        props = tool.Structural.get_object_structural_props(obj)

        self.file = tool.Ifc.get()
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
        assert obj
        props = tool.Structural.get_object_structural_props(obj)
        props.is_editing_axis = False
        if props.axis_empty:
            bpy.data.objects.remove(props.axis_empty)
        return {"FINISHED"}


class EditStructuralItemAxis(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.edit_structural_item_axis"
    bl_label = "Edit Structural Item Axis"

    def _execute(self, context):
        obj = context.active_object
        assert obj
        oprops = tool.Blender.get_object_bim_props(obj)
        props = tool.Structural.get_object_structural_props(obj)
        relative_matrix = props.axis_empty.matrix_world @ obj.matrix_world.inverted()
        z_axis = relative_matrix.col[2][0:3]
        self.file = tool.Ifc.get()
        ifcopenshell.api.structural.edit_structural_item_axis(
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
        assert obj
        props = tool.Structural.get_object_structural_props(obj)

        self.file = tool.Ifc.get()
        item = tool.Ifc.get_entity(obj)
        assert item

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
        assert obj
        props = tool.Structural.get_object_structural_props(obj)
        props.is_editing_connection_cs = False
        if props.ccs_empty:
            bpy.data.objects.remove(props.ccs_empty)
        return {"FINISHED"}


class EditStructuralConnectionCS(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.edit_structural_connection_cs"
    bl_label = "Edit Structural Connection CS"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        obj = context.active_object
        assert obj
        item = tool.Ifc.get_entity(obj)
        assert item
        props = tool.Structural.get_object_structural_props(obj)
        relative_matrix = props.ccs_empty.matrix_world @ obj.matrix_world.inverted()
        x_axis = relative_matrix.col[0][0:3]
        z_axis = relative_matrix.col[2][0:3]
        self.file = tool.Ifc.get()
        ifcopenshell.api.structural.edit_structural_connection_cs(
            self.file,
            structural_item=item,
            axis=z_axis,
            ref_direction=x_axis,
        )
        bpy.ops.bim.disable_editing_structural_connection_cs()
        return {"FINISHED"}


class AssignStructuralLoadCase(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.assign_structural_load_case"
    bl_label = "Assign Structural Load Case"
    bl_description = "Assign the load case to the current structural analysis model"
    bl_options = {"REGISTER", "UNDO"}
    structural_analysis_model: bpy.props.IntProperty()
    load_case: bpy.props.IntProperty()

    def _execute(self, context):
        self.file = tool.Ifc.get()
        ifcopenshell.api.structural.assign_structural_load_group(
            self.file,
            load_groups=[self.file.by_id(self.load_case)],
            structural_analysis_model=self.file.by_id(self.structural_analysis_model),
        )
        return {"FINISHED"}


class UnassignStructuralLoadCase(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.unassign_structural_load_case"
    bl_label = "Unassign Structural Load Case"
    bl_description = "Unassign the load case from the current structural analysis model"
    bl_options = {"REGISTER", "UNDO"}
    structural_analysis_model: bpy.props.IntProperty()
    load_case: bpy.props.IntProperty()

    def _execute(self, context):
        self.file = tool.Ifc.get()
        ifcopenshell.api.structural.unassign_structural_load_group(
            self.file,
            load_groups=[self.file.by_id(self.load_case)],
            structural_analysis_model=self.file.by_id(self.structural_analysis_model),
        )
        return {"FINISHED"}


class AddStructuralLoadCase(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_structural_load_case"
    bl_label = "Add Structural Load Case"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        load_case = ifcopenshell.api.structural.add_structural_load_case(tool.Ifc.get())
        tool.Structural.assign_to_current_structural_analysis_model(load_case)
        return {"FINISHED"}


class EditStructuralLoadCase(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.edit_structural_load_case"
    bl_label = "Edit Structural Load Case"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        props = tool.Structural.get_structural_props()
        attributes = bonsai.bim.helper.export_attributes(props.load_case_attributes)
        self.file = tool.Ifc.get()
        ifcopenshell.api.structural.edit_structural_load_case(
            self.file,
            load_case=self.file.by_id(props.active_load_case_id),
            attributes=attributes,
        )
        bpy.ops.bim.disable_editing_structural_load_case()
        return {"FINISHED"}


class RemoveStructuralLoadCase(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.remove_structural_load_case"
    bl_label = "Remove Structural Load Case"
    bl_options = {"REGISTER", "UNDO"}
    load_case: bpy.props.IntProperty()

    def _execute(self, context):
        self.file = tool.Ifc.get()
        ifcopenshell.api.structural.remove_structural_load_case(self.file, load_case=self.file.by_id(self.load_case))
        return {"FINISHED"}


class EnableEditingStructuralLoadCase(bpy.types.Operator):
    bl_idname = "bim.enable_editing_structural_load_case"
    bl_label = "Enable Editing Structural Load Case"
    bl_options = {"REGISTER", "UNDO"}
    load_case: bpy.props.IntProperty()

    def execute(self, context):
        self.props = tool.Structural.get_structural_props()
        self.props.active_load_case_id = self.load_case
        self.props.load_case_editing_type = "ATTRIBUTES"
        self.props.load_case_attributes.clear()
        bonsai.bim.helper.import_attributes(
            tool.Ifc.get().by_id(self.load_case),
            self.props.load_case_attributes,
            callback=self.import_attributes_callback,
        )
        return {"FINISHED"}

    def import_attributes_callback(self, name: str, prop: object, data: object) -> None | Literal[False]:
        if name in ["SelfWeightCoefficients"]:
            return False


class DisableEditingStructuralLoadCase(bpy.types.Operator):
    bl_idname = "bim.disable_editing_structural_load_case"
    bl_label = "Disable Editing Structural Load Case"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        props = tool.Structural.get_structural_props()
        props.active_load_case_id = 0
        return {"FINISHED"}


class EnableEditingStructuralLoadCaseGroups(bpy.types.Operator):
    bl_idname = "bim.enable_editing_structural_load_case_groups"
    bl_label = "Enable Editing Structural Load Case Groups"
    bl_options = {"REGISTER", "UNDO"}
    load_case: bpy.props.IntProperty()

    def execute(self, context):
        props = tool.Structural.get_structural_props()
        props.active_load_case_id = self.load_case
        props.load_case_editing_type = "GROUPS"
        return {"FINISHED"}


class AddStructuralLoadGroup(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_structural_load_group"
    bl_label = "Add Structural Load Group"
    bl_options = {"REGISTER", "UNDO"}
    load_case: bpy.props.IntProperty()

    def _execute(self, context):
        self.file = tool.Ifc.get()
        load_group = ifcopenshell.api.structural.add_structural_load_group(self.file)
        ifcopenshell.api.group.assign_group(self.file, products=[load_group], group=self.file.by_id(self.load_case))
        return {"FINISHED"}


class RemoveStructuralLoadGroup(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.remove_structural_load_group"
    bl_label = "Remove Structural Load Group"
    bl_options = {"REGISTER", "UNDO"}
    load_group: bpy.props.IntProperty()

    def _execute(self, context):
        self.file = tool.Ifc.get()
        ifcopenshell.api.structural.remove_structural_load_group(self.file, load_group=self.file.by_id(self.load_group))
        return {"FINISHED"}


class EnableEditingStructuralLoadGroupActivities(bpy.types.Operator):
    bl_idname = "bim.enable_editing_structural_load_group_activities"
    bl_label = "Enable Editing Structural Load Group Activities"
    bl_options = {"REGISTER", "UNDO"}
    load_group: bpy.props.IntProperty()

    def execute(self, context):
        self.file = tool.Ifc.get()
        self.props = tool.Structural.get_structural_props()
        self.props.active_load_group_id = self.load_group
        self.props.load_group_editing_type = "ACTIVITY"
        self.load_structural_activities()
        return {"FINISHED"}

    def load_structural_activities(self) -> None:
        self.props.load_group_activities.clear()
        for rel in self.file.by_id(self.load_group).IsGroupedBy:
            for activity in rel.RelatedObjects:
                new = self.props.load_group_activities.add()
                new.ifc_definition_id = activity.id()
                rels = activity.AssignedToStructuralItem
                new.name = (rels[0].RelatingElement.Name if rels else None) or "Unnamed"
                new.applied_load_class = activity.AppliedLoad.is_a()


class AddStructuralActivity(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_structural_activity"
    bl_label = "Add Structural Activity"
    bl_options = {"REGISTER", "UNDO"}
    load_group: bpy.props.IntProperty()

    def _execute(self, context):
        self.props = tool.Structural.get_structural_props()
        if not self.props.applicable_structural_loads:
            self.report({"ERROR"}, "No structural load of the chosen type to apply.")
            return {"CANCELLED"}
        self.file = tool.Ifc.get()
        for obj in context.selected_objects:
            element = tool.Ifc.get_entity(obj)
            if not element:
                continue
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

            activity = ifcopenshell.api.structural.add_structural_activity(
                self.file,
                ifc_class=ifc_class,
                applied_load=self.file.by_id(int(self.props.applicable_structural_loads)),
                structural_member=element,
            )
            ifcopenshell.api.group.assign_group(self.file, products=[activity], group=self.file.by_id(self.load_group))
        bpy.ops.bim.enable_editing_structural_load_group_activities(load_group=self.load_group)
        return {"FINISHED"}


class RemoveStructuralActivity(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.remove_structural_activity"
    bl_label = "Remove Structural Activity"
    bl_options = {"REGISTER", "UNDO"}
    activity: bpy.props.IntProperty()

    def _execute(self, context):
        self.file = tool.Ifc.get()
        props = tool.Structural.get_structural_props()
        ifcopenshell.api.structural.remove_structural_activity(self.file, activity=self.file.by_id(self.activity))
        bpy.ops.bim.enable_editing_structural_load_group_activities(load_group=props.active_load_group_id)
        return {"FINISHED"}


# Load class, activity class, force attributes and moment attributes for each kind of structural item.
APPLY_LOAD_CLASSES = {
    "IfcStructuralPointConnection": (
        "IfcStructuralLoadSingleForce",
        "IfcStructuralPointAction",
        ("ForceX", "ForceY", "ForceZ"),
        ("MomentX", "MomentY", "MomentZ"),
    ),
    "IfcStructuralCurveMember": (
        "IfcStructuralLoadLinearForce",
        "IfcStructuralLinearAction",
        ("LinearForceX", "LinearForceY", "LinearForceZ"),
        ("LinearMomentX", "LinearMomentY", "LinearMomentZ"),
    ),
    "IfcStructuralSurfaceMember": (
        "IfcStructuralLoadPlanarForce",
        "IfcStructuralPlanarAction",
        ("PlanarForceX", "PlanarForceY", "PlanarForceZ"),
        (),
    ),
}

# Blender needs enum item strings to stay referenced while the dialog is open.
apply_load_group_items: list[tuple[str, str, str]] = []


def get_apply_load_groups(self, context: bpy.types.Context) -> list[tuple[str, str, str]]:
    global apply_load_group_items
    model = tool.Structural.get_current_structural_analysis_model()
    groups = list(model.LoadedBy or []) if model else list(tool.Ifc.get().by_type("IfcStructuralLoadCase"))
    apply_load_group_items = []
    for group in groups:
        apply_load_group_items.append((str(group.id()), group.Name or "Unnamed", group.is_a()))
        for rel in group.IsGroupedBy:
            for subgroup in rel.RelatedObjects:
                if subgroup.is_a("IfcStructuralLoadGroup"):
                    name = subgroup.Name or "Unnamed"
                    apply_load_group_items.append((str(subgroup.id()), f"    {name}", subgroup.is_a()))
    apply_load_group_items.append(("0", "New Load Case", "Create a new load case in the current model"))
    return apply_load_group_items


class ApplyStructuralLoad(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.apply_structural_load"
    bl_label = "Apply Structural Load"
    bl_description = "Apply a force to the selected structural point connections, curve members or surface members"
    bl_options = {"REGISTER", "UNDO"}
    load_group: bpy.props.EnumProperty(name="Load Case", items=get_apply_load_groups)
    new_load_case_name: bpy.props.StringProperty(name="New Load Case", default="Load Case")
    input_mode: bpy.props.EnumProperty(
        name="Input",
        items=[
            ("COMPONENTS", "Components", "X, Y and Z components"),
            ("ANGLE", "Angle", "Magnitude and angle above the horizontal, in the X-Z plane"),
            ("SLOPE", "Slope", "Magnitude and rise over run, in the X-Z plane"),
        ],
    )
    magnitude: bpy.props.FloatProperty(name="Magnitude")
    angle: bpy.props.FloatProperty(name="Angle", description="Degrees from +X towards +Z")
    rise: bpy.props.FloatProperty(name="Rise", description="Towards +Z", default=1.0)
    run: bpy.props.FloatProperty(name="Run", description="Towards +X", default=1.0)
    x: bpy.props.FloatProperty(name="X")
    y: bpy.props.FloatProperty(name="Y")
    z: bpy.props.FloatProperty(name="Z")
    moment_x: bpy.props.FloatProperty(name="Moment X")
    moment_y: bpy.props.FloatProperty(name="Moment Y")
    moment_z: bpy.props.FloatProperty(name="Moment Z")
    load_name: bpy.props.StringProperty(name="Load Name", description="Leave empty to name the load after its values")

    def get_targets(self, context: bpy.types.Context) -> tuple[Union[str, None], list[ifcopenshell.entity_instance]]:
        elements = [e for o in context.selected_objects if (e := tool.Ifc.get_entity(o))]
        categories = {c for e in elements for c in APPLY_LOAD_CLASSES if e.is_a(c)}
        if len(categories) != 1:
            return None, []
        category = categories.pop()
        return category, [e for e in elements if e.is_a(category)]

    def invoke(self, context, event):
        if not self.get_targets(context)[0]:
            self.report({"ERROR"}, "Select point connections, curve members or surface members, but only one kind.")
            return {"CANCELLED"}
        return context.window_manager.invoke_props_dialog(self, width=350)

    def get_components(self) -> tuple[float, float, float]:
        if self.input_mode == "COMPONENTS":
            return self.x, self.y, self.z
        x, z = tool.Structural.get_in_plane_components(
            self.input_mode, magnitude=self.magnitude, angle=self.angle, rise=self.rise, run=self.run
        )
        return x, 0.0, z

    def get_unit_symbol(self, category: str) -> str:
        ifc_file = tool.Ifc.get()
        force_unit = ifcopenshell.util.unit.get_project_unit(ifc_file, "FORCEUNIT")
        length_unit = ifcopenshell.util.unit.get_project_unit(ifc_file, "LENGTHUNIT")
        symbol = ifcopenshell.util.unit.get_unit_symbol(force_unit) if force_unit else "N"
        length = ifcopenshell.util.unit.get_unit_symbol(length_unit) if length_unit else "m"
        if category == "IfcStructuralCurveMember":
            return f"{symbol}/{length}"
        elif category == "IfcStructuralSurfaceMember":
            return f"{symbol}/{length}2"
        return symbol

    def get_default_load_name(self, category: str) -> str:
        unit = self.get_unit_symbol(category)
        if self.input_mode == "ANGLE":
            return f"{self.magnitude:g} {unit} at {self.angle:g} deg"
        elif self.input_mode == "SLOPE":
            return f"{self.magnitude:g} {unit} at {self.rise:g}:{self.run:g}"
        values = [f"{axis} {value:g}" for axis, value in zip("XYZ", self.get_components()) if value]
        return f"{', '.join(values) or '0'} {unit}"

    def draw(self, context):
        category, elements = self.get_targets(context)
        layout = self.layout
        layout.prop(self, "load_group")
        if self.load_group == "0":
            layout.prop(self, "new_load_case_name")
        layout.row().prop(self, "input_mode", expand=True)
        if self.input_mode == "COMPONENTS":
            for prop in ("x", "y", "z"):
                layout.prop(self, prop)
            if category == "IfcStructuralPointConnection":
                for prop in ("moment_x", "moment_y", "moment_z"):
                    layout.prop(self, prop)
        else:
            layout.prop(self, "magnitude")
            if self.input_mode == "ANGLE":
                layout.prop(self, "angle")
            else:
                row = layout.row(align=True)
                row.prop(self, "rise")
                row.prop(self, "run")
            x, _, z = self.get_components()
            unit = self.get_unit_symbol(category) if category else ""
            layout.label(text=f"X = {x:.4f}   Z = {z:.4f} {unit}", icon="ORIENTATION_GLOBAL")
        layout.prop(self, "load_name")
        if category:
            layout.label(text=f"Applies to {len(elements)} {category[3:]}", icon="INFO")

    def _execute(self, context):
        category, elements = self.get_targets(context)
        if not category:
            self.report({"ERROR"}, "Select point connections, curve members or surface members, but only one kind.")
            return {"CANCELLED"}
        ifc_file = tool.Ifc.get()
        if self.load_group in ("", "0"):
            group = ifcopenshell.api.structural.add_structural_load_case(
                ifc_file, name=self.new_load_case_name or "Load Case"
            )
            tool.Structural.assign_to_current_structural_analysis_model(group)
        else:
            group = ifc_file.by_id(int(self.load_group))

        load_class, activity_class, force_attributes, moment_attributes = APPLY_LOAD_CLASSES[category]
        values = self.get_components()
        if self.input_mode == "COMPONENTS":
            values += (self.moment_x, self.moment_y, self.moment_z)
        attributes = {name: value or None for name, value in zip(force_attributes + moment_attributes, values)}
        load = ifcopenshell.api.structural.add_structural_load(
            ifc_file, name=self.load_name or self.get_default_load_name(category), ifc_class=load_class
        )
        ifcopenshell.api.structural.edit_structural_load(ifc_file, structural_load=load, attributes=attributes)
        activities = [
            ifcopenshell.api.structural.add_structural_activity(
                ifc_file, ifc_class=activity_class, applied_load=load, structural_member=element
            )
            for element in elements
        ]
        ifcopenshell.api.group.assign_group(ifc_file, products=activities, group=group)
        return {"FINISHED"}


class LoadStructuralLoads(bpy.types.Operator):
    bl_idname = "bim.load_structural_loads"
    bl_label = "Load Structural Loads"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        self.file = tool.Ifc.get()
        props = tool.Structural.get_structural_props()
        props.structural_loads.clear()
        loads = tool.Ifc.get().by_type("IfcStructuralLoad")
        if props.filtered_structural_loads:
            names = [structural_load.Name or "Unnamed" for structural_load in loads]
            for structural_load in loads:
                if (
                    names.count(structural_load.Name or "Unnamed") > 1
                    and self.file.get_total_inverses(structural_load) < 2
                ):
                    continue
                new = props.structural_loads.add()
                new.ifc_definition_id = structural_load.id()
                new.name = structural_load.Name or "Unnamed"
                new.number_of_inverse_references = self.file.get_total_inverses(structural_load)

        else:
            for structural_load in loads:
                new = props.structural_loads.add()
                new.ifc_definition_id = structural_load.id()
                new.name = structural_load.Name or "Unnamed"
                new.number_of_inverse_references = self.file.get_total_inverses(structural_load)
        props.is_editing_loads = True
        bpy.ops.bim.disable_editing_structural_load()
        return {"FINISHED"}


class DisableStructuralLoadEditingUI(bpy.types.Operator):
    bl_idname = "bim.disable_structural_load_editing_ui"
    bl_label = "Disable Structural Load Editing UI"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        props = tool.Structural.get_structural_props()
        props.is_editing_loads = False
        return {"FINISHED"}


class AddStructuralLoad(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_structural_load"
    bl_label = "Add Structural Load"
    bl_options = {"REGISTER", "UNDO"}
    ifc_class: bpy.props.StringProperty()

    def _execute(self, context):
        result = ifcopenshell.api.structural.add_structural_load(
            tool.Ifc.get(), name="New Load", ifc_class=self.ifc_class
        )
        bpy.ops.bim.load_structural_loads()
        bpy.ops.bim.enable_editing_structural_load(structural_load=result.id())
        return {"FINISHED"}


class EnableEditingStructuralLoad(bpy.types.Operator):
    bl_idname = "bim.enable_editing_structural_load"
    bl_label = "Enable Editing Structural Load"
    bl_options = {"REGISTER", "UNDO"}
    structural_load: bpy.props.IntProperty()

    def execute(self, context):
        props = tool.Structural.get_structural_props()
        props.structural_load_attributes.clear()
        bonsai.bim.helper.import_attributes(
            tool.Ifc.get().by_id(self.structural_load), props.structural_load_attributes
        )
        props.active_structural_load_id = self.structural_load
        return {"FINISHED"}


class DisableEditingStructuralLoad(bpy.types.Operator):
    bl_idname = "bim.disable_editing_structural_load"
    bl_label = "Disable Editing Structural Load"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        props = tool.Structural.get_structural_props()
        props.active_structural_load_id = 0
        return {"FINISHED"}


class RemoveStructuralLoad(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.remove_structural_load"
    bl_label = "Remove Structural Load"
    bl_options = {"REGISTER", "UNDO"}
    structural_load: bpy.props.IntProperty()

    def _execute(self, context):
        self.file = tool.Ifc.get()
        ifcopenshell.api.structural.remove_structural_load(
            self.file,
            structural_load=self.file.by_id(self.structural_load),
        )
        bpy.ops.bim.load_structural_loads()
        return {"FINISHED"}


class EditStructuralLoad(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.edit_structural_load"
    bl_label = "Edit Structural Load"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        props = tool.Structural.get_structural_props()
        attributes = bonsai.bim.helper.export_attributes(props.structural_load_attributes)
        self.file = tool.Ifc.get()
        ifcopenshell.api.structural.edit_structural_load(
            self.file,
            structural_load=self.file.by_id(props.active_structural_load_id),
            attributes=attributes,
        )
        bpy.ops.bim.load_structural_loads()
        return {"FINISHED"}


class ToggleFilterStructuralLoads(bpy.types.Operator):
    bl_idname = "bim.toggle_filter_structural_loads"
    bl_label = "Toggle Filter Structural Loads"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        props = tool.Structural.get_structural_props()
        props.filtered_structural_loads = not props.filtered_structural_loads
        bpy.ops.bim.load_structural_loads()
        return {"FINISHED"}


class LoadBoundaryConditions(bpy.types.Operator):
    bl_idname = "bim.load_boundary_conditions"
    bl_label = "Load Boundary Conditions"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        self.file = tool.Ifc.get()
        props = tool.Structural.get_structural_props()
        props.boundary_conditions.clear()
        conditions = tool.Ifc.get().by_type("IfcBoundaryCondition")
        if props.filtered_boundary_conditions:
            names = [boundary_condition.Name or "Unnamed" for boundary_condition in conditions]
            for boundary_condition in conditions:
                if (
                    names.count(boundary_condition["Name"] or "Unnamed") > 1
                    and self.file.get_total_inverses(boundary_condition) < 2
                ):
                    continue
                new = props.boundary_conditions.add()
                new.ifc_definition_id = boundary_condition.id()
                new.name = boundary_condition.Name or "Unnamed"
                new.number_of_inverse_references = self.file.get_total_inverses(boundary_condition)

        else:
            for boundary_condition in conditions:
                new = props.boundary_conditions.add()
                new.ifc_definition_id = boundary_condition.id()
                new.name = boundary_condition.Name or "Unnamed"
                new.number_of_inverse_references = self.file.get_total_inverses(boundary_condition)
        props.is_editing_boundary_conditions = True
        bpy.ops.bim.disable_editing_boundary_condition()
        return {"FINISHED"}


class ToggleFilterBoundaryConditions(bpy.types.Operator):
    bl_idname = "bim.toggle_filter_boundary_conditions"
    bl_label = "Toggle Filter Boundary Conditions"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        props = tool.Structural.get_structural_props()
        props.filtered_boundary_conditions = not props.filtered_boundary_conditions
        bpy.ops.bim.load_boundary_conditions()
        return {"FINISHED"}


class DisableBoundaryConditionEditingUI(bpy.types.Operator):
    bl_idname = "bim.disable_boundary_condition_editing_ui"
    bl_label = "Disable Boundary Condition Editing UI"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        props = tool.Structural.get_structural_props()
        props.is_editing_boundary_conditions = False
        return {"FINISHED"}


class AddBoundaryCondition(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_boundary_condition"
    bl_label = "Add Boundary Condition"
    bl_options = {"REGISTER", "UNDO"}
    ifc_class: bpy.props.StringProperty()

    def _execute(self, context):
        result = ifcopenshell.api.structural.add_structural_boundary_condition(
            tool.Ifc.get(),
            name="New Load",
            ifc_class=self.ifc_class,
        )
        bpy.ops.bim.load_boundary_conditions()
        bpy.ops.bim.enable_editing_boundary_condition(boundary_condition=result.id())
        return {"FINISHED"}


class EnableEditingBoundaryCondition(bpy.types.Operator):
    bl_idname = "bim.enable_editing_boundary_condition"
    bl_label = "Enable Editing Boundary Condition"
    bl_options = {"REGISTER", "UNDO"}
    boundary_condition: bpy.props.IntProperty()

    if TYPE_CHECKING:
        boundary_condition: int

    def execute(self, context):
        boundary_condition = tool.Ifc.get().by_id(self.boundary_condition)
        props = tool.Structural.get_structural_props()
        tool.Structural.import_boundary_condition_attributes(boundary_condition, props)
        props.active_boundary_condition_id = self.boundary_condition
        return {"FINISHED"}


class DisableEditingBoundaryCondition(bpy.types.Operator):
    bl_idname = "bim.disable_editing_boundary_condition"
    bl_label = "Disable Editing Boundary Condition"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        props = tool.Structural.get_structural_props()
        props.active_boundary_condition_id = 0
        return {"FINISHED"}


class RemoveBoundaryCondition(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.remove_boundary_condition"
    bl_label = "Remove Boundary Condition"
    bl_options = {"REGISTER", "UNDO"}
    boundary_condition: bpy.props.IntProperty()

    def _execute(self, context):
        self.file = tool.Ifc.get()
        ifcopenshell.api.structural.remove_structural_boundary_condition(
            self.file,
            boundary_condition=self.file.by_id(self.boundary_condition),
        )
        bpy.ops.bim.load_boundary_conditions()
        return {"FINISHED"}


class EditBoundaryCondition(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.edit_boundary_condition"
    bl_label = "Edit Boundary Condition"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        props = tool.Structural.get_structural_props()
        ifc_file = tool.Ifc.get()
        condition = ifc_file.by_id(props.active_boundary_condition_id)
        tool.Structural.export_and_apply_boundary_condition_attributes(condition, props)
        bpy.ops.bim.load_boundary_conditions()
        return {"FINISHED"}
