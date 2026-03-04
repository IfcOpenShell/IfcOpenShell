# This file was generated with the assistance of an AI coding tool.
import ifcopenshell
import pytest

from ifcmcp.core import IfcSession, IfcSessionError


class TestLoad:
    def test_load_file(self, session, model_file):
        result = session.ifc_load(model_file)
        assert "IFC4" in result
        assert session.model is not None
        assert session.model_path == model_file

    def test_load_sets_entity_count(self, session, model_file):
        result = session.ifc_load(model_file)
        assert "entities" in result

    def test_load_nonexistent_file(self, session):
        with pytest.raises(Exception):
            session.ifc_load("/nonexistent/path/model.ifc")


class TestSave:
    def test_save_no_model(self, session):
        with pytest.raises(IfcSessionError, match="No model loaded"):
            session.ifc_save()

    def test_save_overwrites_original(self, session, model_file):
        session.ifc_load(model_file)
        result = session.ifc_save()
        assert model_file in result

    def test_save_to_new_path(self, session, model_file, tmp_path):
        session.ifc_load(model_file)
        new_path = str(tmp_path / "output.ifc")
        result = session.ifc_save(new_path)
        assert new_path in result
        reloaded = ifcopenshell.open(new_path)
        assert reloaded.schema == "IFC4"

    def test_save_no_path_no_original(self, loaded_session):
        with pytest.raises(IfcSessionError, match="No path specified"):
            loaded_session.ifc_save()
