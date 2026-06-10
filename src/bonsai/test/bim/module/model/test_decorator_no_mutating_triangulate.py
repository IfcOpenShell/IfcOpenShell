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

"""Forward-compat AST contract: decorators do not triangulate in-place.

``bmesh.ops.triangulate(bm, faces=bm.faces)`` mutates its input — adding tri
edges and faces — and uses ear-clip fan triangulation that renders as visible
streaks across n-gon faces at the low alphas decorators favour. The canonical
draw path is ``tool.Blender.draw_bmesh_face_tris`` (wraps ``bm.calc_loop_triangles``,
non-mutating, beauty triangulator)."""

import ast
from pathlib import Path

import pytest

pytestmark = pytest.mark.model


BONSAI_ROOT = Path(__file__).parent.parent.parent / "bonsai"
BIM_MODULE_DIR = BONSAI_ROOT / "bim" / "module"


def _iter_guarded_files():
    yield from sorted(BIM_MODULE_DIR.glob("*/decorator.py"))
    yield BIM_MODULE_DIR / "model" / "opening.py"


def _is_guarded_class(node: ast.ClassDef) -> bool:
    return node.name.endswith("Decorator") or node.name == "DecorationsHandler"


def _is_mutating_triangulate_call(node: ast.AST) -> bool:
    if not isinstance(node, ast.Call):
        return False
    func = node.func
    if not isinstance(func, ast.Attribute) or func.attr != "triangulate":
        return False
    receiver = func.value
    if not isinstance(receiver, ast.Attribute) or receiver.attr != "ops":
        return False
    inner = receiver.value
    return isinstance(inner, ast.Name) and inner.id == "bmesh"


def test_no_decorator_calls_bmesh_ops_triangulate() -> None:
    violations: list[str] = []
    guarded_files = list(_iter_guarded_files())
    assert guarded_files, "Search root contains no decorator modules — test needs updating."

    for path in guarded_files:
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except (SyntaxError, FileNotFoundError):
            continue
        for class_node in (n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)):
            if not _is_guarded_class(class_node):
                continue
            for sub in ast.walk(class_node):
                if _is_mutating_triangulate_call(sub):
                    violations.append(f"{path}:{sub.lineno} {class_node.name} calls bmesh.ops.triangulate")

    assert not violations, (
        "Decorator classes must not call bmesh.ops.triangulate — it mutates "
        "the input bmesh and produces fan-clip artefacts at low alpha. "
        "Use tool.Blender.draw_bmesh_face_tris (wraps bm.calc_loop_triangles). "
        "Violations:\n  " + "\n  ".join(violations)
    )
