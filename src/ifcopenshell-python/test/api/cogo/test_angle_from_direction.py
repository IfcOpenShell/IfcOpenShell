# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2025 Thomas Krijnen <thomas@aecgeeks.com>
#
# This file is part of IfcOpenShell.
#
# IfcOpenShell is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcOpenShell is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcOpenShell.  If not, see <http://www.gnu.org/licenses/>.

import pytest
import ifcopenshell.api.cogo
import math


def test_angle_from_direction():
    assert 0.780925757 == pytest.approx(ifcopenshell.api.cogo.angle_from_direction("N 45 15 22.5 E"))
    assert 2.360666897 == pytest.approx(ifcopenshell.api.cogo.angle_from_direction("N 45 15 22.5 W"))
    assert 3.922518411 == pytest.approx(ifcopenshell.api.cogo.angle_from_direction("S 45 15 22.5 W"))
    assert 5.502259551 == pytest.approx(ifcopenshell.api.cogo.angle_from_direction("S 45 15 22.5 E"))

    assert 0.780925757 == pytest.approx(ifcopenshell.api.cogo.angle_from_direction("n 45 15 22.5 e"))
    assert 2.360666897 == pytest.approx(ifcopenshell.api.cogo.angle_from_direction("n 45 15 22.5 w"))
    assert 3.922518411 == pytest.approx(ifcopenshell.api.cogo.angle_from_direction("s 45 15 22.5 w"))
    assert 5.502259551 == pytest.approx(ifcopenshell.api.cogo.angle_from_direction("s 45 15 22.5 e"))

    assert 0.0 == pytest.approx(ifcopenshell.api.cogo.angle_from_direction("N 90 E"))
    assert 0.0 == pytest.approx(ifcopenshell.api.cogo.angle_from_direction("S 90 E"))

    assert 3.14159265 == pytest.approx(ifcopenshell.api.cogo.angle_from_direction("N 90 W"))
    assert 3.14159265 == pytest.approx(ifcopenshell.api.cogo.angle_from_direction("S 90 W"))

    assert 2.094395102 == pytest.approx(ifcopenshell.api.cogo.angle_from_direction("N 30 W"))
    assert 2.097303984 == pytest.approx(ifcopenshell.api.cogo.angle_from_direction("N 30 10 W"))

    assert 1.570791478 == pytest.approx(ifcopenshell.api.cogo.angle_from_direction("N 00 00 1 E"))
    assert 1.570791478 == pytest.approx(ifcopenshell.api.cogo.angle_from_direction("N 0 0 1 E"))
    assert 1.570791478 == pytest.approx(ifcopenshell.api.cogo.angle_from_direction("N 00 00 1.0 E"))

    with pytest.raises(ValueError,match="Invalid direction string"):
        ifcopenshell.api.cogo.angle_from_direction("Bad String")

    with pytest.raises(ValueError,match="Invalid direction string"):
        ifcopenshell.api.cogo.angle_from_direction("Very Bad String")

    with pytest.raises(ValueError,match="Invalid direction string"):
        ifcopenshell.api.cogo.angle_from_direction("N 100 15 22.5 E")

    with pytest.raises(ValueError,match="Invalid direction string"):
        ifcopenshell.api.cogo.angle_from_direction("N -45 15 22.5 E")

    with pytest.raises(ValueError,match="Invalid direction string"):
        ifcopenshell.api.cogo.angle_from_direction("N 45 -15 22.5 E")

    with pytest.raises(ValueError,match="Invalid direction string"):
        ifcopenshell.api.cogo.angle_from_direction("N 45 88 22.5 E")

    with pytest.raises(ValueError,match="Invalid direction string"):
        ifcopenshell.api.cogo.angle_from_direction("N 45 15 -22.5 E")

    with pytest.raises(ValueError,match="Invalid direction string"):
        ifcopenshell.api.cogo.angle_from_direction("N 45 15 99.5 E")

test_angle_from_direction()

