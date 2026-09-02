# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2026 Petru Conduraru <petru@bimvoice.com>
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

"""Forward-compat AST contract for the MEP quick-add profile Position fix.

``Position`` is mandatory on ``IfcRectangleProfileDef``, ``IfcCircleProfileDef``,
``IfcCircleHollowProfileDef``, ``IfcRectangleHollowProfileDef`` and
``IfcUShapeProfileDef`` in IFC2X3 (it is only optional from IFC4 onward). The
"Add Element" quick-add (``bim.add_element``) creates these profiles directly
via ``file.create_entity(...)`` for the MEP flow segment templates, and would
previously leave ``Position`` unset, producing an IFC2X3 file that fails
schema validation.

``bpy`` is not available in this test environment, so the operator's
``execute()`` cannot be exercised directly. This test instead pins the fix at
the source level: every ``create_entity`` call for one of the five profile
classes above, within ``bonsai/bim/module/root/operator.py``, must pass a
``Position`` keyword argument. A regression here (someone reintroducing one
of these calls without ``Position``) will fail this test even without bpy.
"""

import ast
from pathlib import Path

import pytest

pytestmark = pytest.mark.root

BONSAI_ROOT_OPERATOR = Path(__file__).resolve().parents[4] / "bonsai" / "bim" / "module" / "root" / "operator.py"

# Profile classes where Position is mandatory in IFC2X3 but optional in IFC4.
PROFILE_CLASSES_REQUIRING_POSITION = {
    "IfcRectangleProfileDef",
    "IfcCircleProfileDef",
    "IfcCircleHollowProfileDef",
    "IfcRectangleHollowProfileDef",
    "IfcUShapeProfileDef",
}


def _find_create_entity_profile_calls(tree: ast.Module) -> list[ast.Call]:
    calls = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if not (isinstance(func, ast.Attribute) and func.attr == "create_entity"):
            continue
        if not node.args:
            continue
        first_arg = node.args[0]
        if not isinstance(first_arg, ast.Constant) or not isinstance(first_arg.value, str):
            continue
        if first_arg.value in PROFILE_CLASSES_REQUIRING_POSITION:
            calls.append(node)
    return calls


def test_flow_segment_profile_create_entity_calls_set_position() -> None:
    tree = ast.parse(BONSAI_ROOT_OPERATOR.read_text(encoding="utf-8"))
    calls = _find_create_entity_profile_calls(tree)

    # Sanity check: make sure the AST walk actually found the quick-add call
    # sites, so this test cannot silently pass by finding nothing.
    assert len(calls) >= 5, (
        f"Expected to find at least 5 create_entity(...) calls for "
        f"{sorted(PROFILE_CLASSES_REQUIRING_POSITION)} in {BONSAI_ROOT_OPERATOR.name}, "
        f"found {len(calls)}. Did the MEP quick-add profile creation move or get renamed?"
    )

    missing_position = []
    for call in calls:
        ifc_class = call.args[0].value
        kwarg_names = {kw.arg for kw in call.keywords if kw.arg is not None}
        if "Position" not in kwarg_names:
            missing_position.append((ifc_class, call.lineno))

    assert not missing_position, (
        "The following create_entity(...) calls omit the mandatory-in-IFC2X3 "
        f"Position attribute: {missing_position}. This reproduces the bug where "
        "MEP quick-add flow segments fail IFC2X3 validation."
    )
