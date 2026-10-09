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

import math
import re
from math import degrees
from typing import TYPE_CHECKING, Literal, Union

import bpy
import ifcopenshell.api.group
import ifcopenshell.api.structural
import ifcopenshell.util.unit
from bpy_extras.view3d_utils import location_3d_to_region_2d
from mathutils import Matrix, Vector

import bonsai.bim.helper
import bonsai.core.structural as core
import bonsai.tool as tool
from bonsai.bim.module.structural.data import StructuralAnalysisModelsData, StructuralLoadCasesData
from bonsai.bim.module.structural.decorator import LoadsDecorator
from bonsai.bim.module.structural.load_decoration_data import ShaderInfo


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
        if event.type == "MOUSEMOVE":
            hovered = None
            if view := self.get_view_under_mouse(context, event):
                area, region, rv3d = view
                hovered = LoadsDecorator.pick(region, rv3d, event.mouse_x - region.x, event.mouse_y - region.y)
            if hovered is not LoadsDecorator.hovered:
                LoadsDecorator.hovered = hovered
                tool.Blender.update_all_viewports(context)
        elif event.type == "LEFTMOUSE" and event.value == "PRESS" and LoadsDecorator.hovered:
            if view := self.get_view_under_mouse(context, event):
                area, region, rv3d = view
                hovered = LoadsDecorator.hovered
                # Dialogs open at the cursor, so move it beside the diagram for the dialog not to cover it.
                self.move_cursor_beside_loads(context, region, rv3d, hovered)
                with context.temp_override(window=context.window, area=area, region=region):
                    if hovered.get("activities"):
                        activities = ",".join(str(i) for i in hovered["activities"])
                        bpy.ops.bim.edit_structural_resultant("INVOKE_DEFAULT", activities=activities)
                    else:
                        bpy.ops.bim.edit_structural_load_values("INVOKE_DEFAULT", activity=hovered["activity"])
                return {"RUNNING_MODAL"}
        return {"PASS_THROUGH"}

    def move_cursor_beside_loads(
        self, context: bpy.types.Context, region: bpy.types.Region, rv3d: bpy.types.RegionView3D, hovered: dict
    ) -> None:
        points = [p for pickable in LoadsDecorator.pickables for p in (pickable["tail"], pickable["tip"])]
        points += [info["position"] for info in LoadsDecorator.text_info]
        projected = [location_3d_to_region_2d(region, rv3d, Vector(p)) for p in points]
        projected = [p for p in projected if p is not None]
        if not projected:
            return
        # Work in window coordinates: the dialog may cover other editors, just not the diagram.
        xs = [region.x + p.x for p in projected]
        ys = [region.y + p.y for p in projected]
        left, right, bottom, top = min(xs), max(xs), min(ys), max(ys)
        window_width, window_height = context.window.width, context.window.height
        # The dialog's size in pixels: dialogs are sized in UI units, which follow the display and resolution scale.
        scale = context.preferences.system.ui_scale
        width, height, margin = 420 * scale, 400 * scale, 20 * scale
        level_y, level_x = (bottom + top) / 2, (left + right) / 2
        # A dialog opens centred on the cursor, so put the cursor half a dialog beyond the diagram's edge.
        candidates = [
            (window_width - right, width, right + margin + width / 2, level_y),
            (left, width, left - margin - width / 2, level_y),
            (bottom, height, level_x, bottom - margin - height / 2),
            (window_height - top, height, level_x, top + margin + height / 2),
        ]
        fitting = [c for c in candidates if c[0] >= c[1] + margin]
        # Failing a side with room, take the one with most, which covers the least of the diagram.
        _, _, x, y = fitting[0] if fitting else max(candidates, key=lambda c: c[0] / c[1])
        # Better, open it on the side of the diagram where the clicked arrow is, just clear of the diagram.
        middle = location_3d_to_region_2d(region, rv3d, (Vector(hovered["tail"]) + Vector(hovered["tip"])) / 2)
        if middle is not None:
            direction = Vector((region.x + middle.x - level_x, region.y + middle.y - level_y))
            if direction.length > 1:
                direction.normalize()
                clear_x = ((right - left) / 2 + margin + width / 2) / abs(direction.x) if direction.x else float("inf")
                clear_y = ((top - bottom) / 2 + margin + height / 2) / abs(direction.y) if direction.y else float("inf")
                distance = min(clear_x, clear_y)
                x, y = level_x + direction.x * distance, level_y + direction.y * distance
        x = min(max(x, width / 2), window_width - width / 2)
        y = min(max(y, height / 2), window_height - height / 2)
        context.window.cursor_warp(int(x), int(y))

    def get_view_under_mouse(
        self, context: bpy.types.Context, event: bpy.types.Event
    ) -> Union[tuple[bpy.types.Area, bpy.types.Region, bpy.types.RegionView3D], None]:
        for area in context.window.screen.areas:
            if area.type != "VIEW_3D":
                continue
            for region in area.regions:
                if (
                    region.type == "WINDOW"
                    and region.x <= event.mouse_x < region.x + region.width
                    and region.y <= event.mouse_y < region.y + region.height
                ):
                    return area, region, area.spaces.active.region_3d

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
    bl_description = "Assign the load case to this structural analysis model"
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
    bl_description = "Unassign the load case from this structural analysis model"
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
    bl_description = "Edit the load case, and show its loads and load groups"
    bl_options = {"REGISTER", "UNDO"}
    load_case: bpy.props.IntProperty()

    def execute(self, context):
        self.props = tool.Structural.get_structural_props()
        self.props.active_load_case_id = self.load_case
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
    bl_description = "Show the loads applied in this load case or load group"
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
                new.name = StructuralLoadCasesData.activity_name(activity)
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
        if props.active_load_group_id and props.load_group_editing_type == "ACTIVITY":
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

# Matches the load names generated by StructuralForceInput.get_default_load_name.
_NUMBER = r"-?[\d.]+(?:e[-+]?\d+)?"
_DIRECTION = r"(?: ((?:up|down)-(?:left|right)))?"
DEFAULT_LOAD_NAME = re.compile(
    rf"^(?:{_NUMBER} \S+ at {_NUMBER} deg{_DIRECTION}|{_NUMBER} \S+ at {_NUMBER}:{_NUMBER}{_DIRECTION}"
    rf"|(?:[XYZ] {_NUMBER}(?:, [XYZ] {_NUMBER})*|0) \S+)$"
)
SLOPE_LOAD_NAME = re.compile(rf"^{_NUMBER} \S+ at ({_NUMBER}):({_NUMBER}){_DIRECTION}$")
ANGLE_LOAD_NAME = re.compile(rf"^{_NUMBER} \S+ at ({_NUMBER}) deg{_DIRECTION}$")
DIRECTION_NAMES = {"UP_RIGHT": "", "UP_LEFT": " up-left", "DOWN_LEFT": " down-left", "DOWN_RIGHT": " down-right"}


def get_load_category(load: ifcopenshell.entity_instance) -> Union[str, None]:
    """Get the kind of structural item a load applies to, if it is a force the load dialogs support."""
    return next((c for c, (load_class, *_) in APPLY_LOAD_CLASSES.items() if load.is_a(load_class)), None)


# Property update callbacks get the operator's properties, not the operator, so the name helpers are functions.
def get_force_components(props: "StructuralForceInput") -> tuple[float, float, float]:
    if props.input_mode == "COMPONENTS":
        return props.x, props.y, props.z
    x, z = tool.Structural.get_in_plane_components(
        props.input_mode,
        magnitude=props.magnitude,
        angle=props.angle,
        rise=props.rise,
        run=props.run,
        direction=props.direction,
    )
    return x, 0.0, z


def get_load_unit_symbol(category: str) -> str:
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


def get_default_load_name(props: "StructuralForceInput", category: str) -> str:
    unit = get_load_unit_symbol(category)
    direction = DIRECTION_NAMES[props.direction]
    if props.input_mode == "ANGLE":
        return f"{props.magnitude:g} {unit} at {props.angle:g} deg{direction}"
    elif props.input_mode == "SLOPE":
        return f"{props.magnitude:g} {unit} at {props.rise:g}:{props.run:g}{direction}"
    values = [f"{axis} {value:g}" for axis, value in zip("XYZ", get_force_components(props)) if value]
    return f"{', '.join(values) or '0'} {unit}"


def get_load_attributes(props: "StructuralForceInput", category: str) -> dict[str, Union[float, None]]:
    _, _, force_attributes, moment_attributes = APPLY_LOAD_CLASSES[category]
    values = get_force_components(props)
    if props.input_mode == "COMPONENTS":
        values += (props.moment_x, props.moment_y, props.moment_z)
    else:
        values += (0.0, 0.0, 0.0)
    return {name: value or None for name, value in zip(force_attributes + moment_attributes, values)}


def update_force_inputs(self: "StructuralForceInput", context: bpy.types.Context) -> None:
    # Keep a generated name in step with the values, but never overwrite a name the user typed.
    if self.load_category and (not self.load_name or DEFAULT_LOAD_NAME.match(self.load_name)):
        self.load_name = get_default_load_name(self, self.load_category)
    # Show the load being edited with the values in the dialog until it is confirmed or cancelled.
    if self.preview_load and self.load_category and LoadsDecorator.is_installed:
        ShaderInfo.preview = {self.preview_load: get_load_attributes(self, self.load_category)}
        LoadsDecorator.update()
        tool.Blender.update_all_viewports(context)
    elif getattr(self, "is_previewing", False) and LoadsDecorator.is_installed:
        forces, _ = solve_resultant(self)
        ShaderInfo.preview = {load.id(): get_force_attributes(load, force) for load, force in (forces or {}).items()}
        LoadsDecorator.update()
        tool.Blender.update_all_viewports(context)


def get_resultant_activities(props: "EditStructuralResultant") -> list[ifcopenshell.entity_instance]:
    ifc_file = tool.Ifc.get()
    return [ifc_file.by_id(int(i)) for i in props.activities.split(",") if i]


def get_force(load: ifcopenshell.entity_instance) -> tuple[float, float, float]:
    return tuple(getattr(load, a) or 0.0 for a in ("ForceX", "ForceY", "ForceZ"))


def get_force_attributes(load: ifcopenshell.entity_instance, force: tuple) -> dict[str, Union[float, None]]:
    """The attributes of a single force load with new force components and its own moments"""
    attributes = {a: getattr(load, a) for a in ("MomentX", "MomentY", "MomentZ")}
    attributes.update({a: value or None for a, value in zip(("ForceX", "ForceY", "ForceZ"), force)})
    return attributes


def get_adjusted_indices(props: "EditStructuralResultant") -> list[int]:
    count = len(get_resultant_activities(props))
    return [0, 1] if count == 2 else [i for i in range(min(count, 32)) if props.adjust[i]]


def solve_resultant(
    props: "EditStructuralResultant",
) -> tuple[Union[dict[ifcopenshell.entity_instance, tuple], None], str]:
    """Get the loads to change, and their new forces, for the target resultant, or why it cannot be made.

    Two of the forces keep their directions and change magnitude; the others are kept.
    """
    loads = [activity.AppliedLoad for activity in get_resultant_activities(props)]
    adjusted = get_adjusted_indices(props)
    if len(adjusted) != 2:
        return None, "Tick exactly two forces to adjust"
    forces = [get_force(load) for load in loads]
    kept = [forces[i] for i in range(len(loads)) if i not in adjusted]
    target = [t - sum(force[k] for force in kept) for k, t in enumerate(get_force_components(props))]
    directions = []
    for i in adjusted:
        length = math.hypot(*forces[i])
        if not length:
            return None, f"{loads[i].Name or 'Unnamed'} has no direction to keep"
        directions.append(tuple(c / length for c in forces[i]))
    magnitudes = tool.Structural.solve_two_force_magnitudes(target, directions[0], directions[1])
    if magnitudes is None:
        return None, "The two forces adjusted are parallel, so they cannot make this resultant"
    return {
        loads[i]: tuple(magnitude * c for c in direction)
        for i, magnitude, direction in zip(adjusted, magnitudes, directions)
    }, ""


def get_force_name(force: tuple[float, float, float], unit: str) -> str:
    """A generated name for a force, by its angle from the nearest horizontal if it lies in the X-Z plane"""
    x, y, z = force
    if y:
        values = [f"{axis} {value:g}" for axis, value in zip("XYZ", force) if value]
        return f"{', '.join(values) or '0'} {unit}"
    direction = DIRECTION_NAMES[f"{'UP' if z >= 0 else 'DOWN'}_{'RIGHT' if x >= 0 else 'LEFT'}"]
    angle = math.degrees(math.atan2(abs(z), abs(x)))
    return f"{math.hypot(x, z):g} {unit} at {angle:g} deg{direction}"


def clear_load_preview(context: bpy.types.Context) -> None:
    if ShaderInfo.preview:
        ShaderInfo.preview = {}
        if LoadsDecorator.is_installed:
            LoadsDecorator.update()
            tool.Blender.update_all_viewports(context)


class StructuralForceInput:
    """Force inputs shared by the Apply Load and Edit Load dialogs."""

    load_category: bpy.props.StringProperty(options={"HIDDEN", "SKIP_SAVE"})
    preview_load: bpy.props.IntProperty(options={"HIDDEN", "SKIP_SAVE"})
    input_mode: bpy.props.EnumProperty(
        name="Input",
        items=[
            ("COMPONENTS", "Components", "X, Y and Z components"),
            ("ANGLE", "Angle", "Magnitude and angle above the horizontal, in the X-Z plane"),
            ("SLOPE", "Slope", "Magnitude and rise over run, in the X-Z plane"),
        ],
        update=update_force_inputs,
    )
    direction: bpy.props.EnumProperty(
        name="Direction",
        description="The quadrant the force points into; the angle or slope is measured from the horizontal",
        items=[
            ("UP_RIGHT", "Up-Right", "Measured up from +X"),
            ("UP_LEFT", "Up-Left", "Measured up from -X"),
            ("DOWN_LEFT", "Down-Left", "Measured down from -X"),
            ("DOWN_RIGHT", "Down-Right", "Measured down from +X"),
        ],
        update=update_force_inputs,
    )
    magnitude: bpy.props.FloatProperty(name="Magnitude", update=update_force_inputs)
    angle: bpy.props.FloatProperty(name="Angle", description="Degrees from +X towards +Z", update=update_force_inputs)
    rise: bpy.props.FloatProperty(name="Rise", description="Towards +Z", default=1.0, update=update_force_inputs)
    run: bpy.props.FloatProperty(name="Run", description="Towards +X", default=1.0, update=update_force_inputs)
    x: bpy.props.FloatProperty(name="X", update=update_force_inputs)
    y: bpy.props.FloatProperty(name="Y", update=update_force_inputs)
    z: bpy.props.FloatProperty(name="Z", update=update_force_inputs)
    moment_x: bpy.props.FloatProperty(name="Moment X", update=update_force_inputs)
    moment_y: bpy.props.FloatProperty(name="Moment Y", update=update_force_inputs)
    moment_z: bpy.props.FloatProperty(name="Moment Z", update=update_force_inputs)
    load_name: bpy.props.StringProperty(name="Load Name")

    def get_components(self) -> tuple[float, float, float]:
        return get_force_components(self)

    def get_load_attributes(self, category: str) -> dict[str, Union[float, None]]:
        return get_load_attributes(self, category)

    def set_in_plane_inputs(self, x: float, z: float) -> None:
        """Fill the angle and slope inputs from in-plane components, measured from the nearest horizontal"""
        self.direction = f"{'UP' if z >= 0 else 'DOWN'}_{'RIGHT' if x >= 0 else 'LEFT'}"
        self.magnitude = math.hypot(x, z)
        self.angle = math.degrees(math.atan2(abs(z), abs(x)))
        self.rise, self.run = tool.Structural.get_simple_slope(abs(x), abs(z))

    def get_unit_symbol(self, category: str) -> str:
        return get_load_unit_symbol(category)

    def get_default_load_name(self, category: str) -> str:
        return get_default_load_name(self, category)

    def draw_force_inputs(self, layout: bpy.types.UILayout, category: Union[str, None], show_name: bool = True) -> None:
        layout.row().prop(self, "input_mode", expand=True)
        if self.input_mode == "COMPONENTS":
            for prop in ("x", "y", "z"):
                layout.prop(self, prop)
            if category in ("IfcStructuralPointConnection", "IfcStructuralCurveMember"):
                for prop in ("moment_x", "moment_y", "moment_z"):
                    layout.prop(self, prop)
        else:
            layout.row().prop(self, "direction", expand=True)
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
        if show_name:
            layout.prop(self, "load_name")

    def get_load_name(self, category: str) -> str:
        return self.load_name or self.get_default_load_name(category)


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


class ApplyStructuralLoad(bpy.types.Operator, tool.Ifc.Operator, StructuralForceInput):
    bl_idname = "bim.apply_structural_load"
    bl_label = "Apply Structural Load"
    bl_description = "Apply a force to the selected structural point connections, curve members or surface members"
    bl_options = {"REGISTER", "UNDO"}
    load_group: bpy.props.EnumProperty(name="Load Case", items=get_apply_load_groups)
    new_load_case_name: bpy.props.StringProperty(name="New Load Case", default="Load Case")

    def get_targets(self, context: bpy.types.Context) -> tuple[Union[str, None], list[ifcopenshell.entity_instance]]:
        elements = [e for o in context.selected_objects if (e := tool.Ifc.get_entity(o))]
        categories = {c for e in elements for c in APPLY_LOAD_CLASSES if e.is_a(c)}
        if len(categories) != 1:
            return None, []
        category = categories.pop()
        return category, [e for e in elements if e.is_a(category)]

    def invoke(self, context, event):
        if not (category := self.get_targets(context)[0]):
            self.report({"ERROR"}, "Select point connections, curve members or surface members, but only one kind.")
            return {"CANCELLED"}
        self.load_category = category
        self.load_name = self.get_default_load_name(category)
        return context.window_manager.invoke_props_dialog(self, width=350)

    def draw(self, context):
        category, elements = self.get_targets(context)
        layout = self.layout
        layout.prop(self, "load_group")
        if self.load_group == "0":
            layout.prop(self, "new_load_case_name")
        self.draw_force_inputs(layout, category)
        if category:
            layout.label(text=f"Applies to {len(elements)} {category[3:]}", icon="INFO")
        if not tool.Ifc.get().by_type("IfcStructuralAnalysisModel"):
            layout.label(text="A structural analysis model will be created", icon="INFO")
        elif not tool.Structural.get_current_structural_analysis_model():
            layout.label(text="No current analysis model: choose one to assign the load case to", icon="ERROR")

    def _execute(self, context):
        category, elements = self.get_targets(context)
        if not category:
            self.report({"ERROR"}, "Select point connections, curve members or surface members, but only one kind.")
            return {"CANCELLED"}
        ifc_file = tool.Ifc.get()
        if not ifc_file.by_type("IfcStructuralAnalysisModel"):
            # Loads only take part in an analysis through a model, so start one.
            model = core.add_structural_analysis_model(tool.Ifc, tool.Structural)
            project = ifc_file.by_type("IfcProject")[0]
            ifcopenshell.api.structural.edit_structural_analysis_model(
                ifc_file, structural_analysis_model=model, attributes={"Name": project.Name or "Structural Analysis"}
            )
        for element in elements:
            # Items made before there was a current model belong to none yet.
            if not any(
                rel.RelatingGroup and rel.RelatingGroup.is_a("IfcStructuralAnalysisModel")
                for rel in element.HasAssignments
                if rel.is_a("IfcRelAssignsToGroup")
            ):
                tool.Structural.assign_to_current_structural_analysis_model(element)
        if self.load_group in ("", "0"):
            group = ifcopenshell.api.structural.add_structural_load_case(
                ifc_file, name=self.new_load_case_name or "Load Case"
            )
        else:
            group = ifc_file.by_id(int(self.load_group))
        if group.is_a("IfcStructuralLoadCase") and not group.LoadGroupFor:
            tool.Structural.assign_to_current_structural_analysis_model(group)

        load_class, activity_class, _, _ = APPLY_LOAD_CLASSES[category]
        load = ifcopenshell.api.structural.add_structural_load(
            ifc_file, name=self.get_load_name(category), ifc_class=load_class
        )
        ifcopenshell.api.structural.edit_structural_load(
            ifc_file, structural_load=load, attributes=self.get_load_attributes(category)
        )
        activities = [
            ifcopenshell.api.structural.add_structural_activity(
                ifc_file, ifc_class=activity_class, applied_load=load, structural_member=element
            )
            for element in elements
        ]
        ifcopenshell.api.group.assign_group(ifc_file, products=activities, group=group)
        return {"FINISHED"}


edit_load_group_items: list[tuple[str, str, str]] = []


def get_edit_load_groups(self, context: bpy.types.Context) -> list[tuple[str, str, str]]:
    global edit_load_group_items
    edit_load_group_items = []
    listed = set()
    for load_case in tool.Ifc.get().by_type("IfcStructuralLoadCase"):
        edit_load_group_items.append((str(load_case.id()), load_case.Name or "Unnamed", load_case.is_a()))
        listed.add(load_case)
        for rel in load_case.IsGroupedBy:
            for group in rel.RelatedObjects:
                if group.is_a("IfcStructuralLoadGroup") and group not in listed:
                    edit_load_group_items.append((str(group.id()), f"    {group.Name or 'Unnamed'}", group.is_a()))
                    listed.add(group)
    for group in tool.Ifc.get().by_type("IfcStructuralLoadGroup"):
        if group not in listed:
            edit_load_group_items.append((str(group.id()), group.Name or "Unnamed", group.is_a()))
    edit_load_group_items.append(("0", "New Load Case", "Create a new load case in the current model"))
    return edit_load_group_items


def get_activity_load_groups(activity: ifcopenshell.entity_instance) -> list[ifcopenshell.entity_instance]:
    return [
        rel.RelatingGroup
        for rel in activity.HasAssignments
        if rel.is_a("IfcRelAssignsToGroup") and rel.RelatingGroup and rel.RelatingGroup.is_a("IfcStructuralLoadGroup")
    ]


class EditStructuralLoadValues(bpy.types.Operator, tool.Ifc.Operator, StructuralForceInput):
    bl_idname = "bim.edit_structural_load_values"
    bl_label = "Edit Structural Load"
    bl_description = "Edit the force of a structural load"
    bl_options = {"REGISTER", "UNDO"}
    structural_load: bpy.props.IntProperty(options={"SKIP_SAVE"})
    activity: bpy.props.IntProperty(description="Edit the load applied by this activity instead", options={"SKIP_SAVE"})
    load_group: bpy.props.EnumProperty(name="Load Case", items=get_edit_load_groups, options={"SKIP_SAVE"})
    new_load_case_name: bpy.props.StringProperty(name="New Load Case", default="Load Case")

    def get_load(self) -> ifcopenshell.entity_instance:
        ifc_file = tool.Ifc.get()
        if self.activity:
            return ifc_file.by_id(self.activity).AppliedLoad
        return ifc_file.by_id(self.structural_load)

    def invoke(self, context, event):
        load = self.get_load()
        if not (category := get_load_category(load)):
            # Only forces have a dialog; other loads use the attribute editor.
            return bpy.ops.bim.enable_editing_structural_load(structural_load=load.id())
        self.load_category = category
        _, _, force_attributes, moment_attributes = APPLY_LOAD_CLASSES[category]
        self.x, self.y, self.z = (getattr(load, a) or 0.0 for a in force_attributes)
        self.moment_x, self.moment_y, self.moment_z = (
            (getattr(load, a) or 0.0 for a in moment_attributes) if moment_attributes else (0.0, 0.0, 0.0)
        )
        # IFC only stores components, so derive the in-plane inputs from them, from the nearest horizontal...
        x, y, z = (getattr(load, a) or 0.0 for a in force_attributes)
        self.set_in_plane_inputs(x, z)
        self.input_mode = "COMPONENTS"
        # ... but reopen in the way the load was entered if its generated name records it and still fits.
        name = load.Name or ""
        if not y and (match := SLOPE_LOAD_NAME.match(name)):
            rise, run = float(match[1]), float(match[2])
            direction = match[3].upper().replace("-", "_") if match[3] else "UP_RIGHT"
            if self.fits(x, z, "SLOPE", rise=rise, run=run, direction=direction):
                self.input_mode, self.rise, self.run, self.direction = "SLOPE", rise, run, direction
        elif not y and (match := ANGLE_LOAD_NAME.match(name)):
            angle = float(match[1])
            direction = match[2].upper().replace("-", "_") if match[2] else "UP_RIGHT"
            if self.fits(x, z, "ANGLE", angle=angle, direction=direction):
                self.input_mode, self.angle, self.direction = "ANGLE", angle, direction
        self.load_name = name
        if (activities := self.get_movable_activities()) and (groups := get_activity_load_groups(activities[0])):
            self.load_group = str(groups[0].id())
        # Set last, so that filling in the values above does not start a preview.
        self.preview_load = load.id()
        return context.window_manager.invoke_props_dialog(self, width=350)

    def fits(
        self,
        x: float,
        z: float,
        mode: str,
        angle: float = 0.0,
        rise: float = 0.0,
        run: float = 0.0,
        direction: str = "UP_RIGHT",
    ) -> bool:
        """Whether an angle or slope gives the direction of the components x and z"""
        fx, fz = tool.Structural.get_in_plane_components(
            mode, magnitude=math.hypot(x, z), angle=angle, rise=rise, run=run, direction=direction
        )
        tolerance = 1e-4 * math.hypot(x, z)
        return math.isclose(fx, x, abs_tol=tolerance) and math.isclose(fz, z, abs_tol=tolerance)

    def draw(self, context):
        load = self.get_load()
        category = get_load_category(load)
        layout = self.layout
        if self.get_movable_activities():
            layout.prop(self, "load_group")
            if self.load_group == "0":
                layout.prop(self, "new_load_case_name")
        users = [i for i in tool.Ifc.get().get_inverse(load) if i.is_a("IfcStructuralActivity")]
        layout.label(text=f"Used by {len(users)} applied load{'s' if len(users) != 1 else ''}", icon="INFO")
        load_cases = {g for user in users for g in get_activity_load_groups(user)}
        if len(load_cases) > 1 and not self.get_movable_activities():
            layout.label(text=f"Used in {len(load_cases)} load cases: move one from its applied load", icon="INFO")
        self.draw_force_inputs(layout, category)
        if self.input_mode != "COMPONENTS" and (self.y or self.moment_x or self.moment_y or self.moment_z):
            layout.label(text="Y and moments will be set to zero", icon="ERROR")

    def cancel(self, context):
        clear_load_preview(context)

    def _execute(self, context):
        ShaderInfo.preview = {}  # The edit below refreshes the shown loads.
        load = self.get_load()
        category = get_load_category(load)
        attributes = self.get_load_attributes(category)
        attributes["Name"] = self.get_load_name(category)
        ifc_file = tool.Ifc.get()
        ifcopenshell.api.structural.edit_structural_load(ifc_file, structural_load=load, attributes=attributes)
        activities = self.get_movable_activities()
        if activities and (target := self.get_target_load_group(ifc_file)):
            for activity in activities:
                self.move_activity(ifc_file, activity, target)
        if tool.Structural.get_structural_props().is_editing_loads:
            bpy.ops.bim.load_structural_loads()
        return {"FINISHED"}

    def get_movable_activities(self) -> list[ifcopenshell.entity_instance]:
        """The applied loads the load case choice moves: the one edited, or every use of the load if they share one"""
        ifc_file = tool.Ifc.get()
        if self.activity:
            return [ifc_file.by_id(self.activity)]
        users = [i for i in ifc_file.get_inverse(self.get_load()) if i.is_a("IfcStructuralActivity")]
        load_cases = {frozenset(get_activity_load_groups(user)) for user in users}
        return users if len(load_cases) == 1 else []

    def get_target_load_group(self, ifc_file: ifcopenshell.file) -> Union[ifcopenshell.entity_instance, None]:
        if self.load_group == "0":
            target = ifcopenshell.api.structural.add_structural_load_case(
                ifc_file, name=self.new_load_case_name or "Load Case"
            )
            tool.Structural.assign_to_current_structural_analysis_model(target)
        elif self.load_group:
            target = ifc_file.by_id(int(self.load_group))
        else:
            return None
        return target

    def move_activity(
        self, ifc_file: ifcopenshell.file, activity: ifcopenshell.entity_instance, target: ifcopenshell.entity_instance
    ) -> None:
        groups = get_activity_load_groups(activity)
        if groups == [target]:
            return
        for group in groups:
            ifcopenshell.api.group.unassign_group(ifc_file, products=[activity], group=group)
        ifcopenshell.api.group.assign_group(ifc_file, products=[activity], group=target)


class EditStructuralResultant(bpy.types.Operator, tool.Ifc.Operator, StructuralForceInput):
    bl_idname = "bim.edit_structural_resultant"
    bl_label = "Edit Resultant"
    bl_description = "Set the resultant of the forces at a point, adjusting the magnitudes of two of them"
    bl_options = {"REGISTER", "UNDO"}
    activities: bpy.props.StringProperty(description="Ids of the activities whose forces add up", options={"SKIP_SAVE"})
    adjust: bpy.props.BoolVectorProperty(
        name="Adjust",
        description="Adjust the magnitude of this force, keeping its direction",
        size=32,
        options={"SKIP_SAVE"},
        update=update_force_inputs,
    )
    is_previewing: bpy.props.BoolProperty(options={"HIDDEN", "SKIP_SAVE"})

    def invoke(self, context, event):
        activities = get_resultant_activities(self)
        if len(activities) < 2:
            return {"CANCELLED"}
        if any(activity.GlobalOrLocal == "LOCAL_COORDS" for activity in activities):
            self.report({"ERROR"}, "Only forces in global coordinates can be adjusted to a resultant.")
            return {"CANCELLED"}
        self.load_category = "IfcStructuralPointConnection"
        x, y, z = (sum(get_force(a.AppliedLoad)[k] for a in activities) for k in range(3))
        self.x, self.y, self.z = x, y, z
        self.set_in_plane_inputs(x, z)
        self.input_mode = "ANGLE" if not y else "COMPONENTS"
        self.adjust = [i < 2 for i in range(32)]
        self.is_previewing = True  # Set last, so that filling in the values above does not start a preview.
        return context.window_manager.invoke_props_dialog(self, width=380)

    def draw(self, context):
        layout = self.layout
        activities = get_resultant_activities(self)
        layout.label(text=f"Resultant of {len(activities)} forces", icon="INFO")
        self.draw_force_inputs(layout, self.load_category, show_name=False)
        unit = self.get_unit_symbol(self.load_category)
        if len(activities) > 2:
            layout.label(text="Adjust two forces, keeping their directions:")
            for i, activity in enumerate(activities[:32]):
                layout.prop(self, "adjust", index=i, text=activity.AppliedLoad.Name or "Unnamed")
        forces, error = solve_resultant(self)
        if error:
            layout.label(text=error, icon="ERROR")
            return
        box = layout.box()
        ifc_file = tool.Ifc.get()
        for load, force in forces.items():
            old = get_force(load)
            new = math.copysign(math.hypot(*force), sum(a * b for a, b in zip(force, old)))
            box.label(text=f"{load.Name or 'Unnamed'}: {math.hypot(*old):.2f} → {abs(new):.2f} {unit}")
            if new < 0:
                box.label(text="  reverses its direction (a pull becomes a push)", icon="ERROR")
            users = [i for i in ifc_file.get_inverse(load) if i.is_a("IfcStructuralActivity")]
            if len(users) > 1:
                box.label(text=f"  also used by {len(users) - 1} other applied load(s)", icon="INFO")

    def cancel(self, context):
        clear_load_preview(context)

    def _execute(self, context):
        ShaderInfo.preview = {}  # The edit below refreshes the shown loads.
        forces, error = solve_resultant(self)
        if error:
            self.report({"ERROR"}, error)
            return {"CANCELLED"}
        ifc_file = tool.Ifc.get()
        unit = self.get_unit_symbol(self.load_category)
        for load, force in forces.items():
            attributes = get_force_attributes(load, force)
            if DEFAULT_LOAD_NAME.match(load.Name or ""):
                attributes["Name"] = get_force_name(force, unit)
            ifcopenshell.api.structural.edit_structural_load(ifc_file, structural_load=load, attributes=attributes)
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
