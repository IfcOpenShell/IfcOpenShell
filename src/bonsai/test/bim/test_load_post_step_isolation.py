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

"""Forward-compat AST contract for ``handler.load_post`` step isolation.

Pins #9329: ``load_post`` used to call ``_apply_save_file_invariants``,
``_apply_user_preferences`` (BIM workspace restore) and
``_install_viewport_overlays`` back to back. An exception raised by the
first call aborted the function, so the BIM workspace was silently never
re-added after a session reset (e.g. ``bim.load_project`` with "Should
Start Fresh Session", which calls ``wm.read_homefile``). Each step must
run isolated so a failure in one cannot swallow the ones after it."""

import ast
from pathlib import Path

import pytest

pytestmark = pytest.mark.contract_guard

HANDLER_PATH = Path(__file__).parent.parent.parent / "bonsai" / "bim" / "handler.py"

# The steps load_post must run, in order, each isolated from the others'
# exceptions. If a step's implementation is renamed, update this list.
EXPECTED_STEPS = (
    "_apply_save_file_invariants",
    "_apply_user_preferences",
    "_install_viewport_overlays",
)


def _function_node(tree: ast.Module, name: str) -> ast.FunctionDef:
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    raise AssertionError(f"{name!r} not found in {HANDLER_PATH.name}")


@pytest.fixture(scope="module")
def handler_tree() -> ast.Module:
    return ast.parse(HANDLER_PATH.read_text(encoding="utf-8"))


def _referenced_names(node: ast.AST) -> set[str]:
    names: set[str] = set()
    for sub in ast.walk(node):
        if isinstance(sub, ast.Name):
            names.add(sub.id)
    return names


def _called_name(call: ast.Call) -> str | None:
    if isinstance(call.func, ast.Name):
        return call.func.id
    if isinstance(call.func, ast.Attribute):
        return call.func.attr
    return None


def test_load_post_runs_no_step_unguarded(handler_tree: ast.Module) -> None:
    """``load_post``'s top-level statements must never be a bare, direct call
    to one of the setup steps - each call must go through an isolating
    helper so one step's exception cannot prevent the next from running.
    (A step may still appear nested inside the helper call's arguments,
    e.g. wrapped in a lambda - only the outermost call matters here.)"""
    fn = _function_node(handler_tree, "load_post")
    bare_calls = []
    for stmt in fn.body:
        call = None
        if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
            call = stmt.value
        if call is None:
            continue
        called = _called_name(call)
        if called in EXPECTED_STEPS:
            bare_calls.append(called)
    if bare_calls:
        pytest.fail(
            f"load_post calls {bare_calls} directly at the top level, unguarded. "
            "A failure in one step will silently skip the rest (including the BIM "
            "workspace restore in _apply_user_preferences). Route every step through "
            "an isolating try/except helper. See #9329."
        )


def test_load_post_still_invokes_every_expected_step(handler_tree: ast.Module) -> None:
    """Whatever isolation mechanism is used, load_post must still reference
    every step it's responsible for - the isolation must not have silently
    dropped one instead of wrapping it."""
    fn = _function_node(handler_tree, "load_post")
    referenced = _referenced_names(fn)
    missing = [name for name in EXPECTED_STEPS if name not in referenced]
    if missing:
        pytest.fail(f"load_post no longer references step(s) {missing}. See #9329.")
