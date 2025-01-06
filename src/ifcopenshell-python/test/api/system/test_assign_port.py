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

import numpy
import test.bootstrap
import ifcopenshell.api.unit
import ifcopenshell.api.root
import ifcopenshell.api.system
import ifcopenshell.api.geometry
import ifcopenshell.util.placement
import ifcopenshell.util.system


class TestAssignPort(test.bootstrap.IFC4):
    def test_assigning_a_port_once_only(self):
        port = self.file.createIfcDistributionPort()
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcFlowSegment")
        ifcopenshell.api.system.assign_port(self.file, element=element, port=port)
        ifc2x3 = self.file.schema == "IFC2X3"
        if ifc2x3:
            assert element.HasPorts[0].RelatingPort == port
        else:
            assert element.IsNestedBy[0].RelatedObjects == (port,)
        assert ifcopenshell.util.system.get_ports(element) == [port]
        ifcopenshell.api.system.assign_port(self.file, element=element, port=port)
        assert ifcopenshell.util.system.get_ports(element) == [port]

    def test_updating_the_placement_to_be_relative_if_it_exists(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        ifcopenshell.api.unit.assign_unit(self.file)
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcFlowSegment")
        subelement = ifcopenshell.api.system.add_port(self.file)
        matrix = numpy.array(
            (
                (1.0, 0.0, 0.0, 1.0),
                (0.0, 1.0, 0.0, 1.0),
                (0.0, 0.0, 1.0, 1.0),
                (0.0, 0.0, 0.0, 1.0),
            )
        )
        submatrix = numpy.array(
            (
                (1.0, 0.0, 0.0, 1.0),
                (0.0, 1.0, 0.0, 2.0),
                (0.0, 0.0, 1.0, 3.0),
                (0.0, 0.0, 0.0, 1.0),
            )
        )
        ifcopenshell.api.geometry.edit_object_placement(self.file, product=element, matrix=matrix.copy(), is_si=False)
        ifcopenshell.api.geometry.edit_object_placement(
            self.file, product=subelement, matrix=submatrix.copy(), is_si=False
        )
        ifcopenshell.api.system.assign_port(self.file, element=element, port=subelement)
        assert numpy.array_equal(ifcopenshell.util.placement.get_local_placement(element.ObjectPlacement), matrix)
        assert numpy.array_equal(ifcopenshell.util.placement.get_local_placement(subelement.ObjectPlacement), submatrix)
        assert subelement.ObjectPlacement.PlacementRelTo == element.ObjectPlacement


class TestAssignPortIFC2X3(test.bootstrap.IFC2X3, TestAssignPort):
    pass
