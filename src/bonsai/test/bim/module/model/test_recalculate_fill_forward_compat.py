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

"""AST contract: ``RecalculateFill`` must invoke
``regenerate_simple_opening_bodies`` before recutting hosts.

Hosts recut with a surgical mesh-only path don't refresh the shared mapped
opening source — so any change to a parametric filling's dimensions stays
invisible at the opening boundary until the body representation is
regenerated. Pinning the call site forces future refactors to keep the
regen step in place."""

import ast
from pathlib import Path

import pytest

pytestmark = pytest.mark.model


def _recalculate_fill_body_source() -> str:
    from bonsai.bim.module.model import opening as opening_module

    source = Path(opening_module.__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "RecalculateFill":
            for child in node.body:
                if isinstance(child, ast.FunctionDef) and child.name == "_recalculate_fills":
                    return ast.unparse(child)
    raise AssertionError("RecalculateFill._recalculate_fills was not found in opening.py")


def test_recalculate_fill_regenerates_opening_bodies_before_recut():
    body = _recalculate_fill_body_source()
    assert "regenerate_filling_opening_body" in body, (
        "RecalculateFill._recalculate_fills must call "
        "tool.Model.regenerate_filling_opening_body for each selected "
        "filling before recutting the host. Without that call the host is "
        "recut against a stale shared mapped opening source, so changes "
        "to filling dimensions never surface."
    )
