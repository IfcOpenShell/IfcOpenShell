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

import os
import warnings

import ifcopenshell

from ifctester import ids

FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures", "restriction_unsupported_fraction_digits")
SPEC = os.path.join(FIXTURES, "restriction_unsupported_fraction_digits.ids")
MODEL = os.path.join(FIXTURES, "restriction_unsupported_fraction_digits.ifc")


class TestRestrictionUnsupportedFractionDigitsFixture:
    def test_loading_the_restriction_warns(self):
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            ids.open(SPEC)
        assert any("fractionDigits" in str(w.message) for w in caught)

    def test_restriction_is_not_enforced(self):
        specs = ids.open(SPEC)
        ifc = ifcopenshell.open(MODEL)
        specs.validate(ifc)
        spec = specs.specifications[0]
        assert spec.requirements[0].status is True
        assert spec.status is True
