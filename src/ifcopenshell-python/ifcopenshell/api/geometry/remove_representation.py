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

import ifcopenshell.util.element


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"representation": None}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        styled_items = set()
        presentation_layer_assignments = set()
        textures = set()
        for subelement in self.file.traverse(self.settings["representation"]):
            if subelement.is_a("IfcRepresentationItem"):
                [styled_items.add(s) for s in subelement.StyledByItem or []]
                [textures.add(t) for t in getattr(subelement, "HasTextures", []) or []]
            elif subelement.is_a("IfcRepresentation"):
                for inverse in self.file.get_inverse(subelement):
                    if inverse.is_a("IfcPresentationLayerAssignment"):
                        presentation_layer_assignments.add(inverse)

        ifcopenshell.util.element.remove_deep2(
            self.file,
            self.settings["representation"],
            also_consider=list(styled_items | presentation_layer_assignments),
            do_not_delete=self.file.by_type("IfcGeometricRepresentationContext"),
        )

        for texture in textures:
            ifcopenshell.util.element.remove_deep2(self.file, texture)

        for element in styled_items:
            if not element.Item:
                self.file.remove(element)
        for element in presentation_layer_assignments:
            if len(element.AssignedItems) == 0:
                self.file.remove(element)
