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
import ifcopenshell.guid
from logging import Logger


class Patcher:
    def __init__(self, src: str, file: ifcopenshell.file, logger: Logger, only_duplicates=False):
        """Regenerate GlobalIds in an IFC model

        All root elements in an IFC model must be identified by a unique Global
        ID (also known as a GUID or UUID). Some proprietary BIM software do this
        incorrect (I know right), either by generating an invalid ID, creating
        duplicate IDs, generating IDs in a way that is not universally unique or
        as random as you might prefer (e.g. non-compliant with UUID v4).

        This will regenerate new GlobalIds for the entire model.

        :param only_duplicates: If set to True, new GlobalIds will only be
            generated for duplicate IDs. This is a safe thing to run to ensure
            IFCs are valid. If False, all GlobalIds will be regenerated.
        :type only_duplicates: bool

        Example:

        .. code:: python

            # Regenerate all GlobalIds
            ifcpatch.execute({"input": "input.ifc", "file": model, "recipe": "RegenerateGlobalIds", "arguments": []})

            # Regenerate only duplicate GlobalIds
            ifcpatch.execute({"input": "input.ifc", "file": model, "recipe": "RegenerateGlobalIds", "arguments": [True]})
        """
        self.src = src
        self.file = file
        self.logger = logger
        self.only_duplicates = only_duplicates

    def patch(self):
        if self.only_duplicates:
            duplicates = 0
            invalid_ids = 0

            guids = set()
            for element in self.file.by_type("IfcRoot"):
                if element.GlobalId in guids:
                    element.GlobalId = ifcopenshell.guid.new()
                    duplicates += 1
                elif len(element.GlobalId) != 22 or element.GlobalId[0] not in "0123":
                    element.GlobalId = ifcopenshell.guid.new()
                    invalid_ids += 1
                else:
                    try:
                        ifcopenshell.guid.expand(element.GlobalId)
                    except:
                        element.GlobalId = ifcopenshell.guid.new()
                    invalid_ids += 1
                guids.add(element.GlobalId)

            print("Replaced %s duplicate GlobalIds" % duplicates)
            print("Replaced %s invalid GlobalIds" % invalid_ids)
        else:
            for element in self.file.by_type("IfcRoot"):
                element.GlobalId = ifcopenshell.guid.new()
