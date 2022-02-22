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
        self.settings = {"style": None}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        self.purge_styled_items(self.settings["style"])
        for style in self.settings["style"].Styles or []:
            ifcopenshell.api.run("style.remove_surface_style", self.file, style=style)
        self.file.remove(self.settings["style"])

    def purge_styled_items(self, style):
        for inverse in self.file.get_inverse(style):
            if inverse.is_a("IfcStyledItem") and len(inverse.Styles) == 1:
                self.purge_styled_representations(inverse)
                self.file.remove(inverse)

    def purge_styled_representations(self, styled_item):
        for inverse in self.file.get_inverse(styled_item):
            if inverse.is_a("IfcStyledRepresentation") and len(inverse.Items) == 1:
                self.purge_material_definition_representations(inverse)
                self.file.remove(inverse)

    def purge_material_definition_representations(self, styled_representation):
        for inverse in self.file.get_inverse(styled_representation):
            if inverse.is_a("IfcMaterialDefinitionRepresentation") and len(inverse.Representations) == 1:
                self.file.remove(inverse)
