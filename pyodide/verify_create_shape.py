"""Geometry smoke test executed inside Pyodide by verify_wheels.mjs."""

from pathlib import Path

import ifcopenshell
import ifcopenshell.geom

assert str(Path(ifcopenshell.__file__).parent) in ifcopenshell.get_plugin_search_paths()

# Exercise schema-dependent mapping as well as the geometry kernel. Entity
# creation alone does not call the schema functions imported by the mapping DSO.
model = ifcopenshell.file(schema="IFC4")
point = model.create_entity("IfcCartesianPoint", (0.0, 0.0))
position = model.create_entity("IfcAxis2Placement2D", point)
profile = model.create_entity("IfcRectangleProfileDef", "AREA", None, position, 2.0, 4.0)
direction = model.create_entity("IfcDirection", (0.0, 0.0, 1.0))
solid = model.create_entity("IfcExtrudedAreaSolid", profile, None, direction, 3.0)

shape = ifcopenshell.geom.create_shape(ifcopenshell.geom.settings(), solid, geometry_library="manifold")
assert shape.verts and shape.faces, "create_shape returned an empty mesh"
assert len(shape.verts) % 3 == 0 and len(shape.faces) % 3 == 0
assert all(0 <= index < len(shape.verts) // 3 for index in shape.faces)
for axis, expected in enumerate((2.0, 4.0, 3.0)):
    coordinates = shape.verts[axis::3]
    extent = max(coordinates) - min(coordinates)
    assert abs(extent - expected) < 1e-6, (axis, extent, expected)
print(f"create_shape passed: {len(shape.verts) // 3} vertices, {len(shape.faces) // 3} triangles")
