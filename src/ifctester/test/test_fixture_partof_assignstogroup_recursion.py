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

"""End-to-end regression test for PartOf(relation="IFCRELASSIGNSTOGROUP") recursion.

Documentation/UserManual/partof-facet.md (buildingSMART/IDS, development
branch) states that once a `relation` is specified, "only the given type must
be evaluated (recursively)". `PartOf.__call__`'s IFCRELASSIGNSTOGROUP branch
only ever inspected the element's own, single, direct group and never walked
further up the group-of-groups chain, so a duct assigned to a zone which is
itself assigned to a system was not recognised as being part of that system.
"""

import os

import ifcopenshell

from ifctester import ids

FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")


class TestPartOfAssignsToGroupRecursionFixture:
    def test_a_group_assigned_to_another_group_is_followed_recursively(self):
        directory = os.path.join(FIXTURES, "partof_assignstogroup_recursion")
        specs = ids.open(os.path.join(directory, "partof_assignstogroup_recursion.ids"))
        ifc = ifcopenshell.open(os.path.join(directory, "partof_assignstogroup_recursion.ifc"))
        specs.validate(ifc)

        required, prohibited = specs.specifications

        # The duct is two IfcRelAssignsToGroup hops away from the system (via
        # an intermediate zone). It must still be recognised as part of it.
        assert required.status is True

        # Symmetrically, a prohibited check against the same relationship
        # must correctly fail, not silently pass because only the nearer,
        # non-matching zone was ever inspected.
        assert prohibited.status is False
