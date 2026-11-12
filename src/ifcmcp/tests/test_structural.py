# This file was generated with the assistance of an AI coding tool.
import ifcopenshell.api.group
import ifcopenshell.api.root
import ifcopenshell.api.structural
import pytest

from ifcmcp.core import IfcSession, IfcSessionError
from ifcmcp.server import READ_ONLY_TOOLS, build_server


@pytest.fixture
def structural_session(model):
    """The model fixture with an analysis model: a member, a support, a load
    case with one action and a combination of it."""
    analysis_model = ifcopenshell.api.structural.add_structural_analysis_model(model)
    analysis_model.Name = "Frame"
    member = ifcopenshell.api.root.create_entity(
        model, ifc_class="IfcStructuralCurveMember", predefined_type="RIGID_JOINED_MEMBER", name="Beam"
    )
    support = ifcopenshell.api.root.create_entity(model, ifc_class="IfcStructuralPointConnection", name="Support")
    ifcopenshell.api.structural.add_structural_member_connection(
        model, relating_structural_member=member, related_structural_connection=support
    )
    ifcopenshell.api.structural.add_structural_boundary_condition(model, connection=support)
    ifcopenshell.api.structural.assign_structural_analysis_model(
        model, products=[member, support], structural_analysis_model=analysis_model
    )
    load = ifcopenshell.api.structural.add_structural_load(model, name="Snow", ifc_class="IfcStructuralLoadLinearForce")
    action = ifcopenshell.api.structural.add_structural_activity(
        model, applied_load=load, structural_member=member, ifc_class="IfcStructuralCurveAction"
    )
    case = ifcopenshell.api.structural.add_structural_load_case(model, name="Snow")
    ifcopenshell.api.group.assign_group(model, products=[action], group=case)
    combination = ifcopenshell.api.structural.add_structural_load_combination(model, name="ULS")
    ifcopenshell.api.structural.assign_structural_load_combination(
        model, load_case=case, load_combination=combination, factor=1.5
    )
    analysis_model.LoadedBy = [combination]
    session = IfcSession()
    session.model = model
    return session


class TestStructural:
    def test_no_model(self, session):
        with pytest.raises(IfcSessionError):
            session.ifc_structural()

    def test_no_analysis_model(self, loaded_session):
        assert loaded_session.ifc_structural() == []

    def test_analysis_model(self, structural_session):
        (analysis_model,) = structural_session.ifc_structural()
        assert analysis_model["name"] == "Frame"
        assert [m["name"] for m in analysis_model["members"]] == ["Beam"]
        assert [c["name"] for c in analysis_model["connections"]] == ["Support"]
        (case,) = analysis_model["load_cases"]
        assert case["name"] == "Snow"
        (combination,) = analysis_model["load_combinations"]
        assert combination["name"] == "ULS"
        assert "1.5" in str(combination)

    def test_max_depth(self, structural_session):
        (analysis_model,) = structural_session.ifc_structural(max_depth=1)
        assert analysis_model["members"] == {"truncated": True, "count": 1}

    def test_dispatch(self, structural_session):
        """The embedded (Pyodide) session calls tools by name."""
        (analysis_model,) = structural_session.dispatch("ifc_structural", {"max_depth": 2})
        assert analysis_model["name"] == "Frame"

    def test_offered_to_the_embedded_session(self, session):
        names = {tool["name"] for tool in session.openai_tools()}
        assert "ifc_structural" in names


class TestServer:
    def test_registered_and_read_only(self):
        tools = {t.name: t for t in build_server()._tool_manager.list_tools()}
        assert "ifc_structural" in tools
        assert "ifc_structural" in READ_ONLY_TOOLS
        assert tools["ifc_structural"].description.strip()
