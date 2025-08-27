import pathlib
from typing import List, Sequence, Tuple

import ifcopenshell
import pytest
from OCC.Core.TopoDS import TopoDS_Shape, TopoDS_Compound


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


def _is_swept_shape(occ_shape: TopoDS_Shape) -> bool:
    """Analyze if the given OpenCASCADE shape represents a swept shape using topology exploration."""
    try:
        from OCC.Core.TopExp import TopExp_Explorer
        from OCC.Core.TopAbs import TopAbs_FACE, TopAbs_EDGE, TopAbs_WIRE
        from OCC.Core.BRep_Tool import BRep_Tool
        from OCC.Core.GeomLProp_SLProps import GeomLProp_SLProps
        from OCC.Core.BRepAdaptor_Surface import BRepAdaptor_Surface
        from OCC.Core.GeomAbs import (
            GeomAbs_Cylinder,
            GeomAbs_Plane,
            GeomAbs_SurfaceOfExtrusion,
            GeomAbs_SurfaceOfRevolution,
        )
        from OCC.Core.gp import gp_Vec
        import math
    except ImportError as e:
        raise RuntimeError("pythonocc-core not available for topology analysis") from e

    if occ_shape.IsNull():
        return False

    # Explore faces to look for swept surface characteristics
    face_explorer = TopExp_Explorer(occ_shape, TopAbs_FACE)
    swept_indicators = 0
    total_faces = 0

    while face_explorer.More():
        face = face_explorer.Current()
        total_faces += 1

        # Get the surface adaptor for this face
        surface_adaptor = BRepAdaptor_Surface(face)
        surface_type = surface_adaptor.GetType()

        # Check for surface types that indicate swept geometry
        if surface_type in [GeomAbs_Cylinder, GeomAbs_SurfaceOfExtrusion, GeomAbs_SurfaceOfRevolution]:
            swept_indicators += 1

        # For planar surfaces, check if they form a pattern consistent with swept geometry
        elif surface_type == GeomAbs_Plane:
            # Analyze if planar faces are arranged in a swept pattern
            # This is a simplified check - could be enhanced further
            if _has_parallel_opposite_faces(occ_shape, face):
                swept_indicators += 0.5  # Partial indicator

        face_explorer.Next()

    # Additional check: analyze edge patterns for swept characteristics
    edge_analysis = _analyze_edge_patterns(occ_shape)

    # Determine if this is likely a swept shape
    # If more than 50% of faces show swept characteristics, or we have strong edge patterns
    swept_ratio = swept_indicators / max(total_faces, 1)
    is_swept = swept_ratio > 0.5 or edge_analysis

    if is_swept:
        print(f"Swept shape analysis: {swept_indicators}/{total_faces} faces show swept characteristics")
        if edge_analysis:
            print("Edge pattern analysis also indicates swept geometry")

    return is_swept


def _has_parallel_opposite_faces(shape: TopoDS_Shape, reference_face) -> bool:
    """Check if the shape has faces parallel to the reference face (indicating extrusion)."""
    try:
        from OCC.Core.TopExp import TopExp_Explorer
        from OCC.Core.TopAbs import TopAbs_FACE
        from OCC.Core.BRepAdaptor_Surface import BRepAdaptor_Surface
        from OCC.Core.GeomAbs import GeomAbs_Plane
        from OCC.Core.gp import gp_Vec
        import math

        ref_adaptor = BRepAdaptor_Surface(reference_face)
        if ref_adaptor.GetType() != GeomAbs_Plane:
            return False

        ref_normal = ref_adaptor.Plane().Axis().Direction()

        face_explorer = TopExp_Explorer(shape, TopAbs_FACE)
        while face_explorer.More():
            face = face_explorer.Current()
            if not face.IsSame(reference_face):
                face_adaptor = BRepAdaptor_Surface(face)
                if face_adaptor.GetType() == GeomAbs_Plane:
                    face_normal = face_adaptor.Plane().Axis().Direction()
                    # Check if normals are parallel (dot product close to ±1)
                    dot_product = abs(ref_normal.Dot(face_normal))
                    if dot_product > 0.99:  # Very close to parallel
                        return True
            face_explorer.Next()
        return False
    except:
        return False


def load_ifc_occ_shape(ifc_path: str) -> TopoDS_Shape:
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
def test_dir():
    return pathlib.Path(__file__).parent.resolve().absolute()


def test_simple_sweep_1(test_dir):
    ifc_file_path = test_dir / "input_temp/simple_sweep_1.ifc"
    ifc_mn, ifc_mx, ifc_sz = load_ifc_mesh_bbox(ifc_file_path)
    occ_shape = load_ifc_occ_shape(ifc_file_path)
    assert occ_shape is not None
    assert ifc_sz == pytest.approx((1.1, 0.1, 0.89578254))
    assert ifc_mn == pytest.approx((-1.0, -1.3877787807814457e-17, 0.0))
    assert ifc_mx == pytest.approx((0.10000000000000002, 0.1, 0.8957825463853046))


def test_simple_sweep_2(test_dir):
    ifc_file_path = test_dir / "input_temp/simple_sweep_2.ifc"
    ifc_mn, ifc_mx, ifc_sz = load_ifc_mesh_bbox(ifc_file_path)
    occ_shape = load_ifc_occ_shape(ifc_file_path)
    assert occ_shape is not None
    assert ifc_sz == pytest.approx((1.800000679914902, 0.9243618756667757, 2.0958492522636902))
    assert ifc_mn == pytest.approx((-100.1, -50.0, 197.9041507477363))
    assert ifc_mx == pytest.approx((-98.29999932008509, -49.075638124333224, 200.0))


def test_pipe_12d(test_dir):
    ifc_file_path = test_dir / "input_temp/pipe.ifc"
    ifc_mn, ifc_mx, ifc_sz = load_ifc_mesh_bbox(ifc_file_path)
    occ_shape = load_ifc_occ_shape(ifc_file_path)
    assert occ_shape is not None
    assert ifc_sz == pytest.approx((1.1068712115520611, 6.2215114729478955, 0.35776115971654576))
    assert ifc_mn == pytest.approx((289080.64128449163, 5822851.344592881, 118.70711942014172))
    assert ifc_mx == pytest.approx((289081.7481557032, 5822857.566104354, 119.06488057985827))
