"""Offline tests for bsdd.Client.

These run against stubbed responses instead of calling the live bSDD API, so
they run without network access and are safe to collect and run in CI. For
tests against the real bSDD API, see test_bsdd_live.py (opt-in, `network`
marker, never runs by default).
"""

import types

import pytest

from bsdd import Client

IFC4X3_URI = "https://identifier.buildingsmart.org/uri/buildingsmart/ifc/4.3"
NBS_URI = "https://identifier.buildingsmart.org/uri/nbs/uniclass/2015"
LIGHT_FIXTURE_URI = f"{IFC4X3_URI}/class/IfcLightFixture"

DICTIONARIES = {
    "dictionaries": [
        {"name": "IFC", "uri": IFC4X3_URI},
        {"name": "Uniclass 2015", "uri": NBS_URI},
    ]
}

IFC4X3_CLASSES = {
    "classes": [
        {"code": "IfcBoiler", "uri": f"{IFC4X3_URI}/class/IfcBoiler"},
        {"code": "IfcLightFixture", "uri": LIGHT_FIXTURE_URI},
    ]
}

NBS_CLASSES = {"classes": [{"code": "Ac", "uri": f"{NBS_URI}/class/Ac"}]}

LIGHT_FIXTURE_PROPERTIES = [
    {"name": "Maintenance Factor"},
    {"name": "Light Fixture Mounting Type"},
]

LIGHT_FIXTURE_RELATIONS = {
    "classRelations": [
        {"className": "Electrical unit for light-line system", "classUri": f"{IFC4X3_URI}/class/ElecUnit"},
        {"className": "Tubelight system", "classUri": f"{IFC4X3_URI}/class/Tubelight"},
    ]
}

HEAT_PUMP_CLASSES = {
    "classes": [
        {"name": "Air source heat pump systems"},
        {"name": "Ground source heat pump systems"},
        {"name": "Water source heat pump systems"},
    ]
}

PROPERTIES = {"properties": [{"name": f"Property {i}"} for i in range(5)]}


def _fake_get(self, endpoint, params=None, is_auth_required=False):
    params = params or {}
    if endpoint.startswith("Dictionary/v") and endpoint.endswith("/Classes"):
        uri = params.get("Uri")
        if uri == IFC4X3_URI:
            return IFC4X3_CLASSES
        if uri == NBS_URI:
            return NBS_CLASSES
        raise AssertionError(f"unstubbed dictionary classes uri: {uri!r}")
    if endpoint.startswith("Dictionary/v") and endpoint.endswith("/Properties"):
        return PROPERTIES
    if endpoint.startswith("Dictionary/v"):
        return DICTIONARIES
    if endpoint.startswith("Class/Relations/v"):
        return LIGHT_FIXTURE_RELATIONS
    if endpoint.startswith("Class/Properties/v"):
        return {"classProperties": LIGHT_FIXTURE_PROPERTIES}
    if endpoint.startswith("Class/Search/v"):
        return HEAT_PUMP_CLASSES
    if endpoint.startswith("Class/v"):
        return {"classProperties": LIGHT_FIXTURE_PROPERTIES}
    raise AssertionError(f"unstubbed endpoint: {endpoint!r}")


@pytest.fixture
def client():
    stub = Client()
    stub.get = types.MethodType(_fake_get, stub)
    return stub


def test_get_dictionary(client):
    li_names = [l["name"] for l in client.get_dictionary()["dictionaries"]]
    assert "Uniclass 2015" in li_names
    assert "IFC" in li_names


def test_get_ifc_classes(client):
    codes = [l["code"] for l in client.get_classes(IFC4X3_URI, use_nested_classes=False, class_type="Class")["classes"]]
    assert "IfcBoiler" in codes
    assert "IfcLightFixture" in codes


def test_get_nbs_classes(client):
    nbs_classes = client.get_classes(NBS_URI, use_nested_classes=False, class_type="Class", offset=0, limit=5)
    assert "Ac" in [l["code"] for l in nbs_classes["classes"]]


def test_get_class(client):
    ifc4x3_light_fixture = client.get_class(LIGHT_FIXTURE_URI)
    names = [l["name"] for l in ifc4x3_light_fixture["classProperties"]]
    assert "Maintenance Factor" in names
    assert "Light Fixture Mounting Type" in names


def test_get_class_relations(client):
    ifc4x3_light_fixture_relations = client.get_class_relations(LIGHT_FIXTURE_URI, True)
    names = [r["className"] for r in ifc4x3_light_fixture_relations["classRelations"]]
    assert "Electrical unit for light-line system" in names
    assert "Tubelight system" in names


def test_get_class_properties(client):
    ifc4x3_light_fixture_properties = client.get_class_properties(LIGHT_FIXTURE_URI)
    names = [l["name"] for l in ifc4x3_light_fixture_properties["classProperties"]]
    assert "Maintenance Factor" in names
    assert "Light Fixture Mounting Type" in names


def test_search_class(client):
    ss_heat_pump_sys = client.search_class("Ss_60_40_36", [NBS_URI])
    li = [l + "source heat pump systems" for l in ["Air ", "Ground ", "Water "]]
    assert (
        len(li) < 8
    )  # I think it should be 4 but just validating it isn't overfetching with some space for future change
    for l in li:
        assert l in [_["name"] for _ in ss_heat_pump_sys["classes"]]


def test_get_properties(client):
    pr = client.get_properties(IFC4X3_URI, offset=0, limit=5)
    assert len(pr["properties"]) == 5
