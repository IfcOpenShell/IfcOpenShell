# This file was generated with the assistance of an AI coding tool.

import ifcopenshell
import pytest

from ifc2ca import Ifc2CA


@pytest.fixture
def converter(tmp_path):
    path = tmp_path / "model.ifc"
    ifcopenshell.file(schema="IFC4").write(path)
    return Ifc2CA(path)


class TestParseAppliedCondition:
    def test_vertex_with_unset_rotational_stiffness(self, converter):
        condition = converter.file.create_entity(
            "IfcBoundaryNodeCondition",
            TranslationalStiffnessX=converter.file.create_entity("IfcLinearStiffnessMeasure", 1000.0),
            TranslationalStiffnessY=converter.file.create_entity("IfcBoolean", True),
        )
        assert converter.parse_applied_condition(condition, "Vertex") == {
            "dx": 1000.0,
            "dy": True,
            "dz": None,
            "drx": None,
            "dry": None,
            "drz": None,
        }

    def test_edge_with_unset_stiffness(self, converter):
        condition = converter.file.create_entity(
            "IfcBoundaryEdgeCondition",
            TranslationalStiffnessByLengthX=converter.file.create_entity(
                "IfcModulusOfLinearSubgradeReactionMeasure", 50.0
            ),
        )
        assert converter.parse_applied_condition(condition, "Edge") == {
            "dx": 50.0,
            "dy": None,
            "dz": None,
            "drx": None,
            "dry": None,
            "drz": None,
        }

    def test_face_with_unset_stiffness(self, converter):
        condition = converter.file.create_entity(
            "IfcBoundaryFaceCondition",
            TranslationalStiffnessByAreaZ=converter.file.create_entity("IfcModulusOfSubgradeReactionMeasure", 7.0),
        )
        assert converter.parse_applied_condition(condition, "Face") == {"dx": None, "dy": None, "dz": 7.0}
