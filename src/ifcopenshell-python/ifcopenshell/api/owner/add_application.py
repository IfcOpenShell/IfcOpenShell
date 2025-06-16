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
import ifcopenshell.api.owner
import ifcopenshell.api.pset
from typing import Optional, Any, Union


def add_application(
    file: ifcopenshell.file,
    application_developer: Optional[ifcopenshell.entity_instance] = None,
    version: Optional[str] = None,
    application_full_name: str = "IfcOpenShell",
    application_identifier: str = "IfcOpenShell",
) -> ifcopenshell.entity_instance:
    """Adds a new application

    IFC data may be associated with an authoring application to identify
    which application was responsible for editing or authoring the data. An
    application is defined by the developing organisation, as well as a full
    name and identifier. This is akin to how web browsers have an
    identification string.

    :param application_developer: The IfcOrganization responsible for
        creating the application. Defaults to generating an IfcOpenShell
        organisation if none is provided.
    :param version: The version of the application. Defaults to the
        ifcopenshell.version data if not specified.
    :param application_full_name: The name of the application
    :param application_identifier: An identification string for the
        application intended for computers to read.
    :return: The newly created IfcApplication

    Example:

    .. code:: python

        application = ifcopenshell.api.owner.add_application(model)
    """
    usecase = Usecase()
    usecase.file = file
    return usecase.execute(
        application_developer,
        version or ifcopenshell.version,
        application_full_name,
        application_identifier,
    )


class Usecase:
    file: ifcopenshell.file

    def execute(
        self,
        application_developer: Union[ifcopenshell.entity_instance, None],
        version: str,
        application_full_name: str,
        application_identifier: str,
    ) -> ifcopenshell.entity_instance:
        if not application_developer:
            application_developer = self.create_application_organisation()
        return self.file.create_entity(
            "IfcApplication",
            ApplicationDeveloper=application_developer,
            Version=version,
            ApplicationFullName=application_full_name,
            ApplicationIdentifier=application_identifier,
        )

    def create_application_organisation(self) -> ifcopenshell.entity_instance:
        result = self.file.create_entity(
            "IfcOrganization",
            **{
                "Name": "IfcOpenShell",
                "Description": "IfcOpenShell is an open source software library that helps users and software developers to work with IFC data.",
                "Roles": [
                    self.file.create_entity("IfcActorRole", **{"Role": "USERDEFINED", "UserDefinedRole": "CONTRIBUTOR"})
                ],
            },
        )
        # 0 IfcOrganization.Identification / Id (IFC2X3).
        result[0] = "IfcOpenShell"

        # 4 IfcOrganization.Addresses
        if self.file.schema == "IFC4X3":
            # IfcTelecomAddress is deprecated in IFC4X3.
            actor = ifcopenshell.api.owner.add_actor(self.file, result)
            pset = ifcopenshell.api.pset.add_pset(self.file, actor, "PEnum_AddressType")
            ifcopenshell.api.pset.edit_pset(
                self.file,
                pset,
                properties={
                    "Purpose": "OTHER",
                    "UserDefinedPurpose": "WEBPAGE",
                    "WWWHomePageURL": "https://ifcopenshell.org",
                },
            )
        else:
            result[4] = [
                self.file.create_entity(
                    "IfcTelecomAddress",
                    Purpose="USERDEFINED",
                    UserDefinedPurpose="WEBPAGE",
                    WWWHomePageURL="https://ifcopenshell.org",
                ),
            ]
        return result
