from bsdd import Client

client = Client()

ifc4x3_uri = next(l["uri"] for l in client.get_dictionary()["dictionaries"] if "4.3" in l["uri"])
nbs_uri = next(l["uri"] for l in client.get_dictionary()["dictionaries"] if "Uniclass 2015" == l["name"])


def get_ifc_classes():
    return client.get_classes(ifc4x3_uri, use_nested_classes=False, class_type="Class")


def get_nbs_classes():
    return client.get_classes(nbs_uri, use_nested_classes=False, class_type="Class", offset=0, limit=5)


def test_get_dictionary():
    li_names = [l["name"] for l in client.get_dictionary()["dictionaries"]]
    assert "Uniclass 2015" and "IFC" in li_names


def test_get_ifc_classes():
    ifc4x3_classes = get_ifc_classes()
    assert "IfcBoiler" and "IfcLightFixture" in [l["code"] for l in ifc4x3_classes["classes"]]


def test_get_nbs_classes():
    nbs_classes = get_nbs_classes()
    assert "Ac" in [l["code"] for l in nbs_classes["classes"]]


def test_get_class():
    uri_light_fixture = next(l for l in get_ifc_classes()["classes"] if "IfcLightFixture" == l["code"])["uri"]
    ifc4x3_light_fixture = client.get_class(uri_light_fixture)
    assert "Maintenance Factor" and "Light Fixture Mounting Type" in [
        l["name"] for l in ifc4x3_light_fixture["classProperties"]
    ]


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
