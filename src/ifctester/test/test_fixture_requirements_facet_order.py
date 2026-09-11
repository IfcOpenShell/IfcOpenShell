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

"""End-to-end regression test for buildingSMART/IDS#344.

Schema/ids.xsd's requirementsType wraps its facet elements in an
<xs:sequence maxOccurs="unbounded">. Because the wrapping sequence itself
repeats, a requirements clause can list its facets in any order (or even
interleave repeats of the same facet type) and still validate against the
XSD, even though a plain xs:sequence exists specifically "to produce the
text version of the content in a reliable and consistent way"
(CBenghi, buildingSMART/IDS#175).

Specification.asdict() already canonicalises facet order for round-tripped
output (see the "Canonicalise ordering as per XSD requirements" comment),
but Specification.parse_clause() built self.requirements in raw document
order, so a report generated straight from a parsed .ids file still varied
with how the author happened to order the file, defeating that canonical
ordering elsewhere in the same module.

Loads a minimal .ids/.ifc pair from test/fixtures/ through the same entry
points ifctester's own CLI uses (ids.open, ifcopenshell.open,
Ids.validate), rather than exercising a facet's __call__ directly.
"""

import os

import ifcopenshell

from ifctester import ids

FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")


class TestRequirementsFacetOrderFixture:
    def test_requirements_are_reported_in_canonical_facet_order(self):
        # The .ids file writes <property> before <attribute>, which the XSD
        # permits (buildingSMART/IDS#344) but which is not the canonical
        # entity/partOf/classification/attribute/property/material order.
        specs = ids.open(os.path.join(FIXTURES, "requirements_facet_order", "requirements_facet_order.ids"))
        ifc = ifcopenshell.open(os.path.join(FIXTURES, "requirements_facet_order", "requirements_facet_order.ifc"))
        specs.validate(ifc)
        spec = specs.specifications[0]

        assert spec.status is True

        facet_order = [type(facet).__name__ for facet in spec.requirements]
        assert facet_order == ["Attribute", "Property"], (
            f"requirements were reported in file order {facet_order} instead of "
            "canonical XSD order ['Attribute', 'Property']"
        )
