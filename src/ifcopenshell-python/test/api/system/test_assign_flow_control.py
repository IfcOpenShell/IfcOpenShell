# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2022 Dion Moult <dion@thinkmoult.com>
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
import ifcopenshell.api.system


class TestAssignFlowControl(test.bootstrap.IFC4):
    def test_run(self):
        flow_element = self.file.createIfcFlowSegment()
        flow_control = self.file.create_entity("IfcDistributionControlElement")

        # simple assignment
        relation = ifcopenshell.api.system.assign_flow_control(
            self.file,
            related_flow_control=flow_control,
            relating_flow_element=flow_element,
        )
        assert len(self.file.by_type("IfcRelFlowControlElements")) == 1
        assert relation.RelatingFlowElement == flow_element
        assert relation.RelatedControlElements == (flow_control,)

        # trying to establish existing relationship
        relation0 = ifcopenshell.api.system.assign_flow_control(
            self.file,
            related_flow_control=flow_control,
            relating_flow_element=flow_element,
        )
        assert relation == relation0

        # assigning same control to another object
        flow_element1 = self.file.createIfcFlowSegment()
        relation = ifcopenshell.api.system.assign_flow_control(
            self.file,
            related_flow_control=flow_control,
            relating_flow_element=flow_element1,
        )
        assert relation is None

        # assigning another control to the same object
        flow_control1 = self.file.create_entity("IfcDistributionControlElement")
        relation = ifcopenshell.api.system.assign_flow_control(
            self.file,
            related_flow_control=flow_control1,
            relating_flow_element=flow_element,
        )
        assert len(self.file.by_type("IfcRelFlowControlElements")) == 1
        assert relation.RelatingFlowElement == flow_element
        assert set(relation.RelatedControlElements) == set((flow_control, flow_control1))


class TestAssignFlowControlIFC2X3(test.bootstrap.IFC2X3, TestAssignFlowControl):
    pass
