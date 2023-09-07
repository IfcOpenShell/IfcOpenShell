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

from math import pi
from fractions import Fraction

prefixes = {
    "EXA": 1e18,
    "PETA": 1e15,
    "TERA": 1e12,
    "GIGA": 1e9,
    "MEGA": 1e6,
    "KILO": 1e3,
    "HECTO": 1e2,
    "DECA": 1e1,
    "DECI": 1e-1,
    "CENTI": 1e-2,
    "MILLI": 1e-3,
    "MICRO": 1e-6,
    "NANO": 1e-9,
    "PICO": 1e-12,
    "FEMTO": 1e-15,
    "ATTO": 1e-18,
}

unit_names = [
    "AMPERE",
    "BECQUEREL",
    "CANDELA",
    "COULOMB",
    "CUBIC_METRE",
    "DEGREE_CELSIUS",
    "FARAD",
    "GRAM",
    "GRAY",
    "HENRY",
    "HERTZ",
    "JOULE",
    "KELVIN",
    "LUMEN",
    "LUX",
    "MOLE",
    "NEWTON",
    "OHM",
    "PASCAL",
    "RADIAN",
    "SECOND",
    "SIEMENS",
    "SIEVERT",
    "SQUARE_METRE",
    "METRE",
    "STERADIAN",
    "TESLA",
    "VOLT",
    "WATT",
    "WEBER",
]

si_dimensions = {
    "METRE": (1, 0, 0, 0, 0, 0, 0),
    "SQUARE_METRE": (2, 0, 0, 0, 0, 0, 0),
    "CUBIC_METRE": (3, 0, 0, 0, 0, 0, 0),
    "GRAM": (0, 1, 0, 0, 0, 0, 0),
    "SECOND": (0, 0, 1, 0, 0, 0, 0),
    "AMPERE": (0, 0, 0, 1, 0, 0, 0),
    "KELVIN": (0, 0, 0, 0, 1, 0, 0),
    "MOLE": (0, 0, 0, 0, 0, 1, 0),
    "CANDELA": (0, 0, 0, 0, 0, 0, 1),
    "RADIAN": (0, 0, 0, 0, 0, 0, 0),
    "STERADIAN": (0, 0, 0, 0, 0, 0, 0),
    "HERTZ": (0, 0, -1, 0, 0, 0, 0),
    "NEWTON": (1, 1, -2, 0, 0, 0, 0),
    "PASCAL": (-1, 1, -2, 0, 0, 0, 0),
    "JOULE": (2, 1, -2, 0, 0, 0, 0),
    "WATT": (2, 1, -3, 0, 0, 0, 0),
    "COULOMB": (0, 0, 1, 1, 0, 0, 0),
    "VOLT": (2, 1, -3, -1, 0, 0, 0),
    "FARAD": (-2, -1, 4, 2, 0, 0, 0),
    "OHM": (2, 1, -3, -2, 0, 0, 0),
    "SIEMENS": (-2, -1, 3, 2, 0, 0, 0),
    "WEBER": (2, 1, -2, -1, 0, 0, 0),
    "TESLA": (0, 1, -2, -1, 0, 0, 0),
    "HENRY": (2, 1, -2, -2, 0, 0, 0),
    "DEGREE_CELSIUS": (0, 0, 0, 0, 1, 0, 0),
    "LUMEN": (0, 0, 0, 0, 0, 0, 1),
    "LUX": (-2, 0, 0, 0, 0, 0, 1),
    "BECQUEREL": (0, 0, -1, 0, 0, 0, 0),
    "GRAY": (2, 0, -2, 0, 0, 0, 0),
    "SIEVERT": (2, 0, -2, 0, 0, 0, 0),
    "OTHERWISE": (0, 0, 0, 0, 0, 0, 0),
}

# See https://github.com/buildingSMART/IFC4.3.x-development/issues/72
si_type_names = {
    "ABSORBEDDOSEUNIT": "GRAY",
    "AMOUNTOFSUBSTANCEUNIT": "MOLE",
    "AREAUNIT": "SQUARE_METRE",
    "DOSEEQUIVALENTUNIT": "SIEVERT",
    "ELECTRICCAPACITANCEUNIT": "FARAD",
    "ELECTRICCHARGEUNIT": "COULOMB",
    "ELECTRICCONDUCTANCEUNIT": "SIEMENS",
    "ELECTRICCURRENTUNIT": "AMPERE",
    "ELECTRICRESISTANCEUNIT": "OHM",
    "ELECTRICVOLTAGEUNIT": "VOLT",
    "ENERGYUNIT": "JOULE",
    "FORCEUNIT": "NEWTON",
    "FREQUENCYUNIT": "HERTZ",
    "ILLUMINANCEUNIT": "LUX",
    "INDUCTANCEUNIT": "HENRY",
    "LENGTHUNIT": "METRE",
    "LUMINOUSFLUXUNIT": "LUMEN",
    "LUMINOUSINTENSITYUNIT": "CANDELA",
    "MAGNETICFLUXDENSITYUNIT": "TESLA",
    "MAGNETICFLUXUNIT": "WEBER",
    "MASSUNIT": "GRAM",
    "PLANEANGLEUNIT": "RADIAN",
    "POWERUNIT": "WATT",
    "PRESSUREUNIT": "PASCAL",
    "RADIOACTIVITYUNIT": "BECQUEREL",
    "SOLIDANGLEUNIT": "STERADIAN",
    "THERMODYNAMICTEMPERATUREUNIT": "KELVIN",  # Or, DEGREE_CELSIUS, but this is a quirk of IFC
    "TIMEUNIT": "SECOND",
    "VOLUMEUNIT": "CUBIC_METRE",
    "USERDEFINED": "METRE",
}

# See IfcDimensionalExponents:
# (Length, Mass, Time, ElectricCurrent, ThermodynamicTemperature, AmountOfSubstance, LuminousIntensity)
named_dimensions = {
    "ABSORBEDDOSEUNIT": (2, 0, -2, 0, 0, 0, 0),
    "AMOUNTOFSUBSTANCEUNIT": (0, 0, 0, 0, 0, 1, 0),
    "AREAUNIT": (2, 0, 0, 0, 0, 0, 0),
    "DOSEEQUIVALENTUNIT": (2, 0, -2, 0, 0, 0, 0),
    "ELECTRICCAPACITANCEUNIT": (-2, -1, 4, 2, 0, 0, 0),
    "ELECTRICCHARGEUNIT": (0, 0, 1, 1, 0, 0, 0),
    "ELECTRICCONDUCTANCEUNIT": (-2, -1, 3, 2, 0, 0, 0),
    "ELECTRICCURRENTUNIT": (0, 0, 0, 1, 0, 0, 0),
    "ELECTRICRESISTANCEUNIT": (2, 1, -3, -2, 0, 0, 0),
    "ELECTRICVOLTAGEUNIT": (2, 1, -3, -1, 0, 0, 0),
    "ENERGYUNIT": (2, 1, -2, 0, 0, 0, 0),
    "FORCEUNIT": (1, 1, -2, 0, 0, 0, 0),
    "FREQUENCYUNIT": (0, 0, -1, 0, 0, 0, 0),
    "ILLUMINANCEUNIT": (-2, 0, 0, 0, 0, 1, 1),
    "INDUCTANCEUNIT": (2, 1, -2, -2, 0, 0, 0),
    "LENGTHUNIT": (1, 0, 0, 0, 0, 0, 0),
    "LUMINOUSFLUXUNIT": (0, 0, 0, 0, 0, 1, 1),
    "LUMINOUSINTENSITYUNIT": (0, 0, 0, 0, 0, 0, 1),
    "MAGNETICFLUXDENSITYUNIT": (0, 1, -2, -1, 0, 0, 0),
    "MAGNETICFLUXUNIT": (2, 1, -2, -1, 0, 0, 0),
    "MASSUNIT": (0, 1, 0, 0, 0, 0, 0),
    "PLANEANGLEUNIT": (0, 0, 0, 0, 0, 0, 0),
    "POWERUNIT": (2, 1, -3, 0, 0, 0, 0),
    "PRESSUREUNIT": (-1, 1, -2, 0, 0, 0, 0),
    "RADIOACTIVITYUNIT": (0, 0, -1, 0, 0, 0, 0),
    "SOLIDANGLEUNIT": (0, 0, 0, 0, 0, 0, 0),
    "THERMODYNAMICTEMPERATUREUNIT": (0, 0, 0, 0, 1, 0, 0),
    "TIMEUNIT": (0, 0, 1, 0, 0, 0, 0),
    "VOLUMEUNIT": (3, 0, 0, 0, 0, 0, 0),
    "USERDEFINED": (0, 0, 0, 0, 0, 0, 0),
}

si_conversions = {
    "thou": 0.0000254,
    "inch": 0.0254,
    "foot": 0.3048,
    "yard": 0.914,
    "mile": 1609,
    "square thou": 6.4516e-10,
    "square inch": 0.0006452,
    "square foot": 0.09290304,
    "square yard": 0.83612736,
    "acre": 4046.86,
    "square mile": 2588881,
    "cubic thou": 1.6387064e-14,
    "cubic inch": 0.00001639,
    "cubic foot": 0.02831684671168849,
    "cubic yard": 0.7636,
    "cubic mile": 4165509529,
    "litre": 0.001,
    "fluid ounce UK": 0.0000284130625,
    "fluid ounce US": 0.00002957353,
    "pint UK": 0.000568,
    "pint US": 0.000473,
    "gallon UK": 0.004546,
    "gallon US": 0.003785,
    "degree": pi / 180,
    "ounce": 0.02835,
    "pound": 0.454,
    "ton UK": 1016.0469088,
    "ton US": 907.18474,
    "lbf": 4.4482216153,
    "kip": 4448.2216153,
    "psi": 6894.7572932,
    "ksi": 6894757.2932,
    "minute": 60,
    "hour": 3600,
    "day": 86400,
    "btu": 1055.056,
    "fahrenheit": 1.8,
}


si_offsets = {
    "fahrenheit": -459.67,
}


imperial_types = {
    "thou": "LENGTHUNIT",
    "inch": "LENGTHUNIT",
    "foot": "LENGTHUNIT",
    "yard": "LENGTHUNIT",
    "mile": "LENGTHUNIT",
    "square thou": "AREAUNIT",
    "square inch": "AREAUNIT",
    "square foot": "AREAUNIT",
    "square yard": "AREAUNIT",
    "acre": "AREAUNIT",
    "square mile": "AREAUNIT",
    "cubic thou": "VOLUMEUNIT",
    "cubic inch": "VOLUMEUNIT",
    "cubic foot": "VOLUMEUNIT",
    "cubic yard": "VOLUMEUNIT",
    "cubic mile": "VOLUMEUNIT",
    "litre": "VOLUMEUNIT",
    "fluid ounce UK": "VOLUMEUNIT",
    "fluid ounce US": "VOLUMEUNIT",
    "pint UK": "VOLUMEUNIT",
    "pint US": "VOLUMEUNIT",
    "gallon UK": "VOLUMEUNIT",
    "gallon US": "VOLUMEUNIT",
    "degree": "PLANEANGLEUNIT",
    "ounce": "MASSUNIT",
    "pound": "MASSUNIT",
    "ton UK": "MASSUNIT",
    "ton US": "MASSUNIT",
    "lbf": "FORCEUNIT",
    "kip": "FORCEUNIT",
    "psi": "PRESSUREUNIT",
    "ksi": "PRESSUREUNIT",
    "minute": "TIMEUNIT",
    "hour": "TIMEUNIT",
    "day": "TIMEUNIT",
    "btu": "ENERGYUNIT",
    "fahrenheit": "THERMODYNAMICTEMPERATUREUNIT",
}


prefix_symbols = {
    "EXA": "E",
    "PETA": "P",
    "TERA": "T",
    "GIGA": "G",
    "MEGA": "M",
    "KILO": "k",
    "HECTO": "h",
    "DECA": "da",
    "DECI": "d",
    "CENTI": "c",
    "MILLI": "m",
    "MICRO": "μ",
    "NANO": "n",
    "PICO": "p",
    "FEMTO": "f",
    "ATTO": "a",
}

unit_symbols = {
    # si units
    "CUBIC_METRE": "m3",
    "GRAM": "g",
    "SECOND": "s",
    "SQUARE_METRE": "m2",
    "METRE": "m",
    # non si units
    "cubic inch": "in3",
    "cubic foot": "ft3",
    "cubic yard": "yd3",
    "square inch": "in2",
    "square foot": "ft2",
    "square yard": "yd2",
    "square mile": "mi2",
}


def get_prefix(text):
    if text:
        for prefix in prefixes.keys():
            if prefix in text.upper():
                return prefix


def get_prefix_multiplier(text):
    if not text:
        return 1
    prefix = get_prefix(text)
    if prefix:
        return prefixes[prefix]
    return 1


def get_unit_name(text):
    text = text.upper().replace("METER", "METRE")
    for name in unit_names:
        if name.replace("_", " ") in text:
            return name


def get_si_dimensions(name):
    return si_dimensions.get(name, si_dimensions["OTHERWISE"])


def get_named_dimensions(name):
    return named_dimensions.get(name, (0, 0, 0, 0, 0, 0, 0))


def get_unit_assignment(ifc_file):
    unit_assignments = ifc_file.by_type("IfcUnitAssignment")
    if unit_assignments:
        return unit_assignments[0]


def get_project_unit(ifc_file, unit_type):
    """Get the default project unit of a particular unit type

    :param ifc_file: The IFC file.
    :type ifc_file: ifcopenshell.file.file
    :param unit_type: The type of unit, taken from the list of IFC unit types,
        such as "LENGTHUNIT".
    :type unit_type: str
    :return: The IFC unit entity, or nothing if there is no default project unit
        defined.
    :rtype: ifcopenshell.entity_instance,None
    """
    unit_assignment = get_unit_assignment(ifc_file)
    if unit_assignment:
        for unit in unit_assignment.Units or []:
            if getattr(unit, "UnitType", None) == unit_type:
                return unit


def get_property_unit(prop, ifc_file):
    unit = getattr(prop, "Unit", None)
    if unit:
        return unit
    unit_assignment = get_unit_assignment(ifc_file)
    if not unit_assignment:
        return
    entity = prop.wrapped_data.declaration().as_entity()
    if prop.is_a("IfcPhysicalSimpleQuantity"):
        measure_class = entity.attribute_by_index(3).type_of_attribute().declared_type().name()
    elif prop.is_a("IfcPropertySingleValue") and prop.NominalValue:
        measure_class = prop.NominalValue.is_a()
    elif prop.is_a("IfcPropertyEnumeratedValue") and prop.EnumerationValues:
        measure_class = prop.EnumerationValues[0].is_a()
    elif prop.is_a("IfcPropertyListValue") and prop.ListValues:
        measure_class = prop.ListValues[0].is_a()
    elif prop.is_a("IfcPropertyBoundedValue"):
        if prop.UpperBoundValue:
            measure_class = prop.UpperBoundValue.is_a()
        elif prop.LowerBoundValue:
            measure_class = prop.LowerBoundValue.is_a()
        elif prop.SetPointValue:
            measure_class = prop.SetPointValue.is_a()
    elif prop.is_a("IfcPropertyTableValue"):
        table_units = {}
        for attribute in ["Defining", "Defined"]:
            if getattr(prop, f"{attribute}Unit"):
                table_units[f"{attribute}Unit"] = getattr(prop, f"{attribute}Unit")
            elif getattr(prop, f"{attribute}Values"):
                measure_class = getattr(prop, f"{attribute}Values")[0].is_a()
                unit_type = get_measure_unit_type(measure_class)
                units = [u for u in unit_assignment.Units if getattr(u, "UnitType", None) == unit_type]
                if units:
                    table_units[f"{attribute}Unit"] = units[0]
                else:
                    table_units[f"{attribute}Unit"] = None
            else:
                table_units[f"{attribute}Unit"] = None
        return table_units
    unit_type = get_measure_unit_type(measure_class)
    units = [u for u in unit_assignment.Units if getattr(u, "UnitType", None) == unit_type]
    if units:
        return units[0]


def get_unit_measure_class(unit_type):
    if unit_type == "USERDEFINED":
        # See https://github.com/buildingSMART/IFC4.3.x-development/issues/71
        return "IfcNumericMeasure"
    return "Ifc" + unit_type[0:-4].lower().capitalize() + "Measure"


def get_measure_unit_type(measure_class):
    if measure_class == "IfcNumericMeasure":
        # See https://github.com/buildingSMART/IFC4.3.x-development/issues/71
        return "USERDEFINED"
    for text in ("Ifc", "Measure", "Non", "Positive", "Negative"):
        measure_class = measure_class.replace(text, "")
    return measure_class.upper() + "UNIT"


def get_symbol_measure_class(symbol):
    # Dumb, but everybody gets it, unlike regex golf
    if not symbol:
        return "IfcNumericMeasure"
    symbol = symbol.lower()
    if symbol in ["km", "m", "cm", "mm", "ly", "lf", "lin", "yd", "ft", "in"]:
        return "IfcLengthMeasure"
    elif symbol in ["km2", "m2", "cm2", "mm2", "sqy", "sqft", "sqin"]:
        return "IfcAreaMeasure"
    elif symbol in ["km3", "m3", "cm3", "mm3", "cy", "cft", "cin"]:
        return "IfcVolumeMeasure"
    elif symbol in ["kg", "g", "mt", "kt", "t"]:
        return "IfcMassMeasure"
    elif symbol in ["day", "d", "hour", "hr", "h", "minute", "min", "m", "second", "sec", "s"]:
        return "IfcTimeMeasure"
    return "IfcNumericMeasure"


def get_symbol_quantity_class(symbol):
    # Dumb, but everybody gets it, unlike regex golf
    if not symbol:
        return "IfcQuantityCount"
    symbol = symbol.lower()
    if symbol in ["km", "m", "cm", "mm", "ly", "lf", "lin", "yd", "ft", "in"]:
        return "IfcQuantityLength"
    elif symbol in ["km2", "m2", "cm2", "mm2", "sqy", "sqft", "sqin"]:
        return "IfcQuantityArea"
    elif symbol in ["km3", "m3", "cm3", "mm3", "cy", "cft", "cin"]:
        return "IfcQuantityVolume"
    elif symbol in ["kg", "g", "mt", "kt", "t"]:
        return "IfcQuantityWeight"
    elif symbol in ["day", "d", "hour", "hr", "h", "minute", "min", "m", "second", "sec", "s"]:
        return "IfcQuantityTime"
    return "IfcQuantityCount"


def get_unit_symbol(unit):
    symbol = ""
    if unit.is_a("IfcSIUnit"):
        symbol += prefix_symbols.get(unit.Prefix, "")
    symbol += unit_symbols.get(unit.Name.replace("METER", "METRE"), "?")
    return symbol


def convert_unit(value, from_unit, to_unit):
    """Convert from one unit to another unit

    :param value: The numeric value you want to convert
    :type value: float
    :param from_unit: The IfcNamedUnit to confirm from.
    :type from_unit: ifcopenshell.entity_instance.entity_instance
    :param to_unit: The IfcNamedUnit to confirm from.
    :type to_unit: ifcopenshell.entity_instance.entity_instance
    :return: The converted value.
    :rtype: float
    """
    return convert(
        value, getattr(from_unit, "Prefix", None), from_unit.Name, getattr(to_unit, "Prefix", None), to_unit.Name
    )


def convert(value, from_prefix, from_unit, to_prefix, to_unit):
    """Converts between length, area, and volume units

    In this case, you manually specify the names and (optionally) prefixes to
    convert to and from. In case you want to automatically convert to units
    already available as IFC entities, consider using convert_unit() instead.

    :param value: The numeric value you want to convert
    :type value: float
    :param from_prefix: A prefix from IfcSIPrefix. Can be None.
    :type from_prefix: str,optional
    :param from_unit: IfcSIUnitName or IfcConversionBasedUnit.Name
    :type from_unit: str
    :param to_prefix: A prefix from IfcSIPrefix. Can be None.
    :type to_prefix: str,optional
    :param to_unit: IfcSIUnitName or IfcConversionBasedUnit.Name
    :type to_unit: str
    :return: The converted value.
    :rtype: float
    """
    if from_unit in si_conversions:
        value *= si_conversions[from_unit]
    elif from_prefix:
        value *= get_prefix_multiplier(from_prefix)
        if "SQUARE" in from_unit:
            value *= get_prefix_multiplier(from_prefix)
        elif "CUBIC" in from_unit:
            value *= get_prefix_multiplier(from_prefix)
            value *= get_prefix_multiplier(from_prefix)
    if to_unit in si_conversions:
        return value * (1 / si_conversions[to_unit])
    elif to_prefix:
        value *= 1 / get_prefix_multiplier(to_prefix)
        if "SQUARE" in from_unit:
            value *= 1 / get_prefix_multiplier(to_prefix)
        elif "CUBIC" in from_unit:
            value *= 1 / get_prefix_multiplier(to_prefix)
            value *= 1 / get_prefix_multiplier(to_prefix)
    return value


def calculate_unit_scale(ifc_file):
    """Returns a unit scale factor to convert to and from IFC project length units and SI meters

    Example:

    .. code:: python

        ifc_project_length * unit_scale = si_meters
        si_meters / unit_scale = ifc_project_length

    :param ifc_file: The IFC file.
    :type ifc_file: ifcopenshell.file.file
    :returns: The scale factor
    :rtype: float
    """
    if not ifc_file.by_type("IfcUnitAssignment"):
        return 1
    units = ifc_file.by_type("IfcUnitAssignment")[0]
    unit_scale = 1
    for unit in units.Units:
        if not hasattr(unit, "UnitType") or unit.UnitType != "LENGTHUNIT":
            continue
        while unit.is_a("IfcConversionBasedUnit"):
            unit_scale *= unit.ConversionFactor.ValueComponent.wrappedValue
            unit = unit.ConversionFactor.UnitComponent
        if unit.is_a("IfcSIUnit"):
            unit_scale *= get_prefix_multiplier(unit.Prefix)
    return unit_scale


def format_length(
    value,
    precision,
    decimal_places=2,
    suppress_zero_inches=True,
    unit_system="imperial",
    input_unit="foot",
    output_unit="foot",
):
    """Formats a length for readability and imperial formatting

    :param value: The value in meters if metric, or either decimal feet or
        inches if imperial depending on input_unit.
    :type value: float
    :param precision: How precise the format should be. I.e. round to nearest.
        For imperial, it is 1/Nth. E.g. 12 means to the nearest 1/12th of an
        inch.
    :type precision: float
    :param decimal_places: How many decimal places to display. Defaults to 2.
    :type decimal_places: int
    :param suppress_zero_inches: If imperial, whether or not to supress the
        inches if the inches is zero.
    :type suppress_zero_inches: bool
    :param unit_system: Choose whether your value is "metric" or "imperial"
    :type unit_system: str
    :param input_unit: If imperial, specify whether your value is "foot" or
        "inch".
    :type input_unit: str
    :param output_unit: If imperial, specify whether your value is "foot" to
        format as both feet and inches, or "inch" if only inches should be
        shown.
    """
    if unit_system == "imperial":
        if input_unit == "foot":
            feet = int(value)
            inches = (value - feet) * 12
        elif input_unit == "inch":
            inches = value % 12
            feet = int(round((value - inches) / 12))

        # Round to the nearest 1/N
        nearest = round(inches * precision)

        # Create a fraction based on the rounded value and the precision
        frac = Fraction(nearest, precision)

        # If fraction is a whole number, format it accordingly
        if frac.denominator == 1:
            if suppress_zero_inches and frac.numerator == 0:
                if output_unit == "foot":
                    return f"{feet}'"
                return f'{feet * 12}"'
            if output_unit == "foot":
                return f"{feet}' - {frac.numerator}\""
            return f'{(feet * 12) + frac.numerator}"'
        if frac.numerator > frac.denominator:
            remainder = frac.numerator % frac.denominator
            whole = int((frac.numerator - remainder) / frac.denominator)
            if output_unit == "foot":
                return f"{feet}' - {whole} {remainder}/{frac.denominator}\""
            return f'{(feet * 12) + whole} {remainder}/{frac.denominator}"'
        if output_unit == "foot":
            return f"{feet}' - {frac.numerator}/{frac.denominator}\""
        return f'{feet * 12} {frac.numerator}/{frac.denominator}"'
    elif unit_system == "metric":
        rounded_val = round(value / precision) * precision
        return f"{rounded_val:.{decimal_places}f}"
