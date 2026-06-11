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

"""Forward-compat AST contract for the pen-icon dispatcher monopoly.

Every parametric gizmo group's pen icon must bind to the universal
``bim.enable_editing_parametric`` dispatcher rather than the feature's own
enable operator. The dispatcher is the single chokepoint where pre-edit
checks (shared-representation warning, future safety gates) run; a feature
that binds directly bypasses every such check silently."""

import ast
from pathlib import Path

import pytest

pytestmark = pytest.mark.drawing


BONSAI_ROOT = Path(__file__).parent.parent.parent / "bonsai"
BIM_DIR = BONSAI_ROOT / "bim"
DISPATCHER_IDNAME = "bim.enable_editing_parametric"


def _iter_pen_gizmo_target_set_operator_calls(tree: ast.Module):
    """Yield each ``ast.Call`` matching ``<receiver>.pen_gizmo.target_set_operator(...)``.
    Receiver is any attribute access (``self.pen_gizmo``, ``group.pen_gizmo``, etc.)."""
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if not isinstance(func, ast.Attribute) or func.attr != "target_set_operator":
            continue
        receiver = func.value
        if not isinstance(receiver, ast.Attribute) or receiver.attr != "pen_gizmo":
            continue
        yield node


def test_every_pen_gizmo_binding_routes_through_the_universal_dispatcher() -> None:
    violations: list[str] = []
    found_any = False
    for path in BIM_DIR.rglob("*.py"):
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except SyntaxError:
            continue
        for call in _iter_pen_gizmo_target_set_operator_calls(tree):
            found_any = True
            if not call.args:
                violations.append(f"{path}:{call.lineno} pen_gizmo.target_set_operator() called with no args")
                continue
            first_arg = call.args[0]
            if not isinstance(first_arg, ast.Constant) or not isinstance(first_arg.value, str):
                violations.append(
                    f"{path}:{call.lineno} pen_gizmo.target_set_operator() first arg is not a string literal"
                )
                continue
            if first_arg.value != DISPATCHER_IDNAME:
                violations.append(
                    f"{path}:{call.lineno} pen_gizmo.target_set_operator({first_arg.value!r}) "
                    f"bypasses the universal dispatcher"
                )

    assert found_any, (
        "No pen_gizmo.target_set_operator(...) calls found anywhere under bim/. "
        "Either the gizmo-binding pattern has been refactored away (this test "
        "needs updating) or the search root is wrong."
    )
    assert not violations, (
        "Pen-icon bindings must route through the universal dispatcher "
        f"({DISPATCHER_IDNAME!r}) so the shared-representation warning and any "
        "future pre-edit checks apply to every feature. Violations:\n  " + "\n  ".join(violations)
    )
