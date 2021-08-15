from math import pi

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
    "THERMODYNAMICTEMPERATUREUNIT": "KELVIN", # Or, DEGREE_CELSIUS, but this is a quirk of IFC
    "TIMEUNIT": "SECOND",
    "VOLUMEUNIT": "CUBIC_METRE",
}

# Are you good at physics? Want to help fill these in? :)
named_dimensions = {
    # "ABSORBEDDOSEUNIT": (0, 0, 0, 0, 0, 0, 0),
    "AMOUNTOFSUBSTANCEUNIT": (0, 0, 0, 0, 0, 1, 0),
    "AREAUNIT": (2, 0, 0, 0, 0, 0, 0),
    # "DOSEEQUIVALENTUNIT": (0, 0, 0, 0, 0, 0, 0),
    # "ELECTRICCAPACITANCEUNIT": (0, 0, 0, 0, 0, 0, 0),
    # "ELECTRICCHARGEUNIT": (0, 0, 0, 0, 0, 0, 0),
    # "ELECTRICCONDUCTANCEUNIT": (0, 0, 0, 0, 0, 0, 0),
    "ELECTRICCURRENTUNIT": (0, 0, 0, 1, 0, 0, 0),
    # "ELECTRICRESISTANCEUNIT": (0, 0, 0, 0, 0, 0, 0),
    # "ELECTRICVOLTAGEUNIT": (0, 0, 0, 0, 0, 0, 0),
    "ENERGYUNIT": (2, 1, -2, 0, 0, 0, 0),
    "FORCEUNIT": (1, 1, -2, 0, 0, 0, 0),
    "FREQUENCYUNIT": (0, 0, -1, 0, 0, 0, 0),
    # "ILLUMINANCEUNIT": (0, 0, 0, 0, 0, 0, 0),
    # "INDUCTANCEUNIT": (0, 0, 0, 0, 0, 0, 0),
    "LENGTHUNIT": (1, 0, 0, 0, 0, 0, 0),
    # "LUMINOUSFLUXUNIT": (0, 0, 0, 0, 0, 0, 0),
    "LUMINOUSINTENSITYUNIT": (0, 0, 0, 0, 0, 0, 1),
    # "MAGNETICFLUXDENSITYUNIT": (0, 0, 0, 0, 0, 0, 0),
    # "MAGNETICFLUXUNIT": (0, 0, 0, 0, 0, 0, 0),
    "MASSUNIT": (0, 1, 0, 0, 0, 0, 0),
    "PLANEANGLEUNIT": (0, 0, 0, 0, 0, 0, 0),
    "POWERUNIT": (2, 1, -3, 0, 0, 0, 0),
    "PRESSUREUNIT": (-1, 1, -2, 0, 0, 0, 0),
    # "RADIOACTIVITYUNIT": (0, 0, 0, 0, 0, 0, 0),
    "SOLIDANGLEUNIT": (0, 0, 0, 0, 0, 0, 0),
    "THERMODYNAMICTEMPERATUREUNIT": (0, 0, 0, 0, 1, 0, 0),
    "TIMEUNIT": (0, 0, 1, 0, 0, 0, 0),
    "VOLUMEUNIT": (3, 0, 0, 0, 0, 0, 0),
}

si_conversions = {
    "inch": 0.0254,
    "foot": 0.3048,
    "yard": 0.914,
    "mile": 1609,
    "square inch": 0.0006452,
    "square foot": 0.09290304,
    "square yard": 0.83612736,
    "acre": 4046.86,
    "square mile": 2588881,
    "cubic inch": 0.00001639,
    "cubic foot": 0.02831684671168849,
    "cubic yard": 0.7636,
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
    "CUBIC_METRE": "m3",
    "GRAM": "g",
    "SECOND": "s",
    "SQUARE_METRE": "m2",
    "METRE": "m",
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


def get_property_unit(prop, ifc_file):
    unit = getattr(prop, "Unit", None)
    if unit:
        return unit
    unit_assignment = ifc_file.by_type("IfcUnitAssignment")
    if not unit_assignment:
        return
    entity = prop.wrapped_data.declaration().as_entity()
    if prop.is_a("IfcPhysicalSimpleQuantity"):
        measure_type = entity.attribute_by_index(3).type_of_attribute().declared_type().name()
    elif prop.is_a("IfcPropertySingleValue") and prop.NominalValue:
        measure_type = prop.NominalValue.is_a()
    for text in ("Ifc", "Measure", "Non", "Positive", "Negative"):
        measure_type = measure_type.replace(text, "")
    measure_type = measure_type.upper() + "UNIT"
    units = [u for u in unit_assignment[0].Units if getattr(u, "UnitType", None) == measure_type]
    if units:
        return units[0]


def get_unit_measure_type(unit_type):
    return "Ifc" + unit_type[0:-4].lower().capitalize() + "Measure"


def get_symbol_quantity_class(symbol):
    # Dumb, but everybody gets it, unlike regex golf
    if not symbol:
        return "IfcQuantityCount"
    symbol = symbol.lower()
    if symbol in ["kg", "g", "mt", "kt", "t"]:
        return "IfcQuantityWeight"
    elif symbol in ["day", "d", "hour", "hr", "h", "minute", "min", "m", "second", "sec", "s"]:
        return "IfcQuantityTime"
    elif symbol in ["km3", "m3", "cm3", "mm3", "cy", "cft", "cin"]:
        return "IfcQuantityVolume"
    elif symbol in ["km2", "m2", "cm2", "mm2", "sqy", "sqft", "sqin"]:
        return "IfcQuantityArea"
    elif symbol in ["km", "m", "cm", "mm", "ly", "lf", "lin", "yd", "ft", "in"]:
        return "IfcQuantityLength"
    return "IfcQuantityCount"


def get_unit_symbol(unit):
    if unit.is_a("IfcSIUnit"):
        symbol = ""
        symbol += prefix_symbols.get(unit.Prefix, "")
        symbol += unit_symbols.get(unit.Name.replace("METER", "METRE"), "?")
        return symbol
    return "?"


def convert(value, from_prefix, from_unit, to_prefix, to_unit):
    """Converts between length, area, and volume units

    :param value: The numeric value you want to convert
    :type value: float
    :param from_prefix: A prefix from IfcSIPrefix. Can be None.
    :type from_prefix: string
    :param from_unit: IfcSIUnitName or IfcConversionBasedUnit.Name
    :type from_unit: string
    :param to_prefix: A prefix from IfcSIPrefix. Can be None.
    :type to_prefix: string
    :param to_unit: IfcSIUnitName or IfcConversionBasedUnit.Name
    :type to_unit: string
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


def calculate_unit_scale(file):
    """Returns a unit scale factor to convert to and from IFC project length units and SI meters

    Example::

        ifc_project_length * unit_scale = si_meters
        si_meters / unit_scale = ifc_project_length

    :returns: The scale factor
    :rtype: float
    """
    units = file.by_type("IfcUnitAssignment")[0]
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
