# This file was generated with the assistance of an AI coding tool.
import json
from unittest.mock import patch

import ifcopenshell.api.root
import pytest

from ifcmcp.core import IfcSessionError


def walls(session):
    return [w.Name for w in session.model.by_type("IfcWall")]


def create_wall(session, name="New"):
    result = session.ifc_edit("root.create_entity", json.dumps({"ifc_class": "IfcWall", "name": name}))
    assert result["ok"], result
    return result["result"]["id"]


class TestUndoRedo:
    def test_undo_a_create(self, loaded_session):
        create_wall(loaded_session)
        assert walls(loaded_session) == ["Wall001", "New"]
        loaded_session.ifc_undo()
        assert walls(loaded_session) == ["Wall001"]

    def test_redo_a_create(self, loaded_session):
        create_wall(loaded_session)
        loaded_session.ifc_undo()
        loaded_session.ifc_redo()
        assert walls(loaded_session) == ["Wall001", "New"]

    def test_undo_an_attribute_edit(self, loaded_session):
        wall = loaded_session.model.by_type("IfcWall")[0]
        params = {"product": str(wall.id()), "attributes": json.dumps({"Name": "Renamed"})}
        assert loaded_session.ifc_edit("attribute.edit_attributes", json.dumps(params))["ok"]
        assert wall.Name == "Renamed"
        loaded_session.ifc_undo()
        assert wall.Name == "Wall001"

    def test_undo_a_removal_keeps_the_step_id(self, loaded_session):
        wall = loaded_session.model.by_type("IfcWall")[0]
        wall_id = wall.id()
        assert loaded_session.ifc_edit("root.remove_product", json.dumps({"product": str(wall_id)}))["ok"]
        assert walls(loaded_session) == []
        loaded_session.ifc_undo()
        assert loaded_session.model.by_id(wall_id).Name == "Wall001"

    def test_each_call_is_one_step(self, loaded_session):
        create_wall(loaded_session, "A")
        create_wall(loaded_session, "B")
        assert loaded_session.ifc_undo() == {"ok": True, "undo_available": 1, "redo_available": 1}
        assert walls(loaded_session) == ["Wall001", "A"]

    def test_a_new_change_discards_redo(self, loaded_session):
        create_wall(loaded_session, "A")
        loaded_session.ifc_undo()
        create_wall(loaded_session, "B")
        with pytest.raises(IfcSessionError, match="Nothing to redo"):
            loaded_session.ifc_redo()

    def test_nothing_to_undo(self, loaded_session):
        with pytest.raises(IfcSessionError, match="Nothing to undo"):
            loaded_session.ifc_undo()

    def test_nothing_to_redo(self, loaded_session):
        with pytest.raises(IfcSessionError, match="Nothing to redo"):
            loaded_session.ifc_redo()

    def test_loading_starts_a_new_history(self, loaded_session, model_file):
        create_wall(loaded_session)
        loaded_session.ifc_load(model_file)
        with pytest.raises(IfcSessionError, match="Nothing to undo"):
            loaded_session.ifc_undo()

    def test_no_model(self, session):
        with pytest.raises(IfcSessionError, match="No model loaded"):
            session.ifc_undo()


def half_done(ifc_class):
    """Stand in for run_api: change the model, then fail."""

    def run_api(model, *args, **kwargs):
        ifcopenshell.api.root.create_entity(model, ifc_class=ifc_class, name="Half")
        return {"ok": False, "error": "failed halfway"}

    return run_api


class TestFailedEditsChangeNothing:
    def test_failure_result_is_rolled_back(self, loaded_session):
        with patch("ifcmcp.core.run_api", half_done("IfcWall")):
            assert loaded_session.ifc_edit("root.create_entity", "{}")["ok"] is False
        assert walls(loaded_session) == ["Wall001"]

    def test_exception_is_rolled_back(self, loaded_session):
        def run_api(model, *args, **kwargs):
            ifcopenshell.api.root.create_entity(model, ifc_class="IfcWall", name="Half")
            raise RuntimeError("boom")

        with patch("ifcmcp.core.run_api", run_api), pytest.raises(RuntimeError):
            loaded_session.ifc_edit("root.create_entity", "{}")
        assert walls(loaded_session) == ["Wall001"]

    def test_a_failure_is_not_an_undo_step(self, loaded_session):
        create_wall(loaded_session, "A")
        assert loaded_session.ifc_edit("nosuchmodule.nosuchfunction", "{}")["ok"] is False
        loaded_session.ifc_undo()
        assert walls(loaded_session) == ["Wall001"]

    def test_a_call_that_changes_nothing_is_not_an_undo_step(self, loaded_session):
        with patch("ifcmcp.core.run_api", return_value={"ok": True, "result": None}):
            loaded_session.ifc_edit("root.create_entity", "{}")
        with pytest.raises(IfcSessionError, match="Nothing to undo"):
            loaded_session.ifc_undo()


class TestShapeIsUndoable:
    def test_undo_a_shape(self, loaded_session):
        before = len(list(loaded_session.model))
        result = loaded_session.ifc_shape("rectangle", json.dumps({"size": [1.0, 2.0]}))
        assert result["ok"], result
        assert len(list(loaded_session.model)) > before
        loaded_session.ifc_undo()
        assert len(list(loaded_session.model)) == before
