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

"""Regression contract for #9426: finishing the polyline slab tool without
enough points must end quietly instead of raising IndexError.

``DumbSlabGenerator`` needs a live IFC file and a relating type to construct,
so the tests call ``derive_from_polyline`` as a plain function against a stub
``self``. That is the exact code path the traceback in #9426 names, and the
too-few-points guard has to fire before any indexing for these to pass."""

from types import SimpleNamespace
from unittest.mock import patch

import pytest

pytestmark = pytest.mark.model


class _Point:
    def __init__(self, x, y, z=0.0):
        self.x = x
        self.y = y
        self.z = z


def _polyline_props(points=None):
    """Mimic the polyline props: an empty ``insertion_polyline`` collection
    when nothing was drawn, otherwise a single entry holding the points."""
    if points is None:
        return SimpleNamespace(insertion_polyline=[])
    return SimpleNamespace(insertion_polyline=[SimpleNamespace(polyline_points=points)])


def _derive(points):
    from bonsai.bim.module.model.slab import DumbSlabGenerator

    generator = SimpleNamespace(container_obj=None, location=None, polyline=None)
    with patch("bonsai.tool.Model.get_polyline_props", return_value=_polyline_props(points)):
        return DumbSlabGenerator.derive_from_polyline(generator)


def test_empty_polyline_returns_without_creating_a_slab():
    assert _derive(None) is None


def test_polyline_with_two_points_returns_without_creating_a_slab():
    assert _derive([_Point(0.0, 0.0), _Point(1.0, 0.0)]) is None
