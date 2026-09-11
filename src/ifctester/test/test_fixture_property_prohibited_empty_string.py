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

buildingSMART/IDS property-facet.md states, for a PROHIBITED property
requirement with no value given, that the property "must not exist ...
even if empty." A property explicitly set to an empty string is still
populated in the STEP file (as opposed to the baseName being absent from
the pset entirely), so it must fail the prohibition, not pass it silently.

This mirrors the sibling defect fixed for Attribute.__call__: the same
existence-before-emptiness ordering is applied here for Property.__call__,
without touching how REQUIRED and OPTIONAL treat an empty value (they
intentionally treat it as not populated, unlike PROHIBITED).
"""

import os

import ifcopenshell

from ifctester import ids
from ifctester.facet import Property

FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures", "property_prohibited_empty_string")
SPEC = os.path.join(FIXTURES, "property_prohibited_empty_string.ids")


class TestPropertyProhibitedEmptyStringFixture:
    def test_absent_foo_property_passes_the_prohibition(self):
        specs = ids.open(SPEC)
        ifc = ifcopenshell.open(os.path.join(FIXTURES, "pass-foo_absent.ifc"))
        specs.validate(ifc)
        spec = specs.specifications[0]
        assert spec.status is True
        assert spec.requirements[0].status is True

    def test_empty_string_foo_property_fails_the_prohibition(self):
        specs = ids.open(SPEC)
        ifc = ifcopenshell.open(os.path.join(FIXTURES, "fail-foo_empty_string.ifc"))
        specs.validate(ifc)
        spec = specs.specifications[0]
        assert spec.status is False
        assert spec.requirements[0].status is False

    def test_required_cardinality_still_treats_empty_string_as_no_value(self):
        # REQUIRED and OPTIONAL legitimately treat an empty value as not
        # populated, unlike PROHIBITED. This must stay unchanged.
        ifc = ifcopenshell.open(os.path.join(FIXTURES, "fail-foo_empty_string.ifc"))
        wall = ifc.by_type("IfcWall")[0]

        required_facet = Property(propertySet="Foo_Bar", baseName="Foo", cardinality="required")
        result = required_facet(wall)
        assert result.is_pass is False

    def test_optional_cardinality_still_passes_regardless_of_emptiness(self):
        ifc = ifcopenshell.open(os.path.join(FIXTURES, "fail-foo_empty_string.ifc"))
        wall = ifc.by_type("IfcWall")[0]

        optional_facet = Property(propertySet="Foo_Bar", baseName="Foo", cardinality="optional")
        result = optional_facet(wall)
        assert result.is_pass is True

        ifc_absent = ifcopenshell.open(os.path.join(FIXTURES, "pass-foo_absent.ifc"))
        wall_absent = ifc_absent.by_type("IfcWall")[0]
        result_absent = optional_facet(wall_absent)
        assert result_absent.is_pass is True
