#!/bin/bash

# Hack while we do not have bcf-client on our conda ifcopenshell channel yet
# pip install bcf-client
cd test && python tests.py
cd ../src/ifcopenshell-python/test && pytest -p no:pytest-blender
