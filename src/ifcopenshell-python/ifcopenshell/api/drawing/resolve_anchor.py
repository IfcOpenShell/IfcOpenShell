# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of IfcOpenShell.
#
# IfcOpenShell is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcOpenShell is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcOpenShell.  If not, see <http://www.gnu.org/licenses/>.

"""Resolve a parametric dimension anchor to a world-space coordinate in metres.

NOTE ON COORDINATE SPACE
All anchor coordinates (``pt``, ``hint``) are stored in metres (= Blender world
space).  Profile vertex positions computed from IFC attributes are converted to
metres via ``ifcopenshell.util.unit.calculate_unit_scale``.

Anchor schema (JSON-serialisable dict stored in BBIM_Dimension.Anchors):

  {
    "guid":  str | None,   # element GlobalId; None → WORLD type (free point)
    "type":  str,          # "FACE" | "EDGE" | "VERTEX" | "WORLD"
    "addr":  {
      # FACE_NORMAL — face identified by element-local unit normal (platform-agnostic).
      # Rotation-invariant: moving/rotating the element does not invalidate the anchor.
      "method":       "FACE_NORMAL",
      "normal_local": [float, float, float],  # element-local unit normal

      # PROFILE_LOCAL — point in IfcExtrudedAreaSolid profile-local space.
      # profile_x_m / profile_y_m are in the profile's 2-D local frame, metres.
      # extrusion_z_m is distance along the normalized ExtrudedDirection, metres.
      # snap: "VERTEX" → re-snap to nearest profile vertex on resolution,
      #        "EDGE"  → use coords directly (midpoint between two vertices).
      "method":        "PROFILE_LOCAL",
      "profile_x_m":   float,
      "profile_y_m":   float,
      "extrusion_z_m": float,
      "snap":          "VERTEX" | "EDGE",

      # LAYER_BOUNDARY — face/boundary of a material layer (platform-agnostic).
      # Resolution tiers (first match wins):
      #   layer_id            → IfcMaterialLayer STEP id  (stable in NativeBIM)
      #   layer_material_id   → IfcMaterial STEP id
      #   layer_material_name → IfcMaterial.Name
      #   layer_category      → IfcMaterialLayer.Category (IFC4)
      #   layer_index         → 0-based position in layer set
      #   offset_from_ref_m   → proximity to nearest boundary (geometric fallback)
      "method":             "LAYER_BOUNDARY",
      "layer_id":           int,
      "layer_material_id":  int,
      "layer_material_name": str,
      "layer_category":     str,
      "layer_index":        int,
      "face":               "start" | "end",
      "offset_from_ref_m":  float,
    } | None,
    "hint":  [x, y, z] | None,
    "pt":    [x, y, z]          # cached world position; universal static fallback
  }
"""

from __future__ import annotations

import math
from typing import Optional

import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.util.placement
import ifcopenshell.util.unit


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def resolve_anchor(
    file: ifcopenshell.file,
    anchor: dict,
    settings: Optional[ifcopenshell.geom.settings] = None,
    shape_cache: Optional[dict] = None,
    placement_override: Optional[dict] = None,
) -> Optional[tuple[float, float, float]]:
    """Resolve an anchor dict to a world-space point in metres.

    Resolution order:
      1. WORLD / null guid → return stored ``pt`` directly.
      2. PROFILE_LOCAL → analytically resolve via IfcExtrudedAreaSolid profile coords.
      3. PROFILE_VERT / PROFILE_EDGE → legacy index-based resolution (backwards compat).
      4. FACE_NORMAL → match face group by element-local normal (rotation-invariant).
      5. Fallback → stored ``pt``.

    :param file: The open IFC file.
    :param anchor: Anchor descriptor dict.
    :param settings: ifcopenshell.geom settings; created automatically when None.
    :param shape_cache: Mutable dict keyed by element STEP id to cache shapes.
    :param placement_override: Optional dict mapping element STEP id → 4×4 numpy
        matrix (row-major, metres).  When provided, this matrix is used instead of
        ``element.ObjectPlacement`` for the local→world transform.  Pass the
        Blender object's ``matrix_world`` here so that elements moved in the
        viewport but not yet explicitly synced to IFC are handled correctly.
    :return: ``(x, y, z)`` in metres, or ``None``.
    """
    anchor_type = anchor.get("type", "WORLD")
    guid = anchor.get("guid")

    if anchor_type == "WORLD" or not guid:
        return _pt_or_none(anchor.get("pt"))

    try:
        element = file.by_guid(guid)
    except Exception:
        return _pt_or_none(anchor.get("pt"))

    addr = anchor.get("addr") or {}

    if anchor_type in ("VERTEX", "EDGE"):
        method = addr.get("method", "")
        if method == "PROFILE_LOCAL":
            pt = _resolve_profile_local_anchor(file, element, addr, placement_override)
        elif method == "PROFILE_VERT":
            pt = _resolve_profile_vert_anchor(file, element, addr, placement_override)
        elif method == "PROFILE_EDGE":
            pt = _resolve_profile_edge_anchor(file, element, addr, placement_override)
        elif method == "LOCAL_POINT":
            lx = addr.get("local_x_m")
            ly = addr.get("local_y_m")
            lz = addr.get("local_z_m")
            pt = _local_to_world_m(file, element, (lx, ly, lz), placement_override) if None not in (lx, ly, lz) else None
        else:
            pt = None
        return pt if pt is not None else _pt_or_none(anchor.get("pt"))

    # FACE anchor — check method first; LAYER_BOUNDARY does not need tessellation.
    method = addr.get("method", "FACE_NORMAL")
    if method == "LAYER_BOUNDARY":
        pt = _resolve_layer_boundary_anchor(file, element, addr, placement_override)
        return pt if pt is not None else _pt_or_none(anchor.get("pt"))

    # FACE_NORMAL — match by element-local normal (rotation-invariant).
    shape = _get_shape(file, element, settings, shape_cache)
    if shape is None:
        return _pt_or_none(anchor.get("pt"))

    verts, tris = _extract_mesh(shape)
    if not tris:
        return _pt_or_none(anchor.get("pt"))

    groups = _group_coplanar_tris(verts, tris)
    group_props = [_face_group_props(g, verts, tris) for g in groups]
    world_group_props = [
        {
            "centroid": _local_to_world_m(file, element, gp["centroid"], placement_override),
            "normal": _rotate_local_to_world(element, gp["normal"], placement_override),
            "area": gp["area"],
        }
        for gp in group_props
    ]

    # Support both new FACE_NORMAL (addr.normal_local) and legacy fingerprint field.
    normal_local = addr.get("normal_local") or (addr.get("fingerprint") or {}).get("normal_local")
    hint = anchor.get("hint")
    pt = _find_by_local_normal(group_props, world_group_props, normal_local, hint) if normal_local else None
    return pt if pt is not None else _pt_or_none(anchor.get("pt"))


def build_anchor_from_hit(
    file: ifcopenshell.file,
    element: ifcopenshell.entity_instance,
    hit_location_ifc: tuple[float, float, float],
    hit_normal_ifc: tuple[float, float, float],
    settings: Optional[ifcopenshell.geom.settings] = None,
    shape_cache: Optional[dict] = None,
    placement_override: Optional[dict] = None,
) -> dict:
    """Build a FACE/FACE_NORMAL anchor dict from a viewport ray-cast hit.

    Tessellates the element, finds the best-matching face group, and stores the
    element-local unit normal.  The local normal is rotation-invariant: moving or
    rotating the element does not invalidate the anchor.

    :param file: The open IFC file.
    :param element: The IFC element that was hit.
    :param hit_location_ifc: Hit point in metres (world space).
    :param hit_normal_ifc: Face normal at the hit point (world space, unit vec).
    :param settings: Geometry settings for tessellation.
    :param shape_cache: Mutable shape-cache dict.
    :param placement_override: Optional dict mapping element STEP id → 4×4 numpy
        matrix (metres).  See ``resolve_anchor`` for details.
    :return: Anchor dict ready for JSON serialisation into BBIM_Dimension.
    """
    shape = _get_shape(file, element, settings, shape_cache)
    normal_local: list = list(hit_normal_ifc)  # fallback: world normal as approximation

    if shape is not None:
        verts, tris = _extract_mesh(shape)
        groups = _group_coplanar_tris(verts, tris)
        local_group_props = [_face_group_props(g, verts, tris) for g in groups]
        world_group_props = [
            {
                "centroid": _local_to_world_m(file, element, gp["centroid"], placement_override),
                "normal": _rotate_local_to_world(element, gp["normal"], placement_override),
                "area": gp["area"],
            }
            for gp in local_group_props
        ]
        best = _best_group(world_group_props, hit_normal_ifc, hit_location_ifc)
        if best is not None:
            best_idx, _ = best
            normal_local = list(local_group_props[best_idx]["normal"])

    return {
        "guid": element.GlobalId,
        "type": "FACE",
        "addr": {
            "method": "FACE_NORMAL",
            "normal_local": normal_local,
        },
        "hint": list(hit_location_ifc),
        "pt": list(hit_location_ifc),
    }


def make_world_anchor(pt_ifc: tuple[float, float, float]) -> dict:
    """Build a free-floating (WORLD) anchor — not connected to any element."""
    return {
        "guid": None,
        "type": "WORLD",
        "addr": None,
        "hint": None,
        "pt": list(pt_ifc),
    }


def build_anchor_from_local_point(
    element: ifcopenshell.entity_instance,
    snap_kind: str,
    world_pos: tuple,
    local_pos_m: tuple,
) -> dict:
    """Build a VERTEX/EDGE anchor using element-local coordinates (metres).

    Used as a fallback for tessellated elements (IfcFacetedBrep, etc.) that have
    no IfcExtrudedAreaSolid.  The stored ``local_m`` is resolved back to world
    space via ``_local_to_world_m`` so the anchor follows the element through
    moves and rotations.

    :param element: The IFC element the snap landed on.
    :param snap_kind: ``"VERTEX"`` or ``"EDGE"``.
    :param world_pos: Current world-space snap position in metres (stored as hint/pt).
    :param local_pos_m: Element-local position in metres (rotation-invariant).
    :return: Anchor dict ready for JSON serialisation.
    """
    return {
        "guid": element.GlobalId,
        "type": snap_kind,
        "addr": {
            "method": "LOCAL_POINT",
            "local_x_m": float(local_pos_m[0]),
            "local_y_m": float(local_pos_m[1]),
            "local_z_m": float(local_pos_m[2]),
            "snap": snap_kind,
        },
        "hint": list(world_pos),
        "pt": list(world_pos),
    }


def build_anchor_from_profile_vert(
    file: ifcopenshell.file,
    element: ifcopenshell.entity_instance,
    snap: dict,
) -> dict:
    """Build a VERTEX/PROFILE_LOCAL anchor from a profile snap candidate.

    :param snap: Dict from ``get_profile_snap_candidates`` with keys
        ``snap_world``, ``profile_x_m``, ``profile_y_m``, ``extrusion_z_m``.
    :return: Anchor dict ready for JSON serialisation.
    """
    world_pos = snap["snap_world"]
    return {
        "guid": element.GlobalId,
        "type": "VERTEX",
        "addr": {
            "method": "PROFILE_LOCAL",
            "profile_x_m": snap["profile_x_m"],
            "profile_y_m": snap["profile_y_m"],
            "extrusion_z_m": snap["extrusion_z_m"],
            "snap": "VERTEX",
        },
        "hint": list(world_pos),
        "pt": list(world_pos),
    }


def build_anchor_from_profile_edge(
    file: ifcopenshell.file,
    element: ifcopenshell.entity_instance,
    snap: dict,
) -> dict:
    """Build an EDGE/PROFILE_LOCAL anchor from a profile snap candidate.

    :param snap: Dict from ``get_profile_snap_candidates`` with keys
        ``snap_world``, ``profile_x_m``, ``profile_y_m``, ``extrusion_z_m``.
    :return: Anchor dict ready for JSON serialisation.
    """
    world_pos = snap["snap_world"]
    return {
        "guid": element.GlobalId,
        "type": "EDGE",
        "addr": {
            "method": "PROFILE_LOCAL",
            "profile_x_m": snap["profile_x_m"],
            "profile_y_m": snap["profile_y_m"],
            "extrusion_z_m": snap["extrusion_z_m"],
            "snap": "EDGE",
        },
        "hint": list(world_pos),
        "pt": list(world_pos),
    }


def get_layer_snap_candidates(
    file: ifcopenshell.file,
    element: ifcopenshell.entity_instance,
    placement_override: Optional[dict] = None,
) -> list[dict]:
    """Return one snap candidate per IfcMaterialLayer boundary in the element.

    Each candidate dict has:
      - ``type``:             ``"VERTEX"``
      - ``snap_world``:       mid-height world position on the boundary, metres
      - ``v0``, ``v1``:       base and top endpoints of the boundary line (for GPU draw)
      - ``layer``:            the IfcMaterialLayer entity
      - ``layer_index``:      0-based index in the layer set
      - ``face``:             ``"start"`` or ``"end"``
      - ``offset_from_ref_m``: signed offset from element origin along thickness axis

    Returns [] when the element has no IfcMaterialLayerSetUsage or IfcExtrudedAreaSolid.
    """
    import ifcopenshell.util.element as ifc_elem

    material = ifc_elem.get_material(element, should_inherit=True)
    if not material or not material.is_a("IfcMaterialLayerSetUsage"):
        return []

    usage = material
    layers = usage.ForLayerSet.MaterialLayers
    unit_scale = ifcopenshell.util.unit.calculate_unit_scale(file)

    solid = _get_extrusion_solid(file, element)
    if solid is None:
        return []

    depth_m = float(solid.Depth) * unit_scale
    profile_pts_ifc = _get_profile_points_ifc(solid.SweptArea)
    centroid_x_m = 0.0
    centroid_y_m = 0.0
    x_min_m = x_max_m = 0.0
    y_min_m = y_max_m = 0.0
    if profile_pts_ifc:
        xs = [float(p[0]) * unit_scale for p in profile_pts_ifc]
        ys = [float(p[1]) * unit_scale for p in profile_pts_ifc]
        centroid_x_m = sum(xs) / len(xs)
        centroid_y_m = sum(ys) / len(ys)
        x_min_m, x_max_m = min(xs), max(xs)
        y_min_m, y_max_m = min(ys), max(ys)

    ref_m = float(usage.OffsetFromReferenceLine) * unit_scale
    direction_sense = (getattr(usage, "DirectionSense", None) or "POSITIVE")
    thickness_axis = (getattr(usage, "LayerSetDirection", None) or "AXIS2")
    sense = 1.0 if direction_sense == "POSITIVE" else -1.0

    # Collect unique boundary offsets (adjacent layers share a boundary)
    boundaries: list[tuple] = []  # (layer_index, layer, face, offset_m)
    seen_offsets: set = set()
    cumulative_m = ref_m

    for i, layer in enumerate(layers):
        thickness_m = float(layer.LayerThickness) * unit_scale
        start_m = cumulative_m
        end_m = cumulative_m + sense * thickness_m
        for face_label, offset_m in (("start", start_m), ("end", end_m)):
            key = round(offset_m, 6)
            if key not in seen_offsets:
                seen_offsets.add(key)
                boundaries.append((i, layer, face_label, offset_m))
        cumulative_m = end_m

    def _w(px, py, pz):
        return _profile_coords_to_world_m(file, element, solid, px, py, pz, placement_override)

    candidates: list[dict] = []
    for layer_idx, layer, face, offset_m in boundaries:
        if thickness_axis == "AXIS3":
            # Boundary is a horizontal plane at z = offset_m; span full profile XY extent.
            c0 = _w(x_min_m, y_min_m, offset_m)
            c1 = _w(x_max_m, y_min_m, offset_m)
            c2 = _w(x_max_m, y_max_m, offset_m)
            c3 = _w(x_min_m, y_max_m, offset_m)
            wp_mid = _w(centroid_x_m, centroid_y_m, offset_m)
        elif thickness_axis == "AXIS1":
            # Boundary is a plane at profile_x = offset_m; span full Y extent and Z depth.
            c0 = _w(offset_m, y_min_m, 0.0)
            c1 = _w(offset_m, y_max_m, 0.0)
            c2 = _w(offset_m, y_max_m, depth_m)
            c3 = _w(offset_m, y_min_m, depth_m)
            wp_mid = _w(offset_m, centroid_y_m, depth_m * 0.5)
        else:  # AXIS2
            # Boundary is a plane at profile_y = offset_m; span full X extent and Z depth.
            c0 = _w(x_min_m, offset_m, 0.0)
            c1 = _w(x_max_m, offset_m, 0.0)
            c2 = _w(x_max_m, offset_m, depth_m)
            c3 = _w(x_min_m, offset_m, depth_m)
            wp_mid = _w(centroid_x_m, offset_m, depth_m * 0.5)

        if wp_mid is None:
            continue
        seam_corners = [c for c in (c0, c1, c2, c3) if c is not None]
        candidates.append({
            "type": "VERTEX",
            "snap_world": wp_mid,
            "seam_corners": seam_corners,
            "layer": layer,
            "layer_index": layer_idx,
            "face": face,
            "offset_from_ref_m": offset_m,
        })

    return candidates


def build_anchor_from_layer_boundary(
    file: ifcopenshell.file,
    element: ifcopenshell.entity_instance,
    snap: dict,
) -> dict:
    """Build a FACE/LAYER_BOUNDARY anchor from a layer snap candidate.

    :param snap: Dict from ``get_layer_snap_candidates`` with keys
        ``snap_world``, ``layer``, ``layer_index``, ``face``, ``offset_from_ref_m``.
    :return: Anchor dict ready for JSON serialisation into BBIM_Dimension.
    """
    world_pos = snap["snap_world"]
    layer = snap["layer"]
    mat = getattr(layer, "Material", None)
    return {
        "guid": element.GlobalId,
        "type": "FACE",
        "addr": {
            "method": "LAYER_BOUNDARY",
            "layer_id": layer.id(),
            "layer_material_id": mat.id() if mat else None,
            "layer_material_name": mat.Name if mat else None,
            "layer_category": getattr(layer, "Category", None),
            "layer_index": snap["layer_index"],
            "face": snap["face"],
            "offset_from_ref_m": snap["offset_from_ref_m"],
        },
        "hint": list(world_pos),
        "pt": list(world_pos),
    }


def get_profile_snap_candidates(
    file: ifcopenshell.file,
    element: ifcopenshell.entity_instance,
    placement_override: Optional[dict] = None,
) -> list[dict]:
    """Return snap candidates derived from an element's IfcExtrudedAreaSolid profile.

    Each candidate dict has:
      - ``type``: ``"VERTEX"`` or ``"EDGE"``
      - ``snap_world``: world-space snap position in metres
      - ``profile_x_m``, ``profile_y_m``: position in profile-local 2-D space, metres
      - ``extrusion_z_m``: distance along ExtrudedDirection, metres
      - ``snap``: ``"VERTEX"`` or ``"EDGE"`` (resolution hint)
      - For EDGE candidates: ``v0``, ``v1`` world-space endpoints (for GPU indicator)

    Returns ``[]`` when the element has no IfcExtrudedAreaSolid representation.

    Candidates generated:
      - Base vertices    — each profile vertex at extrusion_z_m = 0
      - Top vertices     — each profile vertex at extrusion_z_m = depth_m
      - Base horiz edges — adjacent profile vertex pairs at extrusion_z_m = 0
      - Top horiz edges  — adjacent profile vertex pairs at extrusion_z_m = depth_m
      - Vertical edges   — same profile vertex at z=0 and z=depth_m (mid z)
    """
    solid = _get_extrusion_solid(file, element)
    if solid is None:
        return []

    unit_scale = ifcopenshell.util.unit.calculate_unit_scale(file)
    profile_pts_ifc = _get_profile_points_ifc(solid.SweptArea)
    if not profile_pts_ifc:
        return []

    depth_m = float(solid.Depth) * unit_scale
    n = len(profile_pts_ifc)
    pts_m = [(float(p[0]) * unit_scale, float(p[1]) * unit_scale) for p in profile_pts_ifc]
    candidates: list[dict] = []

    def world_pos(pt_idx: int, z_m: float):
        return _profile_vert_to_world_m(file, element, solid, pt_idx, z_m, placement_override)

    def midpoint(pa, pb):
        return ((pa[0] + pb[0]) * 0.5, (pa[1] + pb[1]) * 0.5, (pa[2] + pb[2]) * 0.5)

    for z_m in (0.0, depth_m):
        for i, (px_m, py_m) in enumerate(pts_m):
            wp = world_pos(i, z_m)
            if wp is None:
                continue
            candidates.append({
                "type": "VERTEX", "snap_world": wp,
                "profile_x_m": px_m, "profile_y_m": py_m,
                "extrusion_z_m": z_m, "snap": "VERTEX",
            })

            j = (i + 1) % n
            wpb = world_pos(j, z_m)
            if wpb is not None:
                jpx_m, jpy_m = pts_m[j]
                candidates.append({
                    "type": "EDGE",
                    "snap_world": midpoint(wp, wpb),
                    "v0": wp, "v1": wpb,
                    "profile_x_m": (px_m + jpx_m) * 0.5,
                    "profile_y_m": (py_m + jpy_m) * 0.5,
                    "extrusion_z_m": z_m, "snap": "EDGE",
                })

    for i, (px_m, py_m) in enumerate(pts_m):
        wpa = world_pos(i, 0.0)
        wpb = world_pos(i, depth_m)
        if wpa is not None and wpb is not None:
            candidates.append({
                "type": "EDGE",
                "snap_world": midpoint(wpa, wpb),
                "v0": wpa, "v1": wpb,
                "profile_x_m": px_m, "profile_y_m": py_m,
                "extrusion_z_m": depth_m * 0.5, "snap": "EDGE",
            })

    return candidates


# ---------------------------------------------------------------------------
# Profile anchor resolution
# ---------------------------------------------------------------------------


def _get_extrusion_solid(file: ifcopenshell.file, element: ifcopenshell.entity_instance):
    """Return the first IfcExtrudedAreaSolid found in the element's representations."""
    if not hasattr(element, "Representation") or not element.Representation:
        return None
    for rep in element.Representation.Representations:
        for item in rep.Items:
            solid = _unwrap_to_solid(item)
            if solid is not None and solid.is_a("IfcExtrudedAreaSolid"):
                return solid
    return None


def _unwrap_to_solid(item):
    """Recursively unwrap IfcMappedItem / IfcBooleanResult to find the underlying solid."""
    if item.is_a("IfcMappedItem"):
        items = item.MappingSource.MappedRepresentation.Items
        return _unwrap_to_solid(items[0]) if items else None
    if item.is_a("IfcBooleanResult"):
        return _unwrap_to_solid(item.FirstOperand)
    return item


def _get_profile_points_ifc(profile) -> list[tuple[float, float]]:
    """Return list of (x, y) profile vertices in IFC project units.

    Supports IfcRectangleProfileDef (derives 4 corners) and
    IfcArbitraryClosedProfileDef with IfcIndexedPolyCurve or IfcPolyline outer curves.
    """
    if profile.is_a("IfcRectangleProfileDef"):
        xd = float(profile.XDim)
        yd = float(profile.YDim)
        hx, hy = xd / 2.0, yd / 2.0
        cx, cy = 0.0, 0.0
        if hasattr(profile, "Position") and profile.Position and profile.Position.Location:
            loc = profile.Position.Location.Coordinates
            cx, cy = float(loc[0]), float(loc[1])
        return [(cx - hx, cy - hy), (cx + hx, cy - hy), (cx + hx, cy + hy), (cx - hx, cy + hy)]

    if profile.is_a("IfcArbitraryClosedProfileDef"):
        outer = profile.OuterCurve
        if outer.is_a("IfcIndexedPolyCurve"):
            coord_list = outer.Points.CoordList
            return [(float(c[0]), float(c[1])) for c in coord_list]
        if outer.is_a("IfcPolyline"):
            pts = [(float(p.Coordinates[0]), float(p.Coordinates[1])) for p in outer.Points]
            if len(pts) > 1 and pts[0] == pts[-1]:
                pts = pts[:-1]
            return pts

    return []


def _apply_axis2placement3d_m(
    file: ifcopenshell.file,
    placement,
    pt_m: tuple[float, float, float],
) -> tuple[float, float, float]:
    """Apply an IfcAxis2Placement3D to a point that is already in metres.

    Location.Coordinates are in IFC project units and are scaled by unit_scale.
    Rotation basis vectors (Axis, RefDirection) are dimensionless.
    """
    unit_scale = ifcopenshell.util.unit.calculate_unit_scale(file)
    loc = placement.Location.Coordinates
    ox = float(loc[0]) * unit_scale
    oy = float(loc[1]) * unit_scale
    oz = float(loc[2]) * unit_scale

    if placement.Axis:
        zr = placement.Axis.DirectionRatios
        zm = math.sqrt(zr[0] ** 2 + zr[1] ** 2 + zr[2] ** 2)
        zx, zy, zz = (zr[0] / zm, zr[1] / zm, zr[2] / zm) if zm > 1e-12 else (0.0, 0.0, 1.0)
    else:
        zx, zy, zz = 0.0, 0.0, 1.0

    if placement.RefDirection:
        xr = placement.RefDirection.DirectionRatios
        xm = math.sqrt(xr[0] ** 2 + xr[1] ** 2 + xr[2] ** 2)
        xx, xy, xz = (xr[0] / xm, xr[1] / xm, xr[2] / xm) if xm > 1e-12 else (1.0, 0.0, 0.0)
    else:
        xx, xy, xz = 1.0, 0.0, 0.0

    yx = zy * xz - zz * xy
    yy = zz * xx - zx * xz
    yz = zx * xy - zy * xx

    px, py, pz = pt_m
    return (
        ox + px * xx + py * yx + pz * zx,
        oy + px * xy + py * yy + pz * zy,
        oz + px * xz + py * yz + pz * zz,
    )


def _profile_vert_to_world_m(
    file: ifcopenshell.file,
    element: ifcopenshell.entity_instance,
    solid,
    pt_idx: int,
    extrusion_z_m: float,
    placement_override: Optional[dict] = None,
) -> Optional[tuple[float, float, float]]:
    """Convert a profile vertex index + extrusion distance to world-space metres.

    Coordinate flow (all in metres after unit_scale):
      1. Profile 2D point  → scale IFC coords by unit_scale
      2. Add extrusion offset along normalized ExtrudedDirection
      3. Apply solid.Position (IfcAxis2Placement3D) → element-local metres
      4. Apply element ObjectPlacement → world metres
    """
    unit_scale = ifcopenshell.util.unit.calculate_unit_scale(file)

    profile_pts_ifc = _get_profile_points_ifc(solid.SweptArea)
    if not profile_pts_ifc or pt_idx < 0 or pt_idx >= len(profile_pts_ifc):
        return None

    px_m = float(profile_pts_ifc[pt_idx][0]) * unit_scale
    py_m = float(profile_pts_ifc[pt_idx][1]) * unit_scale

    dr = solid.ExtrudedDirection.DirectionRatios
    mag = math.sqrt(sum(d * d for d in dr))
    if mag < 1e-12:
        return None
    ex, ey, ez = dr[0] / mag, dr[1] / mag, dr[2] / mag

    pt_solid_m = (
        px_m + ex * float(extrusion_z_m),
        py_m + ey * float(extrusion_z_m),
        ez * float(extrusion_z_m),
    )

    if solid.Position:
        pt_elem_m = _apply_axis2placement3d_m(file, solid.Position, pt_solid_m)
    else:
        pt_elem_m = pt_solid_m

    return _local_to_world_m(file, element, pt_elem_m, placement_override)


def _profile_coords_to_world_m(
    file: ifcopenshell.file,
    element: ifcopenshell.entity_instance,
    solid,
    px_m: float,
    py_m: float,
    extrusion_z_m: float,
    placement_override: Optional[dict] = None,
) -> Optional[tuple[float, float, float]]:
    """Convert profile-local coordinates (metres) + extrusion distance to world-space metres.

    Identical coordinate flow to ``_profile_vert_to_world_m`` but takes the
    profile 2-D position directly instead of a CoordList index.
    """
    dr = solid.ExtrudedDirection.DirectionRatios
    mag = math.sqrt(sum(d * d for d in dr))
    if mag < 1e-12:
        return None
    ex, ey, ez = dr[0] / mag, dr[1] / mag, dr[2] / mag

    pt_solid_m = (
        px_m + ex * float(extrusion_z_m),
        py_m + ey * float(extrusion_z_m),
        ez * float(extrusion_z_m),
    )

    if solid.Position:
        pt_elem_m = _apply_axis2placement3d_m(file, solid.Position, pt_solid_m)
    else:
        pt_elem_m = pt_solid_m

    return _local_to_world_m(file, element, pt_elem_m, placement_override)


def _resolve_profile_local_anchor(
    file: ifcopenshell.file,
    element: ifcopenshell.entity_instance,
    addr: dict,
    placement_override: Optional[dict] = None,
) -> Optional[tuple[float, float, float]]:
    """Resolve a PROFILE_LOCAL anchor to world-space metres.

    For VERTEX snap type, re-snaps to the nearest current profile vertex so that
    the anchor tracks correctly even when CoordList ordering changes after an
    ``update_representation`` call.  For EDGE snap type the stored midpoint
    coordinates are used directly (the midpoint is already between two vertices
    and is unambiguous after reordering).
    """
    profile_x_m = addr.get("profile_x_m")
    profile_y_m = addr.get("profile_y_m")
    extrusion_z_m = addr.get("extrusion_z_m")
    snap_type = addr.get("snap", "VERTEX")

    if profile_x_m is None or profile_y_m is None or extrusion_z_m is None:
        return None

    solid = _get_extrusion_solid(file, element)
    if solid is None:
        return None

    if snap_type == "VERTEX":
        unit_scale = ifcopenshell.util.unit.calculate_unit_scale(file)
        profile_pts = _get_profile_points_ifc(solid.SweptArea)
        if profile_pts:
            best_px, best_py, best_d2 = profile_x_m, profile_y_m, float("inf")
            for pt in profile_pts:
                px = float(pt[0]) * unit_scale
                py = float(pt[1]) * unit_scale
                d2 = (px - profile_x_m) ** 2 + (py - profile_y_m) ** 2
                if d2 < best_d2:
                    best_d2, best_px, best_py = d2, px, py
            profile_x_m, profile_y_m = best_px, best_py

    return _profile_coords_to_world_m(
        file, element, solid, profile_x_m, profile_y_m, extrusion_z_m, placement_override
    )


def _resolve_profile_vert_anchor(
    file: ifcopenshell.file,
    element: ifcopenshell.entity_instance,
    addr: dict,
    placement_override: Optional[dict] = None,
) -> Optional[tuple[float, float, float]]:
    pt_idx = addr.get("pt_idx")
    extrusion_z_m = addr.get("extrusion_z_m")
    if pt_idx is None or extrusion_z_m is None:
        return None
    solid = _get_extrusion_solid(file, element)
    if solid is None:
        return None
    return _profile_vert_to_world_m(file, element, solid, pt_idx, extrusion_z_m, placement_override)


def _resolve_profile_edge_anchor(
    file: ifcopenshell.file,
    element: ifcopenshell.entity_instance,
    addr: dict,
    placement_override: Optional[dict] = None,
) -> Optional[tuple[float, float, float]]:
    """Resolve a PROFILE_EDGE anchor to the world-space midpoint of the stored edge."""
    pt_idx_a = addr.get("pt_idx_a")
    extrusion_z_m_a = addr.get("extrusion_z_m_a")
    pt_idx_b = addr.get("pt_idx_b")
    extrusion_z_m_b = addr.get("extrusion_z_m_b")
    if any(v is None for v in (pt_idx_a, extrusion_z_m_a, pt_idx_b, extrusion_z_m_b)):
        return None
    solid = _get_extrusion_solid(file, element)
    if solid is None:
        return None
    pa = _profile_vert_to_world_m(file, element, solid, pt_idx_a, extrusion_z_m_a, placement_override)
    pb = _profile_vert_to_world_m(file, element, solid, pt_idx_b, extrusion_z_m_b, placement_override)
    if pa is None or pb is None:
        return None
    return ((pa[0] + pb[0]) * 0.5, (pa[1] + pb[1]) * 0.5, (pa[2] + pb[2]) * 0.5)


# ---------------------------------------------------------------------------
# Layer boundary anchor resolution
# ---------------------------------------------------------------------------


def _get_material_layer_usage(element: ifcopenshell.entity_instance):
    """Return the IfcMaterialLayerSetUsage for an element, or None."""
    import ifcopenshell.util.element as ifc_elem
    mat = ifc_elem.get_material(element, should_inherit=True)
    return mat if (mat and mat.is_a("IfcMaterialLayerSetUsage")) else None


def _resolve_layer_boundary_anchor(
    file: ifcopenshell.file,
    element: ifcopenshell.entity_instance,
    addr: dict,
    placement_override: Optional[dict] = None,
) -> Optional[tuple[float, float, float]]:
    """Resolve a LAYER_BOUNDARY anchor to world-space metres via a 6-tier fallback stack.

    Resolution tiers (first match wins):
      1. layer_id            → IfcMaterialLayer STEP id (most stable)
      2. layer_material_id   → IfcMaterial STEP id
      3. layer_material_name → IfcMaterial.Name
      4. layer_category      → IfcMaterialLayer.Category (IFC4)
      5. layer_index         → 0-based position in layer set
      6. Geometric fallback  → caller uses stored ``pt``
    """
    usage = _get_material_layer_usage(element)
    if usage is None:
        return None

    layers = list(usage.ForLayerSet.MaterialLayers)
    unit_scale = ifcopenshell.util.unit.calculate_unit_scale(file)

    # --- Identify target layer via tier stack ---
    target_idx: Optional[int] = None

    layer_id = addr.get("layer_id")
    if layer_id is not None and target_idx is None:
        for i, layer in enumerate(layers):
            if layer.id() == layer_id:
                target_idx = i
                break

    if target_idx is None:
        layer_material_id = addr.get("layer_material_id")
        if layer_material_id is not None:
            for i, layer in enumerate(layers):
                mat = getattr(layer, "Material", None)
                if mat and mat.id() == layer_material_id:
                    target_idx = i
                    break

    if target_idx is None:
        layer_material_name = addr.get("layer_material_name")
        if layer_material_name:
            for i, layer in enumerate(layers):
                mat = getattr(layer, "Material", None)
                if mat and mat.Name == layer_material_name:
                    target_idx = i
                    break

    if target_idx is None:
        layer_category = addr.get("layer_category")
        if layer_category:
            for i, layer in enumerate(layers):
                if getattr(layer, "Category", None) == layer_category:
                    target_idx = i
                    break

    if target_idx is None:
        stored_idx = addr.get("layer_index")
        if stored_idx is not None and 0 <= stored_idx < len(layers):
            target_idx = stored_idx

    if target_idx is None:
        return None  # tier 6: caller will use stored pt

    # --- Compute boundary offset along thickness axis ---
    ref_m = float(usage.OffsetFromReferenceLine) * unit_scale
    direction_sense = (getattr(usage, "DirectionSense", None) or "POSITIVE")
    thickness_axis = (getattr(usage, "LayerSetDirection", None) or "AXIS2")
    sense = 1.0 if direction_sense == "POSITIVE" else -1.0

    cumulative_m = ref_m
    target_offset_m: Optional[float] = None
    for i, layer in enumerate(layers):
        thickness_m = float(layer.LayerThickness) * unit_scale
        if i == target_idx:
            face = addr.get("face", "start")
            target_offset_m = cumulative_m if face == "start" else cumulative_m + sense * thickness_m
            break
        cumulative_m += sense * thickness_m

    if target_offset_m is None:
        return None

    # --- Convert to world position at profile centroid, mid-extrusion ---
    solid = _get_extrusion_solid(file, element)
    if solid is None:
        return None

    depth_m = float(solid.Depth) * unit_scale
    profile_pts_ifc = _get_profile_points_ifc(solid.SweptArea)
    centroid_x_m = 0.0
    centroid_y_m = 0.0
    if profile_pts_ifc:
        xs = [float(p[0]) * unit_scale for p in profile_pts_ifc]
        ys = [float(p[1]) * unit_scale for p in profile_pts_ifc]
        centroid_x_m = sum(xs) / len(xs)
        centroid_y_m = sum(ys) / len(ys)

    if thickness_axis == "AXIS3":
        return _profile_coords_to_world_m(
            file, element, solid, centroid_x_m, centroid_y_m, target_offset_m, placement_override
        )
    elif thickness_axis == "AXIS1":
        return _profile_coords_to_world_m(
            file, element, solid, target_offset_m, centroid_y_m, depth_m * 0.5, placement_override
        )
    else:  # AXIS2
        return _profile_coords_to_world_m(
            file, element, solid, centroid_x_m, target_offset_m, depth_m * 0.5, placement_override
        )


# ---------------------------------------------------------------------------
# Mesh extraction helpers
# ---------------------------------------------------------------------------


def _get_shape(file, element, settings, shape_cache):
    if shape_cache is None:
        shape_cache = {}
    elem_id = element.id()
    if elem_id in shape_cache:
        return shape_cache[elem_id]

    if settings is None:
        settings = ifcopenshell.geom.settings()
        # Do NOT set USE_WORLD_COORDS — tessellate in local (element-origin) space.
        # The geom kernel caches by representation ID; with USE_WORLD_COORDS=True,
        # moving an element would return stale world-space coords from the cache.
        # We apply the current placement manually via placement_override.
        settings.set("APPLY_DEFAULT_MATERIALS", False)

    try:
        shape = ifcopenshell.geom.create_shape(settings, element)
    except Exception:
        shape = None

    shape_cache[elem_id] = shape
    return shape


def _local_to_world_m(
    file: ifcopenshell.file,
    element: ifcopenshell.entity_instance,
    local_pt_m: tuple,
    placement_override: Optional[dict] = None,
) -> tuple[float, float, float]:
    """Convert a local-space point (metres, from create_shape without USE_WORLD_COORDS)
    to a world-space point in metres.

    When *placement_override* contains the element's STEP id, that 4×4 matrix
    (row-major, already in metres — typically ``np.array(obj.matrix_world)``) is
    used instead of reading ``element.ObjectPlacement`` from the IFC file.  This
    ensures that elements moved in the Blender viewport but not yet explicitly
    synced to IFC (via "Edit Object Placement") are handled correctly.

    Without an override, falls back to ``get_local_placement`` which reads the IFC
    placement and scales IFC-unit translation to metres via ``unit_scale``.
    """
    x, y, z = float(local_pt_m[0]), float(local_pt_m[1]), float(local_pt_m[2])
    if placement_override is not None and element.id() in placement_override:
        m = placement_override[element.id()]  # 4×4, metres, row-major
        return (
            float(m[0][0] * x + m[0][1] * y + m[0][2] * z + m[0][3]),
            float(m[1][0] * x + m[1][1] * y + m[1][2] * z + m[1][3]),
            float(m[2][0] * x + m[2][1] * y + m[2][2] * z + m[2][3]),
        )
    unit_scale = ifcopenshell.util.unit.calculate_unit_scale(file)
    m = ifcopenshell.util.placement.get_local_placement(element.ObjectPlacement)
    return (
        float(m[0][0] * x + m[0][1] * y + m[0][2] * z + m[0][3] * unit_scale),
        float(m[1][0] * x + m[1][1] * y + m[1][2] * z + m[1][3] * unit_scale),
        float(m[2][0] * x + m[2][1] * y + m[2][2] * z + m[2][3] * unit_scale),
    )


def _rotate_local_to_world(
    element: ifcopenshell.entity_instance,
    local_vec: tuple,
    placement_override: Optional[dict] = None,
) -> tuple[float, float, float]:
    """Rotate a direction vector from local to world space (no translation)."""
    x, y, z = float(local_vec[0]), float(local_vec[1]), float(local_vec[2])
    if placement_override is not None and element.id() in placement_override:
        m = placement_override[element.id()]
        return (
            float(m[0][0] * x + m[0][1] * y + m[0][2] * z),
            float(m[1][0] * x + m[1][1] * y + m[1][2] * z),
            float(m[2][0] * x + m[2][1] * y + m[2][2] * z),
        )
    m = ifcopenshell.util.placement.get_local_placement(element.ObjectPlacement)
    return (
        float(m[0][0] * x + m[0][1] * y + m[0][2] * z),
        float(m[1][0] * x + m[1][1] * y + m[1][2] * z),
        float(m[2][0] * x + m[2][1] * y + m[2][2] * z),
    )


def _extract_mesh(shape) -> tuple[list[tuple], list[tuple]]:
    """Return (verts, tris) from a tessellated shape."""
    vf = shape.geometry.verts
    ff = shape.geometry.faces
    verts = [(vf[i * 3], vf[i * 3 + 1], vf[i * 3 + 2]) for i in range(len(vf) // 3)]
    tris = [(ff[i * 3], ff[i * 3 + 1], ff[i * 3 + 2]) for i in range(len(ff) // 3)]
    return verts, tris


# ---------------------------------------------------------------------------
# Coplanar face grouping
# ---------------------------------------------------------------------------

_NORMAL_THRESHOLD = 0.005   # max angle deviation between coplanar normals (~0.3°)
_PLANE_THRESHOLD = 1e-4     # max distance from origin along normal (metres — matches geom output)


def _tri_normal(v0, v1, v2) -> tuple[float, float, float]:
    ax, ay, az = v1[0] - v0[0], v1[1] - v0[1], v1[2] - v0[2]
    bx, by, bz = v2[0] - v0[0], v2[1] - v0[1], v2[2] - v0[2]
    nx = ay * bz - az * by
    ny = az * bx - ax * bz
    nz = ax * by - ay * bx
    mag = math.sqrt(nx * nx + ny * ny + nz * nz)
    if mag < 1e-12:
        return (0.0, 0.0, 0.0)
    return (nx / mag, ny / mag, nz / mag)


def _dot(a, b) -> float:
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def _group_coplanar_tris(verts: list, tris: list) -> list[list[int]]:
    """Group triangle indices whose faces are coplanar (same normal + plane)."""
    n_tris = len(tris)
    normals: list[tuple] = []
    plane_d: list[float] = []

    for a, b, c in tris:
        n = _tri_normal(verts[a], verts[b], verts[c])
        normals.append(n)
        # plane distance: n · centroid
        cx = (verts[a][0] + verts[b][0] + verts[c][0]) / 3
        cy = (verts[a][1] + verts[b][1] + verts[c][1]) / 3
        cz = (verts[a][2] + verts[b][2] + verts[c][2]) / 3
        plane_d.append(n[0] * cx + n[1] * cy + n[2] * cz)

    assigned = [False] * n_tris
    groups: list[list[int]] = []

    for i in range(n_tris):
        if assigned[i]:
            continue
        group = [i]
        assigned[i] = True
        ni, di = normals[i], plane_d[i]
        if ni == (0.0, 0.0, 0.0):
            groups.append(group)
            continue
        for j in range(i + 1, n_tris):
            if assigned[j]:
                continue
            nj, dj = normals[j], plane_d[j]
            if nj == (0.0, 0.0, 0.0):
                continue
            dot_val = _dot(ni, nj)  # signed — opposite normals (dot≈-1) must NOT merge
            if dot_val > 1.0 - _NORMAL_THRESHOLD and abs(di - dj) < _PLANE_THRESHOLD:
                group.append(j)
                assigned[j] = True
        groups.append(group)

    return groups


def _tri_area(v0, v1, v2) -> float:
    ax, ay, az = v1[0] - v0[0], v1[1] - v0[1], v1[2] - v0[2]
    bx, by, bz = v2[0] - v0[0], v2[1] - v0[1], v2[2] - v0[2]
    cx = ay * bz - az * by
    cy = az * bx - ax * bz
    cz = ax * by - ay * bx
    return 0.5 * math.sqrt(cx * cx + cy * cy + cz * cz)


def _face_group_props(group: list[int], verts: list, tris: list) -> dict:
    """Compute normal, total area, and area-weighted centroid for a face group."""
    total_area = 0.0
    wx = wy = wz = 0.0
    nx = ny = nz = 0.0

    for idx in group:
        a, b, c = tris[idx]
        va, vb, vc = verts[a], verts[b], verts[c]
        area = _tri_area(va, vb, vc)
        total_area += area
        cx = (va[0] + vb[0] + vc[0]) / 3
        cy = (va[1] + vb[1] + vc[1]) / 3
        cz = (va[2] + vb[2] + vc[2]) / 3
        wx += cx * area
        wy += cy * area
        wz += cz * area
        n = _tri_normal(va, vb, vc)
        nx += n[0] * area
        ny += n[1] * area
        nz += n[2] * area

    if total_area < 1e-12:
        return {"normal": (0.0, 0.0, 1.0), "area": 0.0, "centroid": (wx, wy, wz)}

    centroid = (wx / total_area, wy / total_area, wz / total_area)

    mag = math.sqrt(nx * nx + ny * ny + nz * nz)
    if mag > 1e-12:
        normal: tuple[float, ...] = (nx / mag, ny / mag, nz / mag)
    else:
        normal = (0.0, 0.0, 1.0)

    return {"normal": normal, "area": total_area, "centroid": centroid}


# ---------------------------------------------------------------------------
# Face group matching
# ---------------------------------------------------------------------------

_NORMAL_MATCH_THRESHOLD = 0.02    # max dot-product deviation for normal match
_CENTROID_MAX_DIST = 10.0         # max IFC-unit distance for centroid proximity


def _dist(a, b) -> float:
    return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 + (a[2] - b[2]) ** 2)


def _best_group(
    group_props: list[dict],
    hit_normal: tuple,
    hit_location: tuple,
) -> Optional[tuple[int, dict]]:
    """Return (index, props) for the best face group matching a ray-cast hit."""
    best_score = -1.0
    best = None

    for i, props in enumerate(group_props):
        dot_val = _dot(props["normal"], hit_normal)
        if dot_val < 1.0 - _NORMAL_MATCH_THRESHOLD:
            continue
        dist = _dist(props["centroid"], hit_location)
        score = dot_val - dist / max(_CENTROID_MAX_DIST, 0.001) * 0.2
        if score > best_score:
            best_score = score
            best = (i, props)

    return best


def _find_by_local_normal(
    local_group_props: list[dict],
    world_group_props: list[dict],
    fp_normal_local: list,
    hint: Optional[list],
) -> Optional[tuple[float, float, float]]:
    """Return the world-space centroid of the face group whose element-local normal
    best matches *fp_normal_local*.  Matching in local space is rotation-invariant —
    moving or rotating the element does not change local normals, so the anchor
    correctly tracks the same face through placement changes and profile edits."""
    best_score = -1.0
    best_centroid = None

    for i, lp in enumerate(local_group_props):
        dot_val = _dot(lp["normal"], fp_normal_local)
        if dot_val < 1.0 - _NORMAL_MATCH_THRESHOLD:
            continue
        score = dot_val
        if hint:
            hint_dist = _dist(world_group_props[i]["centroid"], hint)
            score -= hint_dist / max(_CENTROID_MAX_DIST, 0.001) * 0.1
        if score > best_score:
            best_score = score
            best_centroid = world_group_props[i]["centroid"]

    return best_centroid


# ---------------------------------------------------------------------------
# Misc helpers
# ---------------------------------------------------------------------------


def _pt_or_none(pt) -> Optional[tuple[float, float, float]]:
    if pt:
        return (float(pt[0]), float(pt[1]), float(pt[2]))
    return None
