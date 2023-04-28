# IfcPatch - IFC patching utiliy
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of IfcPatch.
#
# IfcPatch is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcPatch is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcPatch.  If not, see <http://www.gnu.org/licenses/>.

import ifcopenshell
import ifcopenshell.util.schema


class Patcher:
    def __init__(self, src, file, logger, schema="IFC4"):
        """Migrate from one IFC version to another

        Note that this is experimental and will try to preserve as much data as
        possible. Upgrading to IFC4 is more stable than downgrading to IFC2X3.

        :param schema: The schema identifier of the IFC version to migrate to.
        :type schema: str

        Example:

        .. code:: python

            # Upgrade an IFC2X3 model to IFC4
            ifcpatch.execute({"input": model, "recipe": "Migrate", "arguments": ["IFC4"]})
        """
        self.src = src
        self.file = file
        self.logger = logger
        self.schema = schema

    def patch(self):
        self.file_patched = ifcopenshell.file(schema=self.schema)
        migrator = ifcopenshell.util.schema.Migrator()
        for element in self.file:
            migrator.migrate(element, self.file_patched)
            print("Migrating", element)
            print("Successfully converted to", migrator.migrate(element, self.file_patched))
