# IfcTester - IDS based model auditing
# Copyright (C) 2021-2022 Thomas Krijnen <thomas@aecgeeks.com>, Dion Moult <dion@thinkmoult.com>
#
# This file is part of IfcTester.
#
# IfcTester is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcTester is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcTester.  If not, see <http://www.gnu.org/licenses/>.

# This file was generated with the assistance of an AI coding tool.

"""End-to-end regression test for the absolute component of the IDS equality tolerance."""

import os

import ifcopenshell

from ifctester import ids
from ifctester.facet import is_x

FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")


class TestToleranceAbsoluteComponentFixture:
    def test_reals_within_the_documented_tolerance_pass(self):
        # IDS tolerance.md defines the interval as
        # (v - abs(v) * 1e-6 - 1e-6) .. (v + abs(v) * 1e-6 + 1e-6).
        # 1.0000015 is inside the interval for 1.0 and 5e-7 is inside the
        # interval for 0.0, which has no relative component at all.
        directory = os.path.join(FIXTURES, "tolerance_absolute_component")
        specs = ids.open(os.path.join(directory, "tolerance_absolute_component.ids"))
        ifc = ifcopenshell.open(os.path.join(directory, "tolerance_absolute_component.ifc"))
        specs.validate(ifc)
        spec = specs.specifications[0]
        assert spec.requirements[0].status is True
        assert spec.requirements[1].status is True
        assert spec.status is True


class TestIsX:
    def test_zero_uses_the_absolute_tolerance(self):
        assert is_x(0.0, 0.0)
        assert is_x(1e-6, 0.0)
        assert is_x(-1e-6, 0.0)
        assert not is_x(1.1e-6, 0.0)
        assert not is_x(-1.1e-6, 0.0)

    def test_positive_and_negative_values_are_symmetric(self):
        assert is_x(1.0000015, 1.0)
        assert is_x(-1.0000015, -1.0)
        assert is_x(0.9999985, 1.0)
        assert is_x(-0.9999985, -1.0)
        assert not is_x(1.0000021, 1.0)
        assert not is_x(-1.0000021, -1.0)
        assert not is_x(0.9999979, 1.0)
        assert not is_x(-0.9999979, -1.0)
