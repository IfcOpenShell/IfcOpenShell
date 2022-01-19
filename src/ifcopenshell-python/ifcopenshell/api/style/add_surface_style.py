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
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"style": None, "ifc_class": "IfcSurfaceStyleRendering", "attributes": {}}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        for key, value in self.settings["attributes"].items():
            if key == "SurfaceColour" and value:
                self.settings["attributes"][key] = self.create_colour_rgb(value)
            if key == "DiffuseColour" and isinstance(value, dict):
                self.settings["attributes"][key] = self.create_colour_rgb(value)

        style_item = self.file.create_entity(self.settings["ifc_class"], **self.settings["attributes"])
        styles = list(self.settings["style"].Styles or [])

        duplicate_items = [s for s in styles if s.is_a(self.settings["ifc_class"])]
        for duplicate_item in duplicate_items:
            self.file.remove(duplicate_item)

        styles.append(style_item)
        self.settings["style"].Styles = styles
        return style_item

    def create_colour_rgb(self, value):
        return self.file.createIfcColourRgb(value["Name"], value["Red"], value["Green"], value["Blue"])
