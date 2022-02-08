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
        self.settings = {"style": None, "attributes": {}}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        for key, value in self.settings["attributes"].items():
            if key == "SurfaceColour":
                self.edit_surface_colour(value)
            elif key == "SpecularHighlight":
                self.edit_specular_highlight(value)
            elif self.is_colour_or_factor(key):
                self.edit_colour_or_factor(key, value)
            else:
                setattr(self.settings["style"], key, value)

    def edit_surface_colour(self, value):
        if not self.settings["style"].SurfaceColour:
            self.settings["style"].SurfaceColour = self.file.createIfcColourRgb(
                value.get("Name", None), value["Red"], value["Green"], value["Blue"]
            )
        self.settings["style"].SurfaceColour[0] = value.get("Name", None)
        self.settings["style"].SurfaceColour[1] = value["Red"]
        self.settings["style"].SurfaceColour[2] = value["Green"]
        self.settings["style"].SurfaceColour[3] = value["Blue"]

    def is_colour_or_factor(self, name):
        return name in [
            "DiffuseColour",
            "TransmissionColour",
            "DiffuseTransmissionColour",
            "ReflectionColour",
            "SpecularColour",
        ]

    def edit_colour_or_factor(self, name, value):
        if isinstance(value, dict):
            attribute = getattr(self.settings["style"], name)
            if not attribute or not attribute.is_a("IfcColourRgb"):
                colour = self.file.createIfcColourRgb(None, 0, 0, 0)
                setattr(self.settings["style"], name, colour)
                attribute = getattr(self.settings["style"], name)
            attribute[1] = value["Red"]
            attribute[2] = value["Green"]
            attribute[3] = value["Blue"]
        else:
            existing_value = getattr(self.settings["style"], name)
            if existing_value and existing_value.id():
                self.file.remove(existing_value)
            setattr(self.settings["style"], name, self.file.createIfcNormalisedRatioMeasure(value))

    def edit_specular_highlight(self, value):
        if value is None:
            self.settings["style"].SpecularHighlight = None
        elif value.get("IfcSpecularExponent", None):
            self.settings["style"].SpecularHighlight = self.file.createIfcSpecularExponent(value["IfcSpecularExponent"])
        elif value.get("IfcSpecularRoughness", None):
            self.settings["style"].SpecularHighlight = self.file.createIfcSpecularRoughness(
                value["IfcSpecularRoughness"]
            )
