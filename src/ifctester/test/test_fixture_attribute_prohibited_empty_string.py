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

buildingSMART/IDS attribute-facet.md states, for a PROHIBITED attribute
requirement with no value given: "The attribute ... must not exist on
applicable objects, even if empty." An attribute explicitly set to an
empty string is still populated in the STEP file (as opposed to being
left null), so it must fail the prohibition, not pass it silently.
"""

import os

import ifcopenshell

from ifctester import ids

FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures", "attribute_prohibited_empty_string")
SPEC = os.path.join(FIXTURES, "attribute_prohibited_empty_string.ids")


class TestAttributeProhibitedEmptyStringFixture:
    def test_unset_description_passes_the_prohibition(self):
        specs = ids.open(SPEC)
        ifc = ifcopenshell.open(os.path.join(FIXTURES, "pass-description_unset.ifc"))
        specs.validate(ifc)
        spec = specs.specifications[0]
        assert spec.status is True
        assert spec.requirements[0].status is True

    def test_empty_string_description_fails_the_prohibition(self):
        specs = ids.open(SPEC)
        ifc = ifcopenshell.open(os.path.join(FIXTURES, "fail-description_empty_string.ifc"))
        specs.validate(ifc)
        spec = specs.specifications[0]
        assert spec.status is False
        assert spec.requirements[0].status is False
