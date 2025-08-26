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
import ifcopenshell.util.element


def unassign_port(
    file: ifcopenshell.file, element: ifcopenshell.entity_instance, port: ifcopenshell.entity_instance
) -> None:
    """Unassigns a port to an element

    Ports are typically always assigned to a distribution element, but in
    some edge cases you may want to unassign the port to create an orphaned
    port for cleaning or patchin purposes.

    :param element: The IfcDistributionElement to unassign the port from.
    :param port: The IfcDistributionPort you want to unassign.
    :return: None

    Example:

    .. code:: python

        # Create a duct
        duct = ifcopenshell.api.root.create_entity(model,
            ifc_class="IfcDuctSegment", predefined_type="RIGIDSEGMENT")

        # Create 2 ports, one for either end.
        port1 = ifcopenshell.api.system.add_port(model, element=duct)
        port2 = ifcopenshell.api.system.add_port(model, element=duct)

        # Unassign one port for some weird reason.
        ifcopenshell.api.system.unassign_port(model, element=duct, port=port1)
    """
    usecase = Usecase()
    usecase.file = file
    return usecase.execute(element, port)


class Usecase:
    file: ifcopenshell.file

    def execute(self, element: ifcopenshell.entity_instance, port: ifcopenshell.entity_instance) -> None:
        if self.file.schema == "IFC2X3":
            self.element = element
            self.port = port
            return self.execute_ifc2x3()

        for rel in element.IsNestedBy or []:
            if port in rel.RelatedObjects:
                if len(rel.RelatedObjects) == 1:
                    history = rel.OwnerHistory
                    self.file.remove(rel)
                    if history:
                        ifcopenshell.util.element.remove_deep2(self.file, history)
                    return
                related_objects = set(rel.RelatedObjects) or set()
                related_objects.remove(port)
                rel.RelatedObjects = list(related_objects)
                ifcopenshell.api.owner.update_owner_history(self.file, element=rel)

    def execute_ifc2x3(self) -> None:
        for rel in self.element.HasPorts or []:
            if rel.RelatingPort == self.port:
                history = rel.OwnerHistory
                self.file.remove(rel)
                if history:
                    ifcopenshell.util.element.remove_deep2(self.file, history)
                return
