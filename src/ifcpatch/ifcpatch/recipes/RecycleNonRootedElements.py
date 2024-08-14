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

from collections import deque
import ifcopenshell.util.element


class Patcher:
    def __init__(self, src, file, logger):
        """Optimise the filesize of an IFC model by reusing non-rooted elements

        It is possible to non-losslessly optimise the filesize of an IFC model.

        Note that this is usually not recommended. Optimising runs a risk of
        losing some indirect semantic data critical for native IFC authoring.
        Most parties who recommend optimisation are not aware of these risks.
        Optimising is only safe in the context of read-only IFCs.

        If filesize is an issue, another approach would be to use IFCZIP
        instead to compress the model. Optimising the model only typically
        affects filesize and has minimal impact on load times. Large filesizes
        can usually be solved through other means. Consult Bonsai
        documentation on dealing with large models for more details.

        This patch may be run multiple times with diminishing returns.

        Example:

        .. code:: python

            ifcpatch.execute({"input": "input.ifc", "file": model, "recipe": "RecycleNonRootedElements", "arguments": []})
        """
        self.src = src
        self.file = file
        self.logger = logger

    def patch(self):
        deleted = []
        hashes = {}
        for element in self.file:
            if element.is_a("IfcRoot"):
                continue
            h = hash(tuple(element))
            if h in hashes:
                for inverse in self.file.get_inverse(element):
                    ifcopenshell.util.element.replace_attribute(inverse, element, hashes[h])
                deleted.append(element.id())
            else:
                hashes[h] = element
        deleted.sort()
        deleted_q = deque(deleted)
        new = ""
        for line in self.file.wrapped_data.to_string().split("\n"):
            try:
                if int(line.split("=")[0][1:]) != deleted_q[0]:
                    new += line + "\n"
                else:
                    deleted_q.popleft()
            except:
                new += line + "\n"
        self.file = new
