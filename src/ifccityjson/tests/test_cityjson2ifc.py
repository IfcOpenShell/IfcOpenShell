# This file was generated with the assistance of an AI coding tool.

import json

import ifcopenshell
import pytest
from cjio import cityjson
from ifccityjson.cityjson2ifc import Cityjson2ifc

SCALE = [0.001, 0.001, 0.001]
TRANSLATE = [100.0, 200.0, 5.0]


def make_cityjson(tmp_path, with_transform=True, epsg=None):
    data = {
        "type": "CityJSON",
        "version": "1.0",
        "CityObjects": {
            "obj": {
                "type": "CityFurniture",
                "geometry": [
                    {
                        "type": "MultiSurface",
                        "lod": "1",
                        "boundaries": [[[0, 1, 2, 3]]],
                    }
                ],
            }
        },
        "vertices": [[0, 0, 0], [2000, 0, 0], [2000, 3000, 0], [0, 3000, 0]],
    }
    if with_transform:
        data["transform"] = {"scale": SCALE, "translate": TRANSLATE}
    if epsg:
        data["metadata"] = {"referenceSystem": f"http://www.opengis.net/def/crs/EPSG/0/{epsg}"}
    path = tmp_path / "in.json"
    path.write_text(json.dumps(data))
    return path


def convert(tmp_path, cityjson_path):
    output = tmp_path / "out.ifc"
    converter = Cityjson2ifc()
    converter.configuration(file_destination=str(output), split=False)
    converter.convert(cityjson.load(str(cityjson_path), transform=False))
    return ifcopenshell.open(str(output))


class TestCityjson2ifcTransform:
    def test_vertex_coordinates_are_scaled(self, tmp_path):
        model = convert(tmp_path, make_cityjson(tmp_path))
        coordinates = [c for p in model.by_type("IfcCartesianPoint") for c in p.Coordinates]
        assert max(coordinates) == pytest.approx(3.0)

    def test_epsg_without_transform_does_not_crash(self, tmp_path):
        model = convert(tmp_path, make_cityjson(tmp_path, with_transform=False, epsg=7415))
        conversion = model.by_type("IfcMapConversion")[0]
        assert (conversion.Eastings, conversion.Northings, conversion.OrthogonalHeight) == (0.0, 0.0, 0.0)

    def test_epsg_with_transform_sets_map_conversion_translation(self, tmp_path):
        model = convert(tmp_path, make_cityjson(tmp_path, epsg=7415))
        conversion = model.by_type("IfcMapConversion")[0]
        assert (conversion.Eastings, conversion.Northings, conversion.OrthogonalHeight) == tuple(TRANSLATE)
