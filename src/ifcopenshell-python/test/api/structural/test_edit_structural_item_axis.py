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

import ifcopenshell.api.root
import ifcopenshell.api.structural
import test.bootstrap


class TestEditStructuralItemAxis(test.bootstrap.IFC4):
    def test_setting_the_axis_of_a_new_curve_member(self):
        # root.create_entity leaves the mandatory Axis unset, as Bonsai's new members have it
        member = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcStructuralCurveMember")
        assert member.Axis is None
        ifcopenshell.api.structural.edit_structural_item_axis(self.file, structural_item=member, axis=(0.0, 1.0, 0.0))
        assert np.allclose(member.Axis.DirectionRatios, (0.0, 1.0, 0.0))

    def test_setting_the_axis_of_a_new_curve_connection(self):
        connection = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcStructuralCurveConnection")
        assert connection.Axis is None
        ifcopenshell.api.structural.edit_structural_item_axis(self.file, structural_item=connection)
        assert np.allclose(connection.Axis.DirectionRatios, (0.0, 0.0, 1.0))

    def test_replacing_an_axis_and_removing_the_old_direction(self):
        member = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcStructuralCurveMember")
        member.Axis = self.file.createIfcDirection((0.0, 0.0, 1.0))
        ifcopenshell.api.structural.edit_structural_item_axis(self.file, structural_item=member, axis=(0.0, 1.0, 0.0))
        assert np.allclose(member.Axis.DirectionRatios, (0.0, 1.0, 0.0))
        assert self.file.by_type("IfcDirection") == (member.Axis,)

    def test_keeping_an_old_direction_used_elsewhere(self):
        direction = self.file.createIfcDirection((0.0, 0.0, 1.0))
        member = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcStructuralCurveMember")
        other = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcStructuralCurveMember")
        member.Axis = direction
        other.Axis = direction
        ifcopenshell.api.structural.edit_structural_item_axis(self.file, structural_item=member, axis=(0.0, 1.0, 0.0))
        assert other.Axis == direction
