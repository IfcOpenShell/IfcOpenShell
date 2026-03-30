# This file was generated with the assistance of an AI coding tool.
import json

import pytest

from ifcmcp.core import IfcSessionError


class TestShapeList:
    def test_returns_list(self, loaded_session):
        result = loaded_session.ifc_shape_list()
        assert isinstance(result, list)
        assert len(result) > 0

    def test_has_expected_methods(self, loaded_session):
        result = loaded_session.ifc_shape_list()
        names = [m["method"] for m in result]
        assert "polyline" in names
        assert "rectangle" in names
        assert "extrude" in names
        assert "profile" in names
        assert "get_representation" in names

    def test_well_documented_methods_have_descriptions(self, loaded_session):
        result = loaded_session.ifc_shape_list()
        by_name = {m["method"]: m for m in result}
        # These methods have detailed docstrings
        for name in ("polyline", "extrude", "rectangle", "profile", "get_representation"):
            assert by_name[name]["description"], f"'{name}' has no description"

    def test_no_private_methods(self, loaded_session):
        result = loaded_session.ifc_shape_list()
        assert not any(m["method"].startswith("_") for m in result)

    def test_does_not_require_model(self, session):
        # ifc_shape_list is pure introspection — no model needed
        result = session.ifc_shape_list()
        assert isinstance(result, list)


class TestShapeDocs:
    def test_extrude_docs(self, loaded_session):
        result = loaded_session.ifc_shape_docs("extrude")
        assert result["method"] == "extrude"
        assert result["description"]
        assert "params" in result
        param_names = [p["name"] for p in result["params"]]
        assert "profile_or_curve" in param_names
        assert "magnitude" in param_names

    def test_has_return_type(self, loaded_session):
        result = loaded_session.ifc_shape_docs("rectangle")
        assert "return_type" in result

    def test_has_param_descriptions(self, loaded_session):
        result = loaded_session.ifc_shape_docs("polyline")
        params_with_desc = [p for p in result["params"] if "description" in p]
        assert len(params_with_desc) > 0

    def test_unknown_method(self, loaded_session):
        with pytest.raises(ValueError, match="no method"):
            loaded_session.ifc_shape_docs("nonexistent_method")

    def test_private_method_rejected(self, loaded_session):
        with pytest.raises(ValueError):
            loaded_session.ifc_shape_docs("__init__")

    def test_does_not_require_model(self, session):
        result = session.ifc_shape_docs("circle")
        assert result["method"] == "circle"


class TestShapeExecute:
    def test_rectangle(self, loaded_session):
        result = loaded_session.ifc_shape("rectangle", json.dumps({"size": [4.0, 0.2]}))
        assert result["ok"] is True
        assert result["result"]["type"] == "IfcIndexedPolyCurve"

    def test_circle(self, loaded_session):
        result = loaded_session.ifc_shape("circle", json.dumps({"center": [0.0, 0.0], "radius": 0.5}))
        assert result["ok"] is True
        assert result["result"]["type"] == "IfcCircle"

    def test_extrude_chained_from_rectangle(self, loaded_session):
        rect = loaded_session.ifc_shape("rectangle", json.dumps({"size": [4.0, 0.2]}))
        rect_id = rect["result"]["id"]
        result = loaded_session.ifc_shape("extrude", json.dumps({"profile_or_curve": rect_id, "magnitude": 3.0}))
        assert result["ok"] is True
        assert result["result"]["type"] == "IfcExtrudedAreaSolid"

    def test_entity_id_as_integer(self, loaded_session):
        """Entity IDs should be accepted as plain integers (from JSON)."""
        rect = loaded_session.ifc_shape("rectangle", json.dumps({"size": [1.0, 1.0]}))
        rect_id = rect["result"]["id"]
        # Pass as int, not string
        result = loaded_session.ifc_shape("extrude", json.dumps({"profile_or_curve": rect_id, "magnitude": 1.0}))
        assert result["ok"] is True

    def test_rotate_2d_point_returns_list(self, loaded_session):
        """Methods returning numpy arrays should give back plain lists."""
        result = loaded_session.ifc_shape(
            "rotate_2d_point", json.dumps({"point_2d": [1.0, 0.0], "angle": 90.0, "counter_clockwise": True})
        )
        assert result["ok"] is True
        assert isinstance(result["result"], list)
        assert len(result["result"]) == 2

    def test_set_polyline_coords_returns_none(self, loaded_session):
        """In-place methods that return None should give ok=True, result=None."""
        rect = loaded_session.ifc_shape("rectangle", json.dumps({"size": [2.0, 2.0]}))
        rect_id = rect["result"]["id"]
        result = loaded_session.ifc_shape(
            "set_polyline_coords",
            json.dumps({"polyline": rect_id, "coords": [[0.0, 0.0], [3.0, 0.0], [3.0, 3.0], [0.0, 3.0]]}),
        )
        assert result["ok"] is True
        assert result["result"] is None

    def test_unknown_method(self, loaded_session):
        result = loaded_session.ifc_shape("nonexistent_method", "{}")
        assert result["ok"] is False
        assert "error" in result

    def test_private_method_rejected(self, loaded_session):
        with pytest.raises(IfcSessionError):
            loaded_session.ifc_shape("__init__", "{}")

    def test_no_model_raises(self, session):
        with pytest.raises(IfcSessionError, match="No model loaded"):
            session.ifc_shape("rectangle", "{}")

    def test_params_as_dict(self, loaded_session):
        """params can be passed as a dict (not just a JSON string)."""
        result = loaded_session.ifc_shape("rectangle", {"size": [2.0, 1.0]})
        assert result["ok"] is True

    def test_error_on_bad_params(self, loaded_session):
        """Bad parameters should give ok=False with an error message."""
        result = loaded_session.ifc_shape("extrude", json.dumps({"profile_or_curve": 999999, "magnitude": 1.0}))
        assert result["ok"] is False
        assert "error" in result
