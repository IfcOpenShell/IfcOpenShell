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

"""End-to-end regression test for a specific reported defect.

An IDS value with an unrecognised boolean spelling (here "off") used to fall
through to bool(value), which is True for any non-empty string. That made an
unrecognised spelling match a true boolean property, turning a genuine
violation into a false pass.
"""

import os

import ifcopenshell

from ifctester import ids

FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures", "property_boolean_unrecognised_spelling")
SPEC = os.path.join(FIXTURES, "property_boolean_unrecognised_spelling.ids")
MODEL = os.path.join(FIXTURES, "property_boolean_unrecognised_spelling.ifc")


class TestPropertyBooleanUnrecognisedSpellingFixture:
    def test_unrecognised_spelling_does_not_match_a_true_value(self):
        specs = ids.open(SPEC)
        ifc = ifcopenshell.open(MODEL)
        specs.validate(ifc)
        spec = specs.specifications[0]
        assert spec.requirements[0].status is False
        assert spec.status is False
