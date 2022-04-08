#!/bin/bash

cd test && python tests.py
cd ../src/ifcopenshell-python && mv ifcopenshell ifcopenshell-local && make test
