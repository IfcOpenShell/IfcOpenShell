# This file was generated with the assistance of an AI coding tool.
#
# Hello, world! (Python): creating a new file.

import sys

import ifcopenshell

model = ifcopenshell.open(sys.argv[1])

# tag::example
ifc = ifcopenshell.file()
# Or if you want a particular schema:
ifc = ifcopenshell.file(schema="IFC4")
# end::example

assert ifc.schema == "IFC4"
