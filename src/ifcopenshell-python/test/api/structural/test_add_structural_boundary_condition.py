# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2026 Dion Moult <dion@thinkmoult.com>
#
# This file is part of IfcOpenShell.
#
# IfcOpenShell is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcOpenShell is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcOpenShell.  If not, see <http://www.gnu.org/licenses/>.

import pytest

import ifcopenshell.api.root
import ifcopenshell.api.structural
import test.bootstrap


class TestAddStructuralBoundaryConditionIFC4(test.bootstrap.IFC4):
    def test_add_orphan_boundary_node_condition_initializes_stiffnesses_to_free(self):
        condition = ifcopenshell.api.structural.add_structural_boundary_condition(
            self.file, name="Pin", ifc_class="IfcBoundaryNodeCondition"
        )
        assert condition.Name == "Pin"
        assert condition.TranslationalStiffnessX.wrappedValue is False
        assert condition.TranslationalStiffnessY.wrappedValue is False
        assert condition.TranslationalStiffnessZ.wrappedValue is False
        assert condition.RotationalStiffnessX.wrappedValue is False
        assert condition.RotationalStiffnessY.wrappedValue is False
        assert condition.RotationalStiffnessZ.wrappedValue is False

    def test_add_point_connection_boundary_condition(self):
        conn = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcStructuralPointConnection")
        condition = ifcopenshell.api.structural.add_structural_boundary_condition(
            self.file, name="NodeSupport", connection=conn
        )
        assert condition.is_a("IfcBoundaryNodeCondition")
        assert conn.AppliedCondition == condition
        assert condition.TranslationalStiffnessX.wrappedValue is False
        assert condition.RotationalStiffnessZ.wrappedValue is False

    def test_add_curve_connection_boundary_condition(self):
        conn = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcStructuralCurveConnection")
        condition = ifcopenshell.api.structural.add_structural_boundary_condition(
            self.file, name="EdgeSupport", connection=conn
        )
        assert condition.is_a("IfcBoundaryEdgeCondition")
        assert conn.AppliedCondition == condition
        assert condition.TranslationalStiffnessByLengthX.wrappedValue is False
        assert condition.RotationalStiffnessByLengthZ.wrappedValue is False

    def test_add_surface_connection_boundary_condition(self):
        conn = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcStructuralSurfaceConnection")
        condition = ifcopenshell.api.structural.add_structural_boundary_condition(
            self.file, name="FaceSupport", connection=conn
        )
        assert condition.is_a("IfcBoundaryFaceCondition")
        assert conn.AppliedCondition == condition
        assert condition.TranslationalStiffnessByAreaX.wrappedValue is False
        assert condition.TranslationalStiffnessByAreaZ.wrappedValue is False


class TestAddStructuralBoundaryConditionIFC2X3(test.bootstrap.IFC2X3):
    def test_add_orphan_boundary_node_condition_ifc2x3(self):
        condition = ifcopenshell.api.structural.add_structural_boundary_condition(
            self.file, name="Pin", ifc_class="IfcBoundaryNodeCondition"
        )
        assert condition.Name == "Pin"
        assert condition.LinearStiffnessX == 0.0
        assert condition.LinearStiffnessY == 0.0
        assert condition.LinearStiffnessZ == 0.0
        assert condition.RotationalStiffnessX == 0.0
        assert condition.RotationalStiffnessY == 0.0
        assert condition.RotationalStiffnessZ == 0.0


class TestAddStructuralBoundaryConditionSupportIFC4(test.bootstrap.IFC4):
    def stiffnesses(self, condition):
        return {
            name: value.wrappedValue
            for name, value in condition.get_info().items()
            if "Stiffness" in name and value is not None
        }

    def test_a_pinned_point_holds_displacements_only(self):
        conn = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcStructuralPointConnection")
        condition = ifcopenshell.api.structural.add_structural_boundary_condition(
            self.file, connection=conn, support="PINNED"
        )
        stiffnesses = self.stiffnesses(condition)
        assert len(stiffnesses) == 6
        assert all(v is True for k, v in stiffnesses.items() if k.startswith("Translational"))
        assert all(v is False for k, v in stiffnesses.items() if k.startswith("Rotational"))

    def test_a_fixed_edge_holds_rotations_as_well(self):
        conn = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcStructuralCurveConnection")
        condition = ifcopenshell.api.structural.add_structural_boundary_condition(
            self.file, connection=conn, support="FIXED"
        )
        stiffnesses = self.stiffnesses(condition)
        assert len(stiffnesses) == 6
        assert all(stiffnesses.values())

    def test_a_fixed_face_holds_its_displacements(self):
        conn = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcStructuralSurfaceConnection")
        condition = ifcopenshell.api.structural.add_structural_boundary_condition(
            self.file, connection=conn, support="FIXED"
        )
        assert self.stiffnesses(condition) == {f"TranslationalStiffnessByArea{a}": True for a in "XYZ"}

    def test_warping_is_left_free(self):
        condition = ifcopenshell.api.structural.add_structural_boundary_condition(
            self.file, ifc_class="IfcBoundaryNodeConditionWarping", support="FIXED"
        )
        assert condition.RotationalStiffnessZ.wrappedValue is True
        assert condition.WarpingStiffness.wrappedValue is False

    def test_an_unknown_support_is_refused(self):
        with pytest.raises(ValueError):
            ifcopenshell.api.structural.add_structural_boundary_condition(self.file, support="ROLLER")
        assert not self.file.by_type("IfcBoundaryCondition")


class TestAddStructuralBoundaryConditionSupportIFC2X3(test.bootstrap.IFC2X3):
    def test_a_rigid_support_cannot_be_said(self):
        conn = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcStructuralSurfaceConnection")
        with pytest.raises(ValueError, match="IFC2X3"):
            ifcopenshell.api.structural.add_structural_boundary_condition(self.file, connection=conn, support="PINNED")
        assert not self.file.by_type("IfcBoundaryCondition")
        assert conn.AppliedCondition is None
