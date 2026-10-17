# This file was generated with the assistance of an AI coding tool.

import numpy as np
import pytest

import ifcopenshell
import ifcopenshell.geom

kernels = [
    pytest.param(
        kernel,
        marks=pytest.mark.skipif(
            not ifcopenshell.geom.has_geometry_library(kernel),
            reason=f"{kernel} geometry kernel is unavailable",
        ),
    )
    for kernel in ("opencascade", "cgal")
]


def cylinder(radius: float, height: float) -> tuple[ifcopenshell.file, ifcopenshell.entity_instance]:
    f = ifcopenshell.file(schema="IFC4")
    context = f.create_entity("IfcGeometricRepresentationContext")
    position = f.create_entity(
        "IfcAxis2Placement3D", Location=f.create_entity("IfcCartesianPoint", Coordinates=(1.0, 2.0, 3.0))
    )
    csg = f.create_entity(
        "IfcCsgSolid",
        TreeRootExpression=f.create_entity("IfcRightCircularCylinder", Position=position, Height=height, Radius=radius),
    )
    representation = f.create_entity(
        "IfcShapeRepresentation",
        ContextOfItems=context,
        RepresentationIdentifier="Body",
        RepresentationType="CSG",
        Items=[csg],
    )
    element = f.create_entity(
        "IfcBuildingElementProxy",
        GlobalId=ifcopenshell.guid.new(),
        Representation=f.create_entity("IfcProductDefinitionShape", Representations=[representation]),
    )
    return f, element


@pytest.mark.parametrize("kernel", kernels)
def test_right_circular_cylinder_is_converted(kernel: str) -> None:
    _, element = cylinder(0.5, 3.0)
    shape = ifcopenshell.geom.create_shape(ifcopenshell.geom.settings(), element, geometry_library=kernel)
    verts = np.array(shape.geometry.verts).reshape(-1, 3)
    assert np.allclose(verts.min(axis=0), (0.5, 1.5, 3.0), atol=1e-2)
    assert np.allclose(verts.max(axis=0), (1.5, 2.5, 6.0), atol=1e-2)


def test_right_circular_cylinder_with_zero_height_is_not_converted() -> None:
    _, element = cylinder(0.5, 0.0)
    with pytest.raises(RuntimeError):
        ifcopenshell.geom.create_shape(ifcopenshell.geom.settings(), element)
