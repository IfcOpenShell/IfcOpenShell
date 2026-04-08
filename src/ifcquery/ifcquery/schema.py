# This file was generated with the assistance of an AI coding tool.
from __future__ import annotations

from typing import Any

import ifcopenshell
import ifcopenshell.util.doc


def schema(model: ifcopenshell.file, entity_type: str) -> dict[str, Any]:
    """Return IFC class documentation for entity_type from model's schema version."""
    schema_name = model.schema
    try:
        doc = ifcopenshell.util.doc.get_entity_doc(schema_name, entity_type)
    except Exception:
        return {"error": f"Unknown entity: {entity_type}"}
    if not doc:
        return {"error": f"Unknown entity: {entity_type}"}
    return dict(doc)
