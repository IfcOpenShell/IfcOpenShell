# IfcPatch - IFC patching utiliy
# Copyright (C) 2020, 2021, 2022 Dion Moult <dion@thinkmoult.com>
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
import ifcopenshell.api
import ifcopenshell.util.selector


class Patcher:
    def __init__(self, src, file, logger, query: str = ".IfcWall"):
        """Extract Elements

        Extract a subset of elements from an existing IFC data set and save it to a new IFC file.

        :param query: A query to select the subset of IFC elements.
        """
        self.src = src
        self.file = file
        self.logger = logger
        self.query = query

    def patch(self):
        self.contained_ins = {}
        self.aggregates = {}
        self.new = ifcopenshell.file(schema=self.file.wrapped_data.schema)
        self.owner_history = None
        for owner_history in self.file.by_type("IfcOwnerHistory"):
            self.owner_history = self.new.add(owner_history)
            break
        self.add_element(self.file.by_type("IfcProject")[0])
        selector = ifcopenshell.util.selector.Selector()
        for element in selector.parse(self.file, self.query):
            self.add_element(element)
        self.create_spatial_tree()
        self.file = self.new

    def add_element(self, element):
        new_element = self.append_asset(element)
        if not new_element:
            return
        for rel in getattr(element, "ContainedInStructure", []):
            spatial_element = rel.RelatingStructure
            new_spatial_element = self.append_asset(spatial_element)
            self.contained_ins.setdefault(spatial_element.GlobalId, set()).add(new_element)
            self.add_decomposition_parents(spatial_element, new_spatial_element)
        self.add_decomposition_parents(element, new_element)

    def append_asset(self, element):
        try:
            return self.new.by_guid(element.GlobalId)
        except:
            pass
        if element.is_a("IfcProject"):
            return self.new.add(element)
        return ifcopenshell.api.run("project.append_asset", self.new, library=self.file, element=element)

    def add_decomposition_parents(self, element, new_element):
        for rel in element.Decomposes:
            parent = rel.RelatingObject
            new_parent = self.append_asset(parent)
            self.aggregates.setdefault(parent.GlobalId, set()).add(new_element)
            self.add_decomposition_parents(parent, new_parent)

    def create_spatial_tree(self):
        for relating_structure, related_elements in self.contained_ins.items():
            self.new.createIfcRelContainedInSpatialStructure(
                ifcopenshell.guid.new(),
                self.owner_history,
                None,
                None,
                list(related_elements),
                self.new.by_guid(relating_structure),
            )
        for relating_object, related_objects in self.aggregates.items():
            self.new.createIfcRelAggregates(
                ifcopenshell.guid.new(),
                self.owner_history,
                None,
                None,
                self.new.by_guid(relating_object),
                list(related_objects),
            )
