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

"""Contract tests for profile auto-detection resilience (#9922).
Verifies that profile auto-detection methods in ``helper.py`` do not contain
unhandled ``assert face is not None`` statements, and that ``operator.py`` safely
guards the detection results against missing keys and empty collections."""

import ast
from pathlib import Path

import pytest

pytestmark = pytest.mark.geometry

BONSAI_ROOT = Path(__file__).parent.parent.parent.parent.parent / "bonsai"
HELPER_PATH = BONSAI_ROOT / "bim" / "module" / "geometry" / "helper.py"
OPERATOR_PATH = BONSAI_ROOT / "bim" / "module" / "profile" / "operator.py"

TARGET_METHODS = (
    "auto_detect_rectangle_profile_extruded_area_solid",
    "auto_detect_circle_profile_extruded_area_solid",
    "auto_detect_arbitrary_closed_profile_extruded_area_solid",
    "auto_detect_arbitrary_profile_with_voids_extruded_area_solid",
)


def test_helper_profile_auto_detect_has_no_bare_face_asserts():
    """Ensure none of the profile auto-detection methods in helper.py contain
    an unhandled 'assert face is not None' which crashes Blender when faces
    have non-negative-z normals or when mesh has no void candidates (#9922)."""
    assert HELPER_PATH.is_file(), f"helper.py not found at {HELPER_PATH}"
    tree = ast.parse(HELPER_PATH.read_text(encoding="utf-8"))

    found_methods = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name in TARGET_METHODS:
            found_methods.add(node.name)
            for child in ast.walk(node):
                if isinstance(child, ast.Assert):
                    # Check if assert test is checking face is not None
                    if isinstance(child.test, ast.Compare):
                        left = child.test.left
                        if isinstance(left, ast.Name) and left.id == "face":
                            pytest.fail(
                                f"Found forbidden 'assert face ...' in {node.name} at line {child.lineno}. "
                                "Methods must use fallback face selection or return safe empty structures."
                            )

    assert found_methods == set(TARGET_METHODS), f"Missing expected target methods: {set(TARGET_METHODS) - found_methods}"


def test_operator_safely_accesses_inner_curves_and_profile():
    """Ensure AddProfileDef operator guards access to 'inner_curves' and does not
    blindly index indices['inner_curves'] when indices is empty (#9922)."""
    assert OPERATOR_PATH.is_file(), f"operator.py not found at {OPERATOR_PATH}"
    tree = ast.parse(OPERATOR_PATH.read_text(encoding="utf-8"))

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "AddProfileDef":
            # Search for subscripts like indices['inner_curves'] inside the class
            for child in ast.walk(node):
                if isinstance(child, ast.Subscript):
                    if (
                        isinstance(child.value, ast.Name)
                        and child.value.id == "indices"
                        and isinstance(child.slice, ast.Constant)
                        and child.slice.value == "inner_curves"
                    ):
                        pytest.fail(
                            f"Direct indices['inner_curves'] subscript found in AddProfileDef at line {child.lineno}. "
                            "Use indices.get('inner_curves') to avoid KeyError when void detection returns empty."
                        )
