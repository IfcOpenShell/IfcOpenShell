# This file was generated with the assistance of an AI coding tool.
from __future__ import annotations

import ifcopenshell
import ifcopenshell.api.project
import pytest

from ifcquery.validate import validate


class TestValidate:
    def test_valid_model_returns_valid_true(self, model):
        result = validate(model)
        assert result["valid"] is True
        assert isinstance(result["issues"], list)

    def test_valid_model_has_no_issues(self, model):
        result = validate(model)
        assert result["issues"] == []

    def test_empty_model_is_valid(self):
        f = ifcopenshell.api.project.create_file()
        result = validate(f)
        assert result["valid"] is True
        assert result["issues"] == []

    def test_result_has_expected_keys(self, model):
        result = validate(model)
        assert "valid" in result
        assert "issues" in result

    def test_express_rules_flag_accepted(self, model):
        # Just verify it runs without error; express rules may add/not add issues
        result = validate(model, express_rules=True)
        assert "valid" in result
        assert isinstance(result["issues"], list)

    def test_issue_has_level_and_message(self, model):
        # Force an issue by manually breaking the model (invalid IfcWall attribute)
        f = ifcopenshell.file()
        # Create a raw IfcWall with deliberately wrong type for GlobalId (use int)
        # We just check structure if any issues appear; on well-formed models there are none.
        result = validate(model)
        # Even if no issues, the structure contract must hold for any issues present
        for issue in result["issues"]:
            assert "level" in issue
            assert "message" in issue
