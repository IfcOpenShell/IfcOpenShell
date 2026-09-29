# This file was generated with the assistance of an AI coding tool.
from __future__ import annotations

from typing import Any

import ifcopenshell
import ifcopenshell.util.doc


def schema(model: ifcopenshell.file, entity_type: str) -> dict[str, Any]:
    """Look up the IFC documentation for an entity class.

    Returns the class ``description``, its ``predefined_types``, per-attribute
    documentation and a ``spec_url``, resolved against the model's schema
    version. Returns an ``error`` key for an unknown class.

    :param model: The in-memory IFC model, used only for its schema version.
    :param entity_type: IFC class name, for example ``'IfcWall'``.
    """
    schema_name = model.schema
    try:
        doc = ifcopenshell.util.doc.get_entity_doc(schema_name, entity_type)
    except Exception:
        return {"error": f"Unknown entity: {entity_type}"}
    if not doc:
        return {"error": f"Unknown entity: {entity_type}"}
    return dict(doc)
