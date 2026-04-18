# This file was generated with the assistance of an AI coding tool.
from __future__ import annotations

from typing import Any

import ifcopenshell
import ifcopenshell.validate


def validate(model: ifcopenshell.file, express_rules: bool = False) -> dict[str, Any]:
    """Validate the model and return a dict with 'valid' bool and 'issues' list."""
    logger = ifcopenshell.validate.json_logger()
    ifcopenshell.validate.validate(model, logger, express_rules=express_rules)
    issues = [{"level": s["level"], "message": s["message"]} for s in logger.statements]
    return {"valid": len(issues) == 0, "issues": issues}
