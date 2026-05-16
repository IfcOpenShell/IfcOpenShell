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

"""Regenerate a parametric dimension annotation from its BBIM_DimensionTarget anchors.

This module operates purely on IFC data.  It:
  1. Reads the ``Anchors`` JSON array from the ``BBIM_DimensionTarget`` pset on an
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


_PSET_NAME = "BBIM_DimensionTarget"
_METRIC_INTENT_PREFIX = "PARAMETRIC_DIMENSION_SEG_"


def regenerate_dimension(
    file: ifcopenshell.file,
    annotation: ifcopenshell.entity_instance,
    settings: Optional[ifcopenshell.geom.settings] = None,
    shape_cache: Optional[dict] = None,
    placement_override: Optional[dict] = None,
) -> list[tuple[float, float, float]]:
    """Regenerate a parametric dimension from its stored anchor references.

    Resolves every anchor in ``BBIM_DimensionTarget.Anchors``, updates the
    per-segment ``IfcMetric`` values (creating them when absent), and returns
    the resolved world-space points in metres.

    :param file: The open IFC file.
    :param annotation: An ``IfcAnnotation`` with a ``BBIM_DimensionTarget`` pset.
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

    return [pt for pt in resolved if pt is not None]


def get_dimension_segment_lengths(
    file: ifcopenshell.file,
    annotation: ifcopenshell.entity_instance,
) -> list[float]:
    """Return the segment lengths for a parametric dimension from stored anchor pts.

    Distances are computed from the cached ``pt`` fields in ``BBIM_DimensionTarget.Anchors``
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
