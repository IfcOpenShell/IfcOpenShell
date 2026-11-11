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
