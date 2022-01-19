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
    def __init__(self, file, **kwargs):
        """location, axis and ref_direction defines the plane"""
        self.file = file
        self.entity: "IfcRelSpaceBoundary"
        self.relating_space: "IfcSpace | IfcExternalSpatialElement"
        self.related_building_element: "IfcElement"
        self.parent_boundary: "IfcRelSpaceBoundary" = None
        self.corresponding_boundary: "IfcRelSpaceBoundary" = None
        for key, value in kwargs.items():
            setattr(self, key, value)

    def execute(self):
        self.entity.RelatingSpace = self.relating_space
        self.entity.RelatedBuildingElement = self.related_building_element
        if hasattr(self.entity, "ParentBoundary"):
            self.entity.ParentBoundary = self.parent_boundary
        if hasattr(self.entity, "CorrespondingBoundary"):
            self.entity.CorrespondingBoundary = self.corresponding_boundary
