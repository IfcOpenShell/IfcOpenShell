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

import ifcopenshell.api
import ifcopenshell.util.date


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"lag_time": None, "attributes": {}}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        for name, value in self.settings["attributes"].items():
            if name == "LagValue" and value is not None:
                if isinstance(value, float):
                    value = self.file.createIfcRatioMeasure(value)
                else:
                    value = self.file.createIfcDuration(
                        ifcopenshell.util.date.datetime2ifc(value, "IfcDuration")
                    )
            setattr(self.settings["lag_time"], name, value)
        for rel in [
            r
            for r in self.file.get_inverse(self.settings["lag_time"])
            if r.is_a("IfcRelSequence")
        ]:
            ifcopenshell.api.run(
                "sequence.cascade_schedule", self.file, task=rel.RelatedProcess
            )
