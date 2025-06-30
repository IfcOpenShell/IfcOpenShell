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
import ifcopenshell.api.owner
import ifcopenshell.guid
import ifcopenshell.util.element
from typing import Optional, Any


def connect_port(
    file: ifcopenshell.file,
    port1: ifcopenshell.entity_instance,
    port2: ifcopenshell.entity_instance,
    direction: str = "NOTDEFINED",
    element: Optional[ifcopenshell.entity_instance] = None,
) -> None:
    """Connects two ports together

    A distribution element (e.g. a duct) may be connected to another
    distribution element (e.g. a fitting) by connecting a port at one of the
    duct to a port at the same end of the fitting.

    Ports may only have one connection, so you cannot have multiple things
    connected to the same port. Nor can you have incompatible port
    connections, such as an electrical port connected to an airflow port.

    Port connectivity may be explicit or implicit. Explicit connections are
    where the port connectivity is described for every single distribution
    element in detail. For example, a duct segment would have port
    connections to a duct fitting, which would have port connections to
    another duct segment, all the way from a fan to an air terminal exactly
    as constructed on site. Implicit connections only consider the key
    distribution control elements (e.g. the fan and the terminal) and ignore
    all of the details of the duct segments and fittings in between.
    Generally, explicit connectivity is preferred for later detailed design,
    and implicit connectivity is preferred for early phase design.

    :param port1: The port of the first distribution element to connect.
    :param port2: The port of the second distribution element to connect.
    :param direction: The directionality of distribution flow through the
        port connection. NOTDEFINED means that the direction has not yet
        been determined. This is useful during preliminary system design.
        SOURCE means that the flow is from the first element to the second
        element. SINK means that the flow is from the second element to the
        first element. SOURCEANDSINK means that flow is bi-directional
        between the first and second element.  SOURCEANDSINK is a relatively
        rare scenario.
    :param element: Optionally set an element through which the port
        connectivity is made, such as a segment or fitting. This is only to
        be used for implicit port connectivity where the segments and
        fittings are less important.

    Example:

    .. code:: python

        # A completely empty distribution system
        system = ifcopenshell.api.system.add_system(model)

        # Create a duct and a 90 degree bend fitting
        duct = ifcopenshell.api.root.create_entity(model,
            ifc_class="IfcDuctSegment", predefined_type="RIGIDSEGMENT")
        fitting = ifcopenshell.api.root.create_entity(model,
            ifc_class="IfcDuctFitting", predefined_type="BEND")

        # The duct and fitting is part of the system
        ifcopenshell.api.system.assign_system(model, products=[duct], system=system)
        ifcopenshell.api.system.assign_system(model, products=[fitting], system=system)

        # Create 2 ports, one for either end of both the duct and fitting.
        duct_port1 = ifcopenshell.api.system.add_port(model, element=duct)
        duct_port2 = ifcopenshell.api.system.add_port(model, element=duct)
        fitting_port1 = ifcopenshell.api.system.add_port(model, element=fitting)
        fitting_port2 = ifcopenshell.api.system.add_port(model, element=fitting)

        # Connect the duct and fitting together. At this point, we have not
        # yet determined the direction of the flow, so we leave direction as
        # NOTDEFINED.
        ifcopenshell.api.system.connect_port(model, port1=duct_port2, port2=fitting_port1)
    """
    usecase = Usecase()
    usecase.file = file
    usecase.settings = {
        "port1": port1,
        "port2": port2,
        "direction": direction,
        "element": element,
    }
    return usecase.execute()


class Usecase:
    file: ifcopenshell.file
    settings: dict[str, Any]

    def execute(self):
        # Note: there are a number of ambiguities with port connectivity. We
        # assume system topology is represented by a directed graph. In other
        # words, SOURCEANDSINK and NOTDEFINED implies a two way connection, with
        # two IfcRelConnectsPorts. SOURCE or SINK by itself implies a one way
        # connection. NOTDEFINED semantically implies that although you may
        # traverse the graph either direction, the direction has not been
        # determined yet by the engineer. None is not allowed as a direction as
        # we assume None means that no connection is made.

        if self.settings["port1"] == self.settings["port2"]:
            return

        self.purge_existing_connections_to_other_ports()

        if self.settings["direction"] == "SOURCE":
            self.settings["port1"].FlowDirection = "SOURCE"
            self.settings["port2"].FlowDirection = "SINK"
        elif self.settings["direction"] == "SINK":
            self.settings["port1"].FlowDirection = "SINK"
            self.settings["port2"].FlowDirection = "SOURCE"
        else:
            self.settings["port1"].FlowDirection = self.settings["direction"]
            self.settings["port2"].FlowDirection = self.settings["direction"]

        if self.settings["direction"] in ["SOURCE", "SOURCEANDSINK", "NOTDEFINED"]:
            self.set_connected_to()
        else:
            self.purge_connected_to()

        if self.settings["direction"] in ["SINK", "SOURCEANDSINK", "NOTDEFINED"]:
            self.set_connected_from()
        else:
            self.purge_connected_from()

        self.set_realising_element()

    def purge_existing_connections_to_other_ports(self):
        for rel in self.settings["port1"].ConnectedTo or []:
            if rel.RelatedPort != self.settings["port2"]:
                history = rel.OwnerHistory
                self.file.remove(rel)
                if history:
                    ifcopenshell.util.element.remove_deep2(self.file, history)
        for rel in self.settings["port1"].ConnectedFrom or []:
            if rel.RelatingPort != self.settings["port2"]:
                history = rel.OwnerHistory
                self.file.remove(rel)
                if history:
                    ifcopenshell.util.element.remove_deep2(self.file, history)
        for rel in self.settings["port2"].ConnectedTo or []:
            if rel.RelatedPort != self.settings["port1"]:
                history = rel.OwnerHistory
                self.file.remove(rel)
                if history:
                    ifcopenshell.util.element.remove_deep2(self.file, history)
        for rel in self.settings["port2"].ConnectedFrom or []:
            if rel.RelatingPort != self.settings["port1"]:
                history = rel.OwnerHistory
                self.file.remove(rel)
                if history:
                    ifcopenshell.util.element.remove_deep2(self.file, history)

    def set_connected_to(self):
        if self.settings["port1"].ConnectedTo:
            return

        self.file.create_entity(
            "IfcRelConnectsPorts",
            GlobalId=ifcopenshell.guid.new(),
            OwnerHistory=ifcopenshell.api.owner.create_owner_history(self.file),
            RelatingPort=self.settings["port1"],
            RelatedPort=self.settings["port2"],
        )

    def set_connected_from(self):
        if self.settings["port1"].ConnectedFrom:
            return

        self.file.create_entity(
            "IfcRelConnectsPorts",
            GlobalId=ifcopenshell.guid.new(),
            OwnerHistory=ifcopenshell.api.owner.create_owner_history(self.file),
            RelatingPort=self.settings["port2"],
            RelatedPort=self.settings["port1"],
        )

    def purge_connected_to(self):
        for rel in self.settings["port1"].ConnectedTo or []:
            history = rel.OwnerHistory
            self.file.remove(rel)
            if history:
                ifcopenshell.util.element.remove_deep2(self.file, history)

    def purge_connected_from(self):
        for rel in self.settings["port1"].ConnectedFrom or []:
            history = rel.OwnerHistory
            self.file.remove(rel)
            if history:
                ifcopenshell.util.element.remove_deep2(self.file, history)

    def set_realising_element(self):
        for rel in self.settings["port1"].ConnectedTo or []:
            rel.RealizingElement = self.settings["element"]
        for rel in self.settings["port1"].ConnectedFrom or []:
            rel.RealizingElement = self.settings["element"]
