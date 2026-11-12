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

"""Forward-compat AST guards on the batched host-recut entry points.

Two contracts pinned per scanned file/region:

A. Host body recuts route through `tool.Geometry.recut_host`, not directly
   through `bonsai.core.geometry.switch_representation`. Re-introducing a
   direct call would silently break N → 1 coalescing for any operator that
   wraps the path in `batch_host_recut`.

B. Host `update_representation` writes route through
   `tool.Geometry.update_host_representation`, not directly through
   `bpy.ops.bim.update_representation`. Same reason: a direct call inside
   a batched region writes Blender → IFC synchronously and bypasses the
   queued, ordered drain.

Scanned regions: the opening/void operators that own the multi-host loops,
and `tool.Model.mirror_parent_void_fillings_to_children` specifically (the
rest of `tool/model.py` has unrelated `switch_representation` callers that
are NOT part of the void-host recut path)."""

import ast
import inspect
from pathlib import Path

import pytest

pytestmark = pytest.mark.model


BONSAI_ROOT = Path(__file__).parent.parent.parent.parent.parent / "bonsai"

_VOID_OPERATOR = BONSAI_ROOT / "bim" / "module" / "void" / "operator.py"
_OPENING = BONSAI_ROOT / "bim" / "module" / "model" / "opening.py"


def _switch_representation_calls(tree: ast.AST) -> list[ast.Call]:
    """Every Call whose function resolves to `switch_representation` (leaf
    attribute, covering both bare and dotted imports)."""
    hits = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if isinstance(func, ast.Name) and func.id == "switch_representation":
            hits.append(node)
        elif isinstance(func, ast.Attribute) and func.attr == "switch_representation":
            hits.append(node)
    return hits


def _bim_update_representation_calls(tree: ast.AST) -> list[ast.Call]:
    """Every Call to `bpy.ops.bim.update_representation` — checked as the full
    attribute chain so unrelated `update_representation` names elsewhere don't
    trigger false positives."""
    hits = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if not isinstance(func, ast.Attribute) or func.attr != "update_representation":
            continue
        # func.value should be ast.Attribute(attr="bim", value=ast.Attribute(attr="ops", value=ast.Name(id="bpy")))
        bim = func.value
        if not isinstance(bim, ast.Attribute) or bim.attr != "bim":
            continue
        ops = bim.value
        if not isinstance(ops, ast.Attribute) or ops.attr != "ops":
            continue
        bpy_name = ops.value
        if not isinstance(bpy_name, ast.Name) or bpy_name.id != "bpy":
            continue
        hits.append(node)
    return hits


def _format_offender(path: Path, node: ast.AST) -> str:
    return f"{path.name}:{node.lineno}"


def test_void_operator_routes_recuts_through_recut_host():
    source = _VOID_OPERATOR.read_text(encoding="utf-8")
    tree = ast.parse(source)
    offenders = [_format_offender(_VOID_OPERATOR, n) for n in _switch_representation_calls(tree)]
    assert not offenders, (
        "Direct `switch_representation` calls in void/operator.py: "
        + ", ".join(offenders)
        + ". Replace with `tool.Geometry.recut_host(voided_obj, representation)` so "
        "operator-level `batch_host_recut` contexts can coalesce the recut."
    )


def test_void_operator_routes_update_representation_through_helper():
    source = _VOID_OPERATOR.read_text(encoding="utf-8")
    tree = ast.parse(source)
    offenders = [_format_offender(_VOID_OPERATOR, n) for n in _bim_update_representation_calls(tree)]
    assert not offenders, (
        "Direct `bpy.ops.bim.update_representation` calls in void/operator.py: "
        + ", ".join(offenders)
        + ". Replace with `tool.Geometry.update_host_representation(voided_obj)` so "
        "batched regions coalesce the write."
    )


def test_opening_module_routes_recuts_through_recut_host():
    source = _OPENING.read_text(encoding="utf-8")
    tree = ast.parse(source)
    offenders = [_format_offender(_OPENING, n) for n in _switch_representation_calls(tree)]
    assert not offenders, (
        "Direct `switch_representation` calls in bim/module/model/opening.py: "
        + ", ".join(offenders)
        + ". Replace with `tool.Geometry.recut_host(voided_obj, representation)`."
    )


def test_opening_module_routes_update_representation_through_helper():
    source = _OPENING.read_text(encoding="utf-8")
    tree = ast.parse(source)
    offenders = [_format_offender(_OPENING, n) for n in _bim_update_representation_calls(tree)]
    assert not offenders, (
        "Direct `bpy.ops.bim.update_representation` calls in bim/module/model/opening.py: "
        + ", ".join(offenders)
        + ". Replace with `tool.Geometry.update_host_representation(voided_obj)`."
    )


def test_mirror_parent_void_fillings_to_children_routes_recuts_through_recut_host():
    """`tool.Model.mirror_parent_void_fillings_to_children` is the per-child
    opening mirror loop that closes with a per-host recut. The recut MUST go
    through `recut_host` so `tool.Model.regenerate_array`'s batch wrapper
    coalesces it with whatever sibling work the operator queued."""
    from bonsai.tool import model as tool_model_mod

    source = inspect.getsource(tool_model_mod)
    tree = ast.parse(source)
    target = next(
        (
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef) and node.name == "mirror_parent_void_fillings_to_children"
        ),
        None,
    )
    assert target is not None, "mirror_parent_void_fillings_to_children definition not found"

    offenders = [n.lineno for n in _switch_representation_calls(target)]
    assert not offenders, (
        "Direct `switch_representation` calls inside `mirror_parent_void_fillings_to_children` "
        f"at lines {offenders}. Replace with `tool.Geometry.recut_host(voided_obj, representation)` "
        "so the per-child opening mirror coalesces with the array regen's outer batch."
    )
