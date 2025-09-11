# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2021, 2022 Dion Moult <dion@thinkmoult.com>
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
import ifcopenshell.util.schema


def create_file(version: ifcopenshell.util.schema.IFC_SCHEMA = "IFC4") -> ifcopenshell.file:
    """Create a blank IFC model file object

    Create a new IFC file object based on the nominated schema version. The
    schema version you choose determines what type of IFC data you can store
    in this model. The file is blank and contains no entities.

    It also sets up header data for STEP file serialisation, such as the
    current timestamp, IfcOpenShell as the preprocessor, and defaults to a
    DesignTransferView MVD.

    :param version: The schema version of the IFC file. Choose from
        "IFC2X3", "IFC4", or "IFC4X3". If you have loaded in a custom
        schema, you may specify that schema identifier here too.
    :return: The created IFC file object.

    Example:

    .. code:: python

        # Start a new model.
        model = ifcopenshell.api.project.create_file()

        # It's currently a blank model, so typically the first thing we do
        # is create a project in it.
        project = ifcopenshell.api.root.create_entity(model, ifc_class="IfcProject", name="Test")

        # ... and off we go!
    """
    file = ifcopenshell.file(schema=version)
    file.header.file_name.name = "/dev/null"  # Hehehe
    file.header.file_name.time_stamp = (
        datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).astimezone().replace(microsecond=0).isoformat()
    )
    file.header.file_name.preprocessor_version = "IfcOpenShell {}".format(ifcopenshell.version)
    file.header.file_name.originating_system = "IfcOpenShell {}".format(ifcopenshell.version)
    file.header.file_name.authorization = "Nobody"
    file.header.file_description.description = ("ViewDefinition[DesignTransferView]",)
    return file
