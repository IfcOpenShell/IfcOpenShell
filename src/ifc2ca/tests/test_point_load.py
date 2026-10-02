# This file was generated with the assistance of an AI coding tool.

import ifcopenshell
import numpy as np
import pytest

from ifc2ca import Ifc2CA


@pytest.fixture
def converter(tmp_path):
    path = tmp_path / "model.ifc"
    ifcopenshell.file(schema="IFC4").write(path)
    return Ifc2CA(path)


def add_point_action(model, global_or_local):
    load_case = model.create_entity(
        "IfcStructuralLoadCase", GlobalId=ifcopenshell.guid.new(), PredefinedType="LOAD_CASE", Coefficient=1.0
    )
    load_group = model.create_entity(
        "IfcStructuralLoadGroup", GlobalId=ifcopenshell.guid.new(), PredefinedType="LOAD_GROUP"
    )
    action = model.create_entity(
        "IfcStructuralPointAction",
        GlobalId=ifcopenshell.guid.new(),
        AppliedLoad=model.create_entity("IfcStructuralLoadSingleForce", ForceX=100.0),
        GlobalOrLocal=global_or_local,
    )
    model.create_entity(
        "IfcRelAssignsToGroup",
        GlobalId=ifcopenshell.guid.new(),
        RelatedObjects=[action],
        RelatingGroup=load_group,
    )
    model.create_entity(
        "IfcRelAssignsToGroup",
        GlobalId=ifcopenshell.guid.new(),
        RelatedObjects=[load_group],
        RelatingGroup=load_case,
    )
    return action, load_case


def make_data():
    return {
        "actions": [],
        "loadGroups": [],
        "loadsLC": {key: np.zeros(1) for key in ("FX", "FY", "FZ", "MX", "MY", "MZ")},
        "loadsCOMB": {key: None for key in ("FX", "FY", "FZ", "MX", "MY", "MZ")},
    }


class TestAddActionLoads:
    def test_global_point_load_on_vertex(self, converter):
        action, load_case = add_point_action(converter.file, "GLOBAL_COORDS")
        element = {"geometry_type": "Vertex", "orientation": np.eye(3)}
        data = make_data()
        converter.add_action_loads(element, action, data, [load_case])
        assert data["loadsLC"]["FX"] == pytest.approx([100.0])
        assert data["loadsLC"]["FY"] == pytest.approx([0.0])

    def test_local_point_load_on_edge(self, converter):
        action, load_case = add_point_action(converter.file, "LOCAL_COORDS")
        element = {"geometry_type": "Edge", "orientation": np.eye(3)}
        data = make_data()
        converter.add_action_loads(element, action, data, [load_case])
        assert data["loadsLC"]["FX"] == pytest.approx([100.0])
        assert data["loadsLC"]["FY"] == pytest.approx([0.0])
