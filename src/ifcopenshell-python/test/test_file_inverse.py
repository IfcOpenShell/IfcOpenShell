import gc
import sys
import pytest
import pprint
import weakref
import itertools
import ifcopenshell
import ifcopenshell.api


def test_inverse_indices():
    f =  ifcopenshell.file()

    p0 = f.createIfcCartesianPoint((0.,0.,0.))
    p1 = f.createIfcCartesianPoint((1.,0.,0.))
    p2 = f.createIfcCartesianPoint((1.,1.,0.))

    poly = f.createIfcPolyline((p0, p1, p2, p0))
    place = f.createIfcAxis2Placement3D(p0)

    pairs = f.get_inverse(p0, allow_duplicate=True, with_attribute_indices=True)

    for inst, idx in pairs:
        v = inst[idx]
        if type(v) == tuple:
            # @nb this doesn't account for nested lists
            v = list(v)
            i = v.index(p0)
            v[i:i+1] = []
        else:
            v = p1
        inst[idx] = v

    # By now we expect to have removed *both* occurences of p0 from the
    # polyline points and have overwritten the placement location.

    assert poly.Points == (p1, p2)
    assert place.Location == p1


if __name__ == "__main__":
    pytest.main(["-sx", __file__])
