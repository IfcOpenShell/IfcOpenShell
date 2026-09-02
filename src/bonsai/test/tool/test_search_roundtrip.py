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

import pytest

import bonsai.tool as tool
import test.bim.bootstrap
from bonsai.tool.search import Search as subject


class TestFilterQueryRoundTrip(test.bim.bootstrap.NewFile):
    """Importing a filter query into the UI facets and exporting it again must not change it."""

    @pytest.mark.parametrize(
        "query,expected",
        [
            ('query:"Name"!=/Test/', 'query:"Name"!=/Test/'),
            ('query:"Name"=/Test/', 'query:"Name"=/Test/'),
            # Unquoted values are canonically re-quoted by wrap_value; the
            # operator and value must still survive unchanged.
            ('query:"class"=IfcWall', 'query:"class"="IfcWall"'),
            ("IfcWall, Name!=/Test/", "IfcWall, Name!=/Test/"),
        ],
    )
    def test_round_trip_preserves_the_query(self, query, expected):
        filter_groups = subject.get_filter_groups("search")
        subject.import_filter_query(query, filter_groups)
        assert subject.export_filter_query(filter_groups) == expected

    def test_query_facet_comparison_lands_in_the_comparison_property(self):
        filter_groups = subject.get_filter_groups("search")
        subject.import_filter_query('query:"Name"!=/Test/', filter_groups)
        ifc_filter = filter_groups[0].filters[0]
        assert ifc_filter.type == "query"
        assert ifc_filter.comparison == "!="
        assert ifc_filter.value == "/Test/"
