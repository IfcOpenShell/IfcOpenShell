# This file was generated with the assistance of an AI coding tool.
#
# Hello, world! (Python): loading the model.

# tag::example
import sys

import ifcopenshell

# The path is the first command-line argument so this example can be run.
model = ifcopenshell.open(sys.argv[1])
# end::example

assert model.by_type("IfcProject")
