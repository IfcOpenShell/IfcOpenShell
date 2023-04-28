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
    def __init__(self, file, name="foot", conversion_offset=None):
        """Add a conversion based unit

        If you're in one of those countries who don't use SI units, you're
        probably simply using SI units converted into another unit. If you want
        to use _those_ units, you can create a conversion based unit with this
        function. You can choose from one of: inch, foot, yard, mile, square
        inch, square foot, square yard, acre, square mile, cubic inch, cubic
        foot, cubic yard, litre, fluid ounce UK, fluid ounce US, pint UK, pint
        US, gallon UK, gallon US, degree, ounce, pound, ton UK, ton US, lbf,
        kip, psi, ksi, minute, hour, day, btu, and fahrenheit.

        :param name: A converted name chosen from the list above.
        :type name: str
        :param conversion_offset: If you want to offset the conversion further
            by a set number, you may specify it here. For example, fahrenheit is
            1.8 * kelvin - 459.67. The -459.67 is the conversion offset. Note
            that this is just an example and you don't actually need to specify
            that for fahrenheit as it's built into this API function. For
            advanced users only.
        :type conversion_offset: float
        :return: The new IfcConversionBasedUnit or
            IfcConversionBasedUnitWithOffset
        :rtype: ifcopenshell.entity_instance.entity_instance

        Example:

        .. code:: python

            # Some common imperial measurements
            length = ifcopenshell.api.run("unit.add_conversion_based_unit", model, name="inch")
            area = ifcopenshell.api.run("unit.add_conversion_based_unit", model, name="square foot")

            # Make it our default units, if we are doing an imperial building
            ifcopenshell.api.run("unit.assign_unit", model, units=[length, area])
        """
        self.file = file
        self.settings = {"name": name, "conversion_offset": conversion_offset}

    def execute(self):
        unit_type = ifcopenshell.util.unit.imperial_types.get(self.settings["name"], "USERDEFINED")
        dimensions = ifcopenshell.util.unit.named_dimensions[unit_type]
        exponents = self.file.createIfcDimensionalExponents(*dimensions)
        si_name = ifcopenshell.util.unit.si_type_names[unit_type]
        si_unit = self.file.createIfcSIUnit(UnitType=unit_type, Name=si_name)

        conversion_real = ifcopenshell.util.unit.si_conversions.get(self.settings["name"], 1)
        value_component = self.file.create_entity("IfcReal", **{"wrappedValue": conversion_real})
        conversion_factor = self.file.createIfcMeasureWithUnit(value_component, si_unit)

        conversion_offset = self.settings["conversion_offset"]
        if not conversion_offset:
            conversion_offset = ifcopenshell.util.unit.si_offsets.get(self.settings["name"], 0)

        if conversion_offset:
            return self.file.createIfcConversionBasedUnitWithOffset(
                exponents,
                unit_type,
                self.settings["name"],
                conversion_factor,
                conversion_offset,
            )
        return self.file.createIfcConversionBasedUnit(exponents, unit_type, self.settings["name"], conversion_factor)
