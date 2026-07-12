# This file was generated with the assistance of an AI coding tool.
from __future__ import annotations

from typing import Any

import ifcopenshell

AVAILABLE_RULES = ["IFC4QtoBaseQuantities", "IFC4X3QtoBaseQuantities"]


def list_rules() -> list[dict[str, str]]:
    """Return a list of available quantification rule names."""
    return [{"name": name} for name in AVAILABLE_RULES]


def run_quantify(model: ifcopenshell.file, rule: str, selector: str | None = None) -> dict[str, Any]:
    """Run quantity take-off on the model using the named rule.

    Modifies the model in-place by adding/updating IfcElementQuantity psets.
    Returns a summary dict with ok, rule, and elements_quantified.
    """
    from ifc5d.qto import edit_qtos, quantify
    from ifc5d.qto import rules as rule_sets

    if rule not in rule_sets:
        return {"ok": False, "error": f"Unknown rule: {rule}. Available: {list(rule_sets.keys())}"}

    import ifcopenshell.util.selector

    if selector:
        elements = set(ifcopenshell.util.selector.filter_elements(model, selector))
    else:
        elements = set(model.by_type("IfcElement")) | set(model.by_type("IfcSpace"))

    results = quantify(model, elements, rule_sets[rule])
    edit_qtos(model, results)
    return {"ok": True, "rule": rule, "elements_quantified": len(results)}
