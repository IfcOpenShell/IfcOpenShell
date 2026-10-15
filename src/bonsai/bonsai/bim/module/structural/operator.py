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
import webbrowser
from collections.abc import Callable
from math import degrees
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal, Union

import bpy
import ifcopenshell.api.group
import ifcopenshell.api.structural
import ifcopenshell.util.unit
import numpy as np
from bpy_extras.view3d_utils import location_3d_to_region_2d
from mathutils import Euler, Matrix, Vector

import bonsai.bim.helper
import bonsai.core.geometry
import bonsai.core.structural as core
import bonsai.tool as tool
from bonsai.bim.module.structural.data import (
    LoadGroupDecorationData,
    StructuralAnalysisModelsData,
    StructuralLoadCasesData,
)
from bonsai.bim.module.structural.decorator import LoadsDecorator
from bonsai.bim.module.structural.load_decoration_data import ShaderInfo

# The eighths of a circle, counter-clockwise from +X, that directions are given in.
EIGHTH_ITEMS = [
    ("Q1", "Q1", "From → (+X), turning up"),
    ("Q2", "Q2", "From ↑ (+Z), turning right"),
    ("Q3", "Q3", "From ↑ (+Z), turning left"),
    ("Q4", "Q4", "From ← (-X), turning up"),
    ("Q5", "Q5", "From ← (-X), turning down"),
    ("Q6", "Q6", "From ↓ (-Z), turning left"),
    ("Q7", "Q7", "From ↓ (-Z), turning right"),
    ("Q8", "Q8", "From → (+X), turning down"),
]


def draw_pinwheel(layout: bpy.types.UILayout, props: bpy.types.Operator, prop: str = "direction") -> None:
    """A pinwheel of the eight directions, counter-clockwise from Q1 just above +X"""
    pinwheel = layout.column(align=True)
    for cells in (
        (None, "Q3", "Q2", None),
        ("Q4", None, None, "Q1"),
        ("Q5", None, None, "Q8"),
        (None, "Q6", "Q7", None),
    ):
        row = pinwheel.row(align=True)
        for cell in cells:
            if cell:
                row.prop_enum(props, prop, cell)
            else:
                row.label(text="")


def draw_with_lock(
    layout: bpy.types.UILayout,
    props: bpy.types.Operator,
    names: tuple[str, ...],
    lock: Union[str, None] = None,
    grey_unknowns: bool = False,
    focus: str = "",
) -> None:
    """Draw values in a row, with a lock beside them if given, greyed out while it shows them unknown.

    :param focus: A value to start editing as the dialog opens, its value selected to type over, as the label
        clicked to open it stands for.
    """
    row = layout.row(align=True)
    values = row.row(align=True)
    values.enabled = not (lock and grey_unknowns and not getattr(props, lock))
    for name in names:
        cell = values.row(align=True) if name == focus else values
        cell.activate_init = name == focus
        cell.prop(props, name)
    if lock:
        row.prop(props, lock, text="", icon="LOCKED" if getattr(props, lock) else "UNLOCKED")


def set_in_plane_direction(props: bpy.types.Operator, x: float, z: float) -> None:
    """Fill a direction input's eighth, angle and slope from in-plane components, measured from the nearest axis"""
    props.direction, props.angle, _, _ = tool.Structural.get_eighth(x, z)
    # A rise is vertical and a run horizontal, whichever axis the angle is from.
    props.rise, props.run = tool.Structural.get_simple_slope(abs(x), abs(z))


def get_direction_input(subject: str, update: Callable, options: set[str], prefix: str = "") -> Any:
    """A mixin of the inputs for a direction in the X-Z plane: an eighth of a circle, and an angle or slope in it.

    :param subject: What points that way, as named in the direction's description.
    :param update: Called when any of them changes.
    :param prefix: Put before each input's name, and that of the input mode they follow and of their drawing
        method, so that a dialog can have a second set, as Edit Load's for where a force acts.
    """
    annotations = {
        f"{prefix}direction": bpy.props.EnumProperty(
            name="Direction",
            description=f"The eighth of a circle {subject} points into; the angle or slope is measured from its axis",
            items=EIGHTH_ITEMS,
            options=options,
            update=update,
        ),
        f"{prefix}angle": bpy.props.FloatProperty(
            name="Angle", description="Degrees from the eighth's axis", options=options, update=update
        ),
        f"{prefix}rise": bpy.props.FloatProperty(
            name="Rise", description="Towards +Z", default=1.0, options=options, update=update
        ),
        f"{prefix}run": bpy.props.FloatProperty(
            name="Run", description="Towards +X", default=1.0, options=options, update=update
        ),
    }

    def draw_direction_inputs(
        self, layout: bpy.types.UILayout, lock: Union[str, None] = None, grey_unknowns: bool = False
    ) -> None:
        """Draw the pinwheel, then the angle or the rise and run, as the input mode has it"""
        draw_pinwheel(layout, self, f"{prefix}direction")
        names = ("angle",) if getattr(self, f"{prefix}input_mode") == "ANGLE" else ("rise", "run")
        draw_with_lock(layout, self, tuple(prefix + n for n in names), lock, grey_unknowns, getattr(self, "focus", ""))

    return type(
        "DirectionInput", (), {"__annotations__": annotations, f"draw_{prefix}direction_inputs": draw_direction_inputs}
    )


class PickStructuralLoads(bpy.types.Operator):
    """Highlight the shown load under the mouse, and edit it when clicked. Runs while loads are shown"""

    bl_idname = "bim.pick_structural_loads"
    bl_label = "Pick Structural Loads"
    bl_options = {"INTERNAL"}

    def modal(self, context, event):
        assert context.screen
        if not LoadsDecorator.is_installed:
            LoadsDecorator.is_picking = False
            return {"FINISHED"}  # The loads overlay was turned off.
        if event.type == "F5":
            LoadsDecorator.update()
            tool.Blender.update_all_viewports(context)
        if event.type == "MOUSEMOVE":
            hovered = None
            if view := self.get_view_under_mouse(context, event):
                area, region, rv3d = view
                hovered = LoadsDecorator.pick(region, rv3d, event.mouse_x - region.x, event.mouse_y - region.y)
            # Moving between parts of one force, as from its arrow to its angle, changes what is highlighted too.
            part = LoadsDecorator.picked_part if hovered else "arrow"
            if hovered is not LoadsDecorator.hovered or part != LoadsDecorator.hovered_part:
                LoadsDecorator.hovered, LoadsDecorator.hovered_part = hovered, part
                tool.Blender.update_all_viewports(context)
        elif event.type == "LEFTMOUSE" and event.value == "PRESS" and LoadsDecorator.hovered:
            if view := self.get_view_under_mouse(context, event):
                area, region, rv3d = view
                hovered = LoadsDecorator.hovered
                # Dialogs open at the cursor, so move it beside the diagram for the dialog not to cover it.
                self.move_cursor_beside_loads(context, region, rv3d, hovered)
                with context.temp_override(window=context.window, area=area, region=region):
                    # A value clicked is ready to type over as the dialog opens.
                    focus = LoadsDecorator.hovered_focus
                    if hovered.get("add_load_to"):
                        activities = ",".join(str(i) for i in hovered["with_activities"])
                        bpy.ops.bim.add_structural_load_at_point(item=hovered["add_load_to"], activities=activities)
                    elif hovered.get("axes_of"):
                        # A point's axes: made the active point, which Edit Axes edits, as clicking it would.
                        if obj := tool.Ifc.get_object(tool.Ifc.get().by_id(hovered["axes_of"])):
                            for selected in context.selected_objects:
                                selected.select_set(False)
                            obj.select_set(True)
                            context.view_layer.objects.active = obj
                        bpy.ops.bim.edit_structural_connection_axes("INVOKE_DEFAULT", focus=focus)
                    elif hovered.get("moment_resultant"):
                        bpy.ops.bim.edit_structural_resultant_moment("INVOKE_DEFAULT", load_case=hovered["moment_of"])
                    elif hovered.get("moment_of"):
                        bpy.ops.bim.edit_structural_moment_centre(
                            "INVOKE_DEFAULT",
                            load_case=hovered["moment_of"],
                            from_point=hovered["moment_from"],
                            activity=hovered.get("moment_activity", 0),
                            focus=focus,
                        )
                    elif hovered.get("activities"):
                        activities = ",".join(str(i) for i in hovered["activities"])
                        bpy.ops.bim.edit_structural_resultant("INVOKE_DEFAULT", activities=activities, focus=focus)
                    else:
                        bpy.ops.bim.edit_structural_load_values(
                            "INVOKE_DEFAULT", activity=hovered["activity"], focus=focus
                        )
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
        assert context.window_manager
        if not LoadsDecorator.is_installed or LoadsDecorator.is_picking:
            return {"CANCELLED"}
        LoadsDecorator.is_picking = True
        context.window_manager.modal_handler_add(self)
        return {"RUNNING_MODAL"}

    def cancel(self, context):
        LoadsDecorator.is_picking = False


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


def get_dialog_axes(props: "EditStructuralConnectionAxes") -> np.ndarray:
    """The point's axes the dialog describes, as the columns x', y' and z' of a rotation"""
    if props.input_mode == "THREE_D":
        euler = Euler([math.radians(a) for a in (props.rotation_x, props.rotation_y, props.rotation_z)], "XYZ")
        return np.array(euler.to_matrix())
    x, z = tool.Structural.get_in_plane_components(
        props.input_mode, magnitude=1.0, angle=props.angle, rise=props.rise, run=props.run, direction=props.direction
    )
    if not (length := math.hypot(x, z)):
        x, z, length = 1.0, 0.0, 1.0
    x, z = x / length, z / length
    # In the X-Z plane, z' a quarter turn on from x', so that y' stays +Y.
    return np.array(((x, 0.0, -z), (0.0, 1.0, 0.0), (z, 0.0, x)))


def get_dialog_slope(props: "EditStructuralConnectionAxes") -> Union[tuple[float, float], None]:
    """The rise and run the dialog sets the axes by, if it sets them by a slope"""
    return (props.rise, props.run) if props.input_mode == "SLOPE" and (props.rise or props.run) else None


def update_axes_preview(self: "EditStructuralConnectionAxes", context: bpy.types.Context) -> None:
    """Show the point's axes as the dialog has them until it is confirmed or cancelled"""
    if self.item and LoadsDecorator.is_installed:
        ShaderInfo.preview_axes = {self.item: (get_dialog_axes(self), get_dialog_slope(self))}
        redraw_loads(context)


class EditStructuralConnectionAxes(
    bpy.types.Operator, tool.Ifc.Operator, get_direction_input("x'", update_axes_preview, {"SKIP_SAVE"})
):
    bl_idname = "bim.edit_structural_connection_axes"
    bl_label = "Edit Axes"
    bl_description = (
        "Set the point's own axes: x' at an angle or slope, as along an incline, or turned in 3D. Show loads "
        "with the local reference frame to see forces resolved along them"
    )
    bl_options = {"REGISTER", "UNDO"}
    item: bpy.props.IntProperty(options={"HIDDEN", "SKIP_SAVE"})
    # The value to start editing, as the axes' label clicked to open the dialog stands for: angle, rise or run.
    focus: bpy.props.StringProperty(options={"HIDDEN", "SKIP_SAVE"})
    input_mode: bpy.props.EnumProperty(
        name="Input",
        items=[
            ("ANGLE", "Angle", "x' at an angle, in the X-Z plane"),
            ("SLOPE", "Slope", "x' along a rise over a run, as a roof pitch, in the X-Z plane"),
            ("THREE_D", "3D", "Turned any way, by rotations about X, Y and Z"),
        ],
        options={"SKIP_SAVE"},
        update=update_axes_preview,
    )
    rotation_x: bpy.props.FloatProperty(name="X", options={"SKIP_SAVE"}, update=update_axes_preview)
    rotation_y: bpy.props.FloatProperty(name="Y", options={"SKIP_SAVE"}, update=update_axes_preview)
    rotation_z: bpy.props.FloatProperty(name="Z", options={"SKIP_SAVE"}, update=update_axes_preview)

    @classmethod
    def poll(cls, context):
        element = tool.Ifc.get_entity(context.active_object) if context.active_object else None
        return bool(element and element.is_a("IfcStructuralPointConnection"))

    def invoke(self, context, event):
        element = tool.Ifc.get_entity(context.active_object)
        # Reopen in the terms the axes were set in: a slope, an angle in the X-Z plane, or else in 3D.
        self.input_mode, eighth, angle, slope = tool.Structural.get_axes_terms(element)
        if self.input_mode == "THREE_D":
            rotation = tool.Structural.get_axes_rotation(element)
            self.rotation_x, self.rotation_y, self.rotation_z = (
                math.degrees(a) for a in Matrix(rotation.tolist()).to_euler("XYZ")
            )
        else:
            self.direction, self.angle = eighth, angle
            if slope:
                self.rise, self.run = slope
        self.item = element.id()  # Set last, so that filling in the values above does not start a preview.
        return context.window_manager.invoke_props_dialog(self, width=320)

    def draw(self, context):
        layout = self.layout
        layout.row().prop(self, "input_mode", expand=True)
        if self.input_mode == "THREE_D":
            layout.label(text="Rotations, in degrees:")
            for prop in ("rotation_x", "rotation_y", "rotation_z"):
                layout.prop(self, prop)
        else:
            self.draw_direction_inputs(layout)
        rotation = get_dialog_axes(self)
        for k, name in ((0, "x′"), (2, "z′")):
            layout.label(text=f"{name} = ({rotation[0, k]:.3f}, {rotation[1, k]:.3f}, {rotation[2, k]:.3f})")

    def cancel(self, context):
        clear_previews(context)

    def _execute(self, context):
        clear_previews(context)
        element = tool.Ifc.get().by_id(self.item)
        rotation = get_dialog_axes(self)
        ifcopenshell.api.structural.edit_structural_connection_cs(
            tool.Ifc.get(), structural_item=element, axis=rotation[:, 2].tolist(), ref_direction=rotation[:, 0].tolist()
        )
        tool.Structural.set_axes_slope(element, get_dialog_slope(self))
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


def get_chain_activities(item: ifcopenshell.entity_instance, load_case: int) -> list[ifcopenshell.entity_instance]:
    """The applied loads on an item in a load case (0 for none), in their draw order"""
    return tool.Structural.get_chain_activities(item, tool.Ifc.get().by_id(load_case) if load_case else None)


def redraw_loads(context: bpy.types.Context) -> None:
    if LoadsDecorator.is_installed:
        LoadsDecorator.update()
        tool.Blender.update_all_viewports(context)


class MoveStructuralActivity(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.move_structural_activity"
    bl_label = "Move Applied Load"
    bl_description = "Move the applied load earlier or later in its item's tip-to-tail chain for the load case"
    bl_options = {"REGISTER", "UNDO"}
    activity: bpy.props.IntProperty()
    load_case: bpy.props.IntProperty()
    offset: bpy.props.IntProperty(default=-1)

    def _execute(self, context):
        activity = tool.Ifc.get().by_id(self.activity)
        if not (rels := activity.AssignedToStructuralItem):
            return {"CANCELLED"}
        activities = get_chain_activities(rels[0].RelatingElement, self.load_case)
        if activity not in activities:
            return {"CANCELLED"}
        i = activities.index(activity)
        j = i + self.offset
        if not 0 <= j < len(activities):
            return {"CANCELLED"}
        activities[i], activities[j] = activities[j], activities[i]
        tool.Structural.set_draw_order(activities)
        redraw_loads(context)
        return {"FINISHED"}


class ReverseStructuralActivities(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.reverse_structural_activities"
    bl_label = "Reverse Applied Loads"
    bl_description = "Reverse the order of the item's applied loads in the load case's tip-to-tail chain"
    bl_options = {"REGISTER", "UNDO"}
    item: bpy.props.IntProperty()
    load_case: bpy.props.IntProperty()

    def _execute(self, context):
        if len(activities := get_chain_activities(tool.Ifc.get().by_id(self.item), self.load_case)) < 2:
            return {"CANCELLED"}
        tool.Structural.set_draw_order(activities[::-1])
        redraw_loads(context)
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
# An eighth primed, as Q4′, is one of the point's own axes, x' and z', the force was entered against.
_DIRECTION = r"(?: (Q[1-8]′?|(?:up|down)-(?:left|right)))?"
DEFAULT_LOAD_NAME = re.compile(
    rf"^(?:{_NUMBER} \S+ at {_NUMBER} deg{_DIRECTION}|{_NUMBER} \S+ at {_NUMBER}:{_NUMBER}{_DIRECTION}"
    rf"|(?:[XYZ] {_NUMBER}(?:, [XYZ] {_NUMBER})*|0) \S+)$"
)
SLOPE_LOAD_NAME = re.compile(rf"^{_NUMBER} \S+ at ({_NUMBER}):({_NUMBER}){_DIRECTION}$")
ANGLE_LOAD_NAME = re.compile(rf"^{_NUMBER} \S+ at ({_NUMBER}) deg{_DIRECTION}$")
# Names made before the eighths used quadrants measured from the horizontal, which are these eighths.
QUADRANT_EIGHTHS = {"up-right": "Q1", "up-left": "Q4", "down-left": "Q5", "down-right": "Q8"}


def get_direction_suffix(direction: str, on_axes: bool = False) -> str:
    """Q1, measured from +X like a plain angle, is left out of names; one against the point's axes is primed"""
    if on_axes:
        return f" {direction}′"
    return "" if direction == "Q1" else f" {direction}"


def get_named_direction(word: Union[str, None]) -> str:
    word = word.rstrip("′") if word else word
    return QUADRANT_EIGHTHS.get(word, word) if word else "Q1"


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
    if is_on_axes(props):
        x, z = tool.Structural.from_axes(x, z, props.axes_tilt)  # Entered along x' and z'.
    return x, 0.0, z


def get_lock_activity(props: "StructuralForceInput") -> Union[ifcopenshell.entity_instance, None]:
    """The applied load whose values Edit Load locks as known: the one edited, or the only one using the load, or
    none for other dialogs. From the properties alone, as update callbacks get only those.

    Locks belong to applied loads, so a load shared by several has no one set of them.
    """
    if not getattr(props, "activity", 0) and not getattr(props, "structural_load", 0):
        return None
    ifc_file = tool.Ifc.get()
    if props.activity:
        return ifc_file.by_id(props.activity)
    users = [i for i in ifc_file.get_inverse(ifc_file.by_id(props.structural_load)) if i.is_a("IfcStructuralActivity")]
    return users[0] if len(users) == 1 else None


def is_on_axes(props: "StructuralForceInput") -> bool:
    """Whether the angle or slope is entered against the point's own tilted axes rather than X and Z"""
    return bool(getattr(props, "has_axes", False) and props.on_axes and props.input_mode != "COMPONENTS")


def get_common_tilt(items: list[ifcopenshell.entity_instance]) -> Union[float, None]:
    """The tilt of point connections' own axes in the X-Z plane, if they share one and it is not none"""
    tilts = {
        round(tilt, 9) if (tilt := tool.Structural.get_axes_tilt(item)) is not None else None
        for item in items
        if item.is_a("IfcStructuralPointConnection")
    }
    if len(tilts) != 1 or len(items) != sum(item.is_a("IfcStructuralPointConnection") for item in items):
        return None
    tilt = tilts.pop()
    return tilt if tilt else None


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
    direction = get_direction_suffix(props.direction, is_on_axes(props))
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


is_normalising_angle = False
is_setting_magnitude = False
is_remeasuring = False
is_reframing = False


def update_force_inputs(self: "StructuralForceInput", context: bpy.types.Context) -> None:
    # Switching between X and Z and the point's own axes keeps the force, measured in the other frame.
    global is_reframing
    if getattr(self, "has_axes", False) and self.on_axes != self.was_on_axes and not is_reframing:
        is_reframing = True  # Setting the inputs updates again, which must not reframe them again.
        try:
            x, z = tool.Structural.get_in_plane_components(
                "ANGLE" if self.input_mode == "COMPONENTS" else self.input_mode,
                magnitude=self.magnitude,
                angle=self.angle,
                rise=self.rise,
                run=self.run,
                direction=self.direction,
            )
            if self.was_on_axes:
                x, z = tool.Structural.from_axes(x, z, self.axes_tilt)
            if self.on_axes:
                x, z = tool.Structural.to_axes(x, z, self.axes_tilt)
            self.was_on_axes = self.on_axes
            if self.input_mode != "COMPONENTS" and (x or z):
                self.direction, angle, _, _ = tool.Structural.get_eighth(x, z)
                self.angle = round(angle, 9)
                self.rise, self.run = tool.Structural.get_simple_slope(abs(x), abs(z))
        finally:
            is_reframing = False
    # Edit Resultant only: an eighth clicked chooses the axis the same direction is measured from, and the way it
    # turns, as Q6 measures from -Z turning left; the angle typed then sets the direction.
    global is_remeasuring, is_normalising_angle
    measured = getattr(self, "measured_direction", "")
    if (
        measured
        and self.input_mode == "ANGLE"
        and not (is_remeasuring or is_normalising_angle)
        and self.direction != measured
    ):
        x, z = tool.Structural.get_in_plane_components("ANGLE", magnitude=1.0, angle=self.angle, direction=measured)
        if (angle := tool.Structural.get_angle_from_eighth(x, z, self.direction)) is not None:
            is_remeasuring = True  # Setting the angle updates again, which must not measure it again.
            try:
                self.angle = round(angle, 9)
            finally:
                is_remeasuring = False
    if measured:
        self.measured_direction = self.direction
    if self.input_mode == "SLOPE" and self.magnitude:
        # Both eighths of a quadrant give a slope the same direction, so show the one it lands in.
        x, z = tool.Structural.get_in_plane_components(
            "SLOPE", magnitude=self.magnitude, rise=self.rise, run=self.run, direction=self.direction
        )
        eighth = tool.Structural.get_eighth(x, z, self.direction)[0]
        if eighth != self.direction and (int(eighth[1]) + 1) // 2 == (int(self.direction[1]) + 1) // 2:
            self.direction = eighth  # Which updates again, with this eighth.
            return
    global is_setting_magnitude
    if (
        self.input_mode != "COMPONENTS"
        and getattr(self, "given", "MAGNITUDE") != "MAGNITUDE"
        and not is_on_axes(self)
        and not is_setting_magnitude
    ):
        x, z = tool.Structural.get_in_plane_components(
            self.input_mode, magnitude=1.0, angle=self.angle, rise=self.rise, run=self.run, direction=self.direction
        )
        part = abs(x if self.given == "X" else z)
        magnitude = abs(self.given_value) / part if part > 1e-9 else 0.0
        # Blender keeps float properties to single precision, so compare as closely as it can hold them.
        if not math.isclose(magnitude, self.magnitude, rel_tol=1e-6, abs_tol=1e-9):
            is_setting_magnitude = True  # Setting it updates again, which must not set it again.
            try:
                self.magnitude = magnitude
            finally:
                is_setting_magnitude = False
    # Edit Resultant measures from any eighth's axis, so all the way round.
    limit = 360 if measured else 45
    if self.input_mode == "ANGLE" and self.magnitude and not 0 <= self.angle <= limit and not is_normalising_angle:
        # An angle past its eighth points into another: show it there, from that eighth's axis, as names are read.
        x, z = tool.Structural.get_in_plane_components(
            "ANGLE", magnitude=self.magnitude, angle=self.angle, direction=self.direction
        )
        is_normalising_angle = True  # Setting each updates again, before the other is set.
        try:
            self.direction, angle, _, _ = tool.Structural.get_eighth(x, z, self.direction)
            self.angle = round(angle, 9)
        finally:
            is_normalising_angle = False
    # Keep a generated name in step with the values, but never overwrite a name the user typed.
    if self.load_category and (not self.load_name or DEFAULT_LOAD_NAME.match(self.load_name)):
        self.load_name = get_default_load_name(self, self.load_category)
    # Show the load being edited with the values in the dialog until it is confirmed or cancelled.
    if self.preview_load and self.load_category and LoadsDecorator.is_installed:
        attributes = get_load_attributes(self, self.load_category)
        ShaderInfo.preview = {self.preview_load: attributes}
        # Where a resultant is locked, the unknowns move to keep it, so show them moving too.
        if (activity := get_lock_activity(self)) and self.load_category == "IfcStructuralPointConnection":
            force = get_force_components(self)
            forces, _ = get_resolved_forces(
                activity,
                {activity.id(): force},
                {activity.id(): (self.magnitude_locked, self.direction_locked)},
                {activity.GlobalId: (get_same_magnitude_guid(self), getattr(self, "magnitude_ratio", 1.0))},
            )
            for load, solved in (forces or {}).items():
                ShaderInfo.preview[load.id()] = get_force_attributes(load, solved)
                if load.id() == self.preview_load:  # Its own unknowns are found too.
                    ShaderInfo.preview[load.id()].update({k: v for k, v in attributes.items() if "Moment" in k})
            # Where a load case keeps a sum of moments, its unknown moves to keep it, so show that too.
            for case in get_activity_load_groups(activity):
                if (kept := tool.Structural.get_resultant_moment(case)) is None:
                    continue
                edited = {activity.id(): force}
                locks = {activity.id(): (self.magnitude_locked, self.direction_locked)}
                forces, error = solve_case_moment(case, kept, overrides=edited, lock_overrides=locks)
                for load, solved in ({} if error else forces).items():
                    ShaderInfo.preview[load.id()] = get_force_attributes(load, solved)
                    if load.id() == self.preview_load:
                        ShaderInfo.preview[load.id()].update({k: v for k, v in attributes.items() if "Moment" in k})
        redraw_loads(context)
    elif getattr(self, "is_previewing", False) and LoadsDecorator.is_installed:
        forces, resultant, _ = solve_resultant(self)
        ShaderInfo.preview = {load.id(): get_force_attributes(load, force) for load, force in (forces or {}).items()}
        item = get_resultant_item_and_load_case(self)[0]
        ShaderInfo.preview_resultant_eighths = {item.id(): get_chosen_eighth(self, resultant)} if item else {}
        redraw_loads(context)


def get_resolved_forces(
    activity: ifcopenshell.entity_instance,
    forces: Union[dict[int, tuple], None] = None,
    locks: Union[dict[int, tuple[bool, bool]], None] = None,
    links: Union[dict[str, Any], None] = None,
) -> tuple[Union[dict[ifcopenshell.entity_instance, tuple], None], str]:
    """Solve again the unknowns at an applied load's item, for its load case, keeping the resultant as locked.

    :param forces: Forces to take instead of applied loads' own, by activity id, as while editing one.
    :param locks: Locks likewise.
    :param links: Magnitude links likewise, by GlobalId: the other's GlobalId or None, and a ratio.
    :return: The loads to change, and their forces, or none if no resultant is locked there, or why not.
    """
    connects = activity.AssignedToStructuralItem
    item = connects[0].RelatingElement if connects else None
    load_case = tool.Structural.get_activity_load_case(activity)
    if not item or not load_case or not (resultant := tool.Structural.get_resultant(item, load_case)):
        return None, ""
    activities = [
        a
        for a in tool.Structural.get_chain_activities(item, load_case)
        if a.AppliedLoad and a.AppliedLoad.is_a("IfcStructuralLoadSingleForce") and a.GlobalOrLocal != "LOCAL_COORDS"
    ]
    values = [(forces or {}).get(a.id(), get_force(a.AppliedLoad)) for a in activities]
    lock_values = [(locks or {}).get(a.id(), tool.Structural.get_locks(a)) for a in activities]
    groups, factors = tool.Structural.get_magnitude_links(activities, links)
    solved, _, error = tool.Structural.solve_unknowns(
        values,
        lock_values,
        tuple(resultant["Force"]),
        (resultant["MagnitudeLocked"], resultant["DirectionLocked"]),
        groups,
        factors,
    )
    if error:
        return None, error
    return {a.AppliedLoad: f for a, f, lock in zip(activities, solved, lock_values) if not all(lock)}, ""


def write_forces(forces: dict[ifcopenshell.entity_instance, tuple]) -> None:
    """Set single force loads to new forces, keeping their moments, and their generated names in step"""
    ifc_file = tool.Ifc.get()
    unit = get_load_unit_symbol("IfcStructuralPointConnection")
    for load, force in forces.items():
        attributes = get_force_attributes(load, force)
        if DEFAULT_LOAD_NAME.match(load.Name or ""):
            # Entered against the point's own axes, as a primed eighth records, it is named against them still.
            tilt = None
            if re.search(r" Q[1-8]′$", load.Name or ""):
                users = [i for i in ifc_file.get_inverse(load) if i.is_a("IfcStructuralActivity")]
                tilt = get_common_tilt([c[0].RelatingElement for u in users if (c := u.AssignedToStructuralItem)])
            # On the boundary of two eighths, as at 45 degrees, it keeps the one it was named in.
            named = re.search(r" (Q[1-8])′?$", load.Name or "")
            attributes["Name"] = get_force_name(force, unit, tilt, named[1] if named else None)
        ifcopenshell.api.structural.edit_structural_load(ifc_file, structural_load=load, attributes=attributes)


def resolve_resultants(operator: bpy.types.Operator, activities: list[ifcopenshell.entity_instance]) -> None:
    """After applied loads change, solve again the unknowns where a resultant is locked, so that it stays so"""
    for activity in activities:
        forces, error = get_resolved_forces(activity)
        if error:
            operator.report({"WARNING"}, f"The locked resultant could not be kept: {error}")
        elif forces:
            write_forces(forces)


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


def solve_resultant(
    props: "EditStructuralResultant",
) -> tuple[Union[dict[ifcopenshell.entity_instance, tuple], None], Union[tuple, None], str]:
    """Get the loads to change, their new forces, and the resultant, by finding what is unlocked, or why not"""
    activities = get_resultant_activities(props)[:32]
    loads = [activity.AppliedLoad for activity in activities]
    locks = [(props.magnitude_locks[i], props.direction_locks[i]) for i in range(len(loads))]
    if props.magnitude_locked or props.input_mode == "COMPONENTS":
        resultant = get_force_components(props)
    else:
        # Only its direction is known, so take it at any magnitude.
        x, z = tool.Structural.get_in_plane_components(
            props.input_mode,
            magnitude=1.0,
            angle=props.angle,
            rise=props.rise,
            run=props.run,
            direction=props.direction,
        )
        resultant = (x, 0.0, z)
    groups, factors = tool.Structural.get_magnitude_links(activities)
    forces, resultant, error = tool.Structural.solve_unknowns(
        [get_force(load) for load in loads],
        locks,
        resultant,
        (props.magnitude_locked, props.direction_locked),
        groups,
        factors,
    )
    if error:
        return None, None, error
    return {load: force for load, force, lock in zip(loads, forces, locks) if not all(lock)}, resultant, ""


def get_resultant_item_and_load_case(
    props: "EditStructuralResultant",
) -> tuple[Union[ifcopenshell.entity_instance, None], Union[ifcopenshell.entity_instance, None]]:
    """The structural item Edit Resultant's forces act on and their load case, if both are known"""
    activities = get_resultant_activities(props)
    connects = activities[0].AssignedToStructuralItem if activities else None
    if connects and (load_case := tool.Structural.get_activity_load_case(activities[0])):
        return connects[0].RelatingElement, load_case
    return None, None


def get_chosen_eighth(props: "EditStructuralResultant", resultant: Union[tuple, None]) -> Union[str, None]:
    """The eighth Edit Resultant measures the resultant's angle in, if chosen rather than the one it falls in"""
    if props.input_mode != "ANGLE" or not resultant or resultant[1]:
        return None
    x, z = resultant[0], resultant[2]
    if not (x or z):
        return None  # No direction to measure.
    return None if props.direction == tool.Structural.get_eighth(x, z)[0] else props.direction


def get_force_name(
    force: tuple[float, float, float], unit: str, tilt: Union[float, None] = None, eighth: Union[str, None] = None
) -> str:
    """A generated name for a force, by its angle from the nearest axis if it lies in the X-Z plane.

    :param tilt: The tilt of the point's own axes, to name it against them, its eighth primed, as entered so.
    :param eighth: The eighth to name it in if it lies on that eighth's boundary, as it was named before.
    """
    x, y, z = force
    if y:
        values = [f"{axis} {value:g}" for axis, value in zip("XYZ", force) if value]
        return f"{', '.join(values) or '0'} {unit}"
    if tilt:
        x, z = tool.Structural.to_axes(x, z, tilt)
    eighth, angle, _, _ = tool.Structural.get_eighth(x, z, eighth)
    return f"{math.hypot(x, z):g} {unit} at {angle:g} deg{get_direction_suffix(eighth, bool(tilt))}"


def clear_previews(context: bpy.types.Context) -> None:
    """Stop showing a dialog's values in the loads drawing, as when it is confirmed or cancelled"""
    if ShaderInfo.preview or ShaderInfo.preview_axes or ShaderInfo.preview_resultant_eighths:
        ShaderInfo.preview, ShaderInfo.preview_axes, ShaderInfo.preview_resultant_eighths = {}, {}, {}
        redraw_loads(context)


class StructuralForceInput(get_direction_input("the force", update_force_inputs, {"ANIMATABLE"})):
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
    magnitude: bpy.props.FloatProperty(name="Magnitude", update=update_force_inputs)
    given: bpy.props.EnumProperty(
        name="Given",
        description="The value known: the magnitude, or a component, from which and the direction the magnitude follows",
        items=[
            ("MAGNITUDE", "Magnitude", "The magnitude is known"),
            ("X", "X", "The X component is known, as a horizontal capacity; the magnitude is found"),
            ("Z", "Z", "The Z component is known, as a vertical capacity; the magnitude is found"),
        ],
        options={"SKIP_SAVE"},
        update=update_force_inputs,
    )
    given_value: bpy.props.FloatProperty(
        name="Component", description="The size of the known component", update=update_force_inputs
    )
    x: bpy.props.FloatProperty(name="X", update=update_force_inputs)
    y: bpy.props.FloatProperty(name="Y", update=update_force_inputs)
    z: bpy.props.FloatProperty(name="Z", update=update_force_inputs)
    moment_x: bpy.props.FloatProperty(name="Moment X", update=update_force_inputs)
    moment_y: bpy.props.FloatProperty(name="Moment Y", update=update_force_inputs)
    moment_z: bpy.props.FloatProperty(name="Moment Z", update=update_force_inputs)
    load_name: bpy.props.StringProperty(name="Load Name")
    magnitude_locked: bpy.props.BoolProperty(
        name="Magnitude Known",
        description="Whether the magnitude is known. Edit Resultant keeps it, or finds it if unlocked",
        default=True,
        options={"SKIP_SAVE"},
        update=update_force_inputs,
    )
    acts_as: bpy.props.EnumProperty(
        name="Acts As",
        description="Whether the force pulls on its item or pushes on it, which only changes how it is drawn",
        items=[
            ("PULL", "Pull", "Drawn from its point, as a cable pulls"),
            ("PUSH", "Push", "Drawn arriving at its point, as a strut pushes"),
        ],
        options={"SKIP_SAVE"},
    )
    direction_locked: bpy.props.BoolProperty(
        name="Direction Known",
        description="Whether the direction is known. Edit Resultant keeps it, or finds it if unlocked",
        default=True,
        options={"SKIP_SAVE"},
        update=update_force_inputs,
    )
    on_axes: bpy.props.BoolProperty(
        name="Point Axes",
        description=(
            "Enter the angle or slope against the point's own tilted axes, x' and z', as along an incline, rather "
            "than X and Z. Switching keeps the force, measured the other way"
        ),
        options={"SKIP_SAVE"},
        update=update_force_inputs,
    )
    # The value to start editing, as the label clicked to open the dialog stands for: magnitude, angle, rise or run.
    focus: bpy.props.StringProperty(options={"HIDDEN", "SKIP_SAVE"})
    # The point's own axes, if its forces can be entered against them, and the frame last measured in.
    has_axes: bpy.props.BoolProperty(options={"HIDDEN", "SKIP_SAVE"})
    axes_tilt: bpy.props.FloatProperty(options={"HIDDEN", "SKIP_SAVE"})
    was_on_axes: bpy.props.BoolProperty(options={"HIDDEN", "SKIP_SAVE"})

    def get_components(self) -> tuple[float, float, float]:
        return get_force_components(self)

    def get_load_attributes(self, category: str) -> dict[str, Union[float, None]]:
        return get_load_attributes(self, category)

    def set_in_plane_inputs(self, x: float, z: float) -> None:
        """Fill the angle and slope inputs from in-plane components, measured from the nearest axis"""
        set_in_plane_direction(self, x, z)
        self.magnitude = math.hypot(x, z)

    def get_unit_symbol(self, category: str) -> str:
        return get_load_unit_symbol(category)

    def get_default_load_name(self, category: str) -> str:
        return get_default_load_name(self, category)

    def draw_force_inputs(
        self,
        layout: bpy.types.UILayout,
        category: Union[str, None],
        show_name: bool = True,
        show_locks: bool = False,
        grey_unknowns: bool = False,
        show_given: bool = False,
    ) -> None:
        """Draw the force inputs.

        :param show_locks: Show whether the magnitude and direction are known, beside them.
        :param grey_unknowns: Grey out values that are not known, as they are found rather than entered.
        """

        layout.row().prop(self, "input_mode", expand=True)
        if self.input_mode == "COMPONENTS":
            if show_locks:
                row = layout.row(align=True)
                for lock, text in (("magnitude_locked", "Magnitude"), ("direction_locked", "Direction")):
                    row.prop(self, lock, text=text, icon="LOCKED" if getattr(self, lock) else "UNLOCKED")
            for prop in ("x", "y", "z"):
                draw_with_lock(layout, self, (prop,), focus=self.focus)
            if category in ("IfcStructuralPointConnection", "IfcStructuralCurveMember"):
                for prop in ("moment_x", "moment_y", "moment_z"):
                    layout.prop(self, prop)
        else:
            if self.has_axes:
                layout.prop(self, "on_axes", icon="ORIENTATION_LOCAL", toggle=True)
            self.draw_direction_inputs(layout, "direction_locked" if show_locks else None, grey_unknowns)
            # A known component is an X or Z one, so not offered against the point's axes.
            show_given = show_given and not is_on_axes(self)
            if show_given:
                layout.row().prop(self, "given", expand=True)
            if show_given and self.given != "MAGNITUDE":
                # The component is typed, and the magnitude found from it.
                layout.prop(self, "given_value", text=f"{self.given} Component")
                layout.label(text=f"Magnitude = {self.magnitude:.4f}  (found)", icon="UNLOCKED")
            else:
                lock = "magnitude_locked" if show_locks else None
                draw_with_lock(layout, self, ("magnitude",), lock, grey_unknowns, self.focus)
            x, _, z = self.get_components()
            unit = self.get_unit_symbol(category) if category else ""
            layout.label(text=f"X = {x:.4f}   Z = {z:.4f} {unit}", icon="ORIENTATION_GLOBAL")
            if self.has_axes:
                xa, za = tool.Structural.to_axes(x, z, self.axes_tilt)
                layout.label(text=f"x′ = {xa:.4f}   z′ = {za:.4f} {unit}", icon="ORIENTATION_LOCAL")
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
        if (tilt := get_common_tilt(self.get_targets(context)[1])) is not None:
            self.has_axes, self.axes_tilt = True, tilt
        self.load_name = self.get_default_load_name(category)
        return context.window_manager.invoke_props_dialog(self, width=350)

    def draw(self, context):
        category, elements = self.get_targets(context)
        layout = self.layout
        layout.prop(self, "load_group")
        if self.load_group == "0":
            layout.prop(self, "new_load_case_name")
        self.draw_force_inputs(layout, category, show_locks=True, show_given=True)
        if category == "IfcStructuralPointConnection":
            layout.row().prop(self, "acts_as", expand=True)
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
        for activity in activities:  # Only an unlocked value is recorded; loads are known unless said.
            tool.Structural.set_locks(activity, self.magnitude_locked, self.direction_locked)
            tool.Structural.set_push(activity, self.acts_as == "PUSH")
            known = None if self.given == "MAGNITUDE" or is_on_axes(self) else self.given
            tool.Structural.set_known_component(activity, known)
        resolve_resultants(self, activities)
        self.show_load_group(context, group)
        return {"FINISHED"}

    def show_load_group(self, context: bpy.types.Context, group: ifcopenshell.entity_instance) -> None:
        """Show the loads of the load case just applied to, so that the new load is seen"""
        LoadGroupDecorationData.is_loaded = False  # A new load case is not listed yet.
        try:
            tool.Structural.get_structural_props().load_group_to_show = str(group.id())
        except TypeError:
            return  # Not in the current analysis model, so it cannot be shown.
        tool.Structural.get_structural_props().show_loads = True


# Blender needs enum item strings to stay referenced while the dialog is open.
same_magnitude_items: list[tuple[str, str, str]] = []


def get_same_magnitude_items(self, context: bpy.types.Context) -> list[tuple[str, str, str]]:
    """The other point forces in the edited applied load's load case at its item, numbered as calculations are"""
    global same_magnitude_items
    same_magnitude_items = [("NONE", "None", "Its magnitude is its own")]
    if (activity := get_lock_activity(self)) and (connects := activity.AssignedToStructuralItem):
        chain = tool.Structural.get_chain_activities(
            connects[0].RelatingElement, tool.Structural.get_activity_load_case(activity)
        )
        forces = [a for a in chain if a.AppliedLoad and a.AppliedLoad.is_a("IfcStructuralLoadSingleForce")]
        subscripts = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")
        for n, other in enumerate(forces, 1):
            if other != activity:
                name = f"F{str(n).translate(subscripts)}: {other.AppliedLoad.Name or 'Unnamed'}"
                same_magnitude_items.append((str(other.id()), name, "Of equal magnitude to this force"))
    return same_magnitude_items


def get_by_guid(guid: Union[str, None]) -> Union[ifcopenshell.entity_instance, None]:
    """An entity by its GlobalId, or None if there is none, as when a linked one was removed"""
    try:
        return tool.Ifc.get().by_guid(guid) if guid else None
    except RuntimeError:
        return None


def get_same_magnitude_guid(props: "EditStructuralLoadValues") -> Union[str, None]:
    """The GlobalId of the applied load chosen as of equal magnitude, if any"""
    choice = getattr(props, "same_magnitude_as", "NONE")
    return tool.Ifc.get().by_id(int(choice)).GlobalId if choice not in ("", "NONE") else None


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


def get_load_location_objects(
    props: "EditStructuralLoadValues",
) -> tuple[Union[bpy.types.Object, None], Union[bpy.types.Object, None]]:
    """The objects of the point an edited applied load acts at and of the moment centre of a load case it is in,
    if it is a point's and one is"""
    if not props.activity:
        return None, None
    activity = tool.Ifc.get().by_id(props.activity)
    connects = activity.AssignedToStructuralItem
    point = connects[0].RelatingElement if connects else None
    if not point or not point.is_a("IfcStructuralPointConnection"):
        return None, None
    has_vertex = lambda obj: obj if obj and obj.type == "MESH" and obj.data.vertices else None
    for case in get_activity_load_groups(activity):
        if centre := tool.Structural.get_moment_centre(case):
            centre_obj, point_obj = has_vertex(tool.Ifc.get_object(centre)), has_vertex(tool.Ifc.get_object(point))
            if centre_obj and point_obj and centre_obj != point_obj:
                return point_obj, centre_obj
    return None, None


# The kinds of where a force acts that a kept moment can find, by the padlock in Edit Load that unlocks each.
LOCATION_LOCKS = {
    "POINT_X": "location_x_locked",
    "POINT_Z": "location_z_locked",
    "POINT_REACH": "location_distance_locked",
    "POINT_SWING": "location_angle_locked",
}


def get_load_place_unknown(props: "EditStructuralLoadValues") -> Union[str, None]:
    """Which of where the edited applied load acts a load case it is in finds, if any"""
    activity = tool.Ifc.get().by_id(props.activity)
    for case in get_activity_load_groups(activity):
        kind, unknown = tool.Structural.get_moment_centre_unknown(case)
        if unknown == activity and kind in LOCATION_LOCKS:
            return kind
    return None


def get_load_location_offset(props: "EditStructuralLoadValues") -> tuple[float, float]:
    """Where the force's point is from A, as entered: Δx and Δz, or a distance and its direction"""
    if props.location_input_mode == "COMPONENTS":
        return props.location_dx, props.location_dz
    return tool.Structural.get_in_plane_components(
        props.location_input_mode,
        magnitude=props.location_distance,
        angle=props.location_angle,
        rise=props.location_rise,
        run=props.location_run,
        direction=props.location_direction,
    )


# The location inputs each input mode enters the point by, left alone while typed in.
LOCATION_MODE_INPUTS = {
    "COMPONENTS": ("location_dx", "location_dz"),
    "ANGLE": ("location_distance", "location_direction", "location_angle"),
    "SLOPE": ("location_distance", "location_direction", "location_rise", "location_run"),
}


def fill_load_location(props: "EditStructuralLoadValues", keep: tuple[str, ...] = ()) -> None:
    """Fill the location inputs from where the force's point is from A, leaving those typed in"""
    point_obj, centre_obj = get_load_location_objects(props)
    if not point_obj:
        return
    at, point = get_vertex_location(centre_obj), get_vertex_location(point_obj)
    dx, dz = point.x - at.x, point.z - at.z
    values = {"location_dx": dx, "location_dz": dz, "location_distance": math.hypot(dx, dz)}
    if dx or dz:
        values["location_direction"], values["location_angle"], _, _ = tool.Structural.get_eighth(dx, dz)
        values["location_rise"], values["location_run"] = tool.Structural.get_simple_slope(abs(dx), abs(dz))
    MOMENT_CENTRE_FILLING[0] = True  # Filling them must not move the point.
    try:
        for name, value in values.items():
            if name not in keep:
                setattr(props, name, value)
    finally:
        MOMENT_CENTRE_FILLING[0] = False


def refill_load_location(props: "EditStructuralLoadValues", context: bpy.types.Context) -> None:
    """Read where the point is in another input mode: an update callback, so of exactly two arguments"""
    fill_load_location(props)


def move_load_location(props: "EditStructuralLoadValues", context: bpy.types.Context) -> None:
    """Move the edited load's point to where it is entered from the moment centre, keeping its Y, to preview the
    moments with it there"""
    point_obj, centre_obj = get_load_location_objects(props)
    if not point_obj or MOMENT_CENTRE_FILLING[0]:
        return
    MOMENT_CENTRE_PREVIEW.setdefault(point_obj.name, point_obj.matrix_world.translation.copy())
    dx, dz = get_load_location_offset(props)
    at, point = get_vertex_location(centre_obj), get_vertex_location(point_obj)
    point_obj.matrix_world.translation += Vector((at.x + dx, point.y, at.z + dz)) - point
    context.view_layer.update()
    fill_load_location(props, LOCATION_MODE_INPUTS[props.location_input_mode])
    update_force_inputs(props, context)  # Its preview again, so that a kept moment's unknown follows the point.


class EditStructuralLoadValues(
    bpy.types.Operator,
    tool.Ifc.Operator,
    StructuralForceInput,
    get_direction_input("the force's point, from A,", move_load_location, {"SKIP_SAVE"}, prefix="location_"),
):
    bl_idname = "bim.edit_structural_load_values"
    bl_label = "Edit Structural Load"
    bl_description = "Edit the force of a structural load"
    bl_options = {"REGISTER", "UNDO"}
    structural_load: bpy.props.IntProperty(options={"SKIP_SAVE"})
    activity: bpy.props.IntProperty(description="Edit the load applied by this activity instead", options={"SKIP_SAVE"})
    load_group: bpy.props.EnumProperty(name="Load Case", items=get_edit_load_groups, options={"SKIP_SAVE"})
    new_load_case_name: bpy.props.StringProperty(name="New Load Case", default="Load Case")
    # A load just added to be edited, as Add Load at a point does, is removed again if the edit is cancelled.
    remove_on_cancel: bpy.props.BoolProperty(options={"HIDDEN", "SKIP_SAVE"})
    place_from_a: bpy.props.BoolProperty(
        name="Place From A",
        description="Enter where the force acts, from the moment centre A, as components, an angle or a slope, rather "
        "than the force. It moves the force's point, and every load at it",
        default=False,
        options={"SKIP_SAVE"},
    )
    location_input_mode: bpy.props.EnumProperty(
        name="Input",
        items=[
            ("COMPONENTS", "Components", "Δx and Δz, from A to the force's point"),
            ("ANGLE", "Angle", "Distance and angle, from A to the force's point"),
            ("SLOPE", "Slope", "Distance and rise over run, from A to the force's point"),
        ],
        options={"SKIP_SAVE"},
        update=refill_load_location,
    )
    location_x_locked: bpy.props.BoolProperty(
        name="Δx Known",
        description="If not, a kept moment moves the point along X",
        default=True,
        options={"SKIP_SAVE"},
    )
    location_z_locked: bpy.props.BoolProperty(
        name="Δz Known",
        description="If not, a kept moment moves the point along Z",
        default=True,
        options={"SKIP_SAVE"},
    )
    location_distance_locked: bpy.props.BoolProperty(
        name="Distance Known",
        description="If not, a kept moment moves the point along the line from A",
        default=True,
        options={"SKIP_SAVE"},
    )
    location_angle_locked: bpy.props.BoolProperty(
        name="Direction Known",
        description="If not, a kept moment swings the point round A, its distance kept",
        default=True,
        options={"SKIP_SAVE"},
    )
    location_distance: bpy.props.FloatProperty(
        name="Distance",
        description="From A to the force's point",
        subtype="DISTANCE",
        options={"SKIP_SAVE"},
        update=move_load_location,
    )
    location_dx: bpy.props.FloatProperty(
        name="Δx from A",
        description="From the moment centre to the force's point, along X, as the report's table measures it",
        subtype="DISTANCE",
        options={"SKIP_SAVE"},
        update=move_load_location,
    )
    location_dz: bpy.props.FloatProperty(
        name="Δz from A",
        description="From the moment centre to the force's point, along Z, as the report's table measures it",
        subtype="DISTANCE",
        options={"SKIP_SAVE"},
        update=move_load_location,
    )
    same_magnitude_as: bpy.props.EnumProperty(
        name="Magnitude As",
        description=(
            "Another force at the point whose magnitude this one's follows, times the ratio: equal, as two equal "
            "cable tensions are, or a share of it. Solving finds one magnitude for both, or this one follows the "
            "other's if known"
        ),
        items=get_same_magnitude_items,
        options={"SKIP_SAVE"},
        update=update_force_inputs,
    )
    magnitude_ratio: bpy.props.FloatProperty(
        name="Ratio",
        description="How many times the other force's magnitude this one's is, as 0.25 for a quarter of it",
        default=1.0,
        min=1e-6,
        options={"SKIP_SAVE"},
        update=update_force_inputs,
    )

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
        # IFC only stores components, so derive the in-plane inputs from them, from the nearest axis...
        x, y, z = (getattr(load, a) or 0.0 for a in force_attributes)
        self.set_in_plane_inputs(x, z)
        self.input_mode = "COMPONENTS"
        users = [i for i in tool.Ifc.get().get_inverse(load) if i.is_a("IfcStructuralActivity")]
        items = [c[0].RelatingElement for u in users if (c := u.AssignedToStructuralItem)]
        if category == "IfcStructuralPointConnection" and (tilt := get_common_tilt(items)) is not None:
            self.has_axes, self.axes_tilt = True, tilt
        # ... but reopen in the way the load was entered if its generated name records it and still fits,
        # against the point's own axes if its eighth is primed.
        name = load.Name or ""
        match = (SLOPE_LOAD_NAME.match(name) or ANGLE_LOAD_NAME.match(name)) if not y else None
        if match and self.has_axes and (match.groups()[-1] or "").endswith("′"):
            self.was_on_axes = self.on_axes = True  # Both, so that nothing is measured again.
            x, z = tool.Structural.to_axes(x, z, self.axes_tilt)
        if not y and (match := SLOPE_LOAD_NAME.match(name)):
            rise, run = float(match[1]), float(match[2])
            direction = get_named_direction(match[3])
            if self.fits(x, z, "SLOPE", rise=rise, run=run, direction=direction):
                # The eighth first: each value set updates the others, read with the eighth.
                self.input_mode, self.direction, self.rise, self.run = "SLOPE", direction, rise, run
        elif not y and (match := ANGLE_LOAD_NAME.match(name)):
            angle = float(match[1])
            direction = get_named_direction(match[2])
            if self.fits(x, z, "ANGLE", angle=angle, direction=direction):
                self.input_mode, self.direction, self.angle = "ANGLE", direction, angle
        if self.focus in ("x", "y", "z"):
            self.input_mode = "COMPONENTS"  # A component clicked opens with it ready to type.
        if self.on_axes and self.input_mode == "COMPONENTS":
            self.was_on_axes = self.on_axes = False  # The name no longer fits, so reopen in X and Z.
        # A generated name is generated again, so that it reads as the inputs now do, as from its eighth's axis.
        self.load_name = get_default_load_name(self, category) if DEFAULT_LOAD_NAME.match(name) else name
        if lock_activity := self.get_lock_activity():
            self.magnitude_locked, self.direction_locked = tool.Structural.get_locks(lock_activity)
            self.acts_as = "PUSH" if tool.Structural.get_push(lock_activity) else "PULL"
            if self.input_mode != "COMPONENTS" and (component := tool.Structural.get_known_component(lock_activity)):
                self.given_value = abs(x if component == "X" else z)
                self.given = component
            if other := get_by_guid(tool.Structural.get_magnitude_link(lock_activity)):
                if str(other.id()) in [item[0] for item in get_same_magnitude_items(self, context)]:
                    self.same_magnitude_as = str(other.id())
                    self.magnitude_ratio = tool.Structural.get_magnitude_ratio(lock_activity)
        if (activities := self.get_movable_activities()) and (groups := get_activity_load_groups(activities[0])):
            self.load_group = str(groups[0].id())
        MOMENT_CENTRE_PREVIEW.clear()
        fill_load_location(self.properties)
        # Which of where it acts a kept moment finds, if it is this force's.
        for kind, prop in LOCATION_LOCKS.items():
            setattr(self, prop, not (self.activity and get_load_place_unknown(self) == kind))
        # Set last, so that filling in the values above does not start a preview.
        self.preview_load = load.id()
        if self.remove_on_cancel:
            # A load just added is previewed at once: where a resultant is locked, the unknowns move to keep it, as
            # they will on confirming, so that the new force is not hidden under a resultant it alone makes.
            update_force_inputs(self, context)
        return context.window_manager.invoke_props_dialog(self, width=350)

    def fits(
        self,
        x: float,
        z: float,
        mode: str,
        angle: float = 0.0,
        rise: float = 0.0,
        run: float = 0.0,
        direction: str = "Q1",
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
        if get_load_location_objects(self)[0]:
            layout.prop(self, "place_from_a")
            if self.place_from_a:
                self.draw_location_inputs(layout)
                return
        lock_activity = self.get_lock_activity()
        if not lock_activity:
            layout.label(text="Open it from an applied load to lock its values", icon="INFO")
        self.draw_force_inputs(layout, category, show_locks=bool(lock_activity), show_given=bool(lock_activity))
        if lock_activity and category == "IfcStructuralPointConnection":
            row = layout.row(align=True)
            row.prop(self, "same_magnitude_as")
            if self.same_magnitude_as not in ("", "NONE"):
                row.prop(self, "magnitude_ratio", text="×")
            layout.row().prop(self, "acts_as", expand=True)
        if self.input_mode != "COMPONENTS" and (self.y or self.moment_x or self.moment_y or self.moment_z):
            layout.label(text="Y and moments will be set to zero", icon="ERROR")

    def draw_location_inputs(self, layout: bpy.types.UILayout) -> None:
        """Where the force acts, from A, in the input modes the force is entered in"""
        layout.row().prop(self, "location_input_mode", expand=True)
        if self.location_input_mode == "COMPONENTS":
            draw_with_lock(layout, self, ("location_dx",), "location_x_locked")
            draw_with_lock(layout, self, ("location_dz",), "location_z_locked")
        else:
            self.draw_location_direction_inputs(layout, "location_angle_locked")
            draw_with_lock(layout, self, ("location_distance",), "location_distance_locked")
            dx, dz = get_load_location_offset(self)
            length_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
            unit = get_project_unit_symbol("LENGTHUNIT", "m")
            text = f"From A: Δx = {dx / length_scale:.4f}   Δz = {dz / length_scale:.4f} {unit}"
            layout.label(text=text, icon="ORIENTATION_GLOBAL")
        point = tool.Ifc.get_entity(get_load_location_objects(self)[0])
        count = len([r for r in point.AssignedStructuralActivity or [] if r.RelatedStructuralActivity])
        if count > 1:
            layout.label(text=f"Moves the point, and all {count} of its loads with it", icon="INFO")
        unlocked = [kind for kind, prop in LOCATION_LOCKS.items() if not getattr(self, prop)]
        if len(unlocked) > 1:
            layout.label(text="Unlock one of where it acts: a kept moment finds one", icon="ERROR")
        elif unlocked:
            activity = tool.Ifc.get().by_id(self.activity)
            if all(tool.Structural.get_resultant_moment(c) is None for c in get_activity_load_groups(activity)):
                layout.label(text="Found once ΣM_A is kept, in Edit Resultant Moment", icon="INFO")

    def cancel(self, context):
        clear_previews(context)
        restore_moment_centre(context)  # The point, moved to preview its location.
        if self.remove_on_cancel and self.activity:
            load = self.get_load()
            bpy.ops.bim.remove_structural_activity(activity=self.activity)
            if not [i for i in tool.Ifc.get().get_inverse(load) if i.is_a("IfcStructuralActivity")]:
                bpy.ops.bim.remove_structural_load(structural_load=load.id())

    def _execute(self, context):
        ShaderInfo.preview = {}  # The edit below refreshes the shown loads.
        load = self.get_load()
        category = get_load_category(load)
        attributes = self.get_load_attributes(category)
        attributes["Name"] = self.get_load_name(category)
        ifc_file = tool.Ifc.get()
        ifcopenshell.api.structural.edit_structural_load(ifc_file, structural_load=load, attributes=attributes)
        point_obj, _ = get_load_location_objects(self)
        if point_obj and self.activity:
            unlocked = [kind for kind, prop in LOCATION_LOCKS.items() if not getattr(self, prop)]
            if len(unlocked) > 1:
                self.report({"ERROR"}, "Unlock one of where it acts: a kept moment finds one")
                return {"CANCELLED"}
            # Its place unlocked here is the load case's unknown; one this force had, locked here, no longer is.
            activity = tool.Ifc.get().by_id(self.activity)
            for case in get_activity_load_groups(activity):
                kind, unknown = tool.Structural.get_moment_centre_unknown(case)
                if unlocked or (unknown == activity and kind in LOCATION_LOCKS):
                    tool.Structural.set_moment_centre_unknown(case, unlocked[0] if unlocked else None, activity)
        if point_obj and point_obj.name in MOMENT_CENTRE_PREVIEW:
            # Where its location put it, written to the IFC, before kept values are solved again with it there.
            bonsai.core.geometry.edit_object_placement(tool.Ifc, tool.Geometry, tool.Surveyor, obj=point_obj)
        MOMENT_CENTRE_PREVIEW.clear()
        if lock_activity := self.get_lock_activity():
            tool.Structural.set_locks(lock_activity, self.magnitude_locked, self.direction_locked)
            tool.Structural.set_push(lock_activity, self.acts_as == "PUSH")
            known = (
                None if self.input_mode == "COMPONENTS" or self.given == "MAGNITUDE" or is_on_axes(self) else self.given
            )
            tool.Structural.set_known_component(lock_activity, known)
            if self.load_category == "IfcStructuralPointConnection":
                other = get_by_guid(get_same_magnitude_guid(self))
                tool.Structural.set_magnitude_link(lock_activity, other, self.magnitude_ratio)
        activities = self.get_movable_activities()
        if activities and (target := self.get_target_load_group(ifc_file)):
            for activity in activities:
                self.move_activity(ifc_file, activity, target)
        users = [i for i in ifc_file.get_inverse(load) if i.is_a("IfcStructuralActivity")]
        resolve_resultants(self, users)
        keep_resultant_moments(users)
        if tool.Structural.get_structural_props().is_editing_loads:
            bpy.ops.bim.load_structural_loads()
        return {"FINISHED"}

    def get_lock_activity(self) -> Union[ifcopenshell.entity_instance, None]:
        return get_lock_activity(self)

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


class AddStructuralLoadAtPoint(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_structural_load_at_point"
    bl_label = "Add Load"
    bl_description = (
        "Add a force to the point, at 45 degrees and as large as the average of its forces in the load case, and "
        "open it to edit; cancelling the edit removes it"
    )
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}
    item: bpy.props.IntProperty(options={"HIDDEN", "SKIP_SAVE"})
    activities: bpy.props.StringProperty(
        description="Ids of the applied loads at the point in the load case, which the new one joins",
        options={"HIDDEN", "SKIP_SAVE"},
    )

    def _execute(self, context):
        ifc_file = tool.Ifc.get()
        item = ifc_file.by_id(self.item)
        activities = [ifc_file.by_id(int(i)) for i in self.activities.split(",") if i]
        forces = [
            math.hypot(*get_force(a.AppliedLoad))
            for a in activities
            if a.AppliedLoad and a.AppliedLoad.is_a("IfcStructuralLoadSingleForce")
        ]
        magnitude = float(f"{sum(forces) / len(forces):.4g}") if forces else 1.0
        unit = get_load_unit_symbol("IfcStructuralPointConnection")
        load = ifcopenshell.api.structural.add_structural_load(
            ifc_file, name=f"{magnitude:g} {unit} at 45 deg", ifc_class="IfcStructuralLoadSingleForce"
        )
        x, z = tool.Structural.get_in_plane_components("ANGLE", magnitude=magnitude, angle=45, direction="Q1")
        ifcopenshell.api.structural.edit_structural_load(
            ifc_file, structural_load=load, attributes={"ForceX": x, "ForceY": None, "ForceZ": z}
        )
        activity = ifcopenshell.api.structural.add_structural_activity(
            ifc_file, ifc_class="IfcStructuralPointAction", applied_load=load, structural_member=item
        )
        # In the same load case and group as the loads beside it, drawn after them, tip to tail.
        if activities and (groups := get_activity_load_groups(activities[0])):
            ifcopenshell.api.group.assign_group(ifc_file, products=[activity], group=groups[0])
            chain = tool.Structural.get_chain_activities(item, tool.Structural.get_activity_load_case(activity))
            tool.Structural.set_draw_order([a for a in chain if a != activity] + [activity])
        bpy.ops.bim.edit_structural_load_values(
            "INVOKE_DEFAULT", activity=activity.id(), focus="magnitude", remove_on_cancel=True
        )
        return {"FINISHED"}


class EditStructuralResultant(bpy.types.Operator, tool.Ifc.Operator, StructuralForceInput):
    bl_idname = "bim.edit_structural_resultant"
    bl_label = "Edit Resultant"
    bl_description = (
        "Find two unknowns of the forces at a point and their resultant: the magnitudes and directions unlocked"
    )
    bl_options = {"REGISTER", "UNDO"}
    activities: bpy.props.StringProperty(description="Ids of the activities whose forces add up", options={"SKIP_SAVE"})
    magnitude_locks: bpy.props.BoolVectorProperty(
        name="Magnitude Known",
        description="Whether this force's magnitude is known. If not, it is found",
        size=32,
        default=[True] * 32,
        options={"SKIP_SAVE"},
        update=update_force_inputs,
    )
    direction_locks: bpy.props.BoolVectorProperty(
        name="Direction Known",
        description="Whether this force's direction is known. If not, it is found",
        size=32,
        default=[True] * 32,
        options={"SKIP_SAVE"},
        update=update_force_inputs,
    )
    is_previewing: bpy.props.BoolProperty(options={"HIDDEN", "SKIP_SAVE"})
    # The eighth the angle was last measured in, to tell a click on the other eighth of its quadrant.
    measured_direction: bpy.props.StringProperty(options={"HIDDEN", "SKIP_SAVE"})

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
        # Reopen measured in the eighth chosen for it, as from -X rather than +Z.
        item, load_case = self.get_item_and_load_case()
        eighth = tool.Structural.get_resultant_eighth(item, load_case) if item and not y else None
        if eighth and (angle := tool.Structural.get_angle_from_eighth(x, z, eighth)) is not None:
            self.measured_direction = eighth  # First, so that the angle may pass 45 degrees.
            self.direction, self.angle = eighth, angle
        self.measured_direction = self.direction
        locks = [tool.Structural.get_locks(activity) for activity in activities[:32]]
        self.magnitude_locks = [lock[0] for lock in locks] + [True] * (32 - len(locks))
        self.direction_locks = [lock[1] for lock in locks] + [True] * (32 - len(locks))
        if resultant := self.get_locked_resultant():
            self.magnitude_locked, self.direction_locked = resultant["MagnitudeLocked"], resultant["DirectionLocked"]
        else:
            # Leave the resultant as unknown as the forces leave room for: two unknowns in all.
            unlocked = sum(not locked for lock in locks for locked in lock)
            self.magnitude_locked, self.direction_locked = unlocked >= 2, unlocked >= 1
        self.is_previewing = True  # Set last, so that filling in the values above does not start a preview.
        return context.window_manager.invoke_props_dialog(self, width=380)

    def draw(self, context):
        layout = self.layout
        activities = get_resultant_activities(self)
        layout.label(text=f"Resultant of {len(activities)} forces", icon="INFO")
        self.draw_force_inputs(layout, self.load_category, show_name=False, show_locks=True, grey_unknowns=True)
        unit = self.get_unit_symbol(self.load_category)
        layout.label(text="Forces, and which of their values are known:")
        for i, activity in enumerate(activities[:32]):
            row = layout.row(align=True)
            # Numbered as reports and unlocked-value messages number them, tip to tail.
            symbol = "F" + str(i + 1).translate(str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉"))
            row.label(text=f"{symbol}: {activity.AppliedLoad.Name or 'Unnamed'}", icon="FORCE_FORCE")
            for prop, text in (("magnitude_locks", "Magnitude"), ("direction_locks", "Direction")):
                locked = getattr(self, prop)[i]
                row.prop(self, prop, index=i, text=text, icon="LOCKED" if locked else "UNLOCKED")
        forces, resultant, error = solve_resultant(self)
        if error:
            layout.label(text=error, icon="ERROR")
            return
        box = layout.box()
        if not (self.magnitude_locked and self.direction_locked):
            box.label(text=f"Resultant: {get_force_name(resultant, unit)}", icon="FORCE_FORCE")
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
        clear_previews(context)

    def _execute(self, context):
        ShaderInfo.preview, ShaderInfo.preview_resultant_eighths = {}, {}  # The edit below refreshes the shown loads.
        forces, resultant, error = solve_resultant(self)
        if error:
            self.report({"ERROR"}, error)
            return {"CANCELLED"}
        activities = get_resultant_activities(self)
        for i, activity in enumerate(activities[:32]):
            tool.Structural.set_locks(activity, self.magnitude_locks[i], self.direction_locks[i])
        write_forces(forces)
        # Keep the resultant as locked, so that editing a force later solves the unknowns again to keep it.
        item, load_case = self.get_item_and_load_case()
        if item:
            tool.Structural.set_resultant(item, load_case, self.magnitude_locked, self.direction_locked, resultant)
            tool.Structural.set_resultant_eighth(item, load_case, get_chosen_eighth(self, resultant))
        return {"FINISHED"}

    def get_item_and_load_case(
        self,
    ) -> tuple[Union[ifcopenshell.entity_instance, None], Union[ifcopenshell.entity_instance, None]]:
        return get_resultant_item_and_load_case(self)

    def get_locked_resultant(self) -> Union[dict, None]:
        item, load_case = self.get_item_and_load_case()
        return tool.Structural.get_resultant(item, load_case) if item else None


class SetStructuralMomentCentre(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.set_structural_moment_centre"
    bl_label = "Take Moments About Selected Point"
    bl_description = (
        "Take the moments of the load case's point forces about the active point connection, as point A, "
        "drawn with their moment arms and in calculation reports"
    )
    bl_options = {"REGISTER", "UNDO"}
    clear: bpy.props.BoolProperty(name="Clear", default=False, options={"SKIP_SAVE"})

    @classmethod
    def description(cls, context, properties):
        return "Stop taking moments about a point" if properties.clear else cls.bl_description

    def _execute(self, context):
        props = tool.Structural.get_structural_props()
        try:
            group = tool.Ifc.get().by_id(int(props.load_group_to_show))
        except (ValueError, RuntimeError):
            self.report({"ERROR"}, "Choose a load case to show first")
            return {"CANCELLED"}
        centre = None
        if not self.clear:
            centre = tool.Ifc.get_entity(context.active_object) if context.active_object else None
            if not centre or not centre.is_a("IfcStructuralPointConnection"):
                self.report({"ERROR"}, "Select the point connection to take moments about")
                return {"CANCELLED"}
        tool.Structural.set_moment_centre(group, centre)
        redraw_loads(context)
        return {"FINISHED"}


# Where a moment centre was before Edit Moment Centre moved it to preview, by its object's name, to put it back.
MOMENT_CENTRE_PREVIEW: dict[str, Vector] = {}
# The loaded points Edit Moment Centre offers, kept referenced for Blender's enum, which does not copy them.
MOMENT_POINT_ITEMS: list[tuple[str, str, str]] = []


def get_moment_point_items(self: "EditStructuralMomentCentre", context: bpy.types.Context) -> list:
    MOMENT_POINT_ITEMS.clear()
    try:
        case = tool.Ifc.get().by_id(self.load_case)
    except RuntimeError:
        return MOMENT_POINT_ITEMS
    centre = tool.Structural.get_moment_centre(case)
    for item in tool.Structural.get_point_items(case):
        if item != centre:
            MOMENT_POINT_ITEMS.append((str(item.id()), item.Name or "Unnamed", "Measure the centre from this point"))
    return MOMENT_POINT_ITEMS


def get_moment_centre_objects(
    props: "EditStructuralMomentCentre",
) -> tuple[Union[bpy.types.Object, None], Union[bpy.types.Object, None]]:
    """The objects of the moment centre being edited and of the point it is measured from, if both have them"""
    ifc_file = tool.Ifc.get()
    try:
        case = ifc_file.by_id(props.load_case)
        point = ifc_file.by_id(int(props.point))
    except (RuntimeError, ValueError, TypeError):
        return None, None
    centre = tool.Structural.get_moment_centre(case)
    has_vertex = lambda obj: obj if obj and obj.type == "MESH" and obj.data.vertices else None
    return has_vertex(tool.Ifc.get_object(centre) if centre else None), has_vertex(tool.Ifc.get_object(point))


def get_vertex_location(obj: bpy.types.Object) -> Vector:
    return obj.matrix_world @ obj.data.vertices[0].co


# Set while the dialog fills its inputs from where A is, so that filling them does not move it.
MOMENT_CENTRE_FILLING: list[bool] = [False]


def get_moment_offset(props: "EditStructuralMomentCentre") -> tuple[float, float]:
    """Where A is from the point it is measured from, as entered: Δx and Δz, or a distance and its direction"""
    if props.input_mode == "COMPONENTS":
        return props.dx, props.dz
    return tool.Structural.get_in_plane_components(
        props.input_mode,
        magnitude=props.distance,
        angle=props.angle,
        rise=props.rise,
        run=props.run,
        direction=props.direction,
    )


# The inputs each input mode enters A by, which filling from where A is leaves alone while they are typed in.
MOMENT_MODE_INPUTS = {
    "COMPONENTS": ("dx", "dz"),
    "ANGLE": ("distance", "direction", "angle"),
    "SLOPE": ("distance", "direction", "rise", "run"),
}


def get_moment_arm_force(
    props: "EditStructuralMomentCentre",
) -> tuple[Union[Vector, None], Union[Vector, None]]:
    """The force whose moment arm the dialog edits, as X and Z, and where it acts, if one is"""
    try:
        activity = tool.Ifc.get().by_id(props.activity) if props.activity else None
    except RuntimeError:
        return None, None
    return get_moment_arm_force_of(activity) if activity else (None, None)


def get_moment_arm_force_of(
    activity: ifcopenshell.entity_instance,
) -> tuple[Union[Vector, None], Union[Vector, None]]:
    """An applied load's force, as X and Z, and where it acts, if it is a point force in the X-Z plane"""
    load = activity.AppliedLoad
    connects = activity.AssignedToStructuralItem if activity else None
    if not load or not load.is_a("IfcStructuralLoadSingleForce") or not connects:
        return None, None
    obj = tool.Ifc.get_object(connects[0].RelatingElement)
    force = Vector((load.ForceX or 0.0, 0.0, load.ForceZ or 0.0))
    if not obj or obj.type != "MESH" or not obj.data.vertices or not force.length:
        return None, None
    return force, get_vertex_location(obj)


def place_moment_centre(props: "EditStructuralMomentCentre", context: bpy.types.Context, x: float, z: float) -> None:
    """Move the moment centre to X and Z, keeping its Y, to preview the moments about it, and put it back on
    cancelling"""
    centre_obj, _ = get_moment_centre_objects(props)
    if not centre_obj:
        return
    MOMENT_CENTRE_PREVIEW.setdefault(centre_obj.name, centre_obj.matrix_world.translation.copy())
    at = get_vertex_location(centre_obj)
    centre_obj.matrix_world.translation += Vector((x, at.y, z)) - at
    context.view_layer.update()
    # A kept moment stays as A moves: its unknown is solved again, previewed as A is.
    case = tool.Ifc.get().by_id(props.load_case)
    if (kept := tool.Structural.get_resultant_moment(case)) is not None:
        forces, error = solve_case_moment(case, kept)
        ShaderInfo.preview = {} if error else {load.id(): get_force_attributes(load, f) for load, f in forces.items()}
    redraw_loads(context)


def move_moment_centre(props: "EditStructuralMomentCentre", context: bpy.types.Context) -> None:
    """Move the moment centre to where it is entered from the point it is measured from"""
    if MOMENT_CENTRE_FILLING[0]:
        return
    _, point_obj = get_moment_centre_objects(props)
    if not point_obj:
        return
    dx, dz = get_moment_offset(props)
    point = get_vertex_location(point_obj)
    place_moment_centre(props, context, point.x + dx, point.z + dz)
    fill_moment_inputs(props, context, MOMENT_MODE_INPUTS[props.input_mode])


def move_moment_arm(props: "EditStructuralMomentCentre", context: bpy.types.Context) -> None:
    """Slide the moment centre along a force's moment arm to the arm's length entered, keeping the arm's foot on
    the line of action"""
    centre_obj, _ = get_moment_centre_objects(props)
    force, point = get_moment_arm_force(props)
    if MOMENT_CENTRE_FILLING[0] or not centre_obj or not force:
        return
    at = get_vertex_location(centre_obj)
    _, _, foot = tool.Structural.get_moment(np.array(at), np.array(point), np.array(force))
    away = Vector((at.x - foot[0], 0.0, at.z - foot[2]))
    if not away.length:
        return  # On the line of action: no side of it to slide out to.
    target = Vector(foot) + away.normalized() * props.arm
    place_moment_centre(props, context, target.x, target.z)
    fill_moment_inputs(props, context, ("arm",))


def move_moment_angle(props: "EditStructuralMomentCentre", context: bpy.types.Context) -> None:
    """Swing the moment centre round a force's point to the angle phi entered between r and the line of action"""
    swing_moment_centre(props, context, props.phi, "phi")


def move_moment_alpha(props: "EditStructuralMomentCentre", context: bpy.types.Context) -> None:
    """Swing the moment centre to the angle alpha entered at it, between r and the arm, 90 degrees less phi"""
    swing_moment_centre(props, context, 90.0 - props.alpha, "alpha")


def swing_moment_centre(
    props: "EditStructuralMomentCentre", context: bpy.types.Context, phi: float, typed: str
) -> None:
    """Swing the moment centre round a force's point to an angle phi between r and the line of action, keeping r's
    length and the side of the line A is on, leaving the input typed in as it is"""
    centre_obj, _ = get_moment_centre_objects(props)
    force, point = get_moment_arm_force(props)
    if MOMENT_CENTRE_FILLING[0] or not centre_obj or not force:
        return
    r = get_vertex_location(centre_obj) - point
    r.y = 0.0
    along = force.normalized() * (1 if r.dot(force) >= 0 else -1)  # The line of action, towards A.
    across = Vector((-along.z, 0.0, along.x))
    across *= -1 if r.dot(across) < 0 else 1
    angle = math.radians(phi)
    target = point + r.length * (along * math.cos(angle) + across * math.sin(angle))
    place_moment_centre(props, context, target.x, target.z)
    fill_moment_inputs(props, context, (typed,))


def fill_moment_inputs(
    props: "EditStructuralMomentCentre", context: bpy.types.Context, keep: tuple[str, ...] = ()
) -> None:
    """Fill the inputs from where A is now, as Edit Load fills a force's, so that another point or input mode
    reads the same place rather than moving it.

    :param keep: Inputs being typed in, left as they are, so that an angle typed does not jump to the next
        eighth's.
    """
    centre_obj, point_obj = get_moment_centre_objects(props)
    if not centre_obj or not point_obj:
        return
    at, point = get_vertex_location(centre_obj), get_vertex_location(point_obj)
    dx, dz = at.x - point.x, at.z - point.z
    values = {"dx": dx, "dz": dz, "distance": math.hypot(dx, dz)}
    if dx or dz:
        values["direction"], values["angle"], _, _ = tool.Structural.get_eighth(dx, dz)
        values["rise"], values["run"] = tool.Structural.get_simple_slope(abs(dx), abs(dz))
    force, force_point = get_moment_arm_force(props)
    if force:
        _, arm, foot = tool.Structural.get_moment(np.array(at), np.array(force_point), np.array(force))
        values["arm"] = arm
        r, to_foot = at - force_point, Vector(foot) - force_point
        r.y = to_foot.y = 0.0
        values["phi"] = 90.0 if not to_foot.length or not r.length else math.degrees(r.angle(to_foot))
        values["alpha"] = 90.0 - values["phi"]
    MOMENT_CENTRE_FILLING[0] = True
    try:
        for name, value in values.items():
            if name not in keep:
                setattr(props, name, value)
    finally:
        MOMENT_CENTRE_FILLING[0] = False


def refill_moment_inputs(props: "EditStructuralMomentCentre", context: bpy.types.Context) -> None:
    """Fill every input from where A is: an update callback, which Blender requires to take exactly two
    arguments, so fill_moment_inputs, which takes more, cannot be one"""
    fill_moment_inputs(props, context)


class EditStructuralMomentCentre(
    bpy.types.Operator,
    tool.Ifc.Operator,
    get_direction_input("A, from the point,", move_moment_centre, {"SKIP_SAVE"}),
):
    bl_idname = "bim.edit_structural_moment_centre"
    bl_label = "Edit Moment Centre"
    bl_description = (
        "Move the point moments are taken about, A, by its distance and direction from a loaded point, as a force "
        "is entered, or by a force's moment arm, previewing the moments"
    )
    bl_options = {"REGISTER", "UNDO"}
    load_case: bpy.props.IntProperty(options={"HIDDEN", "SKIP_SAVE"})
    # The point to measure from first, as the one whose moment was clicked, if any.
    from_point: bpy.props.IntProperty(options={"HIDDEN", "SKIP_SAVE"})
    # The applied load whose moment arm is edited, as the one whose moment was clicked, if any.
    activity: bpy.props.IntProperty(options={"HIDDEN", "SKIP_SAVE"})
    # The value to start editing, as the label clicked stands for, as Edit Load's focus.
    focus: bpy.props.StringProperty(options={"HIDDEN", "SKIP_SAVE"})
    point: bpy.props.EnumProperty(
        name="From",
        description="The loaded point A is placed from",
        items=get_moment_point_items,
        update=refill_moment_inputs,
    )
    input_mode: bpy.props.EnumProperty(
        name="Input",
        items=[
            ("COMPONENTS", "Components", "Δx and Δz, from the point to A"),
            ("ANGLE", "Angle", "Distance and angle, from the point to A"),
            ("SLOPE", "Slope", "Distance and rise over run, from the point to A"),
        ],
        update=refill_moment_inputs,
    )
    distance: bpy.props.FloatProperty(
        name="Distance", description="From the point to A", subtype="DISTANCE", update=move_moment_centre
    )
    dx: bpy.props.FloatProperty(
        name="Δx to A",
        description="From the point to A, along X. The report's table measures the other way, from A to the point",
        subtype="DISTANCE",
        update=move_moment_centre,
    )
    dz: bpy.props.FloatProperty(
        name="Δz to A",
        description="From the point to A, along Z. The report's table measures the other way, from A to the point",
        subtype="DISTANCE",
        update=move_moment_centre,
    )
    arm: bpy.props.FloatProperty(
        name="d",
        description="The moment arm: from A square to the force's line of action. A slides along it",
        subtype="DISTANCE",
        min=0.0,
        update=move_moment_arm,
    )
    phi: bpy.props.FloatProperty(
        name="φ",
        description="Degrees between r, from the force's point to A, and its line of action. A swings round the point",
        min=0.0,
        max=90.0,
        update=move_moment_angle,
    )
    arm_locked: bpy.props.BoolProperty(
        name="d Known", description="Whether the moment arm is known. If not, a kept moment finds it", default=True
    )
    angle_locked: bpy.props.BoolProperty(
        name="Angle Known",
        description="Whether the angle of r, and with it φ and α, is known. If not, a kept moment finds it",
        default=True,
    )
    reach_locked: bpy.props.BoolProperty(
        name="r Known", description="Whether r's length is known. If not, a kept moment finds it", default=True
    )
    alpha: bpy.props.FloatProperty(
        name="α",
        description="Degrees at A between r and the moment arm, 90 less φ. A swings round the force's point",
        min=0.0,
        max=90.0,
        update=move_moment_alpha,
    )

    def invoke(self, context, event):
        MOMENT_CENTRE_PREVIEW.clear()
        items = get_moment_point_items(self, context)
        if not items:
            self.report({"ERROR"}, "The load case has no loaded points to measure the moment centre from")
            return {"CANCELLED"}
        ids = [item[0] for item in items]
        self.point = str(self.from_point) if str(self.from_point) in ids else ids[0]
        if not self.activity:
            # The force at the point measured from, if it is the only one there, for its moment arm.
            case, point = tool.Ifc.get().by_id(self.load_case), tool.Ifc.get().by_id(int(self.point))
            forces = [a for a in tool.Structural.get_chain_activities(point, case) if get_moment_arm_force_of(a)[0]]
            self.activity = forces[0].id() if len(forces) == 1 else 0
        # A value clicked opens in the input mode that enters it, ready to type over.
        modes = {"dx": "COMPONENTS", "dz": "COMPONENTS", "angle": "ANGLE", "rise": "SLOPE", "run": "SLOPE"}
        if mode := modes.get(self.focus):
            self.input_mode = mode
        elif self.focus == "distance" and self.input_mode == "COMPONENTS":
            self.input_mode = "ANGLE"
        self.focus = self.focus or ("dx" if self.input_mode == "COMPONENTS" else "distance")
        # Which of A's place a kept moment finds, if it is from this force's point.
        kind, activity = tool.Structural.get_moment_centre_unknown(tool.Ifc.get().by_id(self.load_case))
        mine = activity is not None and activity.id() == self.activity
        self.arm_locked, self.angle_locked, self.reach_locked = (
            not (mine and kind == k) for k in ("ARM", "SWING", "REACH")
        )
        fill_moment_inputs(self.properties, context)
        if not get_moment_centre_objects(self)[0]:
            self.report({"ERROR"}, "The load case takes moments about no point")
            return {"CANCELLED"}
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        if len(MOMENT_POINT_ITEMS) > 1:
            layout.prop(self, "point")
        layout.row().prop(self, "input_mode", expand=True)
        if self.input_mode == "COMPONENTS":
            draw_with_lock(layout, self, ("dx",), focus=self.focus)
            draw_with_lock(layout, self, ("dz",), focus=self.focus)
        else:
            self.draw_direction_inputs(layout)
            draw_with_lock(layout, self, ("distance",), focus=self.focus)
            dx, dz = get_moment_offset(self)
            length_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
            unit = get_project_unit_symbol("LENGTHUNIT", "m")
            text = f"To A: Δx = {dx / length_scale:.4f}   Δz = {dz / length_scale:.4f} {unit}"
            layout.label(text=text, icon="ORIENTATION_GLOBAL")
        if get_moment_arm_force(self)[0]:
            box = layout.box()
            load = tool.Ifc.get().by_id(self.activity).AppliedLoad
            box.label(text=f"Moment Arm of {load.Name or 'Unnamed'}")
            draw_with_lock(box, self, ("arm",), "arm_locked", focus=self.focus)
            draw_with_lock(box, self, ("phi",), "angle_locked", focus=self.focus)
            draw_with_lock(box, self, ("alpha",), "angle_locked", focus=self.focus)
            row = box.row(align=True)
            force, point = get_moment_arm_force(self)
            centre_obj, _ = get_moment_centre_objects(self)
            length_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
            reach = (get_vertex_location(centre_obj) - point).length / length_scale if centre_obj else 0.0
            row.label(text=f"r = {reach:.4f} {get_project_unit_symbol('LENGTHUNIT', 'm')}")
            row.prop(self, "reach_locked", text="", icon="LOCKED" if self.reach_locked else "UNLOCKED")
            unlocked = [not lock for lock in (self.arm_locked, self.angle_locked, self.reach_locked)]
            if sum(unlocked) > 1:
                box.label(text="Unlock one of d, the angle and r: a kept moment finds one", icon="ERROR")
            elif any(unlocked) and tool.Structural.get_resultant_moment(tool.Ifc.get().by_id(self.load_case)) is None:
                box.label(text="Found once ΣM_A is kept, in Edit Resultant Moment", icon="INFO")
        case = tool.Ifc.get().by_id(self.load_case)
        centre = tool.Structural.get_moment_centre(case)
        kept = tool.Structural.get_resultant_moment(case)
        moment = kept if kept is not None else tool.Structural.get_moment_about(case, centre) if centre else None
        if moment is not None:
            decimals = tool.Structural.get_structural_props().force_decimals
            unit = f"{get_project_unit_symbol('FORCEUNIT', 'N')}.{get_project_unit_symbol('LENGTHUNIT', 'm')}"
            text = f"ΣM_A = {moment:+.{decimals}f} {unit}"  # Counter-clockwise positive.
            if kept is not None:
                text += "  🔒 kept: the unknown force follows"
            layout.label(text=text, icon="FORCE_VORTEX")

    def cancel(self, context):
        restore_moment_centre(context)

    def _execute(self, context):
        centre_obj, _ = get_moment_centre_objects(self)
        case = tool.Ifc.get().by_id(self.load_case)
        if get_moment_arm_force(self)[0]:
            unlocked = [
                k
                for k, lock in (("ARM", self.arm_locked), ("SWING", self.angle_locked), ("REACH", self.reach_locked))
                if not lock
            ]
            if len(unlocked) > 1:
                self.report({"ERROR"}, "Unlock one of d, the angle and r: a kept moment finds one")
                return {"CANCELLED"}
            # The unknown of A's place, from this force's point, or none; another force's is left as it is.
            kind, activity = tool.Structural.get_moment_centre_unknown(case)
            mine = activity is not None and activity.id() == self.activity and kind in ("ARM", "REACH", "SWING")
            if unlocked or mine:  # A force's position, found in Edit Resultant Moment, is left as it is.
                activity = tool.Ifc.get().by_id(self.activity)
                tool.Structural.set_moment_centre_unknown(case, unlocked[0] if unlocked else None, activity)
        MOMENT_CENTRE_PREVIEW.clear()  # A is where the preview left it.
        ShaderInfo.preview = {}  # The kept moment's forces are written below.
        if centre_obj:
            bonsai.core.geometry.edit_object_placement(tool.Ifc, tool.Geometry, tool.Surveyor, obj=centre_obj)
        keep_resultant_moments(get_case_moment_forces(tool.Ifc.get().by_id(self.load_case))[0])
        redraw_loads(context)
        return {"FINISHED"}


def get_case_moment_forces(
    case: ifcopenshell.entity_instance,
) -> tuple[list[ifcopenshell.entity_instance], list[np.ndarray], list[np.ndarray]]:
    """A load case's point forces, as their applied loads, where each acts from the moment centre, in the project's
    length unit, and the force, by point name and then tip-to-tail order, as moments number them"""
    activities, arms, forces = [], [], []
    centre = tool.Structural.get_moment_centre(case)
    has_vertex = lambda obj: obj and obj.type == "MESH" and obj.data.vertices
    if not centre or not has_vertex(centre_obj := tool.Ifc.get_object(centre)):
        return activities, arms, forces
    length_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
    at = np.array(get_vertex_location(centre_obj))
    for item in tool.Structural.get_point_items(case):
        if not has_vertex(obj := tool.Ifc.get_object(item)):
            continue
        for activity in tool.Structural.get_chain_activities(item, case):
            if (load := activity.AppliedLoad) and load.is_a("IfcStructuralLoadSingleForce"):
                activities.append(activity)
                arms.append((np.array(get_vertex_location(obj)) - at) / length_scale)
                forces.append(np.array(get_force(load)))
    return activities, arms, forces


def solve_case_moment(
    case: ifcopenshell.entity_instance,
    moment: float,
    locks: Union[list[tuple[bool, bool]], None] = None,
    overrides: Union[dict[int, tuple], None] = None,
    lock_overrides: Union[dict[int, tuple[bool, bool]], None] = None,
) -> tuple[dict[ifcopenshell.entity_instance, tuple], str]:
    """The loads whose forces change for a load case's moments to sum to a moment, with their new forces, and why
    not if they cannot. Locks are the applied loads' own unless given.

    :param overrides: Forces by applied load id to use in place of their own, as one being edited.
    :param lock_overrides: Locks by applied load id to use in place of their own, as one being edited.
    """
    activities, arms, forces = get_case_moment_forces(case)
    if not activities:
        return {}, "The load case takes moments about no point, or has no point forces"
    overrides, lock_overrides = overrides or {}, lock_overrides or {}
    forces = [np.array(overrides.get(a.id(), f), dtype=float) for a, f in zip(activities, forces)]
    locks = locks or [lock_overrides.get(a.id(), tool.Structural.get_locks(a)) for a in activities]
    links, factors = tool.Structural.get_magnitude_links(activities)
    solved, error = tool.Structural.solve_moment_unknown(arms, forces, locks, moment, links, factors)
    changed = {
        activity.AppliedLoad: tuple(float(c) for c in new)
        for activity, old, new in zip(activities, forces, solved)
        if not np.allclose(old, new)
    }
    return changed, error


# The words for which place is found, by its kind: of A, or of a force.
CENTRE_UNKNOWN_WORDS = {
    "ARM": "moment arm d",
    "REACH": "distance r",
    "SWING": "angle of r (φ, α)",
    "POINT_X": "point along X",
    "POINT_Z": "point along Z",
    "POINT_REACH": "point along the line from A",
    "POINT_SWING": "point round A",
}


def solve_case_place(
    case: ifcopenshell.entity_instance,
    moment: float,
    unknown: Union[tuple[Union[str, None], Union[ifcopenshell.entity_instance, None]], None] = None,
    locks: Union[list[tuple[bool, bool]], None] = None,
) -> tuple[Union[bpy.types.Object, None], Union[np.ndarray, None], str]:
    """Where the moment centre, or a force's point, must be, in the project's length unit, for a load case's
    moments to sum to a moment, if a place is its unknown: the object to move there, and why not if it cannot be.

    :param unknown: The kind and applied load of the place to find, if not the load case's own, as a dialog has it.
    :param locks: The forces' locks, if not their own, as a dialog has them.
    """
    kind, activity = unknown or tool.Structural.get_moment_centre_unknown(case)
    if not kind:
        return None, None, ""
    activities, arms, forces = get_case_moment_forces(case)
    if activity not in activities:
        return None, None, "The force the place is found from is no longer in the load case"
    if error := get_unlocked_values_error(activities, locks):
        return None, None, error
    at = get_case_centre_location(case)
    points = [arm + at for arm in arms]
    j = activities.index(activity)
    if kind in ("POINT_X", "POINT_Z", "POINT_REACH", "POINT_SWING"):
        # The force's point moves, its loads with it; A stays.
        place, error = tool.Structural.solve_force_point(points, forces, at, moment, j, kind.split("_", 1)[1])
        obj = tool.Ifc.get_object(activity.AssignedToStructuralItem[0].RelatingElement)
        return obj, place, error
    place, error = tool.Structural.solve_centre_position(points, forces, at, moment, kind, j)
    return tool.Ifc.get_object(tool.Structural.get_moment_centre(case)), place, error


def get_unlocked_values_error(
    activities: list[ifcopenshell.entity_instance], locks: Union[list[tuple[bool, bool]], None] = None
) -> str:
    """Why a place cannot be the unknown, if a force's value is unknown too, naming it, from the forces' locks or
    those given"""
    locks = locks or [tool.Structural.get_locks(a) for a in activities]
    unlocked = [
        f"F{i + 1} {kind}"
        for i, lock in enumerate(locks)
        for kind, known in zip(("magnitude", "direction"), lock)
        if not known
    ]
    if not unlocked:
        return ""
    return f"A place is unknown, and so is {', '.join(unlocked)}: a moment finds one value; lock {'it' if len(unlocked) == 1 else 'them'}"


def get_case_centre_location(case: ifcopenshell.entity_instance) -> np.ndarray:
    """Where a load case's moment centre is, in the project's length unit"""
    obj = tool.Ifc.get_object(tool.Structural.get_moment_centre(case))
    return np.array(get_vertex_location(obj)) / ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())


def move_to_place(obj: bpy.types.Object, place: np.ndarray, context: bpy.types.Context, preview: bool = False) -> None:
    """Move a point, the moment centre or a force's, to where it is found, in the project's length unit: to preview
    it, to be put back on cancelling, or for good, written to the IFC"""
    if preview:
        MOMENT_CENTRE_PREVIEW.setdefault(obj.name, obj.matrix_world.translation.copy())
    target = Vector(place) * ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
    if (target - get_vertex_location(obj)).length < 1e-9:
        return  # Where it is already: moving it would only set off another solve after moves.
    obj.matrix_world.translation += target - get_vertex_location(obj)
    context.view_layer.update()
    if not preview:
        bonsai.core.geometry.edit_object_placement(tool.Ifc, tool.Geometry, tool.Surveyor, obj=obj)


def get_moved_activities(items: list[ifcopenshell.entity_instance]) -> list[ifcopenshell.entity_instance]:
    """The applied loads whose kept moments moving these structural items can change: their own, and those of
    each load case taking moments about one of them"""
    activities = [r.RelatedStructuralActivity for item in items for r in item.AssignedStructuralActivity or []]
    for group in tool.Ifc.get().by_type("IfcStructuralLoadGroup"):
        if tool.Structural.get_moment_centre(group) in items:
            activities += get_case_moment_forces(group)[0]
    return [a for a in activities if a]


def get_kept_moment_cases(items: list[ifcopenshell.entity_instance]) -> list[ifcopenshell.entity_instance]:
    """The load cases keeping a sum of moments that moving these structural items changes"""
    cases = {group for activity in get_moved_activities(items) for group in get_activity_load_groups(activity)}
    return [case for case in cases if tool.Structural.get_resultant_moment(case) is not None]


def get_kept_moment_preview(items: list[ifcopenshell.entity_instance]) -> dict[int, dict]:
    """The forces kept moments solve to, as these structural items are being moved, to draw before the move is
    done and they are written; a place found, rather than a force, waits for the move to finish"""
    preview = {}
    for case in get_kept_moment_cases(items):
        if tool.Structural.get_moment_centre_unknown(case)[0]:
            continue
        forces, error = solve_case_moment(case, tool.Structural.get_resultant_moment(case))
        if not error:
            preview |= {load.id(): get_force_attributes(load, force) for load, force in forces.items()}
    return preview


def keep_resultant_moments(activities: list[ifcopenshell.entity_instance]) -> None:
    """Solve again the unknown of each load case these applied loads are in that keeps a sum of moments, as a
    locked resultant is kept, after a force or the moment centre changes: a force's value, or a place"""
    cases = {group for activity in activities for group in get_activity_load_groups(activity)}
    for case in cases:
        if (moment := tool.Structural.get_resultant_moment(case)) is None:
            continue
        if tool.Structural.get_moment_centre_unknown(case)[0]:
            obj, place, error = solve_case_place(case, moment)
            if not error:
                move_to_place(obj, place, bpy.context)
            continue
        forces, error = solve_case_moment(case, moment)
        if not error:
            write_forces(forces)


def get_resultant_moment_locks(props: "EditStructuralResultantMoment") -> list[tuple[bool, bool]]:
    count = len(get_case_moment_forces(tool.Ifc.get().by_id(props.load_case))[0])
    return list(zip(props.magnitude_locks[:count], props.direction_locks[:count]))


def get_dialog_place_unknown(
    props: "EditStructuralResultantMoment",
) -> tuple[Union[str, None], Union[ifcopenshell.entity_instance, None], str]:
    """The place Edit Resultant Moment finds, as its padlocks have it: a force's point along X or Z unlocked
    there, or else the load case's own unknown place, unless it is a force's point locked there. With why not, if
    several."""
    case = tool.Ifc.get().by_id(props.load_case)
    activities = get_case_moment_forces(case)[0][:32]
    unlocked = [
        (kind, a)
        for i, a in enumerate(activities)
        for kind, locks in (("POINT_X", props.position_locks), ("POINT_Z", props.position_z_locks))
        if not locks[i]
    ]
    if len(unlocked) > 1:
        return None, None, "Unlock one force position, X or Z: a moment finds one value"
    if unlocked:
        return unlocked[0][0], unlocked[0][1], ""
    kind, activity = tool.Structural.get_moment_centre_unknown(case)
    # A force's point along X or Z is the padlocks' here; along or round A, Edit Load's, so kept.
    return (None, None, "") if kind in ("POINT_X", "POINT_Z") else (kind, activity, "")


def get_signed_moment(props: "EditStructuralResultantMoment") -> float:
    return props.moment


def solve_resultant_moment(
    props: "EditStructuralResultantMoment",
) -> tuple[dict[ifcopenshell.entity_instance, tuple], str]:
    """The forces Edit Resultant Moment changes, as solve_case_moment gives them, or none with the sum unlocked, as
    it is then found from the forces, which must all be known, or with a place to find"""
    case = tool.Ifc.get().by_id(props.load_case)
    locks = get_resultant_moment_locks(props)
    kind, activity, error = get_dialog_place_unknown(props)
    if error:
        return {}, error
    if kind and not props.moment_locked:
        return {}, "ΣM_A is unlocked, so found from the forces: lock their positions, or lock ΣM_A to find one"
    if props.moment_locked and kind:
        # It moves; no force does. With the dialog's padlocks, not those last kept.
        return {}, solve_case_place(case, get_signed_moment(props), (kind, activity), locks)[2]
    if props.moment_locked:
        return solve_case_moment(case, get_signed_moment(props), locks)
    if not all(locked for lock in locks for locked in lock):
        return {}, "ΣM_A is unlocked, so found from the forces: lock their values, or lock ΣM_A to find one"
    return {}, ""


def update_resultant_moment(props: "EditStructuralResultantMoment", context: bpy.types.Context) -> None:
    """Preview the forces, or the place, found for the moment entered, moments redrawn with them"""
    if not props.is_previewing:
        return
    forces, error = solve_resultant_moment(props)
    ShaderInfo.preview = {} if error else {load.id(): get_force_attributes(load, f) for load, f in forces.items()}
    restore_moment_centre(context)  # Solved from where things were, not from the last preview.
    kind, activity, _ = get_dialog_place_unknown(props)
    if props.moment_locked and not error and kind:
        case = tool.Ifc.get().by_id(props.load_case)
        locks = get_resultant_moment_locks(props)
        obj, place, _ = solve_case_place(case, get_signed_moment(props), (kind, activity), locks)
        move_to_place(obj, place, context, preview=True)
    redraw_loads(context)


class EditStructuralResultantMoment(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.edit_structural_resultant_moment"
    bl_label = "Edit Resultant Moment"
    bl_description = (
        "Set the sum of the moments about A, finding the one force magnitude or direction unlocked, and keep it as "
        "forces change"
    )
    bl_options = {"REGISTER", "UNDO"}
    load_case: bpy.props.IntProperty(options={"HIDDEN", "SKIP_SAVE"})
    moment: bpy.props.FloatProperty(
        name="ΣM_A",
        description="The sum of the moments about A, counter-clockwise positive",
        update=update_resultant_moment,
    )
    moment_locked: bpy.props.BoolProperty(
        name="ΣM_A Known",
        description="Whether the sum of the moments is known, finding a force's value and kept as forces change, or "
        "found from the forces",
        default=True,
        options={"SKIP_SAVE"},
        update=update_resultant_moment,
    )
    magnitude_locks: bpy.props.BoolVectorProperty(
        name="Magnitude Known",
        description="Whether this force's magnitude is known. If not, it is found",
        size=32,
        default=[True] * 32,
        options={"SKIP_SAVE"},
        update=update_resultant_moment,
    )
    direction_locks: bpy.props.BoolVectorProperty(
        name="Direction Known",
        description="Whether this force's direction is known. If not, it is found",
        size=32,
        default=[True] * 32,
        options={"SKIP_SAVE"},
        update=update_resultant_moment,
    )
    position_locks: bpy.props.BoolVectorProperty(
        name="X Position Known",
        description="Whether where this force acts along X is known. If not, its point moves to make the moment",
        size=32,
        default=[True] * 32,
        options={"SKIP_SAVE"},
        update=update_resultant_moment,
    )
    position_z_locks: bpy.props.BoolVectorProperty(
        name="Z Position Known",
        description="Whether where this force acts along Z is known. If not, its point moves to make the moment",
        size=32,
        default=[True] * 32,
        options={"SKIP_SAVE"},
        update=update_resultant_moment,
    )
    is_previewing: bpy.props.BoolProperty(options={"HIDDEN", "SKIP_SAVE"})

    def invoke(self, context, event):
        case = tool.Ifc.get().by_id(self.load_case)
        activities = get_case_moment_forces(case)[0][:32]
        if not activities:
            self.report({"ERROR"}, "The load case takes moments about no point, or has no point forces")
            return {"CANCELLED"}
        kept = tool.Structural.get_resultant_moment(case)
        moment = (
            kept
            if kept is not None
            else tool.Structural.get_moment_about(case, tool.Structural.get_moment_centre(case))
        )
        self.moment = moment or 0.0
        locks = [tool.Structural.get_locks(activity) for activity in activities]
        self.magnitude_locks = [lock[0] for lock in locks] + [True] * (32 - len(locks))
        self.direction_locks = [lock[1] for lock in locks] + [True] * (32 - len(locks))
        kind, unknown = tool.Structural.get_moment_centre_unknown(case)
        rest = [True] * (32 - len(activities))
        self.position_locks = [not (kind == "POINT_X" and a == unknown) for a in activities] + rest
        self.position_z_locks = [not (kind == "POINT_Z" and a == unknown) for a in activities] + rest
        self.moment_locked = kept is not None or not all(locked for lock in locks for locked in lock)
        self.is_previewing = True  # Set last, so that filling in the values above does not start a preview.
        update_resultant_moment(self.properties, context)
        return context.window_manager.invoke_props_dialog(self, width=380)

    def draw(self, context):
        layout = self.layout
        case = tool.Ifc.get().by_id(self.load_case)
        centre = tool.Structural.get_moment_centre(case)
        unit = f"{get_project_unit_symbol('FORCEUNIT', 'N')}.{get_project_unit_symbol('LENGTHUNIT', 'm')}"
        layout.label(text=f"About A: {centre.Name or 'Unnamed'}" if centre else "About A", icon="FORCE_VORTEX")
        row = layout.row(align=True)
        if self.moment_locked:
            values = row.row(align=True)
            values.activate_init = True
            values.prop(self, "moment", text=f"ΣM_A ({unit})")
        else:
            # Found from the forces as they are, so shown rather than entered.
            found = tool.Structural.get_moment_about(case, centre) if centre else None
            text = "ΣM_A: found from the forces"
            if found is not None:
                text = f"ΣM_A = {found:+.2f} {unit}  (found)"
            row.label(text=text)
        row.prop(self, "moment_locked", text="", icon="LOCKED" if self.moment_locked else "UNLOCKED")
        layout.label(text="Forces, and which of their values are known:")
        activities = get_case_moment_forces(case)[0][:32]
        for i, activity in enumerate(activities):
            row = layout.row(align=True)
            symbol = "F" + str(i + 1).translate(str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉"))
            row.label(text=f"{symbol}: {activity.AppliedLoad.Name or 'Unnamed'}", icon="FORCE_FORCE")
            for prop, text in (
                ("magnitude_locks", "Magnitude"),
                ("direction_locks", "Direction"),
                ("position_locks", "X"),
                ("position_z_locks", "Z"),
            ):
                locked = getattr(self, prop)[i]
                row.prop(self, prop, index=i, text=text, icon="LOCKED" if locked else "UNLOCKED")
        kind, activity, _ = get_dialog_place_unknown(self)
        if kind and kind not in ("POINT_X", "POINT_Z", "POINT_REACH", "POINT_SWING"):
            number = activities.index(activity) + 1 if activity in activities else 0
            row = layout.row()
            row.label(text=f"A's place: the {CENTRE_UNKNOWN_WORDS[kind]} of F{number} is found", icon="UNLOCKED")
        forces, error = solve_resultant_moment(self)
        if error:
            layout.label(text=error, icon="ERROR")
            return
        box = layout.box()
        if kind and self.moment_locked:
            name = activity.AppliedLoad.Name or "The force"
            text = f"{name} moves" if kind in ("POINT_X", "POINT_Z", "POINT_REACH", "POINT_SWING") else "A moves"
            box.label(text=f"{text} to make this moment; no force's value changes", icon="FORCE_VORTEX")
            return
        force_unit = get_project_unit_symbol("FORCEUNIT", "N")
        for load, force in forces.items():
            old = get_force(load)
            new = math.copysign(math.hypot(*force), sum(a * b for a, b in zip(force, old)))
            box.label(text=f"{load.Name or 'Unnamed'}: {get_force_name(force, force_unit)}")
            if new < 0:
                box.label(text="  reverses its direction (a pull becomes a push)", icon="ERROR")
        if not forces and self.moment_locked:
            box.label(text="The forces already make this moment", icon="CHECKMARK")
        elif not forces:
            box.label(text="No force changes; ΣM_A is no longer kept", icon="INFO")

    def cancel(self, context):
        clear_previews(context)
        restore_moment_centre(context)

    def _execute(self, context):
        ShaderInfo.preview = {}  # The edit below refreshes the shown loads.
        restore_moment_centre(context)  # Moved for good below, if its place is the unknown.
        case = tool.Ifc.get().by_id(self.load_case)
        locks = get_resultant_moment_locks(self)
        forces, error = solve_resultant_moment(self)
        if error:
            self.report({"ERROR"}, error)
            return {"CANCELLED"}
        for activity, (magnitude, direction) in zip(get_case_moment_forces(case)[0], locks):
            tool.Structural.set_locks(activity, magnitude, direction)
        write_forces(forces)
        # A force's position unlocked here is the load case's unknown place; one locked here no longer is.
        kind, activity, _ = get_dialog_place_unknown(self)
        points = ("POINT_X", "POINT_Z")
        if kind in points or tool.Structural.get_moment_centre_unknown(case)[0] in points:
            tool.Structural.set_moment_centre_unknown(case, kind, activity)
        if self.moment_locked and kind:
            obj, place, _ = solve_case_place(case, get_signed_moment(self), (kind, activity), locks)
            move_to_place(obj, place, context)
        # Kept, so that changing a force or the moment centre later solves the unknown again to keep it; or, found
        # from the forces, no longer kept.
        tool.Structural.set_resultant_moment(case, get_signed_moment(self) if self.moment_locked else None)
        redraw_loads(context)
        return {"FINISHED"}


def get_project_unit_symbol(unit_type: str, default: str) -> str:
    unit = ifcopenshell.util.unit.get_project_unit(tool.Ifc.get(), unit_type)
    return ifcopenshell.util.unit.get_unit_symbol(unit) if unit else default


def restore_moment_centre(context: bpy.types.Context) -> None:
    """Put a moment centre moved to preview back where it was"""
    for name, translation in MOMENT_CENTRE_PREVIEW.items():
        if obj := bpy.data.objects.get(name):
            obj.matrix_world.translation = translation
    MOMENT_CENTRE_PREVIEW.clear()
    ShaderInfo.preview = {}  # And the forces a kept moment solved for as it moved.
    context.view_layer.update()
    redraw_loads(context)


class KeepStructuralMoments(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.keep_structural_moments"
    bl_label = "Keep Moments"
    bl_description = "Solve again the unknowns of kept moments that moving these structural items changes"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}
    items: bpy.props.StringProperty(description="Ids of the structural items moved", options={"SKIP_SAVE"})

    def _execute(self, context):
        ifc_file = tool.Ifc.get()
        items = []
        for item_id in self.items.split(","):
            try:
                items.append(ifc_file.by_id(int(item_id)))
            except (ValueError, RuntimeError):
                continue  # Removed since it moved.
        ShaderInfo.preview = {}  # The forces solved while it moved are written now.
        keep_resultant_moments(get_moved_activities(items))
        redraw_loads(context)
        return {"FINISHED"}


class ExportStructuralCalculations(bpy.types.Operator):
    bl_idname = "bim.export_structural_calculations"
    bl_label = "Export Calculations"
    bl_description = (
        "Write the current analysis model's calculations, with diagrams, as HTML to print and as Markdown, "
        "into a folder in the one chosen"
    )
    directory: bpy.props.StringProperty(subtype="DIR_PATH")
    filter_folder: bpy.props.BoolProperty(default=True, options={"HIDDEN", "SKIP_SAVE"})
    selected_only: bpy.props.BoolProperty(
        name="Selected Items Only", description="Report only the structural items selected", default=False
    )

    @classmethod
    def poll(cls, context):
        if not tool.Structural.get_current_structural_analysis_model():
            cls.poll_message_set("Choose a current analysis model")
            return False
        return True

    def invoke(self, context, event):
        if ifc_path := tool.Ifc.get_path():
            self.directory = str(Path(ifc_path).parent)
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def execute(self, context):
        from bonsai.bim.module.structural import report

        model = tool.Structural.get_current_structural_analysis_model()
        items = None
        if self.selected_only:
            items = {e for o in context.selected_objects if (e := tool.Ifc.get_entity(o))}
        folder = Path(self.directory) / f"{report.get_slug(model.Name)}_calcs"
        page = report.write_report(folder, model, items, tool.Structural.get_structural_props().report_detailed_steps)
        webbrowser.open(page.as_uri())
        self.report({"INFO"}, f"Calculations written to {folder}")
        return {"FINISHED"}


class ShowStructuralLoadCase(bpy.types.Operator):
    bl_idname = "bim.show_structural_load_case"
    bl_label = "Show Load Case"
    bl_description = "Show the loads of this load case in the viewport, or stop showing them if they are shown"
    bl_options = {"REGISTER"}
    load_case: bpy.props.IntProperty()

    def execute(self, context):
        props = tool.Structural.get_structural_props()
        if props.show_loads and props.load_group_to_show == str(self.load_case):
            props.show_loads = False
            return {"FINISHED"}
        try:
            props.load_group_to_show = str(self.load_case)
        except TypeError:
            self.report({"WARNING"}, "This load case is not in the current analysis model.")
            return {"CANCELLED"}
        props.show_loads = True
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
        if props.show_unused_loads_only:
            loads = [load for load in loads if not self.is_used(load)]
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

    def is_used(self, load: ifcopenshell.entity_instance) -> bool:
        """Whether a load is applied in a load case or group, or is part of a load configuration"""
        for inverse in self.file.get_inverse(load):
            if inverse.is_a("IfcStructuralLoadConfiguration"):
                return True
            if inverse.is_a("IfcStructuralActivity") and any(
                rel.is_a("IfcRelAssignsToGroup")
                and rel.RelatingGroup
                and rel.RelatingGroup.is_a("IfcStructuralLoadGroup")
                for rel in inverse.HasAssignments
            ):
                return True
        return False


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
