# This file was generated with the assistance of an AI coding tool.

import pytest

import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.util.shape


def build_brep_with_void(schema, ifc_class, voids_inwards=True):
    """Build boxes with either inward or outward cavity normals from issue #10249."""
    model = ifcopenshell.file(schema=schema)

    def point(coords):
        return model.createIfcCartesianPoint([float(c) for c in coords])

    def direction(coords):
        return model.createIfcDirection([float(c) for c in coords])

    def box(lower, upper, void=False):
        vertices = {}
        edges = {}

        def coordinates(index):
            return [lower if c == 0 else upper for c in index]

        def vertex(index):
            if index not in vertices:
                vertices[index] = model.createIfcVertexPoint(point(coordinates(index)))
            return vertices[index]

        def edge(start, end):
            if (start, end) in edges:
                return edges[start, end], True
            if (end, start) in edges:
                return edges[end, start], False
            line = model.createIfcLine(
                point(coordinates(start)),
                model.createIfcVector(direction([end[i] - start[i] for i in range(3)]), float(upper - lower)),
            )
            result = model.createIfcEdgeCurve(vertex(start), vertex(end), line, True)
            edges[start, end] = result
            return result, True

        planes = {
            (0, 0): ((lower, lower, lower), (1, 0, 0), (0, 1, 0)),
            (0, 1): ((upper, lower, lower), (1, 0, 0), (0, 1, 0)),
            (1, 0): ((lower, lower, lower), (0, 1, 0), (0, 0, 1)),
            (1, 1): ((lower, upper, lower), (0, 1, 0), (0, 0, 1)),
            (2, 0): ((lower, lower, lower), (0, 0, 1), (1, 0, 0)),
            (2, 1): ((lower, lower, upper), (0, 0, 1), (1, 0, 0)),
        }
        faces = []
        for axis in range(3):
            other_axes = [i for i in range(3) if i != axis]
            for side in (0, 1):
                corners = []
                for p, q in ((0, 0), (1, 0), (1, 1), (0, 1)):
                    index = [0, 0, 0]
                    index[axis] = side
                    index[other_axes[0]] = p
                    index[other_axes[1]] = q
                    corners.append(tuple(index))
                # Keep each shell consistent, while varying the cavity's normal direction.
                positive_normal = (side == 1) != void
                if positive_normal != (axis != 1):
                    corners.reverse()
                if ifc_class == "IfcFacetedBrepWithVoids":
                    loop = model.createIfcPolyLoop([vertex(corner).VertexGeometry for corner in corners])
                    bound = model.createIfcFaceOuterBound(loop, True)
                    faces.append(model.createIfcFace([bound]))
                    continue
                oriented_edges = []
                for start, end in zip(corners, corners[1:] + corners[:1]):
                    curve, orientation = edge(start, end)
                    oriented_edges.append(model.createIfcOrientedEdge(None, None, curve, orientation))
                bound = model.createIfcFaceOuterBound(model.createIfcEdgeLoop(oriented_edges), True)
                origin, normal, x_axis = planes[axis, side]
                placement = model.createIfcAxis2Placement3D(point(origin), direction(normal), direction(x_axis))
                faces.append(model.createIfcAdvancedFace([bound], model.createIfcPlane(placement), positive_normal))
        return model.createIfcClosedShell(faces)

    outer = box(0, 4)
    inner = box(1, 2, void=voids_inwards)
    return model, model.create_entity(ifc_class, outer, [inner])


@pytest.mark.parametrize("schema", ["IFC4", "IFC4X3_ADD2"])
@pytest.mark.parametrize("ifc_class", ["IfcAdvancedBrepWithVoids", "IfcFacetedBrepWithVoids"])
@pytest.mark.parametrize("boolean", [False, True])
@pytest.mark.parametrize("reorient_shells", [False, True])
@pytest.mark.parametrize("voids_inwards", [False, True], ids=["voids-outwards", "voids-inwards"])
def test_brep_with_void_volume_10249(schema, ifc_class, boolean, reorient_shells, voids_inwards):
    # https://github.com/IfcOpenShell/IfcOpenShell/issues/10249
    model, brep = build_brep_with_void(schema, ifc_class, voids_inwards)
    item = brep
    if boolean:
        # Remove x >= 3 without touching the enclosed [1, 2]^3 cavity.
        profile = model.createIfcRectangleProfileDef("AREA", None, None, 2.0, 6.0)
        placement = model.createIfcAxis2Placement3D(model.createIfcCartesianPoint((4.0, 2.0, -1.0)))
        tool = model.createIfcExtrudedAreaSolid(profile, placement, model.createIfcDirection((0.0, 0.0, 1.0)), 6.0)
        item = model.createIfcBooleanResult("DIFFERENCE", brep, tool)
    geometry = ifcopenshell.geom.create_shape(
        ifcopenshell.geom.settings(REORIENT_SHELLS=reorient_shells), item, geometry_library="opencascade"
    )
    # The internal [1, 2]^3 box must be subtracted from the outer [0, 4]^3 box.
    assert ifcopenshell.util.shape.get_volume(geometry) == pytest.approx(47.0 if boolean else 63.0)
    assert ifcopenshell.util.shape.get_area(geometry) == pytest.approx(86.0 if boolean else 102.0)


@pytest.mark.parametrize("operator", ["DIFFERENCE", "UNION", "INTERSECTION"])
@pytest.mark.parametrize("invalid_first", [False, True])
def test_boolean_propagates_operand_conversion_failure(operator, invalid_first):
    model = ifcopenshell.file(schema="IFC4")
    profile = model.createIfcRectangleProfileDef("AREA", None, None, 2.0, 2.0)
    placement = model.createIfcAxis2Placement3D(model.createIfcCartesianPoint((0.0, 0.0, 0.0)))
    valid = model.createIfcExtrudedAreaSolid(profile, placement, model.createIfcDirection((0.0, 0.0, 1.0)), 2.0)
    invalid = model.createIfcSphere(placement, -1.0)
    settings = ifcopenshell.geom.settings()
    # A negative-radius sphere maps successfully, but OpenCASCADE cannot construct it.
    assert ifcopenshell.ifcopenshell_wrapper.map_shape(settings, invalid) is not None
    with pytest.raises(RuntimeError, match="Failed to process shape"):
        ifcopenshell.geom.create_shape(settings, invalid, geometry_library="opencascade")
    operands = (invalid, valid) if invalid_first else (valid, invalid)
    boolean = model.createIfcBooleanResult(operator, *operands)
    with pytest.raises(RuntimeError, match="Failed to process shape"):
        ifcopenshell.geom.create_shape(settings, boolean, geometry_library="opencascade")


@pytest.mark.parametrize("empty_first", [False, True])
def test_boolean_accepts_empty_operand(empty_first):
    model = ifcopenshell.file(schema="IFC4")
    blocks = []
    for x in (0.0, 5.0):
        placement = model.createIfcAxis2Placement3D(model.createIfcCartesianPoint((x, 0.0, 0.0)))
        blocks.append(model.createIfcBlock(placement, 2.0, 2.0, 2.0))
    empty = model.createIfcBooleanResult("INTERSECTION", *blocks)
    operands = (empty, blocks[0]) if empty_first else (blocks[0], empty)
    boolean = model.createIfcBooleanResult("DIFFERENCE", *operands)
    geometry = ifcopenshell.geom.create_shape(ifcopenshell.geom.settings(), boolean, geometry_library="opencascade")
    assert ifcopenshell.util.shape.get_volume(geometry) == pytest.approx(0.0 if empty_first else 8.0)
