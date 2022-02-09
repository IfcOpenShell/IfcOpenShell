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


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"style": None, "ifc_class": "IfcSurfaceStyleRendering", "attributes": {}}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        style_item = self.file.create_entity(self.settings["ifc_class"])
        ifcopenshell.api.run(
            "style.edit_surface_style", self.file, style=style_item, attributes=self.settings["attributes"]
        )
        styles = list(self.settings["style"].Styles or [])

        select_class = self.settings["ifc_class"]
        if select_class == "IfcSurfaceStyleRendering":
            select_class = "IfcSurfaceStyleShading"
        duplicate_items = [s for s in styles if s.is_a(select_class)]
        for duplicate_item in duplicate_items:
            ifcopenshell.api.run("style.remove_surface_style", self.file, style=duplicate_item)

        styles = list(self.settings["style"].Styles or [])
        styles.append(style_item)
        self.settings["style"].Styles = styles
        return style_item
