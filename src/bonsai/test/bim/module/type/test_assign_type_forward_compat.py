# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2026
#
# This file is part of Bonsai.
#
# Bonsai is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Bonsai is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Bonsai.  If not, see <http://www.gnu.org/licenses/>.
#
# This file was generated with the assistance of an AI coding tool.

"""Forward-compat AST contracts for the class-mismatched-type-assignment guard.

Two structural invariants that no behavioural test can pin on its own:

1. ``ifcopenshell.api.type.assign_type`` MUST reference
   ``ifcopenshell.util.type.get_applicable_entities`` (or
   ``get_applicable_types``) — the schema-aware applicability lookup that
   produces the canonical class-pairing whitelist. A drift here means the
   API stops rejecting class-mismatched pairs.

2. ``bonsai.bim.module.type.operator`` MUST reference
   ``tool.Type.is_relating_type_compatible`` — the single source of truth
   for partition / WARNING / CANCELLED behaviour in the Bonsai operator
   layer. A drift here re-opens the fan-out hole that silently writes
   schema-corrupt typings into the selection when one (active) object's
   class drove the picker but other selected objects don't match.
"""

import ast
from pathlib import Path

import pytest

pytestmark = pytest.mark.type


BONSAI_ROOT = Path(__file__).resolve().parents[4] / "bonsai"
IFCOPENSHELL_API_ASSIGN_TYPE = (
    Path(__file__).resolve().parents[5] / "ifcopenshell-python" / "ifcopenshell" / "api" / "type" / "assign_type.py"
)
BONSAI_TYPE_OPERATOR = BONSAI_ROOT / "bim" / "module" / "type" / "operator.py"


def _attribute_chain(node: ast.AST) -> str:
    """Render an ``ast.Attribute``/``ast.Name`` chain as a dotted string,
    e.g. ``tool.Type.is_relating_type_compatible``. Returns ``""`` if the
    chain bottoms out on something other than a Name (e.g. a subscript)."""
    parts: list[str] = []
    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value
    if isinstance(node, ast.Name):
        parts.append(node.id)
        return ".".join(reversed(parts))
    return ""


def _all_attribute_chains(tree: ast.Module) -> set[str]:
    chains: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute):
            chain = _attribute_chain(node)
            if chain:
                chains.add(chain)
    return chains


def test_api_assign_type_calls_applicability_lookup() -> None:
    """Pin Layer B: ``ifcopenshell.api.type.assign_type`` references
    ``ifcopenshell.util.type.get_applicable_entities`` (the source of truth
    for which occurrence classes a given type class may type)."""
    tree = ast.parse(IFCOPENSHELL_API_ASSIGN_TYPE.read_text(encoding="utf-8"))
    chains = _all_attribute_chains(tree)
    sentinel = "ifcopenshell.util.type.get_applicable_entities"
    assert sentinel in chains, (
        f"{IFCOPENSHELL_API_ASSIGN_TYPE.name} no longer references {sentinel}. "
        "The API-layer guard against class-mismatched type assignment is gone."
    )


def test_bonsai_type_operator_module_references_compatibility_helper() -> None:
    """Pin Layer C: the Bonsai type operator module references
    ``tool.Type.is_relating_type_compatible``. Every operator in this file
    that fans assign_type calls across a multi-selection must filter
    through this helper to avoid writing mismatched typings on objects the
    panel picker didn't validate."""
    tree = ast.parse(BONSAI_TYPE_OPERATOR.read_text(encoding="utf-8"))
    chains = _all_attribute_chains(tree)
    sentinel = "tool.Type.is_relating_type_compatible"
    assert sentinel in chains, (
        f"{BONSAI_TYPE_OPERATOR.name} no longer references {sentinel}. "
        "Operator-layer partition that prevents schema-illegal type "
        "assignment across multi-selection has been removed."
    )
