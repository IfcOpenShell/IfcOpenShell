# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2026
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
from bonsai.tool.bsdd import Bsdd as subject
from test.bim.bootstrap import NewFile


class TestSearchClass(NewFile):
    def test_classes_missing_reference_code_do_not_crash_the_search(self):
        # Regression test for #9034: the bSDD API marks `referenceCode` (and
        # `name`, `uri`) as optional on a class, so a bare subscript on any
        # of them raised KeyError for dictionaries (e.g. NL-SfB) that return
        # such a class.
        class FakeClient:
            def get_classes(self, **kwargs):
                return {
                    "name": "NL-SfB",
                    "uri": "https://example.org/dictionary/nl-sfb",
                    "classes": [
                        {"name": "No Reference Code", "uri": "https://example.org/class/1"},
                        {"name": "Kolom", "referenceCode": "17", "uri": "https://example.org/class/2"},
                        {"name": "Fundering", "referenceCode": "16", "uri": "https://example.org/class/3"},
                    ],
                }

        original_client = subject.client
        original_get_classification_props = tool.Classification.get_classification_props

        class FakeClassificationProps:
            classification_source = "https://example.org/dictionary/nl-sfb"

        subject.client = FakeClient()
        tool.Classification.get_classification_props = classmethod(lambda cls: FakeClassificationProps())
        try:
            total = subject.search_class("keyword", None)
        finally:
            subject.client = original_client
            tool.Classification.get_classification_props = original_get_classification_props

        props = subject.get_bsdd_props()
        assert total == 3
        # Classes with a reference code sort first (by code), the class
        # missing one is kept, sorted last, instead of being dropped.
        assert [c.name for c in props.classifications] == ["Fundering", "Kolom", "No Reference Code"]
        assert [c.reference_code for c in props.classifications] == ["16", "17", ""]
