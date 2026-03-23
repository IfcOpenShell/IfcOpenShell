# This file was generated with the assistance of an AI coding tool.
from __future__ import annotations

import ifcopenshell
import ifcopenshell.api.cost
import ifcopenshell.api.owner.settings
import ifcopenshell.api.project
import ifcopenshell.api.root
import ifcopenshell.api.unit
import pytest

from ifcquery.cost import cost


@pytest.fixture
def cost_model():
    """Create an IFC4 model with a cost schedule, a top-level item, and one nested subitem."""
    f = ifcopenshell.api.project.create_file()
    ifcopenshell.api.owner.settings.get_user = lambda ifc: (ifc.by_type("IfcPersonAndOrganization") or [None])[0]
    ifcopenshell.api.owner.settings.get_application = lambda ifc: (ifc.by_type("IfcApplication") or [None])[0]

    project = ifcopenshell.api.root.create_entity(f, ifc_class="IfcProject", name="TestProject")
    ifcopenshell.api.unit.assign_unit(f)

    cs = ifcopenshell.api.cost.add_cost_schedule(f, name="Bill of Quantities")
    item = ifcopenshell.api.cost.add_cost_item(f, cost_schedule=cs)
    ifcopenshell.api.cost.edit_cost_item(f, cost_item=item, attributes={"Name": "Concrete Works"})
    cv = ifcopenshell.api.cost.add_cost_value(f, parent=item)
    ifcopenshell.api.cost.edit_cost_value(f, cost_value=cv, attributes={"AppliedValue": 1200.0, "Category": "material"})

    # Add a nested subitem
    subitem = ifcopenshell.api.cost.add_cost_item(f, cost_item=item)
    ifcopenshell.api.cost.edit_cost_item(f, cost_item=subitem, attributes={"Name": "Formwork"})

    return f


class TestCost:
    def test_returns_list(self, cost_model):
        result = cost(cost_model)
        assert isinstance(result, list)

    def test_finds_cost_schedule(self, cost_model):
        result = cost(cost_model)
        assert len(result) == 1

    def test_schedule_has_name(self, cost_model):
        result = cost(cost_model)
        assert result[0]["name"] == "Bill of Quantities"

    def test_schedule_has_id(self, cost_model):
        result = cost(cost_model)
        assert isinstance(result[0]["id"], int)
        assert result[0]["id"] > 0

    def test_schedule_has_items(self, cost_model):
        result = cost(cost_model)
        assert len(result[0]["items"]) == 1

    def test_item_has_required_fields(self, cost_model):
        result = cost(cost_model)
        item = result[0]["items"][0]
        assert "id" in item
        assert "name" in item
        assert "values" in item
        assert "subitems" in item

    def test_item_name(self, cost_model):
        result = cost(cost_model)
        assert result[0]["items"][0]["name"] == "Concrete Works"

    def test_item_has_values(self, cost_model):
        result = cost(cost_model)
        values = result[0]["items"][0]["values"]
        assert len(values) == 1
        assert "formula" in values[0]
        assert "category" in values[0]

    def test_item_value_category(self, cost_model):
        result = cost(cost_model)
        values = result[0]["items"][0]["values"]
        assert values[0]["category"] == "material"

    def test_empty_model_returns_empty_list(self, model):
        result = cost(model)
        assert result == []

    def test_max_depth_none_returns_full_tree(self, cost_model):
        result = cost(cost_model, max_depth=None)
        item = result[0]["items"][0]
        assert isinstance(item["subitems"], list)
        assert len(item["subitems"]) == 1
        assert item["subitems"][0]["name"] == "Formwork"

    def test_max_depth_1_truncates_subitems(self, cost_model):
        result = cost(cost_model, max_depth=1)
        item = result[0]["items"][0]
        assert isinstance(item["subitems"], dict)
        assert item["subitems"]["truncated"] is True
        assert item["subitems"]["count"] == 1

    def test_max_depth_2_expands_to_depth_2(self, cost_model):
        result = cost(cost_model, max_depth=2)
        item = result[0]["items"][0]
        assert isinstance(item["subitems"], list)
        assert item["subitems"][0]["name"] == "Formwork"
        # subitem has no children, so subitems should be empty list
        assert item["subitems"][0]["subitems"] == []
