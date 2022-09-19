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


class Patcher:
    def __init__(self, src, file, logger, args=None):
        self.src = src
        self.file = file
        self.logger = logger
        self.args = args

    def patch(self):
        if self.args and self.args[0] == "DUPLICATE":
            guids = set()
            for element in self.file.by_type("IfcRoot"):
                if element.GlobalId in guids:
                    element.GlobalId = ifcopenshell.guid.new()
                elif len(element.GlobalId) != 22 or element.GlobalId[0] not in "0123":
                    element.GlobalId = ifcopenshell.guid.new()
                else:
                    try:
                        ifcopenshell.guid.expand(element.GlobalId)
                    except:
                        element.GlobalId = ifcopenshell.guid.new()
                guids.add(element.GlobalId)
        else:
            for element in self.file.by_type("IfcRoot"):
                element.GlobalId = ifcopenshell.guid.new()
