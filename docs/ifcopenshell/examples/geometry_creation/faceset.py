# This file was generated with the assistance of an AI coding tool.
#
# Geometry creation (Python): a triangulated face set.

import ifcopenshell

model = ifcopenshell.file(schema="IFC4")

# tag::example
points = model.create_entity("IfcCartesianPointList3D", CoordList=[(0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (0.0, 1.0, 0.0)])
mesh = model.create_entity(
    "IfcTriangulatedFaceSet",
    Coordinates=points,
    Closed=False,
    # One triangle, with one-based indices into the CoordList.
    CoordIndex=[(1, 2, 3)],
)
print(mesh.id())
# end::example

assert mesh.CoordIndex == ((1, 2, 3),)
