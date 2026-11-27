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

import re
from math import degrees
from typing import TYPE_CHECKING, Literal, Union

import bpy
import ifcopenshell.api.attribute
import ifcopenshell.api.group
import ifcopenshell.api.structural
import ifcopenshell.util.structural
import ifcopenshell.util.unit
from bpy_extras.view3d_utils import location_3d_to_region_2d
from mathutils import Matrix, Vector

import bonsai.bim.helper
import bonsai.core.structural as core
import bonsai.tool as tool
from bonsai.bim.module.structural.data import (
    LoadGroupDecorationData,
    StructuralAnalysisModelsData,
    StructuralLoadCasesData,
)
from bonsai.bim.module.structural.decorator import LoadsDecorator
from bonsai.bim.module.structural.load_decoration_data import ShaderInfo


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
        def is_under_mouse(region: bpy.types.Region) -> bool:
            x, y = event.mouse_x - region.x, event.mouse_y - region.y
            return 0 <= x < region.width and 0 <= y < region.height

        for area in context.window.screen.areas:
            if area.type != "VIEW_3D":
                continue
            # With region overlap the sidebar, toolbar and headers lie over the view: what is under them is theirs.
            if any(r.type != "WINDOW" and r.width > 1 and r.height > 1 and is_under_mouse(r) for r in area.regions):
                return None
            for region in area.regions:
                if region.type == "WINDOW" and is_under_mouse(region):
                    # Each view of a quad view has its own region and view.
                    return area, region, region.data
        return None

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
        if not props.relating_structural_member:
            self.report({"WARNING"}, "Select a structural member first.")
            return {"CANCELLED"}
        relating_structural_member = tool.Ifc.get_entity(props.relating_structural_member)
        if not relating_structural_member or not relating_structural_member.is_a("IfcStructuralMember"):
            self.report({"WARNING"}, "Select a structural member first.")
            return {"CANCELLED"}
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


class AddStructuralItem(bpy.types.Operator):
    bl_idname = "bim.add_structural_item"
    bl_label = "Add Structural Item"
    bl_description = (
        "Add a structural item of the class chosen in the Structural Tool at the 3D cursor, "
        "in the current structural analysis model"
    )
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if not tool.Ifc.get():
            cls.poll_message_set("No IFC project loaded.")
            return False
        return True

    def execute(self, context):
        props = tool.Structural.get_structural_props()
        ifc_class = props.structural_item_class
        rprops = tool.Root.get_root_props()
        rprops.ifc_product = "IfcStructuralItem"
        rprops.ifc_class = ifc_class
        if tool.Structural.get_structural_item_predefined_types(ifc_class):
            rprops.ifc_predefined_type = props.structural_item_predefined_type
        rprops.representation_template = tool.Structural.get_structural_item_representation_template(ifc_class)
        rprops.name = ""
        rprops.description = ""
        result = bpy.ops.bim.add_element(skip_dialog=True)
        if "FINISHED" in result and (obj := context.active_object):
            # Structural items are hidden by default: show the one just added, so it can be seen and selected.
            for collection in obj.users_collection:
                if layer_collection := tool.Blender.get_layer_collection(collection):
                    layer_collection.hide_viewport = False
        return result


class ConnectStructuralItems(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.connect_structural_items"
    bl_label = "Connect Structural Items"
    bl_description = (
        "Connect the selected structural members to the selected connection, "
        "or the selected member to the selected connections"
    )
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        elements = [e for o in tool.Blender.get_selected_objects() if (e := tool.Ifc.get_entity(o))]
        try:
            pairs = tool.Structural.get_member_connections_to_add(elements)
        except ValueError as e:
            self.report({"ERROR"}, str(e))
            return {"CANCELLED"}
        ifc_file = tool.Ifc.get()
        for member, connection in pairs:
            ifcopenshell.api.structural.add_structural_member_connection(
                ifc_file, relating_structural_member=member, related_structural_connection=connection
            )
        self.report({"INFO"}, f"{len(pairs)} member connection(s) added")
        return {"FINISHED"}


class AddStructuralSupport(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_structural_support"
    bl_label = "Add Structural Support"
    bl_description = "Hold the selected structural connections, replacing any boundary condition they have"
    bl_options = {"REGISTER", "UNDO"}
    support: bpy.props.EnumProperty(
        name="Support",
        items=(
            ("FIXED", "Fixed", "Hold every displacement and rotation"),
            ("PINNED", "Pinned", "Hold every displacement, leave the rotations free"),
        ),
    )

    if TYPE_CHECKING:
        support: Literal["FIXED", "PINNED"]

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def _execute(self, context):
        elements = [e for o in tool.Blender.get_selected_objects() if (e := tool.Ifc.get_entity(o))]
        connections = [e for e in elements if e.is_a("IfcStructuralConnection")]
        if not connections:
            self.report({"ERROR"}, "Select structural connections.")
            return {"CANCELLED"}
        ifc_file = tool.Ifc.get()
        name = self.support.capitalize()
        for connection in connections:
            previous = connection.AppliedCondition
            try:
                # A schema that cannot hold a support (IFC2X3) refuses the first one, before anything is changed.
                ifcopenshell.api.structural.add_structural_boundary_condition(
                    ifc_file, name=name, connection=connection, support=self.support
                )
            except ValueError as e:
                self.report({"ERROR"}, str(e))
                return {"CANCELLED"}
            if previous and not ifc_file.get_total_inverses(previous):
                ifcopenshell.api.structural.remove_structural_boundary_condition(ifc_file, boundary_condition=previous)
        self.report({"INFO"}, f"{len(connections)} connection(s) {name.lower()}")
        return {"FINISHED"}


class AssignStructuralItemsToCurrentModel(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.assign_structural_items_to_current_model"
    bl_label = "Assign Structural Items to Current Model"
    bl_description = "Assign the selected structural items to the current structural analysis model, or unassign them"
    bl_options = {"REGISTER", "UNDO"}
    unassign: bpy.props.BoolProperty(name="Unassign", default=False)

    if TYPE_CHECKING:
        unassign: bool

    def _execute(self, context):
        if not (model := tool.Structural.get_current_structural_analysis_model()):
            self.report({"ERROR"}, "Choose a current structural analysis model first.")
            return {"CANCELLED"}
        elements = [e for o in tool.Blender.get_selected_objects() if (e := tool.Ifc.get_entity(o))]
        items = tool.Structural.get_structural_items(elements)
        items = [i for i in items if tool.Structural.is_in_structural_analysis_model(i, model) == self.unassign]
        if not items:
            self.report({"INFO"}, "Nothing to change.")
            return {"CANCELLED"}
        if self.unassign:
            core.unassign_structural_analysis_model(tool.Ifc, products=items, structural_analysis_model=model)
        else:
            core.assign_structural_analysis_model(tool.Ifc, products=items, structural_analysis_model=model)
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


class AssignStructuralAnalysisModelToBuilding(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.assign_structural_analysis_model_to_building"
    bl_label = "Assign to Building"
    bl_description = "Record that the structural analysis model serves the chosen building"
    bl_options = {"REGISTER", "UNDO"}
    structural_analysis_model: bpy.props.IntProperty()

    def _execute(self, context):
        props = tool.Structural.get_structural_props()
        if not props.building:
            self.report({"WARNING"}, "The project has no building to assign.")
            return {"CANCELLED"}
        ifc_file = tool.Ifc.get()
        core.assign_to_building(
            tool.Ifc,
            structural_analysis_model=ifc_file.by_id(self.structural_analysis_model),
            building=ifc_file.by_id(int(props.building)),
        )


class UnassignStructuralAnalysisModelFromBuilding(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.unassign_structural_analysis_model_from_building"
    bl_label = "Unassign from Building"
    bl_description = "Stop the structural analysis model serving this building"
    bl_options = {"REGISTER", "UNDO"}
    structural_analysis_model: bpy.props.IntProperty()
    building: bpy.props.IntProperty()

    def _execute(self, context):
        ifc_file = tool.Ifc.get()
        core.unassign_from_building(
            tool.Ifc,
            structural_analysis_model=ifc_file.by_id(self.structural_analysis_model),
            building=ifc_file.by_id(self.building),
        )


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
        # Axis and the edge are both in the item's own coordinates. Without an Axis, or with one along the edge (as
        # when a member is stood up), it starts from the default axes.
        edge = obj.data.vertices[1].co - obj.data.vertices[0].co
        roll = tool.Structural.get_item_axis_roll(edge, Vector(item.Axis.DirectionRatios)) if item.Axis else None
        empty = bpy.data.objects.new("Item Axis", None)
        empty.empty_display_type = "ARROWS"
        empty.matrix_world = tool.Structural.get_item_axes(obj, roll or 0.0)

        props.axis_empty = empty
        props.axis_angle = roll or 0.0
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
        # Back into the item's own coordinates, which Axis is in.
        local = obj.matrix_world.inverted() @ props.axis_empty.matrix_world
        z_axis = tuple(local.to_3x3().col[2].normalized())
        self.file = tool.Ifc.get()
        ifcopenshell.api.structural.edit_structural_item_axis(
            self.file,
            structural_item=self.file.by_id(oprops.ifc_definition_id),
            axis=z_axis,
        )
        bpy.ops.bim.disable_editing_structural_item_axis()
        if LoadsDecorator.is_installed:
            LoadsDecorator.update()  # Loads in the item's local axes turn with its Axis.
            tool.Blender.update_all_viewports(context)
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
    bl_description = "Assign the load case or combination to this structural analysis model"
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
    bl_description = "Unassign the load case or combination from this structural analysis model"
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
        load_case = self.file.by_id(props.active_load_case_id)
        # Only an IfcStructuralLoadCase has self-weight, not a load group typed LOAD_CASE.
        if load_case.is_a("IfcStructuralLoadCase"):
            if props.load_case_has_self_weight:
                attributes["SelfWeightCoefficients"] = list(props.load_case_self_weight)
            else:
                attributes["SelfWeightCoefficients"] = None
        ifcopenshell.api.structural.edit_structural_load_case(self.file, load_case=load_case, attributes=attributes)
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
        load_case_entity = tool.Ifc.get().by_id(self.load_case)
        bonsai.bim.helper.import_attributes(
            load_case_entity,
            self.props.load_case_attributes,
            callback=self.import_attributes_callback,
        )
        coeffs = getattr(load_case_entity, "SelfWeightCoefficients", None)
        if coeffs:
            self.props.load_case_has_self_weight = True
            self.props.load_case_self_weight = tuple(coeffs)
        else:
            self.props.load_case_has_self_weight = False
            self.props.load_case_self_weight = (0.0, 0.0, -1.0)
        return {"FINISHED"}

    def import_attributes_callback(self, name: str, prop: object, data: object) -> None | Literal[False]:
        if name in ["SelfWeightCoefficients"]:
            return False


class SetSelfWeightDownwards(bpy.types.Operator):
    bl_idname = "bim.set_self_weight_downwards"
    bl_label = "Reset Self-Weight Downwards"
    bl_description = "Reset self-weight coefficients to downwards gravity (0, 0, -1) in the analysis model's axes"
    bl_options = {"REGISTER"}

    def execute(self, context):
        props = tool.Structural.get_structural_props()
        props.load_case_has_self_weight = True
        props.load_case_self_weight = (0.0, 0.0, -1.0)
        return {"FINISHED"}


class DisableEditingStructuralLoadCase(bpy.types.Operator):
    bl_idname = "bim.disable_editing_structural_load_case"
    bl_label = "Disable Editing Structural Load Case"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        props = tool.Structural.get_structural_props()
        props.active_load_case_id = 0
        return {"FINISHED"}


class AddStructuralLoadCombination(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_structural_load_combination"
    bl_label = "Add Load Combination"
    bl_description = "Add a load combination, in which load cases are added up, each times a factor"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        combination = ifcopenshell.api.structural.add_structural_load_combination(
            tool.Ifc.get(), name="Load Combination"
        )
        tool.Structural.assign_to_current_structural_analysis_model(combination)
        bpy.ops.bim.enable_editing_structural_load_combination(load_combination=combination.id())
        return {"FINISHED"}


class EnableEditingStructuralLoadCombination(bpy.types.Operator):
    bl_idname = "bim.enable_editing_structural_load_combination"
    bl_label = "Enable Editing Load Combination"
    bl_description = "Edit the load combination and the factors of its load cases"
    bl_options = {"REGISTER", "UNDO"}
    load_combination: bpy.props.IntProperty()

    def execute(self, context):
        props = tool.Structural.get_structural_props()
        combination = tool.Ifc.get().by_id(self.load_combination)
        props.active_load_combination_id = combination.id()
        props.load_combination_attributes.clear()
        bonsai.bim.helper.import_attributes(
            combination, props.load_combination_attributes, callback=self.import_attributes_callback
        )
        factors = get_load_combination_factors(combination)
        props.load_combination_factors.clear()
        load_cases = [g for g in tool.Ifc.get().by_type("IfcStructuralLoadGroup") if tool.Structural.is_load_case(g)]
        for load_case in load_cases:
            new = props.load_combination_factors.add()
            new.name = load_case.Name or "Unnamed"
            new.ifc_definition_id = load_case.id()
            new.is_included = load_case in factors
            new.factor = factors.get(load_case, 1.0)
        return {"FINISHED"}

    def import_attributes_callback(self, name: str, prop: object, data: dict) -> None | Literal[False]:
        # These mean nothing for a combination, and its PredefinedType is what makes it one.
        if name in ("ObjectType", "PredefinedType", "ActionType", "ActionSource"):
            return False
        # A Coefficient multiplies every factor: only shown if the file sets one.
        if name == "Coefficient" and data.get("Coefficient") is None:
            return False


class DisableEditingStructuralLoadCombination(bpy.types.Operator):
    bl_idname = "bim.disable_editing_structural_load_combination"
    bl_label = "Disable Editing Load Combination"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        props = tool.Structural.get_structural_props()
        props.active_load_combination_id = 0
        return {"FINISHED"}


class EditStructuralLoadCombination(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.edit_structural_load_combination"
    bl_label = "Edit Load Combination"
    bl_description = "Save the load combination's attributes and the factors of its load cases"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        props = tool.Structural.get_structural_props()
        ifc_file = tool.Ifc.get()
        combination = ifc_file.by_id(props.active_load_combination_id)
        attributes = bonsai.bim.helper.export_attributes(props.load_combination_attributes)
        ifcopenshell.api.attribute.edit_attributes(ifc_file, product=combination, attributes=attributes)
        factors = get_load_combination_factors(combination)
        if ifc_file.schema != "IFC2X3" and ifcopenshell.util.structural.get_combination_factor_groups(combination):
            # Factors given by load groups, as RFEM writes them, are written again as IFC4 gives factors.
            for load_case in factors:
                ifcopenshell.api.structural.unassign_structural_load_combination(
                    ifc_file, load_case=load_case, load_combination=combination
                )
            factors = {}
        for row in props.load_combination_factors:
            try:
                load_case = ifc_file.by_id(row.ifc_definition_id)
            except RuntimeError:  # Removed while the combination was being edited
                continue
            # Blender keeps the factor in single precision: 1.35 would be written 1.35000002.
            factor = float(f"{row.factor:.7g}")
            if not row.is_included:
                if load_case in factors:
                    ifcopenshell.api.structural.unassign_structural_load_combination(
                        ifc_file, load_case=load_case, load_combination=combination
                    )
            elif factors.get(load_case) is None or f"{factors[load_case]:.7g}" != f"{factor:.7g}":
                ifcopenshell.api.structural.assign_structural_load_combination(
                    ifc_file, load_case=load_case, load_combination=combination, factor=factor
                )
        bpy.ops.bim.disable_editing_structural_load_combination()
        return {"FINISHED"}


class RemoveStructuralLoadCombination(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.remove_structural_load_combination"
    bl_label = "Remove Load Combination"
    bl_description = "Remove the load combination. Its load cases are kept"
    bl_options = {"REGISTER", "UNDO"}
    load_combination: bpy.props.IntProperty()

    def _execute(self, context):
        ifc_file = tool.Ifc.get()
        ifcopenshell.api.structural.remove_structural_load_group(
            ifc_file, load_group=ifc_file.by_id(self.load_combination)
        )
        return {"FINISHED"}


def get_load_combination_factors(
    combination: ifcopenshell.entity_instance,
) -> dict[ifcopenshell.entity_instance, float]:
    """The factor of each load case in a combination, not counting its Coefficient

    A load case grouped without a factor counts once, and one grouped more than once
    counts for the sum, as analysis programs add them up. One given its factor by a
    load group between it and the combination, as RFEM and IFC2X3 do, has that factor.
    """
    factors = ifcopenshell.util.structural.get_combination_factors(combination, include_coefficient=False)
    return {c: f for c, f in factors.items() if tool.Structural.is_load_case(c)}


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
        load = self.file.by_id(int(self.props.applicable_structural_loads))
        group = self.file.by_id(self.load_group)
        # The selected items that can take the load and don't have it here already, as the button says.
        targets = tool.Structural.get_load_targets(context.selected_objects, load, group)
        if not targets:
            self.report({"WARNING"}, "No selected item can take this load, or they all have it here already.")
            return {"CANCELLED"}
        for element in targets:
            activity = ifcopenshell.api.structural.add_structural_activity(
                self.file,
                ifc_class=tool.Structural.APPLIED_LOADS[element.is_a()][0],
                applied_load=load,
                structural_member=element,
            )
            ifcopenshell.api.group.assign_group(self.file, products=[activity], group=group)
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

# Matches the load names generated by StructuralForceInput.get_default_load_name, and those once generated for a
# force entered as a magnitude with an angle or slope, so that they too follow the values.
_NUMBER = r"-?[\d.]+(?:e[-+]?\d+)?"
_DIRECTION = r"(?: (?:up|down)-(?:left|right))?"
DEFAULT_LOAD_NAME = re.compile(
    rf"^(?:{_NUMBER} \S+ at {_NUMBER} deg{_DIRECTION}|{_NUMBER} \S+ at {_NUMBER}:{_NUMBER}{_DIRECTION}"
    rf"|(?:[XYZ] {_NUMBER}(?:, [XYZ] {_NUMBER})*|0) \S+(?: local)?)$"
)


def get_load_category(load: ifcopenshell.entity_instance) -> Union[str, None]:
    """Get the kind of structural item a load applies to, if it is a force the load dialogs support."""
    return next((c for c, (load_class, *_) in APPLY_LOAD_CLASSES.items() if load.is_a(load_class)), None)


# Property update callbacks get the operator's properties, not the operator, so the name helpers are functions.
def get_force_components(props: "StructuralForceInput") -> tuple[float, float, float]:
    return props.x, props.y, props.z


def has_local_axes(category: Union[str, None]) -> bool:
    """Whether a force on this kind of item can be given in the item's own axes: a member's"""
    return category in ("IfcStructuralCurveMember", "IfcStructuralSurfaceMember")


def get_load_unit_symbol(category: str) -> str:
    ifc_file = tool.Ifc.get()
    unit_type = {"IfcStructuralCurveMember": "LINEARFORCEUNIT", "IfcStructuralSurfaceMember": "PLANARFORCEUNIT"}.get(
        category
    )
    if unit_type and (unit := ifcopenshell.util.unit.get_project_unit(ifc_file, unit_type)):
        return ifcopenshell.util.unit.get_unit_symbol(unit)
    # Undeclared: the force unit over the length unit, as readers of the file take it.
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
    values = [f"{axis} {value:g}" for axis, value in zip("XYZ", get_force_components(props)) if value]
    local = " local" if has_local_axes(category) and props.axes == "LOCAL_COORDS" else ""
    return f"{', '.join(values) or '0'} {unit}{local}"


def get_load_attributes(
    props: "StructuralForceInput", category: str, load: Union[ifcopenshell.entity_instance, None] = None
) -> dict[str, Union[float, None]]:
    """The attributes of the force in a dialog, entered in Blender's axes, given in those of the load's model.

    A force in a member's local axes is given as entered: the model's axes do not apply to it."""
    _, _, force_attributes, moment_attributes = APPLY_LOAD_CLASSES[category]
    values = get_force_components(props) + (props.moment_x, props.moment_y, props.moment_z)
    attributes = {name: value or None for name, value in zip(force_attributes + moment_attributes, values)}
    return tool.Structural.to_model_axes(load, attributes) if load else attributes


def update_force_inputs(self: "StructuralForceInput", context: bpy.types.Context) -> None:
    # Keep a generated name in step with the values, but never overwrite a name the user typed.
    if self.load_category and (not self.load_name or DEFAULT_LOAD_NAME.match(self.load_name)):
        self.load_name = get_default_load_name(self, self.load_category)
    # Show the load being edited with the values in the dialog until it is confirmed or cancelled.
    if self.preview_load and self.load_category and LoadsDecorator.is_installed:
        load = tool.Ifc.get().by_id(self.preview_load)
        ShaderInfo.preview = {self.preview_load: get_load_attributes(self, self.load_category, load)}
        LoadsDecorator.update()
        tool.Blender.update_all_viewports(context)


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
    axes: bpy.props.EnumProperty(
        name="Axes",
        description="The axes the components of a force on a member are given in",
        items=[
            ("GLOBAL_COORDS", "Global", "The project's axes: Z is vertical"),
            (
                "LOCAL_COORDS",
                "Local",
                "The member's own axes: for a surface member Z is normal to its surface, "
                "for a curve member X runs along it and Z follows its Axis",
            ),
        ],
        update=update_force_inputs,
    )
    x: bpy.props.FloatProperty(name="X", update=update_force_inputs)
    y: bpy.props.FloatProperty(name="Y", update=update_force_inputs)
    z: bpy.props.FloatProperty(name="Z", update=update_force_inputs)
    moment_x: bpy.props.FloatProperty(name="Moment X", update=update_force_inputs)
    moment_y: bpy.props.FloatProperty(name="Moment Y", update=update_force_inputs)
    moment_z: bpy.props.FloatProperty(name="Moment Z", update=update_force_inputs)
    load_name: bpy.props.StringProperty(name="Load Name")

    def get_components(self) -> tuple[float, float, float]:
        return get_force_components(self)

    def get_load_attributes(
        self, category: str, load: Union[ifcopenshell.entity_instance, None] = None
    ) -> dict[str, Union[float, None]]:
        return get_load_attributes(self, category, load)

    def get_unit_symbol(self, category: str) -> str:
        return get_load_unit_symbol(category)

    def get_default_load_name(self, category: str) -> str:
        return get_default_load_name(self, category)

    def draw_force_inputs(self, layout: bpy.types.UILayout, category: Union[str, None]) -> None:
        if has_local_axes(category):
            layout.row().prop(self, "axes", expand=True)
            if self.axes == "LOCAL_COORDS" and category == "IfcStructuralSurfaceMember":
                layout.label(text="Z is normal to the surface", icon="ORIENTATION_NORMAL")
        for prop in ("x", "y", "z"):
            layout.prop(self, prop)
        if category in ("IfcStructuralPointConnection", "IfcStructuralCurveMember"):
            for prop in ("moment_x", "moment_y", "moment_z"):
                layout.prop(self, prop)
        layout.prop(self, "load_name")

    def get_global_or_local(self, category: str) -> str:
        """The GlobalOrLocal of the activities applying the force"""
        return self.axes if has_local_axes(category) else "GLOBAL_COORDS"

    def get_load_name(self, category: str) -> str:
        return self.load_name or self.get_default_load_name(category)


# Blender needs enum item strings to stay referenced while the dialog is open.
apply_load_group_items: list[tuple[str, str, str]] = []


def is_load_combination(group: ifcopenshell.entity_instance) -> bool:
    return group.is_a("IfcStructuralLoadGroup") and group.PredefinedType == "LOAD_COMBINATION"


def get_apply_load_groups(self, context: bpy.types.Context) -> list[tuple[str, str, str]]:
    global apply_load_group_items
    model = tool.Structural.get_current_structural_analysis_model()
    groups = tool.Structural.get_load_cases(model)
    # A combination groups load cases, not loads: offer its load cases instead.
    groups = [
        g for group in groups for g in (get_combined_load_cases(group) if is_load_combination(group) else [group])
    ]
    apply_load_group_items = []
    listed = set()
    for group in groups:
        if group in listed:
            continue
        listed.add(group)
        apply_load_group_items.append((str(group.id()), group.Name or "Unnamed", group.is_a()))
        for rel in group.IsGroupedBy:
            for subgroup in rel.RelatedObjects:
                if subgroup.is_a("IfcStructuralLoadGroup") and not is_load_combination(subgroup):
                    listed.add(subgroup)
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
        if tool.Structural.is_load_case(group) and not group.LoadGroupFor:
            tool.Structural.assign_to_current_structural_analysis_model(group)

        load_class, activity_class, _, _ = APPLY_LOAD_CLASSES[category]
        load = ifcopenshell.api.structural.add_structural_load(
            ifc_file, name=self.get_load_name(category), ifc_class=load_class
        )
        activities = [
            ifcopenshell.api.structural.add_structural_activity(
                ifc_file,
                ifc_class=activity_class,
                applied_load=load,
                structural_member=element,
                global_or_local=self.get_global_or_local(category),
            )
            for element in elements
        ]
        # Once it acts on its items, whose model gives the axes its values are written in.
        ifcopenshell.api.structural.edit_structural_load(
            ifc_file, structural_load=load, attributes=self.get_load_attributes(category, load)
        )
        ifcopenshell.api.group.assign_group(ifc_file, products=activities, group=group)
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


edit_load_group_items: list[tuple[str, str, str]] = []


def get_edit_load_groups(self, context: bpy.types.Context) -> list[tuple[str, str, str]]:
    global edit_load_group_items
    edit_load_group_items = []
    listed = set()
    for load_case in tool.Structural.get_load_cases():
        edit_load_group_items.append((str(load_case.id()), load_case.Name or "Unnamed", load_case.is_a()))
        listed.add(load_case)
        for rel in load_case.IsGroupedBy:
            for group in rel.RelatedObjects:
                if group.is_a("IfcStructuralLoadGroup") and not is_load_combination(group) and group not in listed:
                    edit_load_group_items.append((str(group.id()), f"    {group.Name or 'Unnamed'}", group.is_a()))
                    listed.add(group)
    for group in tool.Ifc.get().by_type("IfcStructuralLoadGroup"):
        if group not in listed and not is_load_combination(group):
            edit_load_group_items.append((str(group.id()), group.Name or "Unnamed", group.is_a()))
    edit_load_group_items.append(("NONE", "No Load Case", "Not in any load case or load group"))
    edit_load_group_items.append(("0", "New Load Case", "Create a new load case in the current model"))
    return edit_load_group_items


def get_combined_load_cases(combination: ifcopenshell.entity_instance) -> list[ifcopenshell.entity_instance]:
    return list(get_load_combination_factors(combination))


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
    initial_load_group: bpy.props.StringProperty(options={"HIDDEN", "SKIP_SAVE"})
    new_load_case_name: bpy.props.StringProperty(name="New Load Case", default="Load Case")

    def get_load(self) -> ifcopenshell.entity_instance:
        ifc_file = tool.Ifc.get()
        if self.activity:
            return ifc_file.by_id(self.activity).AppliedLoad
        return ifc_file.by_id(self.structural_load)

    def invoke(self, context, event):
        load = self.get_load()
        if not (category := get_load_category(load)):
            # Only forces have a dialog; other loads use the attribute editor of the Structural Loads panel.
            bpy.ops.bim.load_structural_loads()
            bpy.ops.bim.enable_editing_structural_load(structural_load=load.id())
            self.report({"INFO"}, f"Editing {load.Name or 'Unnamed'} in the Structural Loads panel")
            return {"FINISHED"}
        self.load_category = category
        _, _, force_attributes, moment_attributes = APPLY_LOAD_CLASSES[category]
        # In Blender's axes, as the force is drawn, whatever axes its model gives it in.
        values = tool.Structural.to_blender_axes(
            load, {a: getattr(load, a) for a in force_attributes + moment_attributes}
        )
        self.x, self.y, self.z = (values[a] or 0.0 for a in force_attributes)
        self.moment_x, self.moment_y, self.moment_z = (
            (values[a] or 0.0 for a in moment_attributes) if moment_attributes else (0.0, 0.0, 0.0)
        )
        users = self.get_users()
        self.axes = "LOCAL_COORDS" if users and users[0].GlobalOrLocal == "LOCAL_COORDS" else "GLOBAL_COORDS"
        self.load_name = load.Name or ""
        if activities := self.get_movable_activities():
            groups = get_activity_load_groups(activities[0])
            self.load_group = str(groups[0].id()) if groups else "NONE"
        self.initial_load_group = self.load_group
        # Set last, so that filling in the values above does not start a preview.
        self.preview_load = load.id()
        return context.window_manager.invoke_props_dialog(self, width=350)

    def get_users(self) -> list[ifcopenshell.entity_instance]:
        """The applied loads that use the load"""
        return [i for i in tool.Ifc.get().get_inverse(self.get_load()) if i.is_a("IfcStructuralActivity")]

    def draw(self, context):
        load = self.get_load()
        category = get_load_category(load)
        layout = self.layout
        if self.get_movable_activities():
            layout.prop(self, "load_group")
            if self.load_group == "0":
                layout.prop(self, "new_load_case_name")
        users = self.get_users()
        layout.label(text=f"Used by {len(users)} applied load{'s' if len(users) != 1 else ''}", icon="INFO")
        load_cases = {g for user in users for g in get_activity_load_groups(user)}
        if len(load_cases) > 1 and not self.get_movable_activities():
            layout.label(text=f"Used in {len(load_cases)} load cases: move one from its applied load", icon="INFO")
        self.draw_force_inputs(layout, category)
        if has_local_axes(category) and len({u.GlobalOrLocal for u in users}) > 1:
            layout.label(text="Its applied loads use different axes: all will use these", icon="ERROR")

    def cancel(self, context):
        clear_load_preview(context)

    def _execute(self, context):
        ShaderInfo.preview = {}  # The edit below refreshes the shown loads.
        load = self.get_load()
        category = get_load_category(load)
        ifc_file = tool.Ifc.get()
        # The axes first: they decide whether the model's axes apply to the values.
        global_or_local = self.get_global_or_local(category)
        for activity in self.get_users():
            if activity.GlobalOrLocal != global_or_local:
                ifcopenshell.api.attribute.edit_attributes(
                    ifc_file, product=activity, attributes={"GlobalOrLocal": global_or_local}
                )
        attributes = self.get_load_attributes(category, load)
        attributes["Name"] = self.get_load_name(category)
        ifcopenshell.api.structural.edit_structural_load(ifc_file, structural_load=load, attributes=attributes)
        # An applied load in several groups stays in all of them unless another load case is chosen.
        if self.load_group != self.initial_load_group and (activities := self.get_movable_activities()):
            target = self.get_target_load_group(ifc_file)
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
        users = self.get_users()
        load_cases = {frozenset(get_activity_load_groups(user)) for user in users}
        return users if len(load_cases) == 1 else []

    def get_target_load_group(self, ifc_file: ifcopenshell.file) -> Union[ifcopenshell.entity_instance, None]:
        if self.load_group == "0":
            target = ifcopenshell.api.structural.add_structural_load_case(
                ifc_file, name=self.new_load_case_name or "Load Case"
            )
            tool.Structural.assign_to_current_structural_analysis_model(target)
        elif self.load_group and self.load_group != "NONE":
            target = ifc_file.by_id(int(self.load_group))
        else:
            return None
        return target

    def move_activity(
        self,
        ifc_file: ifcopenshell.file,
        activity: ifcopenshell.entity_instance,
        target: Union[ifcopenshell.entity_instance, None],
    ) -> None:
        groups = get_activity_load_groups(activity)
        if groups == ([target] if target else []):
            return
        for group in groups:
            ifcopenshell.api.group.unassign_group(ifc_file, products=[activity], group=group)
        if target:
            ifcopenshell.api.group.assign_group(ifc_file, products=[activity], group=target)


class ShowStructuralLoadCase(bpy.types.Operator):
    bl_idname = "bim.show_structural_load_case"
    bl_label = "Show Load Case"
    bl_description = (
        "Show the loads of this load case or combination in the viewport, or stop showing them if they are shown"
    )
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
            self.report({"WARNING"}, "This load case or combination is not in the current analysis model.")
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
                    names.count(boundary_condition.Name or "Unnamed") > 1
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
