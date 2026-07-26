# This file was generated with the assistance of an AI coding tool.
from __future__ import annotations

import ifcopenshell
import ifcopenshell.api.aggregate
import ifcopenshell.api.owner.settings
import ifcopenshell.api.project
import ifcopenshell.api.root
import ifcopenshell.api.spatial
import ifcopenshell.api.unit
import pytest

from ifcedit.quantify import AVAILABLE_RULES, list_rules, run_quantify


class TestListRules:
    def test_returns_list(self):
        result = list_rules()
        assert isinstance(result, list)

    def test_each_entry_has_name(self):
        result = list_rules()
        for entry in result:
            assert "name" in entry

    def test_ifc4_rule_present(self):
        result = list_rules()
        names = [r["name"] for r in result]
        assert "IFC4QtoBaseQuantities" in names

    def test_ifc4x3_rule_present(self):
        result = list_rules()
        names = [r["name"] for r in result]
        assert "IFC4X3QtoBaseQuantities" in names


@pytest.fixture
def quantify_model():
    """Create an IFC4 model with a wall element."""
    f = ifcopenshell.api.project.create_file()
    ifcopenshell.api.owner.settings.get_user = lambda ifc: (ifc.by_type("IfcPersonAndOrganization") or [None])[0]
    ifcopenshell.api.owner.settings.get_application = lambda ifc: (ifc.by_type("IfcApplication") or [None])[0]

    project = ifcopenshell.api.root.create_entity(f, ifc_class="IfcProject", name="TestProject")
    ifcopenshell.api.unit.assign_unit(f)

    site = ifcopenshell.api.root.create_entity(f, ifc_class="IfcSite", name="TestSite")
    building = ifcopenshell.api.root.create_entity(f, ifc_class="IfcBuilding", name="TestBuilding")
    storey = ifcopenshell.api.root.create_entity(f, ifc_class="IfcBuildingStorey", name="Ground Floor")

    ifcopenshell.api.aggregate.assign_object(f, products=[site], relating_object=project)
    ifcopenshell.api.aggregate.assign_object(f, products=[building], relating_object=site)
    ifcopenshell.api.aggregate.assign_object(f, products=[storey], relating_object=building)

    wall = ifcopenshell.api.root.create_entity(f, ifc_class="IfcWall", name="Wall001")
    ifcopenshell.api.spatial.assign_container(f, products=[wall], relating_structure=storey)

    return f


class TestRunQuantify:
    def test_returns_ok_true(self, quantify_model):
        result = run_quantify(quantify_model, "IFC4QtoBaseQuantities")
        assert result["ok"] is True

    def test_returns_rule_name(self, quantify_model):
        result = run_quantify(quantify_model, "IFC4QtoBaseQuantities")
        assert result["rule"] == "IFC4QtoBaseQuantities"

    def test_returns_elements_quantified(self, quantify_model):
        result = run_quantify(quantify_model, "IFC4QtoBaseQuantities")
        assert "elements_quantified" in result
        assert isinstance(result["elements_quantified"], int)

    def test_unknown_rule_returns_error(self, quantify_model):
        result = run_quantify(quantify_model, "NonExistentRule")
        assert result["ok"] is False
        assert "error" in result

    def test_selector_restricts_elements(self, quantify_model):
        result = run_quantify(quantify_model, "IFC4QtoBaseQuantities", selector="IfcWall")
        assert result["ok"] is True
        assert result["rule"] == "IFC4QtoBaseQuantities"

    def test_empty_selector_runs_on_all(self, quantify_model):
        result = run_quantify(quantify_model, "IFC4QtoBaseQuantities", selector=None)
        assert result["ok"] is True

    def test_default_selector_includes_spaces(self, quantify_model, monkeypatch):
        """IfcSpace is not a subtype of IfcElement, so the default scope must add it explicitly."""
        import ifc5d.qto

        seen_elements = {}

        def fake_quantify(ifc_file, elements, rules):
            seen_elements["elements"] = elements
            return {}

        monkeypatch.setattr(ifc5d.qto, "quantify", fake_quantify)

        space = ifcopenshell.api.root.create_entity(quantify_model, ifc_class="IfcSpace", name="TestSpace")
        run_quantify(quantify_model, "IFC4QtoBaseQuantities")

        assert space in seen_elements["elements"]
