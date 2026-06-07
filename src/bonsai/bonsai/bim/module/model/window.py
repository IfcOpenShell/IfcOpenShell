# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2023 @Andrej730
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


import collections.abc
import json
from typing import TYPE_CHECKING

import bmesh
import bpy
import ifcopenshell
import ifcopenshell.api.geometry
import ifcopenshell.api.material
import ifcopenshell.api.pset
import ifcopenshell.util.element
import ifcopenshell.util.representation
import ifcopenshell.util.unit
from bmesh.types import BMVert
from ifcopenshell.api.geometry.add_window_representation import DEFAULT_PANEL_SCHEMAS
from mathutils import Matrix, Vector

import bonsai.core.geometry
import bonsai.core.root
import bonsai.tool as tool
from bonsai.bim.module.drawing import gizmos as gizmo
from bonsai.bim.module.drawing.gizmos import DimensionGizmoConfig
from bonsai.bim.module.model.wall_offset_gizmos import WALL_OFFSET_GIZMO_CONFIGS
from bonsai.bim.parametric_lifecycle import FeatureModifierEditMixin, PickTypeMixin

if TYPE_CHECKING:
    from bonsai.bim.module.model.prop import BIMWindowProperties

V_ = tool.Blender.V_
# Shorthand for gizmo offset constants used in DimensionGizmoConfig lambdas
_G = gizmo.BaseParametricGizmoGroup


def update_window_modifier_representation(context: bpy.types.Context) -> None:
    obj = context.active_object
    assert obj
    element = tool.Ifc.get_entity(obj)
    assert element
    props = tool.Model.get_window_props(obj)
    ifc_file = tool.Ifc.get()
    si_conversion = ifcopenshell.util.unit.calculate_unit_scale(ifc_file)

    representation_data = {
        "partition_type": props.window_type,
        "overall_height": props.overall_height / si_conversion,
        "overall_width": props.overall_width / si_conversion,
        "lining_properties": {
            "LiningDepth": props.lining_depth / si_conversion,
            "LiningThickness": props.lining_thickness / si_conversion,
            "LiningOffset": props.lining_offset / si_conversion,
            "LiningToPanelOffsetX": props.lining_to_panel_offset_x / si_conversion,
            "LiningToPanelOffsetY": props.lining_to_panel_offset_y / si_conversion,
            "MullionThickness": props.mullion_thickness / si_conversion,
            "FirstMullionOffset": props.first_mullion_offset / si_conversion,
            "SecondMullionOffset": props.second_mullion_offset / si_conversion,
            "TransomThickness": props.transom_thickness / si_conversion,
            "FirstTransomOffset": props.first_transom_offset / si_conversion,
            "SecondTransomOffset": props.second_transom_offset / si_conversion,
        },
        "panel_properties": [],
    }
    number_of_panels, panels_data = props.window_types_panels[props.window_type]
    for panel_i in range(number_of_panels):
        panel_data = {
            "FrameDepth": props.frame_depth[panel_i] / si_conversion,
            "FrameThickness": props.frame_thickness[panel_i] / si_conversion,
        }
        representation_data["panel_properties"].append(panel_data)

    active_context = tool.Geometry.get_active_representation_context(obj)

    # ELEVATION_VIEW representation
    profile = ifcopenshell.util.representation.get_context(ifc_file, "Model", "Profile", "ELEVATION_VIEW")
    if profile:
        representation_data["context"] = profile
        elevation_representation = ifcopenshell.api.geometry.add_window_representation(ifc_file, **representation_data)
        tool.Model.replace_object_ifc_representation(profile, obj, elevation_representation)

    # MODEL_VIEW representation
    # (Model/Body defined only BEFORE Plan/Body to prevent #2744)
    body = ifcopenshell.util.representation.get_context(ifc_file, "Model", "Body", "MODEL_VIEW")
    representation_data["context"] = body
    representation_data["part_of_product"] = ifcopenshell.util.representation.get_part_of_product(element, body)
    model_representation = ifcopenshell.api.geometry.add_window_representation(ifc_file, **representation_data)
    representation_data["part_of_product"] = None
    tool.Model.replace_object_ifc_representation(body, obj, model_representation)
    if fallback_material := (int(props.lining_material) or int(props.framing_material) or int(props.glazing_material)):
        ifcopenshell.api.material.set_shape_aspect_constituents(
            ifc_file,
            element=element,
            context=body,
            materials={
                "Lining": tool.Ifc.get().by_id(int(props.lining_material) or fallback_material),
                "Framing": tool.Ifc.get().by_id(int(props.framing_material) or fallback_material),
                "Glazing": tool.Ifc.get().by_id(int(props.glazing_material) or fallback_material),
            },
        )
    elif material := ifcopenshell.util.element.get_material(element):
        ifcopenshell.api.material.unassign_material(ifc_file, products=[element])
        if not material.is_a("IfcMaterial") and not ifc_file.get_total_inverses(material):
            ifcopenshell.api.material.remove_material_set(ifc_file, material=material)

    # PLAN_VIEW representation
    plan = ifcopenshell.util.representation.get_context(ifc_file, "Plan", "Body", "PLAN_VIEW")
    if plan:
        representation_data["context"] = plan
        plan_representation = ifcopenshell.api.geometry.add_window_representation(ifc_file, **representation_data)
        tool.Model.replace_object_ifc_representation(plan, obj, plan_representation)

    bonsai.core.geometry.switch_representation(
        tool.Ifc,
        tool.Geometry,
        obj=obj,
        representation=ifcopenshell.util.representation.get_representation(element, active_context),
    )

    # type attributes
    if tool.Ifc.get_schema() != "IFC2X3":
        element.PartitioningType = props.window_type

    # occurrences attributes
    occurrences = tool.Ifc.get_all_element_occurrences(element)
    for occurrence in occurrences:
        occurrence.OverallWidth = props.overall_width / si_conversion
        occurrence.OverallHeight = props.overall_height / si_conversion

    tool.Model.update_simple_openings(element)


def create_bm_window_frame(
    bm: bmesh.types.BMesh, size: Vector, thickness: float | list[float], position: Vector = V_(0, 0, 0).freeze()
) -> list[bmesh.types.BMVert]:
    """`thickness` of the profile is defined as list in the following order:
    `(LEFT, TOP, RIGHT, BOTTOM)`

    `thickness` can be also defined just as 1 float value.
    """

    if not isinstance(thickness, collections.abc.Iterable):
        thickness = [thickness] * 4

    th_left, th_up, th_right, th_bottom = thickness

    width, depth, height = size

    verts = [
        (0, [th_left, 0.0, th_bottom]),
        (1, [width - th_right, 0.0, th_bottom]),
        (2, [th_left, 0.0, height - th_up]),
        (3, [width - th_right, 0.0, height - th_up]),
        (4, [0.0, 0.0, 0.0]),
        (5, [0.0, 0.0, height]),
        (6, [width, 0.0, 0.0]),
        (7, [width, 0.0, height]),
    ]

    edges = [
        (0, (0, 1)),
        (1, (2, 3)),
        (2, (4, 5)),
        (3, (6, 7)),
        (4, (7, 5)),
        (5, (1, 3)),
        (6, (4, 6)),
        (7, (0, 2)),
        (8, (2, 5)),
        (9, (3, 7)),
        (10, (4, 0)),
        (11, (1, 6)),
    ]

    faces = [
        (0, (5, 7, 3, 2)),
        (1, (2, 0, 4, 5)),
        (2, (6, 4, 0, 1)),
        (3, (6, 1, 3, 7)),
    ]

    bm.verts.index_update()
    bm.edges.index_update()
    bm.faces.ensure_lookup_table()

    new_verts = [bm.verts.new(v[1]) for v in verts]
    new_edges = [bm.edges.new([new_verts[vi] for vi in edge[1]]) for edge in edges]
    new_faces = [bm.faces.new([new_verts[vi] for vi in face[1]]) for face in faces]

    extruded = bmesh.ops.extrude_face_region(bm, geom=new_faces)
    extrusion_vector = Vector((0, 1, 0)) * depth
    translate_verts = [v for v in extruded["geom"] if isinstance(v, BMVert)]
    bmesh.ops.translate(bm, vec=extrusion_vector, verts=translate_verts)

    bmesh.ops.translate(bm, vec=position, verts=new_verts + translate_verts)

    return new_verts + translate_verts


def create_bm_box(
    bm: bmesh.types.BMesh, size: Vector = V_(1, 1, 1).freeze(), position: Vector = V_(0, 0, 0).freeze()
) -> list[bmesh.types.BMVert]:
    """create a box of `size`, position box first vertex at `position`"""
    box_verts = bmesh.ops.create_cube(bm, size=1)["verts"]
    bmesh.ops.translate(bm, vec=-box_verts[0].co, verts=box_verts)
    bmesh.ops.scale(bm, vec=size, verts=box_verts)
    bmesh.ops.translate(bm, vec=position, verts=box_verts)
    return box_verts


def create_bm_window(
    bm: bmesh.types.BMesh,
    lining_size: Vector,
    lining_thickness: list,
    lining_to_panel_offset_x,
    lining_to_panel_offset_y_full,
    frame_size: Vector,
    frame_thickness: float,
    glass_thickness: float,
    position: Vector,
    x_offsets: list | None = None,
) -> tuple[list[bmesh.types.BMVert], list[bmesh.types.BMVert], list[bmesh.types.BMVert]]:
    """`lining_thickness` and `x_offsets` are expected to be defined as a list,
    similarly to `create_bm_window_frame` `thickness` argument"""

    if x_offsets is None:
        x_offsets = [lining_to_panel_offset_x] * 4

    # window lining
    window_lining_verts = create_bm_window_frame(bm, lining_size, lining_thickness)

    # window frame
    frame_position = V_(x_offsets[0], lining_to_panel_offset_y_full, x_offsets[3])
    frame_verts = create_bm_window_frame(bm, frame_size, frame_thickness, frame_position)

    # window glass
    glass_size = frame_size - V_(frame_thickness * 2, 0, frame_thickness * 2)
    glass_size.y = glass_thickness
    glass_position = frame_position + V_(frame_thickness, frame_size.y / 2 - glass_thickness / 2, frame_thickness)

    glass_verts = create_bm_box(bm, glass_size, glass_position)

    translated_verts = window_lining_verts + frame_verts + glass_verts
    bmesh.ops.translate(bm, vec=position, verts=translated_verts)

    return (window_lining_verts, frame_verts, glass_verts)


def update_window_modifier_bmesh(context: bpy.types.Context) -> None:
    obj = context.active_object
    assert obj
    props = tool.Model.get_window_props(obj)
    if not props.is_editing:
        return

    panel_schema = DEFAULT_PANEL_SCHEMAS[props.window_type]
    accumulated_height = [0] * len(panel_schema[0])
    built_panels = []

    overall_width = props.overall_width
    lining_depth = props.lining_depth
    overall_height = props.overall_height
    lining_to_panel_offset_x = props.lining_to_panel_offset_x
    lining_to_panel_offset_y = props.lining_to_panel_offset_y
    lining_thickness = props.lining_thickness
    lining_offset = props.lining_offset

    mullion_thickness = props.mullion_thickness / 2
    first_mullion_offset = props.first_mullion_offset
    second_mullion_offset = props.second_mullion_offset
    transom_thickness = props.transom_thickness / 2
    first_transom_offset = props.first_transom_offset
    second_transom_offset = props.second_transom_offset

    glass_thickness = 0.01

    bm = bmesh.new()
    panel_schema = list(reversed(panel_schema))

    # TODO: need more readable way to define panel width and height
    unique_rows_in_col = [len(set(row[column_i] for row in panel_schema)) for column_i in range(len(panel_schema[0]))]
    for row_i, panel_row in enumerate(panel_schema):
        accumulated_width = 0
        unique_cols = len(set(panel_row))

        for column_i, panel_i in enumerate(panel_row):
            # detect mullion
            has_mullion = unique_cols > 1
            first_column = column_i == 0
            last_column = column_i == unique_cols - 1
            left_to_mullion = has_mullion and not last_column
            right_to_mullion = has_mullion and not first_column

            # detect transom
            has_transom = unique_rows_in_col[column_i] > 1
            first_row = row_i == 0
            last_row = row_i == unique_rows_in_col[column_i] - 1
            top_to_transom = has_transom and not first_row
            bottom_to_transom = has_transom and not last_row

            # calculate current panel dimensions
            if has_mullion:
                if first_column:
                    panel_width = first_mullion_offset
                elif last_column:
                    panel_width = overall_width - accumulated_width
                else:
                    panel_width = second_mullion_offset - accumulated_width
            else:
                panel_width = overall_width

            if has_transom:
                if first_row:
                    panel_height = first_transom_offset
                elif last_row:
                    panel_height = overall_height - accumulated_height[column_i]
                else:
                    panel_height = second_transom_offset - accumulated_height[column_i]
            else:
                panel_height = overall_height

            if panel_i in built_panels:
                accumulated_height[column_i] += panel_height
                accumulated_width += panel_width
                continue

            frame_depth = props.frame_depth[panel_i]
            frame_thickness = props.frame_thickness[panel_i]
            lining_to_panel_offset_y_full = (lining_depth - frame_depth) + lining_to_panel_offset_y
            # add window
            window_lining_size = V_(
                panel_width,
                lining_depth,
                panel_height,
            )

            # calculate lining thickness and frame size / offset
            # taking into account mullions and transoms
            # fmt: off
            window_lining_thickness = [
                mullion_thickness if right_to_mullion  else lining_thickness,
                transom_thickness if bottom_to_transom else lining_thickness,
                mullion_thickness if left_to_mullion   else lining_thickness,
                transom_thickness if top_to_transom    else lining_thickness,
            ]

            # x offsets can differ if there are mullions or transoms because we're trying to maintain symmetry
            base_frame_clear = lining_to_panel_offset_x + frame_thickness - lining_thickness
            current_offset_x = base_frame_clear - frame_thickness + mullion_thickness
            current_offset_z = base_frame_clear - frame_thickness + transom_thickness
            # fmt: off
            x_offsets = [
                current_offset_x if right_to_mullion  else lining_to_panel_offset_x,  # LEFT
                current_offset_z if bottom_to_transom else lining_to_panel_offset_x,  # TOP
                current_offset_x if left_to_mullion   else lining_to_panel_offset_x,  # RIGHT
                current_offset_z if top_to_transom    else lining_to_panel_offset_x,  # BOTTOM
            ]
            # fmt: on

            frame_size = window_lining_size.copy()
            frame_size.y = frame_depth
            frame_size.x -= x_offsets[0] + x_offsets[2]
            frame_size.z -= x_offsets[1] + x_offsets[3]

            window_position = V_(accumulated_width, 0, accumulated_height[column_i])
            lining_verts, panel_verts, glass_verts = create_bm_window(
                bm,
                window_lining_size,
                window_lining_thickness,
                lining_to_panel_offset_x,
                lining_to_panel_offset_y_full,
                frame_size,
                frame_thickness,
                glass_thickness,
                window_position,
                x_offsets,
            )

            built_panels.append(panel_i)

            accumulated_height[column_i] += panel_height
            accumulated_width += panel_width

    bmesh.ops.translate(bm, vec=V_(0, lining_offset, 0), verts=bm.verts)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0001)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    if bpy.context.active_object.mode == "EDIT":
        bmesh.update_edit_mesh(obj.data)
    else:
        bm.to_mesh(obj.data)
        bm.free()
    obj.data.update()


class BIM_OT_add_window(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "mesh.add_window"
    bl_label = "Add Window"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return tool.Ifc.get() and context.mode == "OBJECT"

    def _execute(self, context):
        ifc_file = tool.Ifc.get()
        if not ifc_file:
            self.report({"ERROR"}, "You need to start IFC project first to create a window.")
            return {"CANCELLED"}

        if context.active_object is not None:
            spawn_location = context.active_object.location.copy()
            context.active_object.select_set(False)
        else:
            spawn_location = bpy.context.scene.cursor.location.copy()

        mesh = bpy.data.meshes.new("IfcWindow")
        obj = bpy.data.objects.new("IfcWindow", mesh)
        obj.location = spawn_location

        element = bonsai.core.root.assign_class(
            tool.Ifc, tool.Collector, tool.Root, obj=obj, ifc_class="IfcWindow", should_add_representation=False
        )
        bonsai.core.geometry.edit_object_placement(tool.Ifc, tool.Geometry, tool.Surveyor, obj=obj)
        if tool.Ifc.get_schema() != "IFC2X3":
            element.PredefinedType = "WINDOW"

        bpy.ops.object.select_all(action="DESELECT")
        bpy.context.view_layer.objects.active = None
        bpy.context.view_layer.objects.active = obj
        tool.Blender.select_object(obj)
        bpy.ops.bim.add_window()
        return {"FINISHED"}


# UI operators
class AddWindow(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_window"
    bl_label = "Add Window"
    bl_description = "Add Bonsai parametric window to the active IFC element"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context: bpy.types.Context) -> set[str]:
        obj = context.active_object
        assert obj
        element = tool.Ifc.get_entity(obj)
        assert element
        props = tool.Model.get_window_props(obj)

        tool.Blender.get_addon_preferences().default_parameters.window.copy_to(props)

        window_data = props.get_general_kwargs(convert_to_project_units=True)
        lining_props = props.get_lining_kwargs(convert_to_project_units=True)
        panel_props = props.get_panel_kwargs(convert_to_project_units=True)

        window_data["lining_properties"] = lining_props
        window_data["panel_properties"] = panel_props
        pset = tool.Pset.get_element_pset(element, "BBIM_Window")
        if not pset:
            pset = ifcopenshell.api.pset.add_pset(tool.Ifc.get(), product=element, name="BBIM_Window")

        ifcopenshell.api.pset.edit_pset(
            tool.Ifc.get(),
            pset=pset,
            properties={"Data": tool.Ifc.get().createIfcText(json.dumps(window_data, default=list))},
        )
        update_window_modifier_representation(context)
        return {"FINISHED"}


class _WindowEditMixin(FeatureModifierEditMixin):
    """Type-specific hooks for window parametric-edit operators. Single-object
    by design (window edits target the active object only)."""

    pset_name = "BBIM_Window"

    @classmethod
    def _is_element_type(cls, element):
        return tool.Parametric.is_window(element)

    @classmethod
    def _get_props(cls, obj: bpy.types.Object):
        return tool.Model.get_window_props(obj)

    @classmethod
    def _update_modifier_representation(cls, obj: bpy.types.Object, context: bpy.types.Context) -> None:
        update_window_modifier_representation(context)


class CancelEditingWindow(_WindowEditMixin, bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.cancel_editing_window"
    bl_label = "Cancel Editing Window"
    bl_description = "Cancel editing and revert window parameters to their previous values"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context: bpy.types.Context) -> set[str]:
        return self._cancel_targets(context)


class FinishEditingWindow(_WindowEditMixin, bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.finish_editing_window"
    bl_label = "Finish Editing Window"
    bl_description = "Apply changes and finish editing window parameters"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context: bpy.types.Context) -> set[str]:
        return self._finish_targets(context)


class EnableEditingWindow(_WindowEditMixin, bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.enable_editing_window"
    bl_label = "Enable Editing Window"
    bl_description = "Enter edit mode to modify window parameters interactively"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context: bpy.types.Context) -> set[str]:
        return self._enable_targets(context)


class RemoveWindow(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.remove_window"
    bl_label = "Remove Window"
    bl_options = {"REGISTER"}

    def _execute(self, context: bpy.types.Context) -> set[str]:  # noqa: ARG002
        obj = context.active_object
        assert obj
        element = tool.Ifc.get_entity(obj)
        assert element
        props = tool.Model.get_window_props(obj)
        props.is_editing = False

        pset = tool.Pset.get_element_pset(element, "BBIM_Window")
        ifcopenshell.api.pset.remove_pset(tool.Ifc.get(), product=element, pset=pset)

        return {"FINISHED"}


class PickWindowType(bpy.types.Operator, tool.Ifc.Operator, PickTypeMixin):
    """Pick a window type from a popup menu."""

    bl_idname = "bim.pick_window_type"
    bl_label = "Pick Window Type"
    bl_options = {"REGISTER", "UNDO"}

    element_checker = tool.Parametric.is_window
    props_getter = tool.Model.get_window_props
    type_literal = tool.Model.WindowType
    type_attr = "window_type"

    def _execute(self, context: bpy.types.Context) -> set[str]:
        return self._pick_type(context)


# Frame accessor factory - creates callbacks that delegate to BIMWindowProperties methods
def _make_frame_accessors(attr_name: str, panel_index: int) -> tuple[
    "collections.abc.Callable[[BIMWindowProperties], float]",
    "collections.abc.Callable[[BIMWindowProperties, float], None]",
]:
    """Create compute/apply callbacks for frame properties at a specific panel index.

    Args:
        attr_name: Property name ("frame_depth" or "frame_thickness")
        panel_index: Panel index (0, 1, or 2)

    Returns:
        Tuple of (compute_fn, apply_fn) that delegate to BIMWindowProperties methods
    """
    return (
        lambda props: props.get_frame_value(attr_name, panel_index),
        lambda props, value: props.set_frame_value(attr_name, panel_index, value),
    )


_frame_accessors = {
    (attr, idx): _make_frame_accessors(attr, idx) for attr in ("frame_depth", "frame_thickness") for idx in range(3)
}


class GizmoWindowEdition(bpy.types.GizmoGroup, gizmo.BaseParametricGizmoGroup):
    bl_idname = "OBJECT_GGT_bim_window_edition"
    bl_label = "Window Editing Gizmo"
    bl_space_type = "VIEW_3D"
    bl_region_type = "WINDOW"
    bl_options = {"3D", "PERSISTENT"}

    enable_editing_operator = "bim.enable_editing_window"
    finish_editing_operator = "bim.finish_editing_window"
    cancel_editing_operator = "bim.cancel_editing_window"
    pick_type_operator = "bim.pick_window_type"

    # matrix_position lambdas replace the get_dimension_matrix_* methods
    dimension_gizmo_props = [
        DimensionGizmoConfig(
            attr_name="overall_width",
            axis=(1, 0, 0),
            min_value=0.01,
            text_offset_sign=-1,
            matrix_position=lambda p: V_(0, p.lining_offset - _G.GIZMO_OFFSET, -_G.GIZMO_OFFSET),
        ),
        DimensionGizmoConfig(
            attr_name="overall_height",
            axis=(0, 0, 1),
            min_value=0.01,
            text_alignment="start",
            matrix_position=lambda p: V_(p.overall_width + _G.GIZMO_OFFSET, p.lining_offset - _G.GIZMO_OFFSET, 0),
        ),
        DimensionGizmoConfig(
            attr_name="lining_depth",
            axis=(0, 1, 0),
            matrix_position=lambda p: V_(p.overall_width / 2, p.lining_offset, p.overall_height),
        ),
        DimensionGizmoConfig(
            attr_name="lining_thickness",
            axis=(1, 0, 0),
            matrix_position=lambda p: V_(0, p.lining_depth / 2 + p.lining_offset, p.overall_height / 2),
        ),
        DimensionGizmoConfig(
            attr_name="lining_to_panel_offset_x",
            axis=(1, 0, 0),
            matrix_position=lambda p: V_(
                0,
                p.get_lining_to_panel_offset_y_full() + p.frame_depth[0] + p.lining_offset,
                p.lining_to_panel_offset_x,
            ),
        ),
        DimensionGizmoConfig(
            attr_name="lining_to_panel_offset_y",
            axis=(0, 1, 0),
            min_value=-10.0,
            matrix_position=lambda p: V_(
                p.overall_width - p.lining_to_panel_offset_x,
                p.lining_depth + p.lining_offset,
                p.lining_to_panel_offset_x,
            ),
        ),
        DimensionGizmoConfig(
            attr_name="frame_depth",
            axis=(0, -1, 0),
            compute_value=_frame_accessors[("frame_depth", 0)][0],
            apply_value=_frame_accessors[("frame_depth", 0)][1],
            matrix_position=lambda p: p.get_frame_position(0, is_depth=True),
        ),
        DimensionGizmoConfig(
            attr_name="frame_thickness",
            axis=(1, 0, 0),
            compute_value=_frame_accessors[("frame_thickness", 0)][0],
            apply_value=_frame_accessors[("frame_thickness", 0)][1],
            matrix_position=lambda p: p.get_frame_position(0, is_depth=False),
        ),
        DimensionGizmoConfig(
            attr_name="second_frame_depth",
            axis=(0, -1, 0),
            compute_value=_frame_accessors[("frame_depth", 1)][0],
            apply_value=_frame_accessors[("frame_depth", 1)][1],
            visibility_condition=lambda p: p.has_second_panel(),
            matrix_position=lambda p: p.get_frame_position(1, is_depth=True),
        ),
        DimensionGizmoConfig(
            attr_name="second_frame_thickness",
            axis=(1, 0, 0),
            compute_value=_frame_accessors[("frame_thickness", 1)][0],
            apply_value=_frame_accessors[("frame_thickness", 1)][1],
            visibility_condition=lambda p: p.has_second_panel(),
            matrix_position=lambda p: p.get_frame_position(1, is_depth=False),
        ),
        DimensionGizmoConfig(
            attr_name="third_frame_depth",
            axis=(0, -1, 0),
            compute_value=_frame_accessors[("frame_depth", 2)][0],
            apply_value=_frame_accessors[("frame_depth", 2)][1],
            visibility_condition=lambda p: p.has_third_panel(),
            matrix_position=lambda p: p.get_frame_position(2, is_depth=True),
        ),
        DimensionGizmoConfig(
            attr_name="third_frame_thickness",
            axis=(1, 0, 0),
            compute_value=_frame_accessors[("frame_thickness", 2)][0],
            apply_value=_frame_accessors[("frame_thickness", 2)][1],
            visibility_condition=lambda p: p.has_third_panel(),
            matrix_position=lambda p: p.get_frame_position(2, is_depth=False),
        ),
        DimensionGizmoConfig(
            attr_name="mullion_thickness",
            axis=(1, 0, 0),
            delta_scale=2.0,
            visibility_condition=lambda p: p.has_mullion(),
            matrix_position=lambda p: V_(
                p.first_mullion_offset - p.mullion_thickness / 2,
                p.lining_offset,
                p.overall_height / 2 + 3 * _G.GIZMO_STACK_OFFSET,
            ),
        ),
        DimensionGizmoConfig(
            attr_name="first_mullion_offset",
            axis=(1, 0, 0),
            visibility_condition=lambda p: p.has_mullion(),
            matrix_position=lambda p: V_(0, p.lining_offset, p.overall_height / 2 + _G.GIZMO_STACK_OFFSET),
        ),
        DimensionGizmoConfig(
            attr_name="second_mullion_offset",
            axis=(1, 0, 0),
            visibility_condition=lambda p: p.has_second_mullion(),
            matrix_position=lambda p: V_(0, p.lining_offset, p.overall_height / 2 + 2 * _G.GIZMO_STACK_OFFSET),
        ),
        DimensionGizmoConfig(
            attr_name="transom_thickness",
            axis=(0, 0, 1),
            delta_scale=2.0,
            visibility_condition=lambda p: p.has_transom(),
            matrix_position=lambda p: V_(
                p.overall_width / 2 + 2 * _G.GIZMO_STACK_OFFSET,
                p.lining_offset,
                p.first_transom_offset - p.transom_thickness / 2,
            ),
        ),
        DimensionGizmoConfig(
            attr_name="first_transom_offset",
            axis=(0, 0, 1),
            visibility_condition=lambda p: p.has_transom(),
            matrix_position=lambda p: V_(p.overall_width / 2, p.lining_offset, 0),
        ),
        DimensionGizmoConfig(
            attr_name="second_transom_offset",
            axis=(0, 0, 1),
            visibility_condition=lambda p: p.has_second_transom(),
            matrix_position=lambda p: V_(p.overall_width / 2 + _G.GIZMO_STACK_OFFSET, p.lining_offset, 0),
        ),
        # lining_offset is handled specially in _update_dimension_gizmo_positions due to negative value support
        DimensionGizmoConfig(attr_name="lining_offset", axis=(0, 1, 0), min_value=-10.0),
        *WALL_OFFSET_GIZMO_CONFIGS,
    ]

    props_getter = tool.Model.get_window_props
    gizmo_pref_name = "window"

    @classmethod
    def is_element_type(cls, element: ifcopenshell.entity_instance) -> bool:
        return tool.Parametric.is_window(element)

    def get_icon_y_extent(self, props: "BIMWindowProperties") -> tuple[float, float]:
        """Get Y extents for window icon positioning.

        Window geometry can extend asymmetrically in +Y and -Y directions
        depending on lining_offset (which can be negative).
        """
        furthest_positive_y = (
            max(0, props.lining_offset) + props.lining_depth + props.lining_to_panel_offset_y + 2 * self.GIZMO_OFFSET
        )
        furthest_negative_y = abs(min(0, props.lining_offset)) + 2 * self.GIZMO_OFFSET
        return (furthest_positive_y, furthest_negative_y)

    # Window uses base class setup() and refresh() - no element-specific gizmos needed

    def _update_dimension_gizmo_positions(
        self, context: bpy.types.Context, mw: Matrix, props: "BIMWindowProperties"
    ) -> None:
        """Update dimension gizmo positions based on camera view direction."""
        # Window uses base implementation with default casing_offset=0
        self._update_view_dependent_dimensions(context, mw, props)
