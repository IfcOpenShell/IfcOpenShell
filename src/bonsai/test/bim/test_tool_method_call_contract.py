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

"""Static contract: every ``tool.<Name>.<method>(...)`` call site must name a
method (or nested class) that actually exists, either on the ``tool/<name>.py``
implementation class or on its ``core/tool.py`` abstract stub.

Found the gap this guards against: ``sheeter.py`` called
``tool.Drawing.create_svg_document(...)``, a method that was renamed away
from a working ``create_svg_schedule`` call in commit 3ede9b254f and never
implemented under its new name, leaving an unconditional ``AttributeError``
on the code path.

This is a pure AST scan over the repository source, not a live Blender
check, so it also catches call sites in code paths that are hard to drive
from a test (they don't need to run to be checked)."""

import ast
from pathlib import Path

import pytest

pytestmark = pytest.mark.geometry

BONSAI_ROOT = Path(__file__).parent.parent.parent / "bonsai"
TOOL_DIR = BONSAI_ROOT / "tool"
CORE_TOOL_FILE = BONSAI_ROOT / "core" / "tool.py"
TOOL_INIT = TOOL_DIR / "__init__.py"
PRODUCTION_DIRS = (BONSAI_ROOT / "bim", BONSAI_ROOT / "tool", BONSAI_ROOT / "core")


def _parse(path: Path) -> ast.Module:
    return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


def _class_members(class_node: ast.ClassDef) -> set[str]:
    """Names directly usable as ``ClassName.<name>``: methods and nested classes."""
    members = set()
    for item in class_node.body:
        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            members.add(item.name)
    return members


def _tool_name_to_module_file() -> dict[str, str]:
    tree = _parse(TOOL_INIT)
    mapping = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module and node.module.startswith("bonsai.tool."):
            modfile = node.module.rsplit(".", 1)[-1] + ".py"
            for alias in node.names:
                mapping[alias.asname or alias.name] = modfile
    return mapping


def _classes_by_name(path: Path) -> dict[str, ast.ClassDef]:
    tree = _parse(path)
    return {node.name: node for node in tree.body if isinstance(node, ast.ClassDef)}


def _build_tool_member_sets() -> dict[str, set[str]]:
    core_classes = _classes_by_name(CORE_TOOL_FILE)
    name_to_module = _tool_name_to_module_file()

    impl_classes_by_file: dict[str, dict[str, ast.ClassDef]] = {}
    for modfile in set(name_to_module.values()):
        fp = TOOL_DIR / modfile
        if fp.exists():
            impl_classes_by_file[modfile] = _classes_by_name(fp)

    member_sets: dict[str, set[str]] = {}
    for name, modfile in name_to_module.items():
        classes = impl_classes_by_file.get(modfile, {})
        impl_node = classes.get(name)
        members = _class_members(impl_node) if impl_node is not None else set()
        core_node = core_classes.get(name)
        if core_node is not None:
            members |= _class_members(core_node)
        member_sets[name] = members
    return member_sets


def _iter_production_sources():
    for root in PRODUCTION_DIRS:
        yield from root.rglob("*.py")


def _iter_tool_calls(tree: ast.Module):
    """Yield (class_name, method_name, lineno) for every ``tool.X.method(...)`` call."""
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if not isinstance(func, ast.Attribute):
            continue
        method_name = func.attr
        owner = func.value
        if not isinstance(owner, ast.Attribute):
            continue
        class_name = owner.attr
        base = owner.value
        if not (isinstance(base, ast.Name) and base.id == "tool"):
            continue
        yield class_name, method_name, node.lineno


def test_tool_method_calls_resolve_to_real_members():
    """Every ``tool.<Name>.<method>(...)`` call site must resolve to a member
    that exists on the implementation class or its core/tool.py stub."""
    member_sets = _build_tool_member_sets()
    known_names = set(member_sets)
    offenders = []
    for source in _iter_production_sources():
        tree = _parse(source)
        for class_name, method_name, lineno in _iter_tool_calls(tree):
            if class_name not in known_names:
                continue
            if method_name not in member_sets[class_name]:
                offenders.append(f"{source.relative_to(BONSAI_ROOT.parent)}:{lineno}: tool.{class_name}.{method_name}(")
    if offenders:
        joined = "\n  ".join(sorted(offenders))
        pytest.fail(
            f"Call sites naming a tool.<Name>.<method> that does not exist "
            f"on the implementation class or its core/tool.py stub:\n  {joined}\n"
            f"Either the method was renamed/removed and the call site is stale, "
            f"or it needs to be implemented."
        )
