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

"""Regenerate a parametric dimension annotation from its BBIM_Dimension anchors.

This module operates purely on IFC data.  It:
  1. Reads the ``Anchors`` JSON array from the ``BBIM_Dimension`` pset on an
     ``IfcAnnotation``.
  2. Resolves each anchor to a world-space point (IFC project units) using
     ``resolve_anchor``.
  3. Computes per-segment distances and updates (or creates) the linked
     ``IfcMetric`` + ``IfcRelAssociatesConstraint`` entities.
  4. Returns the ordered list of resolved world-space points so that the
     Bonsai operator layer can update the Blender curve object.

Updating the Blender curve (converting IFC world coords → annotation local
coords) is the *caller's* responsibility and does **not** happen here.
"""

from __future__ import annotations

import json
import math
from typing import Optional

import ifcopenshell
import ifcopenshell.api.owner
import ifcopenshell.api.pset
import ifcopenshell.geom
import ifcopenshell.guid
import ifcopenshell.util.element

from .resolve_anchor import resolve_anchor


_PSET_NAME = "BBIM_Dimension"
_METRIC_INTENT_PREFIX = "PARAMETRIC_DIMENSION_SEG_"


def regenerate_dimension(
    file: ifcopenshell.file,
    annotation: ifcopenshell.entity_instance,
    settings: Optional[ifcopenshell.geom.settings] = None,
    shape_cache: Optional[dict] = None,
    placement_override: Optional[dict] = None,
) -> list[tuple[float, float, float]]:
    """Regenerate a parametric dimension from its stored anchor references.

    Resolves every anchor in ``BBIM_Dimension.Anchors``, updates the
    per-segment ``IfcMetric`` values (creating them when absent), and returns
    the resolved world-space points in metres.

    :param file: The open IFC file.
    :param annotation: An ``IfcAnnotation`` with a ``BBIM_Dimension`` pset.
    :param settings: Geometry settings for tessellation (shared across calls).
    :param shape_cache: Shape cache dict (shared across calls for performance).
    :param placement_override: Optional dict mapping element STEP id → 4×4 numpy
        matrix (metres, row-major).  Pass ``{elem.id(): np.array(obj.matrix_world)}``
        for each referenced element so that viewport moves not yet synced to the
        IFC ``ObjectPlacement`` are reflected.  See ``resolve_anchor`` for details.
    :return: Ordered list of ``(x, y, z)`` tuples, one per anchor.
             Empty list if the pset is missing or malformed.
    """
    pset_data = ifcopenshell.util.element.get_pset(annotation, _PSET_NAME)
    if not pset_data or "Anchors" not in pset_data:
        return []

    try:
        anchors: list[dict] = json.loads(pset_data["Anchors"])
    except (json.JSONDecodeError, TypeError):
        return []

    if not anchors:
        return []

    if shape_cache is None:
        shape_cache = {}

    resolved: list[Optional[tuple]] = []
    for anchor in anchors:
        pt = resolve_anchor(file, anchor, settings, shape_cache, placement_override)
        if pt is None:
            pt = tuple(anchor["pt"]) if anchor.get("pt") else (0.0, 0.0, 0.0)
        resolved.append(pt)
        anchor["pt"] = list(pt)

    # ForcePerpendicularToFace: project vertices 1…n onto the line through
    # pt[0] in the direction of anchor[0]'s face normal, so the polyline is
    # constrained perpendicular to the face the first vertex is anchored to.
    if pset_data.get("ForcePerpendicularToFace") and len(resolved) >= 2 and resolved[0] is not None:
        normal = _get_anchor_face_normal_world(file, anchors[0], placement_override)
        if normal:
            base = resolved[0]
            for i in range(1, len(resolved)):
                if resolved[i] is None:
                    continue
                pt = resolved[i]
                t = ((pt[0] - base[0]) * normal[0]
                     + (pt[1] - base[1]) * normal[1]
                     + (pt[2] - base[2]) * normal[2])
                resolved[i] = (base[0] + t * normal[0],
                                base[1] + t * normal[1],
                                base[2] + t * normal[2])
                anchors[i]["pt"] = list(resolved[i])

    pset_entity_id = pset_data.get("id")
    if pset_entity_id:
        pset_entity = file.by_id(pset_entity_id)
        ifcopenshell.api.pset.edit_pset(
            file,
            pset=pset_entity,
            properties={"Anchors": json.dumps(anchors)},
        )

    n_segments = len(resolved) - 1
    if n_segments >= 1:
        existing_metrics = _get_segment_metrics(file, annotation)
        _sync_segment_metrics(file, annotation, resolved, existing_metrics)

    # LinePosition: project all points to a fixed absolute world coordinate along the
    # horizontal offset axis (perpendicular to the dimension direction).  Applied after
    # the pset write so anchor["pt"] always stores the true geometry surface hit.
    # Because it is absolute, the dimension line stays put even if the geometry moves.
    # Only active when ForcePerpendicularToFace is also set — the two are semantically coupled.
    line_position = pset_data.get("LinePosition")
    if line_position is not None and pset_data.get("ForcePerpendicularToFace") and resolved:
        face_normal = _get_anchor_face_normal_world(file, anchors[0], placement_override)
        offset_dir = _get_line_offset_direction(face_normal, [pt for pt in resolved if pt is not None])
        if offset_dir:
            resolved = [
                _project_to_line_position(pt, offset_dir, float(line_position)) if pt is not None else None
                for pt in resolved
            ]

    return [pt for pt in resolved if pt is not None]


def get_dimension_segment_lengths(
    file: ifcopenshell.file,
    annotation: ifcopenshell.entity_instance,
) -> list[float]:
    """Return the segment lengths for a parametric dimension from stored anchor pts.

    Distances are computed from the cached ``pt`` fields in ``BBIM_Dimension.Anchors``
    (in metres, matching ifcopenshell.geom output).  Returns an empty list if the pset
    is absent or malformed.
    """
    pset_data = ifcopenshell.util.element.get_pset(annotation, _PSET_NAME)
    if not pset_data or not pset_data.get("Anchors"):
        return []
    try:
        anchors: list[dict] = json.loads(pset_data["Anchors"])
    except Exception:
        return []
    lengths: list[float] = []
    for i in range(len(anchors) - 1):
        pt_a = anchors[i].get("pt")
        pt_b = anchors[i + 1].get("pt")
        if pt_a and pt_b:
            lengths.append(_dist(tuple(pt_a), tuple(pt_b)))
        else:
            lengths.append(0.0)
    return lengths


# ---------------------------------------------------------------------------
# IfcMetric / IfcRelAssociatesConstraint management
# ---------------------------------------------------------------------------


def _get_segment_metrics(
    file: ifcopenshell.file,
    annotation: ifcopenshell.entity_instance,
) -> dict[int, ifcopenshell.entity_instance]:
    """Return {segment_index: IfcMetric} for all constraint rels on the annotation."""
    metrics: dict[int, ifcopenshell.entity_instance] = {}
    for rel in annotation.HasAssociations:
        if not rel.is_a("IfcRelAssociatesConstraint"):
            continue
        intent: str = rel.Intent or ""
        if not intent.startswith(_METRIC_INTENT_PREFIX):
            continue
        try:
            seg_idx = int(intent[len(_METRIC_INTENT_PREFIX):])
        except ValueError:
            continue
        constraint = rel.RelatingConstraint
        if constraint.is_a("IfcMetric"):
            metrics[seg_idx] = constraint
    return metrics


def _sync_segment_metrics(
    file: ifcopenshell.file,
    annotation: ifcopenshell.entity_instance,
    resolved_pts: list[tuple],
    existing: dict[int, ifcopenshell.entity_instance],
) -> None:
    """Create missing and update existing IfcMetric entities for each segment."""
    n_segments = len(resolved_pts) - 1
    seen_guids: set[str] = set()

    # Build a lookup of which elements are at each anchor endpoint
    pset_data = ifcopenshell.util.element.get_pset(annotation, _PSET_NAME)
    anchors: list[dict] = []
    if pset_data and pset_data.get("Anchors"):
        try:
            anchors = json.loads(pset_data["Anchors"])
        except Exception:
            pass

    for seg_idx in range(n_segments):
        if seg_idx in existing:
            pass  # metric already exists; association is still valid
        else:
            # Create new IfcMetric + IfcRelAssociatesConstraint
            # DataValue is IfcMetricValueSelect (entity-only SELECT in IFC4) — omit it;
            # the measured distance is derivable from the anchor pt fields.
            metric = file.create_entity(
                "IfcMetric",
                Name=f"seg_{seg_idx}",
                ConstraintGrade="ADVISORY",
                Benchmark="EQUALTO",
            )
            # Gather related products for this segment (the two anchor elements)
            related: list[ifcopenshell.entity_instance] = [annotation]
            for anchor_idx in (seg_idx, seg_idx + 1):
                if anchor_idx < len(anchors):
                    guid = anchors[anchor_idx].get("guid")
                    if guid and guid not in seen_guids:
                        try:
                            elem = file.by_guid(guid)
                            related.append(elem)
                            seen_guids.add(guid)
                        except Exception:
                            pass

            file.create_entity(
                "IfcRelAssociatesConstraint",
                GlobalId=ifcopenshell.guid.new(),
                OwnerHistory=ifcopenshell.api.owner.create_owner_history(file),
                Intent=f"{_METRIC_INTENT_PREFIX}{seg_idx}",
                RelatingConstraint=metric,
                RelatedObjects=related,
            )

    # Remove orphaned metrics for segments that no longer exist
    for seg_idx, metric in existing.items():
        if seg_idx >= n_segments:
            for rel in file.get_inverse(metric):
                if rel.is_a("IfcRelAssociatesConstraint"):
                    file.remove(rel)
            file.remove(metric)


def _dist(a: tuple, b: tuple) -> float:
    return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 + (a[2] - b[2]) ** 2)


def _project_to_line_position(
    pt: tuple, offset_dir: tuple, target: float
) -> tuple[float, float, float]:
    """Shift *pt* along *offset_dir* so its projection onto that axis equals *target*.

    Keeps every other component of the point unchanged, so only the dimension line
    is repositioned — the measured length stays the same.
    """
    current = pt[0] * offset_dir[0] + pt[1] * offset_dir[1] + pt[2] * offset_dir[2]
    delta = target - current
    return (
        pt[0] + delta * offset_dir[0],
        pt[1] + delta * offset_dir[1],
        pt[2] + delta * offset_dir[2],
    )


def _get_anchor_face_normal_world(
    file: ifcopenshell.file,
    anchor: dict,
    placement_override: Optional[dict] = None,
) -> Optional[tuple[float, float, float]]:
    """Return the world-space unit face normal stored in a FACE anchor, or None.

    Prefers ``normal_local`` (element-local, rotation-invariant) transformed by
    the current element placement.  Falls back to the stored world-space normal.
    """
    if anchor.get("type") != "FACE":
        return None
    guid = anchor.get("guid")
    if not guid:
        return None
    fp = (anchor.get("addr") or {}).get("fingerprint") or {}

    normal_local = fp.get("normal_local")
    if normal_local:
        try:
            element = file.by_guid(guid)
        except Exception:
            return None
        from .resolve_anchor import _rotate_local_to_world
        n = _rotate_local_to_world(element, normal_local, placement_override)
        mag = math.sqrt(n[0] ** 2 + n[1] ** 2 + n[2] ** 2)
        return (n[0] / mag, n[1] / mag, n[2] / mag) if mag > 1e-12 else None

    normal_world = fp.get("normal")
    if normal_world:
        mag = math.sqrt(sum(x * x for x in normal_world))
        return tuple(x / mag for x in normal_world) if mag > 1e-12 else None  # type: ignore[return-value]

    return None


def _get_line_offset_direction(
    face_normal: Optional[tuple[float, float, float]],
    resolved_pts: list[tuple],
) -> Optional[tuple[float, float, float]]:
    """Return the direction to apply LineOffset — parallel to the first face.

    Uses cross(world_Z, dim_direction) to get the horizontal direction
    perpendicular to the dimension line, which slides the line sideways
    (parallel to the face) rather than into/out of it.

    Falls back to cross(face_normal, world_Z) when the dimension line is
    nearly vertical (e.g. elevation dimensions).
    """
    world_z = (0.0, 0.0, 1.0)

    # Primary: use the dimension line direction (anchor[0] → anchor[1])
    if len(resolved_pts) >= 2:
        a, b = resolved_pts[0], resolved_pts[1]
        dx, dy, dz = b[0] - a[0], b[1] - a[1], b[2] - a[2]
        dim_mag = math.sqrt(dx * dx + dy * dy + dz * dz)
        if dim_mag > 1e-10:
            dim_dir = (dx / dim_mag, dy / dim_mag, dz / dim_mag)
            # cross(world_Z, dim_dir) — horizontal direction perp to dimension
            d = (
                world_z[1] * dim_dir[2] - world_z[2] * dim_dir[1],
                world_z[2] * dim_dir[0] - world_z[0] * dim_dir[2],
                world_z[0] * dim_dir[1] - world_z[1] * dim_dir[0],
            )
            mag = math.sqrt(d[0] ** 2 + d[1] ** 2 + d[2] ** 2)
            if mag > 1e-6:
                return (d[0] / mag, d[1] / mag, d[2] / mag)

    # Fallback for vertical dims: cross(face_normal, world_Z)
    if face_normal:
        n = face_normal
        d = (
            n[1] * world_z[2] - n[2] * world_z[1],
            n[2] * world_z[0] - n[0] * world_z[2],
            n[0] * world_z[1] - n[1] * world_z[0],
        )
        mag = math.sqrt(d[0] ** 2 + d[1] ** 2 + d[2] ** 2)
        if mag > 1e-6:
            return (d[0] / mag, d[1] / mag, d[2] / mag)

    return None
