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
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {
            "application_developer": None,
            "version": ifcopenshell.version,
            "application_full_name": "IfcOpenShell",
            "application_identifier": "IfcOpenShell",
        }
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        if not self.settings["application_developer"]:
            self.settings["application_developer"] = self.create_application_organisation()
        return self.file.create_entity(
            "IfcApplication",
            **{
                "ApplicationDeveloper": self.settings["application_developer"],
                "Version": self.settings["version"],
                "ApplicationFullName": self.settings["application_full_name"],
                "ApplicationIdentifier": self.settings["application_identifier"],
            },
        )

    def create_application_organisation(self):
        result = self.file.create_entity(
            "IfcOrganization",
            **{
                "Name": "IfcOpenShell",
                "Description": "IfcOpenShell is an open source software library that helps users and software developers to work with IFC data.",
                "Roles": [
                    self.file.create_entity("IfcActorRole", **{"Role": "USERDEFINED", "UserDefinedRole": "CONTRIBUTOR"})
                ],
                "Addresses": [
                    self.file.create_entity(
                        "IfcTelecomAddress",
                        **{
                            "Purpose": "USERDEFINED",
                            "UserDefinedPurpose": "WEBPAGE",
                            "WWWHomePageURL": "https://ifcopenshell.org",
                        },
                    ),
                ],
            },
        )
        result[0] = "IfcOpenShell"
        return result
