"""Live tests for bsdd.Client against the real bSDD API.

These hit the network and are opt-in only: every test in this module carries
the `network` marker, which is deselected by default (see pyproject.toml).
Run explicitly with:

    python -m pytest tests/test_bsdd_live.py -m network

All fetches happen lazily inside fixtures, not at module import time, so this
file can still be collected without network access; only running a test in
it requires the network.
"""

import pytest

from bsdd import Client

pytestmark = pytest.mark.network


@pytest.fixture(scope="module")
def client():
    return Client()


@pytest.fixture(scope="module")
def dictionaries(client):
    return client.get_dictionary()["dictionaries"]


@pytest.fixture(scope="module")
def ifc4x3_uri(dictionaries):
    return next(l["uri"] for l in dictionaries if "4.3" in l["uri"])


@pytest.fixture(scope="module")
def nbs_uri(dictionaries):
    return next(l["uri"] for l in dictionaries if "Uniclass 2015" == l["name"])


@pytest.fixture(scope="module")
def ifc4x3_classes(client, ifc4x3_uri):
    return client.get_classes(ifc4x3_uri, use_nested_classes=False, class_type="Class")


@pytest.fixture(scope="module")
def nbs_classes(client, nbs_uri):
    return client.get_classes(nbs_uri, use_nested_classes=False, class_type="Class", offset=0, limit=5)


@pytest.fixture(scope="module")
def light_fixture_uri(ifc4x3_classes):
    return next(l for l in ifc4x3_classes["classes"] if "IfcLightFixture" == l["code"])["uri"]


def test_get_dictionary(dictionaries):
    li_names = [l["name"] for l in dictionaries]
    assert "Uniclass 2015" in li_names
    assert "IFC" in li_names


def test_get_ifc_classes(ifc4x3_classes):
    codes = [l["code"] for l in ifc4x3_classes["classes"]]
    assert "IfcBoiler" in codes
    assert "IfcLightFixture" in codes


def test_get_nbs_classes(nbs_classes):
    assert "Ac" in [l["code"] for l in nbs_classes["classes"]]


def test_get_class(client, light_fixture_uri):
    # TODO: fix deprecation warning.
    ifc4x3_light_fixture = client.get_class(light_fixture_uri)
    names = [l["name"] for l in ifc4x3_light_fixture["classProperties"]]
    assert "Maintenance Factor" in names
    assert "Light Fixture Mounting Type" in names


def test_get_class_relations(client, light_fixture_uri):
    ifc4x3_light_fixture_relations = client.get_class_relations(light_fixture_uri, True)
    names = [r["className"] for r in ifc4x3_light_fixture_relations["classRelations"]]
    assert "Electrical unit for light-line system" in names
    assert "Tubelight system" in names


def test_get_class_properties(client, light_fixture_uri):
    ifc4x3_light_fixture_properties = client.get_class_properties(light_fixture_uri)
    names = [l["name"] for l in ifc4x3_light_fixture_properties["classProperties"]]
    assert "Maintenance Factor" in names
    assert "Light Fixture Mounting Type" in names


def test_search_class(client, nbs_uri):
    ss_heat_pump_sys = client.search_class("Ss_60_40_36", [nbs_uri])
    li = [l + "source heat pump systems" for l in ["Air ", "Ground ", "Water "]]
    assert (
        len(li) < 8
    )  # I think it should be 4 but just validating it isn't overfetching with some space for future change
    for l in li:
        assert l in [_["name"] for _ in ss_heat_pump_sys["classes"]]


def test_get_properties(client, ifc4x3_uri):
    pr = client.get_properties(ifc4x3_uri, offset=0, limit=5)
    assert len(pr["properties"]) == 5
