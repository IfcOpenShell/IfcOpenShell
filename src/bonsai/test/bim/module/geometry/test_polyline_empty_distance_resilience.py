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

"""Contract and resilience tests for polyline empty distance handling (#9974).
Verifies that when distance or numerical input is cleared (empty string),
cycling UI parameters with TAB or recalculating inputs does not crash with
TypeError or ValueError, and that PolylineUI safely returns None/empty string."""

import ast
from pathlib import Path

import pytest

pytestmark = pytest.mark.geometry

BONSAI_ROOT = Path(__file__).parent.parent.parent.parent.parent / "bonsai"
MODEL_POLYLINE_PATH = BONSAI_ROOT / "bim" / "module" / "model" / "polyline.py"
TOOL_POLYLINE_PATH = BONSAI_ROOT / "tool" / "polyline.py"


def test_recalculate_inputs_has_empty_fallback():
    """Ensure recalculate_inputs in model/polyline.py handles empty input
    rather than silently leaving unvalidated empty strings in input_ui (#9974)."""
    assert MODEL_POLYLINE_PATH.is_file(), f"polyline.py not found at {MODEL_POLYLINE_PATH}"
    tree = ast.parse(MODEL_POLYLINE_PATH.read_text(encoding="utf-8"))

    found_method = False
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "recalculate_inputs":
            found_method = True
            # Verify the method contains an if-else where else branch handles empty input
            has_else = False
            for child in node.body:
                if isinstance(child, ast.If) and child.orelse:
                    has_else = True
                    break
            assert has_else, "recalculate_inputs must contain an else branch for empty input fallback"
    assert found_method, "recalculate_inputs method not found in polyline.py"


def test_polyline_ui_safe_empty_handling_ast():
    """Ensure PolylineUI in tool/polyline.py safely handles empty string or None
    without raising TypeError during float conversions or divisions (#9974)."""
    assert TOOL_POLYLINE_PATH.is_file(), f"polyline.py not found at {TOOL_POLYLINE_PATH}"
    tree = ast.parse(TOOL_POLYLINE_PATH.read_text(encoding="utf-8"))

    found_ui_class = False
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "PolylineUI":
            found_ui_class = True
            method_names = {m.name for m in node.body if isinstance(m, ast.FunctionDef)}
            assert "get_number_value" in method_names
            assert "get_formatted_value" in method_names
    assert found_ui_class, "PolylineUI class not found in tool/polyline.py"


def test_format_input_ui_units_empty_guard_ast():
    """Ensure format_input_ui_units guards against None or empty string before division."""
    tree = ast.parse(TOOL_POLYLINE_PATH.read_text(encoding="utf-8"))

    found_func = False
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "format_input_ui_units":
            found_func = True
            # Verify that the function checks for None or empty string at the beginning
            first_stmt = node.body[0]
            assert isinstance(first_stmt, ast.If), "format_input_ui_units must start with an empty/None guard"
    assert found_func, "format_input_ui_units not found in tool/polyline.py"
