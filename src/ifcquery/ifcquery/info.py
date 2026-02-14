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

    return result
