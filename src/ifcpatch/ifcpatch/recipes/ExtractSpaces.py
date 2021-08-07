
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
import ifcopenshell.util.selector


class Patcher:
    def __init__(self, src, file, logger, args=None):
        self.src = src
        self.file = file
        self.logger = logger
        self.args = args

    def patch(self):
        self.contained_ins = {}
        self.aggregates = {}
        self.new = ifcopenshell.file(schema=self.file.wrapped_data.schema)
        self.owner_history = None
        for owner_history in self.file.by_type("IfcOwnerHistory"):
            self.owner_history = self.new.add(owner_history)
            break
        selector = ifcopenshell.util.selector.Selector()
        for space in selector.parse(self.file, ".IfcSpace"):
            self.add_element(space)
        self.file = self.new

    def add_element(self, element):
        self.new.add(element)
        for rel_aggregate in element.Decomposes:
            self.add_element(rel_aggregate.RelatingObject)
            self.new.add(rel_aggregate)
