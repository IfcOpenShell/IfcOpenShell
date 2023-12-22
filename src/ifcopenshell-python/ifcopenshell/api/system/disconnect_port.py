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

import ifcopenshell
import ifcopenshell.api
import ifcopenshell.util.element


class Usecase:
    def __init__(self, file, port=None):
        """Disconnects a port from any other port

        A port may only be connected to one other port, so the other port is not
        needed to be specified.

        :param port: The IfcDistributionPort to disconnect.
        :type port: ifcopenshell.entity_instance.entity_instance
        :return: None
        :rtype: None

        Example:

        .. code:: python

            # A completely empty distribution system
            system = ifcopenshell.api.run("system.add_system", model)

            # Create a duct and a 90 degree bend fitting
            duct = ifcopenshell.api.run("root.create_entity", model,
                ifc_class="IfcDuctSegment", predefined_type="RIGIDSEGMENT")
            fitting = ifcopenshell.api.run("root.create_entity", model,
                ifc_class="IfcDuctFitting", predefined_type="BEND")

            # The duct and fitting is part of the system
            ifcopenshell.api.run("system.assign_system", model, product=duct, system=system)
            ifcopenshell.api.run("system.assign_system", model, product=fitting, system=system)

            # Create 2 ports, one for either end of both the duct and fitting.
            duct_port1 = ifcopenshell.api.run("system.add_port", model, element=duct)
            duct_port2 = ifcopenshell.api.run("system.add_port", model, element=duct)
            fitting_port1 = ifcopenshell.api.run("system.add_port", model, element=fitting)
            fitting_port2 = ifcopenshell.api.run("system.add_port", model, element=fitting)

            # Connect the duct and fitting together. At this point, we have not
            # yet determined the direction of the flow, so we leave direction as
            # NOTDEFINED.
            ifcopenshell.api.run("system.connect_port", model, port1=duct_port2, port2=fitting_port1)

            # Disconnect the port. note we could've equally disconnected
            # fitting_port1 instead of duct_port2
            ifcopenshell.api.run("system.disconnect_port", model, port=duct_port2)
        """
        self.file = file
        self.settings = {
            "port": port,
        }

    def execute(self):
        rels = self.settings["port"].ConnectedTo or ()
        rels += self.settings["port"].ConnectedFrom or ()

        for rel in rels:
            rel.RelatingPort.FlowDirection = None
            rel.RelatedPort.FlowDirection = None
            history = rel.OwnerHistory
            self.file.remove(rel)
            if history:
                ifcopenshell.util.element.remove_deep2(self.file, history)
