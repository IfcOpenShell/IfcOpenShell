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

"""Forward-compat AST contract: ``HasShapeAspects`` is an IFC4+ inverse;
direct attribute access raises ``AttributeError`` on pre-IFC4 entity
instances. Production code must read it through ``getattr`` so the
absence in earlier schemas degrades to an empty iterable."""

import ast
from pathlib import Path

import pytest

pytestmark = pytest.mark.geometry


BONSAI_ROOT = Path(__file__).parent.parent.parent.parent.parent / "bonsai"
PRODUCTION_DIRS = (BONSAI_ROOT / "bim", BONSAI_ROOT / "tool", BONSAI_ROOT / "core")

ATTR_NAME = "HasShapeAspects"


def _iter_production_sources():
    for root in PRODUCTION_DIRS:
        yield from root.rglob("*.py")


def test_has_shape_aspects_access_uses_getattr_guard():
    """Every read of ``HasShapeAspects`` in production code must go through
    ``getattr(<expr>, "HasShapeAspects", <default>)`` so files using
    schemas that omit the inverse return the default instead of raising."""
    offenders = []
    for source in _iter_production_sources():
        tree = ast.parse(source.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Attribute) and node.attr == ATTR_NAME:
                offenders.append(f"{source.relative_to(BONSAI_ROOT.parent)}:{node.lineno}")
    if offenders:
        joined = "\n  ".join(sorted(offenders))
        pytest.fail(
            f"Direct .{ATTR_NAME} attribute access in production code:\n  {joined}\n"
            f"Wrap with getattr(<expr>, '{ATTR_NAME}', ()) so pre-IFC4 schemas "
            f"do not raise AttributeError."
        )
