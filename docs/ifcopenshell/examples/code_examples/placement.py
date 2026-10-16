# This file was generated with the assistance of an AI coding tool.
#
# Code examples (Python): get the XYZ coordinates of an element.

import sys

import ifcopenshell

model = ifcopenshell.open(sys.argv[1])

# tag::example
import ifcopenshell.util.placement

wall = model.by_type("IfcWall")[0]
# This returns a 4x4 matrix, including the location and rotation. For example:
# array([[ 1.00000000e+00,  0.00000000e+00,  0.00000000e+00, 2.00000000e+00],
#        [ 0.00000000e+00,  1.00000000e+00,  0.00000000e+00, 3.00000000e+00],
#        [ 0.00000000e+00,  0.00000000e+00,  1.00000000e+00, 5.00000000e+00],
#        [ 0.00000000e+00,  0.00000000e+00,  0.00000000e+00, 1.00000000e+00]])
matrix = ifcopenshell.util.placement.get_local_placement(wall.ObjectPlacement)
# The last column holds the XYZ values, such as:
# array([ 2.00000000e+00,  3.00000000e+00,  5.00000000e+00])
print(matrix[:, 3][:3])
# end::example

assert matrix.shape == (4, 4)
