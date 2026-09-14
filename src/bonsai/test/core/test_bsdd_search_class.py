# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2026 Dion Moult <dion@thinkmoult.com>
#
# This file was generated with the assistance of an AI coding tool.
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

"""Regression test for #9034: bSDD KeyError: 'referenceCode'.

bonsai.tool.bsdd.Bsdd is a Blender-facing tool and normally requires bpy.
This test runs it against a stubbed bpy and a stubbed bonsai.tool package
(instead of the real Blender-dependent one) so that Bsdd.search_class's
response-parsing logic can be exercised with a canned bSDD payload, offline
and without a real Blender session. This mirrors the technique
bonsai/__init__.py already uses to support running test/core without bpy.
"""

import importlib.util
import sys
import types
from pathlib import Path

import pytest

BONSAI_SRC = Path(__file__).resolve().parents[2] / "bonsai"


class _FakeClassificationProps:
    classification_source = "BSDD"


class _FakeClassification:
    @classmethod
    def get_classification_props(cls):
        return _FakeClassificationProps()


class _FakeClassificationItem:
    def __init__(self):
        self.name = ""
        self.reference_code = ""
        self.uri = ""
        self.dictionary_name = ""
        self.dictionary_namespace_uri = ""


class _FakeCollection(list):
    def add(self):
        item = _FakeClassificationItem()
        self.append(item)
        return item


class _FakeDictionary:
    def __init__(self, uri, is_active=True):
        self.uri = uri
        self.is_active = is_active


class _FakeBsddProps:
    def __init__(self, dictionary_uri):
        self.dictionaries = [_FakeDictionary(dictionary_uri)]
        self.classifications = _FakeCollection()


class _FakeClient:
    def __init__(self, response):
        self.response = response

    def get_classes(self, **kwargs):
        return self.response


@pytest.fixture
def bsdd_tool(monkeypatch):
    """Loads the real bonsai/tool/bsdd.py with bpy and bonsai.tool stubbed out."""
    monkeypatch.setitem(sys.modules, "bpy", types.ModuleType("bpy"))

    fake_tool_pkg = types.ModuleType("bonsai.tool")
    fake_tool_pkg.Classification = _FakeClassification
    monkeypatch.setitem(sys.modules, "bonsai.tool", fake_tool_pkg)

    import bonsai

    monkeypatch.setattr(bonsai, "tool", fake_tool_pkg, raising=False)

    spec = importlib.util.spec_from_file_location("bonsai.tool.bsdd_under_test", BONSAI_SRC / "tool" / "bsdd.py")
    module = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, "bonsai.tool.bsdd_under_test", module)
    spec.loader.exec_module(module)
    return module.Bsdd


DICT_URI = "https://identifier.buildingsmart.org/uri/nl-sfb/nl-sfb/2005"


def _search(bsdd_tool, classes):
    props = _FakeBsddProps(DICT_URI)
    bsdd_tool.get_bsdd_props = classmethod(lambda cls: props)
    bsdd_tool.client = _FakeClient({"name": "NL-SfB", "uri": DICT_URI, "classes": classes})
    bsdd_tool.search_class("grond", None, should_paginate=False)
    return list(props.classifications)


@pytest.mark.bsdd
class TestSearchClass:
    def test_classes_without_reference_code_do_not_crash(self, bsdd_tool):
        classes = _search(
            bsdd_tool,
            [
                {"name": "(11) Grond", "referenceCode": "11", "uri": DICT_URI + "/class/11"},
                {"name": "Uncoded class", "uri": DICT_URI + "/class/uncoded"},
            ],
        )
        by_name = {c.name: c for c in classes}
        assert by_name["(11) Grond"].reference_code == "11"
        assert by_name["Uncoded class"].reference_code == ""
        # entries with a referenceCode still sort before those without one.
        assert [c.name for c in classes] == ["(11) Grond", "Uncoded class"]

    def test_classes_with_reference_code_sort_as_before(self, bsdd_tool):
        classes = _search(
            bsdd_tool,
            [
                {"name": "Beton", "referenceCode": "22", "uri": DICT_URI + "/class/22"},
                {"name": "Grond", "referenceCode": "11", "uri": DICT_URI + "/class/11"},
            ],
        )
        assert [c.reference_code for c in classes] == ["11", "22"]
        assert [c.name for c in classes] == ["Grond", "Beton"]
