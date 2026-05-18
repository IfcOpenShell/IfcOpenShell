import csv

import pytest

import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.util.shape

from pathlib import Path

repo_root = Path(__file__).resolve().parent.parent.parent.parent
test_files = repo_root / 'test' / 'input' / 'tests'

settings = ifcopenshell.geom.settings()

testdata = list(csv.reader((test_files / 'data.csv').open(newline='')))[1:]

print(testdata)

@pytest.mark.parametrize("fn,area,volume", testdata)
def test_conversion(fn, area, volume):
    f = ifcopenshell.open(test_files / fn)
    elem = next(inst for inst in f.by_type('IfcElement') if not inst.is_a('IfcOpeningElement'))
    for kernel in ('manifold', 'opencascade', 'cgal'):
        shp = ifcopenshell.geom.create_shape(settings, elem, geometry_library=kernel)
        if area:
            assert pytest.approx(float(area), rel=0.05) == ifcopenshell.util.shape.get_area(shp.geometry)
        if volume:
            assert pytest.approx(float(volume), rel=0.02) == ifcopenshell.util.shape.get_volume(shp.geometry)
