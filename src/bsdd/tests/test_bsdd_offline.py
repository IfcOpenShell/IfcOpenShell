# bSDD - Python bSDD library
# Copyright (C) 2026 IfcOpenShell contributors
#
# This file is part of bSDD.
#
# bSDD is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# bSDD is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with bSDD.  If not, see <http://www.gnu.org/licenses/>.

"""Offline tests for request-parameter construction. These never touch the network:
Client.get() is monkeypatched to capture what would have been sent instead of making
an HTTP call."""

from bsdd import Client


def _client_with_captured_get(monkeypatch):
    captured = {}

    def fake_get(self, endpoint, params=None, is_auth_required=False):
        captured["endpoint"] = endpoint
        captured["params"] = params
        return {}

    monkeypatch.setattr(Client, "get", fake_get)
    return Client(), captured


def test_get_classes_sends_use_nested_classes_false(monkeypatch):
    # Regression test: get_classes() used to build its request params with a blanket
    # `if value:` filter, which is falsy for `use_nested_classes=False`. Explicitly
    # asking for a flat (non-nested) class list therefore silently dropped
    # `UseNestedClasses` from the request, so the server would fall back to its
    # nested-tree default instead of honouring the caller's choice.
    client, captured = _client_with_captured_get(monkeypatch)

    client.get_classes(
        "https://identifier.buildingsmart.org/uri/buildingsmart/ifc-4.3/class/IfcWall",
        use_nested_classes=False,
        search_text="Wall",
    )

    assert captured["params"]["UseNestedClasses"] is False
    assert captured["params"]["SearchText"] == "Wall"


def test_get_classes_sends_zero_offset(monkeypatch):
    # offset=0 is a meaningful, explicit "start from the first result", not "unset".
    client, captured = _client_with_captured_get(monkeypatch)

    client.get_classes("uri-x", offset=0, limit=50)

    assert captured["params"]["offset"] == 0
    assert captured["params"]["limit"] == 50


def test_get_classes_default_is_nested(monkeypatch):
    client, captured = _client_with_captured_get(monkeypatch)

    client.get_classes("uri-x")

    assert captured["params"]["UseNestedClasses"] is True
    assert captured["params"]["ClassType"] == "Class"
    assert "SearchText" not in captured["params"]


def test_get_classes_empty_class_type_is_still_omitted(monkeypatch):
    # class_type="" (used by search_in_dictionary's Dictionary/Classes fallback) means
    # "no ClassType filter" and must stay omitted, unlike UseNestedClasses/offset/limit.
    client, captured = _client_with_captured_get(monkeypatch)

    client.get_classes("uri-x", use_nested_classes=False, class_type="", related_ifc_entity="IfcWall")

    assert "ClassType" not in captured["params"]
    assert captured["params"]["RelatedIfcEntity"] == "IfcWall"
    assert captured["params"]["UseNestedClasses"] is False
