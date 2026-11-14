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

"""End-to-end regression test for a specific reported defect (#7855, #7856).

Entity.__call__ compared self.predefinedType == "USERDEFINED" first. For a
restriction enumeration that includes "USERDEFINED" among its values (e.g.
SOLIDWALL, USERDEFINED), that comparison is truthy for the whole
restriction object, routing every element into the USERDEFINED-only branch
even when its actual predefined type (SOLIDWALL) was a listed, non-USERDEFINED
value. The requirement failed even though SOLIDWALL was explicitly allowed.
"""

import os

import ifcopenshell

from ifctester import ids

FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures", "predefinedtype_restriction_userdefined")
SPEC = os.path.join(FIXTURES, "predefinedtype_restriction_userdefined.ids")
MODEL = os.path.join(FIXTURES, "predefinedtype_restriction_userdefined.ifc")


class TestPredefinedTypeRestrictionUserdefinedFixture:
    def test_solidwall_matches_enumeration_that_also_lists_userdefined(self):
        specs = ids.open(SPEC)
        ifc = ifcopenshell.open(MODEL)
        specs.validate(ifc)
        spec = specs.specifications[0]
        assert spec.requirements[0].status is True
        assert spec.status is True
