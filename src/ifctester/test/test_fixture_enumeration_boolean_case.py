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

"""End-to-end regression test for exact-case enumeration matching on xs:boolean.

cast_to_value() falls back to bool(str) for any string it does not recognise
as "true"/"1"/"false"/"0". bool() is truthy for any non-empty string, so an
enumeration listing only "FALSE" incorrectly matched an actual value of True.
"""

import os

import ifcopenshell

from ifctester import ids

FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")


class TestEnumerationBooleanCaseFixture:
    def test_an_unrecognised_enumeration_literal_never_matches(self):
        directory = os.path.join(FIXTURES, "enumeration_boolean_case")
        specs = ids.open(os.path.join(directory, "enumeration_boolean_case.ids"))
        ifc = ifcopenshell.open(os.path.join(directory, "enumeration_boolean_case.ifc"))
        specs.validate(ifc)
        spec = specs.specifications[0]

        # The actual value is True. An enumeration of only "FALSE" must fail,
        # not silently pass because bool("FALSE") is truthy.
        assert spec.requirements[0].status is False

        # Sanity: lowercase "true" is the recognised XSD boolean literal and
        # must still match an actual value of True after the fix.
        assert spec.requirements[1].status is True
