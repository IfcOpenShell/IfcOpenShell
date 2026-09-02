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

"""End-to-end regression test for a specific reported defect (#8046).

An Entity facet's name written as an xs:restriction (an enumeration list
rather than a single simpleValue) used to crash with AttributeError on
IFC2X3 whenever the requirement failed: the type-inference branch called
str methods (endswith, an f-string) directly on self.name, which is a
Restriction object, not a string, when the requirement is a restriction.
"""

import os

import ifcopenshell

from ifctester import ids

FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures", "entity_restriction_ifc2x3_fail")
SPEC = os.path.join(FIXTURES, "entity_restriction_ifc2x3_fail.ids")
MODEL = os.path.join(FIXTURES, "entity_restriction_ifc2x3_fail.ifc")


class TestEntityRestrictionIfc2x3FailFixture:
    def test_failing_restriction_entity_requirement_does_not_crash(self):
        specs = ids.open(SPEC)
        ifc = ifcopenshell.open(MODEL)
        # This used to raise AttributeError instead of returning a result.
        specs.validate(ifc)
        spec = specs.specifications[0]
        assert spec.requirements[0].status is False
        assert spec.status is False
