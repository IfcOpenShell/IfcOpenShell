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
        self.settings = {
            "shape_representation": None,
            "styles": [],
            "should_use_presentation_style_assignment": False,
        }
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        if not self.settings["styles"]:
            return []
        self.results = []
        for element in self.file.traverse(self.settings["shape_representation"]):
            if not element.is_a("IfcShapeRepresentation"):
                continue
            for item in element.Items:
                if not item.is_a("IfcGeometricRepresentationItem"):
                    continue
                if self.settings["styles"]:
                    # If there are more items than styles, fallback to using the last style
                    style = self.settings["styles"].pop(0)
                name = style.Name
                if self.file.schema == "IFC2X3" or self.settings["should_use_presentation_style_assignment"]:
                    style = self.file.createIfcPresentationStyleAssignment([style])
                self.results.append(self.file.createIfcStyledItem(item, [style], name))
        return self.results
