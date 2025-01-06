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
from typing import Optional


def assign_unit(
    file: ifcopenshell.file,
    units: Optional[list[ifcopenshell.entity_instance]] = None,
    length: Optional[dict] = None,
    area: Optional[dict] = None,
    volume: Optional[dict] = None,
) -> ifcopenshell.entity_instance:
    """Assign default project units

    Whenever a unitised quantity is specified, such as a length, area,
    voltage, pressure, etc, these project units are used by default.

    It is also possible to override units for specific properties. For
    example, generally you might want square metres for area measurements,
    but you might want square millimeters for the measurements of the cross
    sectional area of cables in cable trays. However, this function only
    deals with the default project units.

    :param units: A list of units to assign as project defaults. See
        ifcopenshell.api.unit.add_si_unit, unit.add_conversion_based_unit,
        and unit.add_monetary_unit for information on how to create units.
    :type units: list[ifcopenshell.entity_instance],optional
    :return: The IfcUnitAssignment element
    :rtype: ifcopenshell.entity_instance

    Example:

    .. code:: python

        # You need a project before you can assign units.
        ifcopenshell.api.root.create_entity(model, ifc_class="IfcProject")

        # Millimeters and square meters
        length = ifcopenshell.api.unit.add_si_unit(model, unit_type="LENGTHUNIT", prefix="MILLI")
        area = ifcopenshell.api.unit.add_si_unit(model, unit_type="AREAUNIT")

        # Make it our default units, if we are doing a metric building
        ifcopenshell.api.unit.assign_unit(model, units=[length, area])

        # Alternatively, you may specify without any arguments to
        # automatically create millimeters, square meters, and cubic meters
        # as a convenience for testing purposes. Sorry imperial folks, we
        # prioritise metric here.
        ifcopenshell.api.unit.assign_unit(model)
    """
    usecase = Usecase()
    usecase.file = file
    usecase.settings = {"units": units}
    # This is a convenience function, likely to be deprecated in the future.
    usecase.settings["length"] = length or {"is_metric": True, "raw": "MILLIMETERS"}
    usecase.settings["area"] = area or {"is_metric": True, "raw": "METERS"}
    usecase.settings["volume"] = volume or {"is_metric": True, "raw": "METERS"}
    return usecase.execute()


class Usecase:
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

    def get_unit_assignment(self) -> ifcopenshell.entity_instance:
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

    def assign_units(
        self, unit_assignment: ifcopenshell.entity_instance, new_units: list[ifcopenshell.entity_instance]
    ) -> None:
        units = set(unit_assignment.Units or [])
        for unit in new_units:
            units.add(unit)
        unit_assignment.Units = list(units)

    def create_metric_unit(self, unit_type: str, data: dict) -> ifcopenshell.entity_instance:
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

    def create_imperial_unit(self, unit_type: str, data: dict) -> ifcopenshell.entity_instance:
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
