# This file was generated with the assistance of an AI coding tool.

import pytest

import ifcopenshell
import ifcopenshell.geom


def walls(second_start: float) -> tuple[ifcopenshell.file, ifcopenshell.entity_instance, ifcopenshell.entity_instance]:
    f = ifcopenshell.file(schema="IFC4")
    context = f.create_entity("IfcGeometricRepresentationContext")

    def wall(start: float, end: float) -> ifcopenshell.entity_instance:
        solid = f.create_entity(
            "IfcExtrudedAreaSolid",
            SweptArea=f.create_entity(
                "IfcRectangleProfileDef",
                ProfileType="AREA",
                XDim=end - start,
                YDim=0.2,
                Position=f.create_entity(
                    "IfcAxis2Placement2D",
                    Location=f.create_entity("IfcCartesianPoint", Coordinates=((start + end) / 2, 0.0)),
                ),
            ),
            Position=f.create_entity(
                "IfcAxis2Placement3D", Location=f.create_entity("IfcCartesianPoint", Coordinates=(0.0, 0.0, 0.0))
            ),
            ExtrudedDirection=f.create_entity("IfcDirection", DirectionRatios=(0.0, 0.0, 1.0)),
            Depth=3.0,
        )
        representation = f.create_entity(
            "IfcShapeRepresentation",
            ContextOfItems=context,
            RepresentationIdentifier="Body",
            RepresentationType="SweptSolid",
            Items=[solid],
        )
        return f.create_entity(
            "IfcWall",
            GlobalId=ifcopenshell.guid.new(),
            Representation=f.create_entity("IfcProductDefinitionShape", Representations=[representation]),
        )

    return f, wall(0.0, 2.0), wall(second_start, 4.0)


@pytest.mark.parametrize("second_start, expected", [(1.95, 1), (2.0, 0), (2.05, 0)])
def test_intersection_of_aligned_walls(second_start: float, expected: int) -> None:
    f, a, b = walls(second_start)
    tree = ifcopenshell.geom.tree(backend="opencascade.trianglebvh")
    tree.add_file(f, ifcopenshell.geom.settings())
    assert len(tree.clash_intersection_many([a], [b], tolerance=0.002, check_all=True)) == expected
