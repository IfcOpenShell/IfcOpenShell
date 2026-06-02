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

"""Forward-compat AST contracts for ``bonsai.bim.handler``.

Pins structural invariants on the post-commit refresh path that no
behavioural test can catch on its own — specifically, that the commit-
driven refresh never writes user-intent enum slots."""

import ast
from pathlib import Path

import pytest

pytestmark = pytest.mark.model


HANDLER_PATH = Path(__file__).parent.parent.parent / "bonsai" / "bim" / "handler.py"

# User-intent enums: encode the user's "what to build next" choice on the
# BIM Tool panel. Writing them from a commit-driven path silently resets
# the user's selection on every IFC mutation — selection-change is the
# only legitimate caller.
USER_INTENT_ENUM_ATTRS = frozenset({"ifc_class", "relating_type_id"})

# Functions that must remain free of user-intent enum writes. Both are
# reachable from ``tool.Parametric.refresh_post_commit``.
ENUM_SAFE_FUNCTIONS = ("refresh_bim_tool_headers", "_read_headers_into_props")


def _function_node(tree: ast.Module, name: str) -> ast.FunctionDef:
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    raise AssertionError(f"{name!r} not found in {HANDLER_PATH.name}")


@pytest.fixture(scope="module")
def handler_tree() -> ast.Module:
    return ast.parse(HANDLER_PATH.read_text(encoding="utf-8"))


@pytest.mark.parametrize("fn_name", ENUM_SAFE_FUNCTIONS)
def test_commit_driven_function_does_not_write_user_intent_enums(handler_tree: ast.Module, fn_name: str) -> None:
    """The commit-driven refresh path must never assign to user-intent
    enum slots (``ifc_class``, ``relating_type_id``). Re-targeting these
    from the post-commit hook silently overwrites the user's BIM Tool
    panel selection on every IFC mutation; only selection-change callers
    may write them."""
    fn = _function_node(handler_tree, fn_name)
    offenders = []
    for node in ast.walk(fn):
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if isinstance(target, ast.Attribute) and target.attr in USER_INTENT_ENUM_ATTRS:
                offenders.append((target.attr, node.lineno))
    if offenders:
        msgs = ", ".join(f"{attr} at line {line}" for attr, line in offenders)
        pytest.fail(
            f"{fn_name!r} assigns to user-intent enum slot(s): {msgs}. "
            f"Move this assignment to a selection-driven callback."
        )


def test_refresh_post_commit_calls_header_only_entrypoint(handler_tree: ast.Module) -> None:
    """``tool.Parametric.refresh_post_commit`` must dispatch into
    ``refresh_bim_tool_headers``, not ``update_bim_tool_props``.
    The latter re-targets user-intent enums; routing the post-commit
    hook through it silently resets the user's BIM Tool selection on
    every IFC mutation and crashes on element types absent from the
    ``ifc_class`` enum (e.g. ``IfcAnnotation``)."""
    parametric_path = HANDLER_PATH.parent.parent / "tool" / "parametric.py"
    parametric_tree = ast.parse(parametric_path.read_text(encoding="utf-8"))
    fn = _function_node(parametric_tree, "refresh_post_commit")
    called_handler_attrs = {
        node.func.attr
        for node in ast.walk(fn)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and isinstance(node.func.value, ast.Attribute)
        and node.func.value.attr == "handler"
    }
    assert (
        "refresh_bim_tool_headers" in called_handler_attrs
    ), "refresh_post_commit must call bonsai.bim.handler.refresh_bim_tool_headers"
    assert "update_bim_tool_props" not in called_handler_attrs, (
        "refresh_post_commit must not call update_bim_tool_props " "(re-targets user-intent enums on every commit)"
    )
