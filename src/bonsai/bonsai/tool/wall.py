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

"""Side-effect-free wall helpers — IFC reads and wall-axis geometry, callable from
gizmo lambdas without loading the wall's draft props. The world-space geometry helpers
are pure-math wrappers over ``bonsai.core.model``."""

from __future__ import annotations

from collections import deque
from typing import TYPE_CHECKING, TypedDict

import ifcopenshell
import ifcopenshell.util.element
import ifcopenshell.util.representation
import ifcopenshell.util.unit
from mathutils import Vector

import bonsai.core.model
import bonsai.core.tool
import bonsai.tool as tool

if TYPE_CHECKING:
    import bpy


class WallGeometry(TypedDict):
    anchor_x: float
    length: float
    height: float
    x_angle: float
    thickness: float
    offset: float


class Wall(bonsai.core.tool.Wall):
    @classmethod
    def get_length_and_height(cls, wall: ifcopenshell.entity_instance) -> tuple[float, float] | None:
        """SI length and vertical height of a LAYER2 extruded wall, or ``None`` for
        non-parametric bodies (sweeps, brep, non-extrusion booleans)."""
        representation = tool.Geometry.get_body_representation(wall)
        if not representation:
            return None
        extrusion = tool.Model.get_extrusion(representation)
        if not extrusion:
            return None
        unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
        p1, p2 = ifcopenshell.util.representation.get_reference_line(wall)
        x_angle = tool.Model.get_existing_x_angle(extrusion)
        return bonsai.core.model.length_and_height_from_extrusion(
            extrusion_depth=extrusion.Depth,
            x_angle=x_angle,
            reference_line_x_extent=p2[0] - p1[0],
            unit_scale=unit_scale,
        )

    @classmethod
    def get_axis_local_extent(cls, wall: ifcopenshell.entity_instance) -> tuple[float, float] | None:
        """``(min_x, max_x)`` of the wall's IFC reference line in wall-local SI metres,
        or ``None``. Anchors wall-edge gizmos at IFC-authoritative ends — ``obj.bound_box``
        would drift on trimmed walls or walls with end openings."""
        representation = tool.Geometry.get_body_representation(wall)
        if not representation:
            return None
        unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
        p1, p2 = ifcopenshell.util.representation.get_reference_line(wall)
        x1, x2 = p1[0] * unit_scale, p2[0] * unit_scale
        return (min(x1, x2), max(x1, x2))

    @classmethod
    def get_x_angle(cls, wall: ifcopenshell.entity_instance) -> float | None:
        """Slanted-extrusion angle (radians) of a LAYER2 wall, zero for vertical walls,
        ``None`` for non-parametric bodies. Callers that assume wall-local Z == world Z
        must gate on this being zero."""
        representation = tool.Geometry.get_body_representation(wall)
        if not representation:
            return None
        extrusion = tool.Model.get_extrusion(representation)
        if not extrusion:
            return None
        return tool.Model.get_existing_x_angle(extrusion)

    @classmethod
    def read_geometry(cls, obj: bpy.types.Object) -> WallGeometry | None:
        """Live wall geometry from IFC in SI metres/radians, or ``None`` for
        non-path-connectable walls. Shared by gizmo positioning and draft
        initialisation. Fillet-corner walls carry their chord axis as the
        reference line and report zero thickness / offset (material was
        unassigned at construction); callers that need a layer-driven thickness
        must gate on ``tool.Parametric.is_wall`` upstream."""
        element = tool.Ifc.get_entity(obj)
        if not element or not tool.Parametric.is_path_connectable_wall(element):
            return None
        representation = tool.Geometry.get_body_representation(element)
        if not representation:
            return None
        extrusion = tool.Model.get_extrusion(representation)
        if not extrusion:
            return None
        unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
        p1, p2 = ifcopenshell.util.representation.get_reference_line(element)
        layer_params = tool.Model.get_material_layer_parameters(element)
        x_angle = tool.Model.get_existing_x_angle(extrusion)
        return {
            "anchor_x": p1[0] * unit_scale,
            "length": (p2[0] - p1[0]) * unit_scale,
            "height": bonsai.core.model.vertical_height_from_extrusion_depth(extrusion.Depth * unit_scale, x_angle),
            "x_angle": x_angle,
            "thickness": layer_params["thickness"],
            "offset": layer_params["offset"],
        }

    @classmethod
    def collinear_boundary_world(cls, seg_a: tuple[Vector, Vector], seg_b: tuple[Vector, Vector]) -> Vector:
        """World-space midpoint of the closest endpoint pair across two wall axis segments —
        the anchor for Merge/Unjoin gizmos on collinear or already-joined walls."""
        return Vector(
            bonsai.core.model.closest_endpoint_midpoint(
                (tuple(seg_a[0]), tuple(seg_a[1])),
                (tuple(seg_b[0]), tuple(seg_b[1])),
            )
        )

    @classmethod
    def path_connection_location_world(
        cls,
        seg_self: tuple[Vector, Vector],
        self_conn_type: str,
        seg_other: tuple[Vector, Vector],
        other_conn_type: str,
        parallel_threshold: float = bonsai.core.model.PARALLEL_DOT_THRESHOLD,
    ) -> Vector:
        """World-space physical join point of an ``IfcRelConnectsPathElements`` — an
        endpoint for end-connected walls, the axis intersection for ATPATH junctions."""
        return Vector(
            bonsai.core.model.compute_path_connection_location(
                (tuple(seg_self[0]), tuple(seg_self[1])),
                self_conn_type,
                (tuple(seg_other[0]), tuple(seg_other[1])),
                other_conn_type,
                parallel_threshold,
            )
        )

    @classmethod
    def validate_for_parametric_edit(cls, obj: bpy.types.Object) -> str | None:
        """``None`` if the wall is parametrically editable, else a user-facing string naming
        the specific gap so the user can fix the precise blocker."""
        element = tool.Ifc.get_entity(obj)
        if not element:
            return "Object is not an IFC element."
        if not element.is_a("IfcWall"):
            return f"Object is an {element.is_a()}, not an IfcWall."
        if tool.Model.get_usage_type(element) != "LAYER2":
            return (
                "Wall has no IfcMaterialLayerSetUsage with LayerSetDirection AXIS2 (required for parametric editing)."
            )
        representation = tool.Geometry.get_body_representation(element)
        if not representation:
            return "Wall has no Model/Body/MODEL_VIEW representation to drive parametric dimensions."
        if not tool.Model.get_extrusion(representation):
            return (
                "Wall body is not an IfcExtrudedAreaSolid "
                "(e.g. a brep mesh or boolean result without a base extrusion)."
            )
        return None

    @classmethod
    def has_layer2_usage(cls, wall: ifcopenshell.entity_instance) -> bool:
        """True iff ``wall`` is a LAYER2 parametric wall (has ``IfcMaterialLayerSetUsage``
        with ``LayerSetDirection == AXIS2``). Required by every parametric wall edit —
        non-LAYER2 walls (brep / freeform bodies) cannot be driven by axis + thickness."""
        return tool.Model.get_usage_type(wall) == "LAYER2"

    @classmethod
    def is_straight_axis(cls, wall: ifcopenshell.entity_instance) -> bool:
        """True iff the wall's Axis representation is a single straight line segment.

        Curved-axis walls (e.g. a fillet corner inserted between two straight walls)
        report ``False`` so callers gate them out of operations that assume a straight
        reference line. The check inspects the ``Plan/Axis/GRAPH_VIEW`` representation
        when present; falls back to True when no Axis representation exists (the
        ``Body`` extrusion alone is implicitly straight)."""
        axis_rep = ifcopenshell.util.representation.get_representation(wall, "Plan", "Axis", "GRAPH_VIEW")
        if axis_rep is None or not axis_rep.Items:
            return True
        for item in axis_rep.Items:
            if item.is_a("IfcPolyline"):
                if len(item.Points) != 2:
                    return False
            elif item.is_a("IfcIndexedPolyCurve"):
                # An ``IfcIndexedPolyCurve`` is straight only when (a) its
                # ``Points`` list holds exactly two points and (b) it has no
                # ``Segments`` or only ``IfcLineIndex`` segments. Any ``IfcArcIndex``
                # makes it curved.
                segments = getattr(item, "Segments", None)
                if segments:
                    for seg in segments:
                        if seg.is_a("IfcArcIndex"):
                            return False
                point_list = item.Points
                point_coords = getattr(point_list, "CoordList", None) if point_list else None
                if point_coords and len(point_coords) > 2:
                    return False
            else:
                # Trimmed curve, composite curve, B-spline — definitely curved.
                return False
        return True

    @classmethod
    def get_world_reference_line(cls, obj: bpy.types.Object) -> tuple[Vector, Vector] | None:
        """World-space endpoints of the wall's IFC reference line, in Blender units.

        Returns ``(p1, p2)`` as 3D vectors with the wall's local Z preserved.
        Returns ``None`` when the wall has no IFC element or no IFC Axis
        representation. Anchors to the IFC reference line, not the mesh bound
        box, so it stays correct when the mesh is stale or trimmed past the
        IFC axis endpoints."""
        element = tool.Ifc.get_entity(obj)
        if element is None or not tool.Geometry.has_axis_representation(element):
            return None
        p1, p2 = ifcopenshell.util.representation.get_reference_line(element)
        unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
        local_p1 = Vector((p1[0] * unit_scale, p1[1] * unit_scale, 0.0))
        local_p2 = Vector((p2[0] * unit_scale, p2[1] * unit_scale, 0.0))
        return obj.matrix_world @ local_p1, obj.matrix_world @ local_p2

    @classmethod
    def iter_wall_slab_connections(cls, wall: ifcopenshell.entity_instance):
        """Yield ``(slab, rel)`` tuples for every ``IfcRelConnectsElements(TOP)``
        connecting a slab to this wall — the rel kind ``extend_walls_to_underside``
        creates. Walks ``wall.ConnectedFrom`` because the slab is the relating
        side of the TOP rel."""
        for rel in getattr(wall, "ConnectedFrom", []) or ():
            if not rel.is_a("IfcRelConnectsElements") or rel.Description != "TOP":
                continue
            slab = rel.RelatingElement
            if slab is None:
                continue
            yield slab, rel

    @classmethod
    def iter_slab_wall_connections(cls, slab: ifcopenshell.entity_instance):
        """Yield ``(wall, rel)`` tuples for every wall clipped to this slab's
        underside. Mirror of ``iter_wall_slab_connections`` from the slab side
        — walks ``slab.ConnectedTo``."""
        for rel in getattr(slab, "ConnectedTo", []) or ():
            if not rel.is_a("IfcRelConnectsElements") or rel.Description != "TOP":
                continue
            wall = rel.RelatedElement
            if wall is None:
                continue
            yield wall, rel

    @classmethod
    def find_wall_slab_rel(
        cls, wall: ifcopenshell.entity_instance, slab: ifcopenshell.entity_instance
    ) -> ifcopenshell.entity_instance | None:
        """Return the single ``IfcRelConnectsElements(TOP)`` between ``wall``
        and ``slab``, or ``None`` if none exists. Used by the disconnect
        operator to find the specific rel to remove."""
        for s, rel in cls.iter_wall_slab_connections(wall):
            if s == slab:
                return rel
        return None

    WALL_SLAB_CONNECTION_Z_CLEARANCE = 0.5
    """Lift above the wall top so the disconnect icon sits above the
    extend-vertical / slope gizmo and reads as "the thing above the wall =
    the slab connection"."""

    @classmethod
    def wall_slab_connection_location_world(
        cls, wall_obj: bpy.types.Object, slab_obj: bpy.types.Object
    ) -> Vector | None:
        """World-space anchor for the wall-slab disconnect icon.

        X / Y come from the wall axis midpoint (so the icon sits in the
        middle of the wall horizontally); Z is the wall's top in world space
        plus ``WALL_SLAB_CONNECTION_Z_CLEARANCE`` so the icon perches above
        the slope gizmo. The slab-side gizmo calls this with the same
        arguments so both sides of the same connection render a single
        visual marker. ``slab_obj`` is kept on the signature for the
        symmetric call shape; the helper's body no longer reads from it.
        Returns ``None`` when the wall has no reference line."""
        ref = cls.get_world_reference_line(wall_obj)
        if ref is None:
            return None
        axis_mid_world = (ref[0] + ref[1]) * 0.5
        if wall_obj.bound_box:
            wall_top_local_z = max(c[2] for c in wall_obj.bound_box)
            wall_top_world_z = (wall_obj.matrix_world @ Vector((0.0, 0.0, wall_top_local_z))).z
        else:
            wall_top_world_z = axis_mid_world.z
        return Vector((axis_mid_world.x, axis_mid_world.y, wall_top_world_z + cls.WALL_SLAB_CONNECTION_Z_CLEARANCE))

    @classmethod
    def walk_connected_walls(
        cls,
        start_element: ifcopenshell.entity_instance,
        node_cap: int = 5000,
    ) -> list[ifcopenshell.entity_instance]:
        """BFS over ``IfcRelConnectsPathElements`` from ``start_element``.

        Returns every ``IfcWall`` reachable in either direction (relating /
        related side of the relation) in BFS order with ``start_element``
        first. Stops when ``node_cap`` walls have been visited so a corrupt
        or massive network can't lock up a draw callback. Non-wall path
        elements (e.g. ``IfcRoof``, ``IfcSlab``) are traversed but not
        collected — they may bridge two disjoint wall runs.

        Mirror of ``tool.System.walk_connected_mep_elements``."""
        if not start_element.is_a("IfcWall"):
            return []
        result: list[ifcopenshell.entity_instance] = []
        visited: set[int] = set()
        queue: deque[ifcopenshell.entity_instance] = deque([start_element])
        while queue and len(visited) < node_cap:
            element = queue.popleft()
            if element.id() in visited:
                continue
            visited.add(element.id())
            if element.is_a("IfcWall"):
                result.append(element)
            # ``ConnectedTo`` / ``ConnectedFrom`` are the IFC inverse
            # attributes that expose the relations where this element
            # is the relating / related side respectively.
            for rel in getattr(element, "ConnectedTo", []) or ():
                if rel.is_a("IfcRelConnectsPathElements"):
                    neighbor = rel.RelatedElement
                    if neighbor is not None and neighbor.id() not in visited:
                        queue.append(neighbor)
            for rel in getattr(element, "ConnectedFrom", []) or ():
                if rel.is_a("IfcRelConnectsPathElements"):
                    neighbor = rel.RelatingElement
                    if neighbor is not None and neighbor.id() not in visited:
                        queue.append(neighbor)
        return result

    @classmethod
    def compute_wall_fillet_geometry(
        cls,
        wall_a_obj: bpy.types.Object,
        wall_b_obj: bpy.types.Object,
        radius: float,
        arc_resolution: int = bonsai.core.model.FILLET_DEFAULT_ARC_RESOLUTION,
    ) -> dict | None:
        """Compute fillet geometry between two walls in world space.

        Returns a dict augmented with ``profile_thickness`` and ``height`` from
        the active (A) wall's LAYER2 parameters, plus ``wall_type_id`` and
        ``x_angle``. Returns ``None`` when either wall lacks a reference line
        or LAYER2 usage."""
        axis_a = cls.get_world_reference_line(wall_a_obj)
        axis_b = cls.get_world_reference_line(wall_b_obj)
        if axis_a is None or axis_b is None:
            return None

        wall_a = tool.Ifc.get_entity(wall_a_obj)
        if wall_a is None or not cls.has_layer2_usage(wall_a):
            return None

        seg_a = ((axis_a[0].x, axis_a[0].y, axis_a[0].z), (axis_a[1].x, axis_a[1].y, axis_a[1].z))
        seg_b = ((axis_b[0].x, axis_b[0].y, axis_b[0].z), (axis_b[1].x, axis_b[1].y, axis_b[1].z))
        result = bonsai.core.model.compute_fillet_polylines(seg_a, seg_b, radius, arc_resolution)

        layers = tool.Model.get_material_layer_parameters(wall_a)
        length_height = cls.get_length_and_height(wall_a)
        wall_type = ifcopenshell.util.element.get_type(wall_a)
        result.update(
            {
                "profile_thickness": layers["thickness"],
                "profile_offset": layers["offset"],
                "height": length_height[1] if length_height else None,
                "x_angle": cls.get_x_angle(wall_a) or 0.0,
                "wall_type_id": wall_type.id() if wall_type else None,
            }
        )
        return result
