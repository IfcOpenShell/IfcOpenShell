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

"""Forward-compat AST guard: every multi-object wall topology GizmoGroup
filters Bonsai array children via ``_wall_topology_gizmo_poll_gate`` or
the central ``any_selected_is_array_child`` predicate.

Allow-list (gizmos intentionally outside the rule):

- ``GizmoWallEdition`` — single-object parametric edit gizmo. Its base
  parametric poll already filters array children.
- ``GizmoSlabEdition`` — same as ``GizmoWallEdition`` (inherits
  ``BaseParametricGizmoGroup`` whose poll filters array children).
- ``GizmoWallFilletPreview`` — the preview-owner whose poll must fire
  WHILE its own preview is active; routing it through the topology gate
  would self-block it.

Host-opening gizmos live in a sibling module and intentionally use the
loose base ``_wall_gizmo_poll_gate``: openings track with the child
through ``regenerate_array`` and stay authorable on children.

A new wall ``GizmoGroup`` added without the filter (and not added to the
allow-list with an explanation) fails this test."""

import ast
import inspect

import bpy
import pytest

pytestmark = pytest.mark.model

# Wall gizmo groups intentionally outside the rule. Add a new entry only
# with the in-code reasoning above.
_ALLOWLIST = frozenset({"GizmoSlabEdition", "GizmoWallEdition", "GizmoWallFilletPreview"})

_REQUIRED_CALLEES = frozenset(
    {"_wall_topology_gizmo_poll_gate", "_slab_connection_gizmo_poll_gate", "any_selected_is_array_child"}
)


def _wall_module_source():
    from bonsai.bim.module.model import wall as wall_mod

    return inspect.getsource(wall_mod), wall_mod.__name__


def _wall_gizmo_group_classes():
    """All ``bpy.types.GizmoGroup`` subclasses defined locally in wall.py."""
    from bonsai.bim.module.model import wall as wall_mod

    out = []
    for name in dir(wall_mod):
        obj = getattr(wall_mod, name)
        if not isinstance(obj, type):
            continue
        if not issubclass(obj, bpy.types.GizmoGroup) or obj is bpy.types.GizmoGroup:
            continue
        if obj.__module__ != wall_mod.__name__:
            continue
        out.append((name, obj))
    return out


def _poll_function_calls(class_node):
    """Names of every function called inside ``class_node``'s ``poll`` body.

    ``ast.Call.func`` may be an ``ast.Name`` (bare call) or an ``ast.Attribute``
    (dotted call). For the dotted case the leaf attribute is returned so
    ``tool.Blender.Modifier.any_selected_is_array_child(...)`` registers as
    ``any_selected_is_array_child``."""
    poll_node = next(
        (node for node in class_node.body if isinstance(node, ast.FunctionDef) and node.name == "poll"),
        None,
    )
    if poll_node is None:
        return None
    names = set()
    for sub in ast.walk(poll_node):
        if not isinstance(sub, ast.Call):
            continue
        func = sub.func
        if isinstance(func, ast.Name):
            names.add(func.id)
        elif isinstance(func, ast.Attribute):
            names.add(func.attr)
    return names


def test_every_wall_gizmo_group_filters_array_children_or_is_allowlisted():
    """For every locally-defined wall ``GizmoGroup`` not in the allow-list,
    its ``poll`` must call ``_wall_gizmo_poll_gate`` or the central
    ``any_selected_is_array_child`` predicate. A failure surfaces the list
    of offending classes — the fix is a single early-return through the
    central helper, mirroring the existing peers."""
    source, _module_name = _wall_module_source()
    tree = ast.parse(source)
    class_nodes = {node.name: node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)}
    offenders = []
    for class_name, _cls in _wall_gizmo_group_classes():
        if class_name in _ALLOWLIST:
            continue
        node = class_nodes.get(class_name)
        if node is None:
            offenders.append((class_name, "AST parse did not find the class"))
            continue
        calls = _poll_function_calls(node)
        if calls is None:
            offenders.append((class_name, "no poll() defined; expected the array-child filter call"))
            continue
        if not (calls & _REQUIRED_CALLEES):
            offenders.append((class_name, f"poll() does not call any of {sorted(_REQUIRED_CALLEES)}"))

    assert not offenders, (
        "Wall GizmoGroup classes missing the array-child filter: "
        + ", ".join(f"{n} — {why}" for n, why in offenders)
        + ". Route the poll through `_wall_topology_gizmo_poll_gate(context)` "
        "so the central `any_selected_is_array_child` filter applies, or add "
        "the class to the file's allow-list with a documented reason."
    )
