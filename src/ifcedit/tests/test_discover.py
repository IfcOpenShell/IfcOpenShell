# This file was generated with the assistance of an AI coding tool.
from ifcedit.discover import function_docs, list_functions, list_modules


class TestListModules:
    def test_returns_list(self):
        result = list_modules()
        assert isinstance(result, list)
        assert len(result) > 0

    def test_module_structure(self):
        result = list_modules()
        for entry in result:
            assert "module" in entry
            assert "description" in entry
            assert "functions" in entry
            assert "count" in entry
            assert isinstance(entry["functions"], list)
            assert entry["count"] == len(entry["functions"])

    def test_known_modules_present(self):
        result = list_modules()
        module_names = [m["module"] for m in result]
        for expected in ("root", "spatial", "pset", "aggregate", "unit"):
            assert expected in module_names

    def test_root_module_has_functions(self):
        result = list_modules()
        root = next(m for m in result if m["module"] == "root")
        assert "create_entity" in root["functions"]
        assert root["count"] >= 3


class TestListFunctions:
    def test_root_functions(self):
        result = list_functions("root")
        assert isinstance(result, list)
        names = [f["name"] for f in result]
        assert "create_entity" in names

    def test_function_structure(self):
        result = list_functions("root")
        for fn in result:
            assert "name" in fn
            assert "description" in fn
            assert "params" in fn

    def test_create_entity_params(self):
        result = list_functions("root")
        create = next(f for f in result if f["name"] == "create_entity")
        param_names = [p["name"] for p in create["params"]]
        assert "ifc_class" in param_names
        assert "name" in param_names

    def test_pset_functions(self):
        result = list_functions("pset")
        names = [f["name"] for f in result]
        assert "add_pset" in names
        assert "edit_pset" in names


class TestFunctionDocs:
    def test_create_entity_docs(self):
        result = function_docs("root", "create_entity")
        assert result["module"] == "root"
        assert result["function"] == "create_entity"
        assert result["description"]
        assert isinstance(result["params"], list)
        assert len(result["params"]) > 0

    def test_params_have_types(self):
        result = function_docs("root", "create_entity")
        for param in result["params"]:
            assert "name" in param
            assert "type" in param

    def test_params_have_descriptions(self):
        result = function_docs("root", "create_entity")
        ifc_class = next(p for p in result["params"] if p["name"] == "ifc_class")
        assert "description" in ifc_class
        assert len(ifc_class["description"]) > 0

    def test_return_type(self):
        result = function_docs("root", "create_entity")
        assert "return_type" in result

    def test_assign_container_docs(self):
        result = function_docs("spatial", "assign_container")
        assert result["module"] == "spatial"
        param_names = [p["name"] for p in result["params"]]
        assert "products" in param_names
        assert "relating_structure" in param_names

    def test_unknown_function_raises(self):
        import pytest

        with pytest.raises(ValueError, match="not found"):
            function_docs("root", "nonexistent_function")

    def test_edit_pset_docs(self):
        result = function_docs("pset", "edit_pset")
        param_names = [p["name"] for p in result["params"]]
        assert "pset" in param_names
        assert "properties" in param_names
