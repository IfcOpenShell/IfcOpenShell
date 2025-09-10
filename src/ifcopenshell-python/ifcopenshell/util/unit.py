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

from fractions import Fraction
from math import pi
from typing import Literal, Optional, Union
from collections.abc import Generator

import ifcopenshell
import ifcopenshell.ifcopenshell_wrapper as ifcopenshell_wrapper
import ifcopenshell.api.unit

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
    "NEWTON": "N",
    "PASCAL": "Pa",
    # conversion based units
    "pound-force": "lbf",
    "pound-force per square inch": "psi",
    "thou": "th",
    "inch": "in",
    "foot": "ft",
    "yard": "yd",
    "mile": "mi",
    "square thou": "th2",
    "square inch": "in2",
    "square foot": "ft2",
    "square yard": "yd2",
    "acre": "ac",
    "square mile": "mi2",
    "cubic thou": "th3",
    "cubic inch": "in3",
    "cubic foot": "ft3",
    "cubic yard": "yd3",
    "cubic mile": "mi3",
    "litre": "L",
    "fluid ounce UK": "fl oz",
    "fluid ounce US": "fl oz",
    "pint UK": "pt",
    "pint US": "pt",
    "gallon UK": "gal",
    "gallon US": "gal",
    "degree": "°",
    "ounce": "oz",
    "pound": "lb",
    "ton UK": "ton",
    "ton US": "ton",
    "lbf": "lbf",
    "kip": "kip",
    "psi": "psi",
    "ksi": "ksi",
    "minute": "min",
    "hour": "hr",
    "day": "day",
    "btu": "btu",
    "fahrenheit": "°F",
}

QUANTITY_CLASS = Literal[
    "IfcQuantityCount",
    "IfcQuantityNumber",
    "IfcQuantityLength",
    "IfcQuantityArea",
    "IfcQuantityVolume",
    "IfcQuantityWeight",
    "IfcQuantityTime",
    "IfcQuantityCount",
]

MEASURE_CLASS = Literal[
    "IfcNumericMeasure",
    "IfcLengthMeasure",
    "IfcAreaMeasure",
    "IfcVolumeMeasure",
    "IfcMassMeasure",
]


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


def get_unit_name(text: str) -> Union[str, None]:
    """Get unit name from str, if unit is in SI."""
    text = text.upper().replace("METER", "METRE")
    for name in unit_names:
        if name.replace("_", " ") in text:
            return name


def get_unit_name_universal(text: str) -> Union[str, None]:
    """Get unit name from str, supports both SI and imperial system.

    Can be used to provide units for `convert()`"""
    text = text.upper().replace("METER", "METRE")
    for name in unit_names:
        if name.replace("_", " ") in text:
            return name
    for name in imperial_types:
        if name.upper() in text:
            return name


def get_full_unit_name(unit: ifcopenshell.entity_instance) -> str:
    prefix = getattr(unit, "Prefix", None) or ""
    return prefix + unit.Name.upper()


def get_si_dimensions(name):
    return si_dimensions.get(name, si_dimensions["OTHERWISE"])


def get_named_dimensions(name):
    return named_dimensions.get(name, (0, 0, 0, 0, 0, 0, 0))


def get_unit_assignment(ifc_file: ifcopenshell.file) -> Union[ifcopenshell.entity_instance, None]:
    return ifc_file.by_type("IfcProject")[0].UnitsInContext


def cache_units(ifc_file: ifcopenshell.file) -> None:
    """Cache the default units for performance

    Repetitively fetching project units (such as for determining the unit of a
    property) can be costly. This enables a cache to make it faster. If the
    project units change, you can update the cache by rerunning this function.

    :param ifc_file: The IFC file.
    """
    ifc_file.units = {}
    if assignment := get_unit_assignment(ifc_file):
        ifc_file.units = {u.UnitType: u for u in assignment.Units if getattr(u, "UnitType", None)}


def clear_unit_cache(ifc_file: ifcopenshell.file) -> None:
    """Clears the unit cache of the project

    :param ifc_file: The IFC file.
    """
    ifc_file.units = {}


def get_project_unit(
    ifc_file: ifcopenshell.file, unit_type: str, use_cache: bool = False
) -> Union[ifcopenshell.entity_instance, None]:
    """Get the default project unit of a particular unit type

    :param ifc_file: The IFC file.
    :param unit_type: The type of unit, taken from the list of IFC unit types,
        such as "LENGTHUNIT".
    :return: The IFC unit entity, or nothing if there is no default project
        unit defined.
    """
    if use_cache and not ifc_file.units:
        cache_units(ifc_file)
    if units := ifc_file.units:
        return units.get(unit_type, None)
    if unit_assignment := get_unit_assignment(ifc_file):
        for unit in unit_assignment.Units or []:
            if getattr(unit, "UnitType", None) == unit_type:
                return unit


def get_property_unit(
    prop: ifcopenshell.entity_instance, ifc_file: Union[ifcopenshell.file, None], use_cache: bool = False
) -> Union[ifcopenshell.entity_instance, None]:
    """Gets the unit definition of a property or quantity

    Properties and quantities in psets and qtos can be associated with a unit.
    This unit may be defined at the property itself explicitly, or if not
    specified, fallback to the project default.

    :param prop: The IfcProperty instance. You can fetch this via the instance
        ID if doing :func:`ifcopenshell.util.element.get_psets` with
        ``verbose=True``.
    :param ifc_file: The IFC file being used. This is necessary to check
        default project units.
    :return: The IFC unit entity, or nothing if there is no default project
        unit defined.
    """
    if unit := getattr(prop, "Unit", None):
        return unit

    value = None
    measure_class = None

    if prop.is_a("IfcPhysicalSimpleQuantity"):
        entity = prop.wrapped_data.declaration().as_entity()
        measure_class = entity.attribute_by_index(3).type_of_attribute().declared_type().name()
    elif prop.is_a("IfcPropertySingleValue"):
        measure_class = prop.NominalValue.is_a()
    elif prop.is_a("IfcPropertyEnumeratedValue"):
        if prop.EnumerationReference:
            if unit := prop.EnumerationReference.Unit:
                return unit
            if value := next(iter(prop.EnumerationReference.EnumerationValues or ()), None):
                measure_class = value.is_a()
        if value := next(iter(prop.EnumerationValues or ()), None):
            measure_class = value.is_a()
    elif prop.is_a("IfcPropertyListValue"):
        if value := next(iter(prop.ListValues or ()), None):
            measure_class = value.is_a()
    elif prop.is_a("IfcPropertyBoundedValue"):
        if value := (prop.UpperBoundValue or prop.LowerBoundValue or prop.SetPointValue):
            measure_class = value.is_a()

    if measure_class and (unit_type := get_measure_unit_type(measure_class)):
        if not ifc_file:
            ifc_file = prop.file
        return get_project_unit(ifc_file, unit_type, use_cache=use_cache)


def get_property_table_unit(
    prop: ifcopenshell.entity_instance, ifc_file: Union[ifcopenshell.file, None], use_cache: bool = False
) -> dict[str, Union[ifcopenshell.entity_instance, None]]:
    """
    Gets the unit definition of a property table

    Properties and quantities in psets and qtos can be associated with a unit.
    This unit may be defined at the property itself explicitly, or if not
    specified, fallback to the project default.

    :param prop: The property instance. You can fetch this via the instance ID
        if doing :func:`ifcopenshell.util.element.get_psets` with
        ``verbose=True``.

    :param ifc_file: The IFC file being used. This is necessary to check
        default project units.

    :return: A dictionary containing IFC unit entity by keyword.
        If a unit-entity is missing,
        the value associated to the key is `null`.
    """
    if not ifc_file:
        ifc_file = prop.file
    defining_unit = None
    if unit := prop.DefiningUnit:
        defining_unit = unit
    elif value := next(iter(prop.DefiningValues or ()), None):
        if unit_type := get_measure_unit_type(value.is_a()):
            defining_unit = get_project_unit(ifc_file, unit_type, use_cache=use_cache)

    defined_unit = None
    if unit := prop.DefinedUnit:
        defined_unit = unit
    elif value := next(iter(prop.DefinedValues or ()), None):
        if unit_type := get_measure_unit_type(value.is_a()):
            defined_unit = get_project_unit(ifc_file, unit_type, use_cache=use_cache)

    return {
        "DefiningUnit": defining_unit,
        "DefinedUnit": defined_unit,
    }


def get_unit_measure_class(unit_type: str) -> MEASURE_CLASS:
    """Get the IFC measure class for a unit type.

    IFC has specific classes used to measure different units. An example of an
    IFC measure class is ``IfcLengthMeasure``. An example of the correlating
    unit type (i.e. the IfcUnitEnum) is ``LENGTHUNIT``.

    The inverse function of this is :func:`get_measure_unit_type`

    :param unit_type: A string chosen from IfcUnitEnum, such as LENGTHUNIT
    """
    if unit_type == "USERDEFINED":
        # See https://github.com/buildingSMART/IFC4.3.x-development/issues/71
        return "IfcNumericMeasure"
    return "Ifc" + unit_type[0:-4].lower().capitalize() + "Measure"


def get_measure_unit_type(measure_class: MEASURE_CLASS) -> str:
    """Get the unit type of an IFC measure class

    IFC has different unit types which can be associated with units (e.g. SI
    units, imperial units, derived units, etc). An example of a unit type (i.e.
    an IfcUnitEnum) is ``LENGTHUNIT``. An example of the correlating measure
    class used to store length data is ``IfcLengthMeasure``.

    The inverse fucntion of this is :func:`get_unit_measure_class`

    :param measure_class: The measure class, such as ``IfcLengthMeasure``. If
        you have an ``IfcPropertySingleValue``, you can get this using
        ``prop.NominalValue.is_a()``.
    :return: The unit type, as an uppercase value of IfcUnitEnum.
    """
    if measure_class == "IfcNumericMeasure":
        # See https://github.com/buildingSMART/IFC4.3.x-development/issues/71
        return "USERDEFINED"
    for text in ("Ifc", "Measure", "Non", "Positive", "Negative"):
        measure_class = measure_class.replace(text, "")
    return measure_class.upper() + "UNIT"


def get_symbol_measure_class(symbol: Optional[str] = None) -> MEASURE_CLASS:
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


def get_symbol_quantity_class(symbol: Optional[str] = None) -> QUANTITY_CLASS:
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


def get_unit_symbol(unit: ifcopenshell.entity_instance) -> str:
    symbol: str = ""
    if unit.is_a("IfcSIUnit"):
        symbol += prefix_symbols.get(unit.Prefix, "")
    symbol += unit_symbols.get(unit.Name.replace("METER", "METRE"), "?")
    if unit.is_a("IfcContextDependentUnit") and unit.UnitType == "USERDEFINED":
        symbol = unit.Name
    return symbol


def convert_unit(value: float, from_unit: ifcopenshell.entity_instance, to_unit: ifcopenshell.entity_instance) -> float:
    """Convert from one unit to another unit

    :param value: The numeric value you want to convert
    :param from_unit: The IfcNamedUnit to confirm from.
    :param to_unit: The IfcNamedUnit to confirm from.
    :return: The converted value.
    """
    return convert(
        value, getattr(from_unit, "Prefix", None), from_unit.Name, getattr(to_unit, "Prefix", None), to_unit.Name
    )


def convert(value: float, from_prefix: Optional[str], from_unit: str, to_prefix: Optional[str], to_unit: str) -> float:
    """Converts between length, area, and volume units

    In this case, you manually specify the names and (optionally) prefixes to
    convert to and from. In case you want to automatically convert to units
    already available as IFC entities, consider using convert_unit() instead.

    :param value: The numeric value you want to convert
    :param from_prefix: A prefix from IfcSIPrefix. Can be None
    :param from_unit: IfcSIUnitName or IfcConversionBasedUnit.Name
    :param to_prefix: A prefix from IfcSIPrefix. Can be None
    :param to_unit: IfcSIUnitName or IfcConversionBasedUnit.Name
    :return: The converted value.
    """
    if from_unit.lower() in si_conversions:
        value *= si_conversions[from_unit.lower()]
    elif from_prefix:
        value *= get_prefix_multiplier(from_prefix)
        if "SQUARE" in from_unit:
            value *= get_prefix_multiplier(from_prefix)
        elif "CUBIC" in from_unit:
            value *= get_prefix_multiplier(from_prefix)
            value *= get_prefix_multiplier(from_prefix)
    if to_unit.lower() in si_conversions:
        return value * (1 / si_conversions[to_unit.lower()])
    elif to_prefix:
        value *= 1 / get_prefix_multiplier(to_prefix)
        if "SQUARE" in from_unit:
            value *= 1 / get_prefix_multiplier(to_prefix)
        elif "CUBIC" in from_unit:
            value *= 1 / get_prefix_multiplier(to_prefix)
            value *= 1 / get_prefix_multiplier(to_prefix)
    return value


def calculate_unit_scale(ifc_file: ifcopenshell.file, unit_type: str = "LENGTHUNIT") -> float:
    """Returns a unit scale factor to convert to and from IFC project units and SI units.

    Example:

    .. code:: python

        ifc_project_length * unit_scale = si_meters
        si_meters / unit_scale = ifc_project_length

    :param ifc_file: The IFC file.
    :param unit_type: The type of SI unit, defaults to "LENGTHUNIT"
    :returns: The scale factor
    """
    if (
        type(ifc_file) is ifcopenshell.file
        and unit_type
        not in ifcopenshell.ifcopenshell_wrapper.schema_by_name(ifc_file.schema_identifier)
        .declaration_by_name("IfcUnitEnum")
        .enumeration_items()
    ):
        raise ValueError(f"Unit type {unit_type!r} does not name a valid type")

    # Currently we assume that all ifc projects must have IfcProject.
    if not (projects := ifc_file.by_type("IfcProject")) or not (units := projects[0].UnitsInContext):
        return 1
    unit_scale = 1
    unit: ifcopenshell.entity_instance
    for unit in units.Units:
        if getattr(unit, "UnitType", ...) != unit_type:
            continue
        while unit.is_a("IfcConversionBasedUnit"):
            conversion_factor = unit.ConversionFactor
            unit_scale *= conversion_factor.ValueComponent.wrappedValue
            unit = conversion_factor.UnitComponent
        if unit.is_a("IfcSIUnit"):
            unit_scale *= get_prefix_multiplier(unit.Prefix)
    return unit_scale


def format_length(
    value: float,
    precision: float,
    decimal_places: int = 2,
    suppress_zero_inches=True,
    unit_system: Literal["metric", "imperial"] = "imperial",
    input_unit: Literal["foot", "inch"] = "foot",
    output_unit: Literal["foot", "inch"] = "foot",
) -> str:
    """Formats a length for readability and imperial formatting

    :param value: The value in meters if metric, or either decimal feet or
        inches if imperial depending on input_unit.
    :param precision: How precise the format should be. I.e. round to nearest.
        For imperial, it is 1/Nth. E.g. 12 means to the nearest 1/12th of an
        inch.
    :param decimal_places: How many decimal places to display. Defaults to 2.
    :param suppress_zero_inches: If imperial, whether or not to supress the
        inches if the inches is zero.
    :param unit_system: Choose whether your value is "metric" or "imperial"
    :param input_unit: If imperial, specify whether your value is "foot" or
        "inch".
    :param output_unit: If imperial, specify whether your value is "foot" to
        format as both feet and inches, or "inch" if only inches should be
        shown.
    :returns: The formatted string, such as 1' - 5 1/2".
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


def is_attr_type(
    content_type: ifcopenshell_wrapper.parameter_type,
    ifc_unit_type_name: str,
    include_select_types: bool = True,
) -> Union[ifcopenshell_wrapper.type_declaration, None]:
    cur_decl = content_type

    if hasattr(cur_decl, "name") and cur_decl.name() == ifc_unit_type_name:
        return cur_decl

    if include_select_types:
        if hasattr(cur_decl, "select_list"):
            for select_item in cur_decl.select_list():
                if is_attr_type(select_item, ifc_unit_type_name):
                    return select_item

    if hasattr(cur_decl, "declared_type"):
        return is_attr_type(cur_decl.declared_type(), ifc_unit_type_name, include_select_types)

    if isinstance(cur_decl, ifcopenshell_wrapper.aggregation_type):
        # support aggregate of aggregates, as in IfcCartesianPointList3D.CoordList
        def get_declared_type_from_aggregate(cur_decl):
            cur_decl = cur_decl.type_of_element()
            if not isinstance(cur_decl, ifcopenshell_wrapper.aggregation_type):
                return cur_decl.declared_type()
            return get_declared_type_from_aggregate(cur_decl)

        cur_decl = get_declared_type_from_aggregate(cur_decl)
        return is_attr_type(cur_decl, ifc_unit_type_name, include_select_types)

    return None


FloatOrSequenceOfFloats = Union[float, tuple["FloatOrSequenceOfFloats", ...]]


def iter_element_and_attributes_per_type(ifc_file: ifcopenshell.file, attr_type_name: str) -> Generator[
    tuple[
        ifcopenshell.entity_instance,
        ifcopenshell_wrapper.attribute,
        Union[FloatOrSequenceOfFloats, ifcopenshell.entity_instance],
    ],
    None,
    None,
]:
    schema = ifcopenshell_wrapper.schema_by_name(ifc_file.schema_identifier)

    for element in ifc_file:
        entity = schema.declaration_by_name(element.is_a()).as_entity()
        assert entity
        attrs = entity.all_attributes()
        attrs_derived = entity.derived()
        for attr, val, is_derived in zip(attrs, list(element), attrs_derived):
            if is_derived:
                continue

            # Get all methods and attributes of the element
            attr_type = attr.type_of_attribute()
            base_type = is_attr_type(attr_type, attr_type_name)
            if base_type is None:
                continue

            if val is None:
                continue

            if isinstance(val, ifcopenshell.entity_instance) and not val.is_a(attr_type_name):
                continue
            elif isinstance(val, tuple):
                if not val:
                    continue
                val_ = val[0]
                # If it's a tuple of entities, just yield the entities we need to edit.
                if isinstance(val_, ifcopenshell.entity_instance):
                    for val_ in val:
                        if not val_.is_a(attr_type_name):
                            continue
                        yield element, attr, val_
                    continue

            yield element, attr, val


def convert_file_length_units(ifc_file: ifcopenshell.file, target_units: str = "METER") -> ifcopenshell.file:
    """Converts all units in an IFC file to the specified target units. Returns a new file."""
    import ifcopenshell.util.element
    import ifcopenshell.util.geolocation
    import ifcopenshell.api.georeference
    import ifcopenshell.api.unit

    prefix = get_prefix(target_units)
    si_unit = get_unit_name(target_units)

    # Copy all elements from the original file to the patched file
    file_patched = ifcopenshell.file.from_string(ifc_file.wrapped_data.to_string())

    old_length = get_project_unit(file_patched, "LENGTHUNIT")
    if si_unit:
        new_length = ifcopenshell.api.unit.add_si_unit(file_patched, unit_type="LENGTHUNIT", prefix=prefix)
    else:
        target_units = target_units.lower()
        if imperial_types.get(target_units) != "LENGTHUNIT":
            raise Exception(
                f'Couldn\'t identify target units "{target_units}". '
                'The method supports singular unit names like "CENTIMETER", "METER", "FOOT", etc.'
            )
        new_length = ifcopenshell.api.unit.add_conversion_based_unit(file_patched, name=target_units)

    # support tuple of tuples, as in IfcCartesianPointList3D.CoordList
    def convert_value(value: FloatOrSequenceOfFloats) -> FloatOrSequenceOfFloats:
        if not isinstance(value, tuple):
            return convert_unit(value, old_length, new_length)
        return tuple(convert_value(v) for v in value)

    # Traverse all elements and their nested attributes in the file and convert them
    for element, attr, val in iter_element_and_attributes_per_type(file_patched, "IfcLengthMeasure"):
        # NOTE: There is no risk of editing same entities twice as they're all recreated
        # after file is reloaded as `file_patched`.
        if isinstance(val, ifcopenshell.entity_instance):
            val.wrappedValue = convert_value(val.wrappedValue)
        else:
            new_value = convert_value(val)
            setattr(element, attr.name(), new_value)

    has_map_unit = False
    if (
        ifc_file.schema == "IFC2X3"
        and (crs := ifcopenshell.util.element.get_pset(ifc_file.by_type("IfcProject")[0], name="ePSet_ProjectedCRS"))
        and crs.get("MapUnit")
    ) or (ifc_file.schema != "IFC2X3" and (crs := ifc_file.by_type("IfcProjectedCRS")) and crs[0].MapUnit):
        has_map_unit = True

    if has_map_unit:
        parameters = ifcopenshell.util.geolocation.get_helmert_transformation_parameters(ifc_file)
        ifcopenshell.api.georeference.edit_georeferencing(
            file_patched,
            coordinate_operation={
                "Eastings": parameters.e,
                "Northings": parameters.n,
                "OrthogonalHeight": parameters.h,
                "Scale": parameters.scale / convert_value(1),
            },
        )

    unit_assignment = get_unit_assignment(file_patched)
    unit_assignment.Units = [new_length, *(u for u in unit_assignment.Units if u.UnitType != new_length.UnitType)]
    if not file_patched.get_total_inverses(old_length):
        ifcopenshell.util.element.remove_deep2(file_patched, old_length)

    return file_patched
