# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
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

import ifcopenshell.api


class Usecase:
    def __init__(self, file, name=None, ifc_class="IfcStructuralLoadLinearForce"):
        """Adds a new structural load

        Structural loads may be actions or reactions. A simple load might be a
        static and be linear, planar, or a single point. Alternatively, loads
        may be defined as a configuration of multiple loads.

        :param name: The name of the load
        :type name: str,optional
        :param ifc_class: The subtype of IfcStructuralLoad to create. Consult
            the IFC documentation to see all the types of loads.
        :type ifc_class: str
        :return: The newly created load entity, depending on the ifc_class
            specified.
        :rtype: ifcopenshell.entity_instance.entity_instance

        Example:

        .. code:: python

            # Create a simple linear load
            ifcopenshell.api.run("structural.add_structural_load", model)
        """
        self.file = file
        self.settings = {
            "name": name,
            "ifc_class": ifc_class,
        }

    def execute(self):
        return self.file.create_entity(self.settings["ifc_class"], Name=self.settings["name"])
