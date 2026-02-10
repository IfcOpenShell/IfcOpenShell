import pytest

import ifcmcp.server as server_mod
from ifcmcp.server import ifc_load, ifc_save


class TestLoad:
    def test_load_file(self, model_file):
        result = ifc_load(model_file)
        assert "IFC4" in result
        assert server_mod._model is not None
        assert server_mod._model_path == model_file

    def test_load_sets_entity_count(self, model_file):
        result = ifc_load(model_file)
        assert "entities" in result

    def test_load_nonexistent_file(self):
        with pytest.raises(Exception):
            ifc_load("/nonexistent/path/model.ifc")


class TestSave:
    def test_save_no_model(self):
        with pytest.raises(ValueError, match="No model loaded"):
            ifc_save()

    def test_save_overwrites_original(self, model_file):
        ifc_load(model_file)
        result = ifc_save()
        assert model_file in result

    def test_save_to_new_path(self, model_file, tmp_path):
        ifc_load(model_file)
        new_path = str(tmp_path / "output.ifc")
        result = ifc_save(new_path)
        assert new_path in result
        import ifcopenshell

        reloaded = ifcopenshell.open(new_path)
        assert reloaded.schema == "IFC4"

    def test_save_no_path_no_original(self, loaded_model):
        with pytest.raises(ValueError, match="No path specified"):
            ifc_save()
