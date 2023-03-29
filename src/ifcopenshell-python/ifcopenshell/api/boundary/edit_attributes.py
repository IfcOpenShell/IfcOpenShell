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


class Usecase:
    def __init__(self, file, entity=None, relating_space=None, related_building_element=None, parent_boundary=None, corresponding_boundary=None):
        """Modify the relationships of a space boundary relationship

        Currently this function is quite minimal and offers no advantage to
        manual assignment of the space boundary attributes.

        :param entity: The IfcRelSpaceBoundary to modify
        :type entity: ifcopenshell.entity_instance.entity_instance
        :param relating_space: The IfcSpace or IfcExternalSpatialElement that
            the space boundary is related to.
        :type relating_space: ifcopenshell.entity_instance.entity_instance
        :param related_building_element: The IfcElement that defines the
            boundary, typically an IfcWall.
        :type relating_space: ifcopenshell.entity_instance.entity_instance
        :param parent_boundary: A parent IfcRelSpaceBoundary, only provided if
            this is an inner boundary. This can apply to 1st and 2nd level
            boundaries.
        :type parent_boundary: ifcopenshell.entity_instance.entity_instance,
            optional
        :param corresponding_boundary: The other IfcRelSpaceBoundary on the
            other side of the related element. The pair together represents a
            thermal boundary. This only applies to 2nd level boundaries.
        :type corresponding_boundary: ifcopenshell.entity_instance.entity_instance,
            optional
        :return: None
        :rtype: None
        """
        self.file = file
        self.entity = entity
        self.relating_space = relating_space
        self.related_building_element = related_building_element
        self.parent_boundary = parent_boundary
        self.corresponding_boundary = corresponding_boundary

    def execute(self):
        self.entity.RelatingSpace = self.relating_space
        self.entity.RelatedBuildingElement = self.related_building_element
        if hasattr(self.entity, "ParentBoundary"):
            self.entity.ParentBoundary = self.parent_boundary
        if hasattr(self.entity, "CorrespondingBoundary"):
            self.entity.CorrespondingBoundary = self.corresponding_boundary
