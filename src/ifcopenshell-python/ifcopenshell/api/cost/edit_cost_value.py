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
import ifcopenshell.util.unit
import ifcopenshell.util.element


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"cost_value": None, "attributes": {}}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        for name, value in self.settings["attributes"].items():
            if name == "AppliedValue" and value is not None:
                # TODO: support all applied value select types
                value = self.file.createIfcMonetaryMeasure(value)
            elif name == "UnitBasis":
                old_unit_basis = self.settings["cost_value"].UnitBasis
                if value:
                    value_component = self.file.create_entity(
                        ifcopenshell.util.unit.get_unit_measure_class(value["UnitComponent"].UnitType),
                        value["ValueComponent"],
                    )
                    value = self.file.create_entity("IfcMeasureWithUnit", value_component, value["UnitComponent"])
                if old_unit_basis and len(self.file.get_inverse(old_unit_basis)) == 0:
                    ifcopenshell.util.element.remove_deep(self.file, old_unit_basis)
            setattr(self.settings["cost_value"], name, value)
