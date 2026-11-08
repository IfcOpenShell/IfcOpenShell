# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2026 Bruno Postle <bruno@postle.net>
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
# This file was generated with the assistance of an AI coding tool.

import numpy as np

import ifcopenshell.api.context
import ifcopenshell.api.geometry
import ifcopenshell.api.root
import ifcopenshell.api.structural
import test.bootstrap
from ifcopenshell.util.shape_builder import ShapeBuilder


class TestEditStructuralConnectionCs(test.bootstrap.IFC4):
    def make_point_connection(self, coordinates):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        model = ifcopenshell.api.context.add_context(self.file, context_type="Model")
        context = ifcopenshell.api.context.add_context(
            self.file, context_type="Model", context_identifier="Reference", target_view="GRAPH_VIEW", parent=model
        )
        connection = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcStructuralPointConnection")
        builder = ShapeBuilder(self.file)
        representation = builder.get_representation(context, [builder.vertex(coordinates)])
        ifcopenshell.api.geometry.assign_representation(self.file, product=connection, representation=representation)
        return connection

    def test_setting_the_axes(self):
        connection = self.make_point_connection((0.0, 0.0, 0.0))
        ifcopenshell.api.structural.edit_structural_connection_cs(
            self.file, structural_item=connection, axis=(0.0, 1.0, 0.0), ref_direction=(0.0, 0.0, 1.0)
        )
        ccs = connection.ConditionCoordinateSystem
        assert np.allclose(ccs.Axis.DirectionRatios, (0.0, 1.0, 0.0))
        assert np.allclose(ccs.RefDirection.DirectionRatios, (0.0, 0.0, 1.0))

    def test_placing_a_new_coordinate_system_at_the_reference_point(self):
        # IfcStructuralPointConnection.ConditionCoordinateSystem: the implied placement is at the
        # coordinates of the reference point, in the axes of the ObjectPlacement
        connection = self.make_point_connection((1.0, 2.0, 3.0))
        ifcopenshell.api.structural.edit_structural_connection_cs(self.file, structural_item=connection)
        ccs = connection.ConditionCoordinateSystem
        assert np.allclose(ccs.Location.Coordinates, (1.0, 2.0, 3.0))
