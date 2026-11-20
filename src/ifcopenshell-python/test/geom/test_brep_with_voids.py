# This file was generated with the assistance of an AI coding tool.

import pytest

import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.util.shape


def build_brep_with_void(schema, ifc_class):
    """Build the boxes from issue #10249 with advanced or faceted faces."""
    # Keep the reported loop orientations and SameSense values, including their inconsistencies.
    model = ifcopenshell.file(schema=schema)

    def point(coords):
        return model.createIfcCartesianPoint([float(c) for c in coords])

    def direction(coords):
        return model.createIfcDirection([float(c) for c in coords])

    def box(lower, upper):
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
                faces.append(model.createIfcAdvancedFace([bound], model.createIfcPlane(placement), True))
        return model.createIfcClosedShell(faces)

    outer = box(0, 4)
    inner = box(1, 2)
    return model, model.create_entity(ifc_class, outer, [inner])


@pytest.mark.parametrize("schema", ["IFC4", "IFC4X3_ADD2"])
@pytest.mark.parametrize("ifc_class", ["IfcAdvancedBrepWithVoids", "IfcFacetedBrepWithVoids"])
def test_brep_with_void_volume_10249(schema, ifc_class):
    # https://github.com/IfcOpenShell/IfcOpenShell/issues/10249
    model, brep = build_brep_with_void(schema, ifc_class)
    geometry = ifcopenshell.geom.create_shape(ifcopenshell.geom.settings(), brep, geometry_library="opencascade")
    # The internal [1, 2]^3 box must be subtracted from the outer [0, 4]^3 box.
    assert ifcopenshell.util.shape.get_volume(geometry) == pytest.approx(4.0**3 - 1.0**3)
    assert ifcopenshell.util.shape.get_area(geometry) == pytest.approx(6.0 * (4.0**2 + 1.0**2))
