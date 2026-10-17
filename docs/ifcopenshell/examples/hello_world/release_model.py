# This file was generated with the assistance of an AI coding tool.
#
# Hello, world! (Python): releasing the model.

import sys

import ifcopenshell

model = ifcopenshell.open(sys.argv[1])

# tag::example
# The model is released once nothing refers to it anymore.
del model
# end::example

assert "model" not in globals()
