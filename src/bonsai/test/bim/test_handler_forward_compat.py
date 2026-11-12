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

"""Forward-compat AST contracts for the BIM Tool refresh path.

Pins structural invariants that no behavioural test can catch on its own:
the commit-driven header refresh fires only for the parametric validate-
gizmo operators (``bim.finish_editing_<name>``), never universally — and
the header writer never drifts into user-intent enum writes."""

import ast
from pathlib import Path

import pytest

pytestmark = pytest.mark.model


HANDLER_PATH = Path(__file__).parent.parent.parent / "bonsai" / "bim" / "handler.py"
PARAMETRIC_PATH = HANDLER_PATH.parent.parent / "tool" / "parametric.py"
MODEL_MODULE_DIR = HANDLER_PATH.parent / "module" / "model"

# User-intent enums encode the user's "what to build next" choice on the
# BIM Tool panel. The header-only writer must never drift into enum writes;
# user-intent enums are owned by the selection-change path.
USER_INTENT_ENUM_ATTRS = frozenset({"ifc_class", "relating_type_id"})


def _function_node(tree: ast.Module, name: str) -> ast.FunctionDef:
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    raise AssertionError(f"{name!r} not found in {HANDLER_PATH.name}")


@pytest.fixture(scope="module")
def handler_tree() -> ast.Module:
    return ast.parse(HANDLER_PATH.read_text(encoding="utf-8"))


def test_read_headers_into_props_writes_only_header_floats(handler_tree: ast.Module) -> None:
    """``_read_headers_into_props`` is the header-only writer called from
    the selection-driven refresh. It must not assign to user-intent enum
    slots (``ifc_class``, ``relating_type_id``); those are the
    'what to build next' choice and have their own targeted writes
    earlier in ``update_bim_tool_props``."""
    fn = _function_node(handler_tree, "_read_headers_into_props")
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
            f"_read_headers_into_props assigns to user-intent enum slot(s): {msgs}. "
            f"Header refresh must not re-target the user's BIM Tool panel selection."
        )


def test_refresh_post_commit_gates_header_refresh_on_edit_types_registry() -> None:
    """``tool.Parametric.refresh_post_commit`` fires for every IFC
    operator commit. Only operators whose ``bl_idname`` matches a
    ``ParametricObject.finish_op`` in ``EDIT_TYPES`` (the validate-
    gizmo path) must trigger a BIM Tool header refresh — selection
    didn't change but the header values did. Other operators must
    skip the refresh: they don't target an active-object header edit,
    and their commit context may lack the view-layer attributes the
    refresh reads.

    The gate must consult the registry, not match a string prefix —
    ``EDIT_TYPES`` is the canonical list of parametric features, and
    querying it stays correct even if ``ParametricObject.finish_op``
    changes its derivation rule."""
    parametric_tree = ast.parse(PARAMETRIC_PATH.read_text(encoding="utf-8"))
    fn = _function_node(parametric_tree, "refresh_post_commit")
    found_gated_call = False
    for node in ast.walk(fn):
        if not isinstance(node, ast.If):
            continue
        references_registry = any(
            isinstance(sub, ast.Attribute) and sub.attr == "EDIT_TYPES" for sub in ast.walk(node.test)
        )
        if not references_registry:
            continue
        for body_node in ast.walk(node):
            if (
                isinstance(body_node, ast.Call)
                and isinstance(body_node.func, ast.Attribute)
                and body_node.func.attr == "refresh_bim_tool_headers"
            ):
                found_gated_call = True
                break
        if found_gated_call:
            break
    assert found_gated_call, (
        "tool.Parametric.refresh_post_commit must gate refresh_bim_tool_headers on an "
        "If whose test references EDIT_TYPES (the parametric registry). An ungated call "
        "fires the refresh for commits in contexts that strip view-layer attributes; "
        "a missing call silently drops the validate-gizmo header refresh."
    )


def _modules_with_module_scope_cache_and_clear():
    """Yield ``module_name`` for every ``bim/module/model/*.py`` source that
    declares a module-scope ``GenerationKeyedCache()`` assignment AND a
    top-level ``def clear_caches``. These are the modules whose cache state
    survives file loads and must be drained from ``_apply_save_file_invariants``."""
    for path in MODEL_MODULE_DIR.glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        has_cache = False
        has_clear = False
        for node in tree.body:
            if isinstance(node, ast.FunctionDef) and node.name == "clear_caches":
                has_clear = True
                continue
            if isinstance(node, ast.Assign):
                for sub in ast.walk(node.value):
                    if (
                        isinstance(sub, ast.Call)
                        and isinstance(sub.func, ast.Attribute)
                        and sub.func.attr == "GenerationKeyedCache"
                    ):
                        has_cache = True
                        break
        if has_cache and has_clear:
            yield path.stem


def test_on_load_post_drains_every_module_scope_geom_cache() -> None:
    """Module-scope ``GenerationKeyedCache`` instances persist across file
    loads — the counter they invalidate against is class-level and survives
    a ``.blend`` reload. Without a ``load_post`` drain the cache may serve
    entries whose ``bpy_struct`` references point into the previous file's
    freed ``bpy.data``, raising ``ReferenceError`` on the next attribute read.

    Pin: every model module that exposes both a module-scope cache and a
    top-level ``clear_caches`` is called from ``tool.Parametric.on_load_post``,
    the central post-load drain."""
    parametric_tree = ast.parse(PARAMETRIC_PATH.read_text(encoding="utf-8"))
    fn = _function_node(parametric_tree, "on_load_post")
    drained: set[str] = set()
    for node in ast.walk(fn):
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "clear_caches"
            and isinstance(node.func.value, ast.Name)
        ):
            drained.add(node.func.value.id)
    missing = [name for name in _modules_with_module_scope_cache_and_clear() if name not in drained]
    if missing:
        pytest.fail(
            "Module(s) expose a module-scope GenerationKeyedCache + clear_caches() but "
            f"tool.Parametric.on_load_post does not drain them on load_post: {sorted(missing)}. "
            "Add a `<module>.clear_caches()` call so freshly-loaded files cannot serve "
            "entries holding freed bpy.data references from the previous file."
        )
