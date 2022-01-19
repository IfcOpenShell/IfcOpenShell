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
            "map_conversion": {},
            "projected_crs": {},
            "true_north": [],
        }
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        map_conversion = self.file.by_type("IfcMapConversion")[0]
        projected_crs = self.file.by_type("IfcProjectedCRS")[0]
        for name, value in self.settings["map_conversion"].items():
            setattr(map_conversion, name, value)
        for name, value in self.settings["projected_crs"].items():
            setattr(projected_crs, name, value)
        self.set_true_north()

    def set_true_north(self):
        if self.settings["true_north"] == []:
            return
        for context in self.file.by_type("IfcGeometricRepresentationContext", include_subtypes=False):
            if context.TrueNorth:
                if len(self.file.get_inverse(context.TrueNorth)) != 1:
                    context.TrueNorth = self.file.create_entity("IfcDirection")
            else:
                context.TrueNorth = self.file.create_entity("IfcDirection")
            direction = context.TrueNorth
            if self.settings["true_north"] is None:
                context.TrueNorth = self.settings["true_north"]
            elif context.CoordinateSpaceDimension == 2:
                direction.DirectionRatios = self.settings["true_north"][0:2]
            else:
                direction.DirectionRatios = self.settings["true_north"][0:2] + [0.0]
