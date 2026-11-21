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

import bpy

from bonsai.tool.search import Search as subject
from test.bim.bootstrap import NewFile


def filter_groups():
    return bpy.context.scene.BIMSearchProperties.filter_groups


def facets(groups):
    """Flatten to (enabled, type, value) so the tests read as one line per facet."""
    return [[(f.enabled, f.type, f.value) for f in group.filters] for group in groups]


class TestCommentedOutFacets(NewFile):
    def test_a_commented_out_group_is_imported_as_a_disabled_facet(self):
        groups = filter_groups()
        subject.import_filter_query("IfcWall + /* IfcSlab */", groups)
        assert facets(groups) == [[(True, "entity", "IfcWall")], [(False, "entity", "IfcSlab")]]

    def test_a_disabled_facet_is_exported_as_a_comment(self):
        groups = filter_groups()
        subject.import_filter_query("IfcWall + IfcSlab", groups)
        groups[1].filters[0].enabled = False
        assert subject.export_filter_query(groups) == "IfcWall /* + IfcSlab */"

    def test_a_comment_survives_a_round_trip(self):
        for query in (
            "IfcWall /* + IfcSlab */",
            'IfcWall /*, Name="Foo" */, IfcSlab',
            '/* Name="Foo", */ IfcWall',
            "IfcWall + /* IfcSlab + */ IfcBeam",
            'IfcWall + /* Name="Foo", IfcSlab + */ IfcBeam',
            "/* IfcWall + */ /* IfcSlab + */ IfcBeam",
        ):
            groups = filter_groups()
            subject.import_filter_query(query, groups)
            imported = facets(groups)
            assert subject.export_filter_query(groups) == query
            # And importing what we just exported must land on the same facets again.
            subject.import_filter_query(query, groups)
            assert facets(groups) == imported

    def test_a_comment_may_span_multiple_lines(self):
        groups = filter_groups()
        subject.import_filter_query("IfcWall +\n/* IfcSlab\n*/", groups)
        assert facets(groups) == [[(True, "entity", "IfcWall")], [(False, "entity", "IfcSlab")]]

    def test_a_comment_inside_a_quoted_string_is_not_a_comment(self):
        groups = filter_groups()
        subject.import_filter_query('Name="/* not a comment */"', groups)
        assert facets(groups) == [[(True, "attribute", "/* not a comment */")]]
        assert subject.export_filter_query(groups) == 'Name="/* not a comment */"'

    def test_a_comment_that_is_not_a_facet_is_dropped(self):
        groups = filter_groups()
        subject.import_filter_query("/* level 2 rooms */ IfcSpace", groups)
        assert facets(groups) == [[(True, "entity", "IfcSpace")]]
        assert subject.export_filter_query(groups) == "IfcSpace"

    def test_a_query_with_nothing_enabled_is_empty(self):
        # A comment only query doesn't parse, and an empty query already means "no
        # filter", so the comments are dropped. The facets themselves are still kept.
        groups = filter_groups()
        subject.import_filter_query("/* IfcWall */", groups)
        assert facets(groups) == [[(False, "entity", "IfcWall")]]
        assert subject.export_filter_query(groups) == ""
