import pathlib
from typing import List, Sequence, Tuple

import ifcopenshell
import pytest


def _bbox_from_vertices(verts: List[Tuple[float, float, float]]):
    if not verts:
        return (0, 0, 0), (0, 0, 0)
    xs = [v[0] for v in verts]
    ys = [v[1] for v in verts]
    zs = [v[2] for v in verts]
    mn = (min(xs), min(ys), min(zs))
    mx = (max(xs), max(ys), max(zs))
    return mn, mx


def _size_from_bbox(mn, mx):
    return (mx[0] - mn[0], mx[1] - mn[1], mx[2] - mn[2])


def _triples(flat: Sequence[float]) -> List[Tuple[float, float, float]]:
    return [(float(flat[i]), float(flat[i + 1]), float(flat[i + 2])) for i in range(0, len(flat), 3)]

def load_ifc_mesh_bbox(ifc_path: str):
    """Load first product's mesh from IFC using ifcopenshell.geom and return bbox and size."""
    try:
        import ifcopenshell.geom as geom
    except Exception as e:
        raise RuntimeError("ifcopenshell.geom not available: cannot validate IFC geometry") from e

    settings = geom.settings()
    settings.set(settings.USE_WORLD_COORDS, True)

    f = ifcopenshell.open(ifc_path)
    # Prefer the proxy we created, otherwise take any product with representation
    products = f.by_type("IfcProduct")
    target = None
    for p in products:
        if p.is_a("IfcBuildingElementProxy") and getattr(p, "Representation", None):
            target = p
            break
    if target is None:
        for p in products:
            if getattr(p, "Representation", None):
                target = p
                break
    if target is None:
        raise RuntimeError("No representable product found in IFC for validation")

    shape = geom.create_shape(settings, target)
    verts = _triples(shape.geometry.verts)
    mn, mx = _bbox_from_vertices(verts)
    return mn, mx, _size_from_bbox(mn, mx)

@pytest.fixture
def test_dir():
    return pathlib.Path(__file__).parent.resolve().absolute()
def test_simple_sweep_1(test_dir):
    ifc_mn, ifc_mx, ifc_sz = load_ifc_mesh_bbox(test_dir / "input_temp/simple_sweep_1.ifc")
    assert ifc_sz == pytest.approx((1.1, 0.1, 0.89578254))