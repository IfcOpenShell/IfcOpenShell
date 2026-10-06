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

import os

import pytest

from ifctester import ids

FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures", "property_empty_basename")


class TestPropertyEmptyBasenameFixture:
    def test_an_empty_base_name_is_rejected_on_opening(self):
        with pytest.raises(ids.IdsEmptyParameterError, match="baseName"):
            ids.open(os.path.join(FIXTURES, "property_empty_basename.ids"))
