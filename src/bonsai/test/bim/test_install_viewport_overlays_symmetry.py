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

"""Forward-compat AST contract for ``_install_viewport_overlays``.

``_install_viewport_overlays`` (called from ``load_post``) is supposed to
reset every state-driven viewport decorator to match the *newly loaded*
file's own scene properties: uninstall everything first, then conditionally
reinstall whatever the new scene's properties say should be on. A decorator
whose conditional install has no matching unconditional uninstall keeps
whatever draw handler was left registered by the *previous* file/session,
even though the freshly loaded file's own checkbox reads off, so a stale
overlay silently disagrees with the UI, with no error.

BoundingBoxDecorator regressed this way in a686d709 (2025-05-31): the
conditional install was added alongside four siblings (Georeference,
Aggregate, Nest, WallAxis, SlabDirection) but the matching unconditional
uninstall was never added, unlike every one of those siblings."""

import ast
from pathlib import Path

import pytest

pytestmark = pytest.mark.contract_guard

HANDLER_PATH = Path(__file__).parent.parent.parent / "bonsai" / "bim" / "handler.py"


def _function_node(tree: ast.Module, name: str) -> ast.FunctionDef:
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    raise AssertionError(f"{name!r} not found in {HANDLER_PATH.name}")


def _decorator_name(call: ast.Call) -> "str | None":
    func = call.func
    if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name):
        return func.value.id
    return None


def _collect_conditional_installs(node: ast.AST, conditional: bool, acc: set) -> None:
    """Names receiving a ``.install(`` call reachable only through an ``if``."""
    if isinstance(node, ast.If):
        for child in node.body:
            _collect_conditional_installs(child, True, acc)
        for child in node.orelse:
            _collect_conditional_installs(child, True, acc)
        return
    if isinstance(node, ast.Call) and conditional:
        func = node.func
        if isinstance(func, ast.Attribute) and func.attr == "install":
            name = _decorator_name(node)
            if name:
                acc.add(name)
    for child in ast.iter_child_nodes(node):
        _collect_conditional_installs(child, conditional, acc)


def _collect_unconditional_uninstalls(node: ast.AST, conditional: bool, acc: set) -> None:
    """Names receiving a ``.uninstall(`` call NOT nested inside an ``if``."""
    if isinstance(node, ast.If):
        for child in node.body:
            _collect_unconditional_uninstalls(child, True, acc)
        for child in node.orelse:
            _collect_unconditional_uninstalls(child, True, acc)
        return
    if isinstance(node, ast.Call) and not conditional:
        func = node.func
        if isinstance(func, ast.Attribute) and func.attr == "uninstall":
            name = _decorator_name(node)
            if name:
                acc.add(name)
    for child in ast.iter_child_nodes(node):
        _collect_unconditional_uninstalls(child, conditional, acc)


def test_every_conditionally_installed_decorator_is_unconditionally_uninstalled_first() -> None:
    tree = ast.parse(HANDLER_PATH.read_text(encoding="utf-8"))
    fn = _function_node(tree, "_install_viewport_overlays")

    conditional_installs: set = set()
    unconditional_uninstalls: set = set()
    for stmt in fn.body:
        _collect_conditional_installs(stmt, False, conditional_installs)
        _collect_unconditional_uninstalls(stmt, False, unconditional_uninstalls)

    missing = conditional_installs - unconditional_uninstalls
    if missing:
        pytest.fail(
            f"_install_viewport_overlays conditionally installs {sorted(missing)} but never "
            "unconditionally uninstalls them first. On a file load whose own scene properties "
            "say the decorator should be off, a handler left registered by a previously loaded "
            "file/session survives and keeps drawing, silently disagreeing with the new file's "
            "own (unchecked) UI state. Add `<Name>.uninstall()` to the unconditional block at "
            "the top of _install_viewport_overlays, alongside its conditionally-installed siblings."
        )
