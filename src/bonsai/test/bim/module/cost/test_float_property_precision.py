# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2026 Dion Moult <dion@thinkmoult.com>
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

import bonsai.tool as tool
from test.bim.bootstrap import NewFile

VALUE = 1234567.891


class TestFloatPropertyPrecision(NewFile):
    def test_fixed_cost_value_keeps_double_precision(self):
        props = tool.Cost.get_cost_props()
        props.fixed_cost_value = VALUE
        assert props.fixed_cost_value == VALUE

    def test_quantity_produced_keeps_double_precision(self):
        props = tool.Resource.get_resource_props().productivity
        props.quantity_produced = VALUE
        assert props.quantity_produced == VALUE

    def test_resource_schedule_usage_keeps_double_precision(self):
        resource = tool.Resource.get_resource_props().resources.add()
        resource.schedule_usage = VALUE
        assert resource.schedule_usage == VALUE
