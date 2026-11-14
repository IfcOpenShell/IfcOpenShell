# This file was generated with the assistance of an AI coding tool.

import json

import ifcopenshell
import pytest
from cjio import cityjson
from ifccityjson.cityjson2ifc import Cityjson2ifc


def make_cityjson(tmp_path, lod):
    data = {
        "type": "CityJSON",
        "version": "1.0",
        "CityObjects": {
            "obj": {
                "type": "CityFurniture",
                "geometry": [{"type": "MultiSurface", "lod": lod, "boundaries": [[[0, 1, 2, 3]]]}],
            }
        },
        "vertices": [[0, 0, 0], [2, 0, 0], [2, 3, 0], [0, 3, 0]],
    }
    path = tmp_path / "in.json"
    path.write_text(json.dumps(data))
    return path


def convert(tmp_path, lod, **configuration):
    output = tmp_path / "out.ifc"
    converter = Cityjson2ifc()
    converter.configuration(file_destination=str(output), **configuration)
    converter.convert(cityjson.load(str(make_cityjson(tmp_path, lod)), transform=False))
    return output


def target_views(path):
    model = ifcopenshell.open(str(path))
    return [c.UserDefinedTargetView for c in model.by_type("IfcGeometricRepresentationSubContext")]


class TestCityjson2ifcLod:
    @pytest.mark.parametrize("lod", ["1", 1])
    def test_string_and_numeric_lod_give_the_same_target_view(self, tmp_path, lod):
        output = convert(tmp_path, lod, split=False)
        assert target_views(output) == ["LOD1"]

    def test_numeric_lod_with_split_writes_a_file_per_lod(self, tmp_path):
        convert(tmp_path, 1, split=True)
        assert target_views(tmp_path / "out1.ifc") == ["LOD1"]
