# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2026 Bonsai contributors
#
# This file is part of Bonsai.
#
# Bonsai is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Bonsai is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Bonsai.  If not, see <http://www.gnu.org/licenses/>.


# This file was generated with the assistance of an AI coding tool.

import bonsai.core.tool
from bonsai.tool.resource import Resource as subject
from test.bim.bootstrap import NewFile


class TestImplementsTool(NewFile):
    def test_run(self):
        assert isinstance(subject(), bonsai.core.tool.Resource)


class TestGetAttributesForCostValue(NewFile):
    def test_fixed_uses_the_fixed_cost_value_field(self):
        subject.get_resource_props().fixed_cost_value = 12.5
        assert subject.get_attributes_for_cost_value("FIXED") == {"AppliedValue": 12.5}

    def test_sum_uses_the_wildcard_category(self):
        assert subject.get_attributes_for_cost_value("SUM") == {"Category": "*"}

    def test_category_uses_the_given_category(self):
        assert subject.get_attributes_for_cost_value("CATEGORY", "Labour") == {"Category": "Labour"}
