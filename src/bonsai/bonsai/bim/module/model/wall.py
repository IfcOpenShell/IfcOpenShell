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
#
# This file was modified with the assistance of an AI coding tool.
#
# pyright: reportUnnecessaryTypeIgnoreComment=error

import copy
import math
import weakref
from collections.abc import Iterable
from math import atan2, cos, degrees, pi, sin
from typing import TYPE_CHECKING, Any, ClassVar, Literal, Optional, Union, get_args

import bmesh
import bpy
import ifcopenshell
import ifcopenshell.api.feature
import ifcopenshell.api.geometry
import ifcopenshell.api.material
import ifcopenshell.api.pset
import ifcopenshell.api.root
import ifcopenshell.api.type
import ifcopenshell.geom
import ifcopenshell.util.element
import ifcopenshell.util.placement
import ifcopenshell.util.representation
import ifcopenshell.util.shape
import ifcopenshell.util.shape_builder
import ifcopenshell.util.type
import ifcopenshell.util.unit
import mathutils.geometry
import numpy as np
from mathutils import Matrix, Vector

import bonsai.core.connection
import bonsai.core.geometry
import bonsai.core.model as core
import bonsai.core.root
import bonsai.core.spatial
import bonsai.tool as tool
from bonsai.bim.ifc import IfcStore
from bonsai.bim.module.drawing import gizmos as gizmo
from bonsai.bim.module.drawing.gizmos import DimensionGizmoConfig, IconSlot
from bonsai.bim.module.model import preview_base
from bonsai.bim.module.model.decorator import (
    _BBOX_HIGHLIGHT_LINE_ALPHA,
    _BBOX_HIGHLIGHT_LINE_WIDTH,
    PolylineDecorator,
    ProductDecorator,
    bbox_world_edges,
    draw_polyline_segments,
)
from bonsai.bim.module.model.polyline import PolylineOperator

if TYPE_CHECKING:
    from bonsai.bim.module.model.prop import BIMWallProperties


_FILLET_DEFAULT_RADIUS_M = 0.5  # Fallback when the leg-fraction heuristic cannot resolve a value.
_FILLET_DEFAULT_LEG_FRACTION = 0.25  # Quarter of the shorter available leg — visible without overrunning either wall.
_FILLET_MIN_RADIUS_M = 0.001  # Lower bound — anything smaller renders as a single pixel at common viewport scales.

_ARRAY_CHILD_POLL_MESSAGE = "Selection includes an array child; operate on the array parent instead."


def _poll_reject_array_children(operator_cls) -> bool:
    """Shared operator-poll guard: set the array-child poll message on
    ``operator_cls`` and return ``True`` when the selection includes a Bonsai
    array child, so the caller can early-return ``False`` from its ``poll``.

    Topology mutations against an array child are wiped by the next
    ``regenerate_array`` and would orphan the child's GUID in the parent's
    ``BBIM_Array.Data``. Gizmo groups have their own filter via
    ``_wall_topology_gizmo_poll_gate``; this helper exists so operator
    classes share the same rejection in one line."""
    if tool.Blender.Modifier.any_selected_is_array_child():
        operator_cls.poll_message_set(_ARRAY_CHILD_POLL_MESSAGE)
        return True
    return False


def _wall_gizmo_poll_gate(context: bpy.types.Context) -> bool:
    """Common pre-flight gate every wall gizmo group's ``poll`` runs first:
    viewport gizmos are enabled AND no preview is active. Centralises the
    two checks every wall gizmo group otherwise duplicates inline; returning
    ``False`` here short-circuits the caller's poll before any per-feature
    selection inspection runs."""
    if not tool.Blender.are_viewport_gizmos_enabled():
        return False
    if preview_base.any_preview_active(context):
        return False
    return True


def _resolve_active_partner_pair(
    context: bpy.types.Context,
) -> "tuple[bpy.types.Object, bpy.types.Object, ifcopenshell.entity_instance, ifcopenshell.entity_instance] | None":
    """Return ``(active_obj, partner_obj, active_elem, partner_elem)`` for a
    selection of exactly two IFC-bound objects with the active one named,
    else ``None``. Used by every 2-selection gizmo to skip the standard
    "resolve active + partner + IFC entities" preamble."""
    active = tool.Blender.get_active_object(is_selected=True)
    if active is None:
        return None
    selected = list(tool.Blender.get_selected_objects())
    if len(selected) != 2:
        return None
    partner = next((o for o in selected if o != active), None)
    if partner is None:
        return None
    active_elem = tool.Ifc.get_entity(active)
    partner_elem = tool.Ifc.get_entity(partner)
    if active_elem is None or partner_elem is None:
        return None
    return active, partner, active_elem, partner_elem


def _slab_connection_gizmo_poll_gate(context: bpy.types.Context, *, require_editing: bool = False) -> bool:
    """Shared gate for slab-side connection gizmos: exactly 1 IfcSlab
    selected, not an array child, has at least one wall clipped to its
    underside. With ``require_editing=True`` additionally requires the
    slab's parametric edit lifecycle to be active (pen icon clicked) so
    the gizmo only surfaces after explicit opt-in."""
    active = tool.Blender.get_active_object(is_selected=True)
    if active is None:
        return False
    if len(tool.Blender.get_selected_objects()) != 1:
        return False
    element = tool.Ifc.get_entity(active)
    if element is None or not element.is_a("IfcSlab"):
        return False
    if tool.Blender.Modifier.any_selected_is_array_child():
        return False
    if require_editing and not tool.Model.get_slab_props(active).is_editing:
        return False
    return any(tool.Wall.iter_slab_wall_connections(element))


def _wall_topology_gizmo_poll_gate(context: bpy.types.Context) -> bool:
    """Tighter gate for wall topology gizmos (merge / join / extend / unjoin
    / fillet): base ``_wall_gizmo_poll_gate`` plus an array-child filter.
    Array children are managed replicas — any topology mutation is wiped by
    the next ``regenerate_array``, and ``merge`` would orphan a GUID listed
    in the parent's ``BBIM_Array.Data``. Host-opening gizmos (add / toggle)
    deliberately stay on the base gate so openings remain authorable on
    children, which the array regen pipeline preserves."""
    if not _wall_gizmo_poll_gate(context):
        return False
    if tool.Blender.Modifier.any_selected_is_array_child():
        return False
    return True


def _wall_has_openings(gz_group: bpy.types.GizmoGroup) -> bool:
    """``visible_when`` predicate for the toggle_openings idle slot. Returns
    True iff the active object's IFC element exposes a non-empty HasOpenings
    inverse — keeps the toggle hidden on walls that carry no opening cuts."""
    obj = bpy.context.active_object
    if obj is None:
        return False
    element = tool.Ifc.get_entity(obj)
    if element is None:
        return False
    return tool.Geometry.has_openings(element)


def regenerate_wall_mesh_from_props(obj: bpy.types.Object) -> None:
    """Rebuild ``obj.data`` as a preview box from ``BIMWallProperties`` without touching IFC.

    The preview omits openings, layer materials, and connection joins; those are
    resolved on commit by ``recreate_wall`` / ``recalculate_walls``."""
    props = tool.Model.get_wall_props(obj)
    length = max(props.length, 0.001)
    height = max(props.height, 0.001)
    thickness = max(props.thickness, 0.001)
    offset = props.offset
    x_angle = props.x_angle
    x0 = props.anchor_x
    x1 = x0 + length
    y0 = offset
    y1 = offset + thickness
    # Slope shifts the top face along +Y by height * tan(x_angle), keeping the bottom fixed.
    y_top_shift = core.displacement_from_x_angle(height, x_angle) if x_angle else 0.0

    bm = bmesh.new()
    verts = [
        bm.verts.new((x0, y0, 0.0)),
        bm.verts.new((x1, y0, 0.0)),
        bm.verts.new((x1, y1, 0.0)),
        bm.verts.new((x0, y1, 0.0)),
        bm.verts.new((x0, y0 + y_top_shift, height)),
        bm.verts.new((x1, y0 + y_top_shift, height)),
        bm.verts.new((x1, y1 + y_top_shift, height)),
        bm.verts.new((x0, y1 + y_top_shift, height)),
    ]
    bm.faces.new([verts[0], verts[1], verts[2], verts[3]])
    bm.faces.new([verts[7], verts[6], verts[5], verts[4]])
    bm.faces.new([verts[0], verts[4], verts[5], verts[1]])
    bm.faces.new([verts[3], verts[2], verts[6], verts[7]])
    bm.faces.new([verts[0], verts[3], verts[7], verts[4]])
    bm.faces.new([verts[1], verts[5], verts[6], verts[2]])

    assert isinstance(obj.data, bpy.types.Mesh)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()
    # Mark the mesh as having diverged from the IFC-derived geometry. cancel /
    # no-op-finish reads this and calls recreate_wall to restore openings & layers.
    tool.Model.get_wall_props(obj).mesh_dirty = True


def _restore_wall_mesh_if_dirty(obj: bpy.types.Object) -> None:
    """Re-derive the wall mesh from IFC if the bmesh preview replaced the real geometry.

    Idempotent: clears the dirty flag after restoring. Does call into
    ``ifcopenshell.api.geometry.regenerate_wall_representation`` (one ifc.run), which is
    acceptable here because cancel / no-op-finish are explicit user actions, not per-frame
    events. Skipping the call when no drag happened preserves the byte-identical guarantee
    for the common enable → ✓ no-drag round-trip."""
    props = tool.Model.get_wall_props(obj)
    if not props.mesh_dirty:
        return
    element = tool.Ifc.get_entity(obj)
    if element:
        tool.Model.recreate_wall(element, obj)
    props.mesh_dirty = False


def _read_wall_state_into_props(obj: bpy.types.Object, props: "BIMWallProperties") -> None:
    """Populate the draft props from current IFC state. Caller must have validated the
    wall via ``tool.Wall.validate_for_parametric_edit`` first — this function assumes the
    wall has a LAYER2 usage and an extruded MODEL_VIEW body."""
    geom = tool.Wall.read_geometry(obj)
    assert geom

    props.anchor_x = geom["anchor_x"]
    props.length = max(0.01, geom["length"])
    props.height = max(0.01, geom["height"])
    props.x_angle = geom["x_angle"]
    props.thickness = max(0.001, geom["thickness"])
    props.offset = geom["offset"]
    props.desired_offset_baseline = core.baseline_from_offset(props.offset, props.thickness)

    props.snap_length = props.length
    props.snap_height = props.height
    props.snap_thickness = props.thickness
    props.snap_offset = props.offset
    props.snap_x_angle = props.x_angle
    props.snap_offset_baseline = props.desired_offset_baseline


def _maybe_resync_wall_props_from_ifc(obj: "bpy.types.Object | None") -> None:
    """Re-prime ``BIMWallProperties`` from current IFC after an IFC mutation, so
    non-edit-mode gizmos read post-mutation coordinates. Must be called from an
    operator's ``_execute`` — ID writes from ``GizmoGroup.refresh`` raise
    ``AttributeError: Writing to ID classes in this context is not allowed``.
    No-op during a draft session; the draft is then the source of truth."""
    if obj is None:
        return
    if tool.Wall.validate_for_parametric_edit(obj) is not None:
        return
    props = tool.Model.get_wall_props(obj)
    if props.is_editing:
        return
    _read_wall_state_into_props(obj, props)


def _resync_walls_after_mutation(objs: Iterable["bpy.types.Object | None"]) -> None:
    """Re-prime each wall's draft props after a one-shot IFC mutation. Safe to
    call from operator ``_execute``: ID writes are allowed there, unlike gizmo
    refresh."""
    for obj in objs:
        _maybe_resync_wall_props_from_ifc(obj)


def _regenerate_walls(objs: "Iterable[bpy.types.Object | None]") -> None:
    """Rebuild every wall in ``objs`` from current IFC state — extrusion,
    openings, and any underside slab clip — so the caller doesn't carry
    feature-specific dispatch."""
    for obj in objs:
        if obj is not None:
            tool.Model.regenerate_wall(obj)


class _CommitWallDraftsFirstMixin:
    """Operator mixin that flushes any in-progress wall parametric drafts in
    the current selection before delegating to the subclass's ``_perform``.

    Subclasses implement ``_perform`` instead of ``_execute``; the IFC
    transaction opened by ``tool.Ifc.Operator.execute`` wraps both the
    commit and the perform.

    Place this BEFORE ``bpy.types.Operator`` in the bases tuple so the
    mixin's ``_execute`` resolves first in the MRO."""

    def _execute(self, context: bpy.types.Context):
        _commit_pending_wall_edits_for_selection(context)
        return self._perform(context)

    def _perform(self, context: bpy.types.Context):
        raise NotImplementedError("Subclasses of _CommitWallDraftsFirstMixin must implement _perform.")


class UnjoinWalls(_CommitWallDraftsFirstMixin, bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.unjoin_walls"
    bl_label = "Unjoin Walls"
    bl_description = "Unjoin the selected walls"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if not tool.Model.has_selected_ifc_objects():
            cls.poll_message_set("No IFC objects selected.")
            return False
        if _poll_reject_array_children(cls):
            return False
        return True

    def _perform(self, context):
        core.unjoin_walls(tool.Ifc, tool.Blender, tool.Geometry, DumbWallJoiner(), tool.Model)
        _resync_walls_after_mutation(tool.Blender.get_selected_objects())


class DisconnectElements(_CommitWallDraftsFirstMixin, bpy.types.Operator, tool.Ifc.Operator):
    """Disconnect two IFC elements given their GlobalIds — generic dispatcher
    that infers the connection rel kind via tool.Connection.find_rels and runs
    the right post-disconnect cleanup:

    - ``"path"`` (IfcRelConnectsPathElements) → removes every rel between
      the pair (catches both orientations) via remove_connection + recreates
      both walls + resyncs drafts.
    - ``"element-top"`` (IfcRelConnectsElements with Description=="TOP") →
      disconnect_element + regenerate_wall_to_underside on the wall side.
    - ``"element"`` (other IfcRelConnectsElements) → disconnect_element only.

    Both endpoints by GlobalId so the dispatch survives rename / undo / save.
    Replaces the previous typed UnjoinWallPathConnection + DisconnectWallSlab
    operators with one entry-point gizmos and shortcuts can bind to."""

    bl_idname = "bim.disconnect_elements"
    bl_label = "Disconnect Elements"
    bl_description = "Remove the connection between two IFC elements identified by GlobalId"
    bl_options = {"REGISTER", "UNDO"}

    element_a_guid: bpy.props.StringProperty(name="Element A GlobalId")
    element_b_guid: bpy.props.StringProperty(name="Element B GlobalId")

    @classmethod
    def poll(cls, context):
        if not tool.Model.has_selected_ifc_objects():
            cls.poll_message_set("No IFC objects selected.")
            return False
        if _poll_reject_array_children(cls):
            return False
        return True

    def _perform(self, context):
        ifc_file = tool.Ifc.get()
        try:
            elem_a = ifc_file.by_guid(self.element_a_guid) if self.element_a_guid else None
            elem_b = ifc_file.by_guid(self.element_b_guid) if self.element_b_guid else None
        except RuntimeError:
            elem_a = elem_b = None
        if elem_a is None or elem_b is None:
            self.report({"ERROR"}, "Could not resolve elements from supplied GlobalIds.")
            return
        rels = tool.Connection.find_rels(elem_a, elem_b)
        if not rels:
            self.report({"ERROR"}, "No connection found between elements.")
            return
        # The fillet corner's join with its source walls defines the fillet's
        # identity — unjoining there would tear down the chord axis reference
        # without rebuilding the source walls' miter cuts. Deleting the corner
        # wall is the supported teardown, which cascades back to the source
        # walls via the connection-cleanup handler.
        either_is_fillet = tool.Parametric.is_fillet_corner_wall(elem_a) or tool.Parametric.is_fillet_corner_wall(
            elem_b
        )
        if either_is_fillet and any(k == "path" for _, k in rels):
            self.report(
                {"INFO"},
                "Fillet wall path connections can't be unjoined — delete the fillet wall element to remove the corner.",
            )
            return
        path_objs: list[bpy.types.Object] = []
        for subject, kind in rels:
            bonsai.core.connection.disconnect_rel(
                tool.Ifc,
                tool.Geometry,
                tool.Model,
                tool.Connection,
                subject=subject,
                kind=kind,
                elem=elem_a,
                partner=elem_b,
            )
            if kind == "path":
                obj_a = tool.Ifc.get_object(elem_a)
                obj_b = tool.Ifc.get_object(elem_b)
                if obj_a is not None and obj_a not in path_objs:
                    path_objs.append(obj_a)
                if obj_b is not None and obj_b not in path_objs:
                    path_objs.append(obj_b)
        if path_objs:
            _resync_walls_after_mutation(path_objs)


class ExtendWallsToUnderside(_CommitWallDraftsFirstMixin, bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.extend_walls_to_underside"
    bl_label = "Extend Walls To Underside"
    bl_description = "Extend and clip selected walls at the bottom faces of an object"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if not tool.Model.has_selected_ifc_objects():
            cls.poll_message_set("No IFC objects selected.")
            return False
        return True

    def _perform(self, context):
        slabs: list[bpy.types.Object] = []
        walls: list[bpy.types.Object] = []
        for obj in tool.Blender.get_selected_objects():
            element = tool.Ifc.get_entity(obj)
            if not element:
                continue
            if tool.Parametric.is_path_connectable_wall(element):
                walls.append(obj)
            else:
                slabs.append(obj)
        if slabs and walls:
            core.extend_wall_to_slab(tool.Ifc, tool.Geometry, tool.Model, slabs, walls)
            _resync_walls_after_mutation(walls)
        else:
            self.report({"ERROR"}, "Please select at least one LAYER2 element and at least one other IFC element")


class RegenerateWallToUnderside(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.regenerate_wall_to_underside"
    bl_label = "Regenerate Wall to Underside"
    bl_description = "Re-clip selected walls to their connected underside objects after the slab has moved"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        wall_objs = [
            obj
            for obj in tool.Blender.get_selected_objects()
            if (element := tool.Ifc.get_entity(obj)) and tool.Parametric.is_path_connectable_wall(element)
        ]
        if wall_objs:
            core.regenerate_wall_to_underside(tool.Ifc, tool.Geometry, tool.Model, wall_objs)
        else:
            self.report({"ERROR"}, "Please select at least one LAYER2 element")


class ExtendWallsToWall(_CommitWallDraftsFirstMixin, bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.extend_walls_to_wall"
    bl_label = "Extend Walls To Wall"
    bl_description = "Extend and trim selected walls to another wall"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if _poll_reject_array_children(cls):
            return False
        return True

    def _perform(self, context):
        target_obj = None
        objs = []
        if (
            (obj := tool.Blender.get_active_object(is_selected=True))
            and (element := tool.Ifc.get_entity(obj))
            and tool.Model.get_usage_type(element) == "LAYER2"
        ):
            target_obj = obj
        for obj in tool.Blender.get_selected_objects(include_active=False):
            if (
                obj != target_obj
                and (element := tool.Ifc.get_entity(obj))
                and tool.Model.get_usage_type(element) == "LAYER2"
            ):
                objs.append(obj)
        if target_obj and objs:
            if tool.Ifc.is_moved(target_obj):
                bonsai.core.geometry.edit_object_placement(tool.Ifc, tool.Geometry, tool.Surveyor, obj=target_obj)
            joiner = DumbWallJoiner()
            target_element = tool.Ifc.get_entity(target_obj)
            for obj in objs:
                if tool.Ifc.is_moved(obj):
                    bonsai.core.geometry.edit_object_placement(tool.Ifc, tool.Geometry, tool.Surveyor, obj=obj)
                element = tool.Ifc.get_entity(obj)
                ifcopenshell.api.geometry.connect_wall(
                    tool.Ifc.get(), wall1=element, wall2=target_element, is_atpath=True
                )
                tool.Model.recreate_wall(element, obj)
            tool.Model.recreate_wall(target_element, target_obj)
            _resync_walls_after_mutation([target_obj, *objs])
        else:
            self.report({"ERROR"}, "Please select at least one LAYER2 element and one active LAYER2 element")


class ExtendWallsToPolylinePoint(bpy.types.Operator, PolylineOperator, tool.Ifc.Operator):
    bl_idname = "bim.extend_walls_to_polyline_point"
    bl_label = "Extend Walls To Polyline Point"
    bl_description = "Extend and trim selected walls to another wall"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if not (space := context.space_data) or space.type != "VIEW_3D":
            return False
        for obj in context.selected_objects:
            if not (element := tool.Ifc.get_entity(obj)) or not element.is_a("IfcWall"):
                return False
        return bool(context.selected_objects)

    def __init__(self):
        super().__init__()
        self.connection = "ATEND"

    def set_origin(self, context, event, connection="ATSTART"):
        obj = context.active_object
        ref = tool.Wall.get_world_reference_line(obj)
        if ref is None:
            return
        start = Vector((ref[0].x, ref[0].y, obj.location.z))
        end = Vector((ref[1].x, ref[1].y, obj.location.z))
        direcion = end - start
        value = end if connection == "ATSTART" else start
        self.input_ui.set_value("X", value[0])
        self.input_ui.set_value("Y", value[1])
        self.input_ui.set_value("Z", value[2])
        result = tool.Polyline.insert_polyline_point(self.input_ui, self.tool_state)
        PolylineDecorator.update(event, self.tool_state, self.input_ui, self.snapping_points[0])
        tool.Blender.update_viewport()
        # Point related to the mouse
        polyline_props = tool.Model.get_polyline_props()
        snap_prop = polyline_props.snap_mouse_point[0]
        mouse_point = Vector((snap_prop.x, snap_prop.y, snap_prop.z))

        angle = atan2(direcion.y, direcion.x)

        self.tool_state.lock_axis = True
        self.tool_state.snap_angle = degrees(angle)

    def modal(self, context, event):
        return IfcStore.execute_ifc_operator(self, context, event, method="MODAL")

    def _modal(self, context, event):
        PolylineDecorator.update(event, self.tool_state, self.input_ui, self.snapping_points[0])
        tool.Blender.update_viewport()
        self.handle_lock_axis(context, event)  # Must come before "PASS_THROUGH"
        self.handle_mouse_move(context, event)

        if event.type in {"MIDDLEMOUSE", "WHEELUPMOUSE", "WHEELDOWNMOUSE"}:
            self.handle_mouse_move(context, event)
            return {"PASS_THROUGH"}

        custom_instructions = {
            "Cycle Input": {"icons": True, "keys": ["EVENT_TAB"]},
            "Distance Input": {"icons": True, "keys": ["EVENT_D"]},
            "Flip starting point": {"icons": True, "keys": ["EVENT_F"]},
            "Confirm": {"icons": True, "keys": ["MOUSE_LMB"]},
            "Cancel": {"icons": True, "keys": ["MOUSE_RMB", "EVENT_ESC"]},
        }
        custom_info = []
        self.handle_instructions(context, custom_instructions, custom_info, overwrite=True)
        self.handle_mouse_move(context, event, should_round=True)
        self.choose_axis(event)
        self.handle_snap_selection(context, event)

        if event.value == "RELEASE" and event.type == "F":
            tool.Polyline.clear_polyline()
            self.connection = "ATSTART" if self.connection == "ATEND" else "ATEND"
            self.set_origin(context, event, self.connection)

        if event.value == "RELEASE" and event.type in {"RET", "NUMPAD_ENTER", "RIGHTMOUSE", "LEFTMOUSE"}:
            if self.tool_state.is_input_on:
                is_valid = self.recalculate_inputs(context)
                if is_valid:
                    result = tool.Polyline.insert_polyline_point(self.input_ui, self.tool_state)
                    if result:
                        self.report({"WARNING"}, result)
            else:
                result = tool.Polyline.insert_polyline_point(self.input_ui, self.tool_state)
                if result:
                    self.report({"WARNING"}, result)

            polyline_props = tool.Model.get_polyline_props()
            snap_prop = polyline_props.snap_mouse_point[0]
            snap_obj = bpy.data.objects.get(snap_prop.snap_object)
            if snap_obj and tool.Ifc.get_entity(snap_obj).is_a("IfcWall"):
                tool.Blender.set_active_object(snap_obj)
                ExtendWallsToWall._execute(self, context)
            else:
                point = polyline_props.insertion_polyline[0].polyline_points[1]
                core.extend_walls(
                    tool.Ifc,
                    tool.Blender,
                    tool.Geometry,
                    DumbWallJoiner(),
                    tool.Model,
                    Vector((point.x, point.y, point.z)),
                    self.connection,
                )

            tool.Polyline.clear_polyline()
            context.workspace.status_text_set(text=None)
            PolylineDecorator.uninstall()
            tool.Blender.update_viewport()
            return {"FINISHED"}

        self.handle_keyboard_input(context, event)

        cancel = self.handle_cancelation(context, event)
        if cancel is not None:
            return cancel

        return {"RUNNING_MODAL"}

    def invoke(self, context, event):
        super().invoke(context, event)
        self.set_origin(context, event, self.connection)
        self.tool_state.use_default_container = True
        self.tool_state.plane_method = "XY"
        # Update snaps after changing plane_method
        detected_snaps = tool.Snap.detect_snapping_points(context, event, self.objs_2d_bbox, self.tool_state)
        self.snapping_points = tool.Snap.select_snapping_points(context, event, self.tool_state, detected_snaps)
        tool.Polyline.calculate_distance_and_angle(context, self.input_ui, self.tool_state)
        tool.Blender.update_viewport()
        return {"RUNNING_MODAL"}


class AlignWall(bpy.types.Operator):
    bl_idname = "bim.align_wall"
    bl_label = "Align Wall"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = """ Align the selected walls to the active wall:
    'Ext.': align to the EXTERIOR face
    'C/L': align to wall CENTER
    'Int.': align to the INTERIOR face"""

    AlignType = Literal["CENTER", "EXTERIOR", "INTERIOR"]
    align_type: bpy.props.EnumProperty(  # pyright: ignore [reportRedeclaration]
        items=((i, i, "") for i in get_args(AlignType))
    )

    if TYPE_CHECKING:
        align_type: AlignType

    def execute(self, context):
        try:
            core.align_walls(tool.Ifc, tool.Blender, tool.Model, DumbWallAligner(), self.align_type)
        except core.RequireAtLeastTwoLayeredElements as e:
            self.report({"ERROR"}, str(e))
        return {"FINISHED"}


class FlipWall(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.flip_wall"
    bl_label = "Flip Wall"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Switch the origin from the min XY corner to the max XY corner, and rotates the origin by 180"

    @classmethod
    def poll(cls, context):
        if not tool.Model.has_selected_ifc_objects():
            cls.poll_message_set("No IFC objects selected.")
            return False
        return True

    def _execute(self, context):
        selected_objs = tool.Model.get_selected_mesh_objects()
        joiner = DumbWallJoiner()
        for obj in selected_objs:
            joiner.flip(obj)
        return {"FINISHED"}


class SplitWall(_CommitWallDraftsFirstMixin, bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.split_wall"
    bl_label = "Split Wall"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = (
        "Split selected wall into two walls in correspondence of Blender cursor. The cursor must be in the wall volume"
    )

    @classmethod
    def poll(cls, context):
        if not tool.Model.has_selected_ifc_objects():
            cls.poll_message_set("No IFC objects selected.")
            return False
        if _poll_reject_array_children(cls):
            return False
        return True

    def _perform(self, context):
        selected_objs = tool.Model.get_selected_mesh_objects()
        post_split_walls: list[bpy.types.Object] = []
        for obj in selected_objs:
            new_obj = DumbWallJoiner().split(obj, context.scene.cursor.location)
            post_split_walls.append(obj)
            if new_obj is not None and new_obj not in post_split_walls:
                post_split_walls.append(new_obj)
        _resync_walls_after_mutation(post_split_walls)
        _regenerate_walls(post_split_walls)
        return {"FINISHED"}


class MergeWall(_CommitWallDraftsFirstMixin, bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.merge_wall"
    bl_label = "Merge Wall"
    bl_description = "Merge selected walls into one object"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if not context.active_object:
            cls.poll_message_set("No active object selected.")
            return False
        elif not tool.Model.has_selected_ifc_objects():
            cls.poll_message_set("No mesh IFC objects selected.")
            return False
        mesh_objects = [o for o in tool.Model.get_selected_ifc_objects() if o.type == "MESH"]
        if len(mesh_objects) != 2:
            cls.poll_message_set("Please select exactly two mesh IFC objects.")
            return False
        if _poll_reject_array_children(cls):
            return False
        return True

    def _perform(self, context):
        active_obj = context.active_object
        assert active_obj
        selected_objs = tool.Model.get_selected_mesh_objects()
        # Active-is-survivor — matches Blender's Ctrl+J / "merge at last"
        # convention. The first argument survives, the second is consumed,
        # so the active wall ends up absorbing the other.
        other_obj = next(o for o in selected_objs if o != active_obj)
        DumbWallJoiner().merge(active_obj, other_obj)
        _maybe_resync_wall_props_from_ifc(active_obj)
        _regenerate_walls([active_obj])
        return {"FINISHED"}


class RecalculateWall(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.recalculate_wall"
    bl_label = "Recalculate Wall"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if not tool.Model.has_selected_mesh_ifc_objects():
            cls.poll_message_set("No mesh IFC objects selected.")
            return False
        return True

    def _execute(self, context):
        objects = tool.Model.get_selected_mesh_ifc_objects()
        tool.Model.recalculate_walls(objects)
        return {"FINISHED"}


class ChangeExtrusionDepth(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.change_extrusion_depth"
    bl_label = "Update"
    bl_description = "Update height for the selected objects."
    bl_options = {"REGISTER", "UNDO"}
    depth: bpy.props.FloatProperty()

    @classmethod
    def poll(cls, context):
        if not tool.Model.has_selected_mesh_ifc_objects():
            cls.poll_message_set("No mesh IFC objects selected.")
            return False
        return True

    def _execute(self, context):
        layer2_objs: list[bpy.types.Object] = []
        ifc_file = tool.Ifc.get()
        si_conversion = ifcopenshell.util.unit.calculate_unit_scale(ifc_file)
        selected_objs = tool.Model.get_selected_mesh_ifc_objects()

        for obj in selected_objs:
            element = tool.Ifc.get_entity(obj)
            assert element

            representation = ifcopenshell.util.representation.get_representation(element, "Model", "Body", "MODEL_VIEW")
            if not representation:
                continue
            extrusion = tool.Model.get_extrusion(representation)
            if not extrusion:
                continue
            x, y, z = extrusion.ExtrudedDirection.DirectionRatios
            x_angle = Vector((0, 1)).angle_signed(Vector((y, z)))
            extrusion.Depth = self.depth / si_conversion * (1 / cos(x_angle))
            if tool.Model.get_usage_type(element) == "LAYER2":
                for rel in element.ConnectedFrom:
                    if rel.is_a() == "IfcRelConnectsElements":
                        ifcopenshell.api.geometry.disconnect_element(
                            ifc_file,
                            relating_element=rel.RelatingElement,
                            related_element=element,
                        )
                layer2_objs.append(obj)

        if layer2_objs:
            tool.Model.recalculate_walls(layer2_objs)
            _resync_walls_after_mutation(layer2_objs)
        return {"FINISHED"}


class ChangeExtrusionXAngle(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.change_extrusion_x_angle"
    bl_label = "Update"
    bl_description = "Update angle for the selected objects."
    bl_options = {"REGISTER", "UNDO"}
    x_angle: bpy.props.FloatProperty(name="X Angle", default=0, subtype="ANGLE")

    @classmethod
    def poll(cls, context):
        if not tool.Model.has_selected_mesh_ifc_objects():
            cls.poll_message_set("No mesh IFC objects selected.")
            return False
        return True

    def _execute(self, context):
        layer2_objs: list[bpy.types.Object] = []
        x_angle = 0 if tool.Cad.is_x(self.x_angle, 0, tolerance=0.001) else self.x_angle
        x_angle = 0 if tool.Cad.is_x(self.x_angle, pi, tolerance=0.001) else self.x_angle
        unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
        selected_objs = tool.Model.get_selected_mesh_ifc_objects()
        builder = ifcopenshell.util.shape_builder.ShapeBuilder(tool.Ifc.get())

        for obj in selected_objs:
            element = tool.Ifc.get_entity(obj)
            assert element
            representation = ifcopenshell.util.representation.get_representation(element, "Model", "Body", "MODEL_VIEW")
            if not representation:
                continue
            extrusion = tool.Model.get_extrusion(representation)
            if not extrusion:
                continue
            existing_x_angle = tool.Model.get_existing_x_angle(extrusion)
            existing_x_angle = 0 if tool.Cad.is_x(existing_x_angle, 0, tolerance=0.001) else existing_x_angle
            existing_x_angle = 0 if tool.Cad.is_x(existing_x_angle, pi, tolerance=0.001) else existing_x_angle
            if tool.Model.get_usage_type(element) == "LAYER2":
                x, y, z = extrusion.ExtrudedDirection.DirectionRatios
                depth = core.vertical_height_from_extrusion_depth(extrusion.Depth, existing_x_angle)
                perpendicular_depth = depth * abs(1 / cos(x_angle))
                extrusion.ExtrudedDirection.DirectionRatios = (0.0, sin(x_angle), cos(x_angle))
                layer2_objs.append(obj)
                extrusion.Depth = perpendicular_depth
            else:
                if tool.Model.get_usage_type(element) == "LAYER3":
                    existing_x_angle = tool.Model.get_existing_x_angle(extrusion)
                    existing_x_angle = 0 if tool.Cad.is_x(existing_x_angle, 0, tolerance=0.001) else existing_x_angle
                    existing_x_angle = 0 if tool.Cad.is_x(existing_x_angle, pi, tolerance=0.001) else existing_x_angle

                    profiles = (
                        extrusion.SweptArea.Profiles
                        if extrusion.SweptArea.is_a("IfcCompositeProfileDef")
                        else [extrusion.SweptArea]
                    )
                    for profile in profiles:
                        coord_list = builder.get_polyline_coords(profile.OuterCurve)
                        coord_list = [
                            (p[0], p[1] * abs(cos(existing_x_angle))) for p in coord_list
                        ]  # Reset the transformation and returns to the original points with 0 degrees
                        coord_list = [
                            (p[0], p[1] * abs(1 / cos(x_angle))) for p in coord_list
                        ]  # Apply the transformation for the new x_angle
                        builder.set_polyline_coords(profile.OuterCurve, coord_list)

                    # The extrusion direction calculated previously default to the positive direction
                    # Here we set the extrusion direction to negative if that's the case
                    direction_ratios = Vector((0.0, sin(x_angle), cos(x_angle)))
                    # direction_ratios = Vector(extrusion.ExtrudedDirection.DirectionRatios)
                    layer_params = tool.Model.get_material_layer_parameters(element)
                    perpendicular_depth = layer_params["thickness"] * abs(1 / cos(x_angle)) / unit_scale
                    perpendicular_offset = layer_params["offset"] * abs(1 / cos(x_angle)) / unit_scale
                    offset_direction = direction_ratios.copy()

                    # Check angle and z direction to determine whether the extrusion direction is positive or negative
                    if (abs(x_angle) < (pi / 2) and direction_ratios.z > 0) or (
                        abs(x_angle) > (pi / 2) and direction_ratios.z < 0
                    ):
                        # The extrusion direction is positive. If the layer_parameter is set to negative,
                        # then the we change the extrusion direction.
                        if layer_params["direction_sense"] == "NEGATIVE":
                            direction_ratios *= -1
                    elif ((x_angle) > (pi / 2) and direction_ratios.z > 0) or (
                        (x_angle) < (pi / 2) and direction_ratios.z < 0
                    ):
                        # The extrusion direction is negative. If the layer_parameter is set to positive,
                        # then the we change the extrusion direction.
                        # then the we change the extrusion direction. And the offset direction should remain positive
                        # for either direction sense, so we change it.
                        offset_direction *= -1
                        if layer_params["direction_sense"] == "POSITIVE":
                            direction_ratios *= -1

                    extrusion.ExtrudedDirection.DirectionRatios = tuple(direction_ratios)
                    extrusion.Depth = perpendicular_depth

                    if extrusion.Position or perpendicular_offset != 0:
                        position = offset_direction * perpendicular_offset
                        tool.Model.add_extrusion_position(extrusion, position)

                bonsai.core.geometry.switch_representation(
                    tool.Ifc,
                    tool.Geometry,
                    obj=obj,
                    representation=representation,
                )

                # Object rotation
                current_z_rot = obj.rotation_euler.z
                rot_mat = mathutils.Matrix.Rotation(x_angle, 4, "X")
                obj.rotation_euler = rot_mat.to_euler()
                obj.rotation_euler.z = current_z_rot

        if layer2_objs:
            tool.Model.recalculate_walls(layer2_objs)
            _resync_walls_after_mutation(layer2_objs)
        return {"FINISHED"}


class ChangeLayerLength(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.change_layer_length"
    bl_label = "Update"
    bl_description = "Update length for the selected objects."
    bl_options = {"REGISTER", "UNDO"}
    length: bpy.props.FloatProperty()

    @classmethod
    def poll(cls, context):
        if not tool.Model.has_selected_mesh_ifc_objects():
            cls.poll_message_set("No mesh IFC objects selected.")
            return False
        return True

    def _execute(self, context):
        joiner = DumbWallJoiner()
        selected_objs = tool.Model.get_selected_mesh_ifc_objects()
        for obj in selected_objs:
            joiner.set_length(obj, self.length)
        _resync_walls_after_mutation(selected_objs)


class OffsetWalls(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.offset_walls"
    bl_label = "Offset Walls"
    bl_description = "Offset selected objects from their reference line."
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if not tool.Model.has_selected_mesh_ifc_objects():
            cls.poll_message_set("No mesh IFC objects selected.")
            return False
        return True

    def _execute(self, context):
        props = tool.Model.get_model_props()
        core.offset_walls(tool.Ifc, tool.Blender, tool.Model, props.offset_type_vertical)


class AddWallsFromSlab(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.draw_walls_from_slab"
    bl_label = "Draw Slab From Wall"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.space_data.type == "VIEW_3D"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.relating_type = None
        props = tool.Model.get_model_props()
        relating_type_id = props.relating_type_id
        if relating_type_id:
            self.relating_type = tool.Ifc.get().by_id(int(relating_type_id))

    def _execute(self, context):
        if not self.relating_type:
            return {"FINISHED"}
        slab = tool.Ifc.get_entity(context.active_object)
        if not slab.is_a("IfcSlab"):
            self.report(
                {"WARNING"},
                "Please select a slab.",
            )
            return {"FINISHED"}
        walls = DumbWallGenerator(self.relating_type).generate("SLAB")

        if walls:
            for wall1, wall2 in zip(walls, walls[1:] + [walls[0]]):
                DumbWallJoiner().connect(wall2["obj"], wall1["obj"])


class DrawPolylineWall(bpy.types.Operator, PolylineOperator, tool.Ifc.Operator):
    bl_idname = "bim.draw_polyline_wall"
    bl_label = "Draw Polyline Wall"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.space_data.type == "VIEW_3D"

    def __init__(self, *args, **kwargs):
        bpy.types.Operator.__init__(self, *args, **kwargs)
        PolylineOperator.__init__(self)
        self.relating_type = None
        props = tool.Model.get_model_props()
        relating_type_id = props.relating_type_id
        if relating_type_id:
            self.relating_type = tool.Ifc.get().by_id(int(relating_type_id))

    def create_walls_from_polyline(self, context: bpy.types.Context) -> Union[set[str], None]:
        if not self.relating_type:
            return {"FINISHED"}

        model_props = tool.Model.get_model_props()
        direction_sense = model_props.direction_sense
        offset = model_props.offset

        walls, is_polyline_closed = DumbWallGenerator(self.relating_type).generate("POLYLINE")
        for wall in walls:
            model = tool.Ifc.get()
            element = tool.Ifc.get_entity(wall["obj"])
            material = ifcopenshell.util.element.get_material(element)
            material_set_usage = model.by_id(material.id())
            # if material.is_a("IfcMaterialLayerSetUsage"):
            attributes = {"OffsetFromReferenceLine": offset, "DirectionSense": direction_sense}
            ifcopenshell.api.material.edit_layer_usage(model, usage=material_set_usage, attributes=attributes)
            tool.Model.recalculate_walls([wall["obj"]])

        if walls:
            if is_polyline_closed:
                for wall1, wall2 in zip(walls, walls[1:] + [walls[0]]):
                    DumbWallJoiner().connect(wall2["obj"], wall1["obj"])
            else:
                for wall1, wall2 in zip(walls[:-1], walls[1:]):
                    DumbWallJoiner().connect(wall2["obj"], wall1["obj"])

    def modal(self, context, event):
        return IfcStore.execute_ifc_operator(self, context, event, method="MODAL")

    def _modal(self, context, event):
        if not self.relating_type:
            self.report({"WARNING"}, "You need to select a wall type.")
            PolylineDecorator.uninstall()
            tool.Blender.update_viewport()
            return {"FINISHED"}

        PolylineDecorator.update(event, self.tool_state, self.input_ui, self.snapping_points[0])
        tool.Blender.update_viewport()

        self.handle_lock_axis(context, event)  # Must come before "PASS_TRHOUGH"

        if event.type in {"MIDDLEMOUSE", "WHEELUPMOUSE", "WHEELDOWNMOUSE"}:
            self.handle_mouse_move(context, event)
            return {"PASS_THROUGH"}

        props = tool.Model.get_model_props()
        # Wall axis settings
        if event.value == "RELEASE" and event.type == "F":
            direction_sense = props.direction_sense
            props.direction_sense = "NEGATIVE" if direction_sense == "POSITIVE" else "POSITIVE"
            self.set_offset(context, self.relating_type)

        if event.value == "RELEASE" and event.type == "O":
            items = ("EXTERIOR", "CENTER", "INTERIOR")
            index = items.index(props.offset_type_vertical)
            size = len(items)
            props.offset_type_vertical = items[((index + 1) % size)]
            self.set_offset(context, self.relating_type)

        custom_instructions = {"Choose Axis": {"icons": True, "keys": ["EVENT_X", "EVENT_Y"]}}

        wall_config = [
            f"Direction: {props.direction_sense}",
            f"Offset Type: {props.offset_type_vertical}",
            f"Offset Value: {tool.Polyline.format_input_ui_units(props.offset * self.unit_scale)}",
        ]

        self.handle_instructions(context, custom_instructions, wall_config)

        self.handle_mouse_move(context, event, should_round=True)

        self.choose_axis(event)

        self.handle_snap_selection(context, event)

        if (
            not self.tool_state.is_input_on
            and event.value == "RELEASE"
            and event.type in {"RET", "NUMPAD_ENTER", "RIGHTMOUSE"}
        ):
            self.create_walls_from_polyline(context)
            context.workspace.status_text_set(text=None)
            self.tool_state.plane_method = None
            ProductDecorator.uninstall()
            PolylineDecorator.uninstall()
            tool.Polyline.clear_polyline()
            tool.Blender.update_viewport()
            return {"FINISHED"}

        self.handle_keyboard_input(context, event)
        self.handle_inserting_polyline(context, event)

        cancel = self.handle_cancelation(context, event)
        if cancel is not None:
            ProductDecorator.uninstall()
            return cancel

        return {"RUNNING_MODAL"}

    def invoke(self, context, event):
        return IfcStore.execute_ifc_operator(self, context, event, method="INVOKE")

    def _invoke(self, context, event):
        super().invoke(context, event)
        ProductDecorator.install(context)
        self.tool_state.use_default_container = True
        self.tool_state.plane_method = "XY"
        self.set_offset(context, self.relating_type)
        return {"RUNNING_MODAL"}


class DumbWallAligner:
    # An alignment shifts the origin of all walls to the closest point on the
    # local X axis of the reference wall. In addition, the Z rotation is copied.
    # Z translations are ignored for alignment.
    def set_reference_wall(self, reference_wall: bpy.types.Object):
        self.reference_wall = reference_wall

    def align_centerline(self, wall: bpy.types.Object) -> None:
        self.wall = wall
        self.align_rotation()

        l_start = Vector(self.reference_wall.bound_box[0]).lerp(Vector(self.reference_wall.bound_box[3]), 0.5)
        l_end = Vector(self.reference_wall.bound_box[4]).lerp(Vector(self.reference_wall.bound_box[7]), 0.5)

        start = self.reference_wall.matrix_world @ l_start
        end = self.reference_wall.matrix_world @ l_end

        l_snap_point = Vector(self.wall.bound_box[0]).lerp(Vector(self.wall.bound_box[3]), 0.5)
        snap_point = self.wall.matrix_world @ l_snap_point
        offset = snap_point - self.wall.matrix_world.translation

        point, _ = mathutils.geometry.intersect_point_line(snap_point, start, end)

        new_origin = point - offset
        self.wall.matrix_world.translation[0], self.wall.matrix_world.translation[1] = new_origin.xy

    def align_last_layer(self, wall: bpy.types.Object) -> None:
        self.wall = wall
        self.align_rotation()

        if self.is_rotation_flipped():
            element = tool.Ifc.get_entity(self.wall)
            if tool.Model.get_usage_type(element) == "LAYER2":
                DumbWallJoiner().flip(self.wall)
                bpy.context.view_layer.update()
                snap_point = self.wall.matrix_world @ Vector(self.wall.bound_box[3])
            else:
                snap_point = self.wall.matrix_world @ Vector(self.wall.bound_box[0])
        else:
            snap_point = self.wall.matrix_world @ Vector(self.wall.bound_box[3])

        start = self.reference_wall.matrix_world @ Vector(self.reference_wall.bound_box[3])
        end = self.reference_wall.matrix_world @ Vector(self.reference_wall.bound_box[7])

        point, _ = mathutils.geometry.intersect_point_line(snap_point, start, end)

        offset = snap_point - self.wall.matrix_world.translation
        new_origin = point - offset
        self.wall.matrix_world.translation[0], self.wall.matrix_world.translation[1] = new_origin.xy

    def align_first_layer(self, wall: bpy.types.Object) -> None:
        self.wall = wall
        self.align_rotation()

        if self.is_rotation_flipped():
            element = tool.Ifc.get_entity(self.wall)
            if tool.Model.get_usage_type(element) == "LAYER2":
                DumbWallJoiner().flip(self.wall)
                bpy.context.view_layer.update()
                snap_point = self.wall.matrix_world @ Vector(self.wall.bound_box[0])
            else:
                snap_point = self.wall.matrix_world @ Vector(self.wall.bound_box[3])
        else:
            snap_point = self.wall.matrix_world @ Vector(self.wall.bound_box[0])

        start = self.reference_wall.matrix_world @ Vector(self.reference_wall.bound_box[0])
        end = self.reference_wall.matrix_world @ Vector(self.reference_wall.bound_box[4])

        point, _ = mathutils.geometry.intersect_point_line(snap_point, start, end)

        offset = snap_point - self.wall.matrix_world.translation
        new_origin = point - offset
        self.wall.matrix_world.translation[0], self.wall.matrix_world.translation[1] = new_origin.xy

    def align_rotation(self) -> None:
        reference = (self.reference_wall.matrix_world.to_quaternion() @ Vector((1, 0, 0))).to_2d()
        wall = (self.wall.matrix_world.to_quaternion() @ Vector((1, 0, 0))).to_2d()
        angle = reference.angle_signed(wall)
        if round(degrees(angle) % 360) in (0, 180):
            return
        elif angle > (pi / 2):
            self.wall.rotation_euler[2] -= pi - angle
        else:
            self.wall.rotation_euler[2] += angle
        bpy.context.view_layer.update()

    def is_rotation_flipped(self) -> bool:
        reference = (self.reference_wall.matrix_world.to_quaternion() @ Vector((1, 0, 0))).to_2d()
        wall = (self.wall.matrix_world.to_quaternion() @ Vector((1, 0, 0))).to_2d()
        angle = reference.angle_signed(wall)
        return round(degrees(angle) % 360) == 180


class DumbWallGenerator:
    def __init__(self, relating_type):
        self.relating_type = relating_type
        self.unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())

    def generate(self, insertion_type="CURSOR"):
        self.file = tool.Ifc.get()
        self.layers = tool.Model.get_material_layer_parameters(self.relating_type)
        if not self.layers["thickness"]:
            return

        self.body_context = ifcopenshell.util.representation.get_context(tool.Ifc.get(), "Model", "Body", "MODEL_VIEW")
        self.axis_context = ifcopenshell.util.representation.get_context(tool.Ifc.get(), "Plan", "Axis", "GRAPH_VIEW")

        props = tool.Model.get_model_props()

        self.container = None
        self.container_obj = None
        if container := tool.Root.get_default_container():
            self.container = container
            self.container_obj = tool.Ifc.get_object(container)

        self.width = self.layers["thickness"]
        self.height = props.extrusion_depth
        self.length = props.length
        self.rotation = 0.0
        self.location = Vector((0, 0, 0))
        self.x_angle = 0 if tool.Cad.is_x(props.x_angle, 0, tolerance=0.001) else props.x_angle

        if insertion_type == "POLYLINE":
            return self.derive_from_polyline()
        elif insertion_type == "SLAB":
            return self.derive_from_slab()
        elif insertion_type == "CURSOR":
            return self.derive_from_cursor()

    def derive_from_polyline(self) -> tuple[list[Union[dict[str, Any], None]], bool]:
        polyline_props = tool.Model.get_polyline_props()
        polyline_data = polyline_props.insertion_polyline
        polyline_points = polyline_data[0].polyline_points if polyline_data else []
        is_polyline_closed = False
        if len(polyline_points) > 3:
            first_vec = Vector((polyline_points[0].x, polyline_points[0].y, polyline_points[0].z))
            last_vec = Vector((polyline_points[-1].x, polyline_points[-1].y, polyline_points[-1].z))
            if first_vec == last_vec:
                is_polyline_closed = True

        walls = []
        for i in range(len(polyline_points) - 1):
            vec1 = Vector((polyline_points[i].x, polyline_points[i].y, polyline_points[i].z))
            vec2 = Vector((polyline_points[i + 1].x, polyline_points[i + 1].y, polyline_points[i + 1].z))
            coords = (vec1, vec2)
            walls.append(self.create_wall_from_2_points(coords))
        return walls, is_polyline_closed

    def derive_from_slab(self):
        slab_obj = bpy.context.active_object
        slab = tool.Ifc.get_entity(slab_obj)
        container = ifcopenshell.util.element.get_container(slab)
        self.container_obj = tool.Ifc.get_object(container)
        elevation = self.container_obj.location.z
        representation = ifcopenshell.util.representation.get_representation(slab, "Model", "Body", "MODEL_VIEW")
        extrusion = tool.Model.get_extrusion(representation)
        builder = ifcopenshell.util.shape_builder.ShapeBuilder(tool.Ifc.get())
        polyline_points = builder.get_polyline_coords(extrusion.SweptArea.OuterCurve)
        polyline_points = [[(v * self.unit_scale) for v in p] for p in polyline_points]
        polyline_points = [slab_obj.matrix_world @ Vector((p[0], p[1], elevation)) for p in polyline_points]
        if not tool.Cad.is_counter_clockwise_order(polyline_points[0], polyline_points[1], polyline_points[2]):
            polyline_points = polyline_points[::-1]
        walls = []
        for i in range(len(polyline_points) - 1):
            vec1 = polyline_points[i]
            vec2 = polyline_points[i + 1]
            coords = (vec1, vec2)
            walls.append(self.create_wall_from_2_points(coords))
        return walls

    def create_wall_from_2_points(self, coords, should_round=False) -> Union[dict[str, Any], None]:
        direction = coords[1] - coords[0]
        length = direction.length
        data = {"coords": coords}

        self.length = length
        self.rotation = math.atan2(direction[1], direction[0])
        if should_round:
            # Round to nearest 50mm (yes, metric for now)
            self.length = 0.05 * round(length / 0.05)
            angle_snap = tool.Snap.get_angle_snap_value(bpy.context)
            nearest_degree = math.radians(angle_snap)
            self.rotation = nearest_degree * round(self.rotation / nearest_degree)
        self.location = coords[0]
        data["obj"] = self.create_wall()
        return data

    def derive_from_cursor(self) -> bpy.types.Object:
        RAYCAST_PRECISION = 0.01
        self.location = bpy.context.scene.cursor.location
        if self.container:
            for subelement in ifcopenshell.util.element.get_decomposition(self.container):
                if not subelement.is_a("IfcWall"):
                    continue
                sibling_obj = tool.Ifc.get_object(subelement)
                if not sibling_obj or not isinstance(sibling_obj.data, bpy.types.Mesh):
                    continue
                inv_obj_matrix = sibling_obj.matrix_world.inverted()
                local_location = inv_obj_matrix @ self.location
                try:
                    raycast = sibling_obj.closest_point_on_mesh(local_location, distance=RAYCAST_PRECISION)
                except:
                    # If the mesh has no faces
                    raycast = [None]
                if not raycast[0]:
                    continue
                for face in sibling_obj.data.polygons:
                    normal = (sibling_obj.matrix_world.to_quaternion() @ face.normal).normalized()
                    face_center = sibling_obj.matrix_world @ face.center
                    if (
                        normal.z != 0
                        or abs(mathutils.geometry.distance_point_to_plane(self.location, face_center, normal)) > 0.01
                    ):
                        continue

                    rotation = math.atan2(normal[1], normal[0])
                    rotated_y_axis = Matrix.Rotation(-rotation, 4, "Z")[1].xyz

                    # since wall thickness goes by local Y+ axis
                    # we find best position for the next wall
                    # by finding the face of another wall that will be very close to the some test point.
                    # test point is calculated by applying to cursor position some little offset along the face
                    #
                    # a bit different offset to be safe on raycast
                    test_pos = self.location + rotated_y_axis * RAYCAST_PRECISION * 1.1
                    test_pos_local = inv_obj_matrix @ test_pos
                    raycast = sibling_obj.closest_point_on_mesh(test_pos_local, distance=RAYCAST_PRECISION)

                    if not raycast[0]:
                        continue
                    self.rotation = rotation
                    break

                if self.rotation != 0:
                    break
        return self.create_wall()

    def create_wall(self) -> bpy.types.Object:
        props = tool.Model.get_model_props()
        ifc_class = self.get_relating_type_class(self.relating_type)
        mesh = bpy.data.meshes.new("Dummy")
        obj = bpy.data.objects.new(tool.Model.generate_occurrence_name(self.relating_type, ifc_class), mesh)

        matrix_world = Matrix.Rotation(self.rotation, 4, "Z")
        matrix_world.translation = self.location
        if self.container_obj:
            matrix_world.translation.z = self.container_obj.location.z + props.rl1
        obj.matrix_world = matrix_world
        bpy.context.view_layer.update()

        element = bonsai.core.root.assign_class(
            tool.Ifc,
            tool.Collector,
            tool.Root,
            obj=obj,
            ifc_class=ifc_class,
            should_add_representation=False,
        )
        ifcopenshell.api.type.assign_type(self.file, related_objects=[element], relating_type=self.relating_type)
        if self.axis_context:
            representation = ifcopenshell.api.geometry.add_axis_representation(
                tool.Ifc.get(),
                context=self.axis_context,
                axis=[(0.0, 0.0), (self.length, 0.0)],
            )
            ifcopenshell.api.geometry.assign_representation(
                tool.Ifc.get(), product=element, representation=representation
            )
        bonsai.core.geometry.edit_object_placement(tool.Ifc, tool.Geometry, tool.Surveyor, obj=obj)
        representation = ifcopenshell.api.geometry.add_wall_representation(
            tool.Ifc.get(),
            context=self.body_context,
            thickness=self.layers["thickness"],
            direction_sense=self.layers["direction_sense"],
            offset=self.layers["offset"],
            length=self.length,
            height=self.height,
            x_angle=self.x_angle,
        )
        ifcopenshell.api.geometry.assign_representation(tool.Ifc.get(), product=element, representation=representation)
        bonsai.core.geometry.switch_representation(
            tool.Ifc,
            tool.Geometry,
            obj=obj,
            representation=representation,
        )
        pset = ifcopenshell.api.pset.add_pset(self.file, product=element, name="EPset_Parametric")
        ifcopenshell.api.pset.edit_pset(self.file, pset=pset, properties={"Engine": "Bonsai.DumbLayer2"})
        material = ifcopenshell.util.element.get_material(element)
        material.LayerSetDirection = "AXIS2"
        tool.Blender.select_object(obj)
        return obj

    def get_relating_type_class(self, relating_type: ifcopenshell.entity_instance) -> str:
        classes = ifcopenshell.util.type.get_applicable_entities(relating_type.is_a(), tool.Ifc.get().schema)
        return next(c for c in classes if "StandardCase" not in c)


class DumbWallPlaner:
    def regenerate_from_layer(self, layer: ifcopenshell.entity_instance) -> None:
        for layer_set in layer.ToMaterialLayerSet:
            self.regenerate_from_layer_set(layer_set)

    def regenerate_from_layer_set(self, layer_set: ifcopenshell.entity_instance) -> None:
        walls = []
        total_thickness = sum([l.LayerThickness for l in layer_set.MaterialLayers])
        if not total_thickness:
            return
        for inverse in tool.Ifc.get().get_inverse(layer_set):
            if not inverse.is_a("IfcMaterialLayerSetUsage") or inverse.LayerSetDirection != "AXIS2":
                continue
            if tool.Ifc.get().schema == "IFC2X3":
                for rel in tool.Ifc.get().get_inverse(inverse):
                    if not rel.is_a("IfcRelAssociatesMaterial"):
                        continue
                    walls.extend([tool.Ifc.get_object(e) for e in rel.RelatedObjects])
            else:
                for rel in inverse.AssociatedTo:
                    walls.extend([tool.Ifc.get_object(e) for e in rel.RelatedObjects])
        tool.Model.recalculate_walls([w for w in set(walls) if w])


def _opening_axis_extent(opening, axis_reference, unit_scale):
    """Return ``(min_t, max_t)``: the opening's world-space footprint
    projected onto ``axis_reference`` as parametric positions along the
    wall axis (``0`` is the start of the axis line, ``1`` is its end).
    Used to detect openings whose footprint straddles a cut.

    Computed via ``ifcopenshell.geom.create_shape`` so the result is
    correct for any representation type Bonsai may produce — mapped
    representations, swept-area solids, breps, boolean clips, etc. —
    without needing a Blender object (Bonsai hides openings after
    ``bim.add_opening``). Falls back to a degenerate single-point range
    at the placement origin only when the geometry kernel cannot build
    a shape from the opening."""
    verts = None
    shape_matrix: Optional[Matrix] = None
    try:
        settings = ifcopenshell.geom.settings()
        shape = ifcopenshell.geom.create_shape(settings, opening)
        verts = ifcopenshell.util.shape.get_vertices(shape.geometry)
        shape_matrix = Matrix(ifcopenshell.util.shape.get_shape_matrix(shape).tolist())
    except Exception:
        verts = None
        shape_matrix = None

    if verts is None or shape_matrix is None or len(verts) == 0:
        placement = Matrix(ifcopenshell.util.placement.get_local_placement(opening.ObjectPlacement).tolist())
        placement.translation *= unit_scale
        _, t = mathutils.geometry.intersect_point_line(placement.translation.to_2d(), *axis_reference)
        return t, t

    positions = []
    for v in verts:
        world = (shape_matrix @ Vector((float(v[0]), float(v[1]), float(v[2])))).to_2d()
        _, t = mathutils.geometry.intersect_point_line(world, *axis_reference)
        positions.append(t)
    return min(positions), max(positions)


def _add_void_copy(building_element, source_opening):
    """Add an unfilled IfcOpeningElement to ``building_element`` whose
    geometry and placement mirror ``source_opening``. Used when a filled
    opening's void straddles a wall split — the filling stays on its wall,
    but the void must also apply to the neighbour so its body gets cut."""
    void_copy = ifcopenshell.api.root.copy_class(tool.Ifc.get(), product=source_opening)
    for fill_rel in list(void_copy.HasFillings or ()):
        tool.Ifc.get().remove(fill_rel)
    void_copy.VoidsElements[0].RelatingBuildingElement = building_element
    if void_copy.ObjectPlacement and void_copy.ObjectPlacement.is_a("IfcLocalPlacement"):
        if building_element.ObjectPlacement:
            void_copy.ObjectPlacement.PlacementRelTo = building_element.ObjectPlacement
    if source_opening.Representation:
        void_copy.Representation = ifcopenshell.util.element.copy_deep(
            tool.Ifc.get(), source_opening.Representation, exclude=["IfcGeometricRepresentationContext"]
        )


class DumbWallJoiner:
    def __init__(self):
        self.unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
        self.axis_context = ifcopenshell.util.representation.get_context(tool.Ifc.get(), "Plan", "Axis", "GRAPH_VIEW")
        self.body_context = ifcopenshell.util.representation.get_context(tool.Ifc.get(), "Model", "Body", "MODEL_VIEW")

    def unjoin(self, wall1):
        element1 = tool.Ifc.get_entity(wall1)
        if not element1:
            return

        ifcopenshell.api.geometry.disconnect_path(tool.Ifc.get(), element=element1, connection_type="ATSTART")
        ifcopenshell.api.geometry.disconnect_path(tool.Ifc.get(), element=element1, connection_type="ATEND")

        axis1 = tool.Model.get_wall_axis(wall1)
        axis = copy.deepcopy(axis1["reference"])
        body = copy.deepcopy(axis1["reference"])
        tool.Model.recreate_wall(element1, wall1)

    def split(self, wall1: bpy.types.Object, target: Vector) -> "bpy.types.Object | None":
        unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())

        element1 = tool.Ifc.get_entity(wall1)
        if not element1:
            return

        if tool.Ifc.is_moved(wall1):
            bonsai.core.geometry.edit_object_placement(tool.Ifc, tool.Geometry, tool.Surveyor, obj=wall1)

        ref = tool.Wall.get_world_reference_line(wall1)
        if ref is None:
            return
        axis_world_2d = (ref[0].to_2d(), ref[1].to_2d())
        intersect, cut_percentage = mathutils.geometry.intersect_point_line(target.to_2d(), *axis_world_2d)
        if cut_percentage < 0 or cut_percentage > 1 or tool.Cad.is_x(cut_percentage, (0, 1)):
            return

        wall2 = self.duplicate_wall(wall1)
        element2 = tool.Ifc.get_entity(wall2)

        # The duplicate inherits wall1's slab-trim boolean chain (copied by
        # copy_class) but ``BBIM_Boolean.Data`` carries wall1's stale ids, so
        # ``get_manual_booleans(element2)`` returns empty and the regenerator
        # rebuilds wall2's body without those clips. Strip them up front so
        # wall2 starts clean before the axis + placement reshape.
        tool.Model.strip_underside_booleans(element2)

        # Get the ATEND connection from wall1 to use it in wall2
        relating_element = None
        connections = element1.ConnectedTo
        for conn in connections:
            if conn.is_a("IfcRelConnectsPathElements") and conn.RelatingConnectionType == "ATEND":
                relating_element = conn.RelatedElement
                relating_connection = conn.RelatedConnectionType
                description = conn.Description
                bonsai.core.geometry.remove_connection(tool.Geometry, connection=conn)
        connections = element1.ConnectedFrom
        for conn in connections:
            if conn.is_a("IfcRelConnectsPathElements") and conn.RelatedConnectionType == "ATEND":
                relating_element = conn.RelatingElement
                relating_connection = conn.RelatingConnectionType
                description = conn.Description
                bonsai.core.geometry.remove_connection(tool.Geometry, connection=conn)
        if relating_element:
            ifcopenshell.api.geometry.connect_path(
                tool.Ifc.get(),
                relating_element=relating_element,
                related_element=element2,
                relating_connection=relating_connection,
                related_connection="ATEND",
                description=description,
            )

        # During the duplication process, unfilled voids are copied, so we need
        # to check openings on both element1 and element2. Each wall keeps the
        # opening when the opening's axis-projected extent overlaps that wall's
        # portion of the axis — straddling openings are intentionally kept on
        # both walls so each wall body gets the appropriate cut. Strict
        # inequalities mean a boundary-only touch (or a degenerate single-point
        # extent at the cut) keeps the opening on both walls — the safer
        # default when the helper cannot resolve a true bounding range.
        for opening in [
            r.RelatedOpeningElement for r in element1.HasOpenings if not r.RelatedOpeningElement.HasFillings
        ]:
            min_t, _ = _opening_axis_extent(opening, axis_world_2d, unit_scale)
            if min_t > cut_percentage:
                # Opening lies entirely past the cut — only element2 should keep it.
                ifcopenshell.api.feature.remove_feature(tool.Ifc.get(), feature=opening)

        for opening in [
            r.RelatedOpeningElement for r in element2.HasOpenings if not r.RelatedOpeningElement.HasFillings
        ]:
            _, max_t = _opening_axis_extent(opening, axis_world_2d, unit_scale)
            if max_t < cut_percentage:
                # Opening lies entirely before the cut — only element1 should keep it.
                ifcopenshell.api.feature.remove_feature(tool.Ifc.get(), feature=opening)

        # During the duplication process, filled voids are not copied. So we
        # only need to check fillings on the original element1. The filling
        # (door/window) belongs to whichever wall contains its center, but the
        # void may need to apply to both walls when the void's extent straddles
        # the cut — otherwise the neighbour wall's body would not be cut.
        for opening in [
            r.RelatedOpeningElement for r in list(element1.HasOpenings) if r.RelatedOpeningElement.HasFillings
        ]:
            rel = opening.HasFillings[0]
            min_t, max_t = _opening_axis_extent(opening, axis_world_2d, unit_scale)
            # Use the opening's axis-projected midpoint to classify the side.
            # The filling's ``matrix_world.translation`` is flip-fragile —
            # flipping rotates the filler 180° + translates so the bbox
            # stays visually in place, moving the door origin to the
            # opposite corner, which would mis-classify a flipped door
            # centred over the cut.
            opening_midpoint = (min_t + max_t) / 2
            void_straddles = min_t < cut_percentage < max_t
            if opening_midpoint > cut_percentage:
                # The filling should be moved from element1 to element2.
                new_opening = ifcopenshell.api.root.copy_class(tool.Ifc.get(), product=opening)
                new_opening.VoidsElements[0].RelatingBuildingElement = element2
                if new_opening.ObjectPlacement and new_opening.ObjectPlacement.is_a("IfcLocalPlacement"):
                    if element2.ObjectPlacement:
                        new_opening.ObjectPlacement.PlacementRelTo = element2.ObjectPlacement
                # For now, we do copy opening representations
                if opening.Representation:
                    new_opening.Representation = ifcopenshell.util.element.copy_deep(
                        tool.Ifc.get(), opening.Representation, exclude=["IfcGeometricRepresentationContext"]
                    )

                rel.RelatingOpeningElement = new_opening

                if void_straddles:
                    # Filling moved to element2, but void straddles — add a
                    # pure-void copy back to element1. Read from the original
                    # ``opening`` whose ObjectPlacement still references
                    # element1; ``new_opening`` was rebound to element2 and
                    # would copy element2's frame instead.
                    _add_void_copy(element1, opening)

                # Remove the old opening
                ifcopenshell.api.feature.remove_feature(tool.Ifc.get(), feature=opening)
            elif void_straddles:
                # Filling stays on element1, but void straddles — add a pure-void
                # copy to element2 so its body gets cut.
                _add_void_copy(element2, opening)

        p1, p2 = ifcopenshell.util.representation.get_reference_line(element1)
        p3 = (wall1.matrix_world.inverted() @ intersect.to_3d()).to_2d() / unit_scale
        self.set_axis(element1, p1, p3)
        self.set_axis(element2, p3, p2)

        tool.Model.recreate_wall(element1, wall1)
        tool.Model.recreate_wall(element2, wall2)
        return wall2

    def flip(self, wall1: bpy.types.Object) -> None:
        if tool.Ifc.is_moved(wall1):
            bonsai.core.geometry.edit_object_placement(tool.Ifc, tool.Geometry, tool.Surveyor, obj=wall1)

        if (
            not (element1 := tool.Ifc.get_entity(wall1))
            or not (usage := ifcopenshell.util.element.get_material(element1))
            or not usage.is_a("IfcMaterialLayerSetUsage")
            or usage.LayerSetDirection != "AXIS2"
        ):
            return

        thickness = sum([l.LayerThickness for l in usage.ForLayerSet.MaterialLayers])
        if usage.DirectionSense == "POSITIVE":
            usage.DirectionSense = "NEGATIVE"
        else:
            thickness *= -1
            usage.DirectionSense = "POSITIVE"

        matrix = ifcopenshell.util.placement.get_local_placement(element1.ObjectPlacement)
        offset = matrix[:, 1] * thickness
        matrix[:, 3] += offset
        ifcopenshell.api.geometry.edit_object_placement(
            tool.Ifc.get(), product=element1, matrix=matrix, is_si=False, should_transform_children=False
        )
        tool.Model.recreate_wall(element1, wall1)

    def merge(self, wall1: bpy.types.Object, wall2: bpy.types.Object) -> None:
        if tool.Ifc.is_moved(wall1):
            bonsai.core.geometry.edit_object_placement(tool.Ifc, tool.Geometry, tool.Surveyor, obj=wall1)
        if tool.Ifc.is_moved(wall2):
            bonsai.core.geometry.edit_object_placement(tool.Ifc, tool.Geometry, tool.Surveyor, obj=wall2)

        element1 = tool.Ifc.get_entity(wall1)
        element2 = tool.Ifc.get_entity(wall2)
        assert element1 and element2

        p1, p2 = ifcopenshell.util.representation.get_reference_line(element1)
        p3, p4 = ifcopenshell.util.representation.get_reference_line(element2)

        matrix1i = np.linalg.inv(ifcopenshell.util.placement.get_local_placement(element1.ObjectPlacement))
        matrix2 = ifcopenshell.util.placement.get_local_placement(element2.ObjectPlacement)

        p3 = (matrix1i @ matrix2 @ np.concatenate((p3, (0, 1))))[:2]
        p4 = (matrix1i @ matrix2 @ np.concatenate((p4, (0, 1))))[:2]

        if not np.isclose(p1[1], p4[1], atol=1e-02) or not np.isclose(p3[1], p4[1], atol=1e-02):
            return

        x_ordinates = tuple(co[0] for co in (p1, p2, p3, p4))
        p1[0] = min(x_ordinates)
        p2[0] = max(x_ordinates)
        self.set_axis(element1, p1, p2)

        # ConnectedTo / ConnectedFrom carry both ``IfcRelConnectsPathElements``
        # (the wall-wall joins this loop migrates) and
        # ``IfcRelConnectsElements`` (the slab underside clip). Only the
        # path rels expose ``RelatingConnectionType`` / ``RelatedConnectionType``;
        # the element rels die with element2 via the trailing cascade delete.
        for rel in element2.ConnectedTo:
            if not rel.is_a("IfcRelConnectsPathElements"):
                continue
            ifcopenshell.api.geometry.disconnect_path(
                tool.Ifc.get(), element=element1, connection_type=rel.RelatingConnectionType
            )
            ifcopenshell.api.geometry.connect_path(
                tool.Ifc.get(),
                relating_element=element1,
                related_element=rel.RelatedElement,
                relating_connection=rel.RelatingConnectionType,
                related_connection=rel.RelatedConnectionType,
            )

        for rel in element2.ConnectedFrom:
            if not rel.is_a("IfcRelConnectsPathElements"):
                continue
            ifcopenshell.api.geometry.disconnect_path(
                tool.Ifc.get(), element=element1, connection_type=rel.RelatedConnectionType
            )
            ifcopenshell.api.geometry.connect_path(
                tool.Ifc.get(),
                relating_element=rel.RelatingElement,
                related_element=element1,
                relating_connection=rel.RelatingConnectionType,
                related_connection=rel.RelatedConnectionType,
            )

        # Re-host openings from the discarded wall to the survivor before
        # the cascade delete tears down element2's voids and any filling
        # that depends on them. ``edit_object_placement`` preserves the
        # opening's world position when element1 and element2 have
        # different placements — a ``PlacementRelTo`` swap alone would
        # shift the opening as the relative offset changes.
        ifc_file = tool.Ifc.get()
        for rel in list(element2.HasOpenings):
            opening = rel.RelatedOpeningElement
            rel.RelatingBuildingElement = element1
            if opening.ObjectPlacement:
                world_matrix = ifcopenshell.util.placement.get_local_placement(opening.ObjectPlacement)
                ifcopenshell.api.geometry.edit_object_placement(
                    ifc_file,
                    product=opening,
                    matrix=world_matrix,
                    is_si=False,
                    should_transform_children=False,
                )

        tool.Model.recreate_wall(element1, wall1)

        tool.Geometry.delete_ifc_object(wall2)

    def duplicate_wall(self, wall1):
        wall2 = wall1.copy()
        wall2.data = wall2.data.copy()
        for collection in wall1.users_collection:
            collection.objects.link(wall2)
        bonsai.core.root.copy_class(tool.Ifc, tool.Collector, tool.Geometry, tool.Root, obj=wall2)
        return wall2

    def set_axis(self, wall, p1, p2):
        axis = ifcopenshell.util.representation.get_context(tool.Ifc.get(), "Plan", "Axis", "GRAPH_VIEW")
        builder = ifcopenshell.util.shape_builder.ShapeBuilder(tool.Ifc.get())
        item = builder.polyline([p1, p2])
        rep = builder.get_representation(axis, items=[item])
        if old_rep := ifcopenshell.util.representation.get_representation(wall, axis):
            ifcopenshell.util.element.replace_element(old_rep, rep)
            ifcopenshell.util.element.remove_deep2(tool.Ifc.get(), old_rep)
        else:
            ifcopenshell.api.geometry.assign_representation(tool.Ifc.get(), product=wall, representation=rep)

    def extend(self, wall1, target, connection=False):
        if tool.Ifc.is_moved(wall1):
            bonsai.core.geometry.edit_object_placement(tool.Ifc, tool.Geometry, tool.Surveyor, obj=wall1)
        element1 = tool.Ifc.get_entity(wall1)
        p1, p2 = ifcopenshell.util.representation.get_reference_line(element1)
        unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
        target = (wall1.matrix_world.inverted() @ target).to_2d() / unit_scale
        intersect, intersection_point = mathutils.geometry.intersect_point_line(target, p1, p2)
        if not connection:
            connection = "ATEND" if intersection_point > 0.5 else "ATSTART"

        ifcopenshell.api.geometry.disconnect_path(tool.Ifc.get(), element=element1, connection_type=connection)

        if connection == "ATEND":
            self.set_axis(element1, p1, intersect)
        else:
            self.set_axis(element1, intersect, p2)
        tool.Model.recreate_wall(element1, wall1)

    def set_length(self, wall1: bpy.types.Object, si_length: float) -> None:
        element1 = tool.Ifc.get_entity(wall1)
        assert element1
        if tool.Ifc.is_moved(wall1):
            bonsai.core.geometry.edit_object_placement(tool.Ifc, tool.Geometry, tool.Surveyor, obj=wall1)

        ifcopenshell.api.geometry.disconnect_path(tool.Ifc.get(), element=element1, connection_type="ATEND")

        unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
        p1, p2 = ifcopenshell.util.representation.get_reference_line(element1)
        p2[0] = p1[0] + si_length / unit_scale
        self.set_axis(element1, p1, p2)
        tool.Model.recreate_wall(element1, wall1)

    def connect(self, obj1: bpy.types.Object, obj2: bpy.types.Object) -> None:
        wall1 = tool.Ifc.get_entity(obj1)
        wall2 = tool.Ifc.get_entity(obj2)
        if tool.Ifc.is_moved(obj1):
            bonsai.core.geometry.edit_object_placement(tool.Ifc, tool.Geometry, tool.Surveyor, obj=obj1)
        if tool.Ifc.is_moved(obj2):
            bonsai.core.geometry.edit_object_placement(tool.Ifc, tool.Geometry, tool.Surveyor, obj=obj2)
        ifcopenshell.api.geometry.connect_wall(tool.Ifc.get(), wall1=wall1, wall2=wall2)
        tool.Model.recreate_wall(wall1, obj1)
        tool.Model.recreate_wall(wall2, obj2)

    def create_matrix(self, p, x, y, z):
        return Matrix([x, y, z, p]).to_4x4().transposed()

    def get_extrusion_data(self, representation):
        results = {"item": None, "height": 3.0, "x_angle": 0, "is_sloped": False, "direction": Vector((0, 0, 1))}
        item = representation.Items[0]
        while True:
            if item.is_a("IfcExtrudedAreaSolid"):
                results["item"] = item
                x, y, z = item.ExtrudedDirection.DirectionRatios
                if not tool.Cad.is_x(x, 0) or not tool.Cad.is_x(y, 0) or not tool.Cad.is_x(z, 1):
                    results["direction"] = Vector(item.ExtrudedDirection.DirectionRatios)
                    results["x_angle"] = Vector((0, 1)).angle_signed(Vector((y, z)))
                    results["is_sloped"] = True
                results["height"] = core.vertical_height_from_extrusion_depth(
                    item.Depth * self.unit_scale, results["x_angle"]
                )
                break
            elif item.is_a("IfcBooleanClippingResult"):  # should be before IfcBooleanResult check
                item = item.FirstOperand
            elif item.is_a("IfcBooleanResult"):
                if item.FirstOperand.is_a("IfcExtrudedAreaSolid") or item.FirstOperand.is_a("IfcBooleanResult"):
                    item = item.FirstOperand
                else:
                    item = item.SecondOperand
            else:
                break
        return results

    # TODO reimplement in new version and deprecate
    def clip(self, wall1: bpy.types.Object, slab2: bpy.types.Object) -> float:
        """returns height of the clipped wall, adds clipping plane to `clippings`"""
        element1 = tool.Ifc.get_entity(wall1)
        element2 = tool.Ifc.get_entity(slab2)
        assert element1 and element2

        layers1 = tool.Model.get_material_layer_parameters(element1)
        axis1 = tool.Model.get_wall_axis(wall1, layers1)

        bases = [axis1["base"][0].to_3d(), axis1["base"][1].to_3d(), axis1["side"][0].to_3d(), axis1["side"][1].to_3d()]
        bases = [Vector((v[0], v[1], wall1.matrix_world.translation.z)) for v in bases]  # add wall Z location

        representation = tool.Geometry.get_active_representation(wall1)
        assert representation
        extrusion = self.get_extrusion_data(representation)
        wall_dir = wall1.matrix_world.to_quaternion() @ extrusion["direction"]

        slab_element = tool.Ifc.get_entity(slab2)
        slab_params = tool.Model.get_material_layer_parameters(slab_element)
        slab_representation = ifcopenshell.util.representation.get_representation(
            slab_element, "Model", "Body", "MODEL_VIEW"
        )
        assert slab_representation
        slab_extrusion = tool.Model.get_extrusion(slab_representation)
        existing_x_angle = tool.Model.get_existing_x_angle(slab_extrusion)
        existing_x_angle = 0 if tool.Cad.is_x(existing_x_angle, 0, tolerance=0.001) else existing_x_angle
        existing_x_angle = 0 if tool.Cad.is_x(existing_x_angle, pi, tolerance=0.001) else existing_x_angle
        offset = slab_params["offset"]
        if slab_params["direction_sense"] == "NEGATIVE":
            offset -= slab_params["thickness"]
        slab_pt = slab2.matrix_world @ Vector((0, 0, 0)) + Vector((0, 0, offset * abs(1 / cos(existing_x_angle))))
        slab_dir = slab2.matrix_world.to_quaternion() @ Vector((0, 0, -1))

        tops = [mathutils.geometry.intersect_line_plane(b, b + wall_dir, slab_pt, slab_dir) for b in bases]
        top_index = max(range(4), key=lambda i: tops[i].z)
        i_top = tops[top_index]
        i_bottom = bases[top_index]

        quaternion = slab2.matrix_world.to_quaternion()
        x_axis = quaternion @ Vector((1, 0, 0))
        y_axis = quaternion @ Vector((0, 1, 0))
        z_axis = quaternion @ Vector((0, 0, 1))
        self.clippings.append(
            {
                "type": "IfcBooleanClippingResult",
                "operand_type": "IfcHalfSpaceSolid",
                "matrix": self.create_matrix(i_top, x_axis, y_axis, z_axis),
            }
        )

        return (i_top - i_bottom).length


class EnableEditingWall(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.enable_editing_wall"
    bl_label = "Edit Wall"
    bl_description = "Show wall edit gizmos"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context: bpy.types.Context) -> set[str]:
        obj = context.active_object
        if not obj:
            return {"CANCELLED"}
        reason = tool.Wall.validate_for_parametric_edit(obj)
        if reason:
            self.report({"WARNING"}, f"Cannot edit wall parametrically: {reason}")
            return {"CANCELLED"}
        # If openings are currently shown for editing (via the Toggle Openings gizmo
        # or the Alt+O hotkey), apply them before entering wall edit mode. Otherwise
        # the wall enters edit mode with floating opening previews that don't reflect
        # the IFC state the gizmos read from.
        if tool.Model.get_model_props().openings:
            bpy.ops.bim.edit_openings(apply_all=True)
        props = tool.Model.get_wall_props(obj)
        # Force is_editing False before populating so update_wall stays a no-op
        # while we copy IFC state into the draft properties.
        props.is_editing = False
        _read_wall_state_into_props(obj, props)
        # Mesh stays as the existing IFC-derived geometry until the first gizmo drag
        # — that way an enable → ✓ round-trip with no drag is a true no-op.
        props.mesh_dirty = False
        props.is_editing = True
        return {"FINISHED"}


class CancelEditingWall(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.cancel_editing_wall"
    bl_label = "Discard Wall Edits"
    bl_description = "Discard wall edits"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context: bpy.types.Context) -> set[str]:
        obj = context.active_object
        if not obj:
            return {"CANCELLED"}
        props = tool.Model.get_wall_props(obj)
        # Disable update_wall first so the snap restores don't redraw the preview.
        props.is_editing = False
        props.length = props.snap_length
        props.height = props.snap_height
        props.thickness = props.snap_thickness
        props.offset = props.snap_offset
        # If the user dragged before cancelling, the visible mesh is the simplified
        # preview box (openings/layers stripped). Restore the real IFC-derived geometry
        # so cancel feels like a true undo — equivalent to the user hitting S_G manually.
        _restore_wall_mesh_if_dirty(obj)
        return {"FINISHED"}


class FinishEditingWall(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.finish_editing_wall"
    bl_label = "Apply Wall Edits"
    bl_description = "Apply wall edits"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context: bpy.types.Context) -> set[str]:
        obj = context.active_object
        if not obj:
            return {"CANCELLED"}
        element = tool.Ifc.get_entity(obj)
        if not element:
            return {"CANCELLED"}
        props = tool.Model.get_wall_props(obj)
        # No edit session in progress — finish is a true no-op. Without this guard,
        # an enable that failed validation (e.g. wall without IfcMaterialLayerSetUsage)
        # leaves is_editing=False but a press on finish still walks the sub-ops below,
        # which dereference layer-set-dependent state and crash.
        if not props.is_editing:
            return {"CANCELLED"}

        length_changed = not tool.Cad.is_x(props.length, props.snap_length, tolerance=1e-5)
        height_changed = not tool.Cad.is_x(props.height, props.snap_height, tolerance=1e-5)
        x_angle_changed = not tool.Cad.is_x(props.x_angle, props.snap_x_angle, tolerance=1e-5)
        baseline_changed = props.desired_offset_baseline != props.snap_offset_baseline
        any_change = length_changed or height_changed or x_angle_changed or baseline_changed

        # Order matters: baseline shifts the layer-set reference line, then length
        # adjusts endpoints relative to that, then x_angle changes the slope (and
        # recomputes extrusion direction), and height is applied LAST so it reads the
        # final x_angle when converting vertical-height ↔ extrusion-depth. Running
        # height before x_angle made the slope op overwrite the just-set height.
        # temp_override scopes each sub-op to this wall so the delegated operators
        # don't fan out to other selected walls.
        with bpy.context.temp_override(active_object=obj, selected_objects=[obj]):
            if baseline_changed:
                tool.Model.offset_wall(obj, props.desired_offset_baseline)
                tool.Model.recalculate_walls([obj])
                tool.Model.get_model_props().offset_type_vertical = props.desired_offset_baseline
            if length_changed:
                DumbWallJoiner().set_length(obj, props.length)
                tool.Model.recalculate_walls([obj])
            if x_angle_changed:
                bpy.ops.bim.change_extrusion_x_angle(x_angle=props.x_angle)
            if height_changed:
                bpy.ops.bim.change_extrusion_depth(depth=props.height)

        if any_change:
            props.mesh_dirty = False
        else:
            _restore_wall_mesh_if_dirty(obj)
        # Set only on success: if any sub-op above raised, the draft survives for retry.
        props.is_editing = False
        return {"FINISHED"}


class CycleWallOffset(bpy.types.Operator):
    bl_idname = "bim.cycle_wall_offset"
    bl_label = "Cycle Wall Baseline"
    bl_description = "Cycle wall baseline through Exterior, Centreline, Interior. Shift+click reverses"
    bl_options = {"REGISTER", "UNDO"}
    # Deliberately NOT a tool.Ifc.Operator: this operator never calls into
    # ifcopenshell.api. Inheriting from Ifc.Operator would drag a draft-only
    # property cycle into Bonsai's IFC undo transaction system.

    @classmethod
    def poll(cls, context):
        if not tool.Model.has_selected_ifc_objects():
            cls.poll_message_set("No IFC objects selected.")
            return False
        return True

    # Same order the offset_type_vertical EnumProperty uses in prop.py.
    _ORDER = ("EXTERIOR", "CENTER", "INTERIOR")
    reverse: bpy.props.BoolProperty(name="Reverse", default=False, options={"HIDDEN", "SKIP_SAVE"})

    def invoke(self, context: bpy.types.Context, event: bpy.types.Event) -> set[str]:
        self.reverse = event.shift
        return self.execute(context)

    def execute(self, context: bpy.types.Context) -> set[str]:
        obj = context.active_object
        if not obj:
            return {"CANCELLED"}
        props = tool.Model.get_wall_props(obj)
        if not props.is_editing:
            self.report({"WARNING"}, "Cycle wall offset only works in wall edit mode.")
            return {"CANCELLED"}
        current = props.desired_offset_baseline
        idx = self._ORDER.index(current) if current in self._ORDER else 0
        direction = -1 if self.reverse else 1
        props.desired_offset_baseline = self._ORDER[(idx + direction) % len(self._ORDER)]
        return {"FINISHED"}


class GizmoWallEdition(bpy.types.GizmoGroup, gizmo.BaseParametricGizmoGroup):
    bl_idname = "OBJECT_GGT_bim_wall_edition"
    bl_label = "Wall Editing Gizmo"
    bl_space_type = "VIEW_3D"
    bl_region_type = "WINDOW"
    bl_options = {"3D", "PERSISTENT"}

    enable_editing_operator = "bim.enable_editing_wall"
    finish_editing_operator = "bim.finish_editing_wall"
    cancel_editing_operator = "bim.cancel_editing_wall"
    # Empty disables the base class's auto-created cycle_gizmo at ICON_CYCLE_X.
    # Three state-specific baseline icons (exterior / center / interior) take
    # over that slot, with the active one chosen per frame from props.
    cycle_type_operator = ""

    # Threshold (SI meters) above which a second height gizmo is drawn at the far end of
    # the wall so the user doesn't have to pan across long walls to reach a height handle.
    LONG_WALL_THRESHOLD = 5.0

    dimension_gizmo_props = [
        # length / height / height_end positions are recomputed per frame in
        # ``_update_dimension_gizmo_positions`` so they flip to the camera-facing
        # side of the wall as the viewport is orbited. No static ``matrix_position``
        # here means the base class falls back to Identity, which the override
        # then replaces with the view-dependent coordinates.
        DimensionGizmoConfig(
            attr_name="length",
            axis=(1, 0, 0),
            min_value=0.01,
            text_offset_sign=-1,
        ),
        DimensionGizmoConfig(
            attr_name="height",
            axis=(0, 0, 1),
            min_value=0.01,
        ),
        # Second height gizmo at the far end of long walls. Distinct attr_name so it
        # doesn't collide with the first height gizmo in self.dimension_*_gizmo storage;
        # compute/apply tunnel through to the same props.height.
        DimensionGizmoConfig(
            attr_name="height_end",
            axis=(0, 0, 1),
            min_value=0.01,
            # default-arg captures the class const because lambda body can't see class scope.
            visibility_condition=lambda p, _t=LONG_WALL_THRESHOLD: p.length > _t,
            compute_value=lambda p: p.height,
            apply_value=lambda p, v: setattr(p, "height", max(0.01, v)),
            color="BLUE",
        ),
        # Slope: a Y-axis dimension at the top edge measuring horizontal displacement
        # of the top face. compute/apply translate between displacement (what the user
        # sees & drags) and x_angle (what's stored). Drag toward +Y → positive slope.
        DimensionGizmoConfig(
            attr_name="x_angle",
            axis=(0, 1, 0),
            prop_name="Slope",
            matrix_position=lambda p: Vector((p.anchor_x + p.length / 2, p.offset + p.thickness / 2, p.height)),
            compute_value=lambda p: core.displacement_from_x_angle(p.height, p.x_angle),
            apply_value=lambda p, displacement: setattr(
                p, "x_angle", core.x_angle_from_displacement(p.height, displacement)
            ),
            color="GREEN",
            min_value=-1e6,  # apply_value clamps via atan2; allow negative displacement
            text_formatter=lambda p, displacement: (
                f"{'-' if displacement < 0 else ''}{tool.Unit.format_distance(abs(displacement))} "
                f"({math.degrees(p.x_angle):.1f}°)"
            ),
        ),
    ]

    props_getter = tool.Model.get_wall_props
    gizmo_pref_name = "wall"

    @classmethod
    def is_element_type(cls, element: ifcopenshell.entity_instance) -> bool:
        return tool.Parametric.is_wall(element)

    def get_icon_y_extent(self, props: "BIMWallProperties") -> tuple[float, float]:
        far = props.offset + props.thickness + 2 * self.GIZMO_OFFSET
        near = -props.offset + 2 * self.GIZMO_OFFSET
        return (far, near)

    def _update_dimension_gizmo_positions(
        self, context: bpy.types.Context, mw: Matrix, props: "BIMWallProperties"  # noqa: ARG002
    ) -> None:
        """Re-position length / height / height_end dimensions to the camera-facing
        Y-side of the wall every frame. Mirrors the door & stair pattern: when the
        viewport is orbited past the wall, the handles jump to the visible face
        instead of being stranded behind it.

        - When viewing from -Y: place handles at wall-local Y = ``offset - GIZMO_OFFSET``.
        - When viewing from +Y: place handles at wall-local Y = ``offset + thickness + GIZMO_OFFSET``.

        Slope (``x_angle``) is intentionally NOT view-flipped — it lives at the wall
        axis centerline because the gizmo IS the Y-displacement indicator. Flipping
        it would invert the drag direction relative to the user's pointer motion."""
        viewing_from_neg_y, _ = self._frame_view_dir
        y_camera_side = self.get_camera_facing_outer_y(
            viewing_from_neg_y,
            props.offset,
            props.offset + props.thickness,
            self.GIZMO_OFFSET,
        )
        # Length: along X axis at half-height, on the camera-facing edge.
        self.set_dimension_gizmo_position(
            "length",
            mw,
            Vector((props.anchor_x, y_camera_side, props.height / 2)),
            (1, 0, 0),
        )
        # Height (start of wall): along Z, at the start endpoint, camera-facing side.
        self.set_dimension_gizmo_position(
            "height",
            mw,
            Vector((props.anchor_x, y_camera_side, 0)),
            (0, 0, 1),
        )
        # Height (far end of long walls): along Z, at the end endpoint, camera-facing side.
        self.set_dimension_gizmo_position(
            "height_end",
            mw,
            Vector((props.anchor_x + props.length, y_camera_side, 0)),
            (0, 0, 1),
        )

    # Per-region weakref map populated at setup time. The wall-gizmo preview
    # decorator dereferences this each draw to read live ``is_highlight`` state
    # off the cursor icons (extend-X / extend-Z / split) in the same region
    # it's currently drawing in, so the GPU axis-preview lines only render
    # while the matching icon is hovered.
    _active_instances: ClassVar["dict[int, weakref.ReferenceType[GizmoWallEdition]]"] = {}

    # Row layout: validate / cancel / baseline-triplet / rotate / array.
    # Wall has no ``cycle_type_operator``, so the cycle slot collapses and
    # the baseline triplet takes the cycle X position (0.87). Rotate
    # follows at 1.24. Both slots are declared here — the layout manager
    # assigns the X positions from tuple order.
    feature_slots: ClassVar[tuple[IconSlot, ...]] = (
        IconSlot(
            name="baseline",
            gizmo_idname="VIEW3D_GT_offset",
            variants=("exterior", "center", "interior"),
            operator="bim.cycle_wall_offset",
        ),
        IconSlot(
            name="rotate",
            gizmo_idname="VIEW3D_GT_cycle",
            operator="bim.rotate_wall_90",
            scale=0.30,
        ),
    )

    # Idle-mode pen-row extras. The base class handles setup + per-frame
    # positioning + visibility gating via ``visible_when``; this declaration
    # is the only wall-specific code needed for the toggle-openings icon.
    idle_slots: ClassVar[tuple[IconSlot, ...]] = (
        IconSlot(
            name="toggle_openings",
            gizmo_idname="VIEW3D_GT_add_opening",
            operator="bim.toggle_host_openings",
            visible_when=lambda gg: _wall_has_openings(gg),
        ),
    )

    def setup_element_specific_gizmos(self, context: bpy.types.Context) -> None:
        """Wall-specific gizmos.

        Cursor-anchored (always visible during edit mode, conditional position):

        - ``split_gizmo`` — at the 3D cursor's exact world position when cursor is
          within the wall's X range. Clicking splits the wall there.
        - ``extend_x_gizmo`` — at the wall-local X of the cursor, projected to the
          floor plane (Z=0 in wall-local). Clicking extends/trims the wall's length.
        - ``extend_z_gizmo`` — at the wall-local X of the cursor, projected to the
          wall top (Z=height in wall-local). Clicking extends the wall's height to
          the cursor's Z.
        - ``add_perpendicular_wall_gizmo`` — visible only when the cursor is
          off-axis by more than ``CURSOR_STACK_OFFSET``. Sits at the cursor's
          XY (X clamped to the wall's X-range) on the wall-local floor plane.
          Clicking spawns a perpendicular branch wall; shift+click forms a corner.

        The baseline-state triplet (exterior/center/interior) and the rotate-90
        icon live in ``feature_slots`` — the base class handles creation and
        edit-row positioning; this group only picks variant visibility per
        frame in ``_update_icon_row_extras``. The idle-row ``toggle_openings``
        icon is declared in ``idle_slots`` and fully managed by the base."""
        default_color, highlight_color = self.get_decoration_colors()
        self.split_gizmo = self._setup_icon_gizmo(
            "VIEW3D_GT_split",
            default_color,
            "bim.split_wall_at_cursor",
            highlight_color,
        )
        self.extend_x_gizmo = self._setup_icon_gizmo(
            "VIEW3D_GT_extend",
            default_color,
            "bim.extend_wall_to_cursor",
            highlight_color,
        )
        self.extend_z_gizmo = self._setup_icon_gizmo(
            "VIEW3D_GT_extend_vertical",
            default_color,
            "bim.extend_wall_height_to_cursor",
            highlight_color,
        )
        self.add_perpendicular_wall_gizmo = self._setup_icon_gizmo(
            "VIEW3D_GT_extend",
            default_color,
            "bim.add_perpendicular_wall",
            highlight_color,
        )
        if context.region is not None:
            type(self)._active_instances[context.region.as_pointer()] = weakref.ref(self)

    def _refresh_element_specific(self, context: bpy.types.Context, mw: Matrix, props: "BIMWallProperties") -> None:
        """Position cursor-anchored gizmos and the wall-specific icon-row extras."""
        self._update_cursor_gizmos(context, mw, props)
        self._update_icon_row_extras(context, mw, props)

    # World-Z spacing between stacked cursor icons. ~0.3m is ~1.5× icon diameter
    # at default scale, leaving a small visual gap between consecutive icons.
    CURSOR_STACK_OFFSET = 0.3

    def _stack_offset(self, stack_index: int, screen_up: Vector, clearance: Vector) -> Vector:
        """World-space offset for the ``stack_index``-th icon in a cursor
        row: ``clearance`` (top-down only) plus a screen-up step per slot.
        Single source of truth for the cursor-row stacking discipline."""
        return clearance + screen_up * (stack_index * self.CURSOR_STACK_OFFSET)

    def _update_cursor_gizmos(self, context: bpy.types.Context, mw: Matrix, props: "BIMWallProperties") -> None:
        """Position the cursor-anchored icons (extend-X / extend-Z / split) on the wall
        axis at the cursor's projected X.

        Always visible when a parametric wall is selected — not gated on edit
        mode. The three operators (``bim.extend_wall_to_cursor`` /
        ``bim.extend_wall_height_to_cursor`` / ``bim.split_wall_at_cursor``)
        all poll on wall-selected and commit any pending wall edit before
        acting, so single-click without entering edit mode is the canonical
        flow. The ``WallGizmoPreviewDecorator`` keeps the viewport clean by
        only drawing the action's guide line on hover.

        Two branches by view orientation:

        - **Non-top-down**: world-Z stacking. Each icon sits at the Z its
          action would land at (extend-X at floor, extend-Z at cursor Z,
          split at wall top). Colliding icons stack at ``CURSOR_STACK_OFFSET``
          increments; priority low → high: extend-X, extend-Z, split.
        - **Top-down (plan view)**: world-Z collapses to one screen point,
          so the world-Z stack would invisibly pile every icon on top of
          ``extend_x``. Drop ``extend_z`` (vertical intent has no readable
          cue when looking down +Z) and stack the rest along screen-up at
          the floor anchor."""
        if not hasattr(self, "split_gizmo"):
            return
        all_gizmos = (
            self.extend_x_gizmo,
            self.extend_z_gizmo,
            self.split_gizmo,
            self.add_perpendicular_wall_gizmo,
        )
        cursor_world = context.scene.cursor.location
        cursor_local = mw.inverted() @ cursor_world
        # ``props.anchor_x`` / ``props.length`` mirror IFC and are only refreshed
        # when an operator calls ``_maybe_resync_wall_props_from_ifc``. Reading
        # the live extent from the mesh bbox makes the gizmo position robust
        # against any operator path that skips that re-sync — the mesh is
        # always rebuilt by ``recreate_wall`` to match the current IFC body.
        bbox_x = [v[0] for v in context.active_object.bound_box] if context.active_object else None
        if bbox_x:
            wall_anchor_x = min(bbox_x)
            wall_length = max(bbox_x) - wall_anchor_x
        else:
            wall_anchor_x = props.anchor_x
            wall_length = props.length
        in_range = wall_anchor_x < cursor_local.x < wall_anchor_x + wall_length
        billboard_rot = self._frame_billboard_rot
        top_down = tool.Blender.is_view_top_down(context)
        perp_params = _perpendicular_wall_params(cursor_local.x, cursor_local.y, wall_anchor_x, wall_length)

        # Candidates ordered by priority (lowest first). Each is (gizmo, local_z).
        candidates: list[tuple[bpy.types.Gizmo, float]] = [(self.extend_x_gizmo, 0.0)]
        if not top_down:
            candidates.append((self.extend_z_gizmo, cursor_local.z))
        if in_range:
            # Vertical (world-Z) height → wall-local Z so the icon lands on
            # the slanted top edge for sloped walls (x_angle != 0).
            split_local_z = core.extrusion_depth_from_vertical_height(props.height, props.x_angle)
            candidates.append((self.split_gizmo, split_local_z))

        # Resolve collisions: walk in priority order and ensure each gizmo's
        # final Z is at least CURSOR_STACK_OFFSET above the previous one (when
        # the previous one's final Z is higher).
        resolved: list[tuple[bpy.types.Gizmo, float]] = []
        for gz, desired_z in candidates:
            final_z = desired_z
            for _, prev_z in resolved:
                if abs(final_z - prev_z) < self.CURSOR_STACK_OFFSET:
                    final_z = prev_z + self.CURSOR_STACK_OFFSET
            resolved.append((gz, final_z))

        for gz in all_gizmos:
            gz.hide = True
        screen_up = tool.Blender.get_screen_up_world(context)
        clearance = gizmo.top_down_clearance(context, billboard_rot)
        if top_down:
            # Swap world-Z stacking for screen-up stacking so each icon stays
            # individually clickable when the camera projects world Z to zero.
            # The shared ``top_down_clearance`` lifts the whole stack off the
            # cursor so its small crosshair stays visible for precise pointing.
            base_world = mw @ Vector((cursor_local.x, 0.0, 0.0))
            for index, (gz, _local_z) in enumerate(resolved):
                gz.hide = self.is_gizmo_hidden_by_modal(gz)
                world_pos = base_world + self._stack_offset(index, screen_up, clearance)
                gz.matrix_basis = gizmo.billboarded_at(world_pos, billboard_rot)
                _apply_wall_extend_flips(gz, self, world_pos, mw, cursor_local, props, billboard_rot)
        else:
            # World-Z stacking carries each icon's semantic Z (extend-X at
            # floor, extend-Z at cursor Z, split at wall top). At shallow
            # viewing angles a 0.3 m gap can still project to near-zero
            # screen separation, so add a screen-up offset per stack slot
            # — the world-Z position still drives the icon's meaning, the
            # screen-up term is just visual insurance.
            no_clearance = Vector((0.0, 0.0, 0.0))
            for index, (gz, local_z) in enumerate(resolved):
                gz.hide = self.is_gizmo_hidden_by_modal(gz)
                world_pos = mw @ Vector((cursor_local.x, 0.0, local_z)) + self._stack_offset(
                    index, screen_up, no_clearance
                )
                gz.matrix_basis = gizmo.billboarded_at(world_pos, billboard_rot)
                _apply_wall_extend_flips(gz, self, world_pos, mw, cursor_local, props, billboard_rot)

        if perp_params is not None:
            # Stack the perpendicular gizmo one slot above the on-axis row
            # along screen-up so it stays independently clickable when the
            # cursor sits just past the dead zone. The arrow's in-plane
            # rotation points its +X from the wall projection toward the
            # cursor as a "new wall sprouts this way" cue.
            clamped_x, _length, side_sign = perp_params
            gz = self.add_perpendicular_wall_gizmo
            gz.hide = self.is_gizmo_hidden_by_modal(gz)
            perp_base = mw @ Vector((clamped_x, cursor_local.y, 0.0))
            perp_world = perp_base + self._stack_offset(len(resolved), screen_up, clearance)
            perp_world_dir = (mw.to_3x3().col[1] * side_sign).normalized()
            screen_dir = billboard_rot.transposed() @ perp_world_dir
            angle = math.atan2(screen_dir.y, screen_dir.x)
            gz.matrix_basis = gizmo.billboarded_at(perp_world, billboard_rot) @ Matrix.Rotation(angle, 4, "Z")

    # Map ``props.desired_offset_baseline`` (storage form) to the slot variant
    # name. Centralised here so the variant strings stay aligned with the slot
    # declaration in feature_slots.
    _BASELINE_TO_VARIANT: ClassVar[dict[str, str]] = {
        "EXTERIOR": "exterior",
        "CENTER": "center",
        "INTERIOR": "interior",
    }

    def _update_icon_row_extras(self, context: bpy.types.Context, mw: Matrix, props: "BIMWallProperties") -> None:
        """Pick which baseline variant is visible during edit.

        Baseline triplet: the base class's slot loop already wrote a billboard
        matrix on each variant member at the same X (the cycle slot, since
        wall has no ``cycle_type_operator``). This hook only flips ``hide``
        on each member based on ``props.desired_offset_baseline`` so exactly
        one variant shows. The rotate-90 icon is a single-icon feature slot
        and is fully handled by the base. The toggle-openings idle icon is
        declared in ``idle_slots`` and positioned by the base."""
        active_variant = self._BASELINE_TO_VARIANT.get(props.desired_offset_baseline)
        for variant in ("exterior", "center", "interior"):
            gz = getattr(self, f"baseline_{variant}_gizmo", None)
            if gz is None:
                continue
            if props.is_editing and variant == active_variant:
                gz.hide = self.is_gizmo_hidden_by_modal(gz)
            else:
                gz.hide = True


def _apply_wall_extend_flips(
    gz: bpy.types.Gizmo,
    group: "GizmoWallEdition",
    world_pos: Vector,
    mw: Matrix,
    cursor_local: Vector,
    props: "BIMWallProperties",
    billboard_rot: Matrix,
) -> None:
    """Mirror the wall's extend arrows so each points toward the end the click will move.

    Extend-X: arrow points away from the wall endpoint that the operator would
    keep fixed, accounting for the camera's screen-X orientation. Extend-Z:
    arrow flips downward when the cursor sits below the wall top."""
    if gz is group.extend_x_gizmo:
        if props.length > 0 and cursor_local.x > props.anchor_x + props.length / 2:
            reference_x = props.anchor_x
        else:
            reference_x = props.anchor_x + props.length
        reference_world = mw @ Vector((reference_x, 0.0, 0.0))
        if gizmo.should_flip_extend_arrow(world_pos, reference_world, billboard_rot):
            gz.matrix_basis = gz.matrix_basis @ gizmo.EXTEND_FLIP_MIRROR_X
    elif gz is group.extend_z_gizmo and cursor_local.z < props.height - gizmo.EXTEND_FLIP_EPSILON:
        gz.matrix_basis = gz.matrix_basis @ gizmo.EXTEND_FLIP_MIRROR_Y


def _commit_active_wall_edit_if_any(context: bpy.types.Context) -> bpy.types.Object | None:
    """Return the active object, committing any in-progress wall edit first.

    Used by the scissors/extend gizmo operators: clicking either icon implicitly
    validates the current edit (✓ semantics) before running the follow-up action.
    Returns None when there's no active object — callers should treat that as CANCELLED."""
    obj = context.active_object
    if not obj:
        return None
    props = tool.Model.get_wall_props(obj)
    if props.is_editing:
        bpy.ops.bim.finish_editing_wall()
    return obj


def _perpendicular_wall_params(
    cursor_local_x: float,
    cursor_local_y: float,
    anchor_x: float,
    length: float,
) -> tuple[float, float, float] | None:
    """Geometry of a perpendicular branch wall sprouting from the cursor's
    projection on the source wall axis.

    Returns ``(clamped_x, perpendicular_length, side_sign)`` — the projection
    on the wall axis (clamped to ``[anchor_x, anchor_x + length]``), the
    branch wall length, and the side (+1 / -1) the branch sits on. Returns
    ``None`` when the cursor sits within ``CURSOR_STACK_OFFSET`` of the
    source wall axis (the on-wall dead zone)."""
    if abs(cursor_local_y) <= GizmoWallEdition.CURSOR_STACK_OFFSET:
        return None
    clamped_x = max(anchor_x, min(anchor_x + length, cursor_local_x))
    side_sign = 1.0 if cursor_local_y > 0 else -1.0
    return clamped_x, abs(cursor_local_y), side_sign


def _commit_pending_wall_edits_for_selection(context: bpy.types.Context) -> None:  # noqa: ARG001
    """Thin wall-scoped alias for ``tool.Parametric.commit_pending_edits_for_selection``.

    Encapsulates the ``names=("wall",)`` filter so the registry name is
    touched in exactly one place."""
    tool.Parametric.commit_pending_edits_for_selection(names=("wall",))


class SplitWallAtCursor(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.split_wall_at_cursor"
    bl_label = "Split Wall at Cursor"
    bl_description = "Split wall at 3D cursor location"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if not tool.Model.has_selected_ifc_objects():
            cls.poll_message_set("No IFC objects selected.")
            return False
        return True

    def _execute(self, context: bpy.types.Context) -> set[str]:
        # Applies any pending wall edit first so the split operates on the committed
        # geometry rather than the draft preview box.
        obj = _commit_active_wall_edit_if_any(context)
        if obj is None:
            return {"CANCELLED"}
        bpy.ops.bim.split_wall()
        _maybe_resync_wall_props_from_ifc(obj)
        return {"FINISHED"}


class ExtendWallToCursor(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.extend_wall_to_cursor"
    bl_label = "Extend Wall to Cursor"
    bl_description = "Extend wall length to 3D cursor location"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if not tool.Model.has_selected_ifc_objects():
            cls.poll_message_set("No IFC objects selected.")
            return False
        return True

    def _execute(self, context: bpy.types.Context) -> set[str]:
        if _commit_active_wall_edit_if_any(context) is None:
            return {"CANCELLED"}
        core.extend_walls(
            tool.Ifc,
            tool.Blender,
            tool.Geometry,
            DumbWallJoiner(),
            tool.Model,
            context.scene.cursor.location,
        )
        affected = list(tool.Blender.get_selected_objects())
        _resync_walls_after_mutation(affected)
        _regenerate_walls(affected)
        return {"FINISHED"}


class ExtendWallHeightToCursor(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.extend_wall_height_to_cursor"
    bl_label = "Extend Wall Height to Cursor Z"
    bl_description = "Extend wall height to 3D cursor Z location"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if not tool.Model.has_selected_ifc_objects():
            cls.poll_message_set("No IFC objects selected.")
            return False
        return True

    def _execute(self, context: bpy.types.Context) -> set[str]:
        obj = _commit_active_wall_edit_if_any(context)
        if obj is None:
            return {"CANCELLED"}
        cursor_z = context.scene.cursor.location.z
        base_z = obj.matrix_world.translation.z
        new_height = cursor_z - base_z
        if new_height <= 0:
            self.report(
                {"WARNING"},
                f"Cursor Z ({cursor_z:.2f}m) must be above wall base ({base_z:.2f}m).",
            )
            return {"CANCELLED"}
        with bpy.context.temp_override(active_object=obj, selected_objects=[obj]):
            bpy.ops.bim.change_extrusion_depth(depth=new_height)
        _maybe_resync_wall_props_from_ifc(obj)
        _regenerate_walls([obj])
        return {"FINISHED"}


class AddPerpendicularWall(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_perpendicular_wall"
    bl_label = "Add Perpendicular Wall at Cursor"
    bl_description = (
        "Create a new wall perpendicular to the active wall, from the cursor's "
        "orthogonal projection on the wall axis toward the cursor. "
        "Shift+Click for corner junction: the source wall is trimmed at the "
        "projection, keeping its longer portion."
    )
    bl_options = {"REGISTER", "UNDO"}

    use_corner_junction: bpy.props.BoolProperty(default=False)

    @classmethod
    def poll(cls, context):
        if not tool.Model.has_selected_ifc_objects():
            cls.poll_message_set("No IFC objects selected.")
            return False
        return True

    def invoke(self, context, event):
        self.use_corner_junction = bool(event.shift)
        return self.execute(context)

    def _execute(self, context: bpy.types.Context) -> set[str]:
        source_obj = _commit_active_wall_edit_if_any(context)
        if source_obj is None:
            return {"CANCELLED"}
        source_element = tool.Ifc.get_entity(source_obj)
        if source_element is None:
            self.report({"WARNING"}, "Active object is not an IFC element.")
            return {"CANCELLED"}
        source_type = ifcopenshell.util.element.get_type(source_element)
        if source_type is None:
            self.report({"WARNING"}, "Active wall has no IfcWallType; cannot derive branch wall.")
            return {"CANCELLED"}
        props = tool.Model.get_wall_props(source_obj)
        cursor_local = source_obj.matrix_world.inverted() @ context.scene.cursor.location
        params = _perpendicular_wall_params(cursor_local.x, cursor_local.y, props.anchor_x, props.length)
        if params is None:
            self.report({"INFO"}, "Cursor is on the wall axis; nothing to do.")
            return {"CANCELLED"}
        clamped_x, perpendicular_length, side_sign = params
        start_world = source_obj.matrix_world @ Vector((clamped_x, 0.0, 0.0))
        source_z_rotation = source_obj.matrix_world.to_euler().z
        new_z_rotation = source_z_rotation + side_sign * (pi / 2)

        # Shift+click L-corners the new wall against an endpoint of the
        # source wall: the source is trimmed at the projection, keeping
        # its longer of the two portions.
        if self.use_corner_junction:
            DumbWallJoiner().extend(source_obj, start_world)

        source_layers = tool.Model.get_material_layer_parameters(source_element)

        generator = DumbWallGenerator(source_type)
        generator.file = tool.Ifc.get()
        generator.layers = tool.Model.get_material_layer_parameters(source_type)
        if not generator.layers["thickness"]:
            self.report({"WARNING"}, "Wall type has no layer thickness; cannot create branch wall.")
            return {"CANCELLED"}
        generator.body_context = ifcopenshell.util.representation.get_context(
            tool.Ifc.get(), "Model", "Body", "MODEL_VIEW"
        )
        generator.axis_context = ifcopenshell.util.representation.get_context(
            tool.Ifc.get(), "Plan", "Axis", "GRAPH_VIEW"
        )
        generator.container = None
        generator.container_obj = None
        generator.width = generator.layers["thickness"]
        generator.height = props.height
        generator.length = perpendicular_length
        generator.rotation = new_z_rotation
        generator.location = start_world
        generator.x_angle = 0.0
        new_obj = generator.create_wall()
        new_element = tool.Ifc.get_entity(new_obj)

        # Branch wall inherits the source wall's centerline / offset baseline
        # so the new axis lines up with the source's authored alignment rather
        # than the type's default.
        source_baseline = core.baseline_from_offset(source_layers["offset"], source_layers["thickness"])
        tool.Model.offset_wall(new_obj, source_baseline)

        ifcopenshell.api.geometry.connect_wall(
            tool.Ifc.get(),
            wall1=new_element,
            wall2=source_element,
            is_atpath=not self.use_corner_junction,
        )

        source_container = ifcopenshell.util.element.get_container(source_element)
        if source_container is not None:
            bonsai.core.spatial.assign_container(
                tool.Ifc, tool.Collector, tool.Spatial, container=source_container, objs=[new_obj]
            )

        tool.Model.recreate_wall(source_element, source_obj)
        tool.Model.recreate_wall(new_element, new_obj)

        tool.Blender.deselect_object(source_obj, ensure_active_object=False)
        tool.Blender.set_active_object(new_obj)

        _resync_walls_after_mutation([source_obj, new_obj])
        return {"FINISHED"}


class RotateWall90(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.rotate_wall_90"
    bl_label = "Rotate Wall 90°"
    bl_description = "Rotate wall 90° around Z axis"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if not tool.Model.has_selected_ifc_objects():
            cls.poll_message_set("No IFC objects selected.")
            return False
        return True

    def _execute(self, context: bpy.types.Context) -> set[str]:
        obj = _commit_active_wall_edit_if_any(context)
        if obj is None:
            return {"CANCELLED"}
        with bpy.context.temp_override(active_object=obj, selected_objects=[obj]):
            bpy.ops.bim.rotate_90(axis="Z")
        return {"FINISHED"}


def _wall_axis_world_segment_from_geom(obj: bpy.types.Object, geom: dict) -> tuple[Vector, Vector]:
    """Compose the world-space axis segment from an already-read ``geom`` dict.
    Used by the billboarding gizmo groups so a single cached IFC read drives both
    ``tool.Wall.read_geometry`` *and* the segment, avoiding two reads per wall per frame."""
    p1_local = Vector((geom["anchor_x"], 0.0, 0.0))
    p2_local = Vector((geom["anchor_x"] + geom["length"], 0.0, 0.0))
    return obj.matrix_world @ p1_local, obj.matrix_world @ p2_local


class _WallGeomCachedBillboardingMixin(gizmo.BillboardingGizmoGroupMixin):
    """Adds IFC-read caching to `BillboardingGizmoGroupMixin` for wall-driven
    gizmo groups. ``refresh()`` is Blender's "something state-relevant changed"
    signal — that's when we drop the cache. ``draw_prepare()`` (every redraw) reuses
    whatever ``_get_wall_geom_cached`` populated, so plain camera orbits don't re-hit
    IFC. ``_get_wall_geom_cached`` also drops entries on its own when
    `tool.Parametric.get_geom_generation` advances (any ``tool.Ifc.Operator``
    commit) so external ``bpy.ops`` mutations on the same selection don't leave
    stale geometry behind."""

    def refresh(self, context: bpy.types.Context) -> None:
        self._wall_geom_cache = None
        self._wall_connections_cache = None
        self._wall_pair_predicate_cache = None
        self.position_gizmos(context)


def _get_wall_geom_cached(group: "bpy.types.GizmoGroup", obj: bpy.types.Object) -> dict | None:
    """Per-gizmo-group memoised ``tool.Wall.read_geometry``. Without this, a
    billboarding gizmo group re-runs the IFC read on every camera orbit frame —
    ~120 IFC queries per second per wall, which is unwieldy on dense models.

    Two invalidation paths:

    - ``GizmoGroup.refresh()`` (Blender's state-change hook — selection,
      gizmo modal exit, …) clears ``_wall_geom_cache`` directly.
    - ``tool.Parametric.refresh_post_commit()`` bumps a generation counter on
      every IFC operator commit; the cache stores the generation it was filled
      at and drops on mismatch. This catches ``bpy.ops.bim.*`` mutations that
      edit the wall while the same selection is held (the case Blender's
      ``refresh()`` doesn't fire on)."""
    current_gen = tool.Parametric.get_geom_generation()
    cache_gen = getattr(group, "_wall_geom_cache_gen", None)
    cache = getattr(group, "_wall_geom_cache", None)
    if cache is None or cache_gen != current_gen:
        cache = {}
        group._wall_geom_cache = cache
        group._wall_geom_cache_gen = current_gen
    key = obj.name
    if key not in cache:
        cache[key] = tool.Wall.read_geometry(obj)
    return cache[key]


def _get_wall_connections_cached(
    group: "bpy.types.GizmoGroup",
    elem: ifcopenshell.entity_instance,
) -> "list[tuple[ifcopenshell.entity_instance, str, str]]":
    """Per-gizmo-group memoised ``_iter_path_connections``. Same generation-key
    invalidation as ``_get_wall_geom_cached`` so an IFC mutation drops the cached
    list on the next frame; ``refresh()`` drops it on selection change."""
    current_gen = tool.Parametric.get_geom_generation()
    cache_gen = getattr(group, "_wall_connections_cache_gen", None)
    cache = getattr(group, "_wall_connections_cache", None)
    if cache is None or cache_gen != current_gen:
        cache = {}
        group._wall_connections_cache = cache
        group._wall_connections_cache_gen = current_gen
    key = elem.GlobalId
    if key not in cache:
        cache[key] = _iter_path_connections(elem)
    return cache[key]


def _get_wall_pair_predicate_cached(group: "bpy.types.GizmoGroup", key: tuple, compute):
    """Per-gizmo-group memo for wall-pair predicates (joined / collinear /
    intersection). Caller supplies the cache key (typically pair GlobalIds +
    relevant inputs like matrix_world tuples + thresholds) and a zero-arg
    callable that computes the value on miss. Same generation invalidation as
    the geom cache; ``refresh()`` drops it on selection change."""
    current_gen = tool.Parametric.get_geom_generation()
    cache_gen = getattr(group, "_wall_pair_predicate_cache_gen", None)
    cache = getattr(group, "_wall_pair_predicate_cache", None)
    if cache is None or cache_gen != current_gen:
        cache = {}
        group._wall_pair_predicate_cache = cache
        group._wall_pair_predicate_cache_gen = current_gen
    if key not in cache:
        cache[key] = compute()
    return cache[key]


def _wall_camera_facing_icon_y(context: bpy.types.Context, mw: Matrix, geom: dict) -> float:
    """Wall-local Y for an icon that should sit just outside the camera-facing face.
    Centralised so the billboarding wall gizmos (add-opening, extend-vertically, …)
    share one source of truth for "where does the icon go on the visible side"."""
    viewing_from_negative_y, _ = gizmo.BaseParametricGizmoGroup.get_local_view_direction(context, mw)
    return gizmo.BaseParametricGizmoGroup.get_camera_facing_outer_y(
        viewing_from_negative_y,
        geom["offset"],
        geom["offset"] + geom["thickness"],
        gizmo.BaseParametricGizmoGroup.GIZMO_OFFSET,
    )


def _are_walls_joined(elem_a: ifcopenshell.entity_instance, elem_b: ifcopenshell.entity_instance) -> bool:
    """True if there's an ``IfcRelConnectsPathElements`` relating these two walls.

    Bonsai's wall joiner creates ``IfcRelConnectsPathElements`` (a specialization of
    ``IfcRelConnectsElements``) whenever walls share a corner or mitre. We walk both
    inverse arrays of the first wall and look for the second wall on the other side
    of any path-element rel."""
    for rel in getattr(elem_a, "ConnectedTo", []):
        if rel.is_a("IfcRelConnectsPathElements") and rel.RelatedElement == elem_b:
            return True
    for rel in getattr(elem_a, "ConnectedFrom", []):
        if rel.is_a("IfcRelConnectsPathElements") and rel.RelatingElement == elem_b:
            return True
    return False


def _are_walls_collinear(
    seg_a: tuple[Vector, Vector],
    seg_b: tuple[Vector, Vector],
    parallel_threshold: float = 0.9994,
    line_tolerance: float = 0.05,
) -> bool:
    """Vector wrapper around `core.are_axes_collinear` — converts Vector
    endpoints to plain tuples at the boundary so the math stays unit-testable in
    ``test/core/`` without a mathutils dependency."""
    return core.are_axes_collinear(
        (tuple(seg_a[0]), tuple(seg_a[1])),
        (tuple(seg_b[0]), tuple(seg_b[1])),
        parallel_threshold,
        line_tolerance,
    )


def _collinear_boundary_world(seg_a: tuple[Vector, Vector], seg_b: tuple[Vector, Vector]) -> Vector:
    """Vector wrapper around `core.closest_endpoint_midpoint`."""
    return Vector(
        core.closest_endpoint_midpoint(
            (tuple(seg_a[0]), tuple(seg_a[1])),
            (tuple(seg_b[0]), tuple(seg_b[1])),
        )
    )


def _classify_wall_join_state(
    elem_a: ifcopenshell.entity_instance,
    elem_b: ifcopenshell.entity_instance,
    seg_a: tuple[Vector, Vector],
    seg_b: tuple[Vector, Vector],
    parallel_threshold: float,
    collinear_tolerance: float,
) -> "tuple[core.WallJoinState, Optional[tuple[float, float, float]]]":
    """``(state, intersection)`` — intersection is non-``None`` only on
    the ``"intersect"`` branch."""
    return core.classify_wall_join_state(
        (tuple(seg_a[0]), tuple(seg_a[1])),
        (tuple(seg_b[0]), tuple(seg_b[1])),
        are_joined=_are_walls_joined(elem_a, elem_b),
        parallel_threshold=parallel_threshold,
        collinear_tolerance=collinear_tolerance,
    )


def _iter_path_connections(
    elem: ifcopenshell.entity_instance,
) -> list[tuple[ifcopenshell.entity_instance, str, str]]:
    """For each ``IfcRelConnectsPathElements`` involving ``elem``, yield
    ``(other_element, self_connection_type, other_connection_type)``.

    Walks both inverse arrays (``ConnectedTo`` + ``ConnectedFrom``) so the orientation
    of each rel is normalised to "self first". Non-wall partners are skipped — a wall
    MAY share a path connection with non-wall elements, but the unjoin gizmo only
    exposes wall-to-wall joins to match the existing two-wall gizmo's scope."""
    out: list[tuple[ifcopenshell.entity_instance, str, str]] = []
    for rel in getattr(elem, "ConnectedTo", []):
        if not rel.is_a("IfcRelConnectsPathElements"):
            continue
        other = rel.RelatedElement
        # Malformed / partial IFC files can leave a rel's element ref unset.
        # The partner predicate calls `.is_a(...)` on its argument, so a None
        # would raise mid-frame and silently break the gizmo group — guard
        # before the predicate runs.
        if other is None or not tool.Parametric.is_path_connectable_wall(other):
            continue
        out.append((other, rel.RelatingConnectionType, rel.RelatedConnectionType))
    for rel in getattr(elem, "ConnectedFrom", []):
        if not rel.is_a("IfcRelConnectsPathElements"):
            continue
        other = rel.RelatingElement
        if other is None or not tool.Parametric.is_path_connectable_wall(other):
            continue
        out.append((other, rel.RelatedConnectionType, rel.RelatingConnectionType))
    return out


def _wall_fillet_props(context: bpy.types.Context):
    return preview_base.get_preview_props(context, "wall_fillet")


_FILLET_SLOPE_TOLERANCE_RAD = 1e-4


def _walls_have_zero_slope_for_fillet(operator: bpy.types.Operator, *walls: bpy.types.Object) -> bool:
    """``True`` iff every input wall is vertical (``x_angle`` ~ 0). Reports an
    ERROR on the operator and returns ``False`` otherwise. Slanted-extrusion
    fillets require swept-along-curve geometry that the banana profile builder
    isn't designed for — block the entry points so the user sees a clear
    explanation instead of malformed corner geometry."""
    for wall in walls:
        if wall is None:
            continue
        element = tool.Ifc.get_entity(wall)
        if element is None:
            continue
        x_angle = tool.Wall.get_x_angle(element)
        if x_angle is None:
            continue
        if abs(x_angle) > _FILLET_SLOPE_TOLERANCE_RAD:
            operator.report(
                {"ERROR"},
                "Wall fillet is not supported for slanted walls (non-zero slope). "
                "Reset the wall's slope to vertical and try again.",
            )
            return False
    return True


def _build_curved_corner_body_representation(
    ifc_file: ifcopenshell.file,
    body_context: ifcopenshell.entity_instance,
    arc_center_local: tuple[float, float, float],
    chord_length_si: float,
    radius_si: float,
    r_outer_si: float,
    r_inner_si: float,
    height_si: float,
) -> ifcopenshell.entity_instance:
    """Build an ``IfcShapeRepresentation`` with a banana (annular sector)
    ``IfcExtrudedAreaSolid``.

    Local frame: origin at ``tangent_a``, +X along the chord to ``tangent_b``,
    +Z vertical. ``r_outer_si`` / ``r_inner_si`` come from wall A's
    ``IfcMaterialLayerSetUsage`` so the cross-section matches A at
    ``tangent_a`` rather than centring on the reference arc."""
    unit_scale = ifcopenshell.util.unit.calculate_unit_scale(ifc_file)

    cx_si, cy_si, _ = arc_center_local
    dir_a = (-cx_si / radius_si, -cy_si / radius_si)
    dir_b = ((chord_length_si - cx_si) / radius_si, -cy_si / radius_si)

    # Tessellate the banana profile as an IfcIndexedPolyCurve of straight
    # IfcLineIndex segments rather than analytical trimmed-circle arcs:
    # IfcOpenShell's geometry kernel and tool.Model.import_profile's edit-mode
    # importer both handle polyline segments unconditionally; trimmed-circle
    # alternatives fall through both paths to a coarse fallback or a hard error.
    # 24 chord segments per arc is visually smooth and round-trip-stable.
    arc_resolution = 24
    cross_z = dir_a[0] * dir_b[1] - dir_a[1] * dir_b[0]
    theta_a = math.atan2(dir_a[1], dir_a[0])
    theta_b = math.atan2(dir_b[1], dir_b[0])
    # Take the SHORT angular sweep from theta_a to theta_b. CCW (positive
    # signed cross product) means walking in increasing-theta direction.
    sweep = theta_b - theta_a
    if cross_z >= 0:
        if sweep < 0:
            sweep += 2 * math.pi
    else:
        if sweep > 0:
            sweep -= 2 * math.pi

    def _arc_points(radius: float) -> list[tuple[float, float]]:
        out = []
        for i in range(arc_resolution + 1):
            theta = theta_a + sweep * (i / arc_resolution)
            out.append((cx_si + radius * math.cos(theta), cy_si + radius * math.sin(theta)))
        return out

    # Closed loop in counter-clockwise order: outer arc, radial step to inner
    # arc, inner arc walked backwards, radial step back to outer start. The
    # outer-to-inner and inner-to-outer steps are pure radial lines because
    # the arcs share their endpoint angles.
    outer_points = _arc_points(r_outer_si)
    inner_points_reversed = list(reversed(_arc_points(r_inner_si)))
    raw_points = outer_points + inner_points_reversed
    points_ifc = [(x / unit_scale, y / unit_scale) for x, y in raw_points]

    point_list = ifc_file.createIfcCartesianPointList2D(points_ifc)
    # Indices are 1-based per IFC schema. The curve auto-closes by referencing
    # the first point as the next-segment start; the explicit closing segment
    # survives writers that don't honour implicit close.
    n = len(points_ifc)
    segments = [ifc_file.createIfcLineIndex((i + 1, ((i + 1) % n) + 1)) for i in range(n)]
    curve = ifc_file.createIfcIndexedPolyCurve(point_list, segments, False)
    profile = ifc_file.createIfcArbitraryClosedProfileDef("AREA", None, curve)

    extrusion = ifc_file.createIfcExtrudedAreaSolid(
        profile,
        ifc_file.createIfcAxis2Placement3D(
            ifc_file.createIfcCartesianPoint((0.0, 0.0, 0.0)),
            ifc_file.createIfcDirection((0.0, 0.0, 1.0)),
            ifc_file.createIfcDirection((1.0, 0.0, 0.0)),
        ),
        ifc_file.createIfcDirection((0.0, 0.0, 1.0)),
        height_si / unit_scale,
    )
    return ifc_file.createIfcShapeRepresentation(
        body_context, body_context.ContextIdentifier, "SweptSolid", [extrusion]
    )


def _apply_fillet_corner_geometry(
    ifc_file: ifcopenshell.file,
    corner_obj: bpy.types.Object,
    geom: dict,
    wall_a_obj: bpy.types.Object,
) -> tuple[Vector, Vector, Vector, float] | None:
    """Position the corner wall at ``tangent_a`` and rebuild its banana body
    from ``geom``. Shared by the creation and regenerate paths so a
    neighbour-driven recalc matches creation-time output even when wall A's
    layer set has been edited since.

    Returns ``(x_dir, y_dir, z_dir, chord_length_si)`` on success or ``None``
    on degenerate chord / missing Body context. All probes run before any
    mutation, so failures leave the corner wall untouched."""
    tangent_a = Vector(geom["tangent_a"])
    tangent_b = Vector(geom["tangent_b"])
    chord = tangent_b - tangent_a
    chord_length_si = chord.length
    if chord_length_si < 1e-6:
        return None
    body_context = ifcopenshell.util.representation.get_context(ifc_file, "Model", "Body", "MODEL_VIEW")
    if body_context is None:
        return None

    # Project the chord to the XY plane for the local-frame X axis. The
    # corner wall's Z axis is hardcoded to world Z below, so an XY-aligned
    # X axis is required for an orthonormal rotation matrix. Without the
    # projection, any chord Z component (walls placed at different
    # elevations) leaves x_dir non-orthogonal to z_dir and Blender's
    # Euler decomposition surfaces the skew as spurious sub-degree X/Y
    # rotations on the corner.
    chord_xy = Vector((chord.x, chord.y, 0.0))
    if chord_xy.length < 1e-6:
        return None
    x_dir = chord_xy.normalized()
    z_dir = Vector((0.0, 0.0, 1.0))
    y_dir = z_dir.cross(x_dir).normalized()
    corner_obj.matrix_world = Matrix(
        (
            (x_dir.x, y_dir.x, z_dir.x, tangent_a.x),
            (x_dir.y, y_dir.y, z_dir.y, tangent_a.y),
            (x_dir.z, y_dir.z, z_dir.z, tangent_a.z),
            (0.0, 0.0, 0.0, 1.0),
        )
    )
    bonsai.core.geometry.edit_object_placement(
        tool.Ifc, tool.Geometry, tool.Surveyor, obj=corner_obj, apply_scale=False
    )

    arc_center_world = Vector(geom["arc_center"])
    v_world = arc_center_world - tangent_a
    arc_center_local = (v_world.dot(x_dir), v_world.dot(y_dir), v_world.dot(z_dir))

    # Banana cross-section side: ``side_sign`` picks whether the body endpoints
    # extend toward the arc center (s = -1) or away from it (s = +1), so the
    # cross-section at tangent_a matches wall A's body span instead of being
    # centred on the reference arc.
    radial_a_world = tangent_a - arc_center_world
    if radial_a_world.length > 1e-6:
        radial_a_world = radial_a_world.normalized()
        wall_a_y_world = wall_a_obj.matrix_world.col[1].to_3d().normalized()
        side_sign = 1.0 if wall_a_y_world.dot(radial_a_world) >= 0.0 else -1.0
    else:
        side_sign = -1.0

    # ``arc_radius`` is signed (negative = inverted fillet); banana radii use
    # the magnitude — the sign only flips which side of A's reference line
    # the arc center sits on, not the curve radii themselves.
    radius_si = abs(geom["arc_radius"])
    offset_si = geom["profile_offset"] or 0.0
    thickness_si = geom["profile_thickness"]
    r_endpoint_1 = abs(radius_si + side_sign * offset_si)
    r_endpoint_2 = abs(radius_si + side_sign * (offset_si + thickness_si))
    r_outer_si = max(r_endpoint_1, r_endpoint_2)
    r_inner_si = min(r_endpoint_1, r_endpoint_2)

    new_body = _build_curved_corner_body_representation(
        ifc_file,
        body_context,
        arc_center_local=arc_center_local,
        chord_length_si=chord_length_si,
        radius_si=radius_si,
        r_outer_si=r_outer_si,
        r_inner_si=r_inner_si,
        height_si=geom["height"] or 3.0,
    )
    tool.Model.replace_object_ifc_representation(body_context, corner_obj, new_body)
    return x_dir, y_dir, z_dir, chord_length_si


def _resolve_two_walls(context: bpy.types.Context) -> tuple[bpy.types.Object, bpy.types.Object] | None:
    """``(active, other)`` from a 2-wall selection, both LAYER2 with straight axes."""
    selected = list(tool.Blender.get_selected_objects())
    if len(selected) != 2:
        return None
    active = context.active_object
    if active is None or active not in selected:
        return None
    other = next((o for o in selected if o is not active), None)
    if other is None:
        return None
    for obj in (active, other):
        element = tool.Ifc.get_entity(obj)
        if element is None or not element.is_a("IfcWall"):
            return None
        if not tool.Wall.has_layer2_usage(element):
            return None
        if not tool.Wall.is_straight_axis(element):
            return None
        if tool.Parametric.is_fillet_corner_wall(element):
            # Re-filleting a curved corner would treat its chord as the
            # reference line and produce nonsense geometry.
            return None
    return active, other


def _pick_dominant_wall_material(
    element: ifcopenshell.entity_instance,
) -> Optional[ifcopenshell.entity_instance]:
    """Return a single ``IfcMaterial`` representative of ``element``'s effective
    material — the thickest layer's material when the element resolves to a
    layer set / usage, the material itself when it is already plain, or
    ``None`` for unsupported set kinds and elements with no material."""
    material = tool.Material.get_material(element, should_inherit=True)
    if material is None:
        return None
    if material.is_a("IfcMaterial"):
        return material
    layer_set = None
    if material.is_a("IfcMaterialLayerSetUsage"):
        layer_set = material.ForLayerSet
    elif material.is_a("IfcMaterialLayerSet"):
        layer_set = material
    if layer_set is None:
        return None
    layers_with_material = [layer for layer in (layer_set.MaterialLayers or ()) if layer.Material is not None]
    if not layers_with_material:
        return None
    thickest = max(layers_with_material, key=lambda layer: layer.LayerThickness or 0.0)
    return thickest.Material


def regenerate_fillet_corner_wall(element: ifcopenshell.entity_instance, obj: bpy.types.Object) -> None:
    """Rebuild a fillet corner wall's banana body from ``BBIM_Wall.FilletRadius``
    and its neighbours' current layer parameters."""
    ifc_file = tool.Ifc.get()
    if ifc_file is None:
        return
    radius_si = ifcopenshell.util.element.get_pset(element, "BBIM_Wall", "FilletRadius")
    if not radius_si:
        return

    # Find the two neighbor walls from IfcRelConnectsPathElements. The corner-
    # side connection type is NOTDEFINED so neighbours don't miter against the
    # chord-axis reference line — take the single rel on each side of the
    # corner's inverse graph rather than filtering on type.
    wall_a = None
    for rel in getattr(element, "ConnectedFrom", []):
        if rel.is_a("IfcRelConnectsPathElements"):
            wall_a = rel.RelatingElement
            break
    wall_b = None
    for rel in getattr(element, "ConnectedTo", []):
        if rel.is_a("IfcRelConnectsPathElements"):
            wall_b = rel.RelatedElement
            break
    if wall_a is None or wall_b is None:
        return
    wall_a_obj = tool.Ifc.get_object(wall_a)
    wall_b_obj = tool.Ifc.get_object(wall_b)
    if wall_a_obj is None or wall_b_obj is None:
        return

    geom = tool.Wall.compute_wall_fillet_geometry(wall_a_obj, wall_b_obj, float(radius_si))
    if geom is None or not geom["valid"]:
        return

    # Re-anchors the corner's ObjectPlacement at the new tangent_a and rebuilds
    # the banana body. If a neighbour moved, the new placement follows; if
    # neither moved, the new matrix equals the old within floating-point noise.
    _apply_fillet_corner_geometry(ifc_file, obj, geom, wall_a_obj)
    # The body rebuild swaps the wall's representation, so any prior underside
    # clip is gone. Re-clip from the surviving TOP rels so an extend-to-slab
    # applied to a fillet wall isn't silently wiped on the next neighbour
    # recalc, ChangeExtrusionDepth, or split / merge call site.
    if tool.Model.has_underside_connection(element):
        core.regenerate_wall_to_underside(tool.Ifc, tool.Geometry, tool.Model, [obj])


class EnableWallFilletPreview(bpy.types.Operator):
    """Enter wall-fillet preview mode for two selected walls. No IFC
    mutation until finish."""

    bl_idname = "bim.enable_wall_fillet_preview"
    bl_label = "Enter Wall Fillet Preview"
    bl_description = "Begin tuning the fillet radius before committing the rounded corner"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if _resolve_two_walls(context) is None:
            cls.poll_message_set("Select exactly 2 LAYER2 walls with straight axes.")
            return False
        return True

    def execute(self, context):
        walls = _resolve_two_walls(context)
        if walls is None:
            self.report({"ERROR"}, "Selection no longer eligible for fillet preview.")
            return {"CANCELLED"}
        wall_a, wall_b = walls

        elem_a = tool.Ifc.get_entity(wall_a)
        elem_b = tool.Ifc.get_entity(wall_b)

        if not _walls_have_zero_slope_for_fillet(self, wall_a, wall_b):
            return {"CANCELLED"}

        # Joined / intersecting only; parallel pairs have no corner to round.
        seg_a = tool.Wall.get_world_reference_line(wall_a)
        seg_b = tool.Wall.get_world_reference_line(wall_b)
        if seg_a is None or seg_b is None:
            self.report({"ERROR"}, "Could not read reference line on one of the walls.")
            return {"CANCELLED"}
        are_joined = _are_walls_joined(elem_a, elem_b)
        state, _ = core.classify_wall_join_state(
            (tuple(seg_a[0]), tuple(seg_a[1])),
            (tuple(seg_b[0]), tuple(seg_b[1])),
            are_joined,
            core.PARALLEL_DOT_THRESHOLD,
            core.COLLINEAR_LINE_TOLERANCE,
        )
        if state not in {"intersect", "joined"}:
            self.report({"ERROR"}, f"Fillet requires intersecting or joined walls (state was {state}).")
            return {"CANCELLED"}

        preview_base.sync_uncommitted_moves([wall_a, wall_b])

        props = _wall_fillet_props(context)
        if props is None:
            self.report({"ERROR"}, "Wall fillet preview state is unavailable.")
            return {"CANCELLED"}

        # Auto-cancel any prior preview before opening a fresh one — fillet
        # creates a new IFC entity at finish.
        if props.is_active:
            bpy.ops.bim.cancel_wall_fillet_preview()

        # Default radius: a fraction of the shorter available leg, clamped
        # against the tangent-overshoot upper bound.
        geom = tool.Wall.compute_wall_fillet_geometry(wall_a, wall_b, radius=_FILLET_DEFAULT_RADIUS_M)
        default_radius = _FILLET_DEFAULT_RADIUS_M
        if geom is not None and geom.get("sweep_angle") and geom["sweep_angle"] > 1e-3:
            leg_a_available = geom.get("leg_a_available") or 0.0
            leg_b_available = geom.get("leg_b_available") or 0.0
            shortest_leg = min(leg_a_available, leg_b_available)
            if shortest_leg > 1e-6:
                upper = shortest_leg / max(math.tan(geom["sweep_angle"] / 2), 1e-6)
                default_radius = max(
                    _FILLET_MIN_RADIUS_M,
                    min(_FILLET_DEFAULT_LEG_FRACTION * shortest_leg, upper, _FILLET_DEFAULT_RADIUS_M),
                )

        props.wall_a_id = elem_a.id()
        props.wall_b_id = elem_b.id()
        props.radius = default_radius
        props.editing_corner_id = 0
        props.is_active = True
        return {"FINISHED"}


class FinishWallFilletPreview(bpy.types.Operator):
    """Commit the previewed fillet with the tuned radius and exit preview.

    Preview state survives a failed commit so the user can re-tune without
    re-selecting."""

    bl_idname = "bim.finish_wall_fillet_preview"
    bl_label = "Apply Wall Fillet"
    bl_description = "Commit the rounded corner with the previewed radius"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        return preview_base.commit_preview(
            self,
            context,
            "wall_fillet",
            "create_wall_fillet",
            ("wall_a_id", "wall_b_id", "radius", "editing_corner_id"),
        )


class CancelWallFilletPreview(bpy.types.Operator):
    """Exit wall-fillet preview without committing."""

    bl_idname = "bim.cancel_wall_fillet_preview"
    bl_label = "Cancel Wall Fillet"
    bl_description = "Discard the previewed fillet"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        if context.screen is None:
            return {"CANCELLED"}
        props = preview_base.get_preview_props(context, "wall_fillet")
        if props is None or not props.is_active:
            return {"CANCELLED"}
        # Clear the corner's edit flag so the connection disconnect gizmos
        # disappear in lockstep with the radius preview when the user
        # cancels. The id read happens BEFORE clear_preview_state wipes it.
        corner_id = props.editing_corner_id
        if corner_id:
            ifc_file = tool.Ifc.get()
            if ifc_file is not None:
                try:
                    corner_obj = tool.Ifc.get_object(ifc_file.by_id(corner_id))
                except RuntimeError:
                    corner_obj = None
                if corner_obj is not None:
                    tool.Model.get_wall_props(corner_obj).is_editing = False
        preview_base.clear_preview_state(props)
        return {"FINISHED"}


class EnableWallFilletPreviewFromCorner(bpy.types.Operator):
    """Re-open the fillet preview on an existing corner wall (pen-icon entry).

    Validate deletes and recreates the corner inside a single undo step."""

    bl_idname = "bim.enable_wall_fillet_preview_from_corner"
    bl_label = "Edit Wall Fillet"
    bl_description = "Open the fillet preview for an existing rounded corner — drag radius to retune"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        selected = list(tool.Blender.get_selected_objects())
        if len(selected) != 1:
            return False
        element = tool.Ifc.get_entity(selected[0])
        return element is not None and tool.Parametric.is_fillet_corner_wall(element)

    def execute(self, context: bpy.types.Context):
        selected = list(tool.Blender.get_selected_objects())
        if len(selected) != 1:
            self.report({"ERROR"}, "Select exactly one fillet corner wall.")
            return {"CANCELLED"}
        corner_obj = selected[0]
        corner_elem = tool.Ifc.get_entity(corner_obj)
        if corner_elem is None or not tool.Parametric.is_fillet_corner_wall(corner_elem):
            self.report({"ERROR"}, "Selection is not a fillet corner wall.")
            return {"CANCELLED"}

        radius = ifcopenshell.util.element.get_pset(corner_elem, "BBIM_Wall", "FilletRadius")
        if not radius:
            self.report({"ERROR"}, "Corner wall has no FilletRadius pset to re-edit.")
            return {"CANCELLED"}

        # The corner's own side of the rel is NOTDEFINED (see regenerate_
        # fillet_corner_wall) so neighbours don't miter against the chord axis
        # — read the single rel on each side of the inverse graph rather than
        # filtering on connection type.
        wall_a = None
        for rel in getattr(corner_elem, "ConnectedFrom", []):
            if rel.is_a("IfcRelConnectsPathElements"):
                wall_a = rel.RelatingElement
                break
        wall_b = None
        for rel in getattr(corner_elem, "ConnectedTo", []):
            if rel.is_a("IfcRelConnectsPathElements"):
                wall_b = rel.RelatedElement
                break
        if wall_a is None or wall_b is None:
            self.report({"ERROR"}, "Corner wall is not connected to both source walls anymore.")
            return {"CANCELLED"}

        wall_a_obj = tool.Ifc.get_object(wall_a)
        wall_b_obj = tool.Ifc.get_object(wall_b)
        if not _walls_have_zero_slope_for_fillet(self, wall_a_obj, wall_b_obj):
            return {"CANCELLED"}

        props = _wall_fillet_props(context)
        if props is None:
            self.report({"ERROR"}, "Wall fillet preview state is unavailable.")
            return {"CANCELLED"}
        if props.is_active:
            bpy.ops.bim.cancel_wall_fillet_preview()

        props.wall_a_id = wall_a.id()
        props.wall_b_id = wall_b.id()
        props.radius = float(radius)
        props.editing_corner_id = corner_elem.id()
        props.is_active = True
        # Flag the corner as "in edit mode" so the wall-side connection
        # disconnect gizmos surface in parallel with the fillet preview —
        # one pen-icon click enters BOTH radius retune AND connection
        # inspection.
        tool.Model.get_wall_props(corner_obj).is_editing = True
        return {"FINISHED"}


class CreateWallFillet(bpy.types.Operator, tool.Ifc.Operator):
    """Replace the corner between two straight walls with a curved LAYER2
    corner wall (banana body, inherits layer set / height / x_angle / type
    from wall A)."""

    bl_idname = "bim.create_wall_fillet"
    bl_label = "Create Wall Fillet"
    bl_description = "Replace the corner between two walls with a rounded corner of the given radius"
    bl_options = {"REGISTER", "UNDO"}

    wall_a_id: bpy.props.IntProperty(name="Wall A (active) IFC id")
    wall_b_id: bpy.props.IntProperty(name="Wall B (other) IFC id")
    radius: bpy.props.FloatProperty(
        name="Radius",
        default=0.5,
        subtype="DISTANCE",
        unit="LENGTH",
        description=(
            "Signed radius — positive produces a convex outward fillet, "
            "negative flips the arc center to the opposite side for an "
            "inverted (concave inward) corner."
        ),
    )
    editing_corner_id: bpy.props.IntProperty(
        name="Existing fillet corner IFC id",
        default=0,
        description=(
            "Non-zero on the pen-icon re-edit flow. The operator deletes this "
            "corner + its path connections before recreating with the new radius."
        ),
    )

    if TYPE_CHECKING:
        wall_a_id: int
        wall_b_id: int
        radius: float
        editing_corner_id: int

    def _execute(self, context):
        ifc_file = tool.Ifc.get()
        if ifc_file is None:
            self.report({"ERROR"}, "No IFC file loaded.")
            return {"CANCELLED"}

        try:
            elem_a = ifc_file.by_id(self.wall_a_id)
            elem_b = ifc_file.by_id(self.wall_b_id)
        except Exception:
            self.report({"ERROR"}, "One of the source walls is no longer in the IFC file.")
            return {"CANCELLED"}

        wall_a_obj = tool.Ifc.get_object(elem_a)
        wall_b_obj = tool.Ifc.get_object(elem_b)
        if wall_a_obj is None or wall_b_obj is None:
            self.report({"ERROR"}, "One of the source walls has no Blender object.")
            return {"CANCELLED"}

        if not _walls_have_zero_slope_for_fillet(self, wall_a_obj, wall_b_obj):
            return {"CANCELLED"}

        geom = tool.Wall.compute_wall_fillet_geometry(wall_a_obj, wall_b_obj, self.radius)
        if geom is None or not geom["valid"]:
            reason = geom.get("reason") if geom else "unknown"
            self.report({"ERROR"}, f"Fillet geometry rejected (reason: {reason}).")
            return {"CANCELLED"}
        if geom["wall_type_id"] is None:
            self.report({"ERROR"}, "Active wall has no IfcWallType to inherit.")
            return {"CANCELLED"}

        tangent_a = Vector(geom["tangent_a"])
        tangent_b = Vector(geom["tangent_b"])
        side_a = geom["wall_a_join_side"]
        side_b = geom["wall_b_join_side"]
        chord = tangent_b - tangent_a
        chord_length = chord.length
        if chord_length < 1e-6:
            self.report({"ERROR"}, "Tangent points coincide — invalid fillet geometry.")
            return {"CANCELLED"}

        # Pen-icon re-edit path: remove the existing fillet corner + its two
        # path connections to A and B before recreating. The deletion +
        # recreation runs in the same tool.Ifc.Operator transaction, so a
        # single undo restores the pre-re-edit state.
        if self.editing_corner_id:
            try:
                old_corner = ifc_file.by_id(self.editing_corner_id)
            except Exception:
                old_corner = None
            if old_corner is not None:
                for rel in list(getattr(old_corner, "ConnectedFrom", [])) + list(
                    getattr(old_corner, "ConnectedTo", [])
                ):
                    if rel.is_a("IfcRelConnectsPathElements"):
                        bonsai.core.geometry.remove_connection(tool.Geometry, connection=rel)
                old_corner_obj = tool.Ifc.get_object(old_corner)
                ifcopenshell.api.root.remove_product(ifc_file, product=old_corner)
                if old_corner_obj is not None:
                    bpy.data.objects.remove(old_corner_obj)

        # Drop any existing direct connection between A and B before
        # retopologising — the corner wall will own the new connections at
        # both ends.
        for conn in list(elem_a.ConnectedTo) + list(elem_a.ConnectedFrom):
            if not conn.is_a("IfcRelConnectsPathElements"):
                continue
            other = conn.RelatedElement if conn.RelatingElement == elem_a else conn.RelatingElement
            if other == elem_b:
                bonsai.core.geometry.remove_connection(tool.Geometry, connection=conn)

        # Shorten A and B so their corner-side endpoints sit on the tangent
        # points. DumbWallJoiner.extend projects the world-space target onto
        # the wall's local axis and rewrites the relevant endpoint, then
        # regenerates the body so it matches the new axis.
        joiner = DumbWallJoiner()
        joiner.extend(wall_a_obj, tangent_a, connection=side_a)
        joiner.extend(wall_b_obj, tangent_b, connection=side_b)

        # Instantiate the corner wall from A's wall type so it inherits the
        # material layer set, height, x_angle, and IfcWallType.
        bpy.ops.bim.add_occurrence(relating_type_id=geom["wall_type_id"])
        corner_obj = bpy.context.active_object
        if corner_obj is None:
            self.report({"ERROR"}, "Failed to instantiate the corner wall.")
            return {"CANCELLED"}
        corner_elem = tool.Ifc.get_entity(corner_obj)
        if corner_elem is None:
            self.report({"ERROR"}, "Corner wall has no IFC entity after creation.")
            return {"CANCELLED"}

        # IfcMaterialLayerSetUsage on a wall contracts that the body is
        # derived from the Axis swept along the layer-set thicknesses;
        # spec-honouring importers discard an explicit body when they see a
        # usage. The corner's defining geometry IS the explicit banana body,
        # so neither the usage form nor the owning IfcWallType may stay
        # associated. A plain IfcMaterial carries no swept-layer contract —
        # the corner inherits a single material from the dominant (thickest)
        # layer of wall A's effective material set for QTO / colour /
        # reporting purposes without putting the explicit body at risk.
        ifcopenshell.api.material.unassign_material(ifc_file, products=[corner_elem])
        ifcopenshell.api.type.unassign_type(ifc_file, related_objects=[corner_elem])

        dominant_material = _pick_dominant_wall_material(elem_a)
        if dominant_material is not None:
            ifcopenshell.api.material.assign_material(
                ifc_file,
                products=[corner_elem],
                type="IfcMaterial",
                material=dominant_material,
            )

        placement = _apply_fillet_corner_geometry(ifc_file, corner_obj, geom, wall_a_obj)
        if placement is None:
            self.report({"ERROR"}, "Could not apply fillet corner geometry (degenerate chord or missing body context).")
            return {"CANCELLED"}
        _, _, _, chord_length_si = placement

        # Axis: 2-point straight chord polyline from (0,0) to (chord_length,0)
        # in wall-local IFC units. The body curves while the axis stays
        # straight — IFC viewers and downstream Bonsai code that read the
        # reference line via get_reference_line get a usable 2-point result
        # instead of partial samples off a 3-point arc.
        unit_scale = ifcopenshell.util.unit.calculate_unit_scale(ifc_file)
        joiner.set_axis(
            corner_elem,
            Vector((0.0, 0.0)),
            Vector((chord_length_si / unit_scale, 0.0)),
        )

        # Mark the corner wall BEFORE the downstream recalculate so
        # tool.Model.recreate_wall short-circuits and preserves the curved
        # geometry. The pset also gates the enable poll. FilletRadius is
        # stored alongside IsFilletCorner so the corner can be rebuilt later
        # (neighbour move, layer-thickness edit, pen-icon re-edit).
        pset = ifcopenshell.api.pset.add_pset(ifc_file, product=corner_elem, name="BBIM_Wall")
        ifcopenshell.api.pset.edit_pset(
            ifc_file,
            pset=pset,
            properties={"IsFilletCorner": True, "FilletRadius": float(self.radius)},
        )

        # Connect A and B to the corner with the corner's OWN side typed as
        # NOTDEFINED rather than ATSTART/ATEND. regenerate_wall_representation
        # .join() early-returns when either side is NOTDEFINED, so neighbour
        # A's miter cut never reads the corner's chord-axis reference line.
        # A and B end FLAT at tangent_a / tangent_b — which is perpendicular
        # to their own axis AND to the curve's tangent direction at that
        # point, so the neighbour cross-sections align exactly with the
        # banana profile's cap.
        ifcopenshell.api.geometry.connect_path(
            ifc_file,
            relating_element=elem_a,
            related_element=corner_elem,
            relating_connection=side_a,
            related_connection="NOTDEFINED",
        )
        ifcopenshell.api.geometry.connect_path(
            ifc_file,
            relating_element=corner_elem,
            related_element=elem_b,
            relating_connection="NOTDEFINED",
            related_connection=side_b,
        )

        # Recalculate A and B so their miter cuts pick up the new connections
        # to the corner. The corner itself is skipped by tool.Model.
        # recreate_wall's IsFilletCorner gate, preserving the curved body.
        tool.Model.recalculate_walls([wall_a_obj, corner_obj, wall_b_obj])
        _resync_walls_after_mutation([wall_a_obj, corner_obj, wall_b_obj])
        return {"FINISHED"}


def _wall_fillet_gizmo_x_matrix(location: Vector, x_direction: Vector) -> Matrix:
    """4×4 matrix placing a gizmo at ``location`` with local +X aligned to
    ``x_direction`` in world space."""
    x = x_direction.normalized()
    seed = Vector((0, 0, 1)) if abs(x.z) < 0.9 else Vector((1, 0, 0))
    y = (seed - x * seed.dot(x)).normalized()
    z = x.cross(y)
    mat = Matrix.Identity(4)
    mat[0][:3] = (x.x, y.x, z.x)
    mat[1][:3] = (x.y, y.y, z.y)
    mat[2][:3] = (x.z, y.z, z.z)
    mat.translation = location
    return mat


def _wall_fillet_preview_walls(context: bpy.types.Context):
    """``(wall_a_obj, wall_b_obj)`` pinned by the preview, or ``(None, None)``
    when inactive or stale."""
    props = _wall_fillet_props(context)
    if props is None or not props.is_active:
        return None, None
    ifc_file = tool.Ifc.get()
    if ifc_file is None:
        return None, None
    try:
        elem_a = ifc_file.by_id(props.wall_a_id)
        elem_b = ifc_file.by_id(props.wall_b_id)
    except (RuntimeError, KeyError):
        return None, None
    wall_a_obj = tool.Ifc.get_object(elem_a) if elem_a else None
    wall_b_obj = tool.Ifc.get_object(elem_b) if elem_b else None
    return wall_a_obj, wall_b_obj


class GizmoWallExtendVertically(bpy.types.GizmoGroup, _WallGeomCachedBillboardingMixin):
    """Activates when a LAYER3 element (typically a slab) is active and a LAYER2
    wall is co-selected. Mirrors the N-panel ``Extend To Underside`` button (which
    shows under the same active-LAYER3 + LAYER2-in-selection rule). Clicking
    dispatches ``bim.extend_walls_to_underside``, which extends the wall up to the
    active element's bottom faces.

    Anchored at the wall's local X = 0 (wall origin endpoint), wall-local Y on the
    camera-facing side, and the world Z of the active object — so the icon visually
    sits at the elevation the wall will reach after extending."""

    bl_idname = "OBJECT_GGT_bim_wall_extend_vertically"
    bl_label = "Wall Extend Vertically Gizmo"
    bl_space_type = "VIEW_3D"
    bl_region_type = "WINDOW"
    bl_options = {"3D", "PERSISTENT"}

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        if not _wall_topology_gizmo_poll_gate(context):
            return False
        selected = tool.Blender.get_selected_objects()
        if len(selected) != 2:
            return False
        active = context.active_object
        if active is None or active not in selected:
            return False
        active_element = tool.Ifc.get_entity(active)
        if not active_element or tool.Model.get_usage_type(active_element) != "LAYER3":
            return False
        other = next(o for o in selected if o is not active)
        other_element = tool.Ifc.get_entity(other)
        if not other_element or not tool.Parametric.is_path_connectable_wall(other_element):
            return False
        return True

    def setup(self, context: bpy.types.Context) -> None:
        default_color, highlight_color = self.get_decoration_colors()
        self.extend_vertical_icon = self.setup_icon_gizmo(
            "VIEW3D_GT_extend_vertical",
            default_color,
            highlight_color,
            "bim.extend_walls_to_underside",
        )

    def position_gizmos(self, context: bpy.types.Context) -> None:
        active = context.active_object
        if active is None:
            return
        wall_obj = next((o for o in tool.Blender.get_selected_objects() if o is not active), None)
        if wall_obj is None:
            return
        geom = _get_wall_geom_cached(self, wall_obj)
        if not geom:
            return
        mw = wall_obj.matrix_world
        icon_y = _wall_camera_facing_icon_y(context, mw, geom)
        # X = 0 in wall-local, Y on the camera-facing outer side, world Z lifted to
        # the active object's elevation — the height the wall is about to reach.
        world_pos = mw @ Vector((0.0, icon_y, 0.0))
        world_pos.z = active.matrix_world.translation.z
        billboard_rot = gizmo.get_billboard_rotation(context)
        world_pos += gizmo.top_down_clearance(context, billboard_rot)
        self.extend_vertical_icon.matrix_basis = gizmo.billboarded_at(world_pos, billboard_rot)


class GizmoWallJoinIntersection(bpy.types.GizmoGroup, _WallGeomCachedBillboardingMixin):
    """Activates when exactly two LAYER2 walls are selected. Dispatches between four
    state-specific icons based on the geometric + IFC relationship of the walls:

    - **Joined** (``IfcRelConnectsPathElements`` between them):
      ``unjoin_icon`` (``VIEW3D_GT_split``, outward arrows) at the shared corner.
      Clicking dispatches ``bim.unjoin_walls``.
    - **Collinear** (axes on the same infinite line, not joined):
      ``merge_icon`` (``VIEW3D_GT_merge``, inward arrows) at the midpoint of the
      closest endpoint pair. Clicking dispatches ``bim.merge_wall``.
    - **Joinable corner** (non-parallel, axes meet near endpoints, not joined):
      ``join_icon`` (``VIEW3D_GT_merge``) at the projected intersection on the
      floor, PLUS ``extend_to_wall_icon`` (``VIEW3D_GT_extend``) at the
      intersection at the active wall's Z=height. The Z difference disambiguates
      "join the corner" vs "extend this wall into the other."
    - **None of the above**: all icons hidden.

    Per-frame positioning via `BillboardingGizmoGroupMixin` ensures the icons
    keep facing the camera as the viewport is orbited."""

    bl_idname = "OBJECT_GGT_bim_wall_join_intersection"
    bl_label = "Wall Join Intersection Gizmo"
    bl_space_type = "VIEW_3D"
    bl_region_type = "WINDOW"
    bl_options = {"3D", "PERSISTENT"}

    # Hide the gizmo when walls are nearly parallel (intersection would be unreasonably far).
    # cos(2°) ≈ 0.9994 → walls within ~2° of parallel are treated as parallel for this purpose.
    PARALLEL_DOT_THRESHOLD = 0.9994
    # Perpendicular tolerance (m) for treating two parallel wall axes as collinear.
    COLLINEAR_LINE_TOLERANCE = 0.05

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        if not _wall_topology_gizmo_poll_gate(context):
            return False
        selected = tool.Blender.get_selected_objects()
        if len(selected) != 2:
            return False
        for o in selected:
            element = tool.Ifc.get_entity(o)
            if not element or not tool.Parametric.is_wall(element):
                return False
        return True

    # Screen-space vertical offset between stacked icons in a state branch —
    # camera's screen-up so the fillet icon sits visibly clear of the
    # join/unjoin icon at any view angle.
    ICON_STACK_OFFSET_Y: ClassVar[float] = 0.4

    # Per-region weakref map populated in ``setup()``. The wall-join preview
    # decorator dereferences this each draw to read live ``is_highlight``
    # state off the join / extend-to-wall / fillet icons in the same region
    # it's currently drawing in, so the preview lines can switch to
    # ``decorator_color_selected`` while the user hovers a target.
    _active_instances: ClassVar["dict[int, weakref.ReferenceType[GizmoWallJoinIntersection]]"] = {}

    def setup(self, context: bpy.types.Context) -> None:
        default_color, highlight_color = self.get_decoration_colors()
        self.unjoin_icon = self.setup_icon_gizmo("VIEW3D_GT_split", default_color, highlight_color, "bim.unjoin_walls")
        self.merge_icon = self.setup_icon_gizmo("VIEW3D_GT_merge", default_color, highlight_color, "bim.merge_wall")
        # L-corner glyph reads as "join at the corner"; differentiated from
        # the T glyph (extend) by where the bars meet (corner vs midline).
        self.join_icon = self.setup_icon_gizmo(
            "VIEW3D_GT_wall_corner", default_color, highlight_color, "bim.join_walls_intersection"
        )
        # T-junction glyph reads as "extend this wall into the other's side".
        self.extend_to_wall_icon = self.setup_icon_gizmo(
            "VIEW3D_GT_wall_tee", default_color, highlight_color, "bim.extend_walls_to_wall"
        )
        # Fillet entry — shows in the same two states (joined / intersect)
        # where rounding the corner is well-defined. Click enters the preview
        # flow; GizmoWallFilletPreview takes over from there.
        self.fillet_icon = self.setup_icon_gizmo(
            "VIEW3D_GT_fillet", default_color, highlight_color, "bim.enable_wall_fillet_preview"
        )
        if context.region is not None:
            type(self)._active_instances[context.region.as_pointer()] = weakref.ref(self)

    def _all_icons(self) -> tuple[bpy.types.Gizmo, ...]:
        return (self.unjoin_icon, self.merge_icon, self.join_icon, self.extend_to_wall_icon, self.fillet_icon)

    def _hide_all(self) -> None:
        for icon in self._all_icons():
            icon.hide = True

    def position_gizmos(self, context: bpy.types.Context) -> None:
        selected = list(tool.Blender.get_selected_objects())
        if len(selected) != 2:
            self._hide_all()
            return
        elem_a = tool.Ifc.get_entity(selected[0])
        elem_b = tool.Ifc.get_entity(selected[1])
        geom_a = _get_wall_geom_cached(self, selected[0])
        geom_b = _get_wall_geom_cached(self, selected[1])
        if elem_a is None or elem_b is None or geom_a is None or geom_b is None:
            self._hide_all()
            return
        seg_a = _wall_axis_world_segment_from_geom(selected[0], geom_a)
        seg_b = _wall_axis_world_segment_from_geom(selected[1], geom_b)
        billboard_rot = gizmo.get_billboard_rotation(context)
        screen_up = gizmo.get_screen_up(billboard_rot)
        clearance = gizmo.top_down_clearance(context, billboard_rot)
        anchor_z = self._stack_anchor_z(context, selected, geom_a, geom_b)

        # Pair predicate cache key: pair GlobalIds + world-matrix tuples for
        # both walls. World matrices feed _are_walls_collinear /
        # project_axis_intersection, so they belong in the key.
        pair_guids = tuple(sorted((elem_a.GlobalId, elem_b.GlobalId)))
        mw_a_key = tuple(map(tuple, selected[0].matrix_world))
        mw_b_key = tuple(map(tuple, selected[1].matrix_world))
        mw_key = (mw_a_key, mw_b_key) if elem_a.GlobalId <= elem_b.GlobalId else (mw_b_key, mw_a_key)

        # State 1: walls are already joined → Unjoin (bottom) + Fillet (above).
        joined = _get_wall_pair_predicate_cached(
            self, ("joined", pair_guids), lambda: _are_walls_joined(elem_a, elem_b)
        )
        if joined:
            corner = _collinear_boundary_world(seg_a, seg_b)
            anchor = Vector((corner.x, corner.y, anchor_z)) + clearance
            self._stack_at(anchor, screen_up, billboard_rot, (self.unjoin_icon, self.fillet_icon))
            self.merge_icon.hide = True
            self.join_icon.hide = True
            self.extend_to_wall_icon.hide = True
            return

        # State 2: walls are collinear (parallel axes on the same line) → show Merge
        # at the boundary midpoint between them. No stack; single icon at the
        # geometric boundary makes the merge target unambiguous.
        collinear = _get_wall_pair_predicate_cached(
            self,
            ("collinear", pair_guids, mw_key, self.PARALLEL_DOT_THRESHOLD, self.COLLINEAR_LINE_TOLERANCE),
            lambda: _are_walls_collinear(seg_a, seg_b, self.PARALLEL_DOT_THRESHOLD, self.COLLINEAR_LINE_TOLERANCE),
        )
        if collinear:
            boundary = _collinear_boundary_world(seg_a, seg_b) + clearance
            self.merge_icon.matrix_basis = gizmo.billboarded_at(boundary, billboard_rot)
            self.merge_icon.hide = False
            self.unjoin_icon.hide = True
            self.join_icon.hide = True
            self.extend_to_wall_icon.hide = True
            self.fillet_icon.hide = True
            return

        # State 3: non-parallel walls → Join (L, bottom) + Extend-to-Wall (T)
        # + Fillet (top) stacked along screen-up at the wall-top anchor.
        # PARALLEL_DOT_THRESHOLD (cos 2°) is the only bound that matters:
        # walls within 2° of parallel produce extrusion joints that race
        # toward infinity, so project_axis_intersection returns None and the
        # early-return below hides the whole group.
        intersection_tuple = _get_wall_pair_predicate_cached(
            self,
            ("intersection", pair_guids, mw_key, self.PARALLEL_DOT_THRESHOLD),
            lambda: core.project_axis_intersection(
                (tuple(seg_a[0]), tuple(seg_a[1])),
                (tuple(seg_b[0]), tuple(seg_b[1])),
                self.PARALLEL_DOT_THRESHOLD,
            ),
        )
        if intersection_tuple is None:
            self._hide_all()
            return
        intersection = Vector(intersection_tuple)
        anchor = Vector((intersection.x, intersection.y, anchor_z)) + clearance
        self._stack_at(anchor, screen_up, billboard_rot, (self.extend_to_wall_icon, self.join_icon, self.fillet_icon))
        self.unjoin_icon.hide = True
        self.merge_icon.hide = True

    def _stack_anchor_z(
        self,
        context: bpy.types.Context,
        selected: list[bpy.types.Object],
        geom_a: dict,
        geom_b: dict,
    ) -> float:
        # Wall-top Z is the bottom of the screen-up stack — high enough that
        # the icons sit on top of the wall instead of clipping into it.
        # Prefer the active wall's top (the height the user is operating on);
        # fall back to the taller of the two if the active object isn't one
        # of the selected walls (mid-selection-transition frame).
        active = context.active_object if context.active_object in selected else None
        if active is selected[0]:
            return active.matrix_world.translation.z + geom_a["height"]
        if active is selected[1]:
            return active.matrix_world.translation.z + geom_b["height"]
        return max(
            selected[0].matrix_world.translation.z + geom_a["height"],
            selected[1].matrix_world.translation.z + geom_b["height"],
        )

    def _stack_at(
        self,
        anchor: Vector,
        screen_up: Vector,
        billboard_rot: Matrix,
        icons: tuple[bpy.types.Gizmo, ...],
    ) -> None:
        for k, icon in enumerate(icons):
            icon.matrix_basis = gizmo.billboarded_at(anchor + screen_up * (self.ICON_STACK_OFFSET_Y * k), billboard_rot)
            icon.hide = False


class GizmoWallLinkToggle(gizmo.GizmoLinkToggle, bpy.types.Gizmo):
    """Link-toggle glyph with a partner-wall highlight on hover. The owning
    gizmo group writes the partner Blender object onto each icon every frame
    via ``partner_obj``; on ``is_highlight`` the partner's bbox is outlined
    inline so the user sees which wall the click will disconnect from
    before committing.

    The partner reference is stashed on the gizmo instance rather than
    read back from the bound operator handle because Blender's Gizmo API
    exposes ``target_set_operator`` for binding but no symmetric getter."""

    bl_idname = "VIEW3D_GT_wall_link_toggle"
    __slots__ = ("partner_obj",)

    def setup(self) -> None:
        super().setup()
        self.partner_obj = None

    def draw(self, context: bpy.types.Context) -> None:
        super().draw(context)
        if not self.is_highlight:
            return
        partner = self.partner_obj
        if partner is None:
            return
        draw_wall_partner_bbox(context, partner)


class GizmoWallUnjoinSingle(bpy.types.GizmoGroup, _WallGeomCachedBillboardingMixin):
    """Activates when exactly one LAYER2 wall is selected. Surfaces an unjoin icon at
    every connection location on the wall — wall-wall path connections via
    IfcRelConnectsPathElements + wall-slab underside clips via IfcRelConnectsElements
    with Description=="TOP". A wall may participate in many such rels (up to 1 ATSTART
    + 1 ATEND by end, plus unlimited ATPATH T-junctions, plus one rel per clipped
    slab), so a pool of icons is preallocated and hidden on a per-frame basis based
    on the live connection set.

    Each visible icon dispatches `bim.disconnect_elements` with the active wall +
    partner element GlobalIds set on the bound operator properties, so a click
    removes only the single rel under that icon — the other connections on the
    same wall survive.

    Mutually exclusive with `GizmoWallJoinIntersection` via `poll()` (that group
    requires len(selected) == 2; this one requires 1)."""

    bl_idname = "OBJECT_GGT_bim_wall_unjoin_single"
    bl_label = "Wall Unjoin (single selection) Gizmo"
    bl_space_type = "VIEW_3D"
    bl_region_type = "WINDOW"
    bl_options = {"3D", "PERSISTENT"}

    # Pool size. ATSTART + ATEND + ATPATH connections are rarely more than a handful
    # on real models; 16 is generous enough that excess is exceptional. Excess drops
    # a one-time console warning. The cap exists because Blender only permits
    # GizmoGroup to allocate gizmos inside setup() — draw_prepare / refresh-time
    # creation is forbidden — so the pool must be sized upfront for the worst case.
    POOL_SIZE = 16
    ICON_SCALE = 0.35
    SLAB_STACK_MAX = 5
    SLAB_STACK_OFFSET_Z = 0.5
    # Muted gray used for connection icons that are visible (the connection
    # exists) but inert (clicking dispatches a no-op + INFO report). Fillet
    # corner ↔ source-wall joins use this — disconnecting them would tear
    # down the fillet's chord axis reference, so the supported teardown is
    # deleting the corner wall instead.
    LOCKED_COLOR: ClassVar[tuple[float, float, float]] = (0.5, 0.5, 0.5)

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        # Bypass the shared topology gate's ``any_preview_active`` block —
        # ``BIMWallProperties.is_editing`` is the real gate for this gizmo
        # group, and that flag is set both by the regular wall edit lifecycle
        # AND by the fillet preview entry (so a fillet corner under preview
        # surfaces its connections in parallel with the radius drag).
        if not tool.Blender.are_viewport_gizmos_enabled():
            return False
        if tool.Blender.Modifier.any_selected_is_array_child():
            return False
        active = tool.Blender.get_active_object(is_selected=True)
        if active is None:
            return False
        selected = tool.Blender.get_selected_objects()
        if len(selected) != 1:
            return False
        element = tool.Ifc.get_entity(active)
        if not element or not tool.Parametric.is_path_connectable_wall(element):
            return False
        props = tool.Model.get_wall_props(active)
        if not props.is_editing:
            return False
        return True

    def setup(self, context: bpy.types.Context) -> None:
        default_color, highlight_color = self.get_decoration_colors()
        # Stashed so per-frame ``_bind_unjoin_icon`` can restore the active
        # tone when an icon was muted in a previous frame for fillet lock.
        self._default_unjoin_color = default_color
        # Bind the operator on each pool icon ONCE at setup time and keep the returned
        # OperatorProperties handles. target_set_operator allocates a fresh handle on
        # every call, so calling it from position_gizmos (which fires every redraw
        # frame via draw_prepare) would discard and re-allocate ~60Hz per visible
        # icon. Stashing the handles lets per-frame work be a plain property write.
        self.unjoin_icons = []
        self.unjoin_op_props = []
        for _ in range(self.POOL_SIZE):
            icon = self.setup_icon_gizmo(
                "VIEW3D_GT_wall_link_toggle", default_color, highlight_color, "bim.disconnect_elements"
            )
            icon.hide = True
            self.unjoin_icons.append(icon)
            self.unjoin_op_props.append(icon.target_set_operator("bim.disconnect_elements"))

    def position_gizmos(self, context: bpy.types.Context) -> None:
        # Default: hide every pool slot. The visible-set is rebuilt from the live
        # connection list each frame so disconnects/reconnects elsewhere in the
        # session don't leave ghost icons behind.
        for icon in self.unjoin_icons:
            icon.hide = True

        selected = list(tool.Blender.get_selected_objects())
        if len(selected) != 1:
            return
        wall_obj = selected[0]
        elem = tool.Ifc.get_entity(wall_obj)
        geom = _get_wall_geom_cached(self, wall_obj)
        if elem is None or geom is None:
            return
        seg_self = _wall_axis_world_segment_from_geom(wall_obj, geom)
        billboard_rot = gizmo.get_billboard_rotation(context)
        clearance = gizmo.top_down_clearance(context, billboard_rot)

        path_connections = _get_wall_connections_cached(self, elem)
        slab_connections = list(tool.Wall.iter_wall_slab_connections(elem))
        slab_overflow = max(0, len(slab_connections) - self.SLAB_STACK_MAX)
        if slab_overflow and not getattr(self, "_slab_cap_warned", False):
            print(
                f"[bonsai] GizmoWallUnjoinSingle: wall has {len(slab_connections)} slab "
                f"connections; only the first {self.SLAB_STACK_MAX} are shown stacked."
            )
            self._slab_cap_warned = True
        slab_connections = slab_connections[: self.SLAB_STACK_MAX]
        total = len(path_connections) + len(slab_connections)
        if total > self.POOL_SIZE and not getattr(self, "_pool_cap_warned", False):
            print(
                f"[bonsai] GizmoWallUnjoinSingle: wall has {total} connections "
                f"({len(path_connections)} path + {len(slab_connections)} slab); "
                f"only the first {self.POOL_SIZE} unjoin gizmos are shown."
            )
            self._pool_cap_warned = True

        slot_idx = 0
        self_is_fillet = tool.Parametric.is_fillet_corner_wall(elem)
        for other_elem, self_ct, other_ct in path_connections:
            if slot_idx >= self.POOL_SIZE:
                break
            other_obj = tool.Ifc.get_object(other_elem)
            if other_obj is None:
                continue
            other_geom = _get_wall_geom_cached(self, other_obj)
            if other_geom is None:
                continue
            seg_other = _wall_axis_world_segment_from_geom(other_obj, other_geom)
            location = tool.Wall.path_connection_location_world(seg_self, self_ct, seg_other, other_ct)
            is_locked = self_is_fillet or tool.Parametric.is_fillet_corner_wall(other_elem)
            self._bind_unjoin_icon(
                slot_idx, location + clearance, billboard_rot, elem, other_elem, other_obj, is_locked=is_locked
            )
            slot_idx += 1

        for stack_idx, (slab_elem, _rel) in enumerate(slab_connections):
            if slot_idx >= self.POOL_SIZE:
                break
            slab_obj = tool.Ifc.get_object(slab_elem)
            if slab_obj is None:
                continue
            location = tool.Wall.wall_slab_connection_location_world(wall_obj, slab_obj)
            if location is None:
                continue
            # Stack vertically so each slab gets a distinct clickable icon;
            # hover-highlight then shows the user which slab they're about to
            # disconnect from.
            stacked = location + Vector((0.0, 0.0, stack_idx * self.SLAB_STACK_OFFSET_Z))
            self._bind_unjoin_icon(slot_idx, stacked + clearance, billboard_rot, elem, slab_elem, slab_obj)
            slot_idx += 1

    def _bind_unjoin_icon(
        self, slot_idx, location, billboard_rot, active_elem, partner_elem, partner_obj, *, is_locked=False
    ):
        """Place + bind one pool icon to a (active, partner) GlobalId pair.

        Only the GlobalId properties are rewritten per frame; the operator
        binding itself is the long-lived handle set up at setup() time. GlobalId
        (not Blender object name) keeps the binding stable across renames, file
        save/reload, and any sit-in-the-undo-stack interlude between dispatch
        and execute. The partner Blender object is mirrored onto the icon for
        its hover-outline draw, since the Gizmo API exposes
        ``target_set_operator`` but no symmetric reader.

        ``is_locked=True`` (fillet corner involvement) writes a muted color
        instead of the active tone; the GUIDs still propagate so the bound
        operator can surface a friendly INFO report on click."""
        icon = self.unjoin_icons[slot_idx]
        icon.matrix_basis = gizmo.billboarded_at(location, billboard_rot, scale=self.ICON_SCALE)
        icon.hide = False
        icon.color = self.LOCKED_COLOR if is_locked else self._default_unjoin_color
        self.unjoin_op_props[slot_idx].element_a_guid = active_elem.GlobalId
        self.unjoin_op_props[slot_idx].element_b_guid = partner_elem.GlobalId
        icon.partner_obj = partner_obj


class GizmoSlabUnjoinWalls(bpy.types.GizmoGroup, gizmo.BillboardingGizmoGroupMixin):
    """Slab-side mirror of GizmoWallUnjoinSingle: when exactly one IfcSlab is
    selected and at least one wall is clipped to its underside, surface an
    unjoin icon at each connection point. The icons resolve at the same
    world location as the wall-side gizmo (via the symmetric
    tool.Wall.wall_slab_connection_location_world) so the same connection
    has a single visual marker reachable from either selection.

    Each visible icon dispatches bim.disconnect_elements with the slab +
    wall GlobalIds, so a click removes the single rel under that icon and
    re-clips the wall to whatever remaining slabs it's connected to."""

    bl_idname = "OBJECT_GGT_bim_slab_unjoin_walls"
    bl_label = "Slab Unjoin Walls Gizmo"
    bl_space_type = "VIEW_3D"
    bl_region_type = "WINDOW"
    bl_options = {"3D", "PERSISTENT"}

    POOL_SIZE = 16
    ICON_SCALE = 0.35

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        return _slab_connection_gizmo_poll_gate(context, require_editing=True)

    def setup(self, context: bpy.types.Context) -> None:
        default_color, highlight_color = self.get_decoration_colors()
        self.unjoin_icons = []
        self.unjoin_op_props = []
        for _ in range(self.POOL_SIZE):
            icon = self.setup_icon_gizmo(
                "VIEW3D_GT_wall_link_toggle", default_color, highlight_color, "bim.disconnect_elements"
            )
            icon.hide = True
            self.unjoin_icons.append(icon)
            self.unjoin_op_props.append(icon.target_set_operator("bim.disconnect_elements"))

    def position_gizmos(self, context: bpy.types.Context) -> None:
        for icon in self.unjoin_icons:
            icon.hide = True

        selected = list(tool.Blender.get_selected_objects())
        if len(selected) != 1:
            return
        slab_obj = selected[0]
        slab_elem = tool.Ifc.get_entity(slab_obj)
        if slab_elem is None:
            return

        billboard_rot = gizmo.get_billboard_rotation(context)
        clearance = gizmo.top_down_clearance(context, billboard_rot)
        connections = list(tool.Wall.iter_slab_wall_connections(slab_elem))
        if len(connections) > self.POOL_SIZE and not getattr(self, "_pool_cap_warned", False):
            print(
                f"[bonsai] GizmoSlabUnjoinWalls: slab has {len(connections)} wall connections; "
                f"only the first {self.POOL_SIZE} unjoin gizmos are shown."
            )
            self._pool_cap_warned = True

        slot_idx = 0
        for wall_elem, _rel in connections:
            if slot_idx >= self.POOL_SIZE:
                break
            wall_obj = tool.Ifc.get_object(wall_elem)
            if wall_obj is None:
                continue
            location = tool.Wall.wall_slab_connection_location_world(wall_obj, slab_obj)
            if location is None:
                continue
            icon = self.unjoin_icons[slot_idx]
            icon.matrix_basis = gizmo.billboarded_at(location + clearance, billboard_rot, scale=self.ICON_SCALE)
            icon.hide = False
            self.unjoin_op_props[slot_idx].element_a_guid = slab_elem.GlobalId
            self.unjoin_op_props[slot_idx].element_b_guid = wall_elem.GlobalId
            icon.partner_obj = wall_obj
            slot_idx += 1


class GizmoSlabEdition(bpy.types.GizmoGroup, gizmo.BaseParametricGizmoGroup):
    """Pen / validate / cancel triad for slab disconnect-access mode.

    Polls on a single IfcSlab with at least one wall clipped to its underside.
    Pen routes through the universal ``bim.enable_editing_parametric``
    dispatcher; finish + cancel both clear ``is_editing`` (no IFC mutation —
    the framework requires the triad to exist by name convention even for a
    pure UI gate). ESC, the red-coloured cancel icon, mutual exclusion with
    other active parametric edits, gizmo prefs gating — all handled by the
    base class."""

    bl_idname = "OBJECT_GGT_bim_slab_edition"
    bl_label = "Slab Editing Gizmo"
    bl_space_type = "VIEW_3D"
    bl_region_type = "WINDOW"
    bl_options = {"3D", "PERSISTENT"}

    enable_editing_operator = "bim.enable_editing_slab"
    finish_editing_operator = "bim.finish_editing_slab"
    cancel_editing_operator = "bim.cancel_editing_slab"
    cycle_type_operator = ""

    props_getter = tool.Model.get_slab_props
    gizmo_pref_name = "slab"

    @classmethod
    def is_element_type(cls, element: ifcopenshell.entity_instance) -> bool:
        return tool.Parametric.is_slab(element) and any(tool.Wall.iter_slab_wall_connections(element))


class GizmoPairDisconnect(bpy.types.GizmoGroup, gizmo.BillboardingGizmoGroupMixin):
    """Surfaces a disconnect icon when exactly 2 IFC elements are selected
    and they share a supported rel — currently the wall + slab pair joined
    by an ``IfcRelConnectsElements(TOP)``. Click dispatches
    ``bim.disconnect_elements`` with both GlobalIds. For wall-wall pairs,
    ``GizmoWallJoinIntersection``'s unjoin icon already exposes the same
    affordance via ``bim.unjoin_walls``."""

    bl_idname = "OBJECT_GGT_bim_pair_disconnect"
    bl_label = "Disconnect Pair Gizmo"
    bl_space_type = "VIEW_3D"
    bl_region_type = "WINDOW"
    bl_options = {"3D", "PERSISTENT"}

    ICON_SCALE = 0.35

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        selected = list(tool.Blender.get_selected_objects())
        if len(selected) != 2:
            return False
        if tool.Blender.Modifier.any_selected_is_array_child():
            return False
        elem_a = tool.Ifc.get_entity(selected[0])
        elem_b = tool.Ifc.get_entity(selected[1])
        if elem_a is None or elem_b is None:
            return False
        rels = tool.Connection.find_rels(elem_a, elem_b)
        return any(kind == "element-top" for _, kind in rels)

    def setup(self, context: bpy.types.Context) -> None:
        default_color, highlight_color = self.get_decoration_colors()
        self.disconnect_icon = self.setup_icon_gizmo(
            "VIEW3D_GT_wall_link_toggle", default_color, highlight_color, "bim.disconnect_elements"
        )
        self.disconnect_icon.hide = True
        self.disconnect_op = self.disconnect_icon.target_set_operator("bim.disconnect_elements")

    def position_gizmos(self, context: bpy.types.Context) -> None:
        self.disconnect_icon.hide = True
        pair = _resolve_active_partner_pair(context)
        if pair is None:
            return
        active, partner_obj, active_elem, partner_elem = pair
        # Helper expects wall + slab regardless of which the user marked active.
        if active_elem.is_a("IfcWall"):
            wall_obj, slab_obj = active, partner_obj
        elif partner_elem.is_a("IfcWall"):
            wall_obj, slab_obj = partner_obj, active
        else:
            return
        location = tool.Wall.wall_slab_connection_location_world(wall_obj, slab_obj)
        if location is None:
            return
        billboard_rot = gizmo.get_billboard_rotation(context)
        clearance = gizmo.top_down_clearance(context, billboard_rot)
        self.disconnect_icon.matrix_basis = gizmo.billboarded_at(
            location + clearance, billboard_rot, scale=self.ICON_SCALE
        )
        self.disconnect_icon.hide = False
        self.disconnect_op.element_a_guid = active_elem.GlobalId
        self.disconnect_op.element_b_guid = partner_elem.GlobalId
        self.disconnect_icon.partner_obj = partner_obj


class GizmoWallFilletPreview(bpy.types.GizmoGroup, gizmo.BillboardingGizmoGroupMixin):
    """Gizmo group for the wall-fillet preview: radius dimension widget +
    trim-length dimension widget + validate / cancel icons.

    On degenerate geometry the dimensions and validate hide but cancel stays
    visible so the user always has an exit. Radius and trim widgets express
    the same single DOF — both read/write the canonical `props.radius`."""

    bl_idname = "OBJECT_GGT_bim_wall_fillet_preview"
    bl_label = "Wall Fillet Preview Gizmos"
    bl_space_type = "VIEW_3D"
    bl_region_type = "WINDOW"
    bl_options = {"3D", "PERSISTENT"}

    ICON_SCALE: ClassVar[float] = 0.375
    ICON_SPACING_X: ClassVar[float] = 0.4
    ICON_Z_OFFSET: ClassVar[float] = 1.5

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        props = _wall_fillet_props(context)
        if props is None or not props.is_active:
            return False
        if not tool.Blender.are_viewport_gizmos_enabled():
            return False
        ifc_file = tool.Ifc.get()
        if ifc_file is None:
            return False
        try:
            ifc_file.by_id(props.wall_a_id)
            ifc_file.by_id(props.wall_b_id)
        except (RuntimeError, KeyError):
            return False
        return True

    def setup(self, context: bpy.types.Context) -> None:
        default_color, highlight_color = self.get_decoration_colors()

        # Lazy-fetched closures re-resolve the Scene per call so the freed-RNA
        # crash on file open / undo doesn't hit the gizmo callbacks.
        _props_callback = preview_base.make_props_callback("wall_fillet")

        gz = self.gizmos.new("BIM_GT_gizmo_dimension")
        gz.move_get_cb = preview_base.make_dim_getter(_props_callback, "radius")
        gz.move_set_cb = preview_base.make_dim_setter(_props_callback, "radius")
        # Set `axis` only (NOT `local_axis`) so `get_axis_direction` falls
        # through to the world-space direction set per frame on each gizmo.
        # The preview spans world space independent of either wall's local
        # frame, so the active-object transform that `local_axis` would go
        # through is the wrong frame.
        gz.axis = Vector((1, 0, 0))
        gz.invert_delta = False
        gz.delta_scale = 1.0
        gz.prop_name = "Radius"
        gz.gizmo_group = self
        gz.color = default_color
        gz.color_highlight = highlight_color
        gz.alpha = 1.0
        gz.use_draw_modal = True
        gz.use_draw_scale = False
        gz.text_offset_sign = 1
        gz.text_alignment = gizmo.TextAlignment.CENTER
        # Arrowheads at BOTH ends + extension lines make this read as a proper
        # dimension annotation rather than a single-direction drag arrow.
        gz.show_start_arrow = True
        gz.show_end_arrow = True
        gz.show_extension_lines = True
        gz.text_formatter = None
        self.radius_dim = gz

        # Sweep angle is geometrically invariant during drag (depends only on
        # the angle between the two walls). Cached per frame so the trim
        # getter / setter can convert trim_length ↔ radius via tan(sweep/2)
        # without re-running the full geometry pipeline on every drag tick.
        self._sweep_angle = math.pi / 2

        # Trim-length widget expresses the SAME single DOF as the radius
        # widget via the leg setback distance (intersection → tangent point).
        # Architects often think "how much of each wall do I cut back" rather
        # than "what radius do I want"; this widget surfaces that mental model
        # without introducing a second degree of freedom. Both widgets stay
        # in sync because they read/write the same canonical `radius` field.
        trim_gz = self.gizmos.new("BIM_GT_gizmo_dimension")
        trim_gz.move_get_cb = self._make_trim_getter()
        trim_gz.move_set_cb = self._make_trim_setter()
        trim_gz.axis = Vector((1, 0, 0))
        trim_gz.invert_delta = False
        trim_gz.delta_scale = 1.0
        trim_gz.prop_name = "Trim Length"
        trim_gz.gizmo_group = self
        trim_gz.color = default_color
        trim_gz.color_highlight = highlight_color
        trim_gz.alpha = 1.0
        trim_gz.use_draw_modal = True
        trim_gz.use_draw_scale = False
        trim_gz.text_offset_sign = 1
        trim_gz.text_alignment = gizmo.TextAlignment.CENTER
        trim_gz.show_start_arrow = True
        trim_gz.show_end_arrow = True
        trim_gz.show_extension_lines = True
        trim_gz.text_formatter = None
        self.trim_dim = trim_gz

        from bonsai.bim.module.drawing.gizmos import BaseParametricGizmoGroup

        self.validate_icon = self.gizmos.new("VIEW3D_GT_validate")
        self.validate_icon.use_draw_scale = False
        self.validate_icon.color = BaseParametricGizmoGroup.COLOR_GREEN
        self.validate_icon.color_highlight = highlight_color
        self.validate_icon.target_set_operator("bim.finish_wall_fillet_preview")

        self.cancel_icon = self.gizmos.new("VIEW3D_GT_cancel")
        self.cancel_icon.use_draw_scale = False
        self.cancel_icon.color = BaseParametricGizmoGroup.COLOR_RED
        self.cancel_icon.color_highlight = highlight_color
        self.cancel_icon.target_set_operator("bim.cancel_wall_fillet_preview")

    def _make_trim_getter(self):
        """Closure returning |radius| * tan(sweep/2) — the live leg setback
        distance — from the cached sweep angle and the canonical radius."""

        def _get() -> float:
            props = _wall_fillet_props(bpy.context)
            if props is None:
                return 0.0
            sweep = max(self._sweep_angle, 1e-3)
            return abs(float(props.radius)) * math.tan(sweep / 2.0)

        return _get

    def _make_trim_setter(self):
        """Closure writing radius from a dragged trim_length, preserving the
        radius sign so a concave preview stays concave when the user drags the
        trim widget. Clamps to the FloatProperty's lower bound so the gizmo
        can't push radius below the geometry helper's tolerance."""

        def _set(value: float) -> None:
            props = _wall_fillet_props(bpy.context)
            if props is None:
                return
            sweep = max(self._sweep_angle, 1e-3)
            tan_half = math.tan(sweep / 2.0)
            if tan_half < 1e-9:
                return
            sign = -1.0 if float(props.radius) < 0 else 1.0
            new_radius = sign * max(0.001, float(value)) / tan_half
            props.radius = new_radius
            for area in bpy.context.screen.areas if bpy.context.screen else ():
                if area.type == "VIEW_3D":
                    area.tag_redraw()

        return _set

    def position_gizmos(self, context: bpy.types.Context) -> None:
        wall_a_obj, wall_b_obj = _wall_fillet_preview_walls(context)
        if wall_a_obj is None or wall_b_obj is None:
            for gz in (self.radius_dim, self.trim_dim, self.validate_icon, self.cancel_icon):
                gz.hide = True
            return

        props = _wall_fillet_props(context)
        if props is None:
            for gz in (self.radius_dim, self.trim_dim, self.validate_icon, self.cancel_icon):
                gz.hide = True
            return

        geom = tool.Wall.compute_wall_fillet_geometry(wall_a_obj, wall_b_obj, props.radius)
        billboard_rot = gizmo.get_billboard_rotation(context)

        # Geometry helper failed outright (e.g. wall A's reference line went
        # missing). No anchor to draw on — hide everything.
        if geom is None:
            for gz in (self.radius_dim, self.trim_dim, self.validate_icon, self.cancel_icon):
                gz.hide = True
            return

        # Parallel / near-collinear axes — no defined arc at all. Drop radius
        # + trim + validate; keep cancel visible at the would-be intersection
        # so the user has an exit. The dim widgets have nowhere to anchor.
        if not geom["valid"] and not geom.get("invalid_radius"):
            self.radius_dim.hide = True
            self.trim_dim.hide = True
            self.validate_icon.hide = True
            anchor = None
            if geom.get("arc_center") is not None:
                anchor = Vector(geom["arc_center"])
            elif geom.get("intersection") is not None:
                anchor = Vector(geom["intersection"])
            if anchor is not None:
                # Same screen-up lift as the valid branch so the cancel icon
                # doesn't sit on top of any underlying preview lines in
                # top-down view.
                screen_up = gizmo.get_screen_up(billboard_rot)
                self.cancel_icon.matrix_basis = gizmo.billboarded_at(
                    anchor + screen_up * self.ICON_Z_OFFSET, billboard_rot, scale=self.ICON_SCALE
                )
                self.cancel_icon.hide = False
            else:
                self.cancel_icon.hide = True
            return

        # Both `valid=True` and `invalid_radius=True` populate arc_center,
        # apex, and tangent points. Keep the radius dim visible on overshoot
        # so the user can drag back to a valid radius; hide validate so a
        # commit can't surface an operator-level error.
        invalid_radius = bool(geom.get("invalid_radius"))
        self.radius_dim.hide = False
        self.trim_dim.hide = False
        self.cancel_icon.hide = False
        self.validate_icon.hide = invalid_radius

        # Cache the sweep angle so the trim widget's getter / setter can
        # convert without re-running the geometry pipeline. Falls back to a
        # right angle if the helper somehow omits it.
        self._sweep_angle = float(geom.get("sweep_angle") or math.pi / 2)

        arc = geom["arc"]
        arc_center = Vector(geom["arc_center"])
        tangent_a = Vector(geom["tangent_a"])
        tangent_b = Vector(geom["tangent_b"])
        intersection = Vector(geom["intersection"])

        # Radius dimension at the arc apex with local +X pointing INWARD
        # toward the arc center. Visual line traces apex → center, matching
        # the radius itself; drag in the +X direction (toward arrow tip =
        # toward arc center) increases the radius. Anchored at the FLOOR of
        # the wall (z=0 of the arc samples) so the gizmo reads against the
        # wall geometry rather than hovering in mid-air.
        apex_index = len(arc) // 2
        apex = Vector(arc[apex_index])
        inward = arc_center - apex
        if inward.length > 1e-6:
            inward.normalize()
            self.radius_dim.matrix_basis = _wall_fillet_gizmo_x_matrix(apex, inward)
            self.radius_dim.axis = inward
            self.radius_dim.set_dimension_length(abs(props.radius))
        else:
            self.radius_dim.hide = True

        # Trim dimension along wall A from intersection toward tangent_a;
        # same DOF as the radius widget, both update `radius`.
        along_a = tangent_a - intersection
        tangent_offset = abs(float(props.radius)) * math.tan(self._sweep_angle / 2.0)
        if along_a.length > 1e-6 and tangent_offset > 1e-6:
            along_a_dir = along_a.normalized()
            self.trim_dim.matrix_basis = _wall_fillet_gizmo_x_matrix(intersection, along_a_dir)
            self.trim_dim.axis = along_a_dir
            self.trim_dim.set_dimension_length(tangent_offset)
        else:
            self.trim_dim.hide = True

        # Validate / cancel anchored ABOVE the arc apex along the camera's
        # screen-up direction so they're always visibly clear of the radius
        # dim widget (which runs apex → arc_center). Screen-up keeps the
        # offset perpendicular to the view plane at any angle — world +Z
        # would collapse to zero on-screen in top-down view and plant the
        # icons on top of the radius arrowhead.
        screen_up = gizmo.get_screen_up(billboard_rot)
        anchor = apex + screen_up * self.ICON_Z_OFFSET
        offset_x = billboard_rot @ Vector((self.ICON_SPACING_X, 0.0, 0.0))
        self.validate_icon.matrix_basis = gizmo.billboarded_at(anchor, billboard_rot, scale=self.ICON_SCALE)
        self.cancel_icon.matrix_basis = gizmo.billboarded_at(anchor + offset_x, billboard_rot, scale=self.ICON_SCALE)


class GizmoWallFilletReedit(bpy.types.GizmoGroup, _WallGeomCachedBillboardingMixin):
    """Pen-icon re-edit gizmo for an existing fillet corner wall.

    Mutually exclusive with an active preview and with GizmoWallEdition."""

    bl_idname = "OBJECT_GGT_bim_wall_fillet_reedit"
    bl_label = "Wall Fillet Re-edit Gizmo"
    bl_space_type = "VIEW_3D"
    bl_region_type = "WINDOW"
    bl_options = {"3D", "PERSISTENT"}

    ICON_TOP_LIFT: ClassVar[float] = 0.15

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        if not _wall_topology_gizmo_poll_gate(context):
            return False
        active = tool.Blender.get_active_object(is_selected=True)
        if active is None:
            return False
        selected = list(tool.Blender.get_selected_objects())
        if len(selected) != 1:
            return False
        element = tool.Ifc.get_entity(active)
        if element is None or not element.is_a("IfcWall"):
            return False
        # IsFilletCorner pset is the authoritative signal — the re-edit
        # operator separately verifies both neighbour connections exist and
        # reports a user-facing error if either side has been disconnected
        # since creation. Validating that here would hide the pen icon
        # silently, leaving the user with no obvious next step.
        return tool.Parametric.is_fillet_corner_wall(element)

    def setup(self, context: bpy.types.Context) -> None:
        default_color, highlight_color = self.get_decoration_colors()
        self.edit_icon = self.setup_icon_gizmo(
            "VIEW3D_GT_pen",
            default_color,
            highlight_color,
            "bim.enable_wall_fillet_preview_from_corner",
        )

    def position_gizmos(self, context: bpy.types.Context) -> None:
        selected = list(tool.Blender.get_selected_objects())
        if len(selected) != 1:
            self.edit_icon.hide = True
            return
        corner_obj = selected[0]
        geom = _get_wall_geom_cached(self, corner_obj)
        if geom is None:
            self.edit_icon.hide = True
            return
        billboard_rot = gizmo.get_billboard_rotation(context)
        origin = corner_obj.matrix_world.translation
        top_z = origin.z + (geom.get("height") or 3.0) + self.ICON_TOP_LIFT
        anchor = Vector((origin.x, origin.y, top_z)) + gizmo.top_down_clearance(context, billboard_rot)
        self.edit_icon.matrix_basis = gizmo.billboarded_at(anchor, billboard_rot)
        self.edit_icon.hide = False


class GizmoWallFilletToggleOpenings(bpy.types.GizmoGroup, _WallGeomCachedBillboardingMixin):
    """Surfaces the show / hide openings icon on a fillet-corner wall.

    GizmoWallEdition's idle row already exposes this toggle for LAYER2 walls,
    but its poll routes through the parametric edit pipeline which by IFC
    spec rejects fillet corners (their banana body is hand-built and would be
    flattened by the parametric regen). The openings toggle itself is a
    viewport-state action independent of the body, so a parallel poll keeps
    it available without re-opening the parametric edits."""

    bl_idname = "OBJECT_GGT_bim_wall_fillet_toggle_openings"
    bl_label = "Fillet Wall Toggle Openings Gizmo"
    bl_space_type = "VIEW_3D"
    bl_region_type = "WINDOW"
    bl_options = {"3D", "PERSISTENT"}

    ICON_TOP_LIFT: ClassVar[float] = 0.15
    # Screen-space X offset from the pen icon so the two stack horizontally
    # rather than overlap at the chord midpoint.
    ICON_OFFSET_X: ClassVar[float] = 0.4

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        if not _wall_topology_gizmo_poll_gate(context):
            return False
        active = tool.Blender.get_active_object(is_selected=True)
        if active is None:
            return False
        if len(list(tool.Blender.get_selected_objects())) != 1:
            return False
        element = tool.Ifc.get_entity(active)
        if element is None or not element.is_a("IfcWall"):
            return False
        return tool.Parametric.is_fillet_corner_wall(element)

    def setup(self, context: bpy.types.Context) -> None:
        default_color, highlight_color = self.get_decoration_colors()
        self.toggle_openings_icon = self.setup_icon_gizmo(
            "VIEW3D_GT_add_opening",
            default_color,
            highlight_color,
            "bim.toggle_host_openings",
        )

    def position_gizmos(self, context: bpy.types.Context) -> None:
        selected = list(tool.Blender.get_selected_objects())
        if len(selected) != 1:
            self.toggle_openings_icon.hide = True
            return
        corner_obj = selected[0]
        geom = _get_wall_geom_cached(self, corner_obj)
        if geom is None:
            self.toggle_openings_icon.hide = True
            return
        billboard_rot = gizmo.get_billboard_rotation(context)
        origin = corner_obj.matrix_world.translation
        top_z = origin.z + (geom.get("height") or 3.0) + self.ICON_TOP_LIFT
        anchor = Vector((origin.x, origin.y, top_z)) + gizmo.top_down_clearance(context, billboard_rot)
        offset_x = billboard_rot @ Vector((self.ICON_OFFSET_X, 0.0, 0.0))
        self.toggle_openings_icon.matrix_basis = gizmo.billboarded_at(anchor + offset_x, billboard_rot)
        self.toggle_openings_icon.hide = False


class JoinWallsIntersection(_CommitWallDraftsFirstMixin, bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.join_walls_intersection"
    bl_label = "Join Walls at Corner"
    bl_description = "Join two walls at their corner"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if not tool.Model.has_selected_ifc_objects():
            cls.poll_message_set("No IFC objects selected.")
            return False
        if _poll_reject_array_children(cls):
            return False
        return True

    def _perform(self, context: bpy.types.Context) -> set[str]:
        try:
            core.join_walls_LV(tool.Ifc, tool.Blender, tool.Geometry, DumbWallJoiner(), tool.Model)
        except core.RequireTwoWallsError as e:
            self.report({"ERROR"}, str(e))
            return {"CANCELLED"}
        _resync_walls_after_mutation(tool.Blender.get_selected_objects())
        return {"FINISHED"}


def draw_wall_partner_bbox(
    context: bpy.types.Context,
    partner_obj: bpy.types.Object,
) -> None:
    """Paint a wireframe bbox around ``partner_obj`` in the same 3D pass.
    Called inline from gizmo ``draw()`` methods so the highlight tracks the
    hover cursor one-for-one — no POST_VIEW handler, no timing lag.

    Silently no-ops if the object has no bounding box (e.g. Empties)."""
    segments = bbox_world_edges(partner_obj)
    if not segments:
        return
    prefs = tool.Blender.get_addon_preferences()
    color = prefs.decorator_color_special[:3]
    draw_polyline_segments(
        context,
        segments,
        color,
        _BBOX_HIGHLIGHT_LINE_ALPHA,
        _BBOX_HIGHLIGHT_LINE_WIDTH,
    )


class WallGizmoPreviewDecorator(tool.Blender.ViewportDecorator):
    """Hover-gated preview lines that visualise where a click-to-act wall
    gizmo's operator would move the wall geometry. Four state machines:

    - **Join intersection** — when exactly two non-joined, non-collinear,
      non-parallel LAYER2 walls are selected, draws one line from each wall's
      nearest axis endpoint to the projected XY intersection. Each line stays
      at its own wall's axis Z (so for walls on different storeys the lines
      stay horizontal at their own floor levels). Mirrors the visibility of
      the Join + Extend-to-Wall icons in ``GizmoWallJoinIntersection``.
    - **Extend to cursor** — when a single LAYER2 wall is selected and the
      ``extend`` wall-gizmo pref is enabled, draws one line from the wall's
      nearer axis endpoint to the 3D cursor's projected X on the wall axis.
      Mirrors the visibility of the ``extend_x_gizmo`` icon in
      ``GizmoWallEdition``.
    - **Extend Z to cursor** — one preview line at the cursor's projected X
      from wall base to the cursor's Z, visualising the new total height.
      Hover-gated on ``extend_z_gizmo``.
    - **Split at cursor** — one world-vertical line at the cursor's projected X
      from wall base to wall top, visualising the cut plane. Hover-gated on
      ``split_gizmo``.

    Purely a visual cue — hidden by the same gizmo-preferences toggle as the
    icons themselves."""

    draw_method = "draw_lines"

    LINE_WIDTH = 1.5
    LINE_ALPHA = 0.8
    QUAD_ALPHA = 0.45

    def draw_lines(self, context: bpy.types.Context) -> None:
        if not tool.Blender.are_viewport_gizmos_enabled():
            return
        prefs = tool.Blender.get_addon_preferences()
        self._draw_join_preview(context, prefs)
        self._draw_cursor_extend_preview(context, prefs)
        self._draw_cursor_extend_z_preview(context, prefs)
        self._draw_cursor_split_preview(context, prefs)
        self._draw_cursor_perpendicular_wall_preview(context, prefs)

    def _stroke(
        self,
        context: bpy.types.Context,
        segments: list[tuple[tuple[float, float, float], tuple[float, float, float]]],
        color_rgb: tuple[float, float, float],
    ) -> None:
        draw_polyline_segments(context, segments, color_rgb, self.LINE_ALPHA, self.LINE_WIDTH)

    def _fill(
        self,
        context: bpy.types.Context,
        quads: list[
            tuple[
                tuple[float, float, float],
                tuple[float, float, float],
                tuple[float, float, float],
                tuple[float, float, float],
            ]
        ],
        color_rgb: tuple[float, float, float],
    ) -> None:
        tool.Blender.draw_quads(context, quads, fill_color=(*color_rgb, self.QUAD_ALPHA))

    @staticmethod
    def _wall_floor_quad(mw: Matrix, x0: float, x1: float, y0: float, y1: float) -> tuple[
        tuple[float, float, float],
        tuple[float, float, float],
        tuple[float, float, float],
        tuple[float, float, float],
    ]:
        """4 world-space corners of a Z=0 wall-local rectangle, CCW when
        viewed from +Z. Used for top-down floor-projection quads so the
        extend / split previews stay legible from plan view."""
        return (
            tuple(mw @ Vector((x0, y0, 0.0))),
            tuple(mw @ Vector((x1, y0, 0.0))),
            tuple(mw @ Vector((x1, y1, 0.0))),
            tuple(mw @ Vector((x0, y1, 0.0))),
        )

    def _draw_join_preview(self, context: bpy.types.Context, prefs: Any) -> None:
        """Render four preview lines per wall pair — two at each wall's base
        Z, two at each wall's top Z — extending each axis to the projected
        intersection. Two lines per wall (base + top) communicate the full
        plane that the join/extend operator would weld at, not just the
        floor edge.

        Hover colour:
        - **Join or Fillet hover** → all four lines light up (both walls
          converge at the corner; fillet is a symmetric round of the same
          corner).
        - **Extend-to-Wall hover** → only the base+top of the non-active
          wall (the wall the default-direction operator would extend).
        - Otherwise → ``decorations_colour``."""
        selected = list(tool.Blender.get_selected_objects())
        if len(selected) != 2:
            return
        elem_a = tool.Ifc.get_entity(selected[0])
        elem_b = tool.Ifc.get_entity(selected[1])
        if elem_a is None or elem_b is None:
            return
        if not tool.Parametric.is_path_connectable_wall(elem_a) or not tool.Parametric.is_path_connectable_wall(elem_b):
            return

        geom_a = tool.Wall.read_geometry(selected[0])
        geom_b = tool.Wall.read_geometry(selected[1])
        if geom_a is None or geom_b is None:
            return
        seg_a = _wall_axis_world_segment_from_geom(selected[0], geom_a)
        seg_b = _wall_axis_world_segment_from_geom(selected[1], geom_b)
        parallel_threshold = core.PARALLEL_DOT_THRESHOLD
        collinear_tolerance = core.COLLINEAR_LINE_TOLERANCE
        state, intersection_tuple = _classify_wall_join_state(
            elem_a, elem_b, seg_a, seg_b, parallel_threshold, collinear_tolerance
        )
        if state != "intersect":
            return
        assert intersection_tuple is not None
        floor_lines = core.wall_join_preview_lines(
            (tuple(seg_a[0]), tuple(seg_a[1])),
            (tuple(seg_b[0]), tuple(seg_b[1])),
            intersection_tuple,
        )
        height_a = geom_a.get("height", 0.0)
        height_b = geom_b.get("height", 0.0)
        wall_a_floor, wall_b_floor = floor_lines

        def _lift(seg: tuple, dz: float) -> tuple:
            (sx, sy, sz), (ex, ey, ez) = seg
            return ((sx, sy, sz + dz), (ex, ey, ez + dz))

        wall_a_top = _lift(wall_a_floor, height_a)
        wall_b_top = _lift(wall_b_floor, height_b)
        join_hovered, extend_hovered, fillet_hovered = self._join_group_hover_state(GizmoWallJoinIntersection, context)
        default = tuple(prefs.decorations_colour[:3])
        selected_rgb = tuple(prefs.decorator_color_selected[:3])
        all_lines = [wall_a_floor, wall_a_top, wall_b_floor, wall_b_top]

        if join_hovered or fillet_hovered:
            self._stroke(context, all_lines, selected_rgb)
            return

        if extend_hovered:
            extended_idx = self._extended_wall_index(context, selected)
            if extended_idx is not None:
                extended_lines = [wall_a_floor, wall_a_top] if extended_idx == 0 else [wall_b_floor, wall_b_top]
                untouched_lines = [wall_b_floor, wall_b_top] if extended_idx == 0 else [wall_a_floor, wall_a_top]
                self._stroke(context, untouched_lines, default)
                self._stroke(context, extended_lines, selected_rgb)
                return

        self._stroke(context, all_lines, default)

    @staticmethod
    def _extended_wall_index(context: bpy.types.Context, selected: list[bpy.types.Object]) -> Optional[int]:
        """Index of the non-active wall in ``selected``, or ``None``."""
        active = context.active_object
        if active is selected[0]:
            return 1
        if active is selected[1]:
            return 0
        return None

    def _join_group_hover_state(self, gizmo_cls: type, context: bpy.types.Context) -> tuple[bool, bool, bool]:
        """Return ``(join_hovered, extend_to_wall_hovered, fillet_hovered)``
        from the ``GizmoWallJoinIntersection`` instance in **the same region**
        the decorator is currently drawing in. Returns ``(False, False,
        False)`` when that region has no live gizmo group (poll → False,
        weakref cleared, or no setup yet). Read-only; any access exception
        is swallowed so a transient bpy-state hiccup never breaks the draw
        loop."""
        inst = self._lookup_active_instance(gizmo_cls, context)
        if inst is None:
            return False, False, False
        try:
            return (
                bool(inst.join_icon.is_highlight),
                bool(inst.extend_to_wall_icon.is_highlight),
                bool(inst.fillet_icon.is_highlight),
            )
        except (AttributeError, ReferenceError):
            return False, False, False

    def _active_layer2_wall_for_gizmo_preview(
        self, context: bpy.types.Context, prefs: Any
    ) -> Optional[bpy.types.Object]:
        """Active object iff it is the sole selected object, is a LAYER2 IfcWall,
        and the wall feature's gizmo prefs are enabled. Otherwise ``None``.
        Shared guard for every cursor-anchored extend-preview path so each one
        short-circuits on the same conditions the gizmo group itself uses."""
        gizmo_prefs = getattr(prefs.gizmos, "wall", None)
        if gizmo_prefs is None or not getattr(gizmo_prefs, "enabled", True):
            return None
        active = context.active_object
        if active is None:
            return None
        selected = list(tool.Blender.get_selected_objects())
        if active not in selected or len(selected) != 1:
            return None
        element = tool.Ifc.get_entity(active)
        if element is None or not tool.Parametric.is_wall(element):
            return None
        if tool.Model.get_usage_type(element) != "LAYER2":
            return None
        return active

    def _draw_cursor_extend_preview(self, context: bpy.types.Context, prefs: Any) -> None:
        """Hover-gated floor-plane preview for the extend-X icon. Quads sit
        on the Z=0 plane spanning the wall's ``offset`` to
        ``offset + thickness`` Y band so the operator's effect reads from
        plan view without side-view clutter:

        - **Cursor outside ``[anchor_x, anchor_x+length]`` (grow)**: one
          green ``decorator_color_selected`` quad over the extension
          (nearer endpoint → cursor X).
        - **Cursor inside the wall extent (shrink)**: green quad for the
          portion that REMAINS (cursor X → farther endpoint) + red
          ``decorator_color_error`` quad for the portion the operator
          REMOVES (nearer endpoint → cursor X)."""
        active = self._active_layer2_wall_for_gizmo_preview(context, prefs)
        if active is None:
            return
        if not self._cursor_icon_hovered(GizmoWallEdition, "extend_x_gizmo", context):
            return
        geom = tool.Wall.read_geometry(active)
        if geom is None:
            return
        anchor_x = geom.get("anchor_x", 0.0)
        length = geom.get("length", 0.0)
        offset = geom.get("offset", 0.0)
        thickness = geom.get("thickness", 0.0)
        if length <= 0 or thickness <= 0:
            return
        mw = active.matrix_world
        cursor_local = mw.inverted() @ context.scene.cursor.location
        y_floor_0 = offset
        y_floor_1 = offset + thickness
        start_x = anchor_x
        end_x = anchor_x + length
        keep_color = tuple(prefs.decorator_color_selected[:3])
        nearest_x = start_x if abs(cursor_local.x - start_x) < abs(cursor_local.x - end_x) else end_x

        def emit(x0: float, x1: float, color: tuple[float, float, float]) -> None:
            if abs(x1 - x0) < 1e-6:
                return
            lo, hi = (x0, x1) if x0 < x1 else (x1, x0)
            self._fill(context, [self._wall_floor_quad(mw, lo, hi, y_floor_0, y_floor_1)], color)

        if start_x < cursor_local.x < end_x:
            remove_color = tuple(prefs.decorator_color_error[:3])
            farthest_x = end_x if nearest_x == start_x else start_x
            emit(nearest_x, cursor_local.x, remove_color)
            emit(cursor_local.x, farthest_x, keep_color)
            return
        emit(nearest_x, cursor_local.x, keep_color)

    def _draw_cursor_split_preview(self, context: bpy.types.Context, prefs: Any) -> None:
        """Render two red lines at the cursor's projected X: one vertical along
        the wall's local Z (visible in elevation views), one horizontal across
        the wall's thickness band at floor Z (visible in plan / top-down view).
        Together they trace the cut plane the split operator would commit.
        Hover-gated on the split icon; coloured with the destructive-action
        warning red to match the icon's own hover signal."""
        active = self._active_layer2_wall_for_gizmo_preview(context, prefs)
        if active is None:
            return
        if not self._cursor_icon_hovered(GizmoWallEdition, "split_gizmo", context):
            return
        geom = tool.Wall.read_geometry(active)
        if geom is None:
            return
        anchor_x = geom.get("anchor_x", 0.0)
        length = geom.get("length", 0.0)
        height = geom.get("height", 0.0)
        offset = geom.get("offset", 0.0)
        thickness = geom.get("thickness", 0.0)
        if length <= 0 or height <= 0:
            return
        mw = active.matrix_world
        cursor_local = mw.inverted() @ context.scene.cursor.location
        if not (anchor_x < cursor_local.x < anchor_x + length):
            return
        color = tuple(prefs.decorator_color_error[:3])
        bottom_world = mw @ Vector((cursor_local.x, 0.0, 0.0))
        top_world = mw @ Vector((cursor_local.x, 0.0, height))
        segments: list[tuple[tuple[float, float, float], tuple[float, float, float]]] = [
            (tuple(bottom_world), tuple(top_world))
        ]
        if thickness > 0:
            base_a = mw @ Vector((cursor_local.x, offset, 0.0))
            base_b = mw @ Vector((cursor_local.x, offset + thickness, 0.0))
            segments.append((tuple(base_a), tuple(base_b)))
        self._stroke(context, segments, color)

    def _draw_cursor_extend_z_preview(self, context: bpy.types.Context, prefs: Any) -> None:
        """Hover-gated vertical-line preview for the extend-Z icon at the
        cursor's projected X on the wall axis (y=0 reference-line plane).

        Two cases by cursor Z relative to the wall's current height:

        - **Cursor Z above the wall top (grow)**: one green
          ``decorator_color_selected`` segment from z=height to z=cursor.z
          (the new vertical material).
        - **Cursor Z inside ``(0, height)`` (shrink)**: two segments —
          green from z=0 to z=cursor.z (the portion that REMAINS), red
          ``decorator_color_error`` from z=cursor.z to z=height (the
          portion the operator REMOVES)."""
        active = self._active_layer2_wall_for_gizmo_preview(context, prefs)
        if active is None:
            return
        if not self._cursor_icon_hovered(GizmoWallEdition, "extend_z_gizmo", context):
            return
        geom = tool.Wall.read_geometry(active)
        if geom is None:
            return
        length = geom.get("length", 0.0)
        height = geom.get("height", 0.0)
        if length <= 0 or height <= 0:
            return
        mw = active.matrix_world
        cursor_local = mw.inverted() @ context.scene.cursor.location
        if cursor_local.z <= 0:
            return
        if abs(cursor_local.z - height) < 1e-6:
            return
        keep_color = tuple(prefs.decorator_color_selected[:3])
        cursor_x = cursor_local.x

        def stroke(z0: float, z1: float, color: tuple[float, float, float]) -> None:
            a = mw @ Vector((cursor_x, 0.0, z0))
            b = mw @ Vector((cursor_x, 0.0, z1))
            self._stroke(context, [(tuple(a), tuple(b))], color)

        if cursor_local.z > height:
            stroke(height, cursor_local.z, keep_color)
            return
        remove_color = tuple(prefs.decorator_color_error[:3])
        stroke(0.0, cursor_local.z, keep_color)
        stroke(cursor_local.z, height, remove_color)

    def _draw_cursor_perpendicular_wall_preview(self, context: bpy.types.Context, prefs: Any) -> None:
        """Hover-gated floor-plane preview of the branch wall's footprint.
        Green quad on Z=0 spanning the new wall's perpendicular body band
        (``offset`` to ``offset + thickness`` mapped through the perpendicular
        rotation) and its length from the projection on the source wall axis
        to the cursor."""
        active = self._active_layer2_wall_for_gizmo_preview(context, prefs)
        if active is None:
            return
        if not self._cursor_icon_hovered(GizmoWallEdition, "add_perpendicular_wall_gizmo", context):
            return
        geom = tool.Wall.read_geometry(active)
        if geom is None:
            return
        anchor_x = geom.get("anchor_x", 0.0)
        length = geom.get("length", 0.0)
        offset = geom.get("offset", 0.0)
        thickness = geom.get("thickness", 0.0)
        if length <= 0 or thickness <= 0:
            return
        mw = active.matrix_world
        cursor_local = mw.inverted() @ context.scene.cursor.location
        params = _perpendicular_wall_params(cursor_local.x, cursor_local.y, anchor_x, length)
        if params is None:
            return
        clamped_x, _length, side_sign = params
        # New wall axis sits at source-local X = clamped_x; its body extends
        # perpendicular to that axis. After rotating the new wall's ±Y body
        # band into the source's local frame, the band lands at source-local
        # X = clamped_x − side_sign · {offset, offset+thickness}.
        x_a = clamped_x - side_sign * offset
        x_b = clamped_x - side_sign * (offset + thickness)
        x_lo, x_hi = (x_a, x_b) if x_a < x_b else (x_b, x_a)
        y_lo, y_hi = (0.0, cursor_local.y) if cursor_local.y > 0 else (cursor_local.y, 0.0)
        keep_color = tuple(prefs.decorator_color_selected[:3])
        self._fill(context, [self._wall_floor_quad(mw, x_lo, x_hi, y_lo, y_hi)], keep_color)
