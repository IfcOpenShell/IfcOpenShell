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
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {}
        for key, value in settings.items():
            self.settings[key] = value

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
            self.settings["element"].OwnerHistory = ifcopenshell.api.run(
                "owner.create_owner_history", self.file, **self.settings
            )
            return self.settings["element"].OwnerHistory
        if self.file.get_total_inverses(self.settings["element"].OwnerHistory) > 1:
            new = ifcopenshell.util.element.copy(self.file, self.settings["element"].OwnerHistory)
            self.settings["element"].OwnerHistory = new
        self.settings["element"].OwnerHistory.ChangeAction = "MODIFIED"
        self.settings["element"].OwnerHistory.LastModifiedDate = int(time.time())
        self.settings["element"].OwnerHistory.LastModifyingUser = user
        self.settings["element"].OwnerHistory.LastModifyingApplication = application
        return self.settings["element"].OwnerHistory
