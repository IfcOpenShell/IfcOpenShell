import pathlib
from collections.abc import Sequence

import ifcopenshell
import pytest
from OCC.Core.TopoDS import TopoDS_Shape, TopoDS_Compound


def _bbox_from_vertices(verts: list[tuple[float, float, float]]):
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


def _triples(flat: Sequence[float]) -> list[tuple[float, float, float]]:
    return [(float(flat[i]), float(flat[i + 1]), float(flat[i + 2])) for i in range(0, len(flat), 3)]


def load_ifc_occ_shape(ifc_path: str, verbose=False) -> TopoDS_Shape:
    try:
        import ifcopenshell.geom as geom
    except Exception as e:
        raise RuntimeError("ifcopenshell.geom not available: cannot validate IFC geometry") from e

    settings = geom.settings()
    settings.set(settings.USE_WORLD_COORDS, True)
    settings.set("use-python-opencascade", True)

    # Open the IFC file
    f = ifcopenshell.open(ifc_path)

    # Find the first representable product (prefer IfcBuildingElementProxy, then any product with representation)
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
        raise RuntimeError("No representable product found in IFC for shape extraction")

    # Create the shape using ifcopenshell.geom with opencascade geometry library
    shape_result = geom.create_shape(settings, target, geometry_library="opencascade")

    # Extract the OpenCASCADE TopoDS_Shape from the result
    # The create_shape function returns an object with an occ_shape attribute when using opencascade
    if hasattr(shape_result, "geometry") and shape_result.geometry:
        occ_shape = shape_result.geometry
        if isinstance(occ_shape, TopoDS_Compound):
            json_data = occ_shape.DumpJson()
            if verbose:
                print(json_data)
        else:
            raise NotImplemented(f"Unsupported shape type: {type(occ_shape)}")

        return occ_shape
    else:
        raise RuntimeError("Failed to extract OpenCASCADE shape from IFC geometry")


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
def geom_dir():
    return pathlib.Path(__file__).parent.parent.resolve().absolute() / "fixtures/geom"


def test_simple_sweep_1(geom_dir):
    ifc_file_path = geom_dir / "simple_sweep_1.ifc"
    ifc_mn, ifc_mx, ifc_sz = load_ifc_mesh_bbox(ifc_file_path)
    occ_shape = load_ifc_occ_shape(ifc_file_path)
    assert occ_shape is not None
    assert ifc_sz == pytest.approx((0.8957825463853046, 0.1, 1.1))
    assert ifc_mn == pytest.approx((0.0, 0, -0.1))
    assert ifc_mx == pytest.approx((0.8957825463853046, 0.1, 1.0))


def test_simple_sweep_2(geom_dir):
    ifc_file_path = geom_dir / "simple_sweep_2.ifc"
    ifc_mn, ifc_mx, ifc_sz = load_ifc_mesh_bbox(ifc_file_path)
    occ_shape = load_ifc_occ_shape(ifc_file_path)
    assert occ_shape is not None
    assert ifc_mn == pytest.approx((50.0, 100.0, 200.0))
    assert ifc_mx == pytest.approx((50.89584911299009, 101.70000025609394, 202.0000003710634))
    assert ifc_sz == pytest.approx((0.8958491129900921, 1.7000002560939436, 2.0000003710634076))


def test_pipe_12d(geom_dir):
    ifc_file_path = geom_dir / "pipe.ifc"
    ifc_mn, ifc_mx, ifc_sz = load_ifc_mesh_bbox(ifc_file_path)
    occ_shape = load_ifc_occ_shape(ifc_file_path)
    assert occ_shape is not None
    assert ifc_sz == pytest.approx((1.205888147422229, 0.9929900508137735, 0.35776115971654576))
    assert ifc_mn == pytest.approx((288.9774190979147, 582.0537006391681, 118.70711942014172))
    assert ifc_mx == pytest.approx((290.18330724533695, 583.0466906899819, 119.06488057985827))
