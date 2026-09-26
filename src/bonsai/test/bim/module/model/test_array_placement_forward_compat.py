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

"""Forward-compat AST guards on parametric array placement.

Pins that instance transforms come from ``tool.Array.child_matrix`` and
nowhere else. The regenerator and the drag-time ghost preview both call it,
so a second hand-rolled copy of the offset math would let the preview drift
from what Finish actually builds — precisely the duplication this function
was introduced to remove. It fails silently, too: the array still renders,
the ghosts just point somewhere else.
"""

import ast
from pathlib import Path

import pytest

pytestmark = pytest.mark.model


BONSAI_ROOT = Path(__file__).parent.parent.parent.parent.parent / "bonsai"

_TOOL_ARRAY = BONSAI_ROOT / "tool" / "array.py"
_TOOL_MODEL = BONSAI_ROOT / "tool" / "model.py"
_MODEL_ARRAY = BONSAI_ROOT / "bim" / "module" / "model" / "array.py"


def _function_named(tree: ast.AST, name: str) -> ast.FunctionDef:
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name:
            return node
    raise AssertionError(f"{name!r} not found — it was renamed or removed; update this guard deliberately.")


def _parse(path: Path) -> ast.AST:
    return ast.parse(path.read_text(encoding="utf-8"))


def _calls_to(tree: ast.AST, attr: str) -> list[ast.Call]:
    return [
        n
        for n in ast.walk(tree)
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == attr
    ]


def test_child_matrix_is_the_only_placement_site_in_the_regenerator():
    """``_regenerate_array_body`` must not compute offsets itself."""
    body = _function_named(_parse(_TOOL_MODEL), "_regenerate_array_body")
    assert _calls_to(body, "child_matrix"), (
        "tool.Model._regenerate_array_body no longer calls tool.Array.child_matrix. "
        "Array placement must stay in one function or the drag preview will drift "
        "from the committed result."
    )
    # A re-introduced local offset calculation would show up as arithmetic on
    # the layer's stored distance keys.
    offenders = [
        f"line {node.lineno}: layer[{node.slice.value!r}]"
        for node in ast.walk(body)
        if isinstance(node, ast.Subscript)
        and isinstance(node.slice, ast.Constant)
        and node.slice.value in {"x", "y", "z"}
    ]
    assert not offenders, (
        "_regenerate_array_body reads placement keys directly: "
        + ", ".join(offenders)
        + ". Pass the whole layer dict to tool.Array.child_matrix instead."
    )


def test_preview_decorator_shares_the_regenerator_placement_function():
    """The ghost preview must not re-derive positions."""
    compute = _function_named(_parse(_MODEL_ARRAY), "_compute_segments")
    assert _calls_to(compute, "child_matrix"), (
        "ArrayPreviewDecorator._compute_segments no longer calls tool.Array.child_matrix. "
        "A hand-rolled copy of the placement math makes the drag ghosts lie about "
        "where the copies will land."
    )


def test_step_divisor_never_returns_zero():
    """Guards the DISTRIBUTE divide. Pinned structurally because the failure is a
    hard ZeroDivisionError on a count-1 layer, which is a reachable and entirely
    ordinary state — every array starts at count 1."""
    divisor = _function_named(_parse(_TOOL_ARRAY), "step_divisor")
    has_max_guard = any(
        isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "max" for n in ast.walk(divisor)
    )
    assert has_max_guard, (
        "tool.Array.step_divisor lost its max() floor. A count of 1 (the state "
        "every new array starts in) would divide by zero under DISTRIBUTE."
    )
