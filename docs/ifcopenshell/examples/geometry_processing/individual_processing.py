# This file was generated with the assistance of an AI coding tool.
#
# Geometry processing (Python): processing a single element.

import sys

# tag::example
# tag::setup
import ifcopenshell
import ifcopenshell.geom
# end::setup
import ifcopenshell.util.shape

ifc_file = ifcopenshell.open(sys.argv[1])
element = ifc_file.by_type("IfcWall")[0]

# Choosing a geometry kernel has a big impact on speed and capability. It is
# recommended to use the hybrid of the cgal-simple kernel, with opencascade as
# a fallback.
settings = ifcopenshell.geom.settings()
shape = ifcopenshell.geom.create_shape(settings, element, geometry_library="hybrid-cgal-simple-opencascade")

# The GUID and the STEP ID of the element we processed
print(shape.guid)
print(shape.id)

# The element we are processing
print(ifc_file.by_guid(shape.guid))

# A unique geometry ID, useful to check whether or not two geometries are
# identical for caching and reuse. The naming scheme is:
# IfcShapeRepresentation.id{-layerset-LayerSet.id}{-material-Material.id}{-openings-[Opening n.id ...]}{-world-coords}
print(shape.geometry.id)

# A 4x4 matrix representing the location and rotation of the element, in the form:
# [ [ x_x, y_x, z_x, x   ]
#   [ x_y, y_y, z_y, y   ]
#   [ x_z, y_z, z_z, z   ]
#   [ 0.0, 0.0, 0.0, 1.0 ] ]
# The position is given by the last column: (x, y, z)
# The rotation is described by the first three columns, by explicitly
# specifying the local X, Y, Z axes, in a right-handed coordinate system.
# Objects are never scaled, so the scale factor of the matrix is always 1.
matrix = shape.transformation.matrix

# For convenience, you might want the matrix as a nested numpy array, so you
# can do matrix math, and extract the XYZ location from it.
matrix = ifcopenshell.util.shape.get_shape_matrix(shape)
location = matrix[:, 3][0:3]

# X Y Z of vertices in flattened list e.g. [v1x, v1y, v1z, v2x, v2y, v2z, ...]
# These vertices are local relative to the shape's transformation matrix.
verts = shape.geometry.verts

# Indices of vertices per edge e.g. [e1v1, e1v2, e2v1, e2v2, ...]
# If the geometry is mesh-like, edges contain the original edges.
# These may be quads or ngons and not necessarily triangles.
edges = shape.geometry.edges

# Indices of vertices per triangle face e.g. [f1v1, f1v2, f1v3, f2v1, f2v2, f2v3, ...]
# Note that faces are always triangles.
faces = shape.geometry.faces

# Since the lists are flattened, you may prefer to group them as nested numpy
# arrays, e.g. [[v1x, v1y, v1z], [v2x, v2y, v2z], ...]
grouped_verts = ifcopenshell.util.shape.get_vertices(shape.geometry)
grouped_edges = ifcopenshell.util.shape.get_edges(shape.geometry)
grouped_faces = ifcopenshell.util.shape.get_faces(shape.geometry)

# A list of styles that are relevant to this shape
for style in shape.geometry.materials:
    # The style is named after the IFC entity it comes from, such as
    # "IfcSurfaceStyleRendering-15008", or after the entity class of the
    # element if a default material is applied.
    print(style.name)

    # The colour of the style, as RGB values between 0 and 1
    colour = style.get_color()
    print(colour.r(), colour.g(), colour.b())

    # Each style may have transparency data
    if style.has_transparency():
        print(style.transparency)

# Indices of material applied per triangle face e.g. [f1m, f2m, ...]
material_ids = shape.geometry.material_ids

# IDs of the representation item per triangle face e.g. [f1i, f2i, ...]
item_ids = shape.geometry.item_ids
# end::example

assert shape.id == element.id()
assert len(verts) % 3 == 0 and len(faces) % 3 == 0 and faces
assert len(grouped_faces) == len(faces) // 3
assert len(location) == 3
