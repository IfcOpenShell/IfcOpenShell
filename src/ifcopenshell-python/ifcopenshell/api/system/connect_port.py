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


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {
            "port1": None,
            "port2": None,
            "direction": "NOTDEFINED",
            "element": None,
        }
        for key, value in settings.items():
            self.settings[key] = value

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
                self.file.remove(rel)
        for rel in self.settings["port1"].ConnectedFrom or []:
            if rel.RelatingPort != self.settings["port2"]:
                self.file.remove(rel)
        for rel in self.settings["port2"].ConnectedTo or []:
            if rel.RelatedPort != self.settings["port1"]:
                self.file.remove(rel)
        for rel in self.settings["port2"].ConnectedFrom or []:
            if rel.RelatingPort != self.settings["port1"]:
                self.file.remove(rel)

    def set_connected_to(self):
        if self.settings["port1"].ConnectedTo:
            return

        self.file.create_entity(
            "IfcRelConnectsPorts",
            GlobalId=ifcopenshell.guid.new(),
            OwnerHistory=ifcopenshell.api.run("owner.create_owner_history", self.file),
            RelatingPort=self.settings["port1"],
            RelatedPort=self.settings["port2"],
        )

    def set_connected_from(self):
        if self.settings["port1"].ConnectedFrom:
            return

        self.file.create_entity(
            "IfcRelConnectsPorts",
            GlobalId=ifcopenshell.guid.new(),
            OwnerHistory=ifcopenshell.api.run("owner.create_owner_history", self.file),
            RelatingPort=self.settings["port2"],
            RelatedPort=self.settings["port1"],
        )

    def purge_connected_to(self):
        for rel in self.settings["port1"].ConnectedTo or []:
            self.file.remove(rel)

    def purge_connected_from(self):
        for rel in self.settings["port1"].ConnectedFrom or []:
            self.file.remove(rel)

    def set_realising_element(self):
        for rel in self.settings["port1"].ConnectedTo or []:
            rel.RealizingElement = self.settings["element"]
        for rel in self.settings["port1"].ConnectedFrom or []:
            rel.RealizingElement = self.settings["element"]
