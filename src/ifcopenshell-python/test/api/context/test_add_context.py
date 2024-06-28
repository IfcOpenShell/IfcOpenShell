# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
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

import test.bootstrap
import ifcopenshell.api.context


class TestAddContext(test.bootstrap.IFC4):
    def test_adding_a_3d_context(self):
        self.file.createIfcProject()
        context = ifcopenshell.api.context.add_context(self.file, context_type="Model")
        assert context.ContextType == "Model"
        assert context.is_a() == "IfcGeometricRepresentationContext"
        assert context.WorldCoordinateSystem.is_a() == "IfcAxis2Placement3D"
        assert context.WorldCoordinateSystem.Location.Coordinates == (0, 0, 0)
        assert context.WorldCoordinateSystem.Axis.DirectionRatios == (0, 0, 1)
        assert context.WorldCoordinateSystem.RefDirection.DirectionRatios == (1, 0, 0)
        assert context.CoordinateSpaceDimension == 3

    def test_adding_a_2d_context(self):
        self.file.createIfcProject()
        context = ifcopenshell.api.context.add_context(self.file, context_type="Plan")
        assert context.ContextType == "Plan"
        assert context.is_a() == "IfcGeometricRepresentationContext"
        assert context.WorldCoordinateSystem.is_a() == "IfcAxis2Placement2D"
        assert context.WorldCoordinateSystem.Location.Coordinates == (0, 0)
        assert context.WorldCoordinateSystem.RefDirection.DirectionRatios == (1, 0)
        assert context.CoordinateSpaceDimension == 2

    def test_defaulting_to_3d_with_an_unknown_context_type(self):
        self.file.createIfcProject()
        context = ifcopenshell.api.context.add_context(self.file)
        assert context.ContextType is None
        assert context.is_a() == "IfcGeometricRepresentationContext"
        assert context.WorldCoordinateSystem.is_a() == "IfcAxis2Placement3D"
        assert context.WorldCoordinateSystem.Location.Coordinates == (0, 0, 0)
        assert context.WorldCoordinateSystem.Axis.DirectionRatios == (0, 0, 1)
        assert context.WorldCoordinateSystem.RefDirection.DirectionRatios == (1, 0, 0)
        assert context.CoordinateSpaceDimension == 3

    def test_adding_a_subcontext(self):
        self.test_adding_a_3d_context()
        context = self.file.by_type("IfcGeometricRepresentationContext")[0]
        subcontext = ifcopenshell.api.context.add_context(self.file, parent=context, target_view="NOTDEFINED")
        assert subcontext.is_a("IfcGeometricRepresentationSubContext")
        assert subcontext.TargetView == "NOTDEFINED"

    def test_adding_a_subcontext_with_an_optional_identifier_specified(self):
        self.test_adding_a_3d_context()
        context = self.file.by_type("IfcGeometricRepresentationContext")[0]
        subcontext = ifcopenshell.api.context.add_context(
            self.file, parent=context, target_view="NOTDEFINED", context_identifier="Body"
        )
        assert subcontext.is_a("IfcGeometricRepresentationSubContext")
        assert subcontext.TargetView == "NOTDEFINED"
        assert subcontext.ContextIdentifier == "Body"

    def test_adding_two_contexts(self):
        self.test_adding_a_3d_context()
        self.test_adding_a_2d_context()
        project = self.file.by_type("IfcProject")[0]
        assert len(project.RepresentationContexts) == 2


class TestAddContextIFC2X3(test.bootstrap.IFC2X3, TestAddContext):
    pass
