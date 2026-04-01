# Tests for ifcedit.foreach
import ifcopenshell
import ifcopenshell.api.owner.settings
import ifcopenshell.api.project
import ifcopenshell.api.root
import ifcopenshell.api.spatial
import ifcopenshell.api.unit
import pytest

from ifcedit.foreach import _substitute, run_foreach


@pytest.fixture
def model(model):
    return model


class TestSubstitute:
    def test_single_field(self):
        assert _substitute("--product {id}", {"id": 42}) == "--product 42"

    def test_multiple_fields(self):
        result = _substitute("{type} #{id} ({name})", {"id": 5, "type": "IfcWall", "name": "W1"})
        assert result == "IfcWall #5 (W1)"

    def test_no_placeholder(self):
        assert _substitute("hello", {"id": 1}) == "hello"

    def test_unknown_placeholder_unchanged(self):
        assert _substitute("{unknown}", {"id": 1}) == "{unknown}"


class TestRunForeach:
    def _items(self, model, ifc_class):
        return [{"id": e.id(), "type": e.is_a(), "name": e.Name} for e in model.by_type(ifc_class)]

    def test_rename_single(self, model):
        items = self._items(model, "IfcWall")
        result = run_foreach(
            model, "attribute", "edit_attributes", {"product": "{id}", "attributes": '{"Name": "R"}'}, items
        )
        assert result["ok"] is True
        assert result["count"] == 1
        assert result["errors"] == []
        assert model.by_type("IfcWall")[0].Name == "R"

    def test_rename_multiple(self, model):
        items = self._items(model, "IfcElement")
        result = run_foreach(
            model, "attribute", "edit_attributes", {"product": "{id}", "attributes": '{"Name": "X"}'}, items
        )
        assert result["ok"] is True
        assert result["count"] == len(items)

    def test_empty_list(self, model):
        result = run_foreach(model, "root", "remove_product", {"product": "{id}"}, [])
        assert result["ok"] is True
        assert result["count"] == 0
        assert result["errors"] == []

    def test_bad_id_collects_error(self, model):
        items = [{"id": 999999, "type": "IfcWall", "name": "X"}]
        result = run_foreach(model, "root", "remove_product", {"product": "{id}"}, items)
        assert result["ok"] is False
        assert result["count"] == 0
        assert len(result["errors"]) == 1
        assert result["errors"][0]["index"] == 0

    def test_non_dict_item_collects_error(self, model):
        result = run_foreach(model, "root", "remove_product", {"product": "{id}"}, ["not_a_dict"])
        assert result["ok"] is False
        assert len(result["errors"]) == 1

    def test_partial_failure_counts_successes(self, model):
        wall_id = model.by_type("IfcWall")[0].id()
        items = [
            {"id": wall_id, "type": "IfcWall", "name": "W"},
            {"id": 999999, "type": "IfcWall", "name": "Bad"},
        ]
        result = run_foreach(
            model, "attribute", "edit_attributes", {"product": "{id}", "attributes": '{"Name": "Ok"}'}, items
        )
        assert result["ok"] is False
        assert result["count"] == 1
        assert len(result["errors"]) == 1
