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
import ifcopenshell.api.owner.settings


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        user = ifcopenshell.api.owner.settings.get_user(self.file)
        if self.file.schema != "IFC2X3" and not user:
            return
        application = ifcopenshell.api.owner.settings.get_application(self.file)
        if self.file.schema != "IFC2X3" and not application:
            return
        return self.file.create_entity(
            "IfcOwnerHistory",
            **{
                "OwningUser": user,
                "OwningApplication": application,
                "State": "READWRITE",
                "ChangeAction": "ADDED",
                "LastModifiedDate": int(time.time()),
                "LastModifyingUser": user,
                "LastModifyingApplication": application,
                "CreationDate": int(time.time()),
            },
        )
