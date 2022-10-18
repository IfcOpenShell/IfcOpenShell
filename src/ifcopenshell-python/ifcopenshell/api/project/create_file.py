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

import datetime
import ifcopenshell


class Usecase:
    def __init__(self, version: str = "IFC4"):
        """Create File

        Create a new IFC file object

        :param version: The schema version of the IFC file. Choose from "IFC2X3" or "IFC4".
        :return: file: The created IFC file object.
        """
        self.settings = {"version": version}

    def execute(self) -> ifcopenshell.file:
        self.file = ifcopenshell.file(schema=self.settings["version"])
        self.file.wrapped_data.header.file_name.name = "/dev/null"  # Hehehe
        self.file.wrapped_data.header.file_name.time_stamp = (
            datetime.datetime.utcnow()
            .replace(tzinfo=datetime.timezone.utc)
            .astimezone()
            .replace(microsecond=0)
            .isoformat()
        )
        self.file.wrapped_data.header.file_name.preprocessor_version = "IfcOpenShell {}".format(ifcopenshell.version)
        self.file.wrapped_data.header.file_name.originating_system = "IfcOpenShell {}".format(ifcopenshell.version)
        self.file.wrapped_data.header.file_name.authorization = "Nobody"
        self.file.wrapped_data.header.file_description.description = ("ViewDefinition[DesignTransferView]",)
        return self.file
