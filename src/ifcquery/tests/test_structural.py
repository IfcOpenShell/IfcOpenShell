# This file was generated with the assistance of an AI coding tool.
from __future__ import annotations

from ifcquery.structural import structural


def _only(result):
    assert len(result) == 1
    return result[0]


class TestStructural:
    def test_no_analysis_model(self, model):
        assert structural(model) == []

    def test_analysis_model(self, structural_model):
        analysis = _only(structural(structural_model))
        assert analysis["type"] == "IfcStructuralAnalysisModel"
        assert analysis["name"] == "Analysis"
        assert analysis["predefined_type"] == "LOADING_3D"
        assert analysis["id"] == structural_model.by_type("IfcStructuralAnalysisModel")[0].id()

    def test_members(self, structural_model):
        member = _only(_only(structural(structural_model))["members"])
        assert member["name"] == "Cantilever"
        assert member["predefined_type"] == "RIGID_JOINED_MEMBER"
        assert [c["name"] for c in member["connections"]] == ["Root", "Tip"]
        assert member["building_elements"] == [
            {"id": structural_model.by_type("IfcBeam")[0].id(), "type": "IfcBeam", "name": "Beam"}
        ]
        assert member["activities"] == []

    def test_connections(self, structural_model):
        root, tip = _only(structural(structural_model))["connections"]
        assert root["name"] == "Root"
        assert root["applied_condition"]["type"] == "IfcBoundaryNodeCondition"
        assert root["applied_condition"]["name"] == "Fixed"
        assert root["applied_condition"]["values"] == {"TranslationalStiffnessZ": True, "RotationalStiffnessY": 1000.0}
        assert [m["name"] for m in root["members"]] == ["Cantilever"]
        assert tip["applied_condition"] is None
        assert [a["type"] for a in tip["activities"]] == ["IfcStructuralPointAction"]

    def test_load_cases_are_those_of_the_model(self, structural_model):
        case = _only(_only(structural(structural_model))["load_cases"])
        assert case["name"] == "Live"
        assert case["action_type"] == "VARIABLE_Q"
        assert case["action_source"] == "LIVE_LOAD_Q"
        assert case["self_weight_coefficients"] == [0.0, 0.0, 0.0]

    def test_activities_of_a_load_case_include_those_of_its_load_groups(self, structural_model):
        activity = _only(_only(_only(structural(structural_model))["load_cases"])["activities"])
        assert activity["type"] == "IfcStructuralPointAction"
        assert activity["global_or_local"] == "GLOBAL_COORDS"
        assert activity["item"]["name"] == "Tip"
        assert activity["load"]["type"] == "IfcStructuralLoadSingleForce"
        assert activity["load"]["name"] == "P"
        assert activity["load"]["values"] == {"ForceZ": -1000.0}

    def test_load_combination_factors(self, structural_model):
        combination = _only(_only(structural(structural_model))["load_combinations"])
        assert combination["name"] == "ULS"
        assert combination["coefficient"] == 2.0
        assert [(c["name"], c["factor"]) for c in combination["load_cases"]] == [("Live", 3.0)]

    def test_depth_1_counts_the_lists(self, structural_model):
        analysis = _only(structural(structural_model, max_depth=1))
        assert analysis["members"] == {"truncated": True, "count": 1}
        assert analysis["connections"] == {"truncated": True, "count": 2}
        assert analysis["load_cases"] == {"truncated": True, "count": 1}
        assert analysis["load_combinations"] == {"truncated": True, "count": 1}

    def test_depth_2_counts_the_lists_of_each_entry(self, structural_model):
        analysis = _only(structural(structural_model, max_depth=2))
        member = _only(analysis["members"])
        assert member["connections"] == {"truncated": True, "count": 2}
        assert member["activities"] == []
        assert _only(analysis["load_cases"])["activities"] == {"truncated": True, "count": 1}
        assert _only(analysis["load_combinations"])["load_cases"] == {"truncated": True, "count": 1}
