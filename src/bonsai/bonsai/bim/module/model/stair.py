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
#
# This file was modified with the assistance of an AI coding tool.

import json

import bmesh
import bpy
import ifcopenshell
import ifcopenshell.api.pset
import ifcopenshell.util.element
import ifcopenshell.util.unit
from mathutils import Matrix, Vector

import bonsai.core.root
import bonsai.tool as tool
from bonsai.bim.module.drawing import gizmos as gizmo
from bonsai.bim.module.drawing.gizmos import (
    COLOR_GREEN,
    COLOR_RED,
    DimensionGizmoConfig,
    IconSlot,
)
from bonsai.bim.parametric_lifecycle import IntegerInputDialogMixin, PickTypeMixin
from bonsai.tool.numeric_input import (
    IntegerInputState,
    run_integer_input_modal,
    update_header,
)

V_ = tool.Blender.V_
from typing import TYPE_CHECKING, ClassVar

from bmesh.types import BMVert
from bpy.props import IntProperty

if TYPE_CHECKING:
    from bonsai.bim.module.model.prop import BIMStairProperties


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
    def poll(cls, context: bpy.types.Context) -> bool:
        return tool.Ifc.get() and context.mode == "OBJECT"

    def _execute(self, context: bpy.types.Context) -> set[str]:
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

    def _execute(self, context: bpy.types.Context) -> set[str]:
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
        return {"FINISHED"}


class CancelEditingStair(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.cancel_editing_stair"
    bl_label = "Cancel Editing Stair"
    bl_description = "Cancel editing and revert stair parameters to their previous values"
    bl_options = {"REGISTER"}

    def _execute(self, context: bpy.types.Context) -> set[str]:
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

    def _execute(self, context: bpy.types.Context) -> set[str]:
        obj = context.active_object
        assert obj
        element = tool.Ifc.get_entity(obj)
        assert element
        props = tool.Model.get_stair_props(obj)

        # Use the special method that includes custom_tread_lock for IFC storage
        data = props.get_props_kwargs_for_ifc_export(convert_to_project_units=True)
        regenerate_stair_mesh(obj)
        tool.Model.add_body_representation(obj)

        pset = tool.Pset.get_element_pset(element, "BBIM_Stair")
        data = tool.Ifc.get().createIfcText(json.dumps(data))
        ifcopenshell.api.pset.edit_pset(tool.Ifc.get(), pset=pset, properties={"Data": data})

        # update IfcStairFlight properties
        update_ifc_stair_props(obj)
        props.is_editing = False
        return {"FINISHED"}


class EnableEditingStair(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.enable_editing_stair"
    bl_label = "Enable Editing Stair"
    bl_description = "Enter edit mode to modify stair parameters interactively"
    bl_options = {"REGISTER"}

    def _execute(self, context: bpy.types.Context) -> set[str]:
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

    def _execute(self, context: bpy.types.Context) -> set[str]:
        obj = context.active_object
        assert obj
        props = tool.Model.get_stair_props(obj)
        element = tool.Ifc.get_entity(obj)
        assert element
        props.is_editing = False

        pset = tool.Pset.get_element_pset(element, "BBIM_Stair")
        ifcopenshell.api.pset.remove_pset(tool.Ifc.get(), product=element, pset=pset)

        return {"FINISHED"}


class ToggleStairProperty(bpy.types.Operator):
    """Toggle a boolean property on stair properties"""

    bl_idname = "bim.toggle_stair_property"
    bl_label = "Toggle Stair Property"
    bl_options = {"REGISTER", "UNDO"}

    property_name: bpy.props.StringProperty(
        name="Property Name",
        description="Name of the boolean property to toggle",
        options={"HIDDEN", "SKIP_SAVE"},
    )

    # Map property names to their descriptions
    PROPERTY_DESCRIPTIONS: dict[str, str] = {
        "total_length_lock": "Lock/unlock total stair length. When locked, changing treads adjusts tread depth",
        "custom_tread_lock": "Lock/unlock first and last tread dimensions. When unlocked, they can differ from other treads",
    }

    @classmethod
    def description(cls, context: bpy.types.Context, properties: bpy.types.OperatorProperties) -> str:
        prop_name = properties.property_name
        return cls.PROPERTY_DESCRIPTIONS.get(prop_name, "Toggle a boolean property on stair properties")

    def execute(self, context: bpy.types.Context) -> set[str]:
        obj = context.active_object
        if not obj or not self.property_name:
            return {"CANCELLED"}

        props = tool.Model.get_stair_props(obj)
        if hasattr(props, self.property_name):
            setattr(props, self.property_name, not getattr(props, self.property_name))
            return {"FINISHED"}
        return {"CANCELLED"}


class AdjustStairTreads(bpy.types.Operator):
    """Adjust the number of treads. Shift+click to enter a specific number."""

    bl_idname = "bim.adjust_stair_treads"
    bl_label = "Adjust Stair Treads"
    bl_options = {"REGISTER", "UNDO"}

    increment: IntProperty(name="Increment", default=1)

    def invoke(self, context: bpy.types.Context, event: bpy.types.Event) -> set[str]:
        if event.shift:
            bpy.ops.bim.set_stair_treads("INVOKE_DEFAULT")
            return {"FINISHED"}
        return self.execute(context)

    def execute(self, context: bpy.types.Context) -> set[str]:
        obj = context.active_object
        if not obj:
            return {"CANCELLED"}

        props = tool.Model.get_stair_props(obj)
        new_value = props.number_of_treads + self.increment
        if new_value >= 1:
            props.number_of_treads = new_value

        return {"FINISHED"}


class InputStairTreads(IntegerInputDialogMixin, bpy.types.Operator):
    """Popup-dialog entry point for typing a new ``number_of_treads`` value.
    Bound to the world-space ``xN`` count label in the stair edit row."""

    bl_idname = "bim.input_stair_treads"
    bl_label = "Set Number of Treads"
    bl_description = "Type the number of treads for this stair"
    bl_options = {"REGISTER", "UNDO"}

    number_of_treads: IntProperty(name="Number of Treads", default=1, min=1)
    attr_name = "number_of_treads"
    props_getter = staticmethod(tool.Model.get_stair_props)


class SetStairTreads(bpy.types.Operator):
    """Set the number of treads to a specific value."""

    bl_idname = "bim.set_stair_treads"
    bl_label = "Set Number of Treads"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    def invoke(self, context: bpy.types.Context, event: bpy.types.Event) -> set[str]:  # noqa: ARG002
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

    def modal(self, context: bpy.types.Context, event: bpy.types.Event) -> set[str]:
        return run_integer_input_modal(self, context, event)

    def _apply_value(self, context: bpy.types.Context) -> None:
        obj = context.active_object
        if not obj:
            return
        value = self._input.get_value()
        if value is not None:
            props = tool.Model.get_stair_props(obj)
            props.number_of_treads = value

    def _restore_value(self, context: bpy.types.Context) -> None:
        obj = context.active_object
        if obj:
            props = tool.Model.get_stair_props(obj)
            props.number_of_treads = self._original_value

    def _format_header(self) -> str:
        input_str = self._input.get_input_string()
        validity = "" if self._input.is_valid else " [must be >= 1]"
        return f"Number of Treads: {input_str}_{validity}  |  Enter to confirm, Esc to cancel"


class PickStairType(bpy.types.Operator, PickTypeMixin):
    """Pick a stair type from a popup menu."""

    bl_idname = "bim.pick_stair_type"
    bl_label = "Pick Stair Type"
    bl_options = {"REGISTER", "UNDO"}

    props_getter = tool.Model.get_stair_props
    type_literal = tool.Model.StairType
    type_attr = "stair_type"
    skip_element_check = True

    def execute(self, context: bpy.types.Context) -> set[str]:
        return self._pick_type(context)


# Tread run accessors - callbacks that delegate to BIMStairProperties methods
_tread_run_accessors = {
    0: (
        lambda props: props.get_custom_tread_run(0),
        lambda props, value: props.set_custom_tread_run(0, value),
    ),
    1: (
        lambda props: props.get_custom_tread_run(1),
        lambda props, value: props.set_custom_tread_run(1, value),
    ),
}

# Shorthand for gizmo offset constants used in DimensionGizmoConfig lambdas
_G = gizmo.BaseParametricGizmoGroup


class GizmoStairEdition(bpy.types.GizmoGroup, gizmo.BaseParametricGizmoGroup):
    bl_idname = "OBJECT_GGT_bim_stair_edition"
    bl_label = "Stair Editing Gizmo"
    bl_space_type = "VIEW_3D"
    bl_region_type = "WINDOW"
    bl_options = {"3D", "PERSISTENT"}

    # === Stair-Specific Icon Layout ===
    # Row order: [Validate] [Cancel] [Cycle] [TreadLock] [xN] [Plus] [Minus]
    # The base class assigns X positions from ``feature_slots`` tuple order —
    # adding an icon is a one-line append, no hardcoded X constant.
    ICON_PLUS_MINUS_SCALE = 0.24  # Scale for plus/minus icons (slightly larger)
    ICON_CYCLE_SCALE = 0.3  # Scale for cycle type icon
    ICON_COUNT_LABEL_SCALE = 0.36  # Scale for the xN tread-count label
    ICON_Z_OFFSET = 0.5  # Z offset above geometry for editing icons

    feature_slots: ClassVar[tuple[IconSlot, ...]] = (
        IconSlot(
            name="tread_lock",
            gizmo_idname="VIEW3D_GT_lock",
            variants=("open", "closed"),
            operator="bim.toggle_stair_property",
            color=(1.0, 1.0, 1.0),
            operator_props=(("property_name", "custom_tread_lock"),),
        ),
        IconSlot(name="tread_count_label", placeholder=True),
        IconSlot(
            name="plus",
            gizmo_idname="VIEW3D_GT_plus",
            operator="bim.adjust_stair_treads",
            scale=ICON_PLUS_MINUS_SCALE,
            color=COLOR_GREEN,
            operator_props=(("increment", 1),),
        ),
        IconSlot(
            name="minus",
            gizmo_idname="VIEW3D_GT_minus",
            operator="bim.adjust_stair_treads",
            scale=ICON_PLUS_MINUS_SCALE,
            color=COLOR_RED,
            operator_props=(("increment", -1),),
        ),
    )

    enable_editing_operator = "bim.enable_editing_stair"
    finish_editing_operator = "bim.finish_editing_stair"
    cancel_editing_operator = "bim.cancel_editing_stair"
    pick_type_operator = "bim.pick_stair_type"

    def get_icon_y_extent(self, props: "BIMStairProperties") -> tuple[float, float]:
        """Get Y extents for stair icon positioning.

        Stair geometry extends from Y=0 to Y=width.
        Icons are positioned beyond the width on either side.
        """
        furthest_y = props.width + 2 * self.GIZMO_OFFSET
        return (furthest_y, furthest_y)

    dimension_gizmo_props = [
        DimensionGizmoConfig(
            attr_name="total_length_target",
            axis=(1, 0, 0),
            prop_name="Total Length",
            min_value=0.01,
            text_offset_sign=-1,
            matrix_position=lambda p: V_(0, -_G.GIZMO_OFFSET, -_G.GIZMO_OFFSET),
        ),
        DimensionGizmoConfig(
            attr_name="height",
            axis=(0, 0, 1),
            min_value=0.01,
            text_alignment="start",
            matrix_position=lambda p: V_(p.get_total_run() + _G.GIZMO_OFFSET, -_G.GIZMO_OFFSET, 0),
        ),
        DimensionGizmoConfig(
            attr_name="width",
            axis=(0, 1, 0),
            min_value=0.01,
            matrix_position=lambda p: V_(_G.GIZMO_OFFSET, 0, -_G.GIZMO_OFFSET),
        ),
        DimensionGizmoConfig(
            attr_name="tread_run",
            axis=(1, 0, 0),
            min_value=0.01,
            visibility_condition=lambda p: p.has_tread_run_gizmo(),
            matrix_position=lambda p: V_(
                0 if p.custom_tread_lock else p.custom_first_last_tread_run[0],
                0,
                p.get_riser_height() if p.custom_tread_lock else p.get_riser_height() * 2,
            ),
        ),
        DimensionGizmoConfig(
            attr_name="custom_first_tread_run",
            axis=(1, 0, 0),
            prop_name="First Tread",
            min_value=0.01,
            visibility_condition=lambda p: p.has_custom_treads(),
            compute_value=_tread_run_accessors[0][0],
            apply_value=_tread_run_accessors[0][1],
            matrix_position=lambda p: V_(0, 0, p.get_riser_height()),
        ),
        DimensionGizmoConfig(
            attr_name="custom_last_tread_run",
            axis=(1, 0, 0),
            prop_name="Last Tread",
            min_value=0.01,
            visibility_condition=lambda p: p.has_custom_treads(),
            compute_value=_tread_run_accessors[1][0],
            apply_value=_tread_run_accessors[1][1],
            matrix_position=lambda p: V_(p.get_total_run() - p.custom_first_last_tread_run[1], 0, p.height),
        ),
        DimensionGizmoConfig(
            attr_name="nosing_length",
            axis=(-1, 0, 0),
            matrix_position=lambda p: V_(0, p.width / 2, p.get_riser_height()),
        ),
        DimensionGizmoConfig(
            attr_name="tread_depth",
            axis=(0, 0, -1),
            visibility_condition=lambda p: p.has_tread_depth(),
            matrix_position=lambda p: V_(0, 0, p.get_riser_height()),
        ),
        DimensionGizmoConfig(
            attr_name="riser_height",
            axis=(0, 0, 1),
            min_value=0.01,
            text_alignment="start",
            compute_value=lambda p: p.get_riser_height(),
            apply_value=lambda p, v: p.set_riser_height(v),
            matrix_position=lambda p: V_(p.tread_run, p.width, 0),
        ),
        DimensionGizmoConfig(
            attr_name="nosing_depth",
            axis=(0, 0, -1),
            visibility_condition=lambda p: p.has_nosing(),
            matrix_position=lambda p: V_(-p.nosing_length, p.width / 2, p.get_riser_height()),
        ),
        DimensionGizmoConfig(
            attr_name="base_slab_depth",
            axis=(0, 0, -1),
            visibility_condition=lambda p: p.is_concrete_stair(),
            matrix_position=lambda p: V_(0, p.width / 2, 0),
        ),
        DimensionGizmoConfig(
            attr_name="top_slab_depth",
            axis=(0, 0, -1),
            visibility_condition=lambda p: p.is_concrete_stair(),
            matrix_position=lambda p: V_(p.get_total_run(), p.width / 2, p.height),
        ),
    ]

    # Metadata-driven dispatch for props and preferences
    props_getter = tool.Model.get_stair_props
    gizmo_pref_name = "stair"

    @classmethod
    def is_element_type(cls, element: ifcopenshell.entity_instance) -> bool:
        return tool.Parametric.is_stair(element)

    def setup_element_specific_gizmos(self, context: bpy.types.Context) -> None:
        """Create the total-length lock as an open/closed pair plus the
        ``xN`` tread-count label. Lock click toggles
        ``props.total_length_lock``; the per-frame update hook picks which
        member is visible. Anchored to the stair's far X end (not the edit
        row) so it's positioned by ``_update_lock_gizmo_position`` rather
        than the toolbar slot system.

        The count label binds to ``bim.input_stair_treads`` (popup dialog)
        for click-to-type input and sits at the X reserved by the
        ``tread_count_label`` placeholder slot in ``feature_slots``."""
        self.total_length_lock_open_gizmo, self.total_length_lock_closed_gizmo = self.create_icon_gizmo_lock_pair(
            "bim.toggle_stair_property",
            self.COLOR_BLUE,
            property_name="total_length_lock",
        )
        default_color, highlight_color = self.get_decoration_colors()
        self.tread_count_label_gizmo = self.gizmos.new("BIM_GT_count_label")
        self.tread_count_label_gizmo.use_draw_scale = False
        self.tread_count_label_gizmo.color = default_color
        self.tread_count_label_gizmo.color_highlight = highlight_color
        self.tread_count_label_gizmo.alpha = 0.8
        self.tread_count_label_gizmo.target_set_operator("bim.input_stair_treads")

    def _refresh_element_specific(
        self, context: bpy.types.Context, mw: Matrix, props: "BIMStairProperties"  # noqa: ARG002
    ) -> None:
        """Update stair-specific lock and tread count gizmos. Lock positioning is
        handled per-frame in the dimension-positioning hook."""
        self.update_lock_gizmo(props)
        self.update_tread_lock_gizmo(props)
        self.update_tread_count_gizmos(props)

    def update_lock_gizmo(self, props: "BIMStairProperties") -> None:
        """Show the open/closed total-length lock variant matching
        ``props.total_length_lock``. Positioning is handled per-frame by
        the dimension-positioning hook."""
        if not hasattr(self, "total_length_lock_open_gizmo"):
            return
        if not props.is_editing:
            self.total_length_lock_open_gizmo.hide = True
            self.total_length_lock_closed_gizmo.hide = True
            return
        self.total_length_lock_open_gizmo.hide = props.total_length_lock
        self.total_length_lock_closed_gizmo.hide = not props.total_length_lock

    def update_tread_lock_gizmo(self, props: "BIMStairProperties") -> None:
        """Show the open/closed lock variant matching ``props.custom_tread_lock``.

        Both pair members share an X position (set by the base's slot
        positioning); this picks which one is visible per frame so a state
        flip can't reveal both at once."""
        if not hasattr(self, "tread_lock_open_gizmo"):
            return
        if not props.is_editing:
            self.tread_lock_open_gizmo.hide = True
            self.tread_lock_closed_gizmo.hide = True
            return
        self.tread_lock_open_gizmo.hide = props.custom_tread_lock
        self.tread_lock_closed_gizmo.hide = not props.custom_tread_lock

    def update_tread_count_gizmos(self, props: "BIMStairProperties") -> None:
        """Update visibility of the +/- tread count gizmos and the ``xN``
        label. Positioning is handled in ``_update_editing_icon_positions``."""
        if not hasattr(self, "plus_gizmo") or not hasattr(self, "minus_gizmo"):
            return
        self.update_gizmo_visibility(self.plus_gizmo, props.is_editing)
        # Minus has additional condition: number_of_treads > 1
        self.update_gizmo_visibility(self.minus_gizmo, props.is_editing and props.number_of_treads > 1)
        if hasattr(self, "tread_count_label_gizmo"):
            self.update_gizmo_visibility(self.tread_count_label_gizmo, props.is_editing)

    def _update_dimension_gizmo_positions(
        self, context: bpy.types.Context, mw: Matrix, props: "BIMStairProperties"  # noqa: ARG002
    ) -> None:
        """Update dimension gizmo positions based on camera view direction."""
        viewing_from_negative_y, viewing_from_negative_x = self._frame_view_dir
        billboard_rot = self._frame_billboard_rot
        total_run = props.get_total_run()
        riser_height = props.get_riser_height()

        self._update_overall_dimension_gizmos(mw, props, viewing_from_negative_y, viewing_from_negative_x, total_run)
        self._update_tread_dimension_gizmos(mw, props, viewing_from_negative_y, total_run, riser_height)
        self._update_detail_dimension_gizmos(mw, props, viewing_from_negative_y, riser_height)
        self._update_lock_gizmo_position(mw, props, viewing_from_negative_y, billboard_rot, total_run)
        self._update_editing_icon_positions(mw, props, viewing_from_negative_y, billboard_rot)

    def _update_overall_dimension_gizmos(
        self,
        mw: Matrix,
        props: "BIMStairProperties",
        viewing_from_negative_y: bool,
        viewing_from_negative_x: bool,
        total_run: float,
    ) -> None:
        """Update overall dimension gizmos (total_length, width, height)."""
        y_pos_offset = self.get_y_position_for_view(props, viewing_from_negative_y, use_offset=True)
        x_pos = total_run + self.GIZMO_OFFSET if viewing_from_negative_x else -self.GIZMO_OFFSET

        self.set_dimension_gizmo_position("total_length_target", mw, V_(0, y_pos_offset, -self.GIZMO_OFFSET), (1, 0, 0))
        self.set_dimension_gizmo_position("width", mw, V_(x_pos, 0, -self.GIZMO_OFFSET), (0, 1, 0))
        self.set_dimension_gizmo_position("height", mw, V_(total_run + self.GIZMO_OFFSET, y_pos_offset, 0), (0, 0, 1))

    def _update_tread_dimension_gizmos(
        self,
        mw: Matrix,
        props: "BIMStairProperties",
        viewing_from_negative_y: bool,
        total_run: float,
        riser_height: float,
    ) -> None:
        """Update tread-related dimension gizmos (tread_run, custom first/last tread)."""
        y_pos = self.get_y_position_for_view(props, viewing_from_negative_y, use_offset=False)

        # tread_run position depends on custom_tread_lock state
        if props.custom_tread_lock:
            tread_x, tread_z = 0, riser_height
        else:
            tread_x = props.custom_first_last_tread_run[0]
            tread_z = riser_height * 2
        self.set_dimension_gizmo_position("tread_run", mw, V_(tread_x, y_pos, tread_z), (1, 0, 0))

        self.set_dimension_gizmo_position("custom_first_tread_run", mw, V_(0, y_pos, riser_height), (1, 0, 0))

        last_x = total_run - props.custom_first_last_tread_run[1]
        self.set_dimension_gizmo_position("custom_last_tread_run", mw, V_(last_x, y_pos, props.height), (1, 0, 0))

    def _update_detail_dimension_gizmos(
        self, mw: Matrix, props: "BIMStairProperties", viewing_from_negative_y: bool, riser_height: float
    ) -> None:
        """Update detail dimension gizmos (nosing, tread depth, riser height)."""
        y_pos = self.get_y_position_for_view(props, viewing_from_negative_y, use_offset=False)

        self.set_dimension_gizmo_position("nosing_length", mw, V_(0, props.width / 2, riser_height), (-1, 0, 0))
        self.set_dimension_gizmo_position("tread_depth", mw, V_(0, y_pos, riser_height), (0, 0, -1))
        self.set_dimension_gizmo_position("riser_height", mw, V_(props.tread_run, y_pos, 0), (0, 0, 1))
        self.set_dimension_gizmo_position(
            "nosing_depth", mw, V_(-props.nosing_length, props.width / 2, riser_height), (0, 0, -1)
        )

    def _update_lock_gizmo_position(
        self,
        mw: Matrix,
        props: "BIMStairProperties",
        viewing_from_negative_y: bool,
        billboard_rot: Matrix,
        total_run: float,
    ) -> None:
        """Update lock gizmo pair position based on Y view direction. Writes
        the matrix on both members so a state flip can't reveal a stale pose."""
        y_pos = self.get_y_position_for_view(props, viewing_from_negative_y, use_offset=True)
        self.set_icon_gizmo_pair_position(
            "total_length_lock_open_gizmo",
            "total_length_lock_closed_gizmo",
            mw,
            total_run + self.ICON_Z_OFFSET,
            y_pos,
            -self.GIZMO_OFFSET,
            billboard_rot,
            scale=self.EDITING_ICON_SCALE,
        )

    def _update_editing_icon_positions(
        self, mw: Matrix, props: "BIMStairProperties", viewing_from_negative_y: bool, billboard_rot: Matrix
    ) -> None:
        """Reposition the editing icons at stair's view-dependent Y. The base
        class's update_editing_gizmos already placed them at the default
        ``get_icon_y_offset`` Y — this overrides with the stair-specific
        ``get_icon_y_for_view`` flip so the icons land on the side the
        camera is looking from."""
        if not props.is_editing:
            return

        icon_z = props.height + self.ICON_Z_OFFSET
        y_pos = self.get_icon_y_for_view(props, viewing_from_negative_y)
        slot_x = self._slot_x_positions()

        self.set_icon_gizmo_position("validate_gizmo", mw, 0, y_pos, icon_z, billboard_rot)
        self.set_icon_gizmo_position("cancel_gizmo", mw, self.ICON_CANCEL_X, y_pos, icon_z, billboard_rot)
        self.set_icon_gizmo_position(
            "cycle_gizmo", mw, self.ICON_CYCLE_X, y_pos, icon_z, billboard_rot, scale=self.ICON_CYCLE_SCALE
        )
        self.set_icon_gizmo_pair_position(
            "tread_lock_open_gizmo",
            "tread_lock_closed_gizmo",
            mw,
            slot_x["tread_lock"],
            y_pos,
            icon_z - self.EDITING_ICON_SCALE / 2,
            billboard_rot,
            scale=self.EDITING_ICON_SCALE,
        )
        self.set_icon_gizmo_position(
            "plus_gizmo", mw, slot_x["plus"], y_pos, icon_z, billboard_rot, scale=self.ICON_PLUS_MINUS_SCALE
        )
        self.set_icon_gizmo_position(
            "minus_gizmo", mw, slot_x["minus"], y_pos, icon_z, billboard_rot, scale=self.ICON_PLUS_MINUS_SCALE
        )
        if hasattr(self, "tread_count_label_gizmo"):
            self.tread_count_label_gizmo.set_count(int(props.number_of_treads))
            self.set_icon_gizmo_position(
                "tread_count_label_gizmo",
                mw,
                slot_x["tread_count_label"],
                y_pos,
                icon_z,
                billboard_rot,
                scale=self.ICON_COUNT_LABEL_SCALE,
            )
