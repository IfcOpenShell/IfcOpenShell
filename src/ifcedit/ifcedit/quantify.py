# This file was generated with the assistance of an AI coding tool.
from __future__ import annotations

from typing import Any

import ifcopenshell

AVAILABLE_RULES = ["IFC4QtoBaseQuantities", "IFC4X3QtoBaseQuantities"]


def list_rules() -> list[dict[str, str]]:
    """Return a list of available quantification rule names."""
    return [{"name": name} for name in AVAILABLE_RULES]


def run_quantify(model: ifcopenshell.file, rule: str, selector: str | None = None) -> dict[str, Any]:
    """Compute base quantities for elements and write them into the model.

    This is a write operation: it derives lengths, areas and volumes from
    element geometry and adds or updates their ``IfcElementQuantity`` sets.
    It does not report a schedule — see ``ifcquery.schedule()`` for the
    construction programme and ``ifcquery.cost()`` for cost schedules. An
    unrecognised ``rule`` is reported as an error listing the rules that are
    available.

    :param model: The in-memory IFC model. Modified in-place.
    :param rule: Quantity take-off rule set, for example
        ``'IFC4QtoBaseQuantities'`` or ``'IFC4X3QtoBaseQuantities'``.
    :param selector: ifcopenshell selector restricting which elements are
        measured, e.g. ``'IfcWall'``. Omit to measure every ``IfcElement`` and
        ``IfcSpace``.
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
