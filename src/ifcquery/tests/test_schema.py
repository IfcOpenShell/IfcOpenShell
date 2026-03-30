# This file was generated with the assistance of an AI coding tool.
from __future__ import annotations

import pytest

from ifcquery.schema import schema


class TestSchema:
    def test_ifc_wall_has_description(self, model):
        result = schema(model, "IfcWall")
        assert "description" in result
        assert isinstance(result["description"], str)
        assert len(result["description"]) > 0

    def test_ifc_wall_has_attributes(self, model):
        result = schema(model, "IfcWall")
        assert "attributes" in result

    def test_ifc_wall_has_spec_url(self, model):
        result = schema(model, "IfcWall")
        assert "spec_url" in result

    def test_unknown_entity_returns_error(self, model):
        result = schema(model, "IfcNonExistentFooBar")
        assert "error" in result
        assert "IfcNonExistentFooBar" in result["error"]

    def test_ifc_window_has_description(self, model):
        result = schema(model, "IfcWindow")
        assert "description" in result
        assert len(result["description"]) > 0
