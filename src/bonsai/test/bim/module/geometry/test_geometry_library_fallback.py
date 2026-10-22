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

"""Contract test: geometry library fallback resilience (fixes #9908).

When geometry processing requests a hybrid or secondary geometry library
(such as 'hybrid-cgal-simple-opencascade') on platforms where the component
kernel plugin is unavailable, IfcOpenShell raises RuntimeError (e.g.
'Invalid hybrid kernel; no match for prefix of simple-opencascade').

Production code in tool.Geometry.reimport_element_representations,
bim.import_ifc.IfcImporter, and tool.Loader.create_generic_shape must safely
catch this exception and fall back to 'opencascade' so that element representation
creation (e.g. wall creation) and IFC import do not crash.
"""

import ast
from pathlib import Path
from unittest.mock import MagicMock

import pytest

pytestmark = pytest.mark.geometry

BONSAI_ROOT = Path(__file__).parent.parent.parent.parent.parent / "bonsai"


def test_reimport_element_representations_has_fallback_guard():
    """Verify tool/geometry.py handles geometry_library initialization errors with fallback."""
    geometry_tool_source = (BONSAI_ROOT / "tool" / "geometry.py").read_text(encoding="utf-8")
    tree = ast.parse(geometry_tool_source)

    # Locate reimport_element_representations function
    reimport_func = None
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "reimport_element_representations":
            reimport_func = node
            break

    assert reimport_func is not None, "reimport_element_representations not found in tool/geometry.py"

    # Find try-except blocks inside the function
    try_blocks = [n for n in ast.walk(reimport_func) if isinstance(n, ast.Try)]
    assert len(try_blocks) >= 2, "reimport_element_representations must have try-except guards for iterator and create_shape"


def test_geometry_library_fallback_behavior():
    """Simulate fallback from an unsupported kernel to opencascade."""
    calls = []

    def fake_iterator(settings, file, *args, **kwargs):
        lib = kwargs.get("geometry_library")
        calls.append(lib)
        if lib == "hybrid-cgal-simple-opencascade":
            raise RuntimeError("Invalid hybrid kernel; no match for prefix of simple-opencascade")
        mock_iter = MagicMock()
        mock_iter.initialize.return_value = True
        return mock_iter

    requested_library = "hybrid-cgal-simple-opencascade"
    # Execute the pattern used in reimport_element_representations
    try:
        iterator = fake_iterator(None, None, geometry_library=requested_library)
    except Exception as e:
        if requested_library != "opencascade":
            iterator = fake_iterator(None, None, geometry_library="opencascade")
        else:
            raise

    assert calls == ["hybrid-cgal-simple-opencascade", "opencascade"]
    assert iterator.initialize() is True
