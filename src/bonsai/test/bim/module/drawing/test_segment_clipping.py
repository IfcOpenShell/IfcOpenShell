# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Maxim Vasilyev <qwiglydee@gmail.com>
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

import pytest
from mathutils import Vector
from bonsai.bim.module.drawing.helper import clip_segment


BOUNDS = (10, 30, 10, 30, None, None)

SEGMENTS_INSIDE = (
    (Vector((15, 20)), Vector((25, 20))),
    (Vector((20, 15)), Vector((20, 25))),
    (Vector((15, 15)), Vector((25, 25))),
    (Vector((15, 25)), Vector((25, 15))),
)

SEGMENTS_OUTSIDE = (
    (Vector((15, 35)), Vector((25, 35))),
    (Vector((25, 35)), Vector((35, 25))),
    (Vector((35, 25)), Vector((35, 15))),
    (Vector((35, 15)), Vector((25, 5))),
    (Vector((25, 5)), Vector((15, 5))),
    (Vector((15, 5)), Vector((5, 15))),
    (Vector((5, 15)), Vector((5, 25))),
    (Vector((5, 25)), Vector((15, 35))),
)

SEGMENTS_CLIPPED = (
    ((Vector((5, 20)), Vector((15, 20))), (Vector((10, 20)), Vector((15, 20)))),
    ((Vector((25, 20)), Vector((35, 20))), (Vector((25, 20)), Vector((30, 20)))),
    ((Vector((20, 5)), Vector((20, 15))), (Vector((20, 10)), Vector((20, 15)))),
    ((Vector((20, 15)), Vector((20, 35))), (Vector((20, 15)), Vector((20, 30)))),
    ((Vector((5, 20)), Vector((20, 35))), (Vector((10, 25)), Vector((15, 30)))),
    ((Vector((5, 20)), Vector((20, 5))), (Vector((10, 15)), Vector((15, 10)))),
    ((Vector((35, 20)), Vector((20, 35))), (Vector((30, 25)), Vector((25, 30)))),
    ((Vector((35, 20)), Vector((20, 5))), (Vector((30, 15)), Vector((25, 10)))),
)


@pytest.mark.parametrize("segment", SEGMENTS_INSIDE)
def test_clip_inside(segment):
    clipped = clip_segment(BOUNDS, segment)
    assert clipped == segment


@pytest.mark.parametrize("segment", SEGMENTS_OUTSIDE)
def test_clip_outside(segment):
    clipped = clip_segment(BOUNDS, segment)
    assert clipped is None


@pytest.mark.parametrize("segment,expected", SEGMENTS_CLIPPED)
def test_clip_crossing(segment, expected):
    clipped = clip_segment(BOUNDS, segment)
    assert clipped == expected
