# This file was generated with the assistance of an AI coding tool.
# IfcQuery - IFC model interrogation CLI
# Copyright (C) 2026 Bruno Postle <bruno@postle.net>
#
# This file is part of IfcQuery.
#
# IfcQuery is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcQuery is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcQuery.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import annotations

from typing import Any

import ifcopenshell
import ifcopenshell.util.element
import ifcopenshell.util.placement

# ---------------------------------------------------------------------------
# Geometry summary helpers
# ---------------------------------------------------------------------------

_MAX_PROFILE_POINTS = 20


def _rc(coords) -> list[float]:
    """Round a coordinate sequence to 6 decimal places."""
    return [round(float(c), 6) for c in coords]


def _curve_points(curve) -> list | None:
    if curve.is_a("IfcPolyline"):
        return [_rc(p.Coordinates) for p in curve.Points]
    if curve.is_a("IfcIndexedPolyCurve"):
        return [_rc(c) for c in curve.Points.CoordList]
    return None


def _profile_summary(profile) -> dict:
    t = profile.is_a()
    result: dict[str, Any] = {"type": t}
    if t == "IfcRectangleProfileDef":
        result["x_dim"] = profile.XDim
        result["y_dim"] = profile.YDim
    elif t in ("IfcCircleProfileDef", "IfcCircleHollowProfileDef"):
        result["radius"] = profile.Radius
        if t == "IfcCircleHollowProfileDef":
            result["wall_thickness"] = profile.WallThickness
    elif t in ("IfcArbitraryClosedProfileDef", "IfcArbitraryProfileDefWithVoids"):
        pts = _curve_points(profile.OuterCurve)
        if pts is not None:
            if len(pts) <= _MAX_PROFILE_POINTS:
                result["points"] = pts
            else:
                result["point_count"] = len(pts)
    elif t == "IfcCompositeProfileDef":
        result["profiles"] = [_profile_summary(p) for p in profile.Profiles]
    return result


def _half_space_plane(half_space) -> dict | None:
    if not half_space.is_a("IfcHalfSpaceSolid"):
        return None
    surface = half_space.BaseSurface
    if not surface or not surface.is_a("IfcPlane"):
        return None
    pos = surface.Position
    loc = _rc(pos.Location.Coordinates)
    normal = _rc(pos.Axis.DirectionRatios) if pos.Axis else [0.0, 0.0, 1.0]
    return {"location": loc, "normal": normal}


def _walk_clipping(item) -> tuple:
    """Return (base_solid, [clipping_plane_dicts]) from a BooleanClippingResult chain."""
    planes = []
    current = item
    while current.is_a("IfcBooleanClippingResult"):
        plane = _half_space_plane(current.SecondOperand)
        if plane:
            planes.append(plane)
        current = current.FirstOperand
    return current, planes


def _swept_solid_dict(item) -> dict:
    result: dict[str, Any] = {"solid_type": item.is_a()}
    if item.is_a("IfcExtrudedAreaSolid"):
        result["depth"] = item.Depth
        if item.ExtrudedDirection:
            result["direction"] = _rc(item.ExtrudedDirection.DirectionRatios)
        if item.SweptArea:
            result["profile"] = _profile_summary(item.SweptArea)
    return result


def _summarize_rep(rep) -> dict:
    rep_type = rep.RepresentationType or ""
    result: dict[str, Any] = {"representation_type": rep_type}
    items = list(rep.Items)

    if rep_type == "MappedRepresentation":
        for item in items:
            if item.is_a("IfcMappedItem"):
                return _summarize_rep(item.MappingSource.MappedRepresentation)

    elif rep_type == "SweptSolid":
        result["solids"] = [_swept_solid_dict(item) for item in items]

    elif rep_type == "Clipping":
        solids = []
        for item in items:
            base, planes = _walk_clipping(item)
            solid = _swept_solid_dict(base)
            if planes:
                solid["clipping_planes"] = planes
            solids.append(solid)
        result["solids"] = solids

    elif rep_type == "CSG":
        ops = []
        for item in items:
            if hasattr(item, "Operator"):
                ops.append({"operator": str(item.Operator), "type": item.is_a()})
        if ops:
            result["operations"] = ops

    elif rep_type in ("Brep", "Tessellation", "SolidModel"):
        face_count = 0
        vertex_count = 0
        for item in items:
            if item.is_a("IfcPolygonalFaceSet"):
                face_count += len(item.Faces)
                vertex_count += len(item.Coordinates.CoordList)
            elif item.is_a("IfcFacetedBrep"):
                face_count += len(item.Outer.CfsFaces)
        if face_count:
            result["face_count"] = face_count
        if vertex_count:
            result["vertex_count"] = vertex_count

    return result


def _geometry_summary(element) -> dict | None:
    if not hasattr(element, "Representation") or not element.Representation:
        return None
    body_rep = next(
        (r for r in element.Representation.Representations if r.RepresentationIdentifier == "Body"),
        None,
    )
    if body_rep is None:
        return None
    try:
        return _summarize_rep(body_rep)
    except Exception:
        return None


def _serialize_attribute(value: Any) -> Any:
    """Convert an IFC attribute value to a JSON-serializable form."""
    if isinstance(value, ifcopenshell.entity_instance):
        return {"id": value.id(), "type": value.is_a()}
    if isinstance(value, tuple):
        return [_serialize_attribute(v) for v in value]
    return value


def _material_to_dict(material: ifcopenshell.entity_instance | None) -> dict[str, Any] | None:
    """Convert a material entity to a summary dict."""
    if material is None:
        return None
    result: dict[str, Any] = {
        "id": material.id(),
        "type": material.is_a(),
    }
    if hasattr(material, "Name"):
        result["name"] = material.Name
    return result


def info(model: ifcopenshell.file, element: ifcopenshell.entity_instance) -> dict[str, Any]:
    """Return deep inspection data for an element."""
    result: dict[str, Any] = {
        "id": element.id(),
        "type": element.is_a(),
    }

    # Direct attributes via get_info() which returns a dict of all attributes
    element_info = element.get_info()
    attrs = {}
    for key, value in element_info.items():
        if key in ("id", "type"):
            continue
        attrs[key] = _serialize_attribute(value)
    result["attributes"] = attrs

    # Property sets and quantity sets
    try:
        psets = ifcopenshell.util.element.get_psets(element)
        if psets:
            result["property_sets"] = psets
    except Exception:
        pass

    # Element type
    try:
        element_type = ifcopenshell.util.element.get_type(element)
        if element_type:
            type_info: dict[str, Any] = {
                "id": element_type.id(),
                "type": element_type.is_a(),
            }
            if hasattr(element_type, "Name"):
                type_info["name"] = element_type.Name
            result["element_type"] = type_info
    except Exception:
        pass

    # Material
    try:
        material = ifcopenshell.util.element.get_material(element)
        mat_dict = _material_to_dict(material)
        if mat_dict:
            result["material"] = mat_dict
    except Exception:
        pass

    # Spatial container
    try:
        container = ifcopenshell.util.element.get_container(element)
        if container:
            result["container"] = {
                "id": container.id(),
                "type": container.is_a(),
                "name": container.Name if hasattr(container, "Name") else None,
            }
    except Exception:
        pass

    # Placement (as 4x4 matrix)
    try:
        if hasattr(element, "ObjectPlacement") and element.ObjectPlacement:
            matrix = ifcopenshell.util.placement.get_local_placement(element.ObjectPlacement)
            result["placement"] = matrix.tolist()
    except Exception:
        pass

    # Geometry summary
    geom = _geometry_summary(element)
    if geom:
        result["geometry_summary"] = geom

    return result
