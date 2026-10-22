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

Two contracts pinned here, both protecting invariants that fail *silently*
when broken — the array still renders, it is just subtly wrong, which is
exactly the kind of regression a unit test alone tends not to catch because
nobody thinks to re-run it.

A. **One placement site.** Instance transforms come from
   ``tool.Array.child_matrix`` and nowhere else. The regenerator and the
   drag-time ghost preview both call it, so a second hand-rolled copy of the
   offset math would let the preview drift from what Finish actually builds —
   which is precisely the duplication this function was introduced to remove.

B. **The sweep is never clamped or wrapped.** A radial sweep may exceed one
   full turn (spiral stairs, helical ramps).

   Note *where* this actually bites, because it is counter-intuitive:
   wrapping the final ``angle * i`` product is harmless, since rotations are
   periodic and ``Rotation(630)`` IS ``Rotation(270)``. The damage is done
   upstream of that — clamping the stored property, or normalising the sweep
   before DISTRIBUTE divides it, changes the *step* (540/16 = 33.75 degrees
   becomes 180/16 = 11.25) and quietly rebuilds a different array. Worse, the
   last instance lands correctly either way, so end-position assertions cannot
   detect it.

   The guards below therefore target the two upstream sites: the property
   declaration (this codebase's every other ANGLE property is clamped to under
   one turn, so copying that convention here is a very live regression) and
   the radial math's pre-division angle handling. The numeric contract is
   pinned by ``test_intermediate_instance_proves_the_sweep_was_not_wrapped``
   in ``test/tool/test_array_child_matrix.py``.
"""

import ast
from pathlib import Path

import pytest

pytestmark = pytest.mark.model


BONSAI_ROOT = Path(__file__).parent.parent.parent.parent.parent / "bonsai"

_TOOL_ARRAY = BONSAI_ROOT / "tool" / "array.py"
_TOOL_MODEL = BONSAI_ROOT / "tool" / "model.py"
_MODEL_ARRAY = BONSAI_ROOT / "bim" / "module" / "model" / "array.py"
_MODEL_PROP = BONSAI_ROOT / "bim" / "module" / "model" / "prop.py"

# Decomposition APIs that discard turn count. ``to_euler`` and
# ``to_quaternion`` both normalise; ``Matrix.Rotation`` composing from a raw
# scalar is the safe direction and is deliberately absent from this list.
_ANGLE_LOSSY_ATTRS = {"to_euler", "to_quaternion"}


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


def _modulo_ops(tree: ast.AST) -> list[ast.BinOp]:
    return [n for n in ast.walk(tree) if isinstance(n, ast.BinOp) and isinstance(n.op, ast.Mod)]


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
    offenders = []
    for node in ast.walk(body):
        if isinstance(node, ast.Subscript) and isinstance(node.slice, ast.Constant):
            if node.slice.value in {"x", "y", "z", "angle", "rise", "center", "axis"}:
                offenders.append(f"line {node.lineno}: layer[{node.slice.value!r}]")
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


def _array_angle_prop(tree: ast.AST) -> ast.Call:
    """The ``angle`` property declaration inside ``BIMArrayProperties``."""
    cls = next(n for n in ast.walk(tree) if isinstance(n, ast.ClassDef) and n.name == "BIMArrayProperties")
    for node in cls.body:
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and node.target.id == "angle":
            assert isinstance(node.annotation, ast.Call)
            return node.annotation
    raise AssertionError("BIMArrayProperties.angle not found — renamed or removed.")


def test_array_angle_property_is_not_clamped_to_one_turn():
    """The highest-risk regression in the whole feature.

    Every other ANGLE property in model/prop.py carries a hard min/max under
    one turn (``x_angle`` is +/-180, the roof slope is 0..90). Applying that
    house convention to the array sweep would cap spiral stairs at a single
    turn — and would do it at the UI layer, where none of the placement unit
    tests would notice. ``soft_min``/``soft_max`` are fine: they only tame
    mouse-drag sensitivity and do not clamp typed or programmatic values."""
    angle = _array_angle_prop(_parse(_MODEL_PROP))
    clamps = [kw.arg for kw in angle.keywords if kw.arg in {"min", "max"}]
    assert not clamps, (
        "BIMArrayProperties.angle declares "
        + ", ".join(clamps)
        + ". A hard clamp caps radial arrays at one turn and breaks multi-turn "
        "helices (spiral stairs, helical ramps). Use soft_min/soft_max instead — "
        "they bound the drag without bounding the value."
    )


def test_radial_math_does_not_normalise_the_sweep():
    """No modulo and no euler/quaternion round-trip in the radial math.

    The DISTRIBUTE division happens inside this function, so a modulo anywhere
    in it can land upstream of the division and silently change the step. The
    check is deliberately broader than strictly necessary — a modulo applied
    only to the final product would be harmless — because 'harmless here'
    depends on evaluation order that a later edit can quietly change."""
    radial = _function_named(_parse(_TOOL_ARRAY), "_radial_child_matrix")

    mods = [f"line {n.lineno}" for n in _modulo_ops(radial)]
    assert not mods, (
        "Modulo arithmetic in _radial_child_matrix at "
        + ", ".join(mods)
        + ". Normalising the sweep before DISTRIBUTE divides it changes the step "
        "(540/16 = 33.75 degrees becomes 180/16 = 11.25) and rebuilds a different "
        "array — and the LAST instance still lands correctly, so this does not "
        "show up in end-position assertions."
    )

    lossy = [
        f"line {n.lineno}: .{n.func.attr}()"
        for n in ast.walk(radial)
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr in _ANGLE_LOSSY_ATTRS
    ]
    assert not lossy, (
        "Rotation decomposition in _radial_child_matrix at "
        + ", ".join(lossy)
        + ". to_euler()/to_quaternion() normalise away the turn count; compose the "
        "rotation from the scalar angle with Matrix.Rotation instead."
    )


def test_step_divisor_never_returns_zero():
    """Guards the DISTRIBUTE divide. Pinned structurally because the failure
    is a hard ZeroDivisionError on a count-1 layer, which is a reachable and
    entirely ordinary state (every array starts at count 1)."""
    divisor = _function_named(_parse(_TOOL_ARRAY), "step_divisor")
    has_max_guard = any(
        isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "max" for n in ast.walk(divisor)
    )
    assert has_max_guard, (
        "tool.Array.step_divisor lost its max() floor. A count of 1 (the state "
        "every new array starts in) would divide by zero under DISTRIBUTE."
    )
