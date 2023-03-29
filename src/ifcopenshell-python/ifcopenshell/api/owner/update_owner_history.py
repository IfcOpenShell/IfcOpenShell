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

import time
import ifcopenshell
import ifcopenshell.api
import ifcopenshell.api.owner.settings
import ifcopenshell.util.element


class Usecase:
    def __init__(self, file, element=None):
        """Updates the owner that is assigned to an object

        This ensures that the owner is tracked to have modified the object last,
        including the time when the change occured. See
        ifcopenshell.api.owner.create_owner_history for details.

        :param element: The IfcRoot element to update the ownership details on
            when a change is made.
        :type element: ifcopenshell.entity_instance.entity_instance
        :return: The updated IfcOwnerHistory element.
        :rtype: ifcopenshell.entity_instance.entity_instance

        Example:

        .. code:: python

            # See ifcopenshell.api.owner.create_owner_history for setup
            # [ ... example setup code ... ]

            # We've finished our ownership setup. Now let's start our script and
            # create a space. Notice we don't actually call
            # create_owner_history at all. This is already automatically handled
            # by the API when necessary. Under the hood, the API is actually
            # running this code on the IfcSpace element:
            # element.OwnerHistory = ifcopenshell.api.run("owner.create_owner_history", model)
            space = ifcopenshell.api.run("root.create_entity", model, ifc_class="IfcSpace")

            # Any edits we make will have ownership tracking automatically
            # applied. There is no need to run any owner.update_owner_history
            # API calls either.
            ifcopenshell.api.run("attribute.edit_attributes", model, product=space, attributes={"Name": "Lobby"})
        """
        self.file = file
        self.settings = {"element": element}

    def execute(self):
        if not hasattr(self.settings["element"], "OwnerHistory"):
            return
        user = ifcopenshell.api.owner.settings.get_user(self.file)
        if not user:
            return
        application = ifcopenshell.api.owner.settings.get_application(self.file)
        if not application:
            return
        if not self.settings["element"].OwnerHistory:
            self.settings["element"].OwnerHistory = ifcopenshell.api.run("owner.create_owner_history", self.file)
            return self.settings["element"].OwnerHistory
        if self.file.get_total_inverses(self.settings["element"].OwnerHistory) > 1:
            new = ifcopenshell.util.element.copy(self.file, self.settings["element"].OwnerHistory)
            self.settings["element"].OwnerHistory = new
        self.settings["element"].OwnerHistory.ChangeAction = "MODIFIED"
        self.settings["element"].OwnerHistory.LastModifiedDate = int(time.time())
        self.settings["element"].OwnerHistory.LastModifyingUser = user
        self.settings["element"].OwnerHistory.LastModifyingApplication = application
        return self.settings["element"].OwnerHistory
