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
    def __init__(self, src, file, logger, args=None):
        self.src = src
        self.file = file
        self.logger = logger
        self.args = args

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
