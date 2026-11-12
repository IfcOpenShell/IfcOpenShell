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

"""Forward-compat AST contract: ``core.connection.disconnect_rel`` must have a
branch for every ``kind`` emitted by ``tool.connection.Connection`` lookups.

Adding a new kind (e.g. ``"void"``, ``"fill"``, ``"interferes"``) to
``find_rels`` / ``find_rels_for_element`` without extending ``disconnect_rel``
would silently regress the disconnect operator and the cascade-on-delete: a new
kind would reach the dispatch, hit the ``raise ValueError("Unknown kind")``
fallback, and either crash the operator or leave the cascade half-done. This
guard makes the symmetry mandatory at test time."""

import ast
from pathlib import Path

import pytest

pytestmark = pytest.mark.model


BONSAI_ROOT = Path(__file__).parent.parent.parent / "bonsai"
TOOL_CONNECTION = BONSAI_ROOT / "tool" / "connection.py"
CORE_CONNECTION = BONSAI_ROOT / "core" / "connection.py"


def _find_function(tree: ast.Module, name: str) -> ast.FunctionDef:
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    raise AssertionError(f"Function {name!r} not found")


def _find_method(tree: ast.Module, class_name: str, method_name: str) -> ast.FunctionDef:
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            for child in node.body:
                if isinstance(child, ast.FunctionDef) and child.name == method_name:
                    return child
    raise AssertionError(f"Method {class_name}.{method_name} not found")


def _kinds_emitted_by(method: ast.FunctionDef) -> set[str]:
    """Extract every kind label this method emits.

    Looks at exactly two narrow patterns to avoid false positives from
    docstrings or type-annotation strings:

    - ``_record(rel, "<kind>", …)`` — positional string at index 1, the
      conventional emit shape in ``find_rels`` / ``find_rels_for_element``.
    - ``kind = "<a>" if … else "<b>"`` and chained variants — string
      literals on either branch of an ``ast.IfExp`` assigned to ``kind``.
    """
    kinds: set[str] = set()
    for node in ast.walk(method):
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name) and func.id == "_record" and len(node.args) >= 2:
                arg = node.args[1]
                if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                    kinds.add(arg.value)
                elif isinstance(arg, ast.IfExp):
                    for branch in (arg.body, arg.orelse):
                        if isinstance(branch, ast.Constant) and isinstance(branch.value, str):
                            kinds.add(branch.value)
        elif isinstance(node, ast.Assign):
            targets = [t for t in node.targets if isinstance(t, ast.Name) and t.id == "kind"]
            if not targets or not isinstance(node.value, ast.IfExp):
                continue
            for branch in (node.value.body, node.value.orelse):
                if isinstance(branch, ast.Constant) and isinstance(branch.value, str):
                    kinds.add(branch.value)
    return kinds


def _kind_branches_in_disconnect_rel(tree: ast.Module) -> set[str]:
    """Return every kind matched by ``disconnect_rel``'s ``kind == "…"`` branches."""
    fn = _find_function(tree, "disconnect_rel")
    kinds: set[str] = set()
    for node in ast.walk(fn):
        if isinstance(node, ast.Compare) and len(node.ops) == 1 and isinstance(node.ops[0], ast.Eq):
            left = node.left
            right = node.comparators[0]
            if isinstance(left, ast.Name) and left.id == "kind":
                if isinstance(right, ast.Constant) and isinstance(right.value, str):
                    kinds.add(right.value)
    return kinds


def test_disconnect_rel_handles_every_kind_emitted_by_connection_lookups() -> None:
    tool_tree = ast.parse(TOOL_CONNECTION.read_text(encoding="utf-8"))
    core_tree = ast.parse(CORE_CONNECTION.read_text(encoding="utf-8"))

    emitted = _kinds_emitted_by(_find_method(tool_tree, "Connection", "find_rels")) | _kinds_emitted_by(
        _find_method(tool_tree, "Connection", "find_rels_for_element")
    )
    handled = _kind_branches_in_disconnect_rel(core_tree)

    assert emitted, "Sanity check: no kinds extracted — emit pattern may have changed"

    missing = emitted - handled
    assert not missing, (
        f"core.connection.disconnect_rel is missing branches for kinds {missing}. "
        f"Every kind returned by Connection.find_rels / find_rels_for_element "
        f"must have a matching if/elif branch in the dispatch."
    )
