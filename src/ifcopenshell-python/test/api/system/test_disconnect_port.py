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
import ifcopenshell.util.system


class TestDisconnectPort(test.bootstrap.IFC4):
    def test_disconnecting_a_port(self):
        port = ifcopenshell.api.system.add_port(self.file)
        port2 = ifcopenshell.api.system.add_port(self.file)
        ifcopenshell.api.system.connect_port(self.file, port1=port, port2=port2, direction="NOTDEFINED")
        ifcopenshell.api.system.disconnect_port(self.file, port=port)
        assert port.FlowDirection == None
        assert port2.FlowDirection == None
        assert len(self.file.by_type("IfcRelConnectsPorts")) == 0


class TestDisconnectPortIFC2X3(test.bootstrap.IFC2X3, TestDisconnectPort):
    pass
