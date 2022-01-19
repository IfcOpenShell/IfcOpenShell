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

import ifcopenshell


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {
            "relating_product": None,
            "related_object": None,
        }
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        products = set()
        related_object = None
        if self.settings["related_object"]:
            related_object = self.settings["related_object"]
        elif self.settings["relating_product"]:
            for reference in self.settings["relating_product"].ReferencedBy:
                if reference.is_a("IfcRelAssignsToProduct"):
                    related_object = referenced_by.RelatedObjects[0]
        if related_object:
            assignments = self.settings["related_object"].HasAssignments
            for assignment in assignments:
                if assignment.is_a("IfcRelAssignsToProduct"):
                    products.add(assignment.RelatingProduct.id())
        return products
