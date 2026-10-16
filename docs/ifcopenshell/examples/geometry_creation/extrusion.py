# This file was generated with the assistance of an AI coding tool.
#
# Geometry creation (Python): an extruded rectangular profile.

import ifcopenshell
import ifcopenshell.geom

# tag::example
model = ifcopenshell.file(schema="IFC4")

origin = model.create_entity("IfcCartesianPoint", Coordinates=(0.0, 0.0, 0.0))
axes = model.create_entity("IfcAxis2Placement3D", Location=origin)

# A 1 by 1 metre rectangle, centred at the origin, extruded 1 metre up.
profile = model.create_entity("IfcRectangleProfileDef", ProfileType="AREA", XDim=1.0, YDim=1.0)
up = model.create_entity("IfcDirection", DirectionRatios=(0.0, 0.0, 1.0))
solid = model.create_entity(
    "IfcExtrudedAreaSolid", SweptArea=profile, Position=axes, ExtrudedDirection=up, Depth=1.0
)

# The solid is the Body of the wall, in a 3D model context.
context = model.create_entity(
    "IfcGeometricRepresentationContext",
    ContextType="Model",
    CoordinateSpaceDimension=3,
    Precision=1e-5,
    WorldCoordinateSystem=axes,
)
body = model.create_entity(
    "IfcShapeRepresentation",
    ContextOfItems=context,
    RepresentationIdentifier="Body",
    RepresentationType="SweptSolid",
    Items=[solid],
)
definition = model.create_entity("IfcProductDefinitionShape", Representations=[body])

placement = model.create_entity("IfcLocalPlacement", RelativePlacement=axes)
wall = model.create_entity(
    "IfcWall",
    GlobalId=ifcopenshell.guid.new(),
    Name="Box wall",
    ObjectPlacement=placement,
    Representation=definition,
)
print(wall.id(), wall.Name)
# end::example

shape = ifcopenshell.geom.create_shape(ifcopenshell.geom.settings(), wall)
assert len(shape.geometry.faces) // 3 == 12
