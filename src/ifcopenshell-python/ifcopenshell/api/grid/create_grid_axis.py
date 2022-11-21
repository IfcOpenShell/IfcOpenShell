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
            "axis_tag": "A",
            "same_sense": True,
            "uvw_axes": "UAxes",  # Choose which axes
            "grid": None,
        }
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        element = self.file.create_entity(
            "IfcGridAxis", **{"AxisTag": self.settings["axis_tag"], "SameSense": self.settings["same_sense"]}
        )
        axes = list(getattr(self.settings["grid"], self.settings["uvw_axes"]) or [])
        axes.append(element)
        setattr(self.settings["grid"], self.settings["uvw_axes"], axes)
        return element
