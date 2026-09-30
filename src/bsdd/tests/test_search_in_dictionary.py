# This file was generated with the assistance of an AI coding tool.

from bsdd import Client


def test_search_in_dictionary_filters_classes_by_related_ifc_entity(monkeypatch):
    client = Client()
    calls = []

    def get_classes(**kwargs):
        calls.append(kwargs)
        return {
            "name": "Uniclass 2015",
            "uri": "https://example.org/dictionary",
            "classes": [{"code": "Ss_25_10"}],
            "classesTotalCount": 1,
            "classesOffset": 0,
            "classesCount": 1,
        }

    monkeypatch.setattr(client, "get_classes", get_classes)
    result = client.search_in_dictionary("https://example.org/dictionary", "wall", related_ifc_entity="IfcWall")
    assert calls[0]["related_ifc_entity"] == "IfcWall"
    assert result["dictionary"]["classes"] == [{"code": "Ss_25_10"}]
    assert result["totalCount"] == 1
    assert result["count"] == 1
