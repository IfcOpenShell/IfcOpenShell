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

"""Forward-compat AST contract for the preview cancellation registry.

Every ``PointerProperty`` child of ``BIMPreviewProperties`` whose target
PropertyGroup declares an ``is_active`` BoolProperty is a Scene-level
preview. Each must have a matching ``(child_attr, cancel_op_name)`` entry
in ``preview_base.PREVIEW_CANCEL_OPS`` so the Esc dispatcher and the
``load_post`` stale-flag discard both cover it.

A new preview type that defines its own Enable / Decorator without
registering the cancel pair will silently ignore Esc and leave a stuck
``is_active`` flag across file reloads — exactly the failure mode the
sibling forward-compat guards exist to prevent."""

import ast
from pathlib import Path

import pytest

pytestmark = pytest.mark.model


BONSAI_ROOT = Path(__file__).parent.parent.parent / "bonsai"
PROP_FILE = BONSAI_ROOT / "bim" / "module" / "model" / "prop.py"
UMBRELLA_CLASS = "BIMPreviewProperties"


def _find_class(tree: ast.Module, name: str) -> ast.ClassDef | None:
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == name:
            return node
    return None


def _iter_pointer_property_children(class_node: ast.ClassDef):
    """Yield ``(attr_name, target_class_name)`` for each
    ``<attr>: bpy.props.PointerProperty(type=<TargetClass>)`` annotated
    assignment in the umbrella class body.

    Bonsai follows the Blender convention where the property call lives in
    the *annotation* (PEP 526 syntax) rather than the value — Blender's
    PropertyGroup metaclass picks it up at class creation time."""
    for node in class_node.body:
        if not isinstance(node, ast.AnnAssign) or not isinstance(node.target, ast.Name):
            continue
        if not isinstance(node.annotation, ast.Call):
            continue
        func = node.annotation.func
        if not isinstance(func, ast.Attribute) or func.attr != "PointerProperty":
            continue
        for kw in node.annotation.keywords:
            if kw.arg == "type" and isinstance(kw.value, ast.Name):
                yield node.target.id, kw.value.id
                break


def _class_has_is_active_bool(class_node: ast.ClassDef) -> bool:
    """Return True if ``class_node`` declares ``is_active: bpy.props.BoolProperty(...)``."""
    for node in class_node.body:
        if not isinstance(node, ast.AnnAssign) or not isinstance(node.target, ast.Name):
            continue
        if node.target.id != "is_active":
            continue
        if not isinstance(node.annotation, ast.Call):
            continue
        func = node.annotation.func
        if isinstance(func, ast.Attribute) and func.attr == "BoolProperty":
            return True
    return False


def test_every_preview_propertygroup_is_registered_in_cancel_ops() -> None:
    from bonsai.bim.module.model import preview_base

    registered_attrs = {attr for attr, _op in preview_base.PREVIEW_CANCEL_OPS}

    tree = ast.parse(PROP_FILE.read_text(encoding="utf-8"))
    umbrella = _find_class(tree, UMBRELLA_CLASS)
    assert umbrella is not None, (
        f"Could not find {UMBRELLA_CLASS!r} in {PROP_FILE}. Either the umbrella class "
        "was renamed (this test needs updating) or prop.py was restructured."
    )

    preview_children: list[tuple[str, str]] = []
    for attr, target_class_name in _iter_pointer_property_children(umbrella):
        target = _find_class(tree, target_class_name)
        if target is None:
            continue
        if _class_has_is_active_bool(target):
            preview_children.append((attr, target_class_name))

    assert preview_children, (
        "No PointerProperty children with ``is_active`` BoolProperty found under "
        f"{UMBRELLA_CLASS}. Either the preview convention has been refactored away "
        "(this test needs updating) or prop.py was restructured."
    )

    missing = [(attr, cls) for attr, cls in preview_children if attr not in registered_attrs]
    assert not missing, (
        "Every Scene-level preview PropertyGroup must have a matching "
        "(child_attr, cancel_op_name) tuple in preview_base.PREVIEW_CANCEL_OPS so "
        "Esc dispatch and load_post stale-flag discard cover it. Missing entries:\n  "
        + "\n  ".join(f"BIMPreviewProperties.{attr} (target={cls!r})" for attr, cls in missing)
    )


def test_every_cancel_ops_entry_has_a_real_preview_propertygroup() -> None:
    """The reverse contract: a stale entry in ``PREVIEW_CANCEL_OPS`` whose
    PropertyGroup has been deleted would silently leak to every Esc press
    (dispatching to a missing operator raises ``AttributeError`` inside
    ``try_cancel_active_preview``). Pin that the registry never goes
    stale relative to ``BIMPreviewProperties``."""
    from bonsai.bim.module.model import preview_base

    tree = ast.parse(PROP_FILE.read_text(encoding="utf-8"))
    umbrella = _find_class(tree, UMBRELLA_CLASS)
    assert umbrella is not None

    declared_attrs = {attr for attr, _target in _iter_pointer_property_children(umbrella)}
    orphaned = [attr for attr, _op in preview_base.PREVIEW_CANCEL_OPS if attr not in declared_attrs]
    assert not orphaned, (
        "PREVIEW_CANCEL_OPS contains entries whose PointerProperty child no longer "
        f"exists on {UMBRELLA_CLASS}. Drop the stale tuple(s):\n  " + "\n  ".join(orphaned)
    )
