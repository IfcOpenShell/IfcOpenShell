# This file was generated with the assistance of an AI coding tool.

import pytest

import ifcopenshell


def test_get_argument_by_name_on_defined_type():
    model = ifcopenshell.file(schema="IFC4")
    duration = model.create_entity("IfcDuration", "P1D")
    assert duration.get_argument("wrappedValue") == "P1D"
    with pytest.raises(RuntimeError):
        duration.get_argument("Name")
