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

import types
from types import SimpleNamespace

import bpy
import pytest

from bonsai.bim.module.drawing.gizmos import (
    BaseParametricGizmoGroup,
    BaseSchematicGizmoGroup,
    DimensionGizmoConfig,
)

pytestmark = pytest.mark.drawing


@pytest.fixture(autouse=True)
def _require_real_bpy():
    if not isinstance(bpy, types.ModuleType) or hasattr(bpy, "_mock_name"):
        pytest.skip("requires real Blender (bpy is mocked or absent)")


def test_text_formatter_defaults_to_none():
    config = DimensionGizmoConfig(attr_name="length", axis=(1, 0, 0))
    assert config.text_formatter is None


def test_text_formatter_field_stores_callable():
    formatter = lambda props, value: f"{value:.2f}m"  # noqa: E731
    config = DimensionGizmoConfig(attr_name="length", axis=(1, 0, 0), text_formatter=formatter)
    assert config.text_formatter is not None
    assert callable(config.text_formatter)


def test_text_formatter_receives_props_and_value():
    formatter = lambda props, value: f"{props.label}={value}"  # noqa: E731
    config = DimensionGizmoConfig(attr_name="length", axis=(1, 0, 0), text_formatter=formatter)
    props = SimpleNamespace(label="L")
    assert config.text_formatter(props, 3.14) == "L=3.14"


def test_parametric_base_enables_dimension_snap_by_default():
    """In-place parametric gizmos align to real-world geometry, so dragging
    must respect the global snap toggle (Ctrl-flip during drag) — same
    contract every door / window / wall / stair / roof / mep dimension
    has shipped with."""
    assert BaseParametricGizmoGroup.snap_enabled_on_dimensions is True


def test_schematic_base_disables_dimension_snap():
    """Schematic dimensions float in viewport space; snapping the dragged
    tip to scene vertices would produce spurious value jumps as the
    mouse crosses unrelated geometry. The opt-out lives on the base so
    every schematic subclass inherits it without per-class wiring."""
    assert BaseSchematicGizmoGroup.snap_enabled_on_dimensions is False
