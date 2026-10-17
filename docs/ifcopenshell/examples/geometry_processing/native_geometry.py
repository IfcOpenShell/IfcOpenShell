# This file was generated with the assistance of an AI coding tool.
#
# Geometry processing (Python): the untriangulated OpenCASCADE shape.
#
# This needs pythonOCC, which is not a dependency of IfcOpenShell, so the
# program does nothing when pythonOCC is not installed.

import sys

try:
    import OCC  # noqa: F401
except ImportError:
    print("pythonOCC is not installed, skipping")
    sys.exit(0)

import ifcopenshell

ifc_file = ifcopenshell.open(sys.argv[1])

# tag::example
import ifcopenshell.geom

element = ifc_file.by_type("IfcWall")[0]

settings = ifcopenshell.geom.settings()
settings.set("use-python-opencascade", True)

shape = ifcopenshell.geom.create_shape(settings, element)
# These are methods of the TopoDS_Shape class from pythonOCC
shape_gpXYZ = shape.geometry.Location().Transformation().TranslationPart()
# These are methods of the gp_XYZ class from pythonOCC
print(shape_gpXYZ.X(), shape_gpXYZ.Y(), shape_gpXYZ.Z())
# end::example
