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

"""Forward-compat AST contract for viewport decorator lifecycle.

Any class that tracks Blender draw handlers via a class-level ``handlers``
list MUST subclass ``tool.Blender.ViewportDecorator``. The base sets
``handlers = []`` and ``is_installed = False`` via ``__init_subclass__`` and
provides install / uninstall with the correct ``cls.handlers.clear()``.
A class that declares its own ``handlers = []`` outside the base duplicates
the lifecycle and is at risk of regressing the handler-clear bug class."""

import ast
from pathlib import Path

import pytest

pytestmark = pytest.mark.contract_guard

ADDON_ROOT = Path(__file__).parent.parent.parent / "bonsai"
DECORATORS_GLOB = "bim/module/**/decorator.py"


def _is_empty_handlers_list(target: ast.expr, value: ast.expr | None) -> bool:
    return isinstance(target, ast.Name) and target.id == "handlers" and isinstance(value, ast.List) and not value.elts


def _has_handlers_list_class_attr(class_node: ast.ClassDef) -> bool:
    for node in class_node.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if _is_empty_handlers_list(target, node.value):
                    return True
        elif isinstance(node, ast.AnnAssign):
            if _is_empty_handlers_list(node.target, node.value):
                return True
    return False


def _subclasses_viewport_decorator(class_node: ast.ClassDef) -> bool:
    for base in class_node.bases:
        if isinstance(base, ast.Name) and base.id.endswith("ViewportDecorator"):
            return True
        if isinstance(base, ast.Attribute) and base.attr.endswith("ViewportDecorator"):
            return True
    return False


def test_no_decorator_class_duplicates_viewport_lifecycle() -> None:
    offenders: list[str] = []
    for path in sorted(ADDON_ROOT.glob(DECORATORS_GLOB)):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if not isinstance(node, ast.ClassDef):
                continue
            if not _has_handlers_list_class_attr(node):
                continue
            if _subclasses_viewport_decorator(node):
                continue
            rel = path.relative_to(ADDON_ROOT)
            offenders.append(f"{rel.as_posix()}:{node.lineno}: class {node.name}")
    if offenders:
        listing = "\n  ".join(offenders)
        pytest.fail(
            "Class(es) declare ``handlers = []`` at class scope without subclassing "
            "``tool.Blender.ViewportDecorator``. Migrate to the canonical viewport-lifecycle "
            "base (which sets handlers/is_installed via __init_subclass__ and provides "
            "install/uninstall with the correct cls.handlers.clear()):\n  " + listing
        )
