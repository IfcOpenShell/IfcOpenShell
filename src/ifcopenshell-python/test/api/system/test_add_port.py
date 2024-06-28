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
import ifcopenshell.api.root
import ifcopenshell.api.system
import ifcopenshell.util.system


class TestAddPort(test.bootstrap.IFC4):
    def test_run(self):
        assert ifcopenshell.api.system.add_port(self.file).is_a("IfcDistributionPort")

    def test_assigning_a_port_as_well_if_an_element_is_specified(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcFlowTerminal")
        port = ifcopenshell.api.system.add_port(self.file, element=element)
        assert ifcopenshell.util.system.get_ports(element) == [port]


class TestAddPortIFC2X3(test.bootstrap.IFC2X3, TestAddPort):
    pass
