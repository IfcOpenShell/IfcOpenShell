
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
        selector = ifcopenshell.util.selector.Selector()
        for element in selector.parse(self.file, self.query):
            self.add_element(element)
        self.create_spatial_tree()
        self.file = self.new

    def add_element(self, element):
        new_element = self.new.add(element)
        for rel in element.ContainedInStructure:
            spatial_element = rel.RelatingStructure
            new_spatial_element = self.new.add(spatial_element)
            self.contained_ins.setdefault(spatial_element.GlobalId, set()).add(new_element)
            self.add_spatial_tree(spatial_element, new_spatial_element)
        for rel in element.Decomposes:
            self.new.add(rel.RelatingObject)
            self.aggregates.setdefault(rel.RelatingObject.GlobalId, set()).add(new_element)
        for opening in element.HasOpenings:
            self.new.add(opening)
            self.new.add(opening.RelatedOpeningElement)

    def add_spatial_tree(self, spatial_element, new_spatial_element):
        for rel in spatial_element.Decomposes:
            new = self.new.add(rel.RelatingObject)
            self.aggregates.setdefault(rel.RelatingObject.GlobalId, set()).add(new_spatial_element)
            self.add_spatial_tree(rel.RelatingObject, new)

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
