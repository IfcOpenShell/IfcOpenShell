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
    def __init__(self, file, element=None, port=None):
        """Unassigns a port to an element

        Ports are typically always assigned to a distribution element, but in
        some edge cases you may want to unassign the port to create an orphaned
        port for cleaning or patchin purposes.

        :param element: The IfcDistributionElement to unassign the port from.
        :type element: ifcopenshell.entity_instance.entity_instance
        :param port: The IfcDistributionPort you want to unassign.
        :type port: ifcopenshell.entity_instance.entity_instance
        :return: None
        :rtype: None

        Example:

        .. code:: python

            # Create a duct
            duct = ifcopenshell.api.run("root.create_entity", model,
                ifc_class="IfcDuctSegment", predefined_type="RIGIDSEGMENT")

            # Create 2 ports, one for either end.
            port1 = ifcopenshell.api.run("system.add_port", model, element=duct)
            port2 = ifcopenshell.api.run("system.add_port", model, element=duct)

            # Unassign one port for some weird reason.
            ifcopenshell.api.run("system.unassign_port", model, element=duct, port=port1)
        """
        self.file = file
        self.settings = {
            "element": element,
            "port": port,
        }

    def execute(self):
        if self.file.schema == "IFC2X3":
            return self.execute_ifc2x3()

        for rel in self.settings["element"].IsNestedBy or []:
            if self.settings["port"] in rel.RelatedObjects:
                if len(rel.RelatedObjects) == 1:
                    self.file.remove(rel)
                    return
                related_objects = set(rel.RelatedObjects) or set()
                related_objects.remove(self.settings["port"])
                rel.RelatedObjects = list(related_objects)
                ifcopenshell.api.run("owner.update_owner_history", self.file, **{"element": rel})

    def execute_ifc2x3(self):
        for rel in self.settings["element"].HasPorts or []:
            if rel.RelatingPort == self.settings["port"]:
                self.file.remove(rel)
                return
