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
import ifcopenshell.api
import ifcopenshell.util.element


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {
            "related_object": None,
            "relating_type": None,
        }
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        if not self.settings["relating_type"].RepresentationMaps:
            return
        representations = []
        if self.settings["related_object"].Representation:
            representations = self.settings["related_object"].Representation.Representations
        for representation in representations:
            ifcopenshell.api.run(
                "geometry.unassign_representation",
                self.file,
                product=self.settings["related_object"],
                representation=representation,
            )
            ifcopenshell.api.run("geometry.remove_representation", self.file, **{"representation": representation})
        for representation_map in self.settings["relating_type"].RepresentationMaps:
            representation = representation_map.MappedRepresentation
            mapped_representation = ifcopenshell.api.run(
                "geometry.map_representation", self.file, representation=representation
            )
            ifcopenshell.api.run(
                "geometry.assign_representation",
                self.file,
                product=self.settings["related_object"],
                representation=mapped_representation,
            )
