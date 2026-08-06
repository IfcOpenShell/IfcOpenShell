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

"""End-to-end regression tests for specific reported defects.

Each test here loads a minimal .ids/.ifc pair from test/fixtures/ through
the same entry points ifctester's own CLI uses (ids.open, ifcopenshell.open,
Ids.validate), rather than exercising a facet's __call__ directly.
"""

import os

import ifcopenshell

from ifctester import ids

FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")


class TestClassificationSystemValuePairingFixture:
    def test_system_and_value_must_match_on_the_same_reference(self):
        # The wall has two classification references: SystemA/WRONG and
        # SystemB/ExpectedValue. The requirement asks for SystemA with
        # value ExpectedValue. Neither single reference satisfies both, so
        # the specification must fail, even though "SystemA" appears
        # somewhere on the wall and "ExpectedValue" appears somewhere else
        # on the wall.
        specs = ids.open(
            os.path.join(
                FIXTURES,
                "classification_system_value_pairing",
                "classification_system_value_pairing.ids",
            )
        )
        ifc = ifcopenshell.open(
            os.path.join(
                FIXTURES,
                "classification_system_value_pairing",
                "classification_system_value_pairing.ifc",
            )
        )
        specs.validate(ifc)
        spec = specs.specifications[0]
        assert spec.status is False
        assert spec.requirements[0].status is False
