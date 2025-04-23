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


class TestConnectPort(test.bootstrap.IFC4):
    def test_connecting_a_port(self):
        port = ifcopenshell.api.system.add_port(self.file)
        port2 = ifcopenshell.api.system.add_port(self.file)
        ifcopenshell.api.system.connect_port(self.file, port1=port, port2=port2)
        assert port.ConnectedTo[0].RelatedPort == port2
        assert port2.ConnectedFrom[0].RelatingPort == port
        assert port2.ConnectedTo[0].RelatedPort == port
        assert port.ConnectedFrom[0].RelatingPort == port2
        assert port.FlowDirection == "NOTDEFINED"
        assert port2.FlowDirection == "NOTDEFINED"
        assert len(self.file.by_type("IfcRelConnectsPorts")) == 2

    def test_not_connecting_a_port_twice(self):
        port = ifcopenshell.api.system.add_port(self.file)
        port2 = ifcopenshell.api.system.add_port(self.file)
        ifcopenshell.api.system.connect_port(self.file, port1=port, port2=port2)
        ifcopenshell.api.system.connect_port(self.file, port1=port, port2=port2)
        ifcopenshell.api.system.connect_port(self.file, port1=port2, port2=port)
        assert port.ConnectedTo[0].RelatedPort == port2
        assert port2.ConnectedFrom[0].RelatingPort == port
        assert port2.ConnectedTo[0].RelatedPort == port
        assert port.ConnectedFrom[0].RelatingPort == port2
        assert port.FlowDirection == "NOTDEFINED"
        assert port2.FlowDirection == "NOTDEFINED"
        assert len(self.file.by_type("IfcRelConnectsPorts")) == 2

    def test_connecting_a_port_from_source_to_sink(self):
        port = ifcopenshell.api.system.add_port(self.file)
        port2 = ifcopenshell.api.system.add_port(self.file)
        ifcopenshell.api.system.connect_port(self.file, port1=port, port2=port2, direction="SOURCE")
        assert port.ConnectedTo[0].RelatedPort == port2
        assert port2.ConnectedFrom[0].RelatingPort == port
        assert port.FlowDirection == "SOURCE"
        assert port2.FlowDirection == "SINK"
        assert len(self.file.by_type("IfcRelConnectsPorts")) == 1

    def test_connecting_a_port_from_sink_to_source(self):
        port = ifcopenshell.api.system.add_port(self.file)
        port2 = ifcopenshell.api.system.add_port(self.file)
        ifcopenshell.api.system.connect_port(self.file, port1=port, port2=port2, direction="SINK")
        assert port2.ConnectedTo[0].RelatedPort == port
        assert port.ConnectedFrom[0].RelatingPort == port2
        assert port.FlowDirection == "SINK"
        assert port2.FlowDirection == "SOURCE"
        assert len(self.file.by_type("IfcRelConnectsPorts")) == 1

    def test_connecting_a_port_as_both_source_and_sink(self):
        port = ifcopenshell.api.system.add_port(self.file)
        port2 = ifcopenshell.api.system.add_port(self.file)
        ifcopenshell.api.system.connect_port(self.file, port1=port, port2=port2, direction="SOURCEANDSINK")
        assert port.ConnectedTo[0].RelatedPort == port2
        assert port2.ConnectedFrom[0].RelatingPort == port
        assert port2.ConnectedTo[0].RelatedPort == port
        assert port.ConnectedFrom[0].RelatingPort == port2
        assert port.FlowDirection == "SOURCEANDSINK"
        assert port2.FlowDirection == "SOURCEANDSINK"
        assert len(self.file.by_type("IfcRelConnectsPorts")) == 2

    def test_ports_can_only_connect_to_one_port_at_a_time(self):
        port = ifcopenshell.api.system.add_port(self.file)
        port2 = ifcopenshell.api.system.add_port(self.file)
        port3 = ifcopenshell.api.system.add_port(self.file)
        ifcopenshell.api.system.connect_port(self.file, port1=port, port2=port3, direction="SOURCEANDSINK")
        ifcopenshell.api.system.connect_port(self.file, port1=port, port2=port2, direction="SOURCE")
        assert port.ConnectedTo[0].RelatedPort == port2
        assert port2.ConnectedFrom[0].RelatingPort == port
        assert port.FlowDirection == "SOURCE"
        assert port2.FlowDirection == "SINK"
        assert len(self.file.by_type("IfcRelConnectsPorts")) == 1
        assert not port3.ConnectedTo
        assert not port3.ConnectedFrom

    def test_changing_a_port_from_source_and_sink_to_only_source(self):
        port = ifcopenshell.api.system.add_port(self.file)
        port2 = ifcopenshell.api.system.add_port(self.file)
        ifcopenshell.api.system.connect_port(self.file, port1=port, port2=port2, direction="SOURCEANDSINK")
        ifcopenshell.api.system.connect_port(self.file, port1=port, port2=port2, direction="SOURCE")
        assert port.ConnectedTo[0].RelatedPort == port2
        assert port2.ConnectedFrom[0].RelatingPort == port
        assert port.FlowDirection == "SOURCE"
        assert port2.FlowDirection == "SINK"
        assert len(self.file.by_type("IfcRelConnectsPorts")) == 1

    def test_connecting_ports_with_a_realising_element(self):
        port = ifcopenshell.api.system.add_port(self.file)
        port2 = ifcopenshell.api.system.add_port(self.file)
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcFlowFitting")
        ifcopenshell.api.system.connect_port(self.file, port1=port, port2=port2, element=element)
        assert self.file.by_type("IfcRelConnectsPorts")[0].RealizingElement == element
        ifcopenshell.api.system.connect_port(self.file, port1=port, port2=port2)
        assert self.file.by_type("IfcRelConnectsPorts")[0].RealizingElement is None


class TestConnectPortIFC2X3(test.bootstrap.IFC2X3, TestConnectPort):
    pass
