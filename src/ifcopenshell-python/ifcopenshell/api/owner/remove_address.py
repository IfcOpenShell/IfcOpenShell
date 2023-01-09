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


class Usecase:
    def __init__(self, file, address=None):
        """Removes an address

        Naturally, any organisations or people using that address will have the
        relationship removed.

        :param address: The IfcAddress to remove.
        :type address: ifcopenshell.entity_instance.entity_instance
        :return: None
        :rtype: None

        Example:

        .. code:: python

            organisation = ifcopenshell.api.run("owner.add_organisation", model)
            address = ifcopenshell.api.run("owner.add_address", model,
                assigned_object=organisation, ifc_class="IfcPostalAddress")

            # Change our mind and delete it
            ifcopenshell.api.run("owner.remove_address", model, address=address)
        """
        self.file = file
        self.settings = {"address": address}

    def execute(self):
        for inverse in self.file.get_inverse(self.settings["address"]):
            if inverse.is_a() in ("IfcOrganization", "IfcPerson"):
                if inverse.Addresses == (self.settings["address"],):
                    inverse.Addresses = None
        self.file.remove(self.settings["address"])
