# This file was generated with the assistance of an AI coding tool.
from __future__ import annotations

from typing import Any

import ifcopenshell
import ifcopenshell.validate


def validate(model: ifcopenshell.file, express_rules: bool = False) -> dict[str, Any]:
    """Validate the model against the IFC schema.

    Returns ``valid`` together with a list of ``issues``, each carrying a
    ``level`` and a ``message``. Worth running after a batch of edits and
    before writing the model back to disk.

    :param model: The in-memory IFC model.
    :param express_rules: Also evaluate the schema's EXPRESS rules. Catches
        more problems but is considerably slower (default ``False``).
    """
    logger = ifcopenshell.validate.json_logger()
    ifcopenshell.validate.validate(model, logger, express_rules=express_rules)
    issues = [{"level": s["level"], "message": s["message"]} for s in logger.statements]
    return {"valid": len(issues) == 0, "issues": issues}
