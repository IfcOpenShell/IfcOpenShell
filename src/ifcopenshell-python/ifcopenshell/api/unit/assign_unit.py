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


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {
            "units": None,
            "length": {"is_metric": True, "raw": "MILLIMETERS"},
            "area": {"is_metric": True, "raw": "METERS"},
            "volume": {"is_metric": True, "raw": "METERS"},
        }
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        # We're going to refactor this to split unit creation and assignment
        if self.settings["units"]:
            units = self.settings["units"]
        else:
            del self.settings["units"]  # TODO refactor
            units = []
            for unit_type, data in self.settings.items():
                if data["is_metric"]:
                    units.append(self.create_metric_unit(unit_type, data))
                else:
                    units.append(self.create_imperial_unit(unit_type, data))

        unit_assignment = self.get_unit_assignment()
        self.assign_units(unit_assignment, units)
        return unit_assignment

    def get_unit_assignment(self):
        unit_assignment = self.file.by_type("IfcUnitAssignment")
        if unit_assignment:
            unit_assignment = unit_assignment[0]
            # TODO: handle unit rewriting, which is complicated
        else:
            unit_assignment = self.file.createIfcUnitAssignment()
            if self.file.schema == "IFC2X3":
                self.file.by_type("IfcProject")[0].UnitsInContext = unit_assignment
            else:
                self.file.by_type("IfcContext")[0].UnitsInContext = unit_assignment
        return unit_assignment

    def assign_units(self, unit_assignment, new_units):
        units = set(unit_assignment.Units or [])
        for unit in new_units:
            units.add(unit)
        unit_assignment.Units = list(units)

    def create_metric_unit(self, unit_type, data):
        type_prefix = ""
        if unit_type == "area":
            type_prefix = "SQUARE_"
        elif unit_type == "volume":
            type_prefix = "CUBIC_"
        return self.file.createIfcSIUnit(
            None,
            "{}UNIT".format(unit_type.upper()),
            ifcopenshell.util.unit.get_prefix(data["raw"]),
            type_prefix + ifcopenshell.util.unit.get_unit_name(data["raw"]),
        )

    def create_imperial_unit(self, unit_type, data):
        if unit_type == "length":
            dimensional_exponents = self.file.createIfcDimensionalExponents(1, 0, 0, 0, 0, 0, 0)
            name_prefix = ""
        elif unit_type == "area":
            dimensional_exponents = self.file.createIfcDimensionalExponents(2, 0, 0, 0, 0, 0, 0)
            name_prefix = "square"
        elif unit_type == "volume":
            dimensional_exponents = self.file.createIfcDimensionalExponents(3, 0, 0, 0, 0, 0, 0)
            name_prefix = "cubic"
        si_unit = self.file.createIfcSIUnit(
            None,
            "{}UNIT".format(unit_type.upper()),
            None,
            "{}METRE".format(name_prefix.upper() + "_" if name_prefix else ""),
        )
        if data["raw"] == "INCHES":
            name = "{}inch".format(name_prefix + " " if name_prefix else "")
        elif data["raw"] == "FEET":
            name = "{}foot".format(name_prefix + " " if name_prefix else "")
        elif data["raw"] == "MILES":
            name = "{}mile".format(name_prefix + " " if name_prefix else "")
        elif data["raw"] == "THOU":
            name = "{}thou".format(name_prefix + " " if name_prefix else "")
        value_component = self.file.create_entity(
            "IfcReal", **{"wrappedValue": ifcopenshell.util.unit.si_conversions[name]}
        )
        conversion_factor = self.file.createIfcMeasureWithUnit(value_component, si_unit)
        return self.file.createIfcConversionBasedUnit(
            dimensional_exponents, "{}UNIT".format(unit_type.upper()), name, conversion_factor
        )
