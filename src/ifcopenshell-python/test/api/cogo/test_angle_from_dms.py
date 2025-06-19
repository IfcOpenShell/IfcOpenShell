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


def test_angle_from_dms():
    assert 0.78987057 == pytest.approx(ifcopenshell.api.cogo.angle_from_dms(45,15,22.5))
    assert 2.36066689 == pytest.approx(ifcopenshell.api.cogo.angle_from_dms(135,15,22.5))
    assert 3.75693030 == pytest.approx(ifcopenshell.api.cogo.angle_from_dms(215,15,22.5))
    assert 5.50225955 == pytest.approx(ifcopenshell.api.cogo.angle_from_dms(315,15,22.5))

    assert -0.780925757 == pytest.approx(ifcopenshell.api.cogo.angle_from_dms(-45,15,22.5))
    assert -2.351722084 == pytest.approx(ifcopenshell.api.cogo.angle_from_dms(-135,15,22.5))
    assert -3.747985486 == pytest.approx(ifcopenshell.api.cogo.angle_from_dms(-215,15,22.5))
    assert -5.493314738 == pytest.approx(ifcopenshell.api.cogo.angle_from_dms(-315,15,22.5))

    with pytest.raises(ValueError,match="Invalid argument"):
        ifcopenshell.api.cogo.angle_from_dms(45,-15,22.5)

    with pytest.raises(ValueError,match="Invalid argument"):
        ifcopenshell.api.cogo.angle_from_dms(45,90,22.5)

    with pytest.raises(ValueError,match="Invalid argument"):
        ifcopenshell.api.cogo.angle_from_dms(45,15,-22.5)

    with pytest.raises(ValueError,match="Invalid argument"):
        ifcopenshell.api.cogo.angle_from_dms(45,15,90.5)

test_angle_from_dms()

