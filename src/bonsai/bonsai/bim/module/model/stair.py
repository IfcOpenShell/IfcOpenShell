# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021, 2022 Dion Moult <dion@thinkmoult.com>, @Andrej730
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

import bpy
import json
import bmesh
import math
import ifcopenshell
import ifcopenshell.api.pset
import ifcopenshell.util.element
import ifcopenshell.util.representation
import ifcopenshell.util.unit
import bonsai.core.root
import bonsai.tool as tool
from bonsai.bim.module.drawing import gizmos as gizmo
from bonsai.bim.module.drawing.gizmos import DimensionGizmoConfig
from bonsai.tool.numeric_input import IntegerInputState, run_integer_input_modal, update_header
from mathutils import Vector, Matrix

V_ = tool.Blender.V_
from bmesh.types import BMVert
from bpy.types import Operator
from bpy.props import FloatProperty, IntProperty
from bpy_extras.object_utils import AddObjectHelper, object_data_add
from typing import get_args


def regenerate_stair_mesh(obj: bpy.types.Object) -> None:
    props = tool.Model.get_stair_props(obj)
    props_kwargs = props.get_props_kwargs()
    vertices, edges, faces = tool.Model.generate_stair_2d_profile(**props_kwargs)

    bm = bmesh.new()
    bm.verts.index_update()
    bm.edges.index_update()

    new_verts = [bm.verts.new(v) for v in vertices]
    new_edges = [bm.edges.new((new_verts[e[0]], new_verts[e[1]])) for e in edges]
    bm.verts.index_update()
    bm.edges.index_update()

    bmesh.ops.contextual_create(bm, geom=new_edges)

    bm.faces.ensure_lookup_table()
    faces = bm.faces
    extruded = bmesh.ops.extrude_face_region(bm, geom=faces)
    extrusion_vector = Vector((0, 1, 0)) * props_kwargs["width"]
    translate_verts = [v for v in extruded["geom"] if isinstance(v, BMVert)]
    bmesh.ops.translate(bm, vec=extrusion_vector, verts=translate_verts)

    assert isinstance(obj.data, bpy.types.Mesh)
    if obj.mode == "EDIT":
        bmesh.update_edit_mesh(obj.data)
    else:
        bm.to_mesh(obj.data)
        bm.free()
    obj.data.update()


def update_ifc_stair_props(obj: bpy.types.Object) -> None:
    """should be called after new geometry settled
    since it's going to update ifc representation
    """
    element = tool.Ifc.get_entity(obj)
    assert element
    props = tool.Model.get_stair_props(obj)
    ifc_file = tool.Ifc.get()

    if tool.Ifc.get_schema() != "IFC2X3" and element.is_a("IfcStairFlight"):
        element.PredefinedType = "STRAIGHT"
    number_of_risers = props.number_of_treads + 1
    # update IfcStairFlight properties (seems already deprecated but keep it for now)
    # http://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcStairFlight.htm

    si_conversion = ifcopenshell.util.unit.calculate_unit_scale(ifc_file)
    riser_height = props.height / number_of_risers / si_conversion
    tread_length = props.tread_depth / si_conversion
    nosing_length = props.nosing_length / si_conversion

    if element.is_a("IfcStairFlight"):
        if tool.Ifc.get_schema() == "IFC2X3":
            element.NumberOfRiser = number_of_risers
        else:
            element.NumberOfRisers = number_of_risers

        element.NumberOfTreads = props.number_of_treads
        element.RiserHeight = riser_height
        element.TreadLength = tread_length

    # update pset with ifc properties
    pset_common = tool.Pset.get_element_pset(element, "Pset_StairFlightCommon")
    if not pset_common:
        pset_common = ifcopenshell.api.pset.add_pset(ifc_file, product=element, name="Pset_StairFlightCommon")

    ifcopenshell.api.pset.edit_pset(
        ifc_file,
        pset=pset_common,
        properties={
            "NumberOfRiser": number_of_risers,
            "NumberOfTreads": props.number_of_treads,
            "RiserHeight": riser_height,
            "TreadLength": tread_length,
            "NosingLength": nosing_length,
        },
    )

    # update related annotation objects
    def get_elements_from_product(product: ifcopenshell.entity_instance) -> list[ifcopenshell.entity_instance]:
        elements = []
        for rel in product.ReferencedBy:
            if not rel.is_a("IfcRelAssignsToProduct"):
                continue
            elements.extend(rel.RelatedObjects)
        return elements

    stair_obj = obj
    for rel_element in get_elements_from_product(element):
        if not rel_element.is_a("IfcAnnotation") or rel_element.ObjectType != "STAIR_ARROW":
            continue
        if annotation_obj := tool.Ifc.get_object(rel_element):
            tool.Drawing.setup_annotation_object(annotation_obj, "STAIR_ARROW", stair_obj)


class BIM_OT_add_stair(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "mesh.add_stair"
    bl_label = "Add Stair"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return tool.Ifc.get() and context.mode == "OBJECT"

    def _execute(self, context):
        ifc_file = tool.Ifc.get()
        if not ifc_file:
            self.report({"ERROR"}, "You need to start IFC project first to create a stair.")
            return {"CANCELLED"}

        if context.active_object is not None:
            spawn_location = context.active_object.location.copy()
            context.active_object.select_set(False)
        else:
            spawn_location = bpy.context.scene.cursor.location.copy()

        mesh = bpy.data.meshes.new("IfcStairFlight")
        obj = bpy.data.objects.new("StairFlight", mesh)
        obj.location = spawn_location

        element = bonsai.core.root.assign_class(
            tool.Ifc,
            tool.Collector,
            tool.Root,
            obj=obj,
            ifc_class="IfcStairFlight",
            should_add_representation=False,
        )
        if tool.Ifc.get_schema() != "IFC2X3":
            element.PredefinedType = "STRAIGHT"

        bpy.ops.object.select_all(action="DESELECT")
        bpy.context.view_layer.objects.active = None
        bpy.context.view_layer.objects.active = obj
        tool.Blender.select_object(obj)
        bpy.ops.bim.add_stair()
        return {"FINISHED"}


# UI operators
class AddStair(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_stair"
    bl_label = "Add Stair"
    bl_description = "Add Bonsai parametric stair to the active IFC element"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        obj = context.active_object
        assert obj
        element = tool.Ifc.get_entity(obj)
        assert element
        props = tool.Model.get_stair_props(obj)
        ifc_file = tool.Ifc.get()

        tool.Blender.get_addon_preferences().default_parameters.stair.copy_to(props)

        # Use the special method that includes custom_tread_lock for IFC storage
        stair_data = props.get_props_kwargs_for_ifc_export(convert_to_project_units=True)
        pset = tool.Pset.get_element_pset(element, "BBIM_Stair")
        if not pset:
            pset = ifcopenshell.api.pset.add_pset(ifc_file, product=element, name="BBIM_Stair")

        ifcopenshell.api.pset.edit_pset(
            ifc_file,
            pset=pset,
            properties={"Data": tool.Ifc.get().createIfcText(json.dumps(stair_data))},
        )

        if obj.type == "EMPTY":
            obj = tool.Geometry.recreate_object_with_data(obj, data=bpy.data.meshes.new("temp"), is_global=True)
            tool.Blender.set_active_object(obj)

        regenerate_stair_mesh(obj)
        update_ifc_stair_props(obj)
        tool.Model.add_body_representation(obj)


class CancelEditingStair(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.cancel_editing_stair"
    bl_label = "Cancel Editing Stair"
    bl_description = "Cancel editing and revert stair parameters to their previous values"
    bl_options = {"REGISTER"}

    def _execute(self, context):
        obj = context.active_object
        assert obj
        element = tool.Ifc.get_entity(obj)
        assert element
        data = json.loads(ifcopenshell.util.element.get_pset(element, "BBIM_Stair", "Data"))
        props = tool.Model.get_stair_props(obj)
        # restore previous settings since editing was canceled
        props.set_props_kwargs_from_ifc_data(data)
        regenerate_stair_mesh(obj)

        props.is_editing = False

        return {"FINISHED"}


class FinishEditingStair(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.finish_editing_stair"
    bl_label = "Finish Editing Stair"
    bl_description = "Apply changes and finish editing stair parameters"
    bl_options = {"REGISTER"}

    def _execute(self, context):
        obj = context.active_object
        assert obj
        element = tool.Ifc.get_entity(obj)
        assert element
        props = tool.Model.get_stair_props(obj)

        # Use the special method that includes custom_tread_lock for IFC storage
        data = props.get_props_kwargs_for_ifc_export(convert_to_project_units=True)
        props.is_editing = False
        regenerate_stair_mesh(obj)
        tool.Model.add_body_representation(obj)

        pset = tool.Pset.get_element_pset(element, "BBIM_Stair")
        data = tool.Ifc.get().createIfcText(json.dumps(data))
        ifcopenshell.api.pset.edit_pset(tool.Ifc.get(), pset=pset, properties={"Data": data})

        # update IfcStairFlight properties
        update_ifc_stair_props(obj)
        return {"FINISHED"}


class EnableEditingStair(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.enable_editing_stair"
    bl_label = "Enable Editing Stair"
    bl_description = "Enter edit mode to modify stair parameters interactively"
    bl_options = {"REGISTER"}

    def _execute(self, context):
        obj = context.active_object
        assert obj
        props = tool.Model.get_stair_props(obj)
        element = tool.Ifc.get_entity(obj)
        data = json.loads(ifcopenshell.util.element.get_pset(element, "BBIM_Stair", "Data"))
        # required since we could load pset from .ifc and BIMStairProperties won't be set
        props.set_props_kwargs_from_ifc_data(data)
        props.is_editing = True
        return {"FINISHED"}


class RemoveStair(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.remove_stair"
    bl_label = "Remove Stair"
    bl_options = {"REGISTER"}

    def _execute(self, context):
        obj = context.active_object
        assert obj
        props = tool.Model.get_stair_props(obj)
        element = tool.Ifc.get_entity(obj)
        assert element
        props.is_editing = False

        pset = tool.Pset.get_element_pset(element, "BBIM_Stair")
        ifcopenshell.api.pset.remove_pset(tool.Ifc.get(), product=element, pset=pset)

        return {"FINISHED"}


class ToggleStairTotalLengthLock(bpy.types.Operator):
    """Toggle the total length lock for stair editing"""

    bl_idname = "bim.toggle_stair_total_length_lock"
    bl_label = "Toggle Stair Total Length Lock"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        obj = context.active_object
        if not obj:
            return {"CANCELLED"}

        props = tool.Model.get_stair_props(obj)
        props.total_length_lock = not props.total_length_lock

        return {"FINISHED"}


class ToggleStairCustomTreadLock(bpy.types.Operator):
    """Toggle custom first/last tread runs. When unlocked, first and last treads can have different lengths."""

    bl_idname = "bim.toggle_stair_custom_tread_lock"
    bl_label = "Toggle Custom Tread Lock"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        obj = context.active_object
        if not obj:
            return {"CANCELLED"}

        props = tool.Model.get_stair_props(obj)
        props.custom_tread_lock = not props.custom_tread_lock

        return {"FINISHED"}


class AdjustStairTreads(bpy.types.Operator):
    """Adjust the number of treads. Shift+click to enter a specific number."""

    bl_idname = "bim.adjust_stair_treads"
    bl_label = "Adjust Stair Treads"
    bl_options = {"REGISTER", "UNDO"}

    increment: IntProperty(name="Increment", default=1)

    def invoke(self, context, event):
        if event.shift:
            bpy.ops.bim.set_stair_treads("INVOKE_DEFAULT")
            return {"FINISHED"}
        return self.execute(context)

    def execute(self, context):
        obj = context.active_object
        if not obj:
            return {"CANCELLED"}

        props = tool.Model.get_stair_props(obj)
        new_value = props.number_of_treads + self.increment
        if new_value >= 1:
            props.number_of_treads = new_value

        return {"FINISHED"}


class SetStairTreads(bpy.types.Operator):
    """Set the number of treads to a specific value."""

    bl_idname = "bim.set_stair_treads"
    bl_label = "Set Number of Treads"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    def invoke(self, context, event):  # noqa: ARG002
        obj = context.active_object
        if not obj:
            return {"CANCELLED"}

        props = tool.Model.get_stair_props(obj)
        self._input = IntegerInputState.from_value(props.number_of_treads, min_value=1)
        self._original_value = props.number_of_treads

        bpy.ops.ed.undo_push(message="Set Number of Treads")
        context.window_manager.modal_handler_add(self)
        update_header(context, self._format_header())
        return {"RUNNING_MODAL"}

    def modal(self, context, event):
        return run_integer_input_modal(self, context, event)

    def _apply_value(self, context) -> None:
        obj = context.active_object
        if not obj:
            return
        value = self._input.get_value()
        if value is not None:
            props = tool.Model.get_stair_props(obj)
            props.number_of_treads = value

    def _restore_value(self, context) -> None:
        obj = context.active_object
        if obj:
            props = tool.Model.get_stair_props(obj)
            props.number_of_treads = self._original_value

    def _format_header(self) -> str:
        input_str = self._input.get_input_string()
        validity = "" if self._input.is_valid else " [must be >= 1]"
        return f"Number of Treads: {input_str}_{validity}  |  Enter to confirm, Esc to cancel"


class CycleStairType(bpy.types.Operator):
    """Cycle through stair types. Shift+click to cycle in reverse."""

    bl_idname = "bim.cycle_stair_type"
    bl_label = "Cycle Stair Type"
    bl_options = {"REGISTER", "UNDO"}

    reverse: bpy.props.BoolProperty(name="Reverse", default=False, options={"HIDDEN", "SKIP_SAVE"})

    def invoke(self, context, event):
        self.reverse = event.shift
        return self.execute(context)

    def execute(self, context):
        obj = context.active_object
        if not obj:
            return {"CANCELLED"}

        props = tool.Model.get_stair_props(obj)
        stair_types = get_args(tool.Model.StairType)
        current_idx = stair_types.index(props.stair_type) if props.stair_type in stair_types else 0
        direction = -1 if self.reverse else 1
        props.stair_type = stair_types[(current_idx + direction) % len(stair_types)]

        return {"FINISHED"}


def _compute_first_tread_run(props) -> float:
    """Get the first custom tread run value from the tuple property."""
    return props.custom_first_last_tread_run[0]


def _apply_first_tread_run(props, value: float) -> None:
    """Apply a new first custom tread run value, preserving the second value."""
    props.custom_first_last_tread_run = (max(0.01, value), props.custom_first_last_tread_run[1])


def _compute_last_tread_run(props) -> float:
    """Get the last custom tread run value from the tuple property."""
    return props.custom_first_last_tread_run[1]


def _apply_last_tread_run(props, value: float) -> None:
    """Apply a new last custom tread run value, preserving the first value."""
    props.custom_first_last_tread_run = (props.custom_first_last_tread_run[0], max(0.01, value))


class GizmoStairEdition(bpy.types.GizmoGroup, gizmo.BaseParametricGizmoGroup):
    bl_idname = "OBJECT_GGT_bim_stair_edition"
    bl_label = "Stair Editing Gizmo"
    bl_space_type = "VIEW_3D"
    bl_region_type = "WINDOW"
    bl_options = {"3D", "PERSISTENT"}

    # === Stair-Specific Icon Layout (meters) ===
    # Additional icons for stair editing, positioned after standard icons:
    #   [Validate] [Cancel] [Cycle] [TreadLock] [Plus] [Minus]
    ICON_TREAD_LOCK_X = 1.24  # X position for tread lock toggle icon
    ICON_PLUS_X = 1.61  # X position for add tread (+) icon
    ICON_MINUS_X = 1.98  # X position for remove tread (-) icon
    ICON_PLUS_MINUS_SCALE = 0.24  # Scale for plus/minus icons (slightly larger)

    enable_editing_operator = "bim.enable_editing_stair"
    finish_editing_operator = "bim.finish_editing_stair"
    cancel_editing_operator = "bim.cancel_editing_stair"
    cycle_type_operator = "bim.cycle_stair_type"

    def get_icon_y_offset(self, context, mw):
        """Get Y offset for icons based on view direction.

        Positions icons further than the furthest geometry:
        stair_width + 2 * GIZMO_OFFSET
        """
        obj = context.active_object
        if not obj:
            return self.ICON_Y_OFFSET
        props = self.get_props(obj)
        furthest_y = props.width + 2 * self.GIZMO_OFFSET

        viewing_from_negative_y, _ = self.get_local_view_direction(context, mw)
        if viewing_from_negative_y:
            return -furthest_y
        return furthest_y

    dimension_gizmo_props = [
        DimensionGizmoConfig(
            attr_name="total_length_target",
            axis=(1, 0, 0),
            prop_name="Total Length",
            min_value=0.01,
            text_offset_sign=-1,
        ),
        DimensionGizmoConfig(attr_name="height", axis=(0, 0, 1), min_value=0.01, text_alignment="start"),
        DimensionGizmoConfig(attr_name="width", axis=(0, 1, 0), min_value=0.01),
        DimensionGizmoConfig(
            attr_name="tread_run",
            axis=(1, 0, 0),
            min_value=0.01,
            visibility_condition=lambda props: props.custom_tread_lock or props.number_of_treads > 2,
        ),
        DimensionGizmoConfig(
            attr_name="custom_first_tread_run",
            axis=(1, 0, 0),
            prop_name="First Tread",
            min_value=0.01,
            visibility_condition=lambda props: not props.custom_tread_lock,
            compute_value=_compute_first_tread_run,
            apply_value=_apply_first_tread_run,
        ),
        DimensionGizmoConfig(
            attr_name="custom_last_tread_run",
            axis=(1, 0, 0),
            prop_name="Last Tread",
            min_value=0.01,
            visibility_condition=lambda props: not props.custom_tread_lock,
            compute_value=_compute_last_tread_run,
            apply_value=_apply_last_tread_run,
        ),
        DimensionGizmoConfig(attr_name="nosing_length", axis=(-1, 0, 0)),
        DimensionGizmoConfig(
            attr_name="tread_depth",
            axis=(0, 0, -1),
            visibility_condition=lambda props: props.stair_type != "GENERIC",
        ),
        DimensionGizmoConfig(
            attr_name="riser_height",
            axis=(0, 0, 1),
            min_value=0.01,
            text_alignment="start",
            compute_value=lambda props: props.height / (props.number_of_treads + 1),
            apply_value=lambda props, value: setattr(props, "height", max(0.01, value) * (props.number_of_treads + 1)),
        ),
        DimensionGizmoConfig(
            attr_name="nosing_depth",
            axis=(0, 0, -1),
            visibility_condition=lambda props: props.nosing_length != 0.0 and props.stair_type != "WOOD/STEEL",
        ),
        DimensionGizmoConfig(
            attr_name="base_slab_depth",
            axis=(0, 0, -1),
            visibility_condition=lambda props: props.stair_type == "CONCRETE",
        ),
        DimensionGizmoConfig(
            attr_name="top_slab_depth",
            axis=(0, 0, -1),
            visibility_condition=lambda props: props.stair_type == "CONCRETE",
        ),
    ]

    @classmethod
    def is_element_type(cls, element) -> bool:
        return tool.Blender.Modifier.is_stair(element)

    def get_props(self, obj: bpy.types.Object):
        return tool.Model.get_stair_props(obj)

    def get_gizmo_prefs(self):
        prefs = tool.Blender.get_addon_preferences()
        return prefs.gizmos.stair

    @staticmethod
    def _get_stair_total_run(props) -> float:
        """Calculate the total horizontal run of the stair.

        Takes into account custom first/last tread runs when custom_tread_lock is False.
        """
        number_of_rises = props.number_of_treads + 1
        total_run = 0.0
        default_rises = number_of_rises

        if not props.custom_tread_lock:
            if props.custom_first_last_tread_run[0] is not None:  # May be 0 though
                default_rises -= 1
                total_run += props.custom_first_last_tread_run[0]
            if props.custom_first_last_tread_run[1] is not None:  # May be 0 though
                default_rises -= 1
                total_run += props.custom_first_last_tread_run[1]

        total_run += props.tread_run * default_rises
        return total_run

    @staticmethod
    def _get_first_riser_height(props) -> float:
        """Calculate the height of the first riser."""
        return props.height / (props.number_of_treads + 1)

    def get_dimension_matrix_total_length_target(self, props) -> Matrix:
        return self.compose_gizmo_matrix(V_(0, -self.GIZMO_OFFSET, -self.GIZMO_OFFSET), (1, 0, 0))

    def get_dimension_matrix_height(self, props) -> Matrix:
        total_run = self._get_stair_total_run(props)
        return self.compose_gizmo_matrix(V_(total_run + self.GIZMO_OFFSET, -self.GIZMO_OFFSET, 0), (0, 0, 1))

    def get_dimension_matrix_width(self, props) -> Matrix:
        return self.compose_gizmo_matrix(V_(self.GIZMO_OFFSET, 0, -self.GIZMO_OFFSET), (0, 1, 0))

    def get_dimension_matrix_tread_run(self, props) -> Matrix:
        """Position depends on custom_tread_lock state."""
        riser_height = self._get_first_riser_height(props)
        if props.custom_tread_lock:
            x_offset = 0
            z_offset = riser_height
        else:
            x_offset = props.custom_first_last_tread_run[0]
            z_offset = riser_height * 2
        return self.compose_gizmo_matrix(V_(x_offset, 0, z_offset), (1, 0, 0))

    def get_dimension_matrix_custom_first_tread_run(self, props) -> Matrix:
        riser_height = self._get_first_riser_height(props)
        return self.compose_gizmo_matrix(V_(0, 0, riser_height), (1, 0, 0))

    def get_dimension_matrix_custom_last_tread_run(self, props) -> Matrix:
        total_run = self._get_stair_total_run(props)
        x_offset = total_run - props.custom_first_last_tread_run[1]
        return self.compose_gizmo_matrix(V_(x_offset, 0, props.height), (1, 0, 0))

    def get_dimension_matrix_nosing_length(self, props) -> Matrix:
        riser_height = self._get_first_riser_height(props)
        return self.compose_gizmo_matrix(V_(0, props.width / 2, riser_height), (-1, 0, 0))

    def get_dimension_matrix_tread_depth(self, props) -> Matrix:
        riser_height = self._get_first_riser_height(props)
        return self.compose_gizmo_matrix(V_(0, 0, riser_height), (0, 0, -1))

    def get_dimension_matrix_riser_height(self, props) -> Matrix:
        return self.compose_gizmo_matrix(V_(props.tread_run, props.width, 0), (0, 0, 1))

    def get_dimension_matrix_nosing_depth(self, props) -> Matrix:
        riser_height = self._get_first_riser_height(props)
        return self.compose_gizmo_matrix(V_(-props.nosing_length, props.width / 2, riser_height), (0, 0, -1))

    def get_dimension_matrix_base_slab_depth(self, props) -> Matrix:
        return self.compose_gizmo_matrix(V_(0, props.width / 2, 0), (0, 0, -1))

    def get_dimension_matrix_top_slab_depth(self, props) -> Matrix:
        total_run = self._get_stair_total_run(props)
        return self.compose_gizmo_matrix(V_(total_run, props.width / 2, props.height), (0, 0, -1))

    def setup(self, context: bpy.types.Context) -> None:
        self.setup_editing_gizmos(context)
        self.setup_dimension_gizmos(context)

        prefs = tool.Blender.get_addon_preferences()
        highlight_color = prefs.decorator_color_selected[:3]

        self.lock_gizmo = self.gizmos.new("VIEW3D_GT_lock")
        self.lock_gizmo.use_draw_scale = False
        self.lock_gizmo.color = self.COLOR_BLUE
        self.lock_gizmo.color_highlight = highlight_color
        self.lock_gizmo.alpha = 0.8
        self.lock_gizmo.prop_path = "BIMStairProperties.total_length_lock"
        self.lock_gizmo.target_set_operator("bim.toggle_stair_total_length_lock")

        self.tread_lock_gizmo = self.gizmos.new("VIEW3D_GT_lock")
        self.tread_lock_gizmo.use_draw_scale = False
        self.tread_lock_gizmo.color = (1.0, 1.0, 1.0)
        self.tread_lock_gizmo.color_highlight = highlight_color
        self.tread_lock_gizmo.alpha = 0.8
        self.tread_lock_gizmo.prop_path = "BIMStairProperties.custom_tread_lock"
        self.tread_lock_gizmo.target_set_operator("bim.toggle_stair_custom_tread_lock")

        self.plus_gizmo = self.gizmos.new("VIEW3D_GT_plus")
        self.plus_gizmo.use_draw_scale = False
        self.plus_gizmo.color = self.COLOR_GREEN
        self.plus_gizmo.color_highlight = highlight_color
        self.plus_gizmo.alpha = 0.8
        op = self.plus_gizmo.target_set_operator("bim.adjust_stair_treads")
        op.increment = 1

        self.minus_gizmo = self.gizmos.new("VIEW3D_GT_minus")
        self.minus_gizmo.use_draw_scale = False
        self.minus_gizmo.color = self.COLOR_RED
        self.minus_gizmo.color_highlight = highlight_color
        self.minus_gizmo.alpha = 0.8
        op = self.minus_gizmo.target_set_operator("bim.adjust_stair_treads")
        op.increment = -1

    def refresh(self, context: bpy.types.Context) -> None:
        if not self.is_setup_complete():
            return
        obj = context.active_object
        if not obj:
            return

        props = self.get_props(obj)
        mw = obj.matrix_world
        billboard_rot = gizmo.get_billboard_rotation(context)
        self.update_editing_gizmos(context, mw, props)
        self.update_lock_gizmo(mw, props, billboard_rot)
        self.update_tread_lock_gizmo(props)
        self.update_tread_count_gizmos(props)
        self.update_dimension_gizmos(mw, props)

    def update_lock_gizmo(self, mw: Matrix, props, billboard_rot: Matrix) -> None:
        if self.is_gizmo_hidden_by_modal(self.lock_gizmo):
            self.lock_gizmo.hide = True
            return

        gizmo_prefs = self.get_gizmo_prefs()
        self.lock_gizmo.hide = not props.is_editing or not gizmo_prefs.lock

        if self.lock_gizmo.hide:
            return

        self.lock_gizmo.color = self.COLOR_RED if props.total_length_lock else self.COLOR_GREEN

        total_run = self._get_stair_total_run(props)
        local_transform = (
            Matrix.Translation(Vector((total_run + 0.5, -self.GIZMO_OFFSET, -self.GIZMO_OFFSET)))
            @ billboard_rot
            @ Matrix.Scale(self.EDITING_ICON_SCALE, 4)
        )
        self.lock_gizmo.matrix_basis = mw @ local_transform

    def update_tread_lock_gizmo(self, props) -> None:
        """Update visibility of tread lock gizmo. Positioning is handled in _update_editing_icon_positions."""
        if not hasattr(self, "tread_lock_gizmo"):
            return

        if self.is_gizmo_hidden_by_modal(self.tread_lock_gizmo):
            self.tread_lock_gizmo.hide = True
            return

        gizmo_prefs = self.get_gizmo_prefs()
        self.tread_lock_gizmo.hide = not props.is_editing or not gizmo_prefs.lock

    def update_tread_count_gizmos(self, props) -> None:
        """Update visibility of +/- tread count gizmos. Positioning is handled in _update_editing_icon_positions."""
        if not hasattr(self, "plus_gizmo") or not hasattr(self, "minus_gizmo"):
            return

        plus_hidden_by_modal = self.is_gizmo_hidden_by_modal(self.plus_gizmo)
        minus_hidden_by_modal = self.is_gizmo_hidden_by_modal(self.minus_gizmo)

        if plus_hidden_by_modal:
            self.plus_gizmo.hide = True
        else:
            gizmo_prefs = self.get_gizmo_prefs()
            self.plus_gizmo.hide = not props.is_editing or not gizmo_prefs.plus

        if minus_hidden_by_modal:
            self.minus_gizmo.hide = True
        else:
            gizmo_prefs = self.get_gizmo_prefs()
            self.minus_gizmo.hide = not props.is_editing or props.number_of_treads <= 1 or not gizmo_prefs.minus

    def _update_dimension_gizmo_positions(self, context: bpy.types.Context, mw: Matrix, props) -> None:
        """Update dimension gizmo positions based on camera view direction."""
        viewing_from_negative_y, viewing_from_negative_x = self.get_local_view_direction(context, mw)
        billboard_rot = gizmo.get_billboard_rotation(context)
        total_run = self._get_stair_total_run(props)
        riser_height = self._get_first_riser_height(props)

        self._update_overall_dimension_gizmos(mw, props, viewing_from_negative_y, viewing_from_negative_x, total_run)
        self._update_tread_dimension_gizmos(mw, props, viewing_from_negative_y, total_run, riser_height)
        self._update_detail_dimension_gizmos(mw, props, viewing_from_negative_y, riser_height)
        self._update_lock_gizmo_position(mw, props, viewing_from_negative_y, billboard_rot, total_run)
        self._update_editing_icon_positions(mw, props, viewing_from_negative_y, billboard_rot)

    def _update_overall_dimension_gizmos(
        self, mw: Matrix, props, viewing_from_negative_y: bool, viewing_from_negative_x: bool, total_run: float
    ) -> None:
        """Update overall dimension gizmos (total_length, width, height)."""
        if gizmo := self.get_dimension_gizmo_if_visible("total_length_target"):
            y_pos = self.get_y_position_for_view(props, viewing_from_negative_y, use_offset=True)
            gizmo.matrix_basis = mw @ self.compose_gizmo_matrix(
                V_(0, y_pos, -self.GIZMO_OFFSET), (1, 0, 0)
            )

        if gizmo := self.get_dimension_gizmo_if_visible("width"):
            x_pos = total_run + self.GIZMO_OFFSET if viewing_from_negative_x else -self.GIZMO_OFFSET
            gizmo.matrix_basis = mw @ self.compose_gizmo_matrix(
                V_(x_pos, 0, -self.GIZMO_OFFSET), (0, 1, 0)
            )

        if gizmo := self.get_dimension_gizmo_if_visible("height"):
            y_pos = self.get_y_position_for_view(props, viewing_from_negative_y, use_offset=True)
            gizmo.matrix_basis = mw @ self.compose_gizmo_matrix(
                V_(total_run + self.GIZMO_OFFSET, y_pos, 0), (0, 0, 1)
            )

    def _update_tread_dimension_gizmos(
        self, mw: Matrix, props, viewing_from_negative_y: bool, total_run: float, riser_height: float
    ) -> None:
        """Update tread-related dimension gizmos (tread_run, custom first/last tread)."""
        if gizmo := self.get_dimension_gizmo_if_visible("tread_run"):
            y_pos = self.get_y_position_for_view(props, viewing_from_negative_y, use_offset=False)
            if props.custom_tread_lock:
                x_offset, z_offset = 0, riser_height
            else:
                x_offset = props.custom_first_last_tread_run[0]
                z_offset = riser_height * 2
            gizmo.matrix_basis = mw @ self.compose_gizmo_matrix(
                V_(x_offset, y_pos, z_offset), (1, 0, 0)
            )

        if gizmo := self.get_dimension_gizmo_if_visible("custom_first_tread_run"):
            y_pos = self.get_y_position_for_view(props, viewing_from_negative_y, use_offset=False)
            gizmo.matrix_basis = mw @ self.compose_gizmo_matrix(
                V_(0, y_pos, riser_height), (1, 0, 0)
            )

        if gizmo := self.get_dimension_gizmo_if_visible("custom_last_tread_run"):
            y_pos = self.get_y_position_for_view(props, viewing_from_negative_y, use_offset=False)
            x_offset = total_run - props.custom_first_last_tread_run[1]
            gizmo.matrix_basis = mw @ self.compose_gizmo_matrix(
                V_(x_offset, y_pos, props.height), (1, 0, 0)
            )

    def _update_detail_dimension_gizmos(
        self, mw: Matrix, props, viewing_from_negative_y: bool, riser_height: float
    ) -> None:
        """Update detail dimension gizmos (nosing, tread depth, riser height)."""
        y_pos = self.get_y_position_for_view(props, viewing_from_negative_y, use_offset=False)

        self.set_dimension_gizmo_position("nosing_length", mw, V_(0, props.width / 2, riser_height), (-1, 0, 0))
        self.set_dimension_gizmo_position("tread_depth", mw, V_(0, y_pos, riser_height), (0, 0, -1))
        self.set_dimension_gizmo_position("riser_height", mw, V_(props.tread_run, y_pos, 0), (0, 0, 1))
        self.set_dimension_gizmo_position("nosing_depth", mw, V_(-props.nosing_length, props.width / 2, riser_height), (0, 0, -1))

    def _update_lock_gizmo_position(
        self, mw: Matrix, props, viewing_from_negative_y: bool, billboard_rot: Matrix, total_run: float
    ) -> None:
        """Update lock gizmo position based on Y view direction."""
        y_pos = self.get_y_position_for_view(props, viewing_from_negative_y, use_offset=True)
        self.set_icon_gizmo_position(
            "lock_gizmo", mw, total_run + 0.5, y_pos, -self.GIZMO_OFFSET, billboard_rot, scale=self.EDITING_ICON_SCALE
        )

    def _update_editing_icon_positions(self, mw, props, viewing_from_negative_y, billboard_rot):
        """Update editing icon positions, flipping Y based on viewing angle."""
        if not props.is_editing:
            return

        icon_z = props.height + 0.5
        y_pos = -self.GIZMO_OFFSET if viewing_from_negative_y else props.width + self.GIZMO_OFFSET

        self.set_icon_gizmo_position("validate_gizmo", mw, 0, y_pos, icon_z, billboard_rot)
        self.set_icon_gizmo_position("cancel_gizmo", mw, self.ICON_CANCEL_X, y_pos, icon_z, billboard_rot)
        self.set_icon_gizmo_position("cycle_gizmo", mw, self.ICON_CYCLE_X, y_pos, icon_z, billboard_rot, scale=0.3)
        self.set_icon_gizmo_position(
            "tread_lock_gizmo", mw, self.ICON_TREAD_LOCK_X, y_pos,
            icon_z - self.EDITING_ICON_SCALE / 2, billboard_rot, scale=self.EDITING_ICON_SCALE
        )
        self.set_icon_gizmo_position(
            "plus_gizmo", mw, self.ICON_PLUS_X, y_pos, icon_z, billboard_rot, scale=self.ICON_PLUS_MINUS_SCALE
        )
        self.set_icon_gizmo_position(
            "minus_gizmo", mw, self.ICON_MINUS_X, y_pos, icon_z, billboard_rot, scale=self.ICON_PLUS_MINUS_SCALE
        )
