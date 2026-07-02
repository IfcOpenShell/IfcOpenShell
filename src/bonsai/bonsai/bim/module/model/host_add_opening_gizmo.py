# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2026
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
# This file was generated with the assistance of an AI coding tool.

"""Generic single-click "Add Opening" gizmo for hosts (walls, slabs, roofs).

One GizmoGroup serves every IFC host type that exposes ``HasOpenings``:
parametric LAYER2 walls, any ``IfcSlab``, and any ``IfcRoof``. The poll
guards host-host pairings so this gizmo never overlaps with the existing
wall-join / extend-vertically gizmos. The positioner dispatches on element
type — walls use axis-projection + camera-facing-Y math (which requires the
parametric layer-set); slabs and roofs use a world-Z face bias driven by
the void object's elevation against the host's bounding box."""

import bpy
from mathutils import Vector

import bonsai.tool as tool
from bonsai.bim.module.drawing import gizmos as gizmo
from bonsai.bim.module.model.opening import is_filling_supported
from bonsai.bim.module.model.wall import (
    _get_wall_geom_cached,
    _wall_camera_facing_icon_y,
    _wall_gizmo_poll_gate,
    _WallGeomCachedBillboardingMixin,
)


def is_supported_host(element) -> bool:
    """Total predicate (None → False). Walls accept either a parametric
    LAYER2 wall OR a fillet-corner wall (both expose a usable axis +
    layer-set for the anchor math); slabs and roofs only need the bound
    box so any IfcSlab / IfcRoof qualifies regardless of parametric
    modifier state."""
    if element is None:
        return False
    return tool.Parametric.is_path_connectable_wall(element) or element.is_a("IfcSlab") or element.is_a("IfcRoof")


def is_supported_filling_or_opening(element) -> bool:
    """Total predicate for the add-opening gizmo poll. ``None`` (raw Blender
    mesh) is accepted because the operator converts unclassified meshes
    into ``IfcOpeningElement`` instances. ``IfcOpeningElement`` is accepted
    because reassigning an existing opening to a new host is a legal path
    through the operator. Otherwise defer to the generator's own
    supported-filling predicate."""
    if element is None:
        return True
    if element.is_a("IfcOpeningElement"):
        return True
    return is_filling_supported(element)


def _resolve_active_host(context: bpy.types.Context, n_selected: int):
    """Shared poll prologue: gizmo gate + selection cardinality + active-in-
    selected + IFC entity lookup + supported-host predicate. Returns the
    active element on success, ``None`` on any failure — callers chain their
    feature-specific checks past the early-return."""
    if not _wall_gizmo_poll_gate(context):
        return None
    selected = tool.Blender.get_selected_objects()
    if len(selected) != n_selected:
        return None
    active = context.active_object
    if active is None or active not in selected:
        return None
    element = tool.Ifc.get_entity(active)
    if not element or not is_supported_host(element):
        return None
    return element


class GizmoHostAddOpening(bpy.types.GizmoGroup, _WallGeomCachedBillboardingMixin):
    """Activates when exactly two objects are selected and one is a fillable
    host (wall / slab / roof) while the other is a valid filling (door /
    window / existing opening, or a plain Blender mesh).

    Selection-order independent: the host role is identified by class, not
    by active state. The "+" icon anchors on the host's surface regardless
    of which object was clicked first. The dispatched ``bim.add_opening``
    operator also handles either order.

    Per-frame positioning keeps the icon facing the camera as the viewport
    orbits."""

    bl_idname = "OBJECT_GGT_bim_host_add_opening"
    bl_label = "Host Add Opening Gizmo"
    bl_space_type = "VIEW_3D"
    bl_region_type = "WINDOW"
    bl_options = {"3D", "PERSISTENT"}

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        if not _wall_gizmo_poll_gate(context):
            return False
        selected = list(tool.Blender.get_selected_objects())
        if len(selected) != 2:
            return False
        active = context.active_object
        if active is None or active not in selected:
            return False
        a_element = tool.Ifc.get_entity(selected[0])
        b_element = tool.Ifc.get_entity(selected[1])
        return cls._is_apply_opening_pair(a_element, b_element) or cls._is_apply_opening_pair(b_element, a_element)

    @staticmethod
    def _is_apply_opening_pair(host_element, filling_element) -> bool:
        """``host_element`` qualifies as a fillable host AND ``filling_element``
        qualifies as a filling. Used twice with the operands swapped so the
        gizmo polls true regardless of which of the two selected objects is
        active."""
        if not is_supported_host(host_element):
            return False
        if not hasattr(host_element, "HasOpenings"):
            return False
        return is_supported_filling_or_opening(filling_element)

    def setup(self, context: bpy.types.Context) -> None:
        default_color, highlight_color = self.get_decoration_colors()
        self.add_opening_icon = self.setup_icon_gizmo(
            "VIEW3D_GT_add_opening", default_color, highlight_color, "bim.add_opening"
        )

    def position_gizmos(self, context: bpy.types.Context) -> None:
        selected = list(tool.Blender.get_selected_objects())
        if len(selected) != 2:
            return
        a, b = selected[0], selected[1]
        a_element = tool.Ifc.get_entity(a)
        b_element = tool.Ifc.get_entity(b)
        if is_supported_host(a_element):
            host_obj, host_element, other = a, a_element, b
        elif is_supported_host(b_element):
            host_obj, host_element, other = b, b_element, a
        else:
            return

        if tool.Parametric.is_path_connectable_wall(host_element):
            world_pos = wall_anchor(context, self, host_obj, other)
        else:
            world_pos = layer3_anchor(host_obj, other)
        if world_pos is None:
            return
        self.add_opening_icon.matrix_basis = gizmo.billboarded_at(world_pos, gizmo.get_billboard_rotation(context))


def wall_anchor(
    context: bpy.types.Context, group: bpy.types.GizmoGroup, wall_obj: bpy.types.Object, other: bpy.types.Object
) -> Vector | None:
    """World-space anchor for the add-opening icon on a wall host: void origin
    projected onto the wall reference-line X (clamped to wall extents), lifted to
    the camera-facing wall-local Y."""
    geom = _get_wall_geom_cached(group, wall_obj)
    if not geom:
        return None
    mw = wall_obj.matrix_world
    wall_local = mw.inverted() @ other.matrix_world.translation
    local_x = max(geom["anchor_x"], min(wall_local.x, geom["anchor_x"] + geom["length"]))
    icon_y = _wall_camera_facing_icon_y(context, mw, geom)
    base_world = mw @ Vector((local_x, icon_y, 0.0))
    top_world = mw @ Vector((local_x, icon_y, geom["height"] + gizmo.BaseParametricGizmoGroup.ICON_Z_OFFSET))
    return gizmo.BaseParametricGizmoGroup.pick_visible_anchor(context, base_world, top_world)


def layer3_anchor(host_obj: bpy.types.Object, other: bpy.types.Object) -> Vector:
    """World-space anchor for the add-opening icon on a LAYER3 host (slab / roof):
    void's world XY, lifted just above the host's top face. Predictable height
    regardless of where the void sits vertically — clicking the icon places the
    opening at the void's XY, and the operator handles the actual cut depth."""
    bbox = tool.Blender.get_object_world_bounding_box(host_obj)
    anchor_xy = other.matrix_world.translation.xy
    top_z = bbox["max_z"] + gizmo.BaseParametricGizmoGroup.ICON_Z_OFFSET
    return Vector((anchor_xy.x, anchor_xy.y, top_z))


def host_toggle_anchor(host_obj: bpy.types.Object) -> Vector:
    """Object origin XY, lifted just above the topmost mesh vertex. Tracks
    the parametric origin (useful reference even when the mesh extends
    asymmetrically) and the visible top face (stays clear of sloped or
    stepped bodies)."""
    origin = host_obj.matrix_world.translation
    top_z = tool.Blender.get_object_world_bounding_box(host_obj)["max_z"] + gizmo.BaseParametricGizmoGroup.ICON_Z_OFFSET
    return Vector((origin.x, origin.y, top_z))


class GizmoHostToggleOpenings(bpy.types.GizmoGroup, _WallGeomCachedBillboardingMixin):
    """Fallback toggle-openings icon for hosts that lack their own
    parametric-edit toolbar — slabs today, plus any foreign-authored
    IfcRoof that carries no BBIM_Roof pset (so ``GizmoRoofEdition`` doesn't
    poll for it). Walls and parametric roofs already render an idle-row
    toggle next to the pen and are excluded from this poll.

    When slab parametric-edit lands the slab branch will pen-row-handle
    its own toggle; updating the exclusion predicate here is the only
    migration step needed."""

    bl_idname = "OBJECT_GGT_bim_host_toggle_openings"
    bl_label = "Host Toggle Openings Gizmo"
    bl_space_type = "VIEW_3D"
    bl_region_type = "WINDOW"
    bl_options = {"3D", "PERSISTENT"}

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        element = _resolve_active_host(context, n_selected=1)
        if element is None:
            return False
        if not tool.Geometry.has_openings(element):
            return False
        # Skip when a per-feature parametric-edit gizmo already surfaces
        # an idle-row toggle for this element — walls and parametric roofs
        # both render their own toggle in the pen row.
        if tool.Parametric.is_path_connectable_wall(element):
            return False
        if tool.Parametric.is_roof(element):
            return False
        return True

    def setup(self, context: bpy.types.Context) -> None:
        default_color, highlight_color = self.get_decoration_colors()
        self.toggle_openings_icon = self.setup_icon_gizmo(
            "VIEW3D_GT_add_opening", default_color, highlight_color, "bim.toggle_host_openings"
        )

    def position_gizmos(self, context: bpy.types.Context) -> None:
        host_obj = context.active_object
        if not host_obj:
            return
        self.toggle_openings_icon.matrix_basis = gizmo.billboarded_at(
            host_toggle_anchor(host_obj), gizmo.get_billboard_rotation(context)
        )
