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


class TestMaterialExtendedPropertiesIfc2x3Fixture:
    def test_ifc2x3_material_property_is_checked_without_crashing(self):
        # IfcExtendedMaterialProperties (IFC2X3) has no Properties
        # attribute, only ExtendedProperties. A Property facet on an
        # IFC2X3 IfcMaterial used to raise AttributeError instead of
        # finding the property.
        specs = ids.open(
            os.path.join(
                FIXTURES,
                "material_extended_properties_ifc2x3",
                "material_extended_properties_ifc2x3.ids",
            )
        )
        ifc = ifcopenshell.open(
            os.path.join(
                FIXTURES,
                "material_extended_properties_ifc2x3",
                "material_extended_properties_ifc2x3.ifc",
            )
        )
        specs.validate(ifc)
        spec = specs.specifications[0]
        assert spec.status is True
        assert spec.requirements[0].status is True
