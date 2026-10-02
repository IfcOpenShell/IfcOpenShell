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

"""End-to-end regression tests for a specific reported defect.

A prohibited Property requirement with a pattern-matched propertySet (e.g.
propertySet matching several "Pset_*" sets) evaluated its matching sets with
a single shared is_pass accumulator. An earlier set that lacked the property,
or had a non-matching value, permanently set is_pass to False; a later set
that actually held the prohibited value could then never flip the verdict
back, because a value match only left is_pass unchanged rather than setting
it. The requirement silently passed even though one of the matched sets held
exactly the prohibited value.
"""

import os

import ifcopenshell

from ifctester import ids

FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures", "property_prohibited_multi_pset")
SPEC = os.path.join(FIXTURES, "property_prohibited_multi_pset.ids")


class TestPropertyProhibitedMultiPsetFixture:
    def test_no_matching_pset_has_the_value_passes_the_prohibition(self):
        specs = ids.open(SPEC)
        ifc = ifcopenshell.open(os.path.join(FIXTURES, "pass-no_pset_matches.ifc"))
        specs.validate(ifc)
        spec = specs.specifications[0]
        assert spec.status is True
        assert spec.requirements[0].status is True

    def test_a_later_matching_pset_with_the_value_fails_the_prohibition(self):
        specs = ids.open(SPEC)
        ifc = ifcopenshell.open(os.path.join(FIXTURES, "fail-second_pset_matches.ifc"))
        specs.validate(ifc)
        spec = specs.specifications[0]
        assert spec.status is False
        assert spec.requirements[0].status is False
