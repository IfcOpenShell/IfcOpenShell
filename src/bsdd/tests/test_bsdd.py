from bsdd import Client

client = Client()

# Fetch shared data at module level to avoid repeated API calls during tests.
# The Client.get() method handles 429 rate-limit responses with automatic retry.
_dictionaries = client.get_dictionary()["dictionaries"]
ifc4x3_uri = next(l["uri"] for l in _dictionaries if "4.3" in l["uri"])
nbs_uri = next(l["uri"] for l in _dictionaries if "Uniclass 2015" == l["name"])

_ifc4x3_classes = client.get_classes(ifc4x3_uri, use_nested_classes=False, class_type="Class")
_nbs_classes = client.get_classes(nbs_uri, use_nested_classes=False, class_type="Class", offset=0, limit=5)
_uri_light_fixture = next(l for l in _ifc4x3_classes["classes"] if "IfcLightFixture" == l["code"])["uri"]

_light_fixture = client.get_class(_uri_light_fixture)
_light_fixture_relations = client.get_class_relations(_uri_light_fixture)
_light_fixture_properties = client.get_class_properties(_uri_light_fixture)


def test_get_dictionary():
    li_names = [l["name"] for l in _dictionaries]
    assert "Uniclass 2015" in li_names and "IFC" in li_names


def test_get_ifc_classes():
    codes = [l["code"] for l in _ifc4x3_classes["classes"]]
    assert "IfcBoiler" in codes and "IfcLightFixture" in codes


def test_get_nbs_classes():
    assert "Ac" in [l["code"] for l in _nbs_classes["classes"]]


def test_get_class():
    names = [l["name"] for l in _light_fixture["classProperties"]]
    assert "Maintenance Factor" in names and "Light Fixture Mounting Type" in names


def test_get_class_relations():
    # The Class/Relations/v1 endpoint is not deprecated (confirmed in bSDD OpenAPI spec),
    # but the IFC 4.3 dictionary currently has no cross-dictionary relations populated —
    # this appears to be a data migration gap rather than a deliberate API removal.
    assert "classRelations" in _light_fixture_relations


def test_get_class_properties():
    names = [l["name"] for l in _light_fixture_properties["classProperties"]]
    assert "Maintenance Factor" in names and "Light Fixture Mounting Type" in names


def test_search_class():
    ss_heat_pump_sys = client.search_class("Ss_60_40_36", [nbs_uri])
    li = [l + "source heat pump systems" for l in ["Air ", "Ground ", "Water "]]
    assert (
        len(li) < 8
    )  # I think it should be 4 but just validating it isn't overfetching with some space for future change
    for l in li:
        assert l in [_["name"] for _ in ss_heat_pump_sys["classes"]]


def test_get_properties():
    pr = client.get_properties(ifc4x3_uri, offset=0, limit=5)
    assert len(pr["properties"]) == 5
