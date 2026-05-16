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
ifcopenshell.geom.create_shape() always outputs geometry in **metres** (its
internal unit), regardless of the IFC project's declared length unit (feet, mm,
etc.).  All anchor coordinates (``pt``, ``hint``, fingerprint ``centroid``) are
therefore stored in metres, which is also Blender world space.  The IFC
project's unit_scale is NOT applied here.  Callers that need IFC project units
must divide by ``ifcopenshell.util.unit.calculate_unit_scale(file)`` themselves.

Anchor schema (JSON-serialisable dict stored in BBIM_Dimension.Anchors):

  {
    "guid":  str | None,   # element GlobalId; None → WORLD type (free point)
    "type":  str,          # "FACE" | "CIRCLE_CENTER" | "WORLD"
    "addr":  {
      "method":      str,  # "ANALYTIC" | "TESS_INDEX" | "TESS_FINGERPRINT"
      "repr_id":     int,  # STEP id of representation item (ANALYTIC / TESS_INDEX)
      "repr_type":   str,  # IFC class of representation item
      "face_role":   str,  # "TOP" | "BOTTOM" | "SIDE_<n>" (IfcExtrudedAreaSolid only)
      "tess_index":  int,  # coplanar face-group index (-1 = skip)
      "fingerprint": {
        "normal":    [x, y, z],  # world-space unit normal (IFC project units)
        "area":      float,      # total face area
        "centroid":  [x, y, z]   # area-weighted centroid
      }
    } | None,
    "hint":  [x, y, z] | None,  # original click position for disambiguation
    "pt":    [x, y, z]           # last resolved position — used as fallback
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
      2. ANALYTIC for IfcExtrudedAreaSolid → analytical TOP/BOTTOM face centre.
      3. TESS_INDEX → centroid of a pre-recorded face group by index.
      4. TESS_FINGERPRINT → best face group matched by normal + centroid proximity.
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
    method = addr.get("method", "TESS_FINGERPRINT")

    # --- 1. Analytical path (fast, exact) ---
    if method == "ANALYTIC" and addr.get("repr_type") == "IfcExtrudedAreaSolid":
        pt = _resolve_extruded_area_solid_analytic(file, element, addr, placement_override)
        if pt is not None:
            return pt

    # --- 2 & 3. Tessellation path (universal) ---
    shape = _get_shape(file, element, settings, shape_cache)
    if shape is None:
        return _pt_or_none(anchor.get("pt"))

    verts, tris = _extract_mesh(shape)
    if not tris:
        return _pt_or_none(anchor.get("pt"))

    groups = _group_coplanar_tris(verts, tris)
    group_props = [_face_group_props(g, verts, tris) for g in groups]

    # group_props centroids/normals are in LOCAL metres (no USE_WORLD_COORDS).
    # Build world-space equivalents using placement_override (Blender matrix_world)
    # when available, otherwise fall back to element.ObjectPlacement from IFC.
    world_group_props = [
        {
            "centroid": _local_to_world_m(file, element, gp["centroid"], placement_override),
            "normal": _rotate_local_to_world(element, gp["normal"], placement_override),
            "area": gp["area"],
        }
        for gp in group_props
    ]

    fingerprint = addr.get("fingerprint")
    hint = anchor.get("hint")
    fp_normal_local = fingerprint.get("normal_local") if fingerprint else None

    # TESS_INDEX fast path — only accept when the local fingerprint normal still
    # matches at that index, guarding against face-group reordering after any
    # geometry edit or profile change.
    tess_index = addr.get("tess_index", -1)
    if 0 <= tess_index < len(groups):
        candidate_local = group_props[tess_index]
        if fp_normal_local is None or _dot(candidate_local["normal"], fp_normal_local) >= 1.0 - _NORMAL_MATCH_THRESHOLD:
            return world_group_props[tess_index]["centroid"]
        # Local-normal mismatch — face groups reordered; fall through to fingerprint.

    # TESS_FINGERPRINT — match by element-local normal (rotation-invariant).
    if fp_normal_local:
        pt = _find_by_local_normal(group_props, world_group_props, fp_normal_local, hint)
        if pt is not None:
            return pt
    elif fingerprint:
        # Legacy anchors built before normal_local was stored: fall back to
        # world-space normal matching (not rotation-invariant, but best we can do).
        pt = _find_by_fingerprint(world_group_props, fingerprint, hint)
        if pt is not None:
            return pt

    return _pt_or_none(anchor.get("pt"))


def build_anchor_from_hit(
    file: ifcopenshell.file,
    element: ifcopenshell.entity_instance,
    hit_location_ifc: tuple[float, float, float],
    hit_normal_ifc: tuple[float, float, float],
    settings: Optional[ifcopenshell.geom.settings] = None,
    shape_cache: Optional[dict] = None,
    placement_override: Optional[dict] = None,
) -> dict:
    """Build an anchor dict from a viewport ray-cast hit.

    Tessellates the element, finds the best-matching face group for the hit
    normal/location, computes the fingerprint, and optionally detects an
    IfcExtrudedAreaSolid face role (TOP/BOTTOM) for the analytical path.

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

    tess_index = -1
    fingerprint: dict = {
        "normal": list(hit_normal_ifc),
        "area": 0.0,
        "centroid": list(hit_location_ifc),
    }

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
            tess_index, props = best
            fingerprint = {
                # normal_local: element-local normal — rotation-invariant primary key.
                "normal_local": list(local_group_props[tess_index]["normal"]),
                # world-space fields kept for legacy / disambiguation.
                "normal": list(props["normal"]),
                "area": props["area"],
                "centroid": list(props["centroid"]),
            }

    repr_type, repr_id, face_role = _detect_extruded_face(
        file, element, hit_location_ifc, hit_normal_ifc, placement_override
    )
    method = "ANALYTIC" if repr_type == "IfcExtrudedAreaSolid" else "TESS_FINGERPRINT"

    return {
        "guid": element.GlobalId,
        "type": "FACE",
        "addr": {
            "method": method,
            "repr_id": repr_id,
            "repr_type": repr_type,
            "face_role": face_role,
            "tess_index": tess_index,
            "fingerprint": fingerprint,
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


def _world_normal_to_elem_local(
    file: ifcopenshell.file,
    element: ifcopenshell.entity_instance,
    world_normal: tuple,
    placement_override: Optional[dict] = None,
) -> tuple[float, float, float]:
    """Rotate a world-space direction into element-local space (rotation only, no translation).

    Uses placement_override (Blender matrix_world) when available so that
    elements moved/rotated in the viewport are handled correctly.
    """
    x, y, z = float(world_normal[0]), float(world_normal[1]), float(world_normal[2])
    if placement_override is not None and element.id() in placement_override:
        m = placement_override[element.id()]
        # Inverse rotation = transpose of the 3×3 rotation block.
        lx = float(m[0][0]) * x + float(m[1][0]) * y + float(m[2][0]) * z
        ly = float(m[0][1]) * x + float(m[1][1]) * y + float(m[2][1]) * z
        lz = float(m[0][2]) * x + float(m[1][2]) * y + float(m[2][2]) * z
    else:
        m = ifcopenshell.util.placement.get_local_placement(element.ObjectPlacement)
        lx = float(m[0][0]) * x + float(m[1][0]) * y + float(m[2][0]) * z
        ly = float(m[0][1]) * x + float(m[1][1]) * y + float(m[2][1]) * z
        lz = float(m[0][2]) * x + float(m[1][2]) * y + float(m[2][2]) * z
    mag = math.sqrt(lx * lx + ly * ly + lz * lz)
    if mag > 1e-12:
        return (lx / mag, ly / mag, lz / mag)
    return (x, y, z)


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
# Fingerprint matching
# ---------------------------------------------------------------------------

_NORMAL_MATCH_THRESHOLD = 0.02    # max dot-product deviation for normal match
_CENTROID_MAX_DIST = 10.0         # max IFC-unit distance for centroid proximity


def _dist(a, b) -> float:
    return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 + (a[2] - b[2]) ** 2)


def _find_by_fingerprint(
    group_props: list[dict],
    fingerprint: dict,
    hint: Optional[list],
) -> Optional[tuple[float, float, float]]:
    """Return the centroid of the best-matching face group."""
    fp_normal = fingerprint["normal"]
    fp_centroid = fingerprint["centroid"]

    best_score = -1.0
    best_centroid = None

    for props in group_props:
        dot_val = _dot(props["normal"], fp_normal)
        if dot_val < 1.0 - _NORMAL_MATCH_THRESHOLD:
            continue  # wrong-facing face

        # Score: prefer face whose centroid is closest to stored fingerprint centroid,
        # then to the original click hint.
        centroid_dist = _dist(props["centroid"], fp_centroid)
        if centroid_dist > _CENTROID_MAX_DIST:
            continue

        score = dot_val - centroid_dist / _CENTROID_MAX_DIST * 0.3
        if hint:
            hint_dist = _dist(props["centroid"], hint)
            score -= hint_dist / _CENTROID_MAX_DIST * 0.1

        if score > best_score:
            best_score = score
            best_centroid = props["centroid"]

    return best_centroid


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
# Analytical resolution — IfcExtrudedAreaSolid TOP / BOTTOM / SIDE_*
# ---------------------------------------------------------------------------


def _resolve_extruded_area_solid_analytic(
    file: ifcopenshell.file,
    element: ifcopenshell.entity_instance,
    addr: dict,
    placement_override: Optional[dict] = None,
) -> Optional[tuple[float, float, float]]:
    """Analytically resolve a face centre of an IfcExtrudedAreaSolid.

    Handles TOP, BOTTOM, and SIDE_PLUS_X / SIDE_MINUS_X / SIDE_PLUS_Y / SIDE_MINUS_Y
    roles.  Side-face roles are only supported for IfcRectangleProfileDef; other
    profile types fall back to tessellation fingerprint matching.
    """
    face_role = addr.get("face_role", "")
    _top_bottom = ("TOP", "BOTTOM")
    _sides = ("SIDE_PLUS_X", "SIDE_MINUS_X", "SIDE_PLUS_Y", "SIDE_MINUS_Y")
    if face_role not in _top_bottom + _sides:
        return None

    repr_id = addr.get("repr_id")
    if not repr_id:
        return None

    try:
        solid = file.by_id(repr_id)
    except Exception:
        return None

    if not solid.is_a("IfcExtrudedAreaSolid"):
        return None

    try:
        profile = solid.SweptArea
        dir_ratios = solid.ExtrudedDirection.DirectionRatios
        depth = float(solid.Depth)

        mag = math.sqrt(sum(d * d for d in dir_ratios))
        if mag < 1e-12:
            return None
        dir_vec = tuple(d / mag for d in dir_ratios)

        if face_role in _top_bottom:
            profile_centroid_local = _profile_centroid(profile)
            scale = depth if face_role == "TOP" else 0.0
            px = profile_centroid_local[0] + dir_vec[0] * scale
            py = profile_centroid_local[1] + dir_vec[1] * scale
            pz = dir_vec[2] * scale

        else:  # SIDE_* — only for IfcRectangleProfileDef
            if not profile.is_a("IfcRectangleProfileDef"):
                return None

            x_dim = float(profile.XDim)
            y_dim = float(profile.YDim)
            half_depth = depth / 2.0

            # Profile centre and local axes (from profile.Position 2D placement).
            cx, cy = 0.0, 0.0
            px_axis = (1.0, 0.0)  # profile X in profile 2D
            if hasattr(profile, "Position") and profile.Position:
                loc = profile.Position.Location
                cx = float(loc.Coordinates[0])
                cy = float(loc.Coordinates[1])
                if profile.Position.RefDirection:
                    pr = profile.Position.RefDirection.DirectionRatios
                    pm = math.sqrt(pr[0] ** 2 + pr[1] ** 2)
                    if pm > 1e-12:
                        px_axis = (pr[0] / pm, pr[1] / pm)
            py_axis = (-px_axis[1], px_axis[0])  # 90° rotation

            half_x = x_dim / 2.0
            half_y = y_dim / 2.0

            if face_role == "SIDE_PLUS_X":
                fx = cx + half_x * px_axis[0]
                fy = cy + half_x * px_axis[1]
            elif face_role == "SIDE_MINUS_X":
                fx = cx - half_x * px_axis[0]
                fy = cy - half_x * px_axis[1]
            elif face_role == "SIDE_PLUS_Y":
                fx = cx + half_y * py_axis[0]
                fy = cy + half_y * py_axis[1]
            else:  # SIDE_MINUS_Y
                fx = cx - half_y * py_axis[0]
                fy = cy - half_y * py_axis[1]

            # Lift from profile 2D to solid-local 3D at mid-extrusion depth.
            px = fx + dir_vec[0] * half_depth
            py = fy + dir_vec[1] * half_depth
            pz = dir_vec[2] * half_depth

        if solid.Position:
            local_pt = _apply_axis2placement3d(solid.Position, (px, py, pz))
        else:
            local_pt = (px, py, pz)

        # Apply element placement — use placement_override (Blender matrix_world, metres)
        # when available so that unsync'd viewport moves are reflected.
        return _local_to_world_m(file, element, local_pt, placement_override)
    except Exception:
        return None


def _profile_centroid(profile) -> tuple[float, float]:
    """Return (x, y) centroid of a profile def in its local 2D space."""
    if profile.is_a("IfcRectangleProfileDef"):
        pos = profile.Position
        if pos:
            loc = pos.Location
            return (loc.Coordinates[0], loc.Coordinates[1])
        return (0.0, 0.0)
    if profile.is_a("IfcCircleProfileDef"):
        pos = profile.Position
        if pos:
            loc = pos.Location
            return (loc.Coordinates[0], loc.Coordinates[1])
        return (0.0, 0.0)
    # Fallback for arbitrary profiles — use position location if available
    if hasattr(profile, "Position") and profile.Position:
        loc = profile.Position.Location
        return (loc.Coordinates[0], loc.Coordinates[1])
    return (0.0, 0.0)


def _apply_axis2placement3d(placement, pt: tuple) -> tuple[float, float, float]:
    """Apply an IfcAxis2Placement3D to a local point."""
    loc = placement.Location.Coordinates
    ox, oy, oz = float(loc[0]), float(loc[1]), float(loc[2])

    # Z axis (extrusion direction in placement space)
    if placement.Axis:
        zr = placement.Axis.DirectionRatios
        zx, zy, zz = float(zr[0]), float(zr[1]), float(zr[2])
    else:
        zx, zy, zz = 0.0, 0.0, 1.0

    # X axis (ref direction)
    if placement.RefDirection:
        xr = placement.RefDirection.DirectionRatios
        xx, xy, xz = float(xr[0]), float(xr[1]), float(xr[2])
    else:
        xx, xy, xz = 1.0, 0.0, 0.0

    # Y axis = Z × X
    yx = zy * xz - zz * xy
    yy = zz * xx - zx * xz
    yz = zx * xy - zy * xx

    px, py, pz = pt
    return (
        ox + px * xx + py * yx + pz * zx,
        oy + px * xy + py * yy + pz * zy,
        oz + px * xz + py * yz + pz * zz,
    )


def _mat_apply(m, pt: tuple) -> tuple[float, float, float]:
    """Apply a 4×4 numpy placement matrix to a point."""
    x, y, z = float(pt[0]), float(pt[1]), float(pt[2])
    return (
        float(m[0][0] * x + m[0][1] * y + m[0][2] * z + m[0][3]),
        float(m[1][0] * x + m[1][1] * y + m[1][2] * z + m[1][3]),
        float(m[2][0] * x + m[2][1] * y + m[2][2] * z + m[2][3]),
    )


# ---------------------------------------------------------------------------
# IfcExtrudedAreaSolid face role detection
# ---------------------------------------------------------------------------


def _detect_extruded_face(
    file: ifcopenshell.file,
    element: ifcopenshell.entity_instance,
    hit_location: tuple,
    hit_normal: tuple,
    placement_override: Optional[dict] = None,
) -> tuple[str, int, str]:
    """Identify if the hit face is a face of an IfcExtrudedAreaSolid.

    Returns (repr_type, repr_id, face_role).
    face_role is one of: 'TOP', 'BOTTOM', 'SIDE_PLUS_X', 'SIDE_MINUS_X',
    'SIDE_PLUS_Y', 'SIDE_MINUS_Y', or '' (not recognized).
    Side roles are only returned for IfcRectangleProfileDef.
    """
    if not hasattr(element, "Representation") or not element.Representation:
        return ("", -1, "")

    # Transform hit_normal from world → element-local for accurate role classification.
    hit_normal_elem = _world_normal_to_elem_local(file, element, hit_normal, placement_override)

    for rep in element.Representation.Representations:
        for item in rep.Items:
            solid = _unwrap_mapped(item)
            if not solid or not solid.is_a("IfcExtrudedAreaSolid"):
                continue
            role = _extruded_face_role(solid, hit_normal_elem)
            if role:
                return ("IfcExtrudedAreaSolid", solid.id(), role)

    return ("", -1, "")


def _unwrap_mapped(item):
    """Unwrap IfcMappedItem to its underlying representation item (first item)."""
    if item.is_a("IfcMappedItem"):
        items = item.MappingSource.MappedRepresentation.Items
        return items[0] if items else None
    return item


def _apply_axis2placement3d_rotation_inv(placement, vec: tuple) -> tuple[float, float, float]:
    """Apply the inverse rotation of an IfcAxis2Placement3D to a direction.

    Transforms a direction from element-local space into solid-local space.
    The rotation matrix R = [x_axis | y_axis | z_axis]; its inverse for an
    orthogonal matrix is R^T, computed here by dotting with each basis vector.
    """
    if placement is None:
        return vec

    x, y, z = float(vec[0]), float(vec[1]), float(vec[2])

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

    # Y = Z × X
    yx = zy * xz - zz * xy
    yy = zz * xx - zx * xz
    yz = zx * xy - zy * xx

    # R^T: dot input with each column of R (= each basis axis of the placement).
    inv_x = xx * x + xy * y + xz * z
    inv_y = yx * x + yy * y + yz * z
    inv_z = zx * x + zy * y + zz * z

    mag = math.sqrt(inv_x ** 2 + inv_y ** 2 + inv_z ** 2)
    if mag > 1e-12:
        return (inv_x / mag, inv_y / mag, inv_z / mag)
    return vec


def _extruded_face_role(solid, hit_normal_elem_local: tuple) -> str:
    """Classify the hit face role on an IfcExtrudedAreaSolid.

    Returns 'TOP', 'BOTTOM', 'SIDE_PLUS_X', 'SIDE_MINUS_X', 'SIDE_PLUS_Y',
    'SIDE_MINUS_Y', or ''.  Side roles require IfcRectangleProfileDef.

    :param hit_normal_elem_local: Face normal in element-local space.
    """
    try:
        # Map from element-local to solid-local via solid.Position inverse rotation.
        hit_normal_solid = _apply_axis2placement3d_rotation_inv(solid.Position, hit_normal_elem_local)

        dr = solid.ExtrudedDirection.DirectionRatios
        mag = math.sqrt(sum(d * d for d in dr))
        if mag < 1e-12:
            return ""
        extrude_dir = tuple(d / mag for d in dr)

        dot_extrude = _dot(extrude_dir, hit_normal_solid)
        if dot_extrude > 0.99:
            return "TOP"
        if dot_extrude < -0.99:
            return "BOTTOM"

        # Side face detection — only supported for IfcRectangleProfileDef.
        if not solid.SweptArea.is_a("IfcRectangleProfileDef"):
            return ""

        profile = solid.SweptArea

        # Profile X axis in solid-local 2D (from profile.Position.RefDirection).
        px_axis = (1.0, 0.0)
        if hasattr(profile, "Position") and profile.Position and profile.Position.RefDirection:
            pr = profile.Position.RefDirection.DirectionRatios
            pm = math.sqrt(pr[0] ** 2 + pr[1] ** 2)
            if pm > 1e-12:
                px_axis = (pr[0] / pm, pr[1] / pm)
        py_axis = (-px_axis[1], px_axis[0])  # 90° CCW

        # Lift 2D profile axes to solid-local 3D (profile is in the solid XY plane).
        px_3d = (px_axis[0], px_axis[1], 0.0)
        py_3d = (py_axis[0], py_axis[1], 0.0)

        dot_x = _dot(hit_normal_solid, px_3d)
        dot_y = _dot(hit_normal_solid, py_3d)

        if abs(dot_x) > 0.99:
            return "SIDE_PLUS_X" if dot_x > 0 else "SIDE_MINUS_X"
        if abs(dot_y) > 0.99:
            return "SIDE_PLUS_Y" if dot_y > 0 else "SIDE_MINUS_Y"

    except Exception:
        pass
    return ""


# ---------------------------------------------------------------------------
# Misc helpers
# ---------------------------------------------------------------------------


def _pt_or_none(pt) -> Optional[tuple[float, float, float]]:
    if pt:
        return (float(pt[0]), float(pt[1]), float(pt[2]))
    return None
